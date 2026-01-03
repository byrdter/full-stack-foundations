"""
Authentication request/response schemas.

This module defines Pydantic models for:
- User registration and login requests
- Token responses
- User profile responses

Pattern: Separate request and response schemas for clear API contracts.

Security:
    - Password validation (min length, complexity)
    - Email format validation
    - No password in response schemas
"""

import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.auth.models import UserRole

# =============================================================================
# REQUEST SCHEMAS
# =============================================================================


class UserRegisterRequest(BaseModel):
    """
    User registration request.

    Security:
        - Email validated for proper format
        - Password requires min 8 chars with complexity
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """
        Validate password meets complexity requirements.

        Requirements:
            - At least 8 characters (enforced by Field)
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one digit

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLoginRequest(BaseModel):
    """
    User login request.

    Note: Minimal validation here - actual auth happens in service layer.
    """

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")


class TokenRefreshRequest(BaseModel):
    """
    Token refresh request.

    Security:
        - Refresh token is validated server-side
        - Old token is revoked on successful refresh
    """

    refresh_token: str = Field(..., min_length=1, description="Current refresh token")


class ChangePasswordRequest(BaseModel):
    """
    Password change request (authenticated users).

    Security:
        - Requires current password verification
        - New password must meet complexity requirements
    """

    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_new_password_complexity(cls, v: str) -> str:
        """Validate new password meets complexity requirements."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class EmailVerificationRequest(BaseModel):
    """
    Email verification request.

    Security:
        - Token is validated server-side
        - Token is single-use (marked as used after verification)
    """

    token: str = Field(..., min_length=1, description="Email verification token")


class ResendVerificationRequest(BaseModel):
    """
    Request to resend verification email.

    Rate limited to prevent abuse.
    """

    email: EmailStr = Field(..., description="Email address to resend verification to")


class ForgotPasswordRequest(BaseModel):
    """
    Request to initiate password reset.

    Rate limited to prevent abuse.
    """

    email: EmailStr = Field(..., description="Email address for password reset")


class ResetPasswordRequest(BaseModel):
    """
    Password reset request with token.

    Security:
        - Token is validated server-side
        - Token is single-use
        - New password must meet complexity requirements
    """

    token: str = Field(..., min_length=1, description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    @field_validator("new_password")
    @classmethod
    def validate_new_password_complexity(cls, v: str) -> str:
        """Validate new password meets complexity requirements."""
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class UserResponse(BaseModel):
    """
    User profile response.

    Security:
        - Never includes password_hash
        - Safe to return to client
    """

    id: int
    email: str
    role: UserRole
    is_active: bool
    is_email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    Authentication token response.

    Contains:
        - access_token: Short-lived JWT for API auth
        - refresh_token: Long-lived token for getting new access tokens
        - token_type: Always "bearer"
        - expires_in: Access token lifetime in seconds
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token lifetime in seconds")


class MessageResponse(BaseModel):
    """
    Simple message response for operations that don't return data.

    Used for: logout confirmation, password change confirmation, etc.
    """

    message: str


class AuthErrorResponse(BaseModel):
    """
    Authentication error response.

    Provides consistent error format for auth failures.
    """

    detail: str
    error_code: str | None = None


class EmailVerificationResponse(BaseModel):
    """
    Email verification response.

    Returns updated user profile after email is verified.
    """

    message: str
    user: UserResponse
