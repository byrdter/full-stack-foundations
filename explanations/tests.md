# Guardrail 1: Tests (Correctness Validation)

## What Are Tests?

**Software tests** are automated programs that verify your code does what it's supposed to do. Instead of manually clicking through your application to check if features work, you write code that automatically:

1. **Runs your code** with specific inputs
2. **Checks the output** against expected results
3. **Reports failures** when behavior doesn't match expectations

Think of tests as a **robot quality inspector** that can check thousands of scenarios in seconds.

### Example: Testing a Simple Function

```python
# Code to test
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Test code
def test_add():
    """Verify add() works correctly."""
    result = add(2, 3)
    assert result == 5  # If this fails, test fails
```

When you run this test:
- ✅ If `add(2, 3)` returns `5`, the test **passes**
- ❌ If `add(2, 3)` returns anything else, the test **fails**

## Why Tests Matter for Traditional Development

In traditional human-led development, tests provide:

1. **Confidence**: Know that your code works as intended
2. **Regression prevention**: Catch bugs when changing existing code
3. **Documentation**: Tests show how code should be used
4. **Faster debugging**: Pinpoint exactly what broke
5. **Refactoring safety**: Change code structure without breaking behavior

### Without Tests:

```
Developer writes code → Manually test in browser → Deploy → Bug in production 🔥
```

### With Tests:

```
Developer writes code → Run tests → Tests fail → Fix bugs → Tests pass → Deploy ✅
```

## Why Tests Are CRITICAL for AI Agents (PIV Loop)

For AI agents, tests are not just "nice to have" - they are **essential for autonomous operation**.

### The Fundamental Problem:

**AI agents cannot "intuit" correctness.** They can generate code, but they can't "feel" if it's right.

```
Human Developer:
"Hmm, this feels wrong. Let me check edge cases."
(Uses experience, intuition, domain knowledge)

AI Agent:
"I generated code. Is it correct?"
(Needs executable validation to know)
```

### How Tests Enable the PIV Loop

In the **Plan-Implement-Validate** loop, tests are the **validation** mechanism:

```
┌─────────────────────────────────────────────────────────┐
│ PLAN: Add user registration endpoint                   │
│  - Create User model with email validation             │
│  - Add POST /api/auth/register route                   │
│  - Return 201 on success, 400 on invalid email         │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ IMPLEMENT: AI generates code                           │
│  - Writes User model                                   │
│  - Writes registration route                           │
│  - Writes tests for success and error cases            │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ VALIDATE: Run tests                                    │
│  ✅ test_register_valid_email() → PASS                 │
│  ❌ test_register_invalid_email() → FAIL               │
│     AssertionError: Expected 400, got 500              │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─── ❌ FAILURES ───────────────────────┐
                   │                                       │
                   │   Agent reads error:                  │
                   │   "Expected status 400, got 500"      │
                   │                                       │
                   └───► BACK TO IMPLEMENT                 │
                         (Fix error handling)              │
                                                           │
                   ┌───────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ VALIDATE: Run tests again                              │
│  ✅ test_register_valid_email() → PASS                 │
│  ✅ test_register_invalid_email() → PASS               │
│  ✅ test_register_duplicate_email() → PASS             │
└──────────────────┬──────────────────────────────────────┘
                   ▼
              ✅ ALL PASS → NEXT TASK
```

**Key Insight**: The AI agent **iterates autonomously** until all tests pass. No human in the loop.

### What Tests Tell the AI Agent:

1. **Is my code correct?** - Tests pass/fail
2. **What's wrong?** - Error messages
3. **Where's the bug?** - Failing test shows exact scenario
4. **Am I done?** - All tests pass = validation complete

## Types of Tests in This Repository

This repository uses **three levels of testing** to validate different aspects of the system:

```
┌─────────────────────────────────────────────────────────┐
│                    TESTING PYRAMID                      │
│                                                         │
│                        E2E                              │
│                    (Slowest, Most Complete)             │
│                   /         \                           │
│                  /           \                          │
│              Integration  Tests                         │
│             (Medium Speed)                              │
│            /                  \                         │
│           /                    \                        │
│         Unit Tests                                      │
│    (Fast, Isolated)                                     │
└─────────────────────────────────────────────────────────┘
```

### 1. Unit Tests (Fast, Isolated)

