"""
JWT utility tests.

Tests for:
- Access token creation and decoding
- Refresh token generation
- Token hashing

Pattern: Unit tests with mocked settings for deterministic behavior.
"""

import os
from datetime import timedelta
from unittest.mock import patch

import pytest

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_token,
)
from app.auth.models import UserRole


# Set test JWT secret before importing anything that uses settings
@pytest.fixture(autouse=True)
def _set_jwt_secret():
    """Set JWT secret for testing."""
    with patch.dict(os.environ, {"JWT_SECRET_KEY": "test-secret-key-for-testing-only"}):
        yield


class TestAccessToken:
    """Tests for access token creation and validation."""

    def test_create_access_token(self):
        """Should create a valid JWT access token."""
        token = create_access_token(user_id=1, role=UserRole.user)

        assert isinstance(token, str)
        assert len(token) > 0
        # JWT format: header.payload.signature
        assert token.count(".") == 2

    def test_decode_valid_access_token(self):
        """Should decode a valid access token."""
        token = create_access_token(user_id=42, role=UserRole.admin)
        payload = decode_access_token(token)

        assert payload is not None
        assert payload.user_id == 42
        assert payload.role == UserRole.admin
        assert payload.jti is not None

    def test_decode_invalid_token(self):
        """Should return None for invalid token."""
        payload = decode_access_token("invalid.token.here")

        assert payload is None

    def test_decode_malformed_token(self):
        """Should return None for malformed token."""
        payload = decode_access_token("not-a-jwt-at-all")

        assert payload is None

    def test_decode_empty_token(self):
        """Should return None for empty token."""
        payload = decode_access_token("")

        assert payload is None

    def test_token_with_custom_expiry(self):
        """Should create token with custom expiry."""
        token = create_access_token(
            user_id=1,
            role=UserRole.user,
            expires_delta=timedelta(hours=1),
        )

        payload = decode_access_token(token)
        assert payload is not None


class TestRefreshToken:
    """Tests for refresh token generation."""

    def test_create_refresh_token(self):
        """Should create a secure refresh token."""
        token = create_refresh_token()

        assert isinstance(token, str)
        # 32 bytes = 64 hex characters
        assert len(token) == 64

    def test_refresh_tokens_are_unique(self):
        """Each refresh token should be unique."""
        tokens = [create_refresh_token() for _ in range(10)]

        # All tokens should be unique
        assert len(set(tokens)) == 10


class TestTokenHashing:
    """Tests for token hashing."""

    def test_hash_token(self):
        """Should hash token to SHA256."""
        token = "test-token-value"
        hashed = hash_token(token)

        # SHA256 = 64 hex characters
        assert len(hashed) == 64
        assert hashed != token

    def test_hash_is_deterministic(self):
        """Same token should produce same hash."""
        token = "test-token-value"
        hash1 = hash_token(token)
        hash2 = hash_token(token)

        assert hash1 == hash2

    def test_different_tokens_different_hashes(self):
        """Different tokens should produce different hashes."""
        hash1 = hash_token("token-one")
        hash2 = hash_token("token-two")

        assert hash1 != hash2

    @pytest.mark.security
    def test_hash_is_one_way(self):
        """Hash should not reveal original token."""
        token = "sensitive-token"
        hashed = hash_token(token)

        # Token should not appear in hash
        assert token not in hashed
