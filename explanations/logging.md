# Guardrail 4: Logging (Observability Validation)

## What is Logging?

**Logging** is the practice of recording events, state changes, and diagnostic information while your application runs. Logs create a permanent record of what happened, when, and why.

Think of logs as **a flight recorder** for your application - when something goes wrong, logs help you understand what happened.

### Example: Why Logging Matters

```python
# Without logging:
def process_payment(amount, user_id):
    charge_card(amount)
    update_balance(user_id, amount)
    send_receipt(user_id)
    return {"status": "success"}

# What happens when it fails?
# - Which step failed?
# - What was the error?
# - What were the inputs?
# - How long did it take?
# YOU DON'T KNOW - no visibility!
```

```python
# With logging:
def process_payment(amount: float, user_id: int) -> dict:
    logger.info("payment.process_started",
                amount=amount,
                user_id=user_id)

    try:
        charge_card(amount)
        logger.info("payment.card_charged",
                   amount=amount,
                   user_id=user_id)

        update_balance(user_id, amount)
        logger.info("payment.balance_updated",
                   amount=amount,
                   user_id=user_id)

        send_receipt(user_id)
        logger.info("payment.receipt_sent",
                   user_id=user_id)

        logger.info("payment.process_completed",
                   amount=amount,
                   user_id=user_id)
        return {"status": "success"}

    except CardDeclinedError as e:
        logger.error("payment.card_declined",
                    amount=amount,
                    user_id=user_id,
                    error=str(e),
                    exc_info=True)
        raise
```

**Now when it fails**:
- ✅ You know which step failed (card_declined)
- ✅ You have the error message
- ✅ You have the inputs (amount, user_id)
- ✅ You have a timeline of what succeeded before the failure

## Why Logging Matters for Traditional Development

In human-led development, logging provides:

1. **Debugging** - Understand what happened when bugs occur
2. **Monitoring** - Detect issues in production
3. **Auditing** - Track user actions and system changes
4. **Performance analysis** - Identify slow operations
5. **Security** - Detect suspicious activity

### Without Logging:

```
Bug report: "Payment failed for user 12345"

Developer:
- No idea which step failed
- Can't reproduce the issue
- Asks user for more information
- User doesn't remember details
- Days wasted trying to debug
```

### With Logging:

```
Bug report: "Payment failed for user 12345"

Developer:
- Searches logs for user_id=12345
- Sees exact error: "payment.card_declined"
- Sees error message: "Insufficient funds"
- Sees it happened at 2024-01-15 14:32:15 UTC
- Fixed in 10 minutes
```

## Why Logging is CRITICAL for AI Agents (PIV Loop)

For AI agents, logging serves a fundamentally different purpose than for humans:

### The Fundamental Problem:

**AI agents cannot "remember" what they did unless it's logged.** They also cannot debug issues without reading logs.

```
Human Developer:
"I remember I changed the authentication logic yesterday."
(Has memory, intuition, context)

AI Agent:
"What did I do? What went wrong? Let me read the logs."
(Needs explicit, machine-readable records)
```

### Logging Enables Autonomous Debugging

In the **Plan-Implement-Validate** loop, logs enable **self-diagnosis and correction**:

```
┌─────────────────────────────────────────────────────────┐
│ PLAN: Add user authentication endpoint                 │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ IMPLEMENT: AI generates authentication code            │
│  - Creates login endpoint                              │
│  - Adds password verification                          │
│  - Generates JWT token                                 │
│  - Adds logging at each step                           │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ VALIDATE: Run tests                                    │
│  ❌ test_login_with_valid_credentials FAILED           │
│     AssertionError: Expected 200, got 401              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─── ❌ TEST FAILED ────────────────────┐
                   │                                       │
                   │   Agent reads test output, then       │
                   │   reads LOGS to diagnose:             │
                   │                                       │
                   │   Logs show:                          │
                   │   ✅ user.login_started (email=...)   │
                   │   ✅ user.credentials_validated       │
                   │   ❌ user.token_generation_failed     │
                   │      error="Invalid secret key"       │
                   │                                       │
                   │   Agent sees: JWT secret is wrong!    │
                   │                                       │
                   └───► BACK TO IMPLEMENT                 │
                         (Fix JWT secret configuration)    │
                                                           │
                   ┌───────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ VALIDATE: Run tests again                              │
│  ✅ test_login_with_valid_credentials PASSED           │
│                                                         │
│  Logs show:                                            │
│  ✅ user.login_started                                 │
│  ✅ user.credentials_validated                         │
│  ✅ user.token_generated                               │
│  ✅ user.login_completed                               │
└──────────────────┬──────────────────────────────────────┘
                   ▼
              ✅ ALL PASS → NEXT TASK
```