**What**: Test individual functions/classes in isolation

**Purpose**: Verify single units of logic work correctly

**Speed**: Milliseconds per test

**Example**:
```python
# Unit test - tests ONLY the validate_email function
def test_validate_email_with_valid_email():
    """Test that valid email passes validation."""
    result = validate_email("test@example.com")
    assert result is True

def test_validate_email_with_invalid_email():
    """Test that invalid email fails validation."""
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email("not-an-email")
```

**For AI Agents**: Fast feedback on individual logic components

### 2. Integration Tests (Medium Speed, Connected Components)

**What**: Test multiple components working together (e.g., database + API)

**Purpose**: Verify components integrate correctly

**Speed**: Hundreds of milliseconds per test

**Example**:
```python
# Integration test - tests database + model interaction
@pytest.mark.integration
async def test_user_creation_in_database():
    """Test creating user in real database."""
    async with get_db() as session:
        user = User(email="test@example.com", age=25)
        session.add(user)
        await session.commit()
        await session.refresh(user)

        assert user.id is not None  # Database assigned ID
        assert user.created_at is not None  # Timestamp was set
```

**For AI Agents**: Validates that generated code works with real infrastructure

### 3. End-to-End (E2E) Tests (Slowest, Full System)

**What**: Test complete user workflows through the UI

**Purpose**: Verify the entire system works from user perspective

**Speed**: Seconds per test

**Example**:
```typescript
// E2E test - tests full user registration flow in browser
test('user can register with valid email', async ({ page }) => {
  await page.goto('/register');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'SecurePass123');
  await page.click('button[type="submit"]');

  await expect(page.locator('.success-message')).toHaveText('Registration successful');
});
```

**For AI Agents**: Final validation that UI changes work in real browser

## Backend Testing: pytest

### What is pytest?

**pytest** is a Python testing framework that makes it easy to write simple, scalable tests.

**Key Features**:
- Simple syntax: just write functions starting with `test_`
- Automatic test discovery: finds all test files and functions
- Rich assertion messages: tells you exactly what went wrong
- Fixtures: reusable test setup code
- Async support: test async/await code (critical for FastAPI)

### Our pytest Configuration

Location: `backend/pyproject.toml`

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # Automatically handle async tests
testpaths = ["app", "tests"]  # Where to find tests
markers = [
    "integration: marks tests requiring real database",
]
```

### Running Backend Tests

```bash
# From backend/ directory

# Run all tests
uv run pytest

# Run with verbose output (see each test name)
uv run pytest -v

# Run only fast unit tests (skip integration)
uv run pytest -m "not integration"

# Run only integration tests
uv run pytest -m integration

# Run specific test file
uv run pytest app/core/tests/test_logging.py

# Run specific test function
uv run pytest app/core/tests/test_logging.py::test_logger_includes_request_id
```

### Backend Test Structure

```
backend/app/
├── core/
│   ├── tests/
│   │   ├── conftest.py           # Fixtures for core tests
│   │   ├── test_config.py        # Test configuration loading
│   │   ├── test_database.py      # Test database connection
│   │   ├── test_logging.py       # Test structured logging
│   │   └── test_middleware.py    # Test request logging
│   ├── config.py
│   ├── database.py
│   ├── logging.py
│   └── middleware.py
└── shared/
    ├── tests/
    │   ├── test_models.py        # Test TimestampMixin
    │   ├── test_schemas.py       # Test pagination schemas
    │   └── test_utils.py         # Test utility functions
    ├── models.py
    ├── schemas.py
    └── utils.py
```

**Pattern**: Tests live next to the code they test (`tests/` subdirectory in each feature)

### Example Backend Unit Test

```python
# backend/app/shared/tests/test_utils.py

from datetime import datetime, timezone
from app.shared.utils import utcnow

def test_utcnow_returns_timezone_aware_datetime():
    """Test that utcnow() returns UTC timezone-aware datetime.

    This test verifies:
    - Returns datetime object
    - Has timezone info (not naive)
    - Timezone is UTC
    """
    result = utcnow()

    assert isinstance(result, datetime)
    assert result.tzinfo is not None  # Not naive
    assert result.tzinfo == timezone.utc
