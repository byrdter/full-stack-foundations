"""
Shared security utilities.

This module provides security primitives used across 3+ features.
All utilities follow type-safe patterns and include comprehensive logging.

Pattern: Security utilities are shared only after being used by 3+ features.
DO NOT add utilities here until they meet this threshold.

Security primitives provided:
- Password hashing and verification (bcrypt)
- HTML sanitization (XSS prevention)
- SQL identifier sanitization (SQL injection prevention)
- Rate limiting (brute force prevention)
- PII detection and redaction (data privacy)
- Secure token generation (cryptographically secure)
"""

import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import NewType, Pattern

import bleach
from passlib.context import CryptContext

from app.core.logging import get_logger

logger = get_logger(__name__)

# ============================================================================
# TYPE-SAFE SECURITY PRIMITIVES
# ============================================================================

PlainPassword = NewType("PlainPassword", str)
"""Plain text password (never log, never store)."""

HashedPassword = NewType("HashedPassword", str)
"""Bcrypt hashed password (safe to store)."""

SanitizedHTML = NewType("SanitizedHTML", str)
"""HTML that has been sanitized to prevent XSS."""

SafeSQLIdentifier = NewType("SafeSQLIdentifier", str)
"""SQL identifier that has been validated (table/column name)."""

SecureToken = NewType("SecureToken", str)
"""Cryptographically secure random token."""


# ============================================================================
# PASSWORD HASHING
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: PlainPassword) -> HashedPassword:
    """
    Hash a plain password using bcrypt.

    Used by: users/, admin/, auth/

    Args:
        plain_password: Plain text password (will NOT be logged)

    Returns:
        Bcrypt hashed password safe to store in database

    Example:
        >>> plain = PlainPassword("mysecretpassword123")
        >>> hashed = hash_password(plain)
        >>> isinstance(hashed, str)
        True
        >>> hashed.startswith("$2b$")  # Bcrypt hash prefix
        True

    Security:
        - Uses bcrypt with automatic salt generation
        - Configured for high cost factor (secure but performant)
        - Plain password is NEVER logged
    """
    hashed = pwd_context.hash(str(plain_password))
    logger.info("security.password_hashed")
    return HashedPassword(hashed)


def verify_password(
    plain_password: PlainPassword, hashed_password: HashedPassword
) -> bool:
    """
    Verify a plain password against a bcrypt hash.

    Used by: auth/, users/, admin/

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash from database

    Returns:
        True if password matches, False otherwise

    Example:
        >>> plain = PlainPassword("mysecretpassword123")
        >>> hashed = hash_password(plain)
        >>> verify_password(plain, hashed)
        True
        >>> verify_password(PlainPassword("wrongpassword"), hashed)
        False

    Security:
        - Timing-safe comparison (prevents timing attacks)
        - Plain password is NEVER logged
        - Failed attempts should be rate limited by caller
    """
    is_valid: bool = pwd_context.verify(str(plain_password), str(hashed_password))

    if is_valid:
        logger.info("security.password_verified", result="valid")
    else:
        logger.warning("security.password_verified", result="invalid")

    return is_valid


# ============================================================================
# HTML SANITIZATION (XSS PREVENTION)
# ============================================================================

ALLOWED_HTML_TAGS = ["p", "br", "strong", "em", "ul", "ol", "li", "a", "code", "pre"]
ALLOWED_HTML_ATTRIBUTES = {"a": ["href", "title"]}


def sanitize_html(raw_html: str) -> SanitizedHTML:
    """
    Sanitize HTML to prevent XSS attacks.

    Used by: users/, comments/, posts/

    Args:
        raw_html: Untrusted HTML from user input

    Returns:
        Sanitized HTML safe to render in browser

    Example:
        >>> raw = '<script>alert("XSS")</script><p>Hello</p>'
        >>> clean = sanitize_html(raw)
        >>> clean
        SanitizedHTML('&lt;script&gt;alert("XSS")&lt;/script&gt;<p>Hello</p>')

    Security:
        - Removes all script tags
        - Removes event handlers (onclick, onerror, etc.)
        - Allows only whitelisted tags and attributes
        - Strips all other HTML
    """
    clean = bleach.clean(
        raw_html,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        strip=True,
    )

    if raw_html != clean:
        logger.warning(
            "security.html_sanitized",
            original_length=len(raw_html),
            sanitized_length=len(clean),
            tags_removed=True,
        )
    else:
        logger.info("security.html_sanitized", tags_removed=False)

    return SanitizedHTML(clean)


# ============================================================================
# SQL IDENTIFIER SANITIZATION (SQL INJECTION PREVENTION)
# ============================================================================

# Regex: SQL identifiers must be alphanumeric + underscore, start with letter
SAFE_SQL_IDENTIFIER_PATTERN: Pattern[str] = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")