**Key Insight**: Logs provide **diagnostic information** that enables self-correction.

### What Logging Tells the AI Agent:

1. **What happened?** - Sequence of events
2. **Where did it fail?** - Exact operation that failed
3. **Why did it fail?** - Error message and stack trace
4. **What were the inputs?** - Context for reproduction
5. **How long did it take?** - Performance characteristics

## Structured Logging vs. Plain Text Logging

### Plain Text Logging (Traditional)

```python
# ❌ Plain text - hard to parse
print("User login started")
print(f"User {email} logged in successfully")
print(f"ERROR: Failed to generate token for {email}: {error}")
```

**Output**:
```
User login started
User test@example.com logged in successfully
ERROR: Failed to generate token for test@example.com: Invalid secret key
```

**Problems**:
- Hard to search (grep by email? by error type?)
- No machine-readable structure
- Can't aggregate or analyze
- Mixing formats

### Structured Logging (Modern, AI-Friendly)

```python
# ✅ Structured - machine-readable JSON
logger.info("user.login_started", email=email)
logger.info("user.login_completed", email=email, user_id=user.id)
logger.error("user.token_generation_failed",
            email=email,
            error=str(error),
            error_type="JWTError",
            exc_info=True)
```

**Output** (JSON):
```json
{
  "timestamp": "2024-01-15T14:32:15.123Z",
  "level": "info",
  "event": "user.login_started",
  "email": "test@example.com",
  "request_id": "req-abc123"
}
{
  "timestamp": "2024-01-15T14:32:15.456Z",
  "level": "info",
  "event": "user.login_completed",
  "email": "test@example.com",
  "user_id": 12345,
  "request_id": "req-abc123"
}
{
  "timestamp": "2024-01-15T14:32:15.789Z",
  "level": "error",
  "event": "user.token_generation_failed",
  "email": "test@example.com",
  "error": "Invalid secret key",
  "error_type": "JWTError",
  "request_id": "req-abc123",
  "stack_trace": "..."
}
```

**Benefits**:
- ✅ Easy to search by any field (`email`, `event`, `error_type`)
- ✅ Machine-readable (JSON)
- ✅ Consistent structure
- ✅ Can aggregate and analyze
- ✅ **AI agents can parse and understand**

## The Hybrid Dotted Namespace Pattern

This repository uses a **specific logging pattern** optimized for AI agents:

**Format**: `{domain}.{component}.{action}_{state}`

**Examples**:
- `application.lifecycle.started`
- `request.http_received`
- `database.connection_initialized`
- `user.registration_completed`
- `agent.tool.execution_started`

### Why This Pattern?

1. **Hierarchical** - Clear organization (domain → component → action)
2. **Grep-friendly** - Easy to search (`grep "database\."` or `grep "_failed"`)
3. **AI-parseable** - Clear structure for LLMs to understand
4. **OpenTelemetry compliant** - Follows industry standards
5. **State machine tracking** - Natural expression of lifecycle (_started, _completed, _failed)

### Event Taxonomy

The logging standard defines a **complete taxonomy** of events:

```
application.
├── lifecycle.started
├── lifecycle.stopped
├── config.loaded
└── initialization_failed

request.
├── http_received
├── http_processing
├── http_completed
├── http_failed
├── validation_failed
└── timeout_exceeded

database.
├── connection_initialized
├── connection_established
├── query_executed
├── query_failed
├── transaction_committed
└── health_check_failed

agent.
├── lifecycle.started
├── planning.completed
├── tool.execution_started
├── tool.execution_completed
├── tool.execution_failed
├── llm.call_completed
├── llm.token_usage_recorded
├── memory.storage_written
└── self_correction.initiated
```

