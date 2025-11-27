# Guardrail 3: Type Checks (Safety Validation)

## What is Type Checking?

**Type checking** is the process of verifying that your code uses variables, functions, and data structures in ways consistent with their declared types.

Think of types as **contracts**: "This function accepts a string and returns a number." Type checkers ensure both sides honor the contract.

### Example: The Problem Type Checking Solves

```python
# Without type checking:
def calculate_discount(price, discount_percent):
    return price * (1 - discount_percent / 100)

# What happens?
result = calculate_discount("$50.00", "10%")  # Runtime ERROR!
# TypeError: can't multiply sequence by non-int
```

**Problem**: You passed strings instead of numbers, but Python doesn't catch this until the code runs and crashes.

```python
# With type checking:
def calculate_discount(price: float, discount_percent: float) -> float:
    return price * (1 - discount_percent / 100)

# Type checker catches this BEFORE running:
result = calculate_discount("$50.00", "10%")
# Error: Argument type "str" is not assignable to parameter type "float"
```

**Solution**: Type checker catches the mistake during development, not in production.

## Why Type Checking Matters for Traditional Development

In human-led development, type checking provides:

1. **Early error detection** - Catch bugs at development time, not runtime
2. **Better IDE support** - Autocomplete, refactoring, inline documentation
3. **Self-documenting code** - Types show what functions expect and return
4. **Safer refactoring** - Change code with confidence
5. **Team communication** - Types are a shared language about data structures

### Development Lifecycle Without Types:

```
Write code → Run code → Crash with TypeError →
Debug to find issue → Fix → Run again → Crash elsewhere → Repeat...
```

### Development Lifecycle With Types:

```
Write code → Type checker finds errors → Fix → Type checker passes →
Run code → Works correctly (type errors already caught)
```

## Why Type Checking is CRITICAL for AI Agents (PIV Loop)

For AI agents, type checking serves as the **most important compile-time guardrail**.

### The Fundamental Problem:

**AI agents reason about code statically** (by reading text), not dynamically (by running it). They need **explicit contracts** to generate correct code.

```
Human Developer:
"I know from experience that user.email is a string."
(Relies on implicit knowledge, documentation, codebase familiarity)

AI Agent:
"What is the type of user.email?"
(Needs explicit type declarations to reason correctly)
```

Without type annotations, an AI agent must **guess** what types to use. With types, it has **guarantees**.

### How Type Checking Enables the PIV Loop

In the **Plan-Implement-Validate** loop, type checking is part of **validation**:

```
┌─────────────────────────────────────────────────────────┐
│ PLAN: Add endpoint to update user email                │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ IMPLEMENT: AI generates code                           │
│  def update_email(user_id, new_email):                 │
│      user = get_user(user_id)                          │
│      user.email = new_email                            │
│      save_user(user)                                   │
│      return user                                       │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ VALIDATE: Run type checker (mypy app/)                 │
│  ❌ Error: Missing type annotation for `user_id`       │
│  ❌ Error: Missing type annotation for `new_email`     │
│  ❌ Error: Missing return type annotation             │
│  ❌ Error: Cannot determine type of `user`            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ├─── ❌ FAILURES ───────────────────────┐
                   │                                       │
                   │   Agent reads errors and adds types:  │
                   │                                       │
                   └───► BACK TO IMPLEMENT                 │
                         (Add type annotations)            │
                                                           │
                   ┌───────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ IMPLEMENT: AI adds type annotations                    │
│  def update_email(                                     │
│      user_id: int,                                     │
│      new_email: str                                    │
│  ) -> User:                                            │
│      user = get_user(user_id)                          │
│      user.email = new_email                            │
│      save_user(user)                                   │
│      return user                                       │
└──────────────────┬──────────────────────────────────────┘
                   ▼
┌─────────────────────────────────────────────────────────┐
│ VALIDATE: Run type checker (mypy app/)                 │
│  ✅ Success: no issues found                           │
└──────────────────┬──────────────────────────────────────┘
                   ▼
              ✅ ALL PASS → NEXT TASK
```