```

**What this validates**:
- ✅ Function returns correct type (`datetime`)
- ✅ Datetime has timezone info (not naive)
- ✅ Timezone is UTC (not local)

**For AI Agents**: If an agent generates code that returns a naive datetime, this test fails immediately.

### Example Backend Integration Test

```python
# backend/app/tests/test_database_integration.py

import pytest
from sqlalchemy import text
from app.core.database import get_db

@pytest.mark.integration
async def test_database_connection_works():
    """Test that database connection is successful.

    Integration test that requires real PostgreSQL database.
    Verifies:
    - Database is accessible
    - Can execute simple query
    - Returns expected result
    """
    async with get_db() as session:
        result = await session.execute(text("SELECT 1 as value"))
        row = result.fetchone()

        assert row is not None
        assert row.value == 1
```

**What this validates**:
- ✅ Database connection succeeds
- ✅ Can execute SQL queries
- ✅ Can read results

**For AI Agents**: If an agent breaks database configuration, this test catches it.

### Example FastAPI Endpoint Test

```python
# backend/app/core/tests/test_health.py

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Create test client for API testing."""
    return TestClient(app)

def test_health_endpoint_returns_200(client):
    """Test that /health endpoint returns success."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_health_endpoint_includes_app_name(client):
    """Test that /health includes application name."""
    response = client.get("/health")
    data = response.json()

    assert "app_name" in data
    assert data["app_name"] == "Obsidian Agent Project"
```

**What this validates**:
- ✅ Endpoint returns 200 (not 404, 500, etc.)
- ✅ Response has correct structure
- ✅ Response includes expected fields

**For AI Agents**: If an agent accidentally breaks the health endpoint, these tests fail.

## Frontend Testing: Vitest + Playwright

### What is Vitest?

**Vitest** is a fast unit testing framework for TypeScript/JavaScript, built on Vite.

**Key Features**:
- Lightning fast (powered by Vite)
- TypeScript support built-in
- React Testing Library integration
- MSW (Mock Service Worker) for API mocking
- Watch mode for instant feedback

### What is Playwright?

**Playwright** is an end-to-end testing framework that runs tests in real browsers.

**Key Features**:
- Tests Chrome, Firefox, Safari
- Real browser automation
- Screenshot/video recording on failure
- Network interception
- Parallel test execution

### Our Frontend Testing Stack

```
┌─────────────────────────────────────────────────────────┐
│              FRONTEND TESTING LAYERS                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Unit Tests (Vitest + React Testing Library)           │
│   - Test individual components                         │
│   - Mock API calls with MSW                            │
│   - Fast (milliseconds)                                │
│                                                         │
│  E2E Tests (Playwright)                                │
│   - Test complete workflows in real browser            │
│   - Mock backend endpoints                             │
│   - Slower (seconds)                                   │
└─────────────────────────────────────────────────────────┘
```

### Running Frontend Tests

```bash
# From frontend/ directory

# Run unit tests (Vitest)
npm run test

# Run unit tests in watch mode (re-run on file changes)
npm run test:watch

# Run unit tests with coverage report
npm run test:cov

# Run E2E tests (Playwright)
npm run test:e2e

# Run E2E tests in UI mode (visual debugging)
npm run test:e2e:ui
```

### Frontend Test Structure

```
frontend/src/
├── features/
│   ├── health/
│   │   ├── components/
│   │   │   ├── HealthCard.tsx
│   │   │   └── HealthCard.test.tsx      # Unit test
│   │   ├── api.ts
│   │   ├── hooks.ts
│   │   └── types.ts
│   └── echo/
│       ├── components/
│       │   ├── EchoForm.tsx
│       │   └── EchoForm.test.tsx        # Unit test
│       ├── api.ts
│       └── hooks.ts
├── shared/
│   └── components/
│       ├── ErrorBoundary.tsx
│       └── ErrorBoundary.test.tsx       # Unit test
└── app/
    └── routes/
        ├── HomePage.tsx
        └── HomePage.test.tsx            # Unit test

frontend/e2e/
└── smoke.spec.ts                        # E2E test
```

**Pattern**: Unit tests live next to components (`ComponentName.test.tsx`)

### Example Frontend Unit Test (Vitest)

```typescript
// frontend/src/features/health/components/HealthCard.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HealthCard } from './HealthCard';

