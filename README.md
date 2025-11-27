# Full-Stack Foundations for Agentic AI Applications

A **production-ready foundation** for building autonomous AI applications with FastAPI + PostgreSQL backend and React + TypeScript frontend. Designed with **5 core guardrails** that enable AI agents to plan, implement, validate, and self-correct code autonomously.

## 🎯 What Makes This Different?

This isn't just a starter template - it's a **foundation for agentic AI development** with:

**5 Core Guardrails:**
1. ✅ **Tests** (pytest, vitest, playwright) - Prove code correctness + security
2. ✅ **Linting & Style** (Ruff, ESLint, Prettier) - Enforce consistency + catch vulnerabilities
3. ✅ **Type Checks** (MyPy, Pyright, TypeScript strict) - Prevent bugs + type-safe security
4. ✅ **Logging** (structlog) - Enable debugging + security event tracking
5. ✅ **Architecture** (Vertical Slices) - Predictable structure + security isolation

**Security Integrated Throughout:**
- SQL injection prevention (tests + linting + type safety)
- XSS prevention (sanitization + validation)
- Authentication/authorization patterns
- Rate limiting and brute force prevention
- Secure password hashing (bcrypt)
- PII detection and redaction
- Security event logging

**Complete Example Feature:**
- `backend/app/examples/complete_feature/` demonstrates ALL patterns
- Vertical slice architecture
- Complete logging lifecycle
- Security tests and validation
- Type-safe throughout

## 📂 Repository Structure

```
full-stack-foundations/
├── backend/              # FastAPI + PostgreSQL
│   ├── app/
│   │   ├── core/         # Infrastructure (config, database, logging, health)
│   │   ├── shared/       # Utilities (security, pagination, timestamps)
│   │   │   └── security.py    # Security utilities (passwords, sanitization, rate limiting)
│   │   ├── examples/     # Example features
│   │   │   └── complete_feature/  # Complete notes feature demonstrating all patterns
│   │   ├── tests/        # Integration tests
│   │   └── main.py       # FastAPI app entry point
│   ├── docs/             # Technical standards (pytest, ruff, mypy, logging)
│   ├── alembic/          # Database migrations
│   └── pyproject.toml    # Python dependencies and tool configs
├── frontend/             # React + Vite + TypeScript
│   ├── src/
│   │   ├── app/          # App setup and routing
│   │   ├── features/     # Feature slices (vertical architecture)
│   │   └── shared/       # Shared components and utilities
│   ├── e2e/              # Playwright E2E tests
│   └── package.json      # Node dependencies
├── explanations/         # 📚 COMPREHENSIVE GUARDRAIL DOCUMENTATION
│   ├── README.md         # Reading guide (start here!)
│   ├── overview.md       # PIV loop and philosophy
│   ├── tests.md          # Testing patterns + security testing
│   ├── linting-and-style.md   # Linting + security rules
│   ├── type-checks.md    # Type checking + type safety for security
│   ├── logging.md        # Structured logging + security events
│   └── architecture.md   # Vertical slices + security through isolation
├── CLAUDE.md             # Guidelines for AI agents (Claude Code, etc.)
└── README.md             # This file
```

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
cp .env.example .env              # Customize DATABASE_URL, etc.
uv sync                           # Install dependencies
docker-compose up -d              # Start PostgreSQL
uv run alembic upgrade head       # Apply database migrations
uv run uvicorn app.main:app --reload --port 8123  # Start API server
```

### Frontend Setup

```bash
cd frontend
cp .env.example .env              # Customize API URL if needed
npm install                       # Install dependencies
npm run dev -- --host --port 5173  # Start dev server
```

### Verify Installation

```bash
# Backend health check
curl http://localhost:8123/health
# Should return: {"status":"healthy","service":"api"}

# Frontend
open http://localhost:5173
```

## 📖 Documentation

### For First-Time Users

**Start here:** Read `explanations/README.md` for a complete guide to all guardrails.

**Recommended reading order:**
1. `explanations/overview.md` - Understand the PIV (Plan-Implement-Validate) loop
2. `explanations/tests.md` - Testing + security testing
3. `explanations/linting-and-style.md` - Linting + security rules
4. `explanations/type-checks.md` - Type checking + type-safe security
5. `explanations/logging.md` - Structured logging + security events
6. `explanations/architecture.md` - Vertical slices + security isolation

**Total reading time:** ~2-3 hours for all documents

### For AI Coding Assistants

**Read CLAUDE.md first** - Complete guidelines for AI agents working in this repository.

Key references:
- `backend/app/examples/complete_feature/` - Study this before creating features
- `explanations/architecture.md` - Vertical slice patterns
- `explanations/logging.md` - Event naming patterns
- `backend/app/shared/security.py` - Security utilities

### Quick Reference

**Backend commands** (from `backend/` directory):
```bash
# Type checking
uv run mypy app/
uv run pyright app/

