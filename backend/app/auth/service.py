"""
Authentication service layer.

This module contains all authentication business logic:
- User registration
- User authentication (login)
- Token refresh with rotation
- Logout (token revocation)
- Email verification
- Password reset

Pattern: Complete logging lifecycle (started, completed, failed).

Security:
    - Rate limiting on login attempts
    - Rate limiting on verification email resends
    - Rate limiting on password reset requests
    - Password hashing with bcrypt
    - Refresh token rotation
    - Token revocation on logout
    - Single-use email verification tokens
    - Single-use password reset tokens
"""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiry,
    hash_token,
)
from app.auth.models import EmailVerificationToken, PasswordResetToken, RefreshToken, User
from app.auth.schemas import UserRegisterRequest
from app.core.config import get_settings
from app.core.logging import get_logger
from app.shared.security import (
    HashedPassword,
    PlainPassword,
    RateLimiter,
    generate_secure_token,
    hash_password,
    redact_pii,
    verify_password,
)

logger = get_logger(__name__)

# Rate limiter for login attempts (10 attempts per 5 minutes)
login_rate_limiter = RateLimiter(max_attempts=10, window_seconds=300)

# Rate limiter for verification email resends (3 attempts per 5 minutes)
verification_rate_limiter = RateLimiter(max_attempts=3, window_seconds=300)

# Rate limiter for password reset requests (3 attempts per 5 minutes)
password_reset_rate_limiter = RateLimiter(max_attempts=3, window_seconds=300)

# Email verification token expiry (24 hours)
EMAIL_VERIFICATION_EXPIRY_HOURS = 24

# Password reset token expiry (1 hour)
PASSWORD_RESET_EXPIRY_HOURS = 1


class AuthError(Exception):
    """Base exception for authentication errors."""

    def __init__(self, message: str, error_code: str) -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class UserExistsError(AuthError):
    """Raised when registering with an existing email."""

    def __init__(self) -> None:
        super().__init__("Email already registered", "USER_EXISTS")