**Key Insight**: Type errors provide **precise guidance** on what to fix.

### What Type Checking Tells the AI Agent:

1. **What types to use** - Function signatures, variable types
2. **What's compatible** - Can I pass this value to that function?
3. **What methods exist** - What can I call on this object?
4. **What can be None** - Handle null safely
5. **What's the return value** - What does this function produce?

## Common Type Errors and How Type Checkers Catch Them

### 1. None/Null Access Errors

```python
# ❌ Runtime error (crashes in production)
def get_user_email(user_id: int):
    user = find_user(user_id)  # Returns User | None
    return user.email  # CRASH if user is None!

# Type checker catches this:
# Error: Item "None" has no attribute "email"
```

```python
# ✅ Type-safe version
def get_user_email(user_id: int) -> str | None:
    user = find_user(user_id)  # Returns User | None
    if user is None:
        return None
    return user.email  # Type checker knows user is not None here
```

**For AI Agents**: Prevents generating code that crashes on null values.

### 2. Wrong Argument Types

```python
# ❌ Type error
def calculate_tax(price: float, rate: float) -> float:
    return price * rate

result = calculate_tax("100", "0.08")  # Strings!
# Error: Argument type "str" is not assignable to parameter type "float"
```

**For AI Agents**: Ensures correct types are passed to functions.

### 3. Missing Return Values

```python
# ❌ Type error
def get_username(user_id: int) -> str:
    user = find_user(user_id)
    if user:
        return user.name
    # Missing return! Type checker catches this.
# Error: Function is missing return statement
```

```python
# ✅ Type-safe version
def get_username(user_id: int) -> str | None:
    user = find_user(user_id)
    if user:
        return user.name
    return None  # Explicit return
```

**For AI Agents**: Ensures all code paths return a value.

### 4. Attribute Errors

```python
# ❌ Type error
class User:
    name: str
    email: str

def print_user(user: User) -> None:
    print(user.username)  # Typo! Should be `name`
# Error: "User" has no attribute "username"
```

**For AI Agents**: Catches typos and wrong attribute access.

### 5. Incompatible Types

```python
# ❌ Type error
def process_ids(ids: list[int]) -> None:
    for id in ids:
        print(id)

process_ids(["a", "b", "c"])  # List of strings!
# Error: List[str] is not assignable to List[int]
```

**For AI Agents**: Ensures data structures match expectations.

## Backend Type Checking: MyPy + Pyright

This repository uses **two type checkers** for maximum safety:

1. **MyPy** - Pragmatic, lenient with third-party libraries
2. **Pyright** - Strict, catches edge cases MyPy misses

Think of it as **two quality inspectors** reviewing the same code from different angles.

### Why Two Type Checkers?

```
┌─────────────────────────────────────────────────────────┐
│                      DUAL LAYER                         │
│                                                         │
│  MyPy (First Pass)           Pyright (Second Pass)     │
│  ├─ Pragmatic                ├─ Strictest              │
│  ├─ Development-friendly     ├─ Production gate        │
│  ├─ Fast feedback            ├─ Catches edge cases     │
│  └─ 95% coverage             └─ 100% coverage          │
│                                                         │
│         If BOTH pass → Code is type-safe               │
└─────────────────────────────────────────────────────────┘
```

**For AI Agents**: Two layers of validation = fewer bugs slip through.

### MyPy: Primary Type Checker

**MyPy** is the most popular Python type checker, developed by Dropbox.

**Configuration** (`backend/pyproject.toml`):

```toml
[tool.mypy]
python_version = "3.12"
strict = true
show_error_codes = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = false  # FastAPI decorators aren't typed
```

**Strict Mode Enabled**:
- All functions must have type annotations
- No untyped function calls
- No implicit `Any` types
- Warns about unreachable code

**Running MyPy**:

```bash
# From backend/ directory
uv run mypy app/

# Output when passing:
Success: no issues found in 29 source files

# Output with errors:
app/auth/service.py:45: error: Missing return statement  [return]
app/models.py:12: error: Argument 1 has incompatible type "str"; expected "int"  [arg-type]
Found 2 errors in 2 files (checked 29 source files)
```

### Pyright: Secondary Type Checker

**Pyright** is Microsoft's type checker, written in TypeScript. It's **faster** and **stricter** than MyPy.

**Configuration** (`backend/pyproject.toml`):

```toml
[tool.pyright]
include = ["app"]
pythonVersion = "3.12"
typeCheckingMode = "strict"
reportUnusedFunction = "none"  # Pytest fixtures appear unused
```

**What Pyright Catches That MyPy Doesn't**:

1. **Variance checking** - Stricter subtyping rules
2. **Protocol compliance** - Structural typing validation
3. **Type narrowing** - More precise flow analysis
4. **Generic constraints** - Stricter generic type enforcement

**Running Pyright**:

```bash
# From backend/ directory
uv run pyright app/

# Output when passing:
0 errors, 0 warnings, 0 informations

# Output with errors:
app/core/middleware.py:45:5 - error: Argument type is partially unknown
app/models.py:12:9 - error: "dict[str, Any]" is not assignable to "MutableMapping[str, Any]"
2 errors, 0 warnings, 0 informations
```

### Example: Type Checking in Action

**Before type checking**:
```python
# backend/app/auth/service.py

def authenticate_user(email, password):
    user = get_user_by_email(email)
    if user and verify_password(password, user.password_hash):
        return user
    return None

def get_user_by_email(email):
    return db.query(User).filter_by(email=email).first()
```

**Run MyPy**:
```bash
$ uv run mypy app/

app/auth/service.py:3: error: Missing type annotation for function argument 'email'
app/auth/service.py:3: error: Missing type annotation for function argument 'password'
app/auth/service.py:3: error: Missing return type annotation for public function
app/auth/service.py:8: error: Missing type annotation for function argument 'email'
app/auth/service.py:8: error: Missing return type annotation for public function
Found 5 errors in 1 file (checked 29 source files)
```

**After adding types**:
```python
# backend/app/auth/service.py

from typing import Optional
from app.models import User

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

def get_user_by_email(email: str) -> User | None:
    """Find user by email address.

    Args:
        email: Email address to search for

    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter_by(email=email).first()
```

**Run MyPy again**:
```bash
$ uv run mypy app/
Success: no issues found in 29 source files
```

**Run Pyright**:
```bash
$ uv run pyright app/
0 errors, 0 warnings, 0 informations
```

✅ **Both type checkers pass!**

**For AI Agents**: Clear path from errors to correct, type-safe code.

## Frontend Type Checking: TypeScript Strict Mode

### What is TypeScript?

**TypeScript** is a typed superset of JavaScript. It adds type annotations and compile-time type checking to JavaScript.

**Key Features**:
- **Gradual typing** - Add types incrementally
- **Type inference** - Automatically infers many types
- **Rich IDE support** - Autocomplete, refactoring, inline errors
- **Compiles to JavaScript** - Works everywhere JavaScript does

### Our TypeScript Configuration

Location: `frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "strict": true,                      // Enable all strict checks
    "noUnusedLocals": true,              // Error on unused variables
    "noUnusedParameters": true,          // Error on unused parameters
    "noImplicitReturns": true,           // Error if function missing return
    "forceConsistentCasingInFileNames": true,  // Prevent case-sensitive import errors
  }
}
```

**Strict Mode Enabled**:
- `noImplicitAny` - No variables without explicit type
- `strictNullChecks` - `null` and `undefined` are distinct types
- `strictFunctionTypes` - Strict function parameter checking
- `strictPropertyInitialization` - Class properties must be initialized

### Running TypeScript Type Checks

```bash
# From frontend/ directory

# Check types
npm run typecheck

# Output when passing:
$ npm run typecheck
✓ 0 errors found

# Output with errors:
$ npm run typecheck
src/features/auth/components/LoginForm.tsx:12:5 - error TS2322:
  Type 'string | undefined' is not assignable to type 'string'.
    Type 'undefined' is not assignable to type 'string'.

Found 1 error in 1 file.
```

