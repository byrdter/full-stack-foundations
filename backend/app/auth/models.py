"""
Authentication database models.

This module defines:
- User: Core user account with email/password and role
- RefreshToken: Stored refresh tokens for JWT rotation
- EmailVerificationToken: Tokens for email verification
- PasswordResetToken: Tokens for password reset
- UserRole: Enum for role-based access control

Pattern: SQLAlchemy 2.0 style with Mapped types and TimestampMixin.

Security:
    - Passwords stored as bcrypt hashes (never plain text)
    - Refresh tokens stored as SHA256 hashes
    - Email verification tokens stored as SHA256 hashes
    - Password reset tokens stored as SHA256 hashes
    - is_active controls account access
    - is_email_verified tracks email confirmation
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.models import TimestampMixin


class UserRole(str, Enum):
    """
    User role for access control.

    Roles:
        user: Standard user (default)
        admin: Administrative access
        superadmin: Full system access
    """

    user = "user"
    admin = "admin"
    superadmin = "superadmin"


class User(Base, TimestampMixin):
    """
    User account model.

    Security:
        - password_hash: bcrypt hash, never stores plain password
        - is_active: False until email verified (prevents login)
        - is_email_verified: Tracks email confirmation status
        - role: Controls feature access

    Lifecycle:
        - created_at: Set on INSERT (via TimestampMixin)
        - updated_at: Updated on UPDATE (via TimestampMixin)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole),
        default=UserRole.user,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<User(id={self.id}, email='{self.email}', role={self.role.value})>"


class RefreshToken(Base, TimestampMixin):
    """
    Stored refresh token for JWT rotation.

    Security:
        - token_hash: SHA256 hash, never stores raw token
        - is_revoked: Set True on logout or rotation
        - expires_at: Token expiration time
        - device_info: Optional client info for multi-device tracking

    Pattern:
        - Client receives raw token
        - Server stores SHA256 hash
        - On refresh: validate hash, revoke old, issue new
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token_hash: Mapped[str] = mapped_column(
        String(64),  # SHA256 = 64 hex chars
        unique=True,
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    device_info: Mapped[str | None] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<RefreshToken(id={self.id}, user_id={self.user_id}, "
            f"revoked={self.is_revoked})>"
        )


class EmailVerificationToken(Base, TimestampMixin):
    """
    Token for email address verification.

    Security:
        - token_hash: SHA256 hash, never stores raw token
        - is_used: Set True after successful verification (single-use)
        - expires_at: Token expiration (24 hours from creation)

    Pattern:
        - User receives raw token via email
        - Server stores SHA256 hash
        - On verification: validate hash, mark used, verify user email
    """

    __tablename__ = "email_verification_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token_hash: Mapped[str] = mapped_column(
        String(64),  # SHA256 = 64 hex chars
        unique=True,
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<EmailVerificationToken(id={self.id}, user_id={self.user_id}, "
            f"used={self.is_used})>"
        )


class PasswordResetToken(Base, TimestampMixin):
    """
    Token for password reset.

    Security:
        - token_hash: SHA256 hash, never stores raw token
        - is_used: Set True after successful reset (single-use)
        - expires_at: Token expiration (1 hour from creation)

    Pattern:
        - User requests reset, receives raw token via email
        - Server stores SHA256 hash
        - On reset: validate hash, mark used, update password
    """

    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    token_hash: Mapped[str] = mapped_column(
        String(64),  # SHA256 = 64 hex chars
        unique=True,
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, "
            f"used={self.is_used})>"
        )