**For AI Agents**: Predictable event names make it easy to:
- Generate correct logging code
- Parse logs to understand what happened
- Search for specific events

## Standard States

Events follow a **lifecycle pattern** with standard states:

| State | Meaning | Example |
|-------|---------|---------|
| `_started` | Operation initiated | `tool.execution_started` |
| `_progress` | Operation in progress | `tool.execution_progress` |
| `_completed` | Operation successful | `tool.execution_completed` |
| `_failed` | Operation failed | `tool.execution_failed` |
| `_validated` | Validation successful | `input.validation_validated` |
| `_rejected` | Validation failed | `input.validation_rejected` |
| `_retrying` | Retry attempt | `api.call_retrying` |
| `_timeout` | Operation timed out | `request.http_timeout` |

**Pattern**: Every operation logs `_started` → (`_progress`) → `_completed` OR `_failed`

### Example: Complete Operation Lifecycle

```python
# Start operation
logger.info("user.registration_started", email=email)

try:
    # Validate
    logger.info("user.email_validated", email=email)

    # Create user
    user = create_user(email, password)
    logger.info("user.account_created", email=email, user_id=user.id)

    # Send email
    send_verification_email(user)
    logger.info("user.verification_sent", email=email, user_id=user.id)

    # Success
    logger.info("user.registration_completed",
               email=email,
               user_id=user.id,
               duration_ms=duration)

except ValidationError as e:
    logger.error("user.registration_failed",
                email=email,
                error=str(e),
                error_type="ValidationError",
                stage="validation",
                exc_info=True)
    raise

except DatabaseError as e:
    logger.error("user.registration_failed",
                email=email,
                error=str(e),
                error_type="DatabaseError",
                stage="database",
                exc_info=True)
    raise
```

**Timeline in logs**:
```
✅ user.registration_started
✅ user.email_validated
✅ user.account_created
✅ user.verification_sent
✅ user.registration_completed
```

OR if it fails:
```
✅ user.registration_started
✅ user.email_validated
❌ user.registration_failed (stage=database, error="Connection timeout")
```

**For AI Agents**: Clear timeline shows exactly where failure occurred.

## Security Events

Security logging is a **critical extension** of the logging guardrail. While functional logs track what the system does, security logs track **who did what, when, and whether it was allowed**.

### Why Security Logging Matters

Security logs enable:

1. **Audit trails** - Track all authentication and authorization decisions
2. **Intrusion detection** - Identify suspicious patterns and potential attacks
3. **Compliance** - Meet regulatory requirements (GDPR, SOC 2, HIPAA)
4. **Incident response** - Investigate security breaches
5. **Rate limiting enforcement** - Track and limit abusive behavior

**For AI Agents**: Security logs provide explicit records of security decisions, enabling agents to understand and debug authentication/authorization logic.

### Security Event Taxonomy

#### Authentication Events

```
authentication.
├── login_started              # Login attempt initiated
├── login_completed            # Successful login
├── login_failed               # Failed login (wrong password, etc.)
├── logout_completed           # User logged out
├── token_generated            # Auth token created
├── token_validated            # Token checked and valid
├── token_expired              # Token validation failed (expired)
├── token_revoked              # Token manually revoked
├── password_reset_requested   # Password reset initiated
├── password_reset_completed   # Password successfully reset
├── password_changed           # User changed password
└── mfa_required               # Multi-factor auth required
```

**Examples**:
```python
# Successful login
logger.info("authentication.login_started",
           email=email,
           client_ip=request.client.host)

logger.info("authentication.token_generated",
           user_id=user.id,
           token_type="access",
           expires_in=3600)

logger.info("authentication.login_completed",
           user_id=user.id,
           email=email,
           duration_ms=duration)

# Failed login
logger.warning("authentication.login_failed",
              email=email,
              reason="invalid_password",
              attempt_count=3,
              client_ip=request.client.host)

# Token validation
logger.info("authentication.token_validated",
           user_id=user.id,
           token_type="access")

logger.warning("authentication.token_expired",
              user_id=user.id,
              token_type="access",
              expired_at=token.expires_at)
```

#### Authorization Events

```
authorization.
├── access_granted             # Permission check passed
├── access_denied              # Permission check failed
├── role_assigned              # User granted new role
├── role_revoked               # User role removed
├── permission_checked         # Permission verification
└── ownership_verified         # Resource ownership confirmed
```

