# Guardrail 2: Linting & Style (Consistency Validation)

## What Are Linting and Style Checks?

**Linting** is the process of analyzing code to find potential errors, bugs, stylistic issues, and suspicious constructs.

**Style/Formatting** is the process of automatically arranging code to follow consistent visual patterns (indentation, spacing, line breaks, etc.).

Think of linting as a **grammar checker** and formatting as **auto-formatting** in Microsoft Word - but for code.

### Example: Why Consistency Matters

```python
# Different developers, different styles:

# Developer A writes:
def calculateTotal(items:list)->float:
    total=0
    for item in items:total+=item['price']
    return total

# Developer B writes:
def calculate_total(items: list) -> float:
    total = 0
    for item in items:
        total += item["price"]
    return total
```

Both work, but:
- One is harder to read
- Mixing styles in the same codebase creates confusion
- Code reviews waste time debating style preferences

**Solution**: Automated linting and formatting enforce a single, consistent style.

## Why Linting & Style Matter for Traditional Development

In human-led development, consistent code style provides:

1. **Readability**: Code is easier to understand when it follows patterns
2. **Maintainability**: Consistent structure makes changes predictable
3. **Bug prevention**: Linters catch common mistakes (unused variables, missing imports)
4. **Team efficiency**: No debates about style preferences
5. **Code review focus**: Review logic, not formatting

### The Cost of Inconsistency:

```
Without Linting:
Developer writes code → Code review focuses on style →
Back-and-forth on formatting → Finally merge after fixing style

With Linting:
Developer writes code → Linter auto-fixes style →
Code review focuses on logic → Merge faster
```

## Why Linting & Style Are CRITICAL for AI Agents (PIV Loop)

For AI agents, linting and formatting serve a different purpose than for humans:

### The Fundamental Problem:

**AI agents don't have aesthetic preferences.** They can generate syntactically correct code, but without guardrails, the style will be inconsistent and may contain subtle bugs.

```
Human Developer:
"I prefer single quotes and 2-space indentation."
(Has opinions, follows team conventions)

AI Agent:
"I will generate code. What style should I use?"
(Needs explicit rules, has no preferences)
```

### How Linting Enables the PIV Loop

In the **Plan-Implement-Validate** loop, linting is part of **validation**:

```
┌─────────────────────────────────────────────────────────┐
│ PLAN: Add user authentication endpoint                 │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ IMPLEMENT: AI generates code                           │
│  - Creates authenticate() function                     │
│  - Adds route handler                                  │
│  - Imports required libraries                          │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ VALIDATE: Run linter (ruff check .)                    │
│  ❌ F401: Unused import `hashlib`                      │
│  ❌ E501: Line too long (115 > 100 characters)         │
│  ❌ I001: Import blocks incorrectly ordered            │
│  ❌ ANN001: Missing type annotation for `password`     │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─── ❌ FAILURES ───────────────────────┐
                   │                                       │
                   │   Agent reads errors:                 │
                   │   - Remove unused import              │
                   │   - Break long line                   │
                   │   - Sort imports                      │
                   │   - Add type hint                     │
                   │                                       │
                   └───► BACK TO IMPLEMENT                 │
                         (Fix issues)                      │
                                                           │
                   ┌───────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ VALIDATE: Run linter again (ruff check .)              │
│  ✅ No issues found                                    │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ VALIDATE: Run formatter (ruff format .)                │
│  ✅ All files formatted correctly                      │
└──────────────────┬──────────────────────────────────────┘
                   ▼
              ✅ ALL PASS → NEXT TASK
```

**Key Insight**: The linter provides **explicit, actionable errors** that the agent can fix autonomously.

### What Linting Tells the AI Agent:

1. **Is my code clean?** - Linter passes/fails
2. **What's wrong?** - Specific error codes and messages
3. **Where's the issue?** - File path and line number
4. **How to fix it?** - Many linters auto-fix issues

## Types of Issues Linters Catch

### 1. Code Style Issues

**What**: Visual inconsistencies (spacing, indentation, quotes)

