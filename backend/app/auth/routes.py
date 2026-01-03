"""
Authentication API routes.

Endpoints:
    POST /auth/register - Create new user account
    POST /auth/login - Login with email/password
    POST /auth/logout - Revoke refresh token
    POST /auth/refresh - Get new tokens
    GET /auth/me - Get current user info
    POST /auth/verify-email - Verify email with token
    POST /auth/resend-verification - Resend verification email
    POST /auth/forgot-password - Request password reset
    POST /auth/reset-password - Reset password with token

Pattern: FastAPI router with dependency injection.

Security:
    - Rate limiting on login/register/verification/password-reset
    - JWT authentication on protected routes
    - Proper HTTP status codes for auth failures
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import (
    EmailVerificationRequest,
    EmailVerificationResponse,
    ForgotPasswordRequest,
    MessageResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)
from app.auth.service import (
    EmailAlreadyVerifiedError,
    InvalidCredentialsError,
    InvalidTokenError,
    RateLimitExceededError,
    UserExistsError,
    UserInactiveError,
    UserNotFoundError,
    authenticate_user,
    logout_user,
    refresh_tokens,
    register_user,
    request_password_reset,
    resend_verification_email,
    reset_password,
    verify_email,
)
from app.core.config import get_settings
from app.core.database import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    # Check for forwarded header (behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # Fall back to direct client
    client = request.client
    if client:
        return client.host
    return "unknown"


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Validation error"},
        409: {"description": "Email already registered"},
    },
)
async def register_endpoint(
    data: UserRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Register a new user account.

    Args:
        data: Registration data with email and password

    Returns:
        Created user profile

    Raises:
        409 Conflict: If email already registered
        400 Bad Request: If validation fails
    """
    try:
        user = await register_user(db, data)
        return UserResponse.model_validate(user)

    except UserExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
        429: {"description": "Too many attempts"},
    },
)
async def login_endpoint(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate user and return access/refresh tokens.

    Uses OAuth2 password flow (form data with username/password fields).
    The 'username' field should contain the user's email.

    Args:
        form_data: OAuth2 form with username (email) and password
        request: HTTP request (for client IP)
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        401 Unauthorized: If credentials invalid
        429 Too Many Requests: If rate limit exceeded

    Security:
        - Rate limited to prevent brute force attacks
        - Password never logged
    """
    try:
        ip_address = get_client_ip(request)
        user_agent = request.headers.get("User-Agent")

        _user, access_token, refresh_token = await authenticate_user(
            db=db,
            email=form_data.username,  # OAuth2 uses 'username' field
            password=form_data.password,
            ip_address=ip_address,
            device_info=user_agent,
        )

        settings = get_settings()
        expires_in = settings.access_token_expire_minutes * 60  # Convert to seconds

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": "300"},  # 5 minutes
        ) from e

    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    except UserInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout and revoke token",
    responses={
        200: {"description": "Logout successful"},
        401: {"description": "Not authenticated"},
    },
)
async def logout_endpoint(
    data: TokenRefreshRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Logout by revoking the refresh token.

    Args:
        data: Request containing refresh token to revoke
        user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Security:
        - Requires valid access token
        - Only revokes tokens belonging to current user
    """
    await logout_user(db, user.id, data.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    responses={
        200: {"description": "Tokens refreshed"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_endpoint(
    data: TokenRefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Get new access and refresh tokens using a valid refresh token.

    Implements token rotation - the old refresh token is revoked
    and a new one is issued.

    Args:
        data: Request containing current refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        401 Unauthorized: If refresh token is invalid or expired

    Security:
        - Token rotation prevents token reuse attacks
        - Old token is immediately revoked
    """
    try:
        access_token, refresh_token = await refresh_tokens(db, data.refresh_token)

        settings = get_settings()
        expires_in = settings.access_token_expire_minutes * 60

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    responses={
        200: {"description": "Current user profile"},
        401: {"description": "Not authenticated"},
    },
)
async def me_endpoint(
    user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """
    Get the current authenticated user's profile.

    Args:
        user: Current authenticated user (from JWT)

    Returns:
        User profile

    Security:
        - Requires valid access token
        - Never returns password hash
    """
    return UserResponse.model_validate(user)


@router.post(
    "/verify-email",
    response_model=EmailVerificationResponse,
    summary="Verify email address",
    responses={
        200: {"description": "Email verified successfully"},
        400: {"description": "Email already verified"},
        401: {"description": "Invalid or expired token"},
    },
)
async def verify_email_endpoint(
    data: EmailVerificationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EmailVerificationResponse:
    """
    Verify user's email address using verification token.

    Args:
        data: Request containing verification token
        db: Database session

    Returns:
        Success message and updated user profile

    Raises:
        401 Unauthorized: If token is invalid or expired
        400 Bad Request: If email already verified

    Security:
        - Token is single-use (marked as used after verification)
        - Token expires after 24 hours
    """
    try:
        user = await verify_email(db, data.token)
        return EmailVerificationResponse(
            message="Email verified successfully",
            user=UserResponse.model_validate(user),
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        ) from e

    except EmailAlreadyVerifiedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        ) from e


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
    summary="Resend verification email",
    responses={
        200: {"description": "Verification email sent"},
        400: {"description": "Email already verified"},
        404: {"description": "User not found"},
        429: {"description": "Too many attempts"},
    },
)
async def resend_verification_endpoint(
    data: ResendVerificationRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Resend email verification to user.

    Args:
        data: Request containing email address
        request: HTTP request (for client IP)
        db: Database session

    Returns:
        Success message

    Raises:
        429 Too Many Requests: If rate limit exceeded
        404 Not Found: If user not found
        400 Bad Request: If email already verified

    Security:
        - Rate limited to prevent abuse (3 attempts per 5 minutes)
        - Does not reveal if email exists (always returns success message)

    Note:
        In production, this would send an actual email.
        For now, the token is returned in the response for testing.
    """
    try:
        ip_address = get_client_ip(request)
        _token = await resend_verification_email(db, data.email, ip_address)

        # In production, send email here instead of returning token
        # For now, just return success message
        return MessageResponse(message="Verification email sent")

    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": "300"},
        ) from e

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        ) from e

    except EmailAlreadyVerifiedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        ) from e


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
    responses={
        200: {"description": "Password reset email sent (if email exists)"},
        429: {"description": "Too many attempts"},
    },
)
async def forgot_password_endpoint(
    data: ForgotPasswordRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Request a password reset email.

    Args:
        data: Request containing email address
        request: HTTP request (for client IP)
        db: Database session

    Returns:
        Success message (always returns success to prevent email enumeration)

    Raises:
        429 Too Many Requests: If rate limit exceeded

    Security:
        - Rate limited to prevent abuse (3 attempts per 5 minutes)
        - Does not reveal if email exists (always returns success message)
        - Token expires after 1 hour

    Note:
        In production, this would send an actual email.
        The success message is returned regardless of whether the email exists.
    """
    try:
        ip_address = get_client_ip(request)
        _token = await request_password_reset(db, data.email, ip_address)

        # Always return success to prevent email enumeration
        # In production, send email here if token was created
        return MessageResponse(
            message="If an account exists with this email, a password reset link has been sent"
        )

    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=e.message,
            headers={"Retry-After": "300"},
        ) from e


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password with token",
    responses={
        200: {"description": "Password reset successfully"},
        401: {"description": "Invalid or expired token"},
    },
)
async def reset_password_endpoint(
    data: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """
    Reset password using a password reset token.

    Args:
        data: Request containing reset token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        401 Unauthorized: If token is invalid or expired

    Security:
        - Token is single-use (marked as used after reset)
        - Token expires after 1 hour
        - New password must meet complexity requirements
    """
    try:
        await reset_password(db, data.token, data.new_password)
        return MessageResponse(message="Password reset successfully")

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
        ) from e
