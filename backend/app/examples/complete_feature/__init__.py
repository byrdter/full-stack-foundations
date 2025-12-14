"""
Complete example feature demonstrating all patterns.

This feature demonstrates:
1. **Vertical slice architecture** - All code for notes feature in one folder
2. **Complete logging lifecycle** - Started, completed, failed events
3. **Type safety** - Full type hints with mypy/pyright strict mode
4. **Security** - Authentication, authorization, input validation
5. **Testing** - Unit, integration, and security tests

File structure:
- models.py: Database models (SQLAlchemy 2.0)
- schemas.py: Request/response schemas (Pydantic)
- routes.py: API endpoints (FastAPI)
- service.py: Business logic
- tests/: Comprehensive tests

Usage:
    # In app/main.py
    from app.examples.complete_feature.routes import router as notes_router
    app.include_router(notes_router)

Learn more:
    See explanations/architecture.md for vertical slice architecture details
    See explanations/logging.md for logging patterns
    See explanations/tests.md for testing patterns

Note:
    Router is NOT exported from __init__.py to avoid SQLAlchemy model
    double-import issues during test collection. Import directly from routes.py.
"""

# Don't export router here - it causes SQLAlchemy model conflicts during pytest collection
# Import directly: from app.examples.complete_feature.routes import router
