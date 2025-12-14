# Guardrail 5: Architecture (Clear Structure)

## What is Software Architecture?

**Software architecture** is the high-level organization of your codebase - how you structure files, folders, modules, and the relationships between them.

Think of architecture as the **blueprint for a building**. Just like a building needs a clear plan showing where rooms go and how they connect, software needs a clear plan showing where code goes and how it connects.

### Example: Why Architecture Matters

```
❌ BAD ARCHITECTURE (Everything in one folder):

app/
├── users.py             # User models, routes, business logic all mixed
├── products.py          # Product models, routes, business logic all mixed
├── orders.py            # Order models, routes, business logic all mixed
├── utils.py             # Random utility functions
├── helpers.py           # More random functions
└── main.py              # Everything else

Problems:
- Hard to find code ("where is user validation?")
- Changes affect multiple places
- Can't work on features independently
- Testing is difficult
- New developers are confused
```

```
✅ GOOD ARCHITECTURE (Vertical Slices):

app/
├── users/
│   ├── models.py        # User database models
│   ├── schemas.py       # User request/response types
│   ├── routes.py        # User endpoints
│   ├── service.py       # User business logic
│   └── tests/           # User tests
├── products/
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   ├── service.py
│   └── tests/
└── orders/
    ├── models.py
    ├── schemas.py
    ├── routes.py
    ├── service.py
    └── tests/

Benefits:
- Easy to find code (everything for users is in users/)
- Changes are isolated (users/ doesn't affect products/)
- Can work on features independently
- Testing is straightforward
- New developers understand quickly
```

## Traditional Architecture Patterns

### Layered Architecture (Traditional)

```
app/
├── models/              # All database models
│   ├── user.py
│   ├── product.py
│   └── order.py
├── controllers/         # All route handlers
│   ├── user_controller.py
│   ├── product_controller.py
│   └── order_controller.py
├── services/            # All business logic
│   ├── user_service.py
│   ├── product_service.py
│   └── order_service.py
└── repositories/        # All database access
    ├── user_repository.py
    ├── product_repository.py
    └── order_repository.py
```

**Organization**: By technical layer (all models together, all controllers together)

**Problems**:
1. **Feature changes span many folders** - To add a user feature, you edit 4 different folders
2. **Hard to delete features** - Files scattered across the codebase
3. **Difficult to understand** - Can't see full feature in one place
4. **Testing is complex** - Tests scattered across multiple locations

### Why Layered Architecture Fails for AI Agents

```
Task: "Add user profile picture upload"

Human Developer:
1. Opens models/user.py (adds picture_url field)
2. Opens services/user_service.py (adds upload logic)
3. Opens controllers/user_controller.py (adds endpoint)
4. Opens repositories/user_repository.py (adds query)
5. Keeps mental model of changes across 4 folders

AI Agent:
1. Reads task
2. Must search across 4 different folders
3. Must remember which files to modify
4. Easy to miss a file or create inconsistency
5. Hard to validate completeness
```

**Problem**: Too much cognitive overhead for AI agents to track changes across scattered files.

## Vertical Slice Architecture (Our Choice)

### What is a Vertical Slice?

A **vertical slice** is a self-contained feature that includes ALL code needed for that feature - from database to API to UI - in one place.

```
Feature: User Management

users/                    # Everything for users
├── models.py             # Database: User table
├── schemas.py            # API: Request/response types
├── routes.py             # API: Endpoints (POST /users, GET /users/{id})
├── service.py            # Business logic: Registration, authentication
└── tests/                # Tests: All user tests
    ├── test_models.py
    ├── test_routes.py
    └── test_service.py
```

**Organization**: By feature (all code for one feature together)

**Benefits**:
1. **Feature changes stay in one folder** - To add user feature, edit only users/
2. **Easy to delete features** - Just delete the folder
3. **Easy to understand** - See complete feature in one place
4. **Testing is simple** - All tests in feature folder
5. **AI-friendly** - Clear, predictable structure

### Backend Structure (FastAPI + Python)

