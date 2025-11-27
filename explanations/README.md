# Guardrails for Agentic AI Applications

## What is This?

This folder contains **comprehensive explanations** of the five core guardrails that enable autonomous AI development in this repository. These documents explain not just **what** each guardrail does, but **why** it's critical for AI agents to build software autonomously.

## The Vision

This repository is designed to be a **foundation for agentic AI applications** - applications where AI agents can:

1. **Plan** features and tasks autonomously
2. **Implement** code following established patterns
3. **Validate** their work against automated guardrails
4. **Self-correct** when validation fails
5. **Iterate** until all guardrails pass

The guardrails make this possible by providing **explicit, executable rules** that AI agents can validate against.

## The Five Guardrails

```
┌─────────────────────────────────────────────────────────┐
│                    GUARDRAILS (SAFETY NETS)             │
├─────────────┬─────────────┬─────────────┬─────────┬────┤
│   TESTS     │  LINTING &  │    TYPE     │ LOGGING │ARCH│
│ (Unit, E2E) │    STYLE    │   CHECKS    │(Struct.)│    │
│             │(Ruff, ESLint)│(MyPy, TS)   │         │    │
└─────────────┴─────────────┴─────────────┴─────────┴────┘
```

Each guardrail serves a specific purpose in the **Plan-Implement-Validate (PIV) loop**:

1. **Tests** - Prove the code works correctly
2. **Linting & Style** - Ensure consistent code formatting
3. **Type Checks** - Catch type errors before runtime
4. **Logging** - Enable debugging and observability
5. **Architecture** - Provide clear, predictable code organization

## Reading Guide

### For First-Time Readers

**Start here** to understand the foundation:

1. **[overview.md](./overview.md)** - The big picture
   - What is the PIV loop?
   - Why do AI agents need guardrails?
   - How do all five guardrails work together?
   - What makes this different from traditional development?

Then read the guardrails **in order**:

2. **[tests.md](./tests.md)** - Guardrail 1: Correctness Validation
   - What are tests and why do they matter?
   - pytest (backend), Vitest (frontend), Playwright (E2E)
   - How tests enable autonomous validation
   - Test-driven development for AI agents
   - **Security testing**: SQL injection, XSS, auth/authz tests

3. **[linting-and-style.md](./linting-and-style.md)** - Guardrail 2: Consistency Validation
   - What is linting and formatting?
   - Ruff (backend), ESLint + Prettier (frontend)
   - How linters catch bugs and enforce style
   - Auto-fix capabilities for AI agents
   - **Security linting**: Ruff S-prefix rules (S101-S608)

4. **[type-checks.md](./type-checks.md)** - Guardrail 3: Safety Validation
   - What is type checking?
   - MyPy + Pyright (backend), TypeScript strict mode (frontend)
   - How type checking prevents entire classes of bugs
   - Type-safe contracts for AI code generation
   - **Type safety for security**: NewType wrappers for sensitive data

5. **[logging.md](./logging.md)** - Guardrail 4: Observability Validation
   - What is structured logging?
   - The hybrid dotted namespace pattern
   - How logs enable autonomous debugging
   - structlog (backend) with JSON output
   - **Security events**: authentication.*, authorization.*, security.*, audit.*

6. **[architecture.md](./architecture.md)** - Guardrail 5: Clear Structure
   - What is vertical slice architecture?
   - Why it's better than layered architecture for AI
   - Feature slice patterns
   - How to add new features consistently
   - **Security through isolation**: Limited blast radius, feature-level permissions

**Reading time**: ~2-3 hours for all documents

### For Quick Reference

Looking for something specific? Jump directly to:

- **How to run tests?** → [tests.md](./tests.md#running-backend-tests)
- **How to test security?** → [tests.md](./tests.md#security-testing)
- **How to fix linting errors?** → [linting-and-style.md](./linting-and-style.md#running-ruff)
- **What security rules does Ruff enforce?** → [linting-and-style.md](./linting-and-style.md#security-linting-rules)
- **How to add type annotations?** → [type-checks.md](./type-checks.md#type-annotation-patterns)
- **How to use types for security?** → [type-checks.md](./type-checks.md#type-safety-for-security)
- **What event names to use?** → [logging.md](./logging.md#the-hybrid-dotted-namespace-pattern)
- **How to log security events?** → [logging.md](./logging.md#security-events)
- **Where to put new code?** → [architecture.md](./architecture.md#feature-slice-pattern)
- **How to isolate sensitive features?** → [architecture.md](./architecture.md#security-through-isolation)

### For AI Coding Assistants

If you're an AI coding assistant (like Claude Code, GitHub Copilot, etc.) working in this repository:

1. Read **[overview.md](./overview.md)** to understand the PIV loop and your role
2. Reference **[architecture.md](./architecture.md)** when creating new features
3. Check **[logging.md](./logging.md)** for event naming patterns
4. Use **[tests.md](./tests.md)**, **[linting-and-style.md](./linting-and-style.md)**, and **[type-checks.md](./type-checks.md)** when validation fails

These documents explain **why** each guardrail exists and **how** to use it correctly.

## Document Structure

Each guardrail document follows a consistent structure:

### 1. What is it?
Clear definition with simple examples

### 2. Why it matters for traditional development
Benefits for human developers

### 3. Why it's CRITICAL for AI agents
How it enables the PIV loop and autonomous development

### 4. How it works in this repository
Specific tools, configurations, and examples from this codebase

### 5. Examples in action
Real code examples showing before/after

### 6. Best practices
DO's and DON'Ts for effective use

### 7. The Contract
What AI agents promise to enforce

## Who Are These For?

### Human Developers
- **Understand the patterns** - Why this repository is structured this way
- **Onboard quickly** - Learn the guardrails and how to work with them
- **Build confidently** - Know that guardrails will catch mistakes
- **Collaborate with AI** - Understand how AI agents use these guardrails

### AI Agents
- **Generate correct code** - Follow established patterns
- **Self-validate** - Check work against guardrails
- **Debug autonomously** - Use logs and error messages to fix issues
- **Iterate efficiently** - PIV loop until all guardrails pass

### Technical Leaders
- **Evaluate the approach** - Understand the agentic development philosophy
- **Assess completeness** - See what's implemented and what's missing
- **Plan adoption** - Use as a template for your own projects
- **Train teams** - Share as educational resource

### Students & Learners
- **Learn best practices** - Modern development patterns
- **Understand AI-assisted development** - How AI changes software development
- **Study architecture** - Vertical slice architecture explained
- **Build better applications** - Apply these patterns in your projects

## Key Concepts

### The PIV Loop (Plan-Implement-Validate)

```
┌─────────────────────────────────────────────────────────┐
│                    PLAN PHASE                           │
│  - AI agent analyzes requirements                       │
│  - Breaks down into discrete tasks                      │
│  - Determines implementation approach                   │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 IMPLEMENT PHASE                         │
│  - AI agent generates code                              │
│  - Creates tests, updates documentation                 │
│  - Follows architectural patterns                       │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│                 VALIDATE PHASE                          │
│  - Run all guardrails automatically                     │
│  - Tests, type checks, linting, logging validation      │
│  - Architecture compliance                              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─── ✅ ALL PASS ──────► NEXT TASK
                   │
                   └─── ❌ FAILURES ─────► BACK TO IMPLEMENT
                            (with error details)
```

The AI agent **iterates autonomously** until all validation passes. No human intervention needed.

### Why Guardrails Enable Autonomy

**Without guardrails**:
```
AI generates code → Human reviews → Human finds bugs →
Human provides feedback → AI fixes → Human reviews again → Repeat...
```
- Slow (human in the loop)
- Inconsistent (depends on reviewer)
- Not scalable

**With guardrails**:
```
AI generates code → Guardrails validate → Failures found →
AI reads errors → AI fixes → Guardrails pass → Done
```
- Fast (no human needed)
- Consistent (same rules every time)
- Scalable (unlimited parallelism)

### The Hierarchy of Validation

```
┌─────────────────────────────────────────────────────────┐
│                    COMPILE TIME                         │
│  ✅ Type Checks (MyPy, Pyright, TypeScript)             │
│  ✅ Linting (Ruff, ESLint)                              │
│  ✅ Architecture Validation (Vertical Slices)           │
│                                                         │
│  Fastest feedback - catches errors before running code  │
└─────────────────────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│                    TEST TIME                            │
│  ✅ Unit Tests (pytest, vitest)                         │
│  ✅ Integration Tests (database, API)                   │
│  ✅ E2E Tests (Playwright)                              │
│                                                         │
│  Medium speed - validates behavior and correctness      │
└─────────────────────────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│                    RUNTIME                              │
│  ✅ Structured Logging (observability)                  │
│  ✅ Error Monitoring (production issues)                │
│                                                         │
│  Slowest - but critical for debugging production        │
└─────────────────────────────────────────────────────────┘
```

**Goal**: Catch errors as early as possible (compile time > test time > runtime)

## Quick Reference

### Running All Guardrails

**Backend** (from `backend/` directory):
```bash
# Type checks
uv run mypy app/
uv run pyright app/

# Linting
uv run ruff check .
uv run ruff format .

# Tests
uv run pytest -v
```

**Frontend** (from `frontend/` directory):
```bash
# Type checks
npm run typecheck

# Linting
npm run lint
npm run format

# Tests
npm run test
npm run test:e2e
```

### Common Patterns

#### Adding a New Feature

1. **Create feature folder** (see [architecture.md](./architecture.md#feature-slice-pattern))
   - Backend: `app/feature_name/`
   - Frontend: `src/features/feature_name/`

2. **Create required files**
   - Backend: `models.py`, `schemas.py`, `routes.py`, `service.py`, `tests/`
   - Frontend: `types.ts`, `api.ts`, `hooks.ts`, `components/`

3. **Implement with logging** (see [logging.md](./logging.md#example-complete-feature-with-logging))
   - Use event pattern: `feature.action_state`
   - Log start, complete, fail

4. **Add type annotations** (see [type-checks.md](./type-checks.md#type-annotation-patterns))
   - All function parameters
   - All return types
   - No `Any` types

5. **Write tests** (see [tests.md](./tests.md#test-structure))
   - Unit tests for business logic
   - Integration tests for database
   - E2E tests for user workflows
   - Security tests (SQL injection, XSS, auth/authz)

6. **Validate**
   - Run type checks (catch type errors + security issues)
   - Run linter (catch bugs + security vulnerabilities)
   - Run tests (verify correctness + security properties)
   - All pass? ✅ Done!

#### Debugging Failed Validation

When guardrails fail:

1. **Read the error message** - It tells you exactly what's wrong
2. **Fix the issue** - Follow the error's guidance
3. **Re-run validation** - Check if it passes now
4. **Check logs** (if runtime error) - See what happened
5. **Iterate** - Repeat until all pass

## Additional Resources

### In This Repository

- **[../CLAUDE.md](../CLAUDE.md)** - Instructions for Claude Code (AI coding assistant)
- **[../backend/docs/](../backend/docs/)** - Detailed technical standards
  - `pytest-standard.md` - Complete pytest configuration
  - `ruff-standard.md` - Complete Ruff configuration
  - `mypy-standard.md` - Complete MyPy configuration
  - `pyright-standard.md` - Complete Pyright configuration
  - `logging-standard.md` - Complete event taxonomy
- **[../frontend/README.md](../frontend/README.md)** - Frontend setup and commands
- **[../README.md](../README.md)** - Repository overview

### External Resources

- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) - Logging standards
- [Vertical Slice Architecture](https://www.jimmybogard.com/vertical-slice-architecture/) - Architecture pattern
- [pytest Documentation](https://docs.pytest.org/) - Testing framework
- [Ruff Documentation](https://docs.astral.sh/ruff/) - Python linter
- [MyPy Documentation](https://mypy.readthedocs.io/) - Python type checker
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) - TypeScript guide
- [React Query Documentation](https://tanstack.com/query/latest) - Data fetching

## Contributing

When adding new features or modifying existing code:

1. **Follow the patterns** - Consistency is critical for AI agents
2. **Update documentation** - Keep explanations current
3. **Add examples** - Show how to use new patterns
4. **Maintain guardrails** - Don't weaken validation rules
5. **Test everything** - Every feature needs tests

## Philosophy

> **"Guardrails are not restrictions - they are enablers."**

Guardrails don't slow down development. They **accelerate** it by:

- **Catching errors early** - Before they reach production
- **Enabling automation** - AI agents can validate autonomously
- **Building confidence** - Know your code is correct
- **Reducing rework** - Fix issues immediately, not later
- **Scaling development** - More agents, same quality

This repository proves that **foundations first = trust & velocity**.

When guardrails are solid, AI agents move fast and autonomously. When guardrails are missing, every change requires human review.

We choose **automation over manual review**.

---

**Questions or feedback?** Open an issue in the repository or update these documents to make them clearer.

**Ready to build?** Start with [overview.md](./overview.md) and see how autonomous AI development works.