def sanitize_sql_identifier(identifier: str) -> SafeSQLIdentifier:
    """
    Validate SQL identifier (table or column name) to prevent SQL injection.

    Used by: dynamic query builders (use sparingly!)

    Args:
        identifier: SQL table or column name

    Returns:
        Validated SQL identifier

    Raises:
        ValueError: If identifier contains invalid characters

    Example:
        >>> sanitize_sql_identifier("users")
        SafeSQLIdentifier('users')
        >>> sanitize_sql_identifier("user_profiles")
        SafeSQLIdentifier('user_profiles')
        >>> sanitize_sql_identifier("users; DROP TABLE")
        Traceback (most recent call last):
        ...
        ValueError: Invalid SQL identifier: must be alphanumeric + underscore

    Security:
        - NEVER use user input directly in SQL identifiers
        - Always validate with this function first
        - Prefer parameterized queries over dynamic SQL
        - This is a LAST RESORT - avoid dynamic SQL when possible

    Warning:
        This function should be used SPARINGLY. In 99% of cases,
        you should use parameterized queries with SQLAlchemy instead.
    """
    if not SAFE_SQL_IDENTIFIER_PATTERN.match(identifier):
        logger.error(
            "security.sql_injection_attempted",
            identifier=identifier,
            pattern="invalid_characters",
        )
        raise ValueError(
            f"Invalid SQL identifier '{identifier}': "
            "must be alphanumeric + underscore, start with letter"
        )

    logger.info("security.sql_identifier_validated", identifier=identifier)
    return SafeSQLIdentifier(identifier)


# ============================================================================
# RATE LIMITING (BRUTE FORCE PREVENTION)
# ============================================================================