describe('HealthCard', () => {
  it('displays application name from health data', () => {
    // Render component with test data
    render(<HealthCard data={{ status: 'ok', app_name: 'Test App' }} />);

    // Assert that app name is displayed
    expect(screen.getByText('Test App')).toBeInTheDocument();
  });

  it('displays "ok" status with green indicator', () => {
    render(<HealthCard data={{ status: 'ok', app_name: 'Test App' }} />);

    const statusElement = screen.getByText(/status.*ok/i);
    expect(statusElement).toBeInTheDocument();
    expect(statusElement).toHaveClass('text-green-600');
  });
});
```

**What this validates**:
- ✅ Component renders without crashing
- ✅ Displays correct data from props
- ✅ Applies correct CSS classes

**For AI Agents**: If an agent breaks component rendering, these tests fail instantly.

### Example Frontend E2E Test (Playwright)

```typescript
// frontend/e2e/smoke.spec.ts

import { test, expect } from '@playwright/test';

test('health card displays application status', async ({ page }) => {
  // Mock the API response
  await page.route('**/health', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'ok',
        app_name: 'Full Stack Foundations',
      }),
    });
  });

  // Navigate to home page
  await page.goto('/');

  // Wait for health card to appear
  const healthCard = page.locator('[data-testid="health-card"]');
  await expect(healthCard).toBeVisible();

  // Verify content
  await expect(healthCard).toContainText('Full Stack Foundations');
  await expect(healthCard).toContainText('ok');
});
```

**What this validates**:
- ✅ Page loads successfully
- ✅ API call is made
- ✅ Component renders with API data
- ✅ Correct content is displayed to user

**For AI Agents**: Final validation that the entire feature works end-to-end.

### Mocking API Calls (MSW)

**Problem**: Unit tests shouldn't make real API calls (slow, unreliable, requires backend)

**Solution**: Mock Service Worker (MSW) intercepts API calls and returns fake data

```typescript
// frontend/tests/mocks/handlers.ts

import { http, HttpResponse } from 'msw';