**Example**:
```python
# ❌ Inconsistent (linter catches these)
def myFunction( x,y ):
    result=x+y
    return result

# ✅ Consistent (after auto-format)
def my_function(x, y):
    result = x + y
    return result
```

**For AI Agents**: Ensures all generated code follows the same visual pattern.

### 2. Logical Errors

**What**: Code that compiles but is likely wrong

**Example**:
```python
# ❌ Linter catches: Undefined variable
def process_data():
    result = calculate()  # calculate() not defined
    return result

# ❌ Linter catches: Unused variable
def get_user():
    user = fetch_user()  # Variable assigned but never used
    return None
```

**For AI Agents**: Catches mistakes in generated code before runtime.

### 3. Security Vulnerabilities

**What**: Dangerous patterns that could create security holes

**Example**:
```python
# ❌ Linter catches: Hardcoded password
PASSWORD = "admin123"

# ❌ Linter catches: SQL injection risk
query = f"SELECT * FROM users WHERE email = '{user_input}'"

# ❌ Linter catches: Dangerous eval()
eval(user_input)
```

**For AI Agents**: Prevents AI from generating vulnerable code.

### 4. Import Organization

**What**: Imports in random order make code harder to read

**Example**:
```python
# ❌ Disorganized imports
from app.core.database import get_db
import os
from fastapi import FastAPI
import sys
from app.shared.utils import utcnow

# ✅ Organized imports (after linter fixes)
import os
import sys

from fastapi import FastAPI

from app.core.database import get_db
from app.shared.utils import utcnow
```

**For AI Agents**: Consistent import organization across all files.

### 5. Type Annotation Enforcement

**What**: Missing or incomplete type hints

**Example**:
```python
# ❌ Linter catches: Missing type annotations
def process_user(user):
    return user.email

# ✅ Complete type annotations
def process_user(user: User) -> str:
    return user.email
```

**For AI Agents**: Forces agent to include type hints (enables type checking).

## Backend Linting: Ruff

### What is Ruff?

**Ruff** is an extremely fast Python linter and formatter written in Rust. It replaces multiple tools (Flake8, isort, Black, pyupgrade) with a single, performant solution.

**Key Features**:
- **10-100x faster** than traditional Python linters
- **Auto-fixes** most issues automatically
- **800+ rules** from popular Python linters
- **Deterministic** - same input always produces same output

### Why Ruff for AI Agents?

1. **Speed**: Fast feedback loop (lints entire codebase in milliseconds)
2. **Auto-fix**: Agent can automatically fix most issues
3. **Comprehensive**: Catches errors, style, security, complexity
4. **Consistent**: Same formatting every time

### Our Ruff Configuration

Location: `backend/pyproject.toml`

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors (style)
    "W",      # pycodestyle warnings
    "F",      # pyflakes (logical errors)
    "I",      # isort (import sorting)
    "B",      # flake8-bugbear (bug detection)
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade (modernize syntax)
    "ANN",    # flake8-annotations (type hints)
    "S",      # flake8-bandit (security)
    "DTZ",    # flake8-datetimez (timezone-aware datetimes)
    "RUF",    # Ruff-specific rules
    "ARG",    # flake8-unused-arguments
    "PTH",    # flake8-use-pathlib (prefer Path over os.path)
]
```

### Rule Categories Explained

| Category | What It Catches | Why It Matters for AI |
|----------|----------------|----------------------|
| **E/W** | Style violations (PEP 8) | Consistent formatting |
| **F** | Logical errors (undefined names, unused imports) | Prevents broken code |
| **I** | Import sorting | Organized, predictable imports |
| **B** | Common bugs (mutable defaults, etc.) | Catches subtle mistakes |
| **C4** | Inefficient comprehensions | Cleaner, faster code |
| **UP** | Outdated syntax | Modern Python patterns |
| **ANN** | Missing type annotations | Enables type checking |
| **S** | Security vulnerabilities | Prevents dangerous code |
| **DTZ** | Timezone-naive datetimes | Prevents time bugs |
| **RUF** | Ruff best practices | Performance, clarity |
| **ARG** | Unused arguments | Clean function signatures |
| **PTH** | Using `os.path` instead of `pathlib` | Modern path handling |

### Running Ruff

```bash
# From backend/ directory