**Examples**:
```python
# Access granted
logger.info("authorization.access_granted",
           user_id=user.id,
           resource="users",
           resource_id=target_user_id,
           action="read",
           role="admin")

# Access denied
logger.warning("authorization.access_denied",
              user_id=user.id,
              resource="users",
              resource_id=target_user_id,
              action="delete",
              role="user",
              reason="insufficient_permissions")

# Ownership verification
logger.info("authorization.ownership_verified",
           user_id=user.id,
           resource="document",
           resource_id=doc_id)
```

#### Security Threat Events

```
security.
├── rate_limit_exceeded        # Too many requests from IP/user
├── suspicious_activity_detected # Unusual behavior pattern
├── brute_force_detected       # Multiple failed login attempts
├── invalid_token_detected     # Malformed or tampered token
├── sql_injection_attempted    # SQL injection pattern detected
├── xss_attempted              # XSS pattern detected
├── csrf_token_mismatch        # CSRF protection triggered
├── ip_blocked                 # IP address blocked
├── account_locked             # Account locked due to security
└── pii_detected               # Personally identifiable info found
```

**Examples**:
```python
# Rate limiting
logger.warning("security.rate_limit_exceeded",
              user_id=user.id if user else None,
              client_ip=request.client.host,
              endpoint=request.url.path,
              request_count=request_count,
              window_seconds=60)

# Brute force detection
logger.error("security.brute_force_detected",
            email=email,
            client_ip=request.client.host,
            failed_attempts=failed_attempts,
            time_window_minutes=5)

# Injection attempt
logger.error("security.sql_injection_attempted",
            client_ip=request.client.host,
            endpoint=request.url.path,
            suspicious_input=sanitized_input[:100],  # First 100 chars only
            pattern_matched="union_select")

# Account locked
logger.warning("security.account_locked",
              user_id=user.id,
              email=user.email,
              reason="too_many_failed_logins",
              locked_until=locked_until)
```

#### Data Access Events (Audit Trail)

```
audit.
├── data_accessed              # Sensitive data read
├── data_modified              # Sensitive data changed
├── data_deleted               # Data deletion
├── data_exported              # Data export operation
├── settings_changed           # System settings modified
└── admin_action_performed     # Administrative action
```

**Examples**:
```python
# Data access
logger.info("audit.data_accessed",
           user_id=user.id,
           resource="user_profiles",
           resource_id=profile_id,
           fields=["email", "phone", "ssn"])

# Data modification
logger.info("audit.data_modified",
           user_id=user.id,
           resource="user_profiles",
           resource_id=profile_id,
           fields_changed=["email", "phone"],
           old_values=old_values,  # Be careful with sensitive data
           new_values=new_values)

# Admin action
logger.warning("audit.admin_action_performed",
              admin_id=admin.id,
              action="delete_user",
              target_user_id=target_id,
              reason="gdpr_request")
```

### Security Logging Best Practices

#### ✅ DO Log:

1. **All authentication attempts** - Success and failure
2. **All authorization checks** - Granted and denied
3. **Failed security validations** - Invalid tokens, CSRF failures
4. **Rate limiting events** - Who was rate limited and why
5. **Security incidents** - Injection attempts, suspicious patterns
6. **Admin actions** - User deletions, role changes, settings modifications
7. **Data access to sensitive resources** - PII, financial data
8. **Client IP addresses** - For tracking and blocking
9. **User agents** - Detect bot activity

#### ❌ DON'T Log:

1. **Passwords** (plain or hashed) - Never log credentials
2. **Session tokens** (full tokens) - Log token IDs only
3. **Credit card numbers** - Never log full PAN
4. **Social security numbers** - Redact or don't log
5. **API keys** - Never log secrets
6. **Sensitive query parameters** - Sanitize before logging
7. **Full request/response bodies** - May contain sensitive data

### Example: Complete Authentication Flow with Security Logging