### Example: TypeScript in Action

**Before type checking**:
```typescript
// frontend/src/features/users/api.ts

export async function fetchUser(userId) {
  const response = await fetch(`/api/users/${userId}`);
  const data = await response.json();
  return data;
}

export function getUserEmail(user) {
  return user.email;
}
```

**TypeScript errors**:
```
src/features/users/api.ts:3:33 - error TS7006:
  Parameter 'userId' implicitly has an 'any' type.

src/features/users/api.ts:9:30 - error TS7006:
  Parameter 'user' implicitly has an 'any' type.
```

**After adding types**:
```typescript
// frontend/src/features/users/api.ts
// frontend/src/features/users/types.ts

export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

export async function fetchUser(userId: number): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.statusText}`);
  }
  const data: User = await response.json();
  return data;
}

export function getUserEmail(user: User): string {
  return user.email;
}
```

**TypeScript passes**:
```bash
$ npm run typecheck
✓ 0 errors found
```

**For AI Agents**: Clear interface definitions guide correct code generation.

### React Component Type Safety

```typescript
// ❌ Without types
export function UserCard({ user, onDelete }) {
  return (
    <div>
      <h3>{user.name}</h3>
      <button onClick={() => onDelete(user.id)}>Delete</button>
    </div>
  );
}

// TypeScript errors:
// - Binding element 'user' implicitly has an 'any' type
// - Binding element 'onDelete' implicitly has an 'any' type
```

```typescript
// ✅ With types
import type { User } from './types';

interface UserCardProps {
  user: User;
  onDelete: (userId: number) => void;
}

export function UserCard({ user, onDelete }: UserCardProps) {
  return (
    <div>
      <h3>{user.name}</h3>
      <button onClick={() => onDelete(user.id)}>Delete</button>
    </div>
  );
}

// TypeScript passes:
// ✓ Props are typed
// ✓ IDE knows `user` has `name` and `id`
// ✓ `onDelete` expects a number
```

**For AI Agents**: Type-safe React components with clear contracts.

## Type Checking in CI/CD Pipeline

Our GitHub Actions run all type checkers automatically:

```yaml
# .github/workflows/backend.yml
- name: Run MyPy
  run: |
    cd backend
    uv run mypy app/

- name: Run Pyright
  run: |
    cd backend
    uv run pyright app/

# .github/workflows/frontend.yml
- name: Run TypeScript type check
  run: |
    cd frontend
    npm run typecheck
```

**Result**: Every commit is type-checked. If types fail, the commit is marked as failing.

**For AI Agents**: Continuous type validation on every change.

## Best Practices for AI-Friendly Type Checking

### ✅ DO:

1. **Annotate all function signatures** - Parameters and return types
2. **Use specific types** - `list[User]` not `list[Any]`
3. **Handle None explicitly** - Use `| None` and check for None
4. **Define interfaces/types** - For complex data structures
5. **Use type aliases** - For reusable type definitions
6. **Enable strict mode** - Catch more errors early
7. **Run type checkers frequently** - Before every commit

### ❌ DON'T:

1. **Use `Any` everywhere** - Defeats the purpose of type checking
2. **Ignore type errors** - Fix them or understand why
3. **Skip return types** - Always annotate what function returns
4. **Use `# type: ignore`** - Only as last resort with explanation
5. **Mix typed and untyped code** - Be consistent
6. **Assume type inference** - Be explicit in public APIs

## Common Type Patterns

### Optional Values

```python
# Python (MyPy/Pyright)
def find_user(user_id: int) -> User | None:
    user = db.get(User, user_id)
    return user  # May be None

# TypeScript
function findUser(userId: number): User | null {
  const user = db.get(userId);
  return user;  // May be null
}
```

### Generic Types