```
backend/app/
├── core/                          # Shared infrastructure
│   ├── config.py                  # Settings (database URL, etc.)
│   ├── database.py                # Database connection
│   ├── logging.py                 # Structured logging setup
│   ├── middleware.py              # Request logging middleware
│   ├── exceptions.py              # Global exception handlers
│   ├── health.py                  # Health check endpoints
│   └── tests/                     # Infrastructure tests
│       ├── test_config.py
│       ├── test_database.py
│       └── test_logging.py
├── shared/                        # Cross-feature utilities
│   ├── models.py                  # TimestampMixin (used by 3+ features)
│   ├── schemas.py                 # PaginationParams (used by 3+ features)
│   ├── utils.py                   # utcnow() (used by 3+ features)
│   └── tests/
│       ├── test_models.py
│       └── test_schemas.py
└── features/                      # Feature slices (examples)
    ├── users/                     # User management feature
    │   ├── models.py              # User model
    │   ├── schemas.py             # UserCreate, UserResponse
    │   ├── routes.py              # POST /users, GET /users/{id}
    │   ├── service.py             # register(), authenticate()
    │   └── tests/
    │       ├── test_models.py
    │       ├── test_routes.py
    │       └── test_service.py
    ├── products/                  # Product management feature
    │   ├── models.py              # Product model
    │   ├── schemas.py             # ProductCreate, ProductResponse
    │   ├── routes.py              # CRUD endpoints for products
    │   ├── service.py             # Business logic
    │   └── tests/
    └── orders/                    # Order processing feature
        ├── models.py              # Order, OrderItem models
        ├── schemas.py             # OrderCreate, OrderResponse
        ├── routes.py              # Order endpoints
        ├── service.py             # Order processing logic
        └── tests/
```

### Frontend Structure (React + TypeScript)

```
frontend/src/
├── app/                           # Application setup
│   ├── App.tsx                    # Root component
│   ├── router.tsx                 # Route definitions
│   ├── providers/                 # Context providers
│   │   ├── QueryProvider.tsx     # React Query setup
│   │   └── ThemeProvider.tsx     # Theme setup
│   └── routes/                    # Page components
│       ├── HomePage.tsx
│       ├── HomePage.test.tsx
│       └── NotFoundPage.tsx
├── shared/                        # Cross-feature utilities
│   ├── components/                # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── ErrorBoundary.tsx
│   │   └── ErrorBoundary.test.tsx
│   ├── lib/                       # Utilities
│   │   ├── api.ts                 # API client wrapper
│   │   ├── queryClient.ts         # React Query config
│   │   └── utils.ts               # Helper functions
│   └── types/                     # Shared types
│       └── common.ts
└── features/                      # Feature slices
    ├── health/                    # Health check feature
    │   ├── api.ts                 # fetchHealth()
    │   ├── types.ts               # HealthData interface
    │   ├── hooks.ts               # useHealth()
    │   └── components/
    │       ├── HealthCard.tsx
    │       └── HealthCard.test.tsx
    ├── users/                     # User management feature
    │   ├── api.ts                 # fetchUsers(), createUser()
    │   ├── types.ts               # User, UserCreate types
    │   ├── hooks.ts               # useUsers(), useCreateUser()
    │   └── components/
    │       ├── UserList.tsx
    │       ├── UserList.test.tsx
    │       ├── UserForm.tsx
    │       └── UserForm.test.tsx
    └── products/                  # Product management feature
        ├── api.ts
        ├── types.ts
        ├── hooks.ts
        └── components/
            ├── ProductCard.tsx
            └── ProductCard.test.tsx
```

## The Rule: When to Share Code

**Rule**: Code moves to `shared/` ONLY when used by **3 or more features**.

### Examples

**❌ DON'T share prematurely**:
```python
# Only used by users/ feature
users/utils.py          # Keep here, don't move to shared/

# Only used by products/ feature
products/helpers.py     # Keep here, don't move to shared/
```

**✅ DO share when reused**:
```python
# Used by users/, products/, and orders/
shared/utils.py         # Move to shared/
    - utcnow()          # All features need current time
    - generate_id()     # All features need IDs

# Used by users/, products/, and orders/
shared/models.py        # Move to shared/
    - TimestampMixin    # All models need created_at/updated_at
```

**Why this rule?**:
1. **Avoid premature abstraction** - Don't share until you have 3 examples
2. **Keep features independent** - Features shouldn't depend on each other
3. **Easy to refactor** - Easy to move code to shared/ when needed

## Feature Slice Pattern

Each feature follows the same structure:

### Backend Feature Structure

