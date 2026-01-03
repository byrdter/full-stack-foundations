"""
Authentication feature module.

This module provides complete authentication functionality:
- User registration and login
- JWT access tokens + refresh token rotation
- Role-based access control (user, admin, superadmin)
- Password reset and email verification (Phase 2-3)
- OAuth2 providers (Phase 4)

Pattern: Vertical slice architecture - all auth components in one feature.
"""

from app.auth.dependencies import get_current_user, get_current_user_optional, require_role
from app.auth.models import (
    EmailVerificationToken,
    PasswordResetToken,
    RefreshToken,
    User,
    UserRole,
)
from app.auth.routes import router

__all__ = [
    "EmailVerificationToken",
    "PasswordResetToken",
    "RefreshToken",
    "User",
    "UserRole",
    "get_current_user",
    "get_current_user_optional",
    "require_role",
    "router",
]
