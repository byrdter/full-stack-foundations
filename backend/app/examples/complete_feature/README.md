# Complete Example Feature: Notes

This is a **complete example feature** demonstrating all patterns and best practices for the full-stack-foundations repository.

## Purpose

This feature serves as a **reference implementation** showing:

1. ✅ **Vertical Slice Architecture** - All code in one folder
2. ✅ **Complete Logging Lifecycle** - Started, completed, failed events
3. ✅ **Type Safety** - Full type hints (mypy/pyright strict mode)
4. ✅ **Security** - Authentication, authorization, input validation
5. ✅ **Testing** - Unit tests and security tests

## What This Feature Does

The Notes feature allows authenticated users to:
- Create text notes with title and content
- List their notes (paginated)
- Get a specific note by ID
- Update a note
- Delete a note

**Security**: Users can only access/modify their own notes (ownership model).

## File Structure

```
complete_feature/
├── __init__.py                 # Feature exports
├── models.py                   # Database models (SQLAlchemy 2.0)
├── schemas.py                  # Request/response schemas (Pydantic)
├── routes.py                   # API endpoints (FastAPI)
├── service.py                  # Business logic
├── tests/                      # Tests
│   ├── __init__.py
│   └── test_schemas.py         # Pydantic validation tests
└── README.md                   # This file
```

## What Each File Demonstrates

### `models.py` - Database Models

**Demonstrates:**
- SQLAlchemy 2.0 style with `Mapped` types
- `TimestampMixin` for automatic `created_at`/`updated_at`
- Foreign key relationships
- Type-safe column definitions
- Ownership tracking (`owner_id`)

**Key Pattern:**
```python
class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
```

### `schemas.py` - Request/Response Validation

**Demonstrates:**
- Pydantic `BaseModel` for validation
- `field_validator` for custom validation
- Security validation (length limits, HTML prevention)
- Request vs Response schemas
- Type-safe field definitions

**Key Patterns:**
```python
class NoteCreate(BaseModel):
    title: str
    content: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if "<" in v or ">" in v:
            raise ValueError("HTML tags not allowed")
        return v.strip()
```

### `routes.py` - API Endpoints

**Demonstrates:**
- FastAPI router configuration
- Dependency injection (`Depends`)
- Type-safe request/response handling
- Authentication enforcement
- Comprehensive API documentation
- HTTP status codes

**Key Pattern:**
```python
@router.post("", response_model=NoteResponse, status_code=201)
async def create_note_endpoint(
    note_data: NoteCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    note = await create_note(db, note_data, owner_id=user_id)
    return NoteResponse.model_validate(note)
```

### `service.py` - Business Logic

**Demonstrates:**
- **Complete logging lifecycle**:
  - `note.create_started` → operation begins
  - `note.create_completed` → success
  - `note.create_failed` → failure with error details
- Error handling with proper logging
- Type-safe function signatures
- Database operations (SQLAlchemy 2.0)
- Authorization checks (ownership verification)
- Audit logging for sensitive operations

**Key Pattern:**
```python
async def create_note(db: AsyncSession, note_data: NoteCreate, owner_id: int) -> Note:
    # START
    logger.info("note.create_started", owner_id=owner_id)

    try:
        note = Note(**note_data.model_dump(), owner_id=owner_id)
        db.add(note)
        await db.commit()

        # SUCCESS
        logger.info("note.create_completed", note_id=note.id)
        return note

    except Exception as e:
        # FAILURE
        logger.error("note.create_failed", error=str(e), exc_info=True)
        raise
```

### `tests/` - Comprehensive Tests

**Demonstrates:**
- Testing Pydantic validators
- Security tests (`@pytest.mark.security`)
- Testing XSS prevention
- Testing input validation
- Using `pytest.raises` for expected failures

**Key Pattern:**
```python
@pytest.mark.security
def test_html_in_title_raises_error() -> None:
    """Test that HTML tags are rejected (XSS prevention)."""
    with pytest.raises(ValidationError):
        NoteCreate(title="<script>alert('XSS')</script>", content="Content")
```