```
feature_name/
├── models.py          # Database models (SQLAlchemy)
├── schemas.py         # API schemas (Pydantic)
├── routes.py          # API endpoints (FastAPI)
├── service.py         # Business logic
└── tests/             # Feature tests
    ├── test_models.py
    ├── test_routes.py
    └── test_service.py
```

**File purposes**:

**models.py** - Database tables
```python
from sqlalchemy import String, Integer
from app.core.database import Base
from app.shared.models import TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
```

**schemas.py** - Request/response types
```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    """Request: Create new user"""
    email: EmailStr
    name: str

class UserResponse(BaseModel):
    """Response: User data"""
    id: int
    email: str
    name: str
    created_at: str
```

**routes.py** - API endpoints
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    return await create_user_service(db, user_data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> User:
    return await get_user_service(db, user_id)
```

**service.py** - Business logic
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger

logger = get_logger(__name__)

async def create_user_service(
    db: AsyncSession,
    user_data: UserCreate,
) -> User:
    """Create a new user."""
    logger.info("user.create_started", email=user_data.email)

    user = User(**user_data.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info("user.create_completed",
               email=user.email,
               user_id=user.id)

    return user
```

### Frontend Feature Structure

```
feature_name/
├── api.ts             # API calls
├── types.ts           # TypeScript interfaces
├── hooks.ts           # React Query hooks
└── components/        # UI components
    ├── Component.tsx
    └── Component.test.tsx
```

**File purposes**:

**types.ts** - TypeScript interfaces
```typescript
export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

export interface UserCreate {
  email: string;
  name: string;
}
```

**api.ts** - API calls
```typescript
import { apiClient } from '@/shared/lib/api';
import type { User, UserCreate } from './types';

export async function fetchUsers(): Promise<User[]> {
  const response = await apiClient.get('/users');
  return response.data;
}

export async function createUser(data: UserCreate): Promise<User> {
  const response = await apiClient.post('/users', data);
  return response.data;
}
```

**hooks.ts** - React Query hooks
```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { fetchUsers, createUser } from './api';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });
}

export function useCreateUser() {
  return useMutation({
    mutationFn: createUser,
  });
}
```

**components/UserList.tsx** - UI component
```typescript
import { useUsers } from '../hooks';

export function UserList() {
  const { data: users, isLoading } = useUsers();

  if (isLoading) return <div>Loading...</div>;

  return (
    <ul>
      {users?.map((user) => (
        <li key={user.id}>{user.name} ({user.email})</li>
      ))}
    </ul>
  );
}
```

## Why Vertical Slices Enable AI Agents

### 1. Predictable Structure

**Human**: "Where do I add user registration?"

**AI Agent**: "Check the pattern. Registration is a user feature, so:"
- Backend: `app/users/service.py` - add `register()` function
- Backend: `app/users/routes.py` - add `POST /users/register` endpoint
- Backend: `app/users/schemas.py` - add `UserRegister` schema
- Frontend: `src/features/users/api.ts` - add `registerUser()` function
- Frontend: `src/features/users/hooks.ts` - add `useRegister()` hook
- Frontend: `src/features/users/components/RegisterForm.tsx` - add UI

**No guesswork. Pattern is clear.**

### 2. Isolated Changes

```
Task: "Add product ratings feature"

Layered Architecture:
- Edit models/product.py (add rating field)
- Edit controllers/product_controller.py (add rating endpoint)
- Edit services/product_service.py (add rating logic)
- Edit repositories/product_repository.py (add rating query)
- Hope you didn't miss anything...

Vertical Slice:
- Create products/rating.py (all rating logic)
- Edit products/models.py (add rating field)
- Edit products/routes.py (add rating endpoint)
- Edit products/schemas.py (add rating types)
- All changes in products/ folder ✅
```

**AI Agent can focus on ONE folder**.

### 3. Easy to Validate Completeness

```
Task: "Add order cancellation"

Checklist for AI agent:
✅ Does orders/models.py have cancellation status?
✅ Does orders/schemas.py have CancelOrder schema?
✅ Does orders/routes.py have POST /orders/{id}/cancel?
✅ Does orders/service.py have cancel_order() function?
✅ Does orders/tests/ have test_cancel_order()?

If ANY is missing, feature is incomplete.
```

**Clear definition of "done"**.

### 4. Independent Testing

```python
# Test just the users feature
pytest app/users/tests/

# Test just the products feature
pytest app/products/tests/

# Test everything
pytest
```

**AI agent can validate one feature at a time**.

### 5. Easy to Delete

```
Task: "Remove the products feature"

Layered Architecture:
- Delete models/product.py
- Delete controllers/product_controller.py
- Delete services/product_service.py
- Delete repositories/product_repository.py
- Delete tests for products... where are they?
- Check for imports... in 50 files
- Hope nothing breaks

Vertical Slice:
- Delete products/ folder
- Check for imports in other features
- Done ✅
```

**Clean removal without scattered references**.

## Real-World Example: Adding a Feature

**Task**: "Add a comments feature where users can comment on products"

### Step 1: Create Feature Structure

```bash
# Backend
mkdir app/comments
touch app/comments/models.py
touch app/comments/schemas.py
touch app/comments/routes.py
touch app/comments/service.py
mkdir app/comments/tests

# Frontend
mkdir src/features/comments
touch src/features/comments/api.ts
touch src/features/comments/types.ts
touch src/features/comments/hooks.ts
mkdir src/features/comments/components
```

### Step 2: Implement Backend

**app/comments/models.py**:
```python
from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.shared.models import TimestampMixin

class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    user: Mapped["User"] = relationship()
    product: Mapped["Product"] = relationship()
```

**app/comments/schemas.py**:
```python
from pydantic import BaseModel

class CommentCreate(BaseModel):
    text: str
    product_id: int

class CommentResponse(BaseModel):
    id: int
    text: str
    user_id: int
    product_id: int
    created_at: str
```

**app/comments/routes.py**:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .schemas import CommentCreate, CommentResponse
from .service import create_comment, get_product_comments

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("", response_model=CommentResponse)
async def add_comment(
    comment_data: CommentCreate,
    user_id: int,  # From auth
    db: AsyncSession = Depends(get_db),
):
    return await create_comment(db, comment_data, user_id)

@router.get("/product/{product_id}", response_model=list[CommentResponse])
async def list_product_comments(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_product_comments(db, product_id)
```

**app/comments/service.py**:
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from .models import Comment
from .schemas import CommentCreate

logger = get_logger(__name__)

async def create_comment(
    db: AsyncSession,
    comment_data: CommentCreate,
    user_id: int,
) -> Comment:
    logger.info("comment.create_started",
               user_id=user_id,
               product_id=comment_data.product_id)

    comment = Comment(
        **comment_data.model_dump(),
        user_id=user_id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    logger.info("comment.create_completed",
               comment_id=comment.id,
               user_id=user_id)

    return comment

async def get_product_comments(
    db: AsyncSession,
    product_id: int,
) -> list[Comment]:
    result = await db.execute(
        select(Comment).where(Comment.product_id == product_id)
    )
    return list(result.scalars().all())
```

### Step 3: Implement Frontend

**src/features/comments/types.ts**:
```typescript
export interface Comment {
  id: number;
  text: string;
  user_id: number;
  product_id: number;
  created_at: string;
}

export interface CommentCreate {
  text: string;
  product_id: number;
}
```

**src/features/comments/api.ts**:
```typescript
import { apiClient } from '@/shared/lib/api';
import type { Comment, CommentCreate } from './types';

export async function createComment(data: CommentCreate): Promise<Comment> {
  const response = await apiClient.post('/comments', data);
  return response.data;
}

export async function fetchProductComments(productId: number): Promise<Comment[]> {
  const response = await apiClient.get(`/comments/product/${productId}`);
  return response.data;
}
```

**src/features/comments/hooks.ts**:
```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { createComment, fetchProductComments } from './api';

export function useProductComments(productId: number) {
  return useQuery({
    queryKey: ['comments', 'product', productId],
    queryFn: () => fetchProductComments(productId),
  });
}

export function useCreateComment() {
  return useMutation({
    mutationFn: createComment,
  });
}
```

**src/features/comments/components/CommentList.tsx**:
```typescript
import { useProductComments } from '../hooks';

interface CommentListProps {
  productId: number;
}

export function CommentList({ productId }: CommentListProps) {
  const { data: comments, isLoading } = useProductComments(productId);

  if (isLoading) return <div>Loading comments...</div>;

  return (
    <div>
      {comments?.map((comment) => (
        <div key={comment.id}>
          <p>{comment.text}</p>
          <small>{comment.created_at}</small>
        </div>
      ))}
    </div>
  );
}
```

### Step 4: Register Feature

**app/main.py** (backend):
```python
from app.comments.routes import router as comments_router

app.include_router(comments_router)
```

**Done!** Complete feature in vertical slices.

## Best Practices for AI-Friendly Architecture

### ✅ DO:

1. **Follow the pattern** - Every feature has the same structure
2. **Keep features independent** - Don't import from other features
3. **Share only when needed** - Move to shared/ after 3 uses
4. **Name consistently** - users/, products/, orders/ (plural nouns)
5. **Test within features** - All tests in feature/tests/
6. **Document deviations** - If you break the pattern, explain why

### ❌ DON'T:

1. **Cross-import features** - users/ shouldn't import from products/
2. **Share prematurely** - Don't move to shared/ until 3 features need it
3. **Mix concerns** - Keep database, API, and UI separate
4. **Skip tests** - Every feature needs tests
5. **Create deep nesting** - Max 2-3 levels deep

## Security Through Isolation

### How Vertical Slices Enhance Security

Vertical slice architecture doesn't just improve code organization - it creates **natural security boundaries** that limit attack surface and blast radius.

**Traditional layered architecture security problem**:
```
Security breach in any layer affects ENTIRE application

models/                    # All models in one place
├── user.py                # User credentials
├── product.py             # Product data
├── payment.py             # Payment data
└── admin.py               # Admin functions

If payment.py is compromised → attacker has access to:
- User credentials (same folder)
- Admin functions (same folder)
- All business logic (all in services/)
- All database access (all in repositories/)

Blast radius: ENTIRE APPLICATION ❌
```

**Vertical slice architecture security advantage**:
```
Security breach limited to SINGLE FEATURE

features/
├── users/                 # User feature isolated
│   ├── models.py          # Only user data
│   ├── service.py         # Only user logic
│   └── tests/             # User security tests
├── payments/              # Payment feature isolated
│   ├── models.py          # Only payment data
│   ├── service.py         # Only payment logic
│   └── tests/             # Payment security tests
└── admin/                 # Admin feature isolated
    ├── models.py          # Only admin data
    ├── service.py         # Only admin logic
    └── tests/             # Admin security tests

If payments/ is compromised → attacker only has access to:
- Payment data (within payments/ folder)
- Payment logic (within payments/ folder)

Blast radius: SINGLE FEATURE ✅
```

### Security Principle: Defense in Depth Through Layers

Vertical slices create **multiple layers of security** within each feature:

```
1. Network Layer (CORS, Rate Limiting)
         ↓
2. Authentication Layer (auth/ feature)
         ↓
3. Authorization Layer (per-feature permissions)
         ↓
4. Input Validation Layer (Pydantic schemas)
         ↓
5. Business Logic Layer (service.py)
         ↓
6. Database Layer (parameterized queries)
         ↓
7. Audit Layer (security logging)
```

**Example: Payment Processing Feature**
```python
# app/payments/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.logging import get_logger
from app.shared.security import require_auth, require_ownership, sanitize_input
from .schemas import PaymentCreate, PaymentResponse
from .service import create_payment

router = APIRouter(prefix="/payments", tags=["payments"])
logger = get_logger(__name__)

@router.post("", response_model=PaymentResponse)
async def submit_payment(
    payment_data: PaymentCreate,            # Layer 4: Input validation
    user_id: int = Depends(require_auth),   # Layer 3: Authentication
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a payment (protected endpoint).

    Security layers:
    - Authentication: Must be logged in
    - Ownership: Can only pay for own orders
    - Input validation: Amount, card number format
    - SQL injection prevention: Parameterized queries
    - Logging: All payment attempts logged
    """
    # Layer 3: Authorization (ownership check)
    logger.info("payment.create_started",
                user_id=user_id,
                amount=payment_data.amount)

    # Layer 5: Business logic with security checks
    try:
        payment = await create_payment(db, payment_data, user_id)

        # Layer 7: Audit logging
        logger.info("audit.payment_submitted",
                   payment_id=payment.id,
                   user_id=user_id,
                   amount=payment.amount)

        return payment

    except Exception as e:
        # Layer 7: Security event logging
        logger.error("payment.create_failed",
                    user_id=user_id,
                    error=str(e),
                    exc_info=True)
        raise
```

### Feature-Level Permission Boundaries

**Pattern**: Each feature defines its own permissions and access rules.

```python
# app/users/permissions.py
from typing import Literal

UserPermission = Literal["read", "update", "delete"]

def can_update_user(current_user_id: int, target_user_id: int) -> bool:
    """Users can only update their own profile."""
    return current_user_id == target_user_id

def can_delete_user(current_user_id: int, target_user_id: int, is_admin: bool) -> bool:
    """Only admins or the user themselves can delete."""
    return is_admin or current_user_id == target_user_id

# app/users/routes.py
@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Feature-level authorization check
    if not can_update_user(current_user.id, user_id):
        logger.warning("authorization.access_denied",
                      current_user_id=current_user.id,
                      target_user_id=user_id,
                      action="update_user")
        raise HTTPException(status_code=403, detail="Cannot update other users")

    return await update_user_service(db, user_id, updates)
```

**Benefits**:
- **Feature autonomy** - Each feature owns its security rules
- **Easy to audit** - All permissions in feature/permissions.py
- **Easy to test** - Permission tests in feature/tests/test_permissions.py
- **No cross-feature permission leaks** - users/ can't accidentally grant products/ permissions

### Shared Security Utilities Pattern

**Rule**: Security utilities move to `shared/security.py` when used by **3+ features**.

```python
# app/shared/security.py
from typing import NewType
import bleach
from passlib.context import CryptContext

# Type-safe security primitives
SanitizedHTML = NewType('SanitizedHTML', str)
HashedPassword = NewType('HashedPassword', str)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def sanitize_html(raw: str) -> SanitizedHTML:
    """
    Sanitize HTML to prevent XSS attacks.

    Used by: users/, comments/, posts/
    """
    clean = bleach.clean(
        raw,
        tags=['p', 'br', 'strong', 'em', 'ul', 'ol', 'li'],
        strip=True
    )
    return SanitizedHTML(clean)

def hash_password(plain_password: str) -> HashedPassword:
    """
    Hash password with bcrypt.

    Used by: users/, admin/, auth/
    """
    hashed = pwd_context.hash(plain_password)
    return HashedPassword(hashed)

def verify_password(plain_password: str, hashed: HashedPassword) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, str(hashed))

class RateLimiter:
    """
    Rate limiting for brute force prevention.

    Used by: auth/, api/, webhooks/
    """
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        # Implementation...
```

**Why shared**:
- Security utilities are used by 3+ features (auth/, users/, admin/)
- Critical to have single implementation (no duplication)
- Easier to audit and update in one place
- Type safety enforced across all features

### Isolating Sensitive Features

**Pattern**: Sensitive features (auth, payments, admin) get extra isolation layers.

#### Example: Authentication Feature Isolation

```
app/auth/                        # Completely isolated feature
├── models.py                    # Token, Session models (sensitive)
├── schemas.py                   # LoginRequest, TokenResponse
├── routes.py                    # POST /auth/login, /auth/logout
├── service.py                   # Authentication logic
├── permissions.py               # Auth-specific permissions
├── rate_limiting.py             # Auth-specific rate limiting
├── tests/
│   ├── test_login.py            # Login tests
│   ├── test_rate_limiting.py   # Brute force prevention tests
│   ├── test_token_expiry.py    # Token security tests
│   └── test_security.py         # SQL injection, XSS tests
└── README.md                    # Security documentation

Features that depend on auth:
- Import ONLY public functions (get_current_user, require_auth)
- NEVER import internal auth logic
- NEVER access auth database models directly
```

**Security through controlled exports**:
```python
# app/auth/__init__.py
"""
Authentication feature - controlled public API.

Only these functions should be imported by other features.
All internal auth logic is private to this feature.
"""

# Public API (safe to import)
from .service import get_current_user, require_auth, require_admin

# Everything else is PRIVATE
# Other features should NEVER import:
# - auth.models (Token, Session) ❌
# - auth.service internal functions ❌
# - auth.rate_limiting internals ❌

__all__ = [
    "get_current_user",
    "require_auth",
    "require_admin",
]
```

**Usage in other features**:
```python
# app/users/routes.py
from app.auth import require_auth  # ✅ Safe - public API
from app.auth.models import Token  # ❌ FORBIDDEN - internal model

@router.get("/profile")
async def get_profile(
    user_id: int = Depends(require_auth),  # ✅ Using public API
):
    # Feature isolated - auth logic stays in auth/
    return await get_user(user_id)
```

### Security Testing Within Features

**Pattern**: Each feature contains its own security tests.

```python
# app/auth/tests/test_security.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.security
def test_login_prevents_sql_injection(client: TestClient):
    """Test that login is immune to SQL injection."""
    payloads = [
        "admin' OR '1'='1",
        "'; DROP TABLE users; --",
        "admin' --",
    ]

    for payload in payloads:
        response = client.post("/auth/login", json={
            "email": payload,
            "password": "test123"
        })

        # Should return 401 (not found), not 500 (SQL error)
        assert response.status_code == 401

        # Should not leak database information
        error = response.json().get("detail", "")
        assert "SQL" not in error.upper()
        assert "SELECT" not in error.upper()

@pytest.mark.security
def test_login_rate_limiting(client: TestClient):
    """Test that excessive login attempts are blocked."""
    for _ in range(5):
        client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrong"
        })

    # 6th attempt should be rate limited
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrong"
    })

    assert response.status_code == 429  # Too Many Requests
    assert "rate limit" in response.json()["detail"].lower()

@pytest.mark.security
def test_token_expiry(client: TestClient):
    """Test that expired tokens are rejected."""
    # Create expired token
    expired_token = create_test_token(expires_in_seconds=-3600)

    response = client.get("/auth/verify", headers={
        "Authorization": f"Bearer {expired_token}"
    })

    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()
```

**Benefits**:
- Security tests live with the feature they protect
- Run `pytest app/auth/tests/test_security.py -m security` to audit one feature
- AI agents can add security tests when creating features
- Clear what security properties each feature guarantees

### Example: Complete Secure Feature

**Task**: "Create a secure products feature with authentication and authorization"

```python
# app/products/models.py
from sqlalchemy import Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.shared.models import TimestampMixin

class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(1000))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

# app/products/schemas.py
from pydantic import BaseModel, field_validator

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float

    @field_validator('price')
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Price cannot be negative")
        if v > 1_000_000:
            raise ValueError("Price exceeds maximum allowed")
        return v

    @field_validator('name', 'description')
    @classmethod
    def validate_no_html(cls, v: str) -> str:
        # Prevent HTML/script injection
        if '<' in v or '>' in v or 'script' in v.lower():
            raise ValueError("HTML tags not allowed")
        return v

# app/products/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.logging import get_logger
from app.auth import require_auth
from .schemas import ProductCreate, ProductResponse
from .service import create_product, get_product, update_product, delete_product

router = APIRouter(prefix="/products", tags=["products"])
logger = get_logger(__name__)

@router.post("", response_model=ProductResponse)
async def create_product_endpoint(
    product_data: ProductCreate,
    user_id: int = Depends(require_auth),  # Authentication
    db: AsyncSession = Depends(get_db),
):
    """Create product (authenticated users only)."""
    logger.info("product.create_started", user_id=user_id)

    product = await create_product(db, product_data, owner_id=user_id)

    logger.info("product.create_completed",
               product_id=product.id,
               user_id=user_id)

    return product

@router.delete("/{product_id}")
async def delete_product_endpoint(
    product_id: int,
    user_id: int = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete product (owner only)."""
    # Authorization check
    product = await get_product(db, product_id)

    if product.owner_id != user_id:
        logger.warning("authorization.access_denied",
                      user_id=user_id,
                      product_id=product_id,
                      action="delete")
        raise HTTPException(status_code=403, detail="Not the product owner")

    await delete_product(db, product_id)

    logger.info("audit.product_deleted",
               product_id=product_id,
               user_id=user_id)

    return {"message": "Product deleted"}

# app/products/tests/test_security.py
@pytest.mark.security
def test_cannot_delete_others_products(client: TestClient, auth_token: str):
    """Test that users cannot delete products they don't own."""
    # User 1 creates product
    response = client.post("/products",
                          json={"name": "Test", "price": 10.0},
                          headers={"Authorization": f"Bearer {auth_token}"})
    product_id = response.json()["id"]

    # User 2 tries to delete (different token)
    other_token = create_test_token(user_id=999)
    response = client.delete(f"/products/{product_id}",
                            headers={"Authorization": f"Bearer {other_token}"})

    assert response.status_code == 403
    assert "not the product owner" in response.json()["detail"].lower()

@pytest.mark.security
def test_product_price_validation(client: TestClient, auth_token: str):
    """Test that negative prices are rejected."""
    response = client.post("/products",
                          json={"name": "Test", "price": -10.0},
                          headers={"Authorization": f"Bearer {auth_token}"})

    assert response.status_code == 422
    assert "price cannot be negative" in str(response.json()).lower()
```

### Security Benefits of Vertical Slices

| Security Concern | How Vertical Slices Help |
|-----------------|--------------------------|
| **Blast Radius** | Compromise limited to single feature folder |
| **Attack Surface** | Each feature exposes only its own endpoints |
| **Permission Leaks** | Features cannot accidentally grant each other's permissions |
| **Audit Trails** | All security logs for a feature in one place |
| **Security Testing** | Security tests isolated per feature |
| **Code Review** | Review security of one feature at a time |
| **Vulnerability Patching** | Fix affects only one feature |
| **Compliance** | Easier to prove isolation for SOC 2, ISO 27001 |

### The Security Contract for Architecture

```
┌─────────────────────────────────────────────────────────┐
│           SECURITY THROUGH ISOLATION                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  "When organizing code, I will:                        │
│                                                         │
│   ✅ Isolate sensitive features (auth/, payments/)     │
│   ✅ Limit feature exports to safe public APIs         │
│   ✅ Keep permissions within feature boundaries        │
│   ✅ Test security within each feature                 │
│   ✅ Share security utilities only after 3 uses        │
│   ✅ Log all security events within feature            │
│   ✅ Never leak internal models/logic to other features│
│                                                         │
│  Security guarantees per feature:                      │
│                                                         │
│   - Authentication enforced at route level             │
│   - Authorization checked in business logic            │
│   - Input validation via Pydantic schemas              │
│   - SQL injection prevented by parameterized queries   │
│   - XSS prevented by input sanitization                │
│   - Audit logs for all sensitive operations            │
│   - Security tests covering common vulnerabilities     │
│                                                         │
│  Blast radius if compromised: SINGLE FEATURE ONLY"     │
└─────────────────────────────────────────────────────────┘
```

## Summary: Architecture as Cognitive Scaffolding for AI

Architecture is the **fifth and final guardrail** because it:

1. **Provides predictability** - AI knows where code goes
2. **Enables isolation** - Changes stay in one folder
3. **Simplifies validation** - Clear definition of "complete"
4. **Enables testing** - Each feature tests independently
5. **Supports deletion** - Easy to remove features
6. **Reduces cognitive load** - AI focuses on one folder at a time

### The Architecture Contract for AI Agents:

```
┌─────────────────────────────────────────────────────────┐
│    AI AGENT PROMISE (Enforced by Architecture)          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  "When implementing features, I will:                  │
│                                                         │
│   ✅ Follow the vertical slice pattern                 │
│   ✅ Put all feature code in one folder                │
│   ✅ Create models, schemas, routes, service, tests    │
│   ✅ Keep features independent (no cross-imports)      │
│   ✅ Only move to shared/ after 3 uses                 │
│   ✅ Follow naming conventions (plural nouns)          │
│   ✅ Register feature in main.py                       │
│                                                         │
│  For each feature, I will create:                      │
│                                                         │
│   Backend:                                             │
│   - feature/models.py (database)                       │
│   - feature/schemas.py (API types)                     │
│   - feature/routes.py (endpoints)                      │
│   - feature/service.py (logic)                         │
│   - feature/tests/ (tests)                             │
│                                                         │
│   Frontend:                                            │
│   - feature/types.ts (TypeScript)                      │
│   - feature/api.ts (API calls)                         │
│   - feature/hooks.ts (React Query)                     │
│   - feature/components/ (UI + tests)                   │
│                                                         │
│  I will NEVER scatter feature code across the          │
│  codebase or create inconsistent structures."          │
└─────────────────────────────────────────────────────────┘
```

This contract ensures **consistent, maintainable, AI-friendly code organization**.

## Next Steps

1. Read [overview.md](./overview.md) to understand how all guardrails work together
2. Explore `backend/app/core/` for infrastructure examples
3. Explore `backend/app/shared/` for shared utilities
4. Look at existing features for examples
5. Practice creating a new feature following the pattern

Remember: **Architecture is the foundation that makes all other guardrails effective**. When code is well-organized, AI agents can navigate, understand, and modify it autonomously. Good architecture enables autonomous development at scale.