export const handlers = [
  // Mock GET /health
  http.get('*/health', () => {
    return HttpResponse.json({
      status: 'ok',
      app_name: 'Test App',
    });
  }),

  // Mock POST /echo
  http.post('*/echo', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      message: body.message,
      timestamp: new Date().toISOString(),
    });
  }),
];
```

**Benefits**:
- ✅ Tests run fast (no network delay)
- ✅ Tests work offline
- ✅ Tests are deterministic (same results every time)
- ✅ Can test error scenarios easily

**For AI Agents**: Enables fast validation without backend dependency.

## Test-Driven Development (TDD) for AI Agents

In the PIV loop, AI agents can practice **test-driven development**:

```
┌─────────────────────────────────────────────────────────┐
│ 1. PLAN: Agent reads requirements                      │
│    "Add endpoint to delete user by ID"                 │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 2. IMPLEMENT: Agent writes TESTS FIRST                 │
│    - test_delete_user_success()                        │
│    - test_delete_user_not_found()                      │
│    - test_delete_user_unauthorized()                   │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 3. VALIDATE: Run tests (expected to FAIL)             │
│    ❌ All tests fail (endpoint doesn't exist yet)      │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 4. IMPLEMENT: Agent writes CODE to make tests pass    │
│    - Create DELETE /users/{id} endpoint               │
│    - Add authorization check                          │
│    - Handle not found case                            │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ 5. VALIDATE: Run tests again                          │
│    ✅ test_delete_user_success() → PASS                │
│    ✅ test_delete_user_not_found() → PASS              │
│    ✅ test_delete_user_unauthorized() → PASS           │
└──────────────────┬──────────────────────────────────────┘
                   ▼
              ✅ DONE - NEXT TASK
```

**Why this works for AI**:
1. Tests define the **specification** explicitly
2. Failing tests guide **implementation**
3. Passing tests confirm **completion**
4. No ambiguity about "done"

## What Makes Tests AI-Friendly?

Good tests for AI agents have these properties:

### 1. Clear Failure Messages

```python
# ❌ BAD - Vague error
assert result
# AssertionError: assert False

# ✅ GOOD - Specific error
assert result.status_code == 200, f"Expected 200, got {result.status_code}"
# AssertionError: Expected 200, got 404
```

**Why**: AI agent can read "Expected 200, got 404" and know exactly what to fix.

### 2. Descriptive Test Names

```python
# ❌ BAD - Unclear what this tests
def test_user():
    ...

# ✅ GOOD - Clear scenario and expectation
def test_user_registration_fails_with_duplicate_email():
    ...
```

**Why**: Agent can see which scenario failed and understand the context.

### 3. One Assertion Per Concept

```python
# ❌ BAD - Multiple unrelated assertions
def test_user_endpoint():
    response = client.post("/users", json=data)
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert response.json()["created_at"] is not None
    assert response.headers["Content-Type"] == "application/json"

# ✅ GOOD - Separate concerns
def test_user_creation_returns_201():
    response = client.post("/users", json=data)
    assert response.status_code == 201

def test_user_creation_returns_email():
    response = client.post("/users", json=data)
    assert response.json()["email"] == "test@example.com"
```

**Why**: When test fails, agent knows exactly which aspect is broken.

### 4. Test Both Success and Failure Cases

```python
# Test success case
def test_login_with_valid_credentials():
    response = client.post("/login", json={"email": "user@example.com", "password": "correct"})
    assert response.status_code == 200

# Test failure case
def test_login_with_invalid_credentials():
    response = client.post("/login", json={"email": "user@example.com", "password": "wrong"})
    assert response.status_code == 401

# Test edge case
def test_login_with_missing_password():
    response = client.post("/login", json={"email": "user@example.com"})
    assert response.status_code == 422  # Validation error
```

**Why**: Agent validates all code paths, not just happy path.

## Testing in CI/CD Pipeline

Our tests run automatically on every code change via GitHub Actions:

```yaml
# .github/workflows/backend.yml

- name: Run backend tests
  run: |
    cd backend
    uv run pytest -v

- name: Run backend type checks
  run: |
    cd backend
    uv run mypy app/
    uv run pyright app/
```

```yaml
# .github/workflows/frontend.yml

- name: Run frontend tests
  run: |
    cd frontend
    npm run test

- name: Run E2E tests
  run: |
    cd frontend
    npm run test:e2e
```

**Result**: Every commit is automatically validated. If tests fail, the commit is marked as failing.

**For AI Agents**: Continuous validation means agents get feedback on every change.

## Current Test Coverage

### Backend Tests (81+ tests)

```
backend/app/
├── core/tests/          # Infrastructure tests
│   ├── test_config.py        (15 tests)
│   ├── test_database.py      (12 tests)
│   ├── test_exceptions.py    (9 tests)
│   ├── test_health.py        (8 tests)
│   ├── test_logging.py       (7 tests)
│   └── test_middleware.py    (6 tests)
└── shared/tests/        # Shared utility tests
    ├── test_models.py        (10 tests)
    ├── test_schemas.py       (8 tests)
    └── test_utils.py         (6 tests)
```

**All tests pass in < 1 second** (fast feedback for AI agents)

### Frontend Tests

```
frontend/src/
├── features/
│   ├── health/components/HealthCard.test.tsx
│   ├── readiness/components/ReadinessCard.test.tsx
│   └── echo/components/EchoForm.test.tsx
├── shared/components/ErrorBoundary.test.tsx
└── app/routes/HomePage.test.tsx

frontend/e2e/
└── smoke.spec.ts  # Tests all features end-to-end
```

## Security Testing

Security testing is a **critical extension** of the testing guardrail. While functional tests validate that code works correctly, security tests validate that code works **safely**.

### Why Security Testing Matters for AI Agents

AI agents can inadvertently generate vulnerable code because they:
- May not recognize security anti-patterns
- Could concatenate strings instead of using parameterized queries
- Might not sanitize user input properly
- Could expose sensitive data in responses

**Security tests catch these issues automatically** in the validation phase of the PIV loop.

### Types of Security Tests

#### 1. SQL Injection Prevention

```python
# backend/app/features/users/tests/test_security.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_user_search_prevents_sql_injection():
    """Test that user search is immune to SQL injection attacks.

    This test verifies:
    - SQL injection attempts are handled safely
    - Parameterized queries are used (not string concatenation)
    - No database errors leak to the response
    """
    # Common SQL injection payloads
    injection_attempts = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "admin' --",
        "' UNION SELECT * FROM users --",
    ]

    for payload in injection_attempts:
        response = client.get(f"/users/search?q={payload}")

        # Should not cause server error
        assert response.status_code in [200, 400, 422]

        # Should not return all users (sign of successful injection)
        if response.status_code == 200:
            data = response.json()
            assert not (isinstance(data, list) and len(data) > 100)

        # Should not leak database errors
        if response.status_code >= 400:
            error = response.json().get("detail", "")
            assert "SQL" not in error
            assert "database" not in error.lower()