```python
# Python
from typing import Generic, TypeVar

T = TypeVar("T")

class Response(Generic[T]):
    data: T
    status: int

# Usage
user_response: Response[User] = Response(data=user, status=200)
```

```typescript
// TypeScript
interface Response<T> {
  data: T;
  status: number;
}

// Usage
const userResponse: Response<User> = { data: user, status: 200 };
```

### Union Types

```python
# Python
def process_id(id: int | str) -> None:
    if isinstance(id, int):
        # Type checker knows id is int here
        print(f"Integer ID: {id}")
    else:
        # Type checker knows id is str here
        print(f"String ID: {id.upper()}")
```

```typescript
// TypeScript
function processId(id: number | string): void {
  if (typeof id === 'number') {
    // Type checker knows id is number here
    console.log(`Integer ID: ${id}`);
  } else {
    // Type checker knows id is string here
    console.log(`String ID: ${id.toUpperCase()}`);
  }
}
```

## Type Safety for Security

Type checking is a **powerful security tool** that prevents entire classes of vulnerabilities by enforcing type contracts at compile time. When combined with proper design, types can make certain security vulnerabilities **impossible** rather than just unlikely.

### Why Type Safety Matters for Security

Type systems prevent security vulnerabilities by:

1. **Preventing injection attacks** - Typed query builders prevent SQL injection
2. **Enforcing input validation** - Types ensure validation happens
3. **Protecting sensitive data** - Types prevent accidental exposure
4. **Ensuring authentication** - Types enforce auth checks
5. **Validating authorization** - Types check permissions at compile time

### SQL Injection Prevention Through Types

#### ❌ Unsafe: String-Based Queries

```python
# Type checker can't help here - it's just a string
def get_user_by_email(email: str) -> User | None:
    query = f"SELECT * FROM users WHERE email = '{email}'"  # SQL injection!
    return db.execute(query)

# Type checker says: ✓ Types are correct
# Security scanner says: ✗ SQL injection vulnerability
```

#### ✅ Safe: Typed Query Builder

```python
from sqlalchemy import select
from app.models import User

def get_user_by_email(email: str) -> User | None:
    # Type-safe: select() returns SelectStatement[User]
    # Email is automatically parameterized
    stmt = select(User).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()

# Type checker says: ✓ Types are correct
# Security scanner says: ✓ Uses parameterized queries
```

**How types help**:
- `select()` returns a typed `SelectStatement`, not a raw string
- `.where()` takes typed columns and values
- No way to inject SQL - the API doesn't allow it

#### Advanced: Preventing Raw SQL

```python
from typing import NewType
from sqlalchemy import select

# Create a type that can only be constructed safely
SafeQuery = NewType('SafeQuery', str)

def execute_query(query: SafeQuery) -> list[dict]:
    """Execute only pre-approved queries."""
    return db.execute(str(query))

def make_safe_query(table: str, column: str, value: str) -> SafeQuery:
    """Construct query with validation."""
    # Validate table and column names (whitelist)
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table}")
    if column not in ALLOWED_COLUMNS[table]:
        raise ValueError(f"Invalid column: {column}")

    # Use parameterized query
    query = f"SELECT * FROM {table} WHERE {column} = :value"
    return SafeQuery(query)

# ✅ Must use make_safe_query - can't pass raw strings
query = make_safe_query("users", "email", "test@example.com")
execute_query(query)

# ❌ Type error - can't pass string directly
execute_query("SELECT * FROM users")  # Type error!
```

### XSS Prevention Through Types

#### ❌ Unsafe: Accepting Raw HTML

```python
# Backend
def create_comment(content: str) -> Comment:
    # What if content contains <script> tags?
    return Comment(content=content)
```

```typescript
// Frontend
function CommentDisplay({ comment }: { comment: Comment }) {
  // Dangerous! XSS vulnerability
  return <div dangerouslySetInnerHTML={{ __html: comment.content }} />;
}
```

#### ✅ Safe: Typed Sanitization