## How to Use This Example

### 1. Study the Code

Read the files in this order:
1. `models.py` - See database structure
2. `schemas.py` - See validation rules
3. `service.py` - See business logic + logging
4. `routes.py` - See API endpoints
5. `tests/` - See testing patterns

### 2. Run the Tests

```bash
# From backend/ directory
uv run pytest app/examples/complete_feature/tests/ -v
```

### 3. Copy the Pattern

When creating a new feature:

```bash
# Create feature folder
mkdir app/my_feature
cd app/my_feature

# Copy structure
touch models.py schemas.py routes.py service.py __init__.py
mkdir tests
```

Then follow the patterns from this example.

### 4. Register the Router

In `app/main.py`:
```python
from app.examples.complete_feature.routes import router as notes_router

app.include_router(notes_router)
```

## Logging Patterns

This feature demonstrates the **complete logging lifecycle**:

```
┌─────────────────────────────────────┐
│  1. ACTION STARTED                  │
│  Log: note.create_started           │
│  Context: owner_id, input size      │
└───────────┬─────────────────────────┘
            ▼
┌─────────────────────────────────────┐
│  2. PERFORM OPERATION               │
│  - Database write                   │
│  - Business logic                   │
└───────────┬─────────────────────────┘
            │
            ├──► SUCCESS ──────┐
            │                  ▼
            │     ┌─────────────────────────────┐
            │     │  3a. ACTION COMPLETED       │
            │     │  Log: note.create_completed │
            │     │  Context: note_id           │
            │     └─────────────────────────────┘
            │
            └──► FAILURE ──────┐
                               ▼
                  ┌─────────────────────────────┐
                  │  3b. ACTION FAILED          │
                  │  Log: note.create_failed    │
                  │  Context: error, exc_info   │
                  └─────────────────────────────┘
```

**Every operation follows this pattern:**
- Log START with context
- Perform operation
- Log SUCCESS or FAILURE with details

## Security Patterns

### 1. Input Validation (Pydantic)

```python
# Length limits
title: max 200 characters
content: max 10,000 characters

# XSS prevention
HTML tags rejected: <script>, <p>, <br>, etc.
```

### 2. Authentication

```python
# Every endpoint requires user_id
user_id: int = Depends(get_current_user_id)
```

### 3. Authorization (Ownership Checks)

```python
# Users can only access their own notes
if note.owner_id != user_id:
    raise HTTPException(status_code=403, detail="Access denied")
```

### 4. Audit Logging

```python
# Log sensitive operations
logger.info("audit.note_deleted", note_id=note_id, user_id=user_id)
```

## Type Safety

This feature is **100% type-safe**:

```bash
# Zero type errors
uv run mypy app/examples/complete_feature/
uv run pyright app/examples/complete_feature/
```

**All functions have:**
- Type hints for all parameters
- Return type annotations
- No `Any` types
- No type suppressions

## Testing Coverage

Tests cover:
- ✅ **Validation** - Pydantic field validators
- ✅ **Security** - XSS prevention, HTML rejection
- ✅ **Edge cases** - Empty strings, whitespace, length limits
- ✅ **Expected failures** - Invalid input raises proper errors

## Learn More

- **Architecture**: See `explanations/architecture.md` for vertical slice details
- **Logging**: See `explanations/logging.md` for event taxonomy
- **Testing**: See `explanations/tests.md` for testing patterns
- **Type Safety**: See `explanations/type-checks.md` for type checking
- **Security**: See all explanation docs for security patterns

## Next Steps

1. **Study this feature** - Understand all the patterns
2. **Run the tests** - See them pass
3. **Create your own feature** - Follow this structure
4. **Add to main.py** - Register your router
5. **Run guardrails** - Type check, lint, test
6. **Iterate** - Fix any issues, repeat

Remember: **This is the pattern for ALL features in this repository.**

Every feature should follow this structure. Consistency enables AI agents to generate correct code autonomously.