```

**For AI Agents**: If agent uses string concatenation for SQL, this test fails.

#### 2. Cross-Site Scripting (XSS) Prevention

```python
def test_user_profile_sanitizes_xss_attacks():
    """Test that user-submitted content is sanitized to prevent XSS.

    This test verifies:
    - HTML tags are escaped or removed
    - JavaScript cannot be injected
    - Output is safe for rendering in browser
    """
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(1)'>",
    ]

    for payload in xss_payloads:
        # Attempt to create user with XSS in name
        response = client.post("/users", json={
            "email": "test@example.com",
            "name": payload
        })

        # Should either reject or sanitize
        if response.status_code == 201:
            user_data = response.json()
            # Name should be escaped/sanitized
            assert "<script>" not in user_data["name"]
            assert "javascript:" not in user_data["name"]
            assert "<iframe" not in user_data["name"]
```

**For AI Agents**: Ensures all user input is sanitized before storage/display.

#### 3. Authentication & Authorization Testing

```python
def test_protected_endpoint_requires_authentication():
    """Test that protected endpoints reject unauthenticated requests."""
    # Attempt to access protected resource without token
    response = client.get("/users/me")

    assert response.status_code == 401
    assert "authenticate" in response.json()["detail"].lower()

def test_user_cannot_access_other_users_data():
    """Test that users cannot access other users' private data.

    This test verifies:
    - Authorization checks are enforced
    - User A cannot read/modify User B's data
    - Horizontal privilege escalation is prevented
    """
    # Create two users
    user_a_token = create_test_user_and_login("usera@example.com")
    user_b_token = create_test_user_and_login("userb@example.com")

    # User A tries to access User B's profile
    response = client.get(
        "/users/me",  # This should return User B's ID
        headers={"Authorization": f"Bearer {user_b_token}"}
    )
    user_b_id = response.json()["id"]

    # User A attempts to access User B's data
    response = client.get(
        f"/users/{user_b_id}",
        headers={"Authorization": f"Bearer {user_a_token}"}
    )

    # Should be forbidden
    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()

def test_admin_actions_require_admin_role():
    """Test that admin-only actions are protected by role checks."""
    # Create regular user
    user_token = create_test_user_and_login("user@example.com", role="user")

    # Attempt admin action (e.g., delete any user)
    response = client.delete(
        "/admin/users/123",
        headers={"Authorization": f"Bearer {user_token}"}
    )

    # Should be forbidden
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()
```

**For AI Agents**: Validates authentication/authorization logic is correctly implemented.

#### 4. Rate Limiting & Abuse Prevention

```python
import pytest

@pytest.mark.integration
def test_login_endpoint_has_rate_limiting():
    """Test that login endpoint prevents brute force attacks.

    This test verifies:
    - Rate limiting is enforced
    - Excessive requests are blocked
    - Legitimate requests are allowed
    """
    # Attempt many failed logins
    for i in range(10):
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": f"wrong_password_{i}"
        })

        # After threshold, should be rate limited
        if i >= 5:
            assert response.status_code == 429  # Too Many Requests
            assert "rate limit" in response.json()["detail"].lower()
```

**For AI Agents**: Ensures rate limiting is implemented for sensitive endpoints.

#### 5. Sensitive Data Exposure Prevention

```python
def test_user_response_excludes_password_hash():
    """Test that sensitive data is never exposed in API responses.

    This test verifies:
    - Password hashes are not returned
    - Sensitive fields are excluded from responses
    - Response matches schema (no extra fields)
    """
    # Create user
    response = client.post("/users", json={
        "email": "test@example.com",
        "password": "SecurePassword123!"
    })

    assert response.status_code == 201
    user_data = response.json()

    # Sensitive fields should NOT be in response
    assert "password" not in user_data
    assert "password_hash" not in user_data
    assert "hashed_password" not in user_data

    # Only expected fields
    assert set(user_data.keys()) == {"id", "email", "created_at"}