```python
# Backend - Use NewType for sanitized content
from typing import NewType

SanitizedHTML = NewType('SanitizedHTML', str)
PlainText = NewType('PlainText', str)

def sanitize_html(raw: str) -> SanitizedHTML:
    """Sanitize HTML to prevent XSS."""
    import bleach
    clean = bleach.clean(
        raw,
        tags=['p', 'br', 'strong', 'em'],  # Whitelist
        strip=True
    )
    return SanitizedHTML(clean)

def create_comment(content: str) -> Comment:
    # Must sanitize before storing
    sanitized = sanitize_html(content)
    return Comment(content=sanitized)
```

```typescript
// Frontend - Typed content types
type SanitizedHTML = string & { readonly __brand: unique symbol };
type PlainText = string & { readonly __brand: unique symbol };

function sanitizeHTML(raw: string): SanitizedHTML {
  // Use DOMPurify
  return DOMPurify.sanitize(raw) as SanitizedHTML;
}

interface Comment {
  id: number;
  content: SanitizedHTML;  // Type enforces sanitization
}

function CommentDisplay({ comment }: { comment: Comment }) {
  // TypeScript ensures content is already sanitized
  return <div dangerouslySetInnerHTML={{ __html: comment.content }} />;
}
```

**How types help**:
- Can't create `SanitizedHTML` except through `sanitize_html()`
- Type system ensures all HTML is sanitized before use
- Compiler error if you try to use raw string as HTML

### Authentication Enforcement Through Types

#### ❌ Unsafe: Optional User

```python
def get_current_user() -> User | None:
    """Get user from session - might be None."""
    return session.get("user")

def transfer_money(amount: float) -> None:
    user = get_current_user()
    # Forgot to check if user is None!
    process_transfer(user.id, amount)  # Crash or security issue
```

#### ✅ Safe: Required User

```python
from typing import Annotated
from fastapi import Depends, HTTPException

def get_authenticated_user() -> User:
    """Get authenticated user or raise 401."""
    user = session.get("user")
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user  # Type: User (not User | None)

@app.post("/transfer")
async def transfer_money(
    amount: float,
    user: Annotated[User, Depends(get_authenticated_user)]
):
    # Type guarantees user exists and is authenticated
    process_transfer(user.id, amount)  # Always safe
```

**How types help**:
- `get_authenticated_user()` returns `User`, not `User | None`
- Type system ensures authentication check happened
- Can't forget to check - type error if you try

### Authorization Enforcement Through Types

#### ❌ Unsafe: Runtime Permission Checks

```python
def delete_user(user_id: int, requesting_user: User) -> None:
    # Easy to forget permission check
    db.delete(User, user_id)
```

#### ✅ Safe: Type-Level Permissions

```python
from typing import NewType, TypeVar

# Create permission types
AdminUser = NewType('AdminUser', User)
OwnerUser = NewType('OwnerUser', User)

def require_admin(user: User) -> AdminUser:
    """Verify user is admin, return typed as AdminUser."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return AdminUser(user)

def delete_user(user_id: int, admin: AdminUser) -> None:
    # Type guarantees admin check happened
    db.delete(User, user_id)

# Usage
@app.delete("/users/{user_id}")
async def delete_user_endpoint(
    user_id: int,
    user: Annotated[User, Depends(get_authenticated_user)]
):
    admin = require_admin(user)  # Explicit permission check
    delete_user(user_id, admin)   # Type-safe

    # ❌ Type error if you try to skip check
    # delete_user(user_id, user)  # Error: User != AdminUser
```

**How types help**:
- `AdminUser` type proves permission was checked
- Can't call admin functions without being `AdminUser` type
- Compiler enforces authorization logic

### Sensitive Data Protection Through Types

#### ❌ Unsafe: Exposing Sensitive Fields

```python
@dataclass
class User:
    id: int
    email: str
    password_hash: str  # Sensitive!

def get_user(user_id: int) -> User:
    return db.get(User, user_id)

@app.get("/users/{user_id}")
async def get_user_endpoint(user_id: int) -> User:
    # Accidentally exposes password_hash in API response!
    return get_user(user_id)
```