class RateLimiter:
    """
    Rate limiter for preventing brute force attacks.

    Used by: auth/, api/, webhooks/

    Example:
        >>> limiter = RateLimiter(max_attempts=5, window_seconds=300)
        >>> limiter.check_limit("user@example.com", "192.168.1.1")
        True
        >>> for _ in range(5):
        ...     limiter.record_attempt("user@example.com", "192.168.1.1")
        >>> limiter.check_limit("user@example.com", "192.168.1.1")
        False

    Security:
        - Tracks attempts per identifier + IP address
        - Prevents credential stuffing
        - Prevents brute force attacks
        - Logs all rate limit violations

    Implementation note:
        This is a simple in-memory implementation.
        For production, use Redis or similar distributed cache.
    """

    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 300,
    ) -> None:
        """
        Initialize rate limiter.

        Args:
            max_attempts: Maximum attempts allowed in window
            window_seconds: Time window in seconds (default: 5 minutes)
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        # Key: (identifier, ip_address) -> list of attempt timestamps
        self._attempts: dict[tuple[str, str], list[datetime]] = {}

        logger.info(
            "security.rate_limiter_initialized",
            max_attempts=max_attempts,
            window_seconds=window_seconds,
        )

    def _get_key(self, identifier: str, ip_address: str) -> tuple[str, str]:
        """Get cache key for identifier + IP combination."""
        return (identifier, ip_address)

    def _clean_old_attempts(self, key: tuple[str, str]) -> None:
        """Remove attempts outside the time window."""
        if key not in self._attempts:
            return

        cutoff = datetime.now(timezone.utc) - timedelta(seconds=self.window_seconds)
        self._attempts[key] = [
            attempt for attempt in self._attempts[key] if attempt > cutoff
        ]

        if not self._attempts[key]:
            del self._attempts[key]

    def check_limit(self, identifier: str, ip_address: str) -> bool:
        """
        Check if identifier + IP is within rate limit.

        Args:
            identifier: User identifier (email, username, etc.)
            ip_address: Client IP address

        Returns:
            True if within limit, False if limit exceeded

        Example:
            >>> limiter = RateLimiter(max_attempts=3, window_seconds=60)
            >>> limiter.check_limit("test@example.com", "127.0.0.1")
            True
        """
        key = self._get_key(identifier, ip_address)
        self._clean_old_attempts(key)

        if key not in self._attempts:
            return True

        attempt_count = len(self._attempts[key])
        is_within_limit = attempt_count < self.max_attempts

        if not is_within_limit:
            logger.warning(
                "security.rate_limit_exceeded",
                identifier=identifier,
                ip_address=ip_address,
                attempt_count=attempt_count,
                max_attempts=self.max_attempts,
            )

        return is_within_limit

    def record_attempt(self, identifier: str, ip_address: str) -> None:
        """
        Record an attempt for identifier + IP.

        Args:
            identifier: User identifier (email, username, etc.)
            ip_address: Client IP address

        Example:
            >>> limiter = RateLimiter()
            >>> limiter.record_attempt("test@example.com", "127.0.0.1")
        """
        key = self._get_key(identifier, ip_address)
        self._clean_old_attempts(key)

        if key not in self._attempts:
            self._attempts[key] = []

        self._attempts[key].append(datetime.now(timezone.utc))

        logger.info(
            "security.rate_limit_attempt_recorded",
            identifier=identifier,
            ip_address=ip_address,
            total_attempts=len(self._attempts[key]),
        )

    def reset(self, identifier: str, ip_address: str) -> None:
        """
        Reset rate limit for identifier + IP (e.g., after successful login).

        Args:
            identifier: User identifier
            ip_address: Client IP address

        Example:
            >>> limiter = RateLimiter()
            >>> limiter.reset("test@example.com", "127.0.0.1")
        """
        key = self._get_key(identifier, ip_address)
        if key in self._attempts:
            del self._attempts[key]
            logger.info(
                "security.rate_limit_reset",
                identifier=identifier,
                ip_address=ip_address,
            )


# ============================================================================
# PII DETECTION (DATA PRIVACY)
# ============================================================================

# Regex patterns for common PII
EMAIL_PATTERN: Pattern[str] = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)
PHONE_PATTERN: Pattern[str] = re.compile(
    r"\b(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"
)
SSN_PATTERN: Pattern[str] = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CREDIT_CARD_PATTERN: Pattern[str] = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")


def contains_pii(text: str) -> bool:
    """
    Check if text contains Personally Identifiable Information (PII).

    Used by: logging/, audit/, data_export/

    Args:
        text: Text to check for PII

    Returns:
        True if PII detected, False otherwise

    Example:
        >>> contains_pii("My email is test@example.com")
        True
        >>> contains_pii("The product costs $19.99")
        False

    Security:
        - Detects emails, phone numbers, SSNs, credit cards
        - Use this before logging user-generated content
        - GDPR/CCPA compliance helper

    Warning:
        This is not 100% accurate. Use as a safety check,
        not as the sole PII detection mechanism.
    """
    patterns_checked = 0
    pii_found = False

    if EMAIL_PATTERN.search(text):
        pii_found = True
        patterns_checked += 1

    if PHONE_PATTERN.search(text):
        pii_found = True
        patterns_checked += 1

    if SSN_PATTERN.search(text):
        pii_found = True
        patterns_checked += 1

    if CREDIT_CARD_PATTERN.search(text):
        pii_found = True
        patterns_checked += 1

    if pii_found:
        logger.warning("security.pii_detected", patterns_matched=patterns_checked)

    return pii_found


def redact_pii(text: str) -> str:
    """
    Redact PII from text (replace with [REDACTED]).

    Used by: logging/, audit/, error_reporting/

    Args:
        text: Text potentially containing PII

    Returns:
        Text with PII redacted

    Example:
        >>> redact_pii("Email: test@example.com, Phone: 555-123-4567")
        'Email: [REDACTED_EMAIL], Phone: [REDACTED_PHONE]'

    Security:
        - Redacts emails, phone numbers, SSNs, credit cards
        - Safe to log redacted output
        - GDPR/CCPA compliance helper
    """
    redacted = text

    # Redact emails
    redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", redacted)

    # Redact phone numbers
    redacted = PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)

    # Redact SSNs
    redacted = SSN_PATTERN.sub("[REDACTED_SSN]", redacted)

    # Redact credit cards
    redacted = CREDIT_CARD_PATTERN.sub("[REDACTED_CREDIT_CARD]", redacted)

    if text != redacted:
        logger.info("security.pii_redacted")

    return redacted


# ============================================================================
# SECURE TOKEN GENERATION
# ============================================================================


def generate_secure_token(length: int = 32) -> SecureToken:
    """
    Generate cryptographically secure random token.

    Used by: auth/, password_reset/, api_keys/

    Args:
        length: Token length in bytes (default: 32 = 256 bits)

    Returns:
        Hex-encoded secure random token

    Example:
        >>> token = generate_secure_token(16)
        >>> len(token)
        32  # 16 bytes = 32 hex characters
        >>> isinstance(token, str)
        True

    Security:
        - Uses secrets module (cryptographically secure)
        - NOT random.Random() (predictable, insecure)
        - Suitable for password reset tokens, API keys, session tokens
        - 32 bytes = 256 bits of entropy (recommended minimum)
    """
    token = secrets.token_hex(length)

    logger.info(
        "security.token_generated",
        length_bytes=length,
        length_hex=len(token),
    )

    return SecureToken(token)


def generate_secure_password(length: int = 16) -> PlainPassword:
    """
    Generate cryptographically secure random password.

    Used by: user_creation/, password_reset/, admin/

    Args:
        length: Password length in characters (default: 16)

    Returns:
        Secure random password

    Example:
        >>> password = generate_secure_password(12)
        >>> len(password) >= 12
        True

    Security:
        - Uses secrets module (cryptographically secure)
        - Contains uppercase, lowercase, digits, punctuation
        - Minimum recommended length: 12 characters
    """
    import string

    alphabet = string.ascii_letters + string.digits + string.punctuation
    password_chars = [secrets.choice(alphabet) for _ in range(length)]
    password = "".join(password_chars)

    logger.info("security.password_generated", length=length)

    return PlainPassword(password)
