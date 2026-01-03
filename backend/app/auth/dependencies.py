"""
Authentication dependencies for FastAPI.

This module provides:
- get_current_user: Require authenticated user
- get_current_user_optional: Allow anonymous access
- require_role: Factory for role-based authorization

Pattern: FastAPI Depends() for route-level authentication.

Security:
    - Validates JWT access tokens
    - Checks user is active
    - Enforces role-based access control
"""

from collections.abc import Callable, Coroutine
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_access_token
from app.auth.models import User, UserRole
from app.core.database import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Optional OAuth2 scheme (returns None if no token)
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        token: JWT access token from Authorization header
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException 401: If token is invalid or user not found
        HTTPException 401: If user is not active

    Usage:
        @router.get("/protected")
        async def protected_route(
            user: Annotated[User, Depends(get_current_user)]
        ):
            return {"user_id": user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("auth.authentication_failed", reason="invalid_token")
        raise credentials_exception

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == payload.user_id))
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning(
            "auth.authentication_failed",
            reason="user_not_found",
            user_id=payload.user_id,
        )
        raise credentials_exception

    # Check user is active
    if not user.is_active:
        logger.warning(
            "auth.authentication_failed",
            reason="user_inactive",
            user_id=user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(
        "auth.user_authenticated",
        user_id=user.id,
        role=user.role.value,
    )

    return user


async def get_current_user_optional(
    token: Annotated[str | None, Depends(oauth2_scheme_optional)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """
    Get the current user if authenticated, otherwise None.

    Use this for routes that work with or without authentication,
    providing different behavior based on auth status.

    Args:
        token: Optional JWT access token
        db: Database session

    Returns:
        User if authenticated, None otherwise

    Usage:
        @router.get("/public")
        async def public_route(
            user: Annotated[User | None, Depends(get_current_user_optional)]
        ):
            if user:
                return {"message": f"Hello {user.email}"}
            return {"message": "Hello anonymous"}
    """
    if token is None:
        return None

    # Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        return None

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == payload.user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        return None

    return user


def require_role(
    allowed_roles: list[UserRole],
) -> Callable[[User], Coroutine[Any, Any, User]]:
    """
    Factory function to create role-checking dependencies.

    Args:
        allowed_roles: List of roles that are allowed access

    Returns:
        Dependency function that checks user role

    Raises:
        HTTPException 403: If user's role is not in allowed_roles

    Usage:
        # Single role
        @router.get("/admin-only")
        async def admin_route(
            user: Annotated[User, Depends(require_role([UserRole.admin]))]
        ):
            return {"message": "Admin access granted"}

        # Multiple roles
        @router.get("/admin-or-superadmin")
        async def admin_route(
            user: Annotated[User, Depends(require_role([UserRole.admin, UserRole.superadmin]))]
        ):
            return {"message": "Elevated access granted"}
    """

    async def role_checker(
        user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if user.role not in allowed_roles:
            logger.warning(
                "auth.authorization_failed",
                user_id=user.id,
                user_role=user.role.value,
                required_roles=[r.value for r in allowed_roles],
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        logger.info(
            "auth.authorization_granted",
            user_id=user.id,
            user_role=user.role.value,
        )

        return user

    return role_checker


# Convenience dependencies for common role checks
require_admin = require_role([UserRole.admin, UserRole.superadmin])
require_superadmin = require_role([UserRole.superadmin])