#### ✅ Safe: Separate Public and Internal Types

```python
@dataclass
class UserInternal:
    """Internal user representation with sensitive data."""
    id: int
    email: str
    password_hash: str  # Only for internal use

@dataclass
class UserPublic:
    """Public user representation without sensitive data."""
    id: int
    email: str
    # No password_hash!

def get_user_internal(user_id: int) -> UserInternal:
    """Get full user data (internal use only)."""
    return db.get(UserInternal, user_id)

def to_public(user: UserInternal) -> UserPublic:
    """Convert to public representation."""
    return UserPublic(id=user.id, email=user.email)

@app.get("/users/{user_id}")
async def get_user_endpoint(user_id: int) -> UserPublic:
    # Type system ensures we return public type only
    user_internal = get_user_internal(user_id)
    return to_public(user_internal)  # Safe - no sensitive data
```

**How types help**:
- `UserPublic` type can't contain `password_hash`
- API endpoints must return `UserPublic`, not `UserInternal`
- Impossible to accidentally expose sensitive data

### Password Type Safety

```python
from typing import NewType

# Never pass passwords as plain strings
PlainPassword = NewType('PlainPassword', str)
HashedPassword = NewType('HashedPassword', bytes)

def hash_password(password: PlainPassword) -> HashedPassword:
    """Hash password using bcrypt."""
    import bcrypt
    return HashedPassword(bcrypt.hashpw(password.encode(), bcrypt.gensalt()))

def verify_password(password: PlainPassword, hash: HashedPassword) -> bool:
    """Verify password against hash."""
    import bcrypt
    return bcrypt.checkpw(password.encode(), hash)

def create_user(email: str, password: PlainPassword) -> User:
    # Type ensures password is hashed
    password_hash = hash_password(password)
    return User(email=email, password_hash=password_hash)

# ❌ Type error - can't pass string directly
create_user("test@example.com", "password123")  # Error!

# ✅ Must explicitly mark as password
create_user("test@example.com", PlainPassword("password123"))
```

### Frontend: Type-Safe API Responses

```typescript
// Define exact response types
interface UserPublic {
  id: number;
  email: string;
  // password_hash explicitly NOT included
}

interface UserPrivate {
  id: number;
  email: string;
  phone: string;
  // Still no password_hash
}

// API client returns typed responses
async function fetchUser(userId: number): Promise<UserPublic> {
  const response = await apiClient.get(`/users/${userId}`);
  return response.data;  // TypeScript validates structure
}

// Using the data
function UserProfile({ userId }: { userId: number }) {
  const { data: user } = useQuery(['user', userId], () => fetchUser(userId));

  // TypeScript knows user is UserPublic
  return (
    <div>
      <h2>{user.email}</h2>
      {/* TypeScript error - password_hash doesn't exist on UserPublic */}
      {/* <p>{user.password_hash}</p> */}
    </div>
  );
}
```

### Type-Safe Input Validation

```python
from pydantic import BaseModel, EmailStr, field_validator, Field

class UserCreate(BaseModel):
    """Type-safe user creation with validation."""
    email: EmailStr  # Validates email format
    password: str = Field(min_length=8, max_length=100)
    age: int = Field(ge=13, le=120)  # Age between 13 and 120

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

# Type checker ensures validation
@app.post("/users")
async def create_user(user_data: UserCreate) -> UserPublic:
    # Type system guarantees:
    # - email is valid format
    # - password is 8-100 chars with uppercase and digit
    # - age is 13-120
    # All validated automatically by Pydantic
    return create_user_internal(user_data)
```

### Security Through Type Constraints

```python
from typing import Literal, Annotated
from pydantic import Field

# Constrained types prevent invalid values
UserRole = Literal["user", "admin", "moderator"]  # Only these values allowed

class User(BaseModel):
    id: int
    role: UserRole  # Type error if assigned anything else

# Constrained integers
PositiveInt = Annotated[int, Field(gt=0)]
Port = Annotated[int, Field(ge=1, le=65535)]

def process_payment(amount: PositiveInt) -> None:
    # Type guarantees amount > 0
    charge_card(amount)

def start_server(port: Port) -> None:
    # Type guarantees valid port number
    bind(port)
```