class InvalidCredentialsError(AuthError):
    """Raised when login credentials are invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password", "INVALID_CREDENTIALS")


class RateLimitExceededError(AuthError):
    """Raised when rate limit is exceeded."""

    def __init__(self) -> None:
        super().__init__("Too many attempts. Please try again later.", "RATE_LIMIT_EXCEEDED")


class InvalidTokenError(AuthError):
    """Raised when refresh token is invalid or expired."""

    def __init__(self) -> None:
        super().__init__("Invalid or expired token", "INVALID_TOKEN")


class UserInactiveError(AuthError):
    """Raised when user account is not active."""

    def __init__(self) -> None:
        super().__init__("User account is not active", "USER_INACTIVE")


class EmailAlreadyVerifiedError(AuthError):
    """Raised when trying to verify an already verified email."""

    def __init__(self) -> None:
        super().__init__("Email already verified", "EMAIL_ALREADY_VERIFIED")


class UserNotFoundError(AuthError):
    """Raised when user is not found."""

    def __init__(self) -> None:
        super().__init__("User not found", "USER_NOT_FOUND")


async def register_user(
    db: AsyncSession,
    data: UserRegisterRequest,
) -> User:
    """
    Register a new user.

    Args:
        db: Database session
        data: Registration data (email, password)

    Returns:
        Created User object

    Raises:
        UserExistsError: If email already registered

    Logging:
        - auth.register_started: When registration begins
        - auth.register_completed: On successful registration
        - auth.register_failed: On failure
    """
    logger.info(
        "auth.register_started",
        email=redact_pii(data.email),
    )

    try:
        # Hash password
        hashed = hash_password(PlainPassword(data.password))

        # Create user (inactive until email verified)
        # For Phase 1, we set is_active=True to allow immediate login
        # Phase 2 will add email verification and set is_active=False initially
        user = User(
            email=data.email,
            password_hash=hashed,
            is_active=True,  # TODO: Set to False when email verification added
            is_email_verified=False,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info(
            "auth.register_completed",
            user_id=user.id,
            email=redact_pii(user.email),
        )

        return user

    except IntegrityError as err:
        await db.rollback()
        logger.warning(
            "auth.register_failed",
            reason="email_exists",
            email=redact_pii(data.email),
        )
        raise UserExistsError() from err

    except Exception as e:
        await db.rollback()
        logger.error(
            "auth.register_failed",
            error=str(e),
            error_type=type(e).__name__,
            email=redact_pii(data.email),
            exc_info=True,
        )
        raise


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
    ip_address: str,
    device_info: str | None = None,
) -> tuple[User, str, str]:
    """
    Authenticate user and issue tokens.

    Args:
        db: Database session
        email: User's email
        password: Plain text password
        ip_address: Client IP address (for rate limiting)
        device_info: Optional device/browser info

    Returns:
        Tuple of (User, access_token, refresh_token)

    Raises:
        RateLimitExceededError: If too many failed attempts
        InvalidCredentialsError: If email/password invalid
        UserInactiveError: If user account is not active

    Logging:
        - auth.login_started: When login begins
        - auth.login_completed: On successful login
        - auth.login_failed: On failure
    """
    logger.info(
        "auth.login_started",
        email=redact_pii(email),
        ip_address=ip_address,
    )

    # Check rate limit BEFORE attempting authentication
    if not login_rate_limiter.check_limit(email, ip_address):
        logger.warning(
            "auth.login_failed",
            reason="rate_limit_exceeded",
            email=redact_pii(email),
            ip_address=ip_address,
        )
        raise RateLimitExceededError()

    try:
        # Find user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user is None:
            # Record failed attempt
            login_rate_limiter.record_attempt(email, ip_address)
            logger.warning(
                "auth.login_failed",
                reason="user_not_found",
                email=redact_pii(email),
            )
            raise InvalidCredentialsError()

        # Verify password
        if not verify_password(PlainPassword(password), HashedPassword(user.password_hash)):
            # Record failed attempt
            login_rate_limiter.record_attempt(email, ip_address)
            logger.warning(
                "auth.login_failed",
                reason="invalid_password",
                user_id=user.id,
            )
            raise InvalidCredentialsError()

        # Check user is active
        if not user.is_active:
            logger.warning(
                "auth.login_failed",
                reason="user_inactive",
                user_id=user.id,
            )
            raise UserInactiveError()

        # Reset rate limiter on successful login
        login_rate_limiter.reset(email, ip_address)

        # Create tokens
        access_token = create_access_token(user.id, user.role)
        refresh_token = create_refresh_token()

        # Store refresh token hash in database
        token_hash = hash_token(refresh_token)
        expires_at = get_refresh_token_expiry()

        db_token = RefreshToken(
            token_hash=token_hash,
            user_id=user.id,
            expires_at=expires_at,
            device_info=device_info,
        )
        db.add(db_token)
        await db.commit()

        settings = get_settings()
        logger.info(
            "auth.login_completed",
            user_id=user.id,
            role=user.role.value,
            access_token_expires_minutes=settings.access_token_expire_minutes,
        )

        return user, access_token, refresh_token

    except (RateLimitExceededError, InvalidCredentialsError, UserInactiveError):
        # Re-raise auth-specific errors
        raise

    except Exception as e:
        logger.error(
            "auth.login_failed",
            error=str(e),
            error_type=type(e).__name__,
            email=redact_pii(email),
            exc_info=True,
        )
        raise


async def refresh_tokens(
    db: AsyncSession,
    refresh_token: str,
) -> tuple[str, str]:
    """
    Refresh access token using refresh token (with rotation).

    Args:
        db: Database session
        refresh_token: Current refresh token

    Returns:
        Tuple of (new_access_token, new_refresh_token)

    Raises:
        InvalidTokenError: If refresh token is invalid, expired, or revoked

    Logging:
        - auth.refresh_started: When refresh begins
        - auth.refresh_completed: On successful refresh
        - auth.refresh_failed: On failure

    Security:
        - Old refresh token is revoked (rotation)
        - New refresh token is issued
        - Prevents token reuse attacks
    """
    logger.info("auth.refresh_started")

    try:
        # Hash the provided token
        token_hash = hash_token(refresh_token)

        # Find token in database
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        db_token = result.scalar_one_or_none()

        if db_token is None:
            logger.warning("auth.refresh_failed", reason="token_not_found")
            raise InvalidTokenError()

        # Check if revoked
        if db_token.is_revoked:
            logger.warning(
                "auth.refresh_failed",
                reason="token_revoked",
                user_id=db_token.user_id,
            )
            raise InvalidTokenError()

        # Check if expired
        if db_token.expires_at < datetime.now(UTC):
            logger.warning(
                "auth.refresh_failed",
                reason="token_expired",
                user_id=db_token.user_id,
            )
            raise InvalidTokenError()

        # Get user
        user_result = await db.execute(select(User).where(User.id == db_token.user_id))
        user: User | None = user_result.scalar_one_or_none()

        if user is None or not user.is_active:
            logger.warning(
                "auth.refresh_failed",
                reason="user_not_found_or_inactive",
                user_id=db_token.user_id,
            )
            raise InvalidTokenError()

        # Revoke old token (rotation)
        db_token.is_revoked = True

        # Create new tokens
        new_access_token = create_access_token(user.id, user.role)
        new_refresh_token = create_refresh_token()

        # Store new refresh token
        new_token_hash = hash_token(new_refresh_token)
        new_expires_at = get_refresh_token_expiry()

        new_db_token = RefreshToken(
            token_hash=new_token_hash,
            user_id=user.id,
            expires_at=new_expires_at,
            device_info=db_token.device_info,
        )
        db.add(new_db_token)
        await db.commit()

        logger.info(
            "auth.refresh_completed",
            user_id=user.id,
        )

        return new_access_token, new_refresh_token

    except InvalidTokenError:
        # Re-raise auth-specific errors
        raise

    except Exception as e:
        await db.rollback()
        logger.error(
            "auth.refresh_failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise


async def logout_user(
    db: AsyncSession,
    user_id: int,
    refresh_token: str,
) -> None:
    """
    Logout user by revoking refresh token.

    Args:
        db: Database session
        user_id: User's ID
        refresh_token: Token to revoke

    Logging:
        - auth.logout_started: When logout begins
        - auth.logout_completed: On successful logout
    """
    logger.info(
        "auth.logout_started",
        user_id=user_id,
    )

    try:
        # Hash the provided token
        token_hash = hash_token(refresh_token)

        # Find and revoke token
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == user_id,
            )
        )
        db_token = result.scalar_one_or_none()

        if db_token is not None:
            db_token.is_revoked = True
            await db.commit()

        logger.info(
            "auth.logout_completed",
            user_id=user_id,
        )

    except Exception as e:
        await db.rollback()
        logger.error(
            "auth.logout_failed",
            error=str(e),
            error_type=type(e).__name__,
            user_id=user_id,
            exc_info=True,
        )
        raise


async def get_user_by_id(
    db: AsyncSession,
    user_id: int,
) -> User | None:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User's database ID

    Returns:
        User if found, None otherwise
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> User | None:
    """
    Get user by email.

    Args:
        db: Database session
        email: User's email address

    Returns:
        User if found, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_email_verification_token(
    db: AsyncSession,
    user: User,
) -> str:
    """
    Create an email verification token for a user.

    Args:
        db: Database session
        user: User to create verification token for

    Returns:
        Raw verification token (to be sent via email)

    Logging:
        - auth.verification_token_created: On successful creation
    """
    logger.info(
        "auth.verification_token_started",
        user_id=user.id,
    )

    # Generate secure token
    raw_token = generate_secure_token(32)
    token_hash_value = hash_token(raw_token)
    expires_at = datetime.now(UTC) + timedelta(hours=EMAIL_VERIFICATION_EXPIRY_HOURS)

    # Create token record
    db_token = EmailVerificationToken(
        token_hash=token_hash_value,
        user_id=user.id,
        expires_at=expires_at,
    )
    db.add(db_token)
    await db.commit()

    logger.info(
        "auth.verification_token_created",
        user_id=user.id,
        expires_in_hours=EMAIL_VERIFICATION_EXPIRY_HOURS,
    )

    return raw_token