# Check for linting issues
uv run ruff check .

# Auto-fix issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Check + format in one command
uv run ruff check . --fix && uv run ruff format .
```

### Example: Ruff in Action

**Before linting**:
```python
# backend/app/auth/service.py

import sys
from fastapi import FastAPI
from app.core.database import get_db
import os
from app.shared.utils import utcnow


def authenticate_user(email,password):
    user=get_user_by_email(email)
    if user and verify_password(password,user.password_hash):
        return user
    return None
```

**Run linter**:
```bash
$ uv run ruff check app/auth/service.py

app/auth/service.py:1:8: F401 [*] `sys` imported but unused
app/auth/service.py:4:8: F401 [*] `os` imported but unused
app/auth/service.py:8:21: ANN001 Missing type annotation for function argument `email`
app/auth/service.py:8:27: ANN001 Missing type annotation for function argument `password`
app/auth/service.py:8:36: ANN201 Missing return type annotation for public function
app/auth/service.py:9:9: E225 Missing whitespace around operator

Found 6 errors.
[*] 2 fixable with the `--fix` option.
```

**Run auto-fix**:
```bash
$ uv run ruff check app/auth/service.py --fix
Fixed 2 errors.

$ uv run ruff format app/auth/service.py
1 file reformatted.
```

**After linting + formatting**:
```python
# backend/app/auth/service.py

from fastapi import FastAPI

from app.core.database import get_db
from app.shared.utils import utcnow


def authenticate_user(email: str, password: str) -> User | None:
    """Authenticate user with email and password.

    Args:
        email: User email address
        password: Plain text password to verify

    Returns:
        User object if authentication succeeds, None otherwise
    """
    user = get_user_by_email(email)
    if user and verify_password(password, user.password_hash):
        return user
    return None
```

**What changed**:
- ✅ Removed unused imports (`sys`, `os`)
- ✅ Sorted imports (stdlib → third-party → first-party)
- ✅ Added type annotations (`email: str`, `password: str`, `-> User | None`)
- ✅ Fixed spacing around `=` operator
- ✅ Consistent formatting (spaces, line breaks)

**For AI Agents**: The agent sees clear errors, runs `--fix`, and the code is clean.

## Frontend Linting: ESLint + Prettier

### What is ESLint?

**ESLint** is a JavaScript/TypeScript linter that finds and fixes problems in your code.

**Key Features**:
- **Configurable rules** for JavaScript/TypeScript/React
- **Auto-fix** for many issues
- **Plugin ecosystem** for frameworks (React, Vue, etc.)

### What is Prettier?

**Prettier** is an opinionated code formatter that enforces consistent style.

**Key Features**:
- **Automatic formatting** - no configuration needed
- **Deterministic** - same code always formats the same way
- **Integrates with ESLint** - linting + formatting in one pipeline

### Why ESLint + Prettier for AI Agents?

1. **ESLint catches bugs** - Unused variables, missing dependencies, potential null references
2. **Prettier enforces style** - Consistent quotes, indentation, line breaks
3. **Auto-fix everything** - Agent can fix issues without manual intervention
4. **React-specific rules** - Catches React Hook mistakes, accessibility issues

### Our ESLint Configuration

Location: `frontend/.eslintrc.cjs`

```javascript
module.exports = {
  parser: "@typescript-eslint/parser",
  plugins: [
    "@typescript-eslint",  // TypeScript rules
    "react",               // React best practices
    "react-hooks",         // React Hooks rules
    "jsx-a11y",            // Accessibility rules
    "import",              // Import organization
  ],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended",
    "plugin:import/recommended",
    "prettier",  // Prettier integration
  ],
  rules: {
    "import/order": "error",  // Enforce import sorting
  },
};
```

### ESLint Rule Categories

| Plugin | What It Catches | Why It Matters for AI |
|--------|----------------|----------------------|
| **eslint:recommended** | Basic JS errors (undefined vars, etc.) | Prevents broken code |
| **@typescript-eslint** | TypeScript-specific issues | Type safety violations |
| **react** | React best practices | Proper component patterns |
| **react-hooks** | Hooks mistakes (missing deps, wrong order) | Prevents runtime bugs |
| **jsx-a11y** | Accessibility violations | Ensures usable UI |
| **import** | Import organization | Clean, sorted imports |
| **prettier** | Formatting consistency | Uniform code style |

### Our Prettier Configuration

Location: `frontend/.prettierrc`

```json
{
  "singleQuote": true,      // Use 'single' not "double"
  "trailingComma": "all",   // Add trailing commas everywhere
  "printWidth": 100,        // 100 characters per line
  "semi": true              // Always use semicolons
}
```

### Running Frontend Linting

```bash
# From frontend/ directory