### Type Safety Best Practices for Security

#### ✅ DO:

1. **Use NewType for sensitive data** - `PlainPassword`, `SanitizedHTML`, `AdminUser`
2. **Separate public and internal types** - `UserPublic` vs `UserInternal`
3. **Use typed query builders** - SQLAlchemy, not raw SQL strings
4. **Enforce authentication with types** - Return `User`, not `User | None`
5. **Use Pydantic for validation** - Types + validation in one
6. **Use Literal types for enums** - Prevent invalid values
7. **Type API responses explicitly** - No `Any` in response types

#### ❌ DON'T:

1. **Use strings for sensitive data** - Use `NewType` wrappers
2. **Return sensitive data in public types** - Separate types
3. **Skip type annotations for security functions** - Always type
4. **Use `Any` for user input** - Use Pydantic models
5. **Ignore type errors in security code** - Fix them
6. **Mix authenticated and unauthenticated types** - Make distinction clear

### Summary

Type safety is a **compile-time security layer** that:

1. **Prevents injection** - Typed query builders prevent SQL/shell injection
2. **Enforces validation** - Types ensure input is validated
3. **Protects data** - Separate types for public/private data
4. **Requires authentication** - Types enforce auth checks
5. **Validates authorization** - Permission types at compile time

**For AI Agents**: Type-safe security patterns make vulnerabilities **impossible**, not just unlikely. When an agent generates code with proper types, entire classes of security bugs cannot exist.

## Summary: Type Checking as Compile-Time Safety Net

Type checking is the **most important compile-time guardrail** because it:

1. **Catches bugs before runtime** - No crashes in production from type errors
2. **Enables IDE support** - Autocomplete, refactoring, inline documentation
3. **Documents code automatically** - Types show contracts clearly
4. **Guides AI code generation** - Explicit contracts enable correct generation
5. **Enables refactoring** - Change code with confidence
6. **Prevents entire bug classes** - Null pointer errors, wrong types, missing returns

### The Type Checking Contract for AI Agents:

```
┌─────────────────────────────────────────────────────────┐
│     AI AGENT PROMISE (Enforced by Type Checkers)        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  "I will ensure all generated code:                    │
│                                                         │
│   ✅ Has complete type annotations                     │
│   ✅ Uses correct types for all parameters             │
│   ✅ Returns correct types from all functions          │
│   ✅ Handles None/null explicitly                      │
│   ✅ Uses type-safe data structures                    │
│   ✅ Passes MyPy strict mode                           │
│   ✅ Passes Pyright strict mode (backend)              │
│   ✅ Passes TypeScript strict mode (frontend)          │
│                                                         │
│  If ANY type error is found, I will:                   │
│                                                         │
│   1. Read the error message                            │
│   2. Identify the type mismatch                        │
│   3. Add or fix type annotations                       │
│   4. Re-run type checkers                              │
│   5. Repeat until all checkers pass                    │
│                                                         │
│  I will NEVER use `Any` or `# type: ignore` to make    │
│  errors disappear without understanding them."         │
└─────────────────────────────────────────────────────────┘
```

This contract ensures **type-safe, reliable code** generated at machine speed.

## Next Steps

1. Read [logging.md](./logging.md) to understand structured logging for AI agents
2. Read [architecture.md](./architecture.md) to understand code organization
3. Explore `backend/docs/mypy-standard.md` for complete MyPy documentation
4. Explore `backend/docs/pyright-standard.md` for complete Pyright documentation
5. Run `uv run mypy app/` and `uv run pyright app/` in `backend/` to see type checking in action
6. Run `npm run typecheck` in `frontend/` to see TypeScript type checking

Remember: **Type checking is the foundation of reliability**. It catches entire classes of bugs before code ever runs, enabling AI agents to generate production-ready code autonomously.