```python
from app.core.logging import get_logger
import time

logger = get_logger(__name__)

async def login(email: str, password: str, client_ip: str) -> AuthToken:
    """Authenticate user and return token."""
    start = time.time()

    logger.info("authentication.login_started",
               email=email,
               client_ip=client_ip)

    try:
        # Check rate limiting
        if await is_rate_limited(email, client_ip):
            logger.warning("security.rate_limit_exceeded",
                          email=email,
                          client_ip=client_ip,
                          endpoint="/auth/login")
            raise HTTPException(status_code=429, detail="Too many attempts")

        # Get user
        user = await get_user_by_email(email)
        if not user:
            logger.warning("authentication.login_failed",
                          email=email,
                          reason="user_not_found",
                          client_ip=client_ip)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            logger.warning("authentication.login_failed",
                          email=email,
                          user_id=user.id,
                          reason="account_locked",
                          locked_until=user.locked_until.isoformat(),
                          client_ip=client_ip)
            raise HTTPException(status_code=403, detail="Account locked")

        # Verify password
        if not verify_password(password, user.password_hash):
            # Track failed attempt
            await increment_failed_attempts(user.id)

            logger.warning("authentication.login_failed",
                          email=email,
                          user_id=user.id,
                          reason="invalid_password",
                          failed_attempts=user.failed_attempts + 1,
                          client_ip=client_ip)

            # Check for brute force
            if user.failed_attempts >= 4:
                logger.error("security.brute_force_detected",
                            email=email,
                            user_id=user.id,
                            failed_attempts=user.failed_attempts + 1,
                            client_ip=client_ip)

                # Lock account
                await lock_account(user.id, duration_minutes=30)
                logger.warning("security.account_locked",
                              user_id=user.id,
                              email=email,
                              reason="too_many_failed_logins",
                              duration_minutes=30)

            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Reset failed attempts on successful login
        await reset_failed_attempts(user.id)

        # Generate token
        token = generate_token(user)
        logger.info("authentication.token_generated",
                   user_id=user.id,
                   token_id=token.id,  # Log token ID, not the token itself
                   token_type="access",
                   expires_in=3600)

        # Success
        duration_ms = (time.time() - start) * 1000
        logger.info("authentication.login_completed",
                   user_id=user.id,
                   email=email,
                   client_ip=client_ip,
                   duration_ms=round(duration_ms, 2))

        return token

    except HTTPException:
        raise
    except Exception as e:
        logger.error("authentication.login_failed",
                    email=email,
                    error=str(e),
                    error_type=type(e).__name__,
                    client_ip=client_ip,
                    exc_info=True)
        raise
```

**Logs produced by successful login**:
```json
{"timestamp": "2024-01-15T10:00:00.000Z", "level": "info", "event": "authentication.login_started", "email": "user@example.com", "client_ip": "192.168.1.1"}
{"timestamp": "2024-01-15T10:00:00.123Z", "level": "info", "event": "authentication.token_generated", "user_id": 123, "token_id": "tok_abc123", "token_type": "access", "expires_in": 3600}
{"timestamp": "2024-01-15T10:00:00.145Z", "level": "info", "event": "authentication.login_completed", "user_id": 123, "email": "user@example.com", "client_ip": "192.168.1.1", "duration_ms": 145.23}
```

**Logs produced by failed login (brute force)**:
```json
{"timestamp": "2024-01-15T10:00:00.000Z", "level": "info", "event": "authentication.login_started", "email": "attacker@evil.com", "client_ip": "10.0.0.1"}
{"timestamp": "2024-01-15T10:00:00.050Z", "level": "warning", "event": "authentication.login_failed", "email": "attacker@evil.com", "user_id": 456, "reason": "invalid_password", "failed_attempts": 5, "client_ip": "10.0.0.1"}
{"timestamp": "2024-01-15T10:00:00.051Z", "level": "error", "event": "security.brute_force_detected", "email": "attacker@evil.com", "user_id": 456, "failed_attempts": 5, "client_ip": "10.0.0.1"}
{"timestamp": "2024-01-15T10:00:00.052Z", "level": "warning", "event": "security.account_locked", "user_id": 456, "email": "attacker@evil.com", "reason": "too_many_failed_logins", "duration_minutes": 30}
```

### Querying Security Logs

```bash
# Find all failed login attempts
grep '"event":"authentication.login_failed"' logs.json

# Find brute force attacks
grep '"event":"security.brute_force_detected"' logs.json | jq

# Find all actions by specific user
grep '"user_id":123' logs.json | jq -r '.event'

# Find all access denials
grep '"event":"authorization.access_denied"' logs.json | jq

# Find rate limiting events
grep '"event":"security.rate_limit_exceeded"' logs.json

# Count failed logins by email
grep '"event":"authentication.login_failed"' logs.json | jq -r '.email' | sort | uniq -c | sort -rn

# Find all admin actions
grep '"event":"audit.admin_action_performed"' logs.json | jq
```

### Security Event Retention

**Recommended retention periods**:

- **Authentication logs**: 90 days minimum (compliance requirement)
- **Authorization logs**: 90 days minimum
- **Security incidents**: 1 year minimum
- **Audit trail (data access)**: 7 years (depending on regulations)
- **Rate limiting**: 30 days

### Compliance Considerations

Security logging supports compliance with:

- **GDPR**: Audit trail of data access and modifications
- **SOC 2**: Authentication, authorization, and admin actions
- **HIPAA**: PHI access logging and audit trails
- **PCI DSS**: Failed login attempts, access control changes

**For AI Agents**: Security event logs provide a complete audit trail of all security decisions, enabling agents to understand authentication/authorization flows and debug security issues autonomously.

## Required Log Attributes

Every log should include **context fields** for debugging:

### All Logs (Automatic)

- `timestamp` - ISO 8601 timestamp
- `level` - Log level (info, warning, error)
- `event` - Event name (domain.component.action_state)
- `request_id` - Correlation ID (automatic via middleware)

### Request Logs

- `method` - HTTP method (GET, POST, etc.)
- `path` - Request path (/api/users)
- `status_code` - Response status (200, 404, etc.)
- `duration_ms` - Request duration in milliseconds
- `client_host` - Client IP address

### Error Logs

- `error` - Error message
- `error_type` - Error class name (ValueError, DatabaseError)
- `exc_info` - Set to `True` for full stack trace
- `retryable` - Boolean, is error retryable?
- `retry_count` - Number of retry attempts

### Agent Logs (Future)

- `agent_id` - Agent instance ID
- `run_id` - Execution run ID
- `tool` - Tool name
- `model` - LLM model name
- `tokens_prompt` - Prompt token count
- `tokens_completion` - Completion token count
- `cost_usd` - Estimated cost

## Backend Logging: structlog

### What is structlog?

**structlog** is a Python library for structured logging that outputs JSON.

**Key Features**:
- **JSON output** - Machine-readable logs
- **Context binding** - Attach context to all logs in a request
- **Processors** - Transform log data before output
- **Performance** - Fast, minimal overhead

### Our structlog Configuration

Location: `backend/app/core/logging.py`

**Key Setup**:
- JSON output for production
- Request ID correlation (via `contextvars`)
- Timestamp in ISO 8601 format
- Stack traces for errors

### Request ID Correlation

Every HTTP request gets a unique `request_id` that's automatically added to all logs:

```python
# Middleware adds request_id to context
request_id = str(uuid.uuid4())
context_vars.request_id.set(request_id)

# Now ALL logs in this request include request_id automatically
logger.info("request.http_received", method="POST", path="/api/users")
logger.info("user.registration_started", email=email)
logger.info("database.query_executed", table="users")
logger.info("request.http_completed", status_code=201)

# All logs have the same request_id
```

**Why This Matters**:
- Trace a single request through the entire system
- See all operations for one user action
- Debug multi-step workflows

**For AI Agents**: Can read logs and follow a complete request lifecycle.

### Example: structlog in Action

```python
# backend/app/features/users/service.py

from app.core.logging import get_logger

logger = get_logger(__name__)

async def register_user(email: str, password: str) -> User:
    """Register a new user."""
    logger.info("user.registration_started", email=email)

    try:
        # Validate email
        if not is_valid_email(email):
            logger.error("user.registration_failed",
                        email=email,
                        error="Invalid email format",
                        error_type="ValidationError")
            raise ValueError("Invalid email format")

        logger.info("user.email_validated", email=email)

        # Create user
        user = await create_user_in_db(email, password)
        logger.info("user.account_created",
                   email=email,
                   user_id=user.id)

        # Send verification
        await send_verification_email(user)
        logger.info("user.verification_sent",
                   email=email,
                   user_id=user.id)

        logger.info("user.registration_completed",
                   email=email,
                   user_id=user.id)

        return user

    except Exception as e:
        logger.error("user.registration_failed",
                    email=email,
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True)
        raise
```

**Logs Output** (JSON):

```json
{"timestamp": "2024-01-15T14:32:15.123Z", "level": "info", "event": "user.registration_started", "email": "test@example.com", "request_id": "req-abc123"}
{"timestamp": "2024-01-15T14:32:15.234Z", "level": "info", "event": "user.email_validated", "email": "test@example.com", "request_id": "req-abc123"}
{"timestamp": "2024-01-15T14:32:15.456Z", "level": "info", "event": "user.account_created", "email": "test@example.com", "user_id": 12345, "request_id": "req-abc123"}
{"timestamp": "2024-01-15T14:32:15.678Z", "level": "info", "event": "user.verification_sent", "email": "test@example.com", "user_id": 12345, "request_id": "req-abc123"}
{"timestamp": "2024-01-15T14:32:15.890Z", "level": "info", "event": "user.registration_completed", "email": "test@example.com", "user_id": 12345, "request_id": "req-abc123"}
```

**For AI Agents**: Can parse JSON, extract events, understand flow.

## Searching and Analyzing Logs

### Searching with grep

```bash
# All agent events
grep '"event":"agent\.' logs.json

# All tool operations
grep '"event":"agent\.tool\.' logs.json

# Failed events across system
grep '_failed"' logs.json

# Specific request trace
grep '"request_id":"req-abc123"' logs.json

# All database errors
grep '"event":"database\.' logs.json | grep '"level":"error"'
```

### Analyzing with jq

```bash
# Extract all event types
cat logs.json | jq -r '.event'

# Count events by type
cat logs.json | jq -r '.event' | sort | uniq -c | sort -rn

# Find slow requests (>1000ms)
cat logs.json | jq 'select(.duration_ms > 1000)'

# Average duration by endpoint
cat logs.json | jq -s 'group_by(.path) | map({
  path: .[0].path,
  avg_duration: (map(.duration_ms) | add / length)
})'

# Error rate by domain
cat logs.json | jq -r 'select(.level == "error") | .event' | cut -d'.' -f1 | sort | uniq -c
```

**For AI Agents**: Can programmatically query logs to diagnose issues.

## Logging Best Practices for AI Agents

### ✅ DO:

1. **Log at operation boundaries** - Start, complete, fail
2. **Use standard event names** - Follow the taxonomy
3. **Include context** - All relevant IDs, values, durations
4. **Log errors with stack traces** - `exc_info=True`
5. **Use consistent states** - `_started`, `_completed`, `_failed`
6. **Include performance metrics** - `duration_ms`, `tokens`, `cost`
7. **Correlate related events** - Use `request_id`, `run_id`

### ❌ DON'T:

1. **Log sensitive data** - Passwords, API keys, credit cards
2. **Use inconsistent event names** - Follow the taxonomy
3. **Log without context** - Always include relevant IDs
4. **Skip error logging** - Always log failures
5. **Use print() statements** - Use structured logging
6. **Log at too high volume** - Don't log inside tight loops

## Example: Complete Feature with Logging

```python
# backend/app/features/orders/service.py

from app.core.logging import get_logger
import time

logger = get_logger(__name__)

async def process_order(order_id: int, user_id: int) -> Order:
    """Process an order from start to finish."""
    start = time.time()

    logger.info("order.process_started",
               order_id=order_id,
               user_id=user_id)

    try:
        # Step 1: Load order
        order = await load_order(order_id)
        logger.info("order.loaded",
                   order_id=order_id,
                   total=order.total)

        # Step 2: Process payment
        logger.info("order.payment_started",
                   order_id=order_id,
                   amount=order.total)

        payment = await charge_payment(order)

        logger.info("order.payment_completed",
                   order_id=order_id,
                   amount=order.total,
                   payment_id=payment.id)

        # Step 3: Update inventory
        logger.info("order.inventory_update_started",
                   order_id=order_id,
                   item_count=len(order.items))

        await update_inventory(order)

        logger.info("order.inventory_updated",
                   order_id=order_id)

        # Step 4: Send confirmation
        await send_confirmation_email(order, user_id)
        logger.info("order.confirmation_sent",
                   order_id=order_id,
                   user_id=user_id)

        # Success
        duration_ms = (time.time() - start) * 1000
        logger.info("order.process_completed",
                   order_id=order_id,
                   user_id=user_id,
                   total=order.total,
                   duration_ms=round(duration_ms, 2))

        return order

    except PaymentError as e:
        logger.error("order.process_failed",
                    order_id=order_id,
                    user_id=user_id,
                    error=str(e),
                    error_type="PaymentError",
                    stage="payment",
                    retryable=False,
                    exc_info=True)
        raise

    except InventoryError as e:
        logger.error("order.process_failed",
                    order_id=order_id,
                    user_id=user_id,
                    error=str(e),
                    error_type="InventoryError",
                    stage="inventory",
                    retryable=True,
                    exc_info=True)
        raise

    except Exception as e:
        logger.error("order.process_failed",
                    order_id=order_id,
                    user_id=user_id,
                    error=str(e),
                    error_type=type(e).__name__,
                    stage="unknown",
                    retryable=False,
                    exc_info=True)
        raise
```

**Success Logs**:
```
✅ order.process_started (order_id=123, user_id=456)
✅ order.loaded (order_id=123, total=99.99)
✅ order.payment_started (order_id=123, amount=99.99)
✅ order.payment_completed (order_id=123, payment_id=789)
✅ order.inventory_update_started (order_id=123, item_count=3)
✅ order.inventory_updated (order_id=123)
✅ order.confirmation_sent (order_id=123, user_id=456)
✅ order.process_completed (order_id=123, duration_ms=1234.56)
```

**Failure Logs** (payment failed):
```
✅ order.process_started (order_id=123, user_id=456)
✅ order.loaded (order_id=123, total=99.99)
✅ order.payment_started (order_id=123, amount=99.99)
❌ order.process_failed (error="Card declined", error_type="PaymentError", stage="payment", retryable=false)
```

**For AI Agents**: Complete visibility into what succeeded and what failed.

## Summary: Logging as Observability for Autonomous Systems

Logging is the **most critical observability guardrail** for AI agents because it:

1. **Enables autonomous debugging** - Agents read logs to diagnose failures
2. **Provides execution history** - Complete record of what happened
3. **Supports correlation** - Trace requests across the system
4. **Enables performance analysis** - Identify slow operations
5. **Facilitates monitoring** - Detect issues in real-time
6. **Creates audit trails** - Track all system changes

### The Logging Contract for AI Agents:

```
┌─────────────────────────────────────────────────────────┐
│      AI AGENT PROMISE (Enforced by Logging)             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  "I will log all significant operations:               │
│                                                         │
│   ✅ Operation start (_started)                        │
│   ✅ Operation completion (_completed)                 │
│   ✅ Operation failure (_failed)                       │
│   ✅ All errors with stack traces (exc_info=True)      │
│   ✅ All context (IDs, durations, errors)              │
│   ✅ Following the event taxonomy                      │
│   ✅ Using structured JSON format                      │
│                                                         │
│  When debugging failures, I will:                      │
│                                                         │
│   1. Read logs for the failing test/operation          │
│   2. Identify which step failed                        │
│   3. Read error message and stack trace                │
│   4. Identify root cause from logs                     │
│   5. Fix the issue                                     │
│   6. Verify logs show success after fix                │
│                                                         │
│  I will NEVER ignore logging or use print() instead."  │
└─────────────────────────────────────────────────────────┘
```

This contract ensures **complete observability** of all AI-generated code and autonomous debugging capabilities.

## Next Steps

1. Read [architecture.md](./architecture.md) to understand code organization patterns
2. Explore `backend/docs/logging-standard.md` for the complete event taxonomy
3. Explore `backend/app/core/logging.py` for the structlog configuration
4. Look at examples in `backend/app/core/middleware.py` for request logging
5. Practice reading JSON logs with `jq` and `grep`

Remember: **Logs are how AI agents understand the past**. Without structured, comprehensive logging, agents cannot debug failures or understand system behavior. Logging enables autonomous, self-correcting development.