# Run ESLint
npm run lint

# Run ESLint with auto-fix
npm run lint -- --fix

# Run Prettier check
npm run format

# Run Prettier with auto-fix
npm run format:fix

# Run both in one command
npm run lint -- --fix && npm run format:fix
```

### Example: ESLint + Prettier in Action

**Before linting**:
```typescript
// frontend/src/features/auth/components/LoginForm.tsx

import { Button } from '@/shared/components/Button'
import { useState } from 'react'
import { Input } from '@/shared/components/Input'
import React from 'react'

export function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    console.log(email,password)
  }

  return <form onSubmit={handleSubmit}>
    <Input value={email} onChange={(e)=>setEmail(e.target.value)} />
    <Input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" />
    <Button type="submit">Login</Button>
  </form>
}
```

**Run linter**:
```bash
$ npm run lint

frontend/src/features/auth/components/LoginForm.tsx
  4:8   warning  'React' is defined but never used  @typescript-eslint/no-unused-vars
  10:23 error    Missing type annotation for 'e'    @typescript-eslint/explicit-function-return-type
  16:22 error    Missing space before '=>'          prettier/prettier
  17:26 error    Missing space before '=>'          prettier/prettier

✖ 4 problems (3 errors, 1 warning)
```

**Run auto-fix**:
```bash
$ npm run lint -- --fix
$ npm run format:fix
```

**After linting + formatting**:
```typescript
// frontend/src/features/auth/components/LoginForm.tsx

import { useState } from 'react';

import { Button } from '@/shared/components/Button';
import { Input } from '@/shared/components/Input';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log(email, password);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <Input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        type="password"
      />
      <Button type="submit">Login</Button>
    </form>
  );
}
```

**What changed**:
- ✅ Removed unused `React` import
- ✅ Sorted imports (React stdlib → internal)
- ✅ Added type annotation (`e: React.FormEvent`)
- ✅ Fixed spacing around arrow functions
- ✅ Reformatted JSX for readability
- ✅ Consistent quotes, semicolons, trailing commas

**For AI Agents**: Clear errors → run auto-fix → clean code.

## Pre-commit Hooks: Automatic Validation

This repository uses **Husky + lint-staged** to run linting automatically before every commit:

```json
// frontend/package.json

"lint-staged": {
  "*.{ts,tsx}": [
    "eslint --fix",
    "prettier --write"
  ]
}
```

**How it works**:
```
┌─────────────────────────────────────────────────────────┐
│ Developer (or AI agent) runs: git commit               │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ Pre-commit hook triggers                               │
│  - Run ESLint on staged files                          │
│  - Run Prettier on staged files                        │
│  - Auto-fix issues                                     │
└──────────────────┬──────────────────────────────────────┘
                   ▼
            ┌──────┴──────┐
            │             │
         ✅ PASS       ❌ FAIL
            │             │
            ▼             ▼
     Commit succeeds   Commit blocked
                      (fix issues first)
```

**For AI Agents**: Ensures no improperly formatted code enters the repository.

## Common Linting Issues AI Agents Face

### 1. Unused Imports

```python
# ❌ Agent imports library but forgets to use it
from datetime import datetime  # Unused

def get_timestamp():
    return time.time()  # Uses time, not datetime

# Linter: F401 `datetime` imported but unused
```

**Fix**: Remove unused import or use it.

### 2. Missing Type Annotations

```python
# ❌ Agent forgets type hints
def calculate_total(items):
    return sum(item.price for item in items)

# Linter: ANN001 Missing type annotation for `items`
# Linter: ANN201 Missing return type annotation
```

**Fix**: Add type hints.

```python
# ✅ Fixed
def calculate_total(items: list[Item]) -> float:
    return sum(item.price for item in items)
```

### 3. Security Vulnerabilities

```python
# ❌ Agent hardcodes sensitive data
API_KEY = "sk-1234567890abcdef"

# Linter: S105 Possible hardcoded password
```

**Fix**: Use environment variables.

```python
# ✅ Fixed
API_KEY = os.getenv("API_KEY")
```

### 4. React Hooks Dependency Issues

```typescript
// ❌ Agent creates useEffect with missing dependency
useEffect(() => {
  fetchUserData(userId);
}, []);  // Missing userId in dependency array

// Linter: react-hooks/exhaustive-deps
//   React Hook useEffect has a missing dependency: 'userId'
```

**Fix**: Add missing dependency.

```typescript
// ✅ Fixed
useEffect(() => {
  fetchUserData(userId);
}, [userId]);
```

## Linting in CI/CD Pipeline

Our GitHub Actions automatically run linting on every commit:

```yaml
# .github/workflows/backend.yml
- name: Run backend linting
  run: |
    cd backend
    uv run ruff check .
    uv run ruff format . --check

# .github/workflows/frontend.yml
- name: Run frontend linting
  run: |
    cd frontend
    npm run lint
    npm run format
```

**Result**: Every commit is validated. If linting fails, the commit is marked as failing.

**For AI Agents**: Continuous validation on every push.

## Security Linting Rules

Linting is a **critical first line of defense** against security vulnerabilities. This repository uses Ruff's security rules (`S` prefix, from flake8-bandit) to catch common security anti-patterns before code ever runs.

### Why Security Linting Matters for AI Agents

AI agents can inadvertently generate insecure code because they:
- May not recognize security anti-patterns in generated code
- Could use dangerous functions without understanding the risks
- Might hardcode sensitive data in code
- Could create SQL injection vulnerabilities through string concatenation

**Security linters catch these issues instantly** during the validation phase.

### Enabled Security Rules (Ruff S-Prefix)

Our configuration enables comprehensive security checking:

```toml
# backend/pyproject.toml

[tool.ruff.lint]
select = [
    "S",      # flake8-bandit (security)
    # ... other rules
]

ignore = [
    "S311",   # Standard random is fine for non-crypto use
]
```

### Common Security Rules and Examples

#### S101: Assert Used Outside Tests

```python
# ❌ FAIL: Using assert for validation
def process_payment(amount):
    assert amount > 0, "Amount must be positive"
    # In production, assertions can be disabled with -O flag
    charge_card(amount)

# ✅ PASS: Use explicit validation
def process_payment(amount: float) -> None:
    if amount <= 0:
        raise ValueError("Amount must be positive")
    charge_card(amount)
```

**Ruff catches**: `S101 [*] Use of assert detected`

**Why**: Assertions can be disabled in optimized Python (`python -O`), making validation disappear in production.

#### S102, S103, S104, S105, S106, S107: Dangerous Function Calls

```python
# ❌ FAIL: Using exec() with user input
user_code = request.json.get("code")
exec(user_code)  # S102: Arbitrary code execution

# ❌ FAIL: Using eval() with user input
result = eval(user_input)  # S307: Arbitrary code execution

# ❌ FAIL: Hardcoded passwords
PASSWORD = "admin123"  # S105: Hardcoded password

# ❌ FAIL: Hardcoded SQL password
DB_URL = "postgresql://user:password@localhost/db"  # S105

# ✅ PASS: Use environment variables
import os
PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_URL = os.getenv("DATABASE_URL")
```

**Ruff catches**:
- `S102: Use of exec detected`
- `S307: Use of possibly insecure function eval`
- `S105: Possible hardcoded password`

**Why**: These patterns create critical security vulnerabilities.

#### S108: Insecure Temp File Creation

```python
# ❌ FAIL: Insecure temp file
import tempfile
tmp = tempfile.mktemp()  # S108: Insecure, race condition
with open(tmp, 'w') as f:
    f.write(secret_data)

# ✅ PASS: Secure temp file
import tempfile
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write(secret_data)
    tmp = f.name
```

**Ruff catches**: `S108: Probable insecure usage of temp file/directory`

**Why**: `mktemp()` has race conditions. Attacker can predict filename and read/modify it.

#### S113: Request Without Timeout

```python
# ❌ FAIL: No timeout on HTTP request
import requests
response = requests.get("https://api.example.com/data")  # S113

# ✅ PASS: Always use timeout
import requests
response = requests.get(
    "https://api.example.com/data",
    timeout=30  # Prevents hanging forever
)
```

**Ruff catches**: `S113: Probable use of requests call without timeout`

**Why**: Without timeout, request can hang indefinitely, enabling denial of service.

#### S501, S506: SQL Injection Vulnerabilities

```python
# ❌ FAIL: SQL injection via string formatting
user_input = request.args.get("email")
query = f"SELECT * FROM users WHERE email = '{user_input}'"  # S608
cursor.execute(query)

# ❌ FAIL: SQL injection via concatenation
query = "SELECT * FROM users WHERE id = " + str(user_id)  # S608
cursor.execute(query)

# ✅ PASS: Use parameterized queries (SQLAlchemy)
from sqlalchemy import select, text
from app.models import User

# With ORM (best)
stmt = select(User).where(User.email == user_input)
result = await session.execute(stmt)

# With raw SQL (parameterized)
stmt = text("SELECT * FROM users WHERE email = :email")
result = await session.execute(stmt, {"email": user_input})
```

**Ruff catches**: `S608: Possible SQL injection vector through string-based query construction`

**Why**: String formatting/concatenation allows SQL injection attacks.

#### S603, S604, S605, S606, S607: Shell Injection

```python
# ❌ FAIL: Shell injection via os.system
import os
filename = request.args.get("file")
os.system(f"cat {filename}")  # S605: Shell injection

# ❌ FAIL: Shell injection via subprocess
import subprocess
subprocess.call(f"ls {user_dir}", shell=True)  # S602: Shell injection

# ✅ PASS: Use subprocess without shell=True
import subprocess
subprocess.run(
    ["ls", user_dir],  # List, not string - prevents injection
    shell=False,  # Explicit
    check=True
)

# ✅ BETTER: Use pathlib for file operations
from pathlib import Path
files = list(Path(user_dir).iterdir())
```

**Ruff catches**:
- `S605: Starting a process with a shell`
- `S602: subprocess call with shell=True`

**Why**: Shell=True enables command injection via shell metacharacters.

#### S324: Insecure Hash Functions

```python
# ❌ FAIL: Using MD5 for passwords
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()  # S324

# ❌ FAIL: Using SHA1 for passwords
password_hash = hashlib.sha1(password.encode()).hexdigest()  # S324

# ✅ PASS: Use bcrypt/argon2/scrypt for passwords
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# ✅ PASS: Or use passlib
from passlib.hash import argon2
password_hash = argon2.hash(password)
```

**Ruff catches**: `S324: Use of insecure MD5 hash function`

**Why**: MD5 and SHA1 are cryptographically broken and unsuitable for passwords.

#### S501: Request With verify=False

```python
# ❌ FAIL: Disabling SSL verification
import requests
response = requests.get(
    "https://api.example.com",
    verify=False  # S501: Insecure!
)