async def verify_email(
    db: AsyncSession,
    token: str,
) -> User:
    """
    Verify a user's email using verification token.

    Args:
        db: Database session
        token: Raw verification token

    Returns:
        Updated User object with verified email

    Raises:
        InvalidTokenError: If token is invalid, expired, or already used
        EmailAlreadyVerifiedError: If email is already verified

    Logging:
        - auth.email_verification_started: When verification begins
        - auth.email_verification_completed: On successful verification
        - auth.email_verification_failed: On failure
    """
    logger.info("auth.email_verification_started")

    try:
        # Hash the provided token
        token_hash_value = hash_token(token)

        # Find token in database
        result = await db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.token_hash == token_hash_value
            )
        )
        db_token = result.scalar_one_or_none()

        if db_token is None:
            logger.warning("auth.email_verification_failed", reason="token_not_found")
            raise InvalidTokenError()

        # Check if already used
        if db_token.is_used:
            logger.warning(
                "auth.email_verification_failed",
                reason="token_already_used",
                user_id=db_token.user_id,
            )
            raise InvalidTokenError()

        # Check if expired
        if db_token.expires_at < datetime.now(UTC):
            logger.warning(
                "auth.email_verification_failed",
                reason="token_expired",
                user_id=db_token.user_id,
            )
            raise InvalidTokenError()

        # Get user
        user_result = await db.execute(
            select(User).where(User.id == db_token.user_id)
        )
        user: User | None = user_result.scalar_one_or_none()

        if user is None:
            logger.warning(
                "auth.email_verification_failed",
                reason="user_not_found",
                user_id=db_token.user_id,
            )
            raise InvalidTokenError()

        # Check if already verified
        if user.is_email_verified:
            logger.warning(
                "auth.email_verification_failed",
                reason="already_verified",
                user_id=user.id,
            )
            raise EmailAlreadyVerifiedError()

        # Mark token as used
        db_token.is_used = True

        # Verify user's email
        user.is_email_verified = True

        await db.commit()
        await db.refresh(user)

        logger.info(
            "auth.email_verification_completed",
            user_id=user.id,
        )

        return user

    except (InvalidTokenError, EmailAlreadyVerifiedError):
        raise

    except Exception as e:
        await db.rollback()
        logger.error(
            "auth.email_verification_failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise


async def resend_verification_email(
    db: AsyncSession,
    email: str,
    ip_address: str,
) -> str:
    """
    Resend verification email to user.

    Args:
        db: Database session
        email: User's email address
        ip_address: Client IP address (for rate limiting)

    Returns:
        Raw verification token (to be sent via email)

    Raises:
        RateLimitExceededError: If too many resend attempts
        UserNotFoundError: If user not found
        EmailAlreadyVerifiedError: If email already verified

    Logging:
        - auth.resend_verification_started: When resend begins
        - auth.resend_verification_completed: On successful resend
        - auth.resend_verification_failed: On failure
    """
    logger.info(
        "auth.resend_verification_started",
        email=redact_pii(email),
    )

    # Check rate limit
    if not verification_rate_limiter.check_limit(email, ip_address):
        logger.warning(
            "auth.resend_verification_failed",
            reason="rate_limit_exceeded",
            email=redact_pii(email),
        )
        raise RateLimitExceededError()

    try:
        # Record attempt
        verification_rate_limiter.record_attempt(email, ip_address)

        # Find user
        user = await get_user_by_email(db, email)

        if user is None:
            logger.warning(
                "auth.resend_verification_failed",
                reason="user_not_found",
                email=redact_pii(email),
            )
            raise UserNotFoundError()

        # Check if already verified
        if user.is_email_verified:
            logger.warning(
                "auth.resend_verification_failed",
                reason="already_verified",
                user_id=user.id,
            )
            raise EmailAlreadyVerifiedError()

        # Create new verification token
        raw_token = await create_email_verification_token(db, user)

        logger.info(
            "auth.resend_verification_completed",
            user_id=user.id,
        )

        return raw_token

    except (RateLimitExceededError, UserNotFoundError, EmailAlreadyVerifiedError):
        raise

    except Exception as e:
        await db.rollback()
        logger.error(
            "auth.resend_verification_failed",
            error=str(e),
            error_type=type(e).__name__,
            email=redact_pii(email),
            exc_info=True,
        )
        raise


async def create_password_reset_token(
    db: AsyncSession,
    user: User,
) -> str:
    """
    Create a password reset token for a user.

    Args:
        db: Database session
        user: User to create reset token for

    Returns:
        Raw reset token (to be sent via email)

    Logging:
        - auth.password_reset_token_created: On successful creation
    """
    logger.info(
        "auth.password_reset_token_started",
        user_id=user.id,
    )

    # Generate secure token
    raw_token = generate_secure_token(32)
    token_hash_value = hash_token(raw_token)
    expires_at = datetime.now(UTC) + timedelta(hours=PASSWORD_RESET_EXPIRY_HOURS)

    # Create token record
    db_token = PasswordResetToken(
        token_hash=token_hash_value,
        user_id=user.id,
        expires_at=expires_at,
    )
    db.add(db_token)
    await db.commit()

    logger.info(
        "auth.password_reset_token_created",
        user_id=user.id,
        expires_in_hours=PASSWORD_RESET_EXPIRY_HOURS,
    )

    return raw_token


async def request_password_reset(
    db: AsyncSession,
    email: str,
    ip_address: str,
) -> str | None:
    """
    Request a password reset for a user.

    Args:
        db: Database session
        email: User's email address
        ip_address: Client IP address (for rate limiting)

    Returns:
        Raw reset token if user exists, None otherwise
        (None is returned to prevent email enumeration)

    Raises:
        RateLimitExceededError: If too many reset attempts

    Logging:
        - auth.password_reset_requested: When request begins
        - auth.password_reset_request_completed: On completion
        - auth.password_reset_request_failed: On failure

    Security:
        - Rate limited to prevent abuse
        - Does not reveal if email exists (returns success message regardless)
    """
    logger.info(
        "auth.password_reset_requested",
        email=redact_pii(email),
    )

    # Check rate limit
    if not password_reset_rate_limiter.check_limit(email, ip_address):
        logger.warning(
            "auth.password_reset_request_failed",
            reason="rate_limit_exceeded",
            email=redact_pii(email),
        )
        raise RateLimitExceededError()

    try:
        # Record attempt
        password_reset_rate_limiter.record_attempt(email, ip_address)

        # Find user
        user = await get_user_by_email(db, email)

        if user is None:
            # Don't reveal that user doesn't exist
            logger.info(
                "auth.password_reset_request_completed",
                email=redact_pii(email),
                user_found=False,
            )
            return None

        # Create reset token
        raw_token = await create_password_reset_token(db, user)

        logger.info(
            "auth.password_reset_request_completed",
            user_id=user.id,
            user_found=True,
        )

        return raw_token

    except RateLimitExceededError:
        raise

    except Exception as e:
        await db.rollback()
        logger.error(
            "auth.password_reset_request_failed",
            error=str(e),
            error_type=type(e).__name__,
            email=redact_pii(email),
            exc_info=True,
        )
        raise


async def reset_password(
    db: AsyncSession,
    token: str,
    new_password: str,
) -> User:
    """
    Reset user's password using reset token.

    Args:
        db: Database session
        token: Raw password reset token
        new_password: New password to set

    Returns:
        Updated User object

    Raises:
        InvalidTokenError: If token is invalid, expired, or already used

    Logging:
        - auth.password_reset_started: When reset begins
        - auth.password_reset_completed: On successful reset
        - auth.password_reset_failed: On failure

    Security:
        - Token is single-use (marked as used after reset)
        - Token expires after 1 hour
        - New password is hashed before storage
    """
    logger.info("auth.password_reset_started")

    try:
        # Hash the provided token
        token_hash_value = hash_token(token)

        # Find token in database
        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash_value
            )
        )
        db_token = result.scalar_one_or_none()

        if db_token is None:
            logger.warning("auth.password_reset_failed", reason="token_not_found")
            raise InvalidTokenError()

        # Check if already used
        if db_token.is_used:
            logger.warning(
                "auth.password_reset_failed",
                reason="token_already_used",
                user_id=db_token.user_id,
            )
            raise InvalidTokenError()

        # Check if expired
        if db_token.expires_at < datetime.now(UTC):
            logger.warning(
                "auth.password_reset_failed",
                reason="token_expired",
                user_id=db_token.user_id,
            )
            raise InvalidTokenError()

        # Get user
        user_result = await db.execute(
            select(User).where(User.id == db_token.user_id)
        )
        user: User | None = user_result.scalar_one_or_none()

        if user is None:
            logger.warning(
                "auth.password_reset_failed",
                reason="user_not_found",
                user_id=db_token.user_id,
            )
            raise InvalidTokenError()

        # Mark token as used
        db_token.is_used = True

        # Update user's password
        user.password_hash = hash_password(PlainPassword(new_password))

        await db.commit()
        await db.refresh(user)

        logger.info(
            "auth.password_reset_completed",
            user_id=user.id,
        )

        return user

    except InvalidTokenError:
        raise

    except Exception as e:
        await db.rollback()
        logger.error(
            "auth.password_reset_failed",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise
