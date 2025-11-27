# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI + PostgreSQL application using **vertical slice architecture**, optimized for AI-assisted development. Python 3.12+, strict type checking with MyPy and Pyright. Backend code now lives in `backend/` with FastAPI; frontend lives in `frontend/` (React + Vite). Run backend commands from inside `backend/`.

**This repository is a foundation for agentic AI applications** with 5 core guardrails:
1. **Tests** (pytest, vitest, playwright) - Including security tests
2. **Linting & Style** (Ruff, ESLint, Prettier) - Including security rules
3. **Type Checks** (MyPy, Pyright, TypeScript strict) - Type-safe security
4. **Logging** (structlog) - Including security events
5. **Architecture** (Vertical Slices) - Security through isolation

See `explanations/` folder for comprehensive documentation on each guardrail.

## Core Principles

**KISS** (Keep It Simple, Stupid)

- Prefer simple, readable solutions over clever abstractions

**YAGNI** (You Aren't Gonna Need It)

- Don't build features until they're actually needed

**Vertical Slice Architecture**

- Each feature owns its database models, schemas, routes, and business logic
- Features live in separate directories under `backend/app/` (e.g., `backend/app/products/`, `backend/app/orders/`)
- Shared utilities go in `backend/app/shared/` only when used by 3+ features
- Core infrastructure (`backend/app/core/`) is shared across all features

**Type Safety (CRITICAL)**

- Strict type checking enforced (MyPy + Pyright in strict mode)
- All functions, methods, and variables MUST have type annotations
- Zero type suppressions allowed
- All functions must have complete type hints
- Strict mypy & pyright configuration is enforced
- No `Any` types without explicit justification
- Test files have relaxed typing rules (see pyproject.toml)

**AI-Optimized Patterns**

- Structured logging: Use `domain.component.action_state` pattern (hybrid dotted namespace)
  - Format: `{domain}.{component}.{action}_{state}`
  - Examples: `user.registration_started`, `product.create_completed`, `agent.tool.execution_failed`
  - See `backend/docs/logging-standard.md` for complete event taxonomy
- Request correlation: All logs include `request_id` automatically via context vars
- Consistent verbose naming: Predictable patterns for AI code generation

## Essential Commands

Run backend commands from inside `backend/`.

### Development

```bash
# Start development server (port 8123)
uv run uvicorn app.main:app --reload --port 8123
```

### Testing

```bash
# Run all tests (34 tests, <1s execution)
uv run pytest -v

# Run integration tests only
uv run pytest -v -m integration

# Run specific test
uv run pytest -v app/core/tests/test_database.py::test_function_name
```

### Type Checking must be green

```bash
# MyPy (strict mode)
uv run mypy app/

# Pyright (strict mode)
uv run pyright app/
```

### Linting & Formatting must be green

```bash
# Check linting
uv run ruff check .

# Auto-format code
uv run ruff format .
```

### Database Migrations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Start PostgreSQL (Docker)
docker-compose up -d
```

### Docker

```bash
# Build and start all services
docker-compose up -d --build

# View app logs
docker-compose logs -f app

# Stop all services
docker-compose down
```

## Architecture

### Directory Structure

```
backend/
├── app/
│   ├── core/           # Infrastructure (config, database, logging, middleware, health, exceptions)
│   ├── shared/         # Cross-feature utilities (pagination, timestamps, error schemas, SECURITY)
│   │   └── security.py # Security utilities (passwords, sanitization, rate limiting, PII)
│   ├── examples/       # Example features demonstrating all patterns
│   │   └── complete_feature/  # Complete example: notes feature with all guardrails
│   ├── tests/          # Backend unit/integration tests
│   └── main.py         # FastAPI application entry point
├── alembic/            # Migrations
├── docs/               # Standards for logging, typing, linting, testing
├── Dockerfile          # Backend image
└── docker-compose.yml  # Backend + Postgres services

explanations/           # Comprehensive guardrail documentation
├── README.md           # Reading guide
├── overview.md         # PIV loop and philosophy
├── tests.md            # Testing + security testing
├── linting-and-style.md  # Linting + security rules
├── type-checks.md      # Type checking + type safety for security
├── logging.md          # Structured logging + security events
└── architecture.md     # Vertical slices + security through isolation

frontend/
└── ...                 # React + Vite app and guardrails
```

### Database

**SQLAlchemy Setup**

- Async engine with connection pooling (pool_size=5, max_overflow=10)
- Base class: `app.core.database.Base` (extends `DeclarativeBase`)
- Session dependency: `get_db()` from `app.core.database`
- All models should inherit `TimestampMixin` from `app.shared.models` for automatic `created_at`/`updated_at`

**Migration Workflow**

1. Define/modify models inheriting from `Base` and `TimestampMixin`
2. Run `uv run alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Apply: `uv run alembic upgrade head`

### Logging

**Philosophy:** Logs are optimized for AI agent consumption. Include enough context for an LLM to understand and fix issues without human intervention.

**Structured Logging (structlog)**

- JSON output for AI-parseable logs
- Request ID correlation using `contextvars`
- Logger: `from app.core.logging import get_logger; logger = get_logger(__name__)`
- Event naming: Hybrid dotted namespace pattern `domain.component.action_state`
  - Examples: `user.registration_completed`, `database.connection_initialized`, `request.http_received`
  - Detailed taxonomy: See `backend/docs/logging-standard.md`
- Exception logging: Always include `exc_info=True` for stack traces

**Event Pattern Guidelines:**

- **Format:** `{domain}.{component}.{action}_{state}`
- **Domains:** application, request, database, health, agent, external, feature-name
- **States:** `_started`, `_completed`, `_failed`, `_validated`, `_rejected`, `_retrying`
- **Why:** OpenTelemetry compliant, AI/LLM parseable, grep-friendly, scalable for agents

**Middleware**

- `RequestLoggingMiddleware`: Logs all requests with correlation IDs
- `CORSMiddleware`: Configured for local development (see `app.core.config`)
- Adds `X-Request-ID` header to all responses

### Documentation Style

**Use Google-style docstrings** for all functions, classes, and modules:

```python
def process_request(user_id: str, query: str) -> dict[str, Any]:
    """Process a user request and return results.

    Args:
        user_id: Unique identifier for the user.
        query: The search query string.

    Returns:
        Dictionary containing results and metadata.

    Raises:
        ValueError: If query is empty or invalid.
        ProcessingError: If processing fails after retries.
    """
```

### Tool Docstrings for Agents

**Critical Difference:** Tool docstrings are read by LLMs during tool selection. They must guide the agent to choose the RIGHT tool, use it EFFICIENTLY, and compose tools into workflows.

Standard Google-style docstrings document **what code does** for human developers.
Agent tool docstrings guide **when to use the tool and how** for LLM reasoning.

**Key Principles:**

1. **Guide Tool Selection** - Agent must choose this tool over alternatives
2. **Prevent Token Waste** - Steer toward efficient parameter choices
3. **Enable Composition** - Show how tool fits into multi-step workflows
4. **Set Expectations** - Explain performance characteristics and limitations
5. **Provide Examples** - Concrete usage with realistic data

### Shared Utilities

**Pagination** (`app.shared.schemas`)

- `PaginationParams`: Query params with `.offset` property
- `PaginatedResponse[T]`: Generic response with `.total_pages` property

**Timestamps** (`app.shared.models`)

- `TimestampMixin`: Adds `created_at` and `updated_at` columns
- `utcnow()`: Timezone-aware UTC datetime helper

**Error Handling** (`app.shared.schemas`, `app.core.exceptions`)

- `ErrorResponse`: Standard error response format
- Global exception handlers configured in `app.main`

**Security** (`app.shared.security`)

- `hash_password()`, `verify_password()` - Bcrypt password hashing
- `sanitize_html()` - XSS prevention (removes dangerous HTML)
- `sanitize_sql_identifier()` - SQL injection prevention
- `RateLimiter` - Brute force prevention
- `contains_pii()`, `redact_pii()` - PII detection and redaction
- `generate_secure_token()` - Cryptographically secure tokens
- Type-safe security primitives: `PlainPassword`, `HashedPassword`, `SanitizedHTML`, etc.

### Configuration

- Environment variables via Pydantic Settings (`app.core.config`)
- Required: `DATABASE_URL` (postgresql+asyncpg://...)
- Copy `.env.example` to `.env` for local development
- Settings singleton: `get_settings()` from `app.core.config`

## Security Patterns

Security is integrated throughout all 5 guardrails:

**1. Security Testing** (`@pytest.mark.security`)
- SQL injection prevention tests
- XSS prevention tests
- Authentication/authorization tests
- Rate limiting tests
- Sensitive data exposure tests

**2. Security Linting** (Ruff S-prefix rules)
- S105: Hardcoded password detection
- S608: SQL injection via string formatting
- S324: Insecure hash functions (MD5, SHA1)
- S501: SSL verification disabled
- S602/S605: Shell injection

**3. Type Safety for Security** (NewType wrappers)
```python
from app.shared.security import PlainPassword, HashedPassword, SanitizedHTML

def hash_password(plain: PlainPassword) -> HashedPassword:
    # Type system enforces that passwords are handled securely
    pass
```

**4. Security Event Logging**
- `authentication.*` - Login, token, logout events
- `authorization.*` - Access granted/denied
- `security.*` - Rate limits, brute force, injection attempts
- `audit.*` - Data access, modifications, exports

**5. Security Through Isolation** (Vertical Slices)
- Each feature folder is isolated (limited blast radius)
- Sensitive features (auth/, payments/) have controlled exports
- Feature-level permission boundaries
- Authorization checks in service layer

See `explanations/` for comprehensive security documentation.

## Development Guidelines

**When Creating New Features**

**IMPORTANT**: Study `backend/app/examples/complete_feature/` first! This is a complete example feature (notes) demonstrating all patterns:
- Vertical slice structure
- Complete logging lifecycle (started, completed, failed)
- Type safety with full annotations
- Security (auth, authorization, input validation)
- Comprehensive tests (unit + security)

To create a new feature:

1. Study the example: `backend/app/examples/complete_feature/` and read its `README.md`
2. Create feature directory under `backend/app/` (e.g., `backend/app/products/`)
3. Structure: `models.py`, `schemas.py`, `routes.py`, `service.py`, `tests/`
4. Models inherit from `Base` and `TimestampMixin`
5. Use `get_db()` dependency for database sessions
6. Follow complete logging lifecycle:
   - START: `logger.info("feature.action_started", **context)`
   - SUCCESS: `logger.info("feature.action_completed", **context, duration_ms=X)`
   - FAILURE: `logger.error("feature.action_failed", exc_info=True, error=str(e), **context)`
7. Add security tests with `@pytest.mark.security`
8. Add router to `app/main.py`: `app.include_router(feature_router)`

**Type Checking**

- Run both MyPy and Pyright before committing
- No type suppressions (`# type: ignore`, `# pyright: ignore`) unless absolutely necessary
- Document suppressions with inline comments explaining why

**Testing**

- Write tests alongside feature code in `tests/` subdirectory
- Use `@pytest.mark.integration` for tests requiring real database
- Fast unit tests preferred (<1s total execution time)
- Test fixtures in `app/tests/conftest.py` (under `backend/`)

**Logging Best Practices**

- Start action: `logger.info("feature.action_started", **context)`
- Success: `logger.info("feature.action_completed", **context)`
- Failure: `logger.error("feature.action_failed", exc_info=True, error=str(e), error_type=type(e).__name__, **context)`
- Include context: IDs, durations, error details
- Avoid generic events like "processing" or "handling"
- Use standard states: `_started`, `_completed`, `_failed`, `_validated`, `_rejected`

**Database Patterns**

- Always use async/await with SQLAlchemy
- Use `select()` instead of `.query()` (SQLAlchemy 2.0 style)
- Leverage `expire_on_commit=False` in session config
- Test database operations with `@pytest.mark.integration`

**API Patterns**

- Health checks: `/health`, `/health/db`, `/health/ready`
- Pagination: Use `PaginationParams` and `PaginatedResponse[T]`
- Error responses: Use `ErrorResponse` schema
- Route prefixes: Use router `prefix` parameter for feature namespacing