# ✅ PASS: Keep SSL verification enabled
import requests
response = requests.get(
    "https://api.example.com",
    # verify=True is the default
    timeout=30
)
```

**Ruff catches**: `S501: Probable use of requests call with verify=False disabling SSL certificate checks`

**Why**: Disabling SSL verification enables man-in-the-middle attacks.

### Frontend Security Linting (ESLint)

ESLint doesn't have as many built-in security rules, but we can configure security-focused plugins:

#### Dangerous Eval Usage

```typescript
// ❌ FAIL: Using eval
const userCode = getUserInput();
eval(userCode);  // ESLint: no-eval

// ✅ PASS: Don't execute arbitrary code
// If you need dynamic behavior, use a safe parser or whitelist
```

#### Dangerous innerHTML

```typescript
// ❌ FAIL: XSS via innerHTML
const userComment = getUserComment();
element.innerHTML = userComment;  // React: dangerouslySetInnerHTML warning

// ✅ PASS: Use text content or sanitize
element.textContent = userComment;  // Safe - escapes HTML

// ✅ PASS: Or use a sanitization library
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userComment);
```

### Configured Security Rules

Our backend configuration:

```toml
# backend/pyproject.toml

[tool.ruff.lint]
select = [
    "S",      # flake8-bandit (security)
    "DTZ",    # flake8-datetimez (timezone-aware datetimes)
    # ... other rules
]

ignore = [
    "S311",   # Standard random is fine for non-crypto use
              # (e.g., generating test IDs, sampling data)
              # For cryptographic randomness, use secrets module
]
```

**Note on S311**: We allow `random.random()` for non-security purposes:

```python
# ✅ OK: Using random for test data
import random
test_id = f"test-{random.randint(1000, 9999)}"

# ❌ NOT OK: Using random for security
import random
session_token = str(random.randint(100000, 999999))  # Predictable!

# ✅ CORRECT: Use secrets for security
import secrets
session_token = secrets.token_urlsafe(32)
```

### Running Security Linting

```bash
# Run all Ruff checks (includes security)
uv run ruff check .

# Run only security checks (S-prefix)
uv run ruff check . --select S

# Show what security rules would catch
uv run ruff check . --select S --diff

# Fix auto-fixable security issues
uv run ruff check . --select S --fix
```

### Security Linting in CI/CD

Add security-specific checks to CI:

```yaml
# .github/workflows/backend.yml

- name: Run security linting
  run: |
    cd backend
    uv run ruff check . --select S --no-fix
    # Fail build if security issues found
```

### Real-World Example: Security Linting Catches Vulnerability

**Before linting**:
```python
# backend/app/auth/service.py

import hashlib
from fastapi import HTTPException

def create_user(email: str, password: str):
    # ❌ Multiple security issues
    password_hash = hashlib.md5(password.encode()).hexdigest()  # S324

    # ❌ SQL injection risk
    query = f"INSERT INTO users (email, password) VALUES ('{email}', '{password_hash}')"  # S608
    db.execute(query)
```

**Run security linting**:
```bash
$ uv run ruff check app/auth/service.py --select S

app/auth/service.py:6:20: S324 Use of insecure MD5 hash function for security purposes
app/auth/service.py:9:13: S608 Possible SQL injection vector through string-based query construction

Found 2 errors.
```

**After fixing**:
```python
# backend/app/auth/service.py

import bcrypt
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

async def create_user(
    session: AsyncSession,
    email: str,
    password: str
) -> User:
    # ✅ Secure password hashing
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # ✅ Parameterized query (ORM)
    user = User(email=email, password_hash=password_hash)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
```

**Run linting again**:
```bash
$ uv run ruff check app/auth/service.py --select S
All checks passed!
```

**For AI Agents**: Security linter caught critical vulnerabilities (weak hashing + SQL injection) that would have been exploitable in production.

### Security Linting Best Practices

#### ✅ DO:

1. **Enable all security rules** - Start with full S-prefix coverage
2. **Run security checks in CI** - Block merges if security issues found
3. **Fix security issues immediately** - Don't ignore or disable rules
4. **Use secure alternatives** - bcrypt not MD5, parameterized queries not string concat
5. **Document exceptions** - If you disable a rule, explain why
6. **Review ignored rules** - Periodically audit `ignore` list
7. **Combine with security tests** - Linting + tests = defense in depth

#### ❌ DON'T:

1. **Disable security rules globally** - Only ignore specific instances with justification
2. **Ignore security warnings** - They indicate real vulnerabilities
3. **Use `# noqa` without comment** - Always explain why a rule is suppressed
4. **Trust frameworks completely** - Verify security features with linting
5. **Skip security linting in CI** - Make it a required check
6. **Use insecure defaults** - Always opt for secure patterns

