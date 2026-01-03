"""
JWT token utilities for authentication.

This module provides:
- Access token creation and validation (JWT)
- Refresh token generation (secure random, not JWT)
- Token hashing for database storage

Security:
    - Access tokens: Short-lived JWT with user_id and role
    - Refresh tokens: Long-lived secure random, stored as SHA256 hash
    - Never log token values, only metadata
"""

import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.auth.models import UserRole
from app.core.config import get_settings
from app.core.logging import get_logger
from app.shared.security import SecureToken, generate_secure_token

logger = get_logger(__name__)


class TokenPayload:
    """
    Decoded JWT access token payload.

    Attributes:
        user_id: User's database ID
        role: User's role for authorization
        exp: Token expiration time
        iat: Token issued at time
        jti: Unique token identifier
    """

    def __init__(
        self,
        user_id: int,
        role: UserRole,
        exp: datetime,
        iat: datetime,
        jti: str,
    ) -> None:
        self.user_id = user_id
        self.role = role
        self.exp = exp
        self.iat = iat
        self.jti = jti


def create_access_token(
    user_id: int,
    role: UserRole,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User's database ID
        role: User's role for authorization
        expires_delta: Custom expiration time (default: from settings)

    Returns:
        Encoded JWT access token string

    Security:
        - Short-lived (default 15 minutes)
        - Contains user_id and role for stateless auth
        - Signed with HS256 algorithm
    """
    settings = get_settings()

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    now = datetime.now(UTC)
    expire = now + expires_delta
    jti = generate_secure_token(16)  # Unique token ID

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role.value,
        "exp": expire,
        "iat": now,
        "jti": jti,
    }

    token: str = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    logger.info(
        "auth.access_token_created",
        user_id=user_id,
        role=role.value,
        expires_in_minutes=expires_delta.total_seconds() / 60,
    )

    return token


def decode_access_token(token: str) -> TokenPayload | None:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT access token string

    Returns:
        TokenPayload if valid, None if invalid or expired

    Security:
        - Validates signature
        - Checks expiration
        - Logs validation failures
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        user_id = int(payload["sub"])
        role = UserRole(payload["role"])
        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat = datetime.fromtimestamp(payload["iat"], tz=UTC)
        jti = payload["jti"]

        logger.info(
            "auth.access_token_validated",
            user_id=user_id,
            role=role.value,
        )

        return TokenPayload(
            user_id=user_id,
            role=role,
            exp=exp,
            iat=iat,
            jti=jti,
        )

    except JWTError as e:
        logger.warning(
            "auth.access_token_invalid",
            error=str(e),
            error_type=type(e).__name__,
        )
        return None

    except (KeyError, ValueError) as e:
        logger.warning(
            "auth.access_token_malformed",
            error=str(e),
            error_type=type(e).__name__,
        )
        return None


def create_refresh_token() -> SecureToken:
    """
    Create a secure refresh token.

    Returns:
        Cryptographically secure random token (hex encoded)

    Security:
        - NOT a JWT (opaque token)
        - 32 bytes = 256 bits of entropy
        - Must be stored as SHA256 hash in database
        - Client receives raw token, server stores hash

    Note:
        Use hash_token() before storing in database.
    """
    token = generate_secure_token(32)

    logger.info("auth.refresh_token_created")

    return token


def hash_token(token: str) -> str:
    """
    Hash a token for secure database storage.

    Args:
        token: Raw token string

    Returns:
        SHA256 hex digest (64 characters)

    Security:
        - One-way hash (cannot recover original)
        - Used for refresh tokens and password reset tokens
        - Client keeps raw token, server stores hash
    """
    return hashlib.sha256(token.encode()).hexdigest()


def get_refresh_token_expiry() -> datetime:
    """
    Get expiration datetime for a new refresh token.

    Returns:
        Datetime when refresh token should expire

    Security:
        - Default 7 days (configurable via settings)
        - Long-lived but revocable
    """
    settings = get_settings()
    return datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