def test_error_messages_dont_leak_implementation_details():
    """Test that error messages don't expose system internals."""
    # Trigger database error (e.g., invalid ID format)
    response = client.get("/users/invalid_id_format")

    # Should not leak stack traces, SQL, file paths
    if response.status_code >= 500:
        error = response.json()
        error_str = str(error).lower()

        assert "traceback" not in error_str
        assert "/app/" not in error_str  # No file paths
        assert "postgresql" not in error_str  # No database details
        assert "sqlalchemy" not in error_str
```

**For AI Agents**: Prevents accidental exposure of sensitive data or implementation details.

#### 6. Input Validation & Injection Prevention

```python
def test_email_validation_prevents_header_injection():
    """Test that email fields prevent email header injection attacks."""
    injection_attempts = [
        "test@example.com\nBcc: attacker@evil.com",
        "test@example.com\r\nCc: attacker@evil.com",
        "test@example.com%0ABcc:attacker@evil.com",
    ]

    for payload in injection_attempts:
        response = client.post("/users", json={
            "email": payload,
            "name": "Test User"
        })

        # Should reject invalid email format
        assert response.status_code == 422
        assert "email" in response.json()["detail"][0]["loc"]

def test_path_traversal_prevention():
    """Test that file path inputs prevent directory traversal attacks."""
    traversal_attempts = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
    ]

    for payload in traversal_attempts:
        response = client.get(f"/files/{payload}")

        # Should either reject or normalize path
        assert response.status_code in [400, 404]
        # Should not expose system files
        if response.status_code == 200:
            assert "root:" not in response.text  # Unix passwd file
```

**For AI Agents**: Validates proper input sanitization and validation.

### Frontend Security Testing

#### 1. XSS Prevention in React Components

```typescript
// frontend/src/features/users/components/UserProfile.test.tsx

import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile Security', () => {
  it('should escape HTML in user-generated content', () => {
    const maliciousUser = {
      id: 1,
      name: '<script>alert("XSS")</script>',
      bio: '<img src=x onerror=alert(1)>',
    };

    render(<UserProfile user={maliciousUser} />);

    // Script tags should be rendered as text, not executed
    expect(screen.getByText(/script/i)).toBeInTheDocument();

    // Should not find actual script elements in DOM
    const scripts = document.querySelectorAll('script');
    const maliciousScripts = Array.from(scripts).filter(
      s => s.textContent?.includes('alert')
    );
    expect(maliciousScripts).toHaveLength(0);
  });

  it('should sanitize dangerous attributes', () => {
    const user = {
      id: 1,
      website: 'javascript:alert(1)',
      name: 'Test User',
    };

    render(<UserProfile user={user} />);

    // Links should not have javascript: protocol
    const links = screen.queryAllByRole('link');
    links.forEach(link => {
      expect(link.getAttribute('href')).not.toMatch(/^javascript:/i);
    });
  });
});
```

**For AI Agents**: Ensures React components properly escape user content.

#### 2. Authentication State Testing

```typescript
// frontend/src/features/auth/components/ProtectedRoute.test.tsx

import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';

describe('ProtectedRoute Security', () => {
  it('should redirect unauthenticated users to login', () => {
    // Mock unauthenticated state
    const mockUseAuth = vi.fn(() => ({ isAuthenticated: false }));

    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    );

    // Should not show protected content
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();

    // Should redirect to login
    expect(window.location.pathname).toBe('/login');
  });

  it('should show protected content for authenticated users', () => {
    const mockUseAuth = vi.fn(() => ({ isAuthenticated: true }));

    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </MemoryRouter>
    );

    // Should show protected content
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
});
```

**For AI Agents**: Validates authentication guards work correctly.

### Security Test Markers

Use pytest markers to categorize security tests:

```python
# backend/pyproject.toml

[tool.pytest.ini_options]
markers = [
    "integration: marks tests requiring real database",
    "security: marks security-specific tests",
    "auth: marks authentication/authorization tests",
]
```

Run only security tests:
```bash
# Run all security tests
uv run pytest -m security -v

# Run auth tests specifically
uv run pytest -m auth -v