### Security Linting Coverage

Ruff's S-prefix rules catch:

| Category | Rules | What They Catch |
|----------|-------|-----------------|
| **Code Injection** | S102, S307, S602, S605 | exec(), eval(), shell injection |
| **Hardcoded Secrets** | S105, S106, S107 | Passwords, tokens, keys in code |
| **Crypto Issues** | S324, S501 | Weak hashing, disabled SSL |
| **SQL Injection** | S608 | String-based query construction |
| **File Security** | S108 | Insecure temp files |
| **HTTP Security** | S113, S501 | Missing timeouts, disabled SSL |
| **Random Numbers** | S311 | Non-crypto random for security |
| **Assertions** | S101 | Assertions for critical checks |

**For AI Agents**: Security linting provides **immediate feedback** on security anti-patterns, preventing vulnerabilities before code ever runs.

## Best Practices for AI-Friendly Linting

### ✅ DO:

1. **Run linter after every code change** - Immediate feedback
2. **Use auto-fix aggressively** - Let tools fix most issues
3. **Fix all warnings** - Don't ignore linter output
4. **Configure strict rules** - More rules = better code quality
5. **Integrate with CI/CD** - Enforce linting on every commit

### ❌ DON'T:

1. **Disable linter rules without reason** - Each rule catches real issues
2. **Ignore linter warnings** - Warnings become errors later
3. **Skip formatting** - Inconsistent code is hard to read
4. **Manually format code** - Let tools handle it
5. **Commit un-linted code** - Use pre-commit hooks

## Summary: Linting as Quality Assurance for AI

Linting and formatting are the **second-most critical guardrail** (after tests) because they:

1. **Enforce consistency** - All generated code follows the same patterns
2. **Catch subtle bugs** - Unused variables, missing imports, logical errors
3. **Prevent security issues** - Hardcoded secrets, SQL injection, dangerous patterns
4. **Enable auto-fix** - Agent can fix most issues without human intervention
5. **Provide clear errors** - Actionable messages guide fixes
6. **Speed up validation** - Linting is fast (milliseconds)

### The Linting Contract for AI Agents:

```
┌─────────────────────────────────────────────────────────┐
│       AI AGENT PROMISE (Enforced by Linters)            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  "I will ensure all generated code:                    │
│                                                         │
│   ✅ Has no linting errors                             │
│   ✅ Follows consistent formatting                     │
│   ✅ Has no unused imports or variables                │
│   ✅ Has complete type annotations                     │
│   ✅ Has no security vulnerabilities                   │
│   ✅ Uses modern syntax patterns                       │
│   ✅ Has organized, sorted imports                     │
│                                                         │
│  If ANY linting issue is found, I will:                │
│                                                         │
│   1. Read the error message                            │
│   2. Run auto-fix (ruff check --fix)                   │
│   3. Manually fix remaining issues                     │
│   4. Re-run linter until clean                         │
│   5. Never commit un-linted code                       │
│                                                         │
│  I will NEVER disable linter rules to make errors go   │
│  away."                                                │
└─────────────────────────────────────────────────────────┘
```

This contract ensures **professional, consistent, bug-free code** generated at machine speed.

## Next Steps

1. Read [type-checks.md](./type-checks.md) to understand type safety validation
2. Explore `backend/pyproject.toml` for full Ruff configuration
3. Explore `frontend/.eslintrc.cjs` for full ESLint configuration
4. Run `uv run ruff check .` in `backend/` to see linting in action
5. Run `npm run lint` in `frontend/` to see ESLint in action

Remember: **Linting is automated code review**. It catches issues that would otherwise require human reviewers, enabling faster, autonomous development.
