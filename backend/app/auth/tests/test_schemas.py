"""
Authentication schema tests.

Tests validation logic for:
- UserRegisterRequest: Email format, password complexity
- UserLoginRequest: Basic validation
- TokenRefreshRequest: Token presence

Pattern: Use pytest.raises for validation error testing.
"""

import pytest
from pydantic import ValidationError

from app.auth.schemas import (
    ChangePasswordRequest,
    EmailVerificationRequest,
    ResendVerificationRequest,
    TokenRefreshRequest,
    UserLoginRequest,
    UserRegisterRequest,
)


class TestUserRegisterRequest:
    """Tests for registration request schema."""

    def test_valid_registration(self):
        """Valid registration data should pass validation."""
        data = UserRegisterRequest(
            email="test@example.com",
            password="SecurePass123",
        )
        assert data.email == "test@example.com"
        assert data.password == "SecurePass123"

    def test_invalid_email_format(self):
        """Invalid email format should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(email="not-an-email", password="SecurePass123")

        errors = exc_info.value.errors()
        assert any("email" in str(e["loc"]) for e in errors)

    def test_password_too_short(self):
        """Password less than 8 characters should fail."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(email="test@example.com", password="Short1")

        errors = exc_info.value.errors()
        assert any("password" in str(e["loc"]) for e in errors)

    @pytest.mark.security
    def test_password_requires_uppercase(self):
        """Password without uppercase should fail."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(email="test@example.com", password="lowercase123")

        errors = exc_info.value.errors()
        assert any("uppercase" in str(e["msg"]).lower() for e in errors)

    @pytest.mark.security
    def test_password_requires_lowercase(self):
        """Password without lowercase should fail."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(email="test@example.com", password="UPPERCASE123")

        errors = exc_info.value.errors()
        assert any("lowercase" in str(e["msg"]).lower() for e in errors)

    @pytest.mark.security
    def test_password_requires_digit(self):
        """Password without digit should fail."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(email="test@example.com", password="NoDigitsHere")

        errors = exc_info.value.errors()
        assert any("digit" in str(e["msg"]).lower() for e in errors)

    @pytest.mark.security
    def test_password_max_length(self):
        """Password exceeding max length should fail."""
        long_password = "A" * 129 + "a1"  # 131 chars, exceeds 128
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(email="test@example.com", password=long_password)

        errors = exc_info.value.errors()
        assert len(errors) > 0


class TestUserLoginRequest:
    """Tests for login request schema."""

    def test_valid_login(self):
        """Valid login data should pass validation."""
        data = UserLoginRequest(
            email="test@example.com",
            password="anypassword",
        )
        assert data.email == "test@example.com"
        assert data.password == "anypassword"

    def test_invalid_email_format(self):
        """Invalid email should fail."""
        with pytest.raises(ValidationError):
            UserLoginRequest(email="not-an-email", password="password")

    def test_empty_password(self):
        """Empty password should fail."""
        with pytest.raises(ValidationError):
            UserLoginRequest(email="test@example.com", password="")


class TestTokenRefreshRequest:
    """Tests for token refresh request schema."""

    def test_valid_refresh_request(self):
        """Valid refresh token should pass."""
        data = TokenRefreshRequest(refresh_token="some-token-value")
        assert data.refresh_token == "some-token-value"

    def test_empty_refresh_token(self):
        """Empty refresh token should fail."""
        with pytest.raises(ValidationError):
            TokenRefreshRequest(refresh_token="")


class TestChangePasswordRequest:
    """Tests for password change request schema."""

    def test_valid_password_change(self):
        """Valid password change should pass."""
        data = ChangePasswordRequest(
            current_password="oldpassword",
            new_password="NewSecure123",
        )
        assert data.current_password == "oldpassword"
        assert data.new_password == "NewSecure123"

    @pytest.mark.security
    def test_new_password_requires_complexity(self):
        """New password must meet complexity requirements."""
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(
                current_password="oldpassword",
                new_password="weakpassword",  # No uppercase or digit
            )

        errors = exc_info.value.errors()
        assert len(errors) > 0


class TestEmailVerificationRequest:
    """Tests for email verification request schema."""

    def test_valid_verification_request(self):
        """Valid verification token should pass."""
        data = EmailVerificationRequest(token="some-verification-token")
        assert data.token == "some-verification-token"

    def test_empty_token(self):
        """Empty token should fail."""
        with pytest.raises(ValidationError):
            EmailVerificationRequest(token="")


class TestResendVerificationRequest:
    """Tests for resend verification request schema."""

    def test_valid_resend_request(self):
        """Valid email should pass."""
        data = ResendVerificationRequest(email="test@example.com")
        assert data.email == "test@example.com"

    def test_invalid_email_format(self):
        """Invalid email should fail."""
        with pytest.raises(ValidationError):
            ResendVerificationRequest(email="not-an-email")