# Run security tests in CI
uv run pytest -m security --maxfail=1
```

### Security Testing Best Practices

#### ✅ DO:

1. **Test common attack vectors** - SQL injection, XSS, CSRF, path traversal
2. **Test authentication boundaries** - Unauthenticated, authenticated, admin
3. **Test authorization logic** - Ensure users can only access their own data
4. **Test input validation** - All user inputs should be validated
5. **Test error handling** - Errors shouldn't leak sensitive information
6. **Use security test markers** - Categorize and run security tests separately
7. **Test rate limiting** - Prevent brute force and abuse
8. **Fail fast in CI** - Use `--maxfail=1` for security tests

#### ❌ DON'T:

1. **Skip security tests** - They're as important as functional tests
2. **Test only happy paths** - Security is about edge cases and abuse
3. **Assume frameworks handle it** - Always verify security features work
4. **Ignore authentication** - Test both authenticated and unauthenticated scenarios
5. **Expose test credentials** - Use environment variables for test users
6. **Skip frontend security** - XSS and CSRF affect frontend too

### Security Test Coverage Goals

Aim for **100% coverage** on:
- Authentication logic (login, logout, token validation)
- Authorization checks (role checks, ownership validation)
- Input validation (all user inputs)
- Sensitive data handling (password hashing, PII)

**For AI Agents**: Security tests provide **explicit rules** about what constitutes secure code. When an agent generates authentication logic, these tests validate it's secure.

## Best Practices for AI-Friendly Tests

### ✅ DO:

1. **Write descriptive test names** - `test_user_registration_fails_with_invalid_email()`
2. **Test edge cases** - Empty strings, null values, boundary conditions
3. **Use clear assertions** - `assert result == expected, f"Expected {expected}, got {result}"`
4. **Mock external dependencies** - Don't make real API calls, database calls in unit tests
5. **Keep tests fast** - Unit tests should run in milliseconds
6. **Use markers** - `@pytest.mark.integration` for slow tests
7. **Test error cases** - Not just happy path

### ❌ DON'T:

1. **Write vague test names** - `test_user()`, `test_api()`
2. **Skip error testing** - Only testing success scenarios
3. **Use magic values** - `assert result == 42` (what is 42?)
4. **Make tests dependent** - Test 2 requires Test 1 to run first
5. **Ignore failing tests** - Fix them or delete them
6. **Write slow unit tests** - Mock databases, APIs, file I/O

## Summary: Tests as the Foundation of Autonomous Development

Tests are the **most critical guardrail** for AI agents because they:

1. **Provide immediate feedback** - Agent knows instantly if code works
2. **Enable self-correction** - Error messages guide fixes
3. **Define "done"** - All tests pass = task complete
4. **Catch regressions** - Ensure new changes don't break existing features
5. **Enable confidence** - Humans can trust AI-generated code
6. **Enable velocity** - No waiting for manual QA

### The Testing Contract for AI Agents:

```
┌─────────────────────────────────────────────────────────┐
│          AI AGENT PROMISE (Enforced by Tests)           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  "I will not move to the next task until:              │
│                                                         │
│   ✅ All unit tests pass                               │
│   ✅ All integration tests pass                        │
│   ✅ All E2E tests pass                                │
│   ✅ No new test failures introduced                   │
│   ✅ Coverage meets minimum threshold                  │
│                                                         │
│  If ANY test fails, I will:                            │
│                                                         │
│   1. Read the error message                            │
│   2. Identify the failing scenario                     │
│   3. Fix the code                                      │
│   4. Re-run tests                                      │
│   5. Repeat until all tests pass                       │
│                                                         │
│  I will NEVER skip tests or mark them as 'todo'."      │
└─────────────────────────────────────────────────────────┘
```

This contract enables **autonomous, trustworthy development** at machine speed.

## Next Steps

1. Read [linting-and-style.md](./linting-and-style.md) to understand code consistency validation
2. Read [type-checks.md](./type-checks.md) to understand type safety guarantees
3. Explore `backend/app/core/tests/` for real test examples
4. Explore `frontend/src/features/*/components/*.test.tsx` for frontend test examples
5. Run `uv run pytest -v` in `backend/` to see tests in action
6. Run `npm run test` in `frontend/` to see frontend tests

Remember: **Tests are executable specifications**. They tell the AI agent exactly what "correct" means.