# Linting & formatting
uv run ruff check .
uv run ruff format .

# Testing
uv run pytest -v                    # All tests
uv run pytest -v -m security        # Security tests only
uv run pytest -v -m integration     # Integration tests only

# Database migrations
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

**Frontend commands** (from `frontend/` directory):
```bash
npm run typecheck     # TypeScript type checking
npm run lint          # ESLint
npm run format        # Prettier
npm run test          # Vitest unit tests
npm run test:e2e      # Playwright E2E tests
```

## 🛡️ Security Features

Security is integrated throughout all 5 guardrails:

### 1. Security Testing
- SQL injection prevention tests
- XSS prevention tests
- Authentication/authorization tests
- Rate limiting tests
- Sensitive data exposure tests
- Mark security tests with `@pytest.mark.security`

### 2. Security Linting (Ruff S-rules)
- S105: Hardcoded password detection
- S608: SQL injection via string concatenation
- S324: Insecure hash functions (MD5, SHA1)
- S501: SSL verification disabled
- S602/S605: Shell injection risks

### 3. Type Safety for Security
```python
from app.shared.security import PlainPassword, HashedPassword, SanitizedHTML

def hash_password(plain: PlainPassword) -> HashedPassword:
    """Type system enforces secure password handling."""
    return hash_password(plain)
```

### 4. Security Event Logging
- `authentication.*` - Login, token, logout events
- `authorization.*` - Access granted/denied
- `security.*` - Rate limits, brute force attempts, injection attempts
- `audit.*` - Data access, modifications, admin actions

### 5. Security Through Isolation
- Vertical slices limit blast radius
- Feature-level permissions
- Sensitive features (auth/, payments/) have controlled exports

## 🏗️ Creating New Features

**IMPORTANT**: Study `backend/app/examples/complete_feature/` first!

This complete example demonstrates:
- ✅ Vertical slice structure (`models.py`, `schemas.py`, `routes.py`, `service.py`, `tests/`)
- ✅ Complete logging lifecycle (started, completed, failed)
- ✅ Type safety (full annotations, strict mode)
- ✅ Security (auth, authorization, input validation)
- ✅ Comprehensive tests (unit + security)

**Steps to create a new feature:**

1. Study the example: `backend/app/examples/complete_feature/README.md`
2. Create feature folder: `mkdir backend/app/my_feature`
3. Create structure: `models.py`, `schemas.py`, `routes.py`, `service.py`, `tests/`
4. Follow the patterns from the example
5. Register router in `backend/app/main.py`
6. Run guardrails: type check, lint, test
7. Iterate until all pass

## 🤖 For AI Agents

This repository is **optimized for autonomous AI development** using the PIV loop:

```
┌─────────────────────────────────────────┐
│  PLAN: Break down requirements          │
└─────────────┬───────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│  IMPLEMENT: Write code following patterns│
└─────────────┬───────────────────────────┘
              ▼
┌─────────────────────────────────────────┐
│  VALIDATE: Run all 5 guardrails         │
│  - Tests, Linting, Type checks, etc.    │
└─────────┬──────────┬────────────────────┘
          │          │
   ✅ PASS │          │ ❌ FAIL
          │          ▼
          │    ┌─────────────────────────┐
          │    │  Self-correct and retry │
          │    └─────────┬───────────────┘
          │              │
          │              ▼ (back to IMPLEMENT)
          ▼
      NEXT TASK
```

**Read CLAUDE.md for complete AI agent guidelines.**

## 📚 Additional Resources

- **Backend standards:** `backend/docs/` (pytest, ruff, mypy, pyright, logging)
- **Backend README:** `backend/README.md`
- **Frontend README:** `frontend/README.md`
- **Explanations:** `explanations/` (comprehensive guardrail documentation)

## 🎓 Philosophy

> **"Guardrails are not restrictions - they are enablers."**

Guardrails accelerate development by:
- ✅ Catching errors early (compile time > test time > runtime)
- ✅ Enabling autonomous validation (AI agents self-correct)
- ✅ Building confidence (know your code is correct and secure)
- ✅ Reducing rework (fix issues immediately, not later)
- ✅ Scaling development (more agents, same quality)

**Foundations first = trust & velocity.**

When guardrails are solid, AI agents move fast and autonomously. When guardrails are missing, every change requires human review.

We choose **automation over manual review**.

---

**Ready to build?** Start with `explanations/README.md` and see how autonomous AI development works.
