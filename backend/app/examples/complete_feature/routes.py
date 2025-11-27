"""
Note routes - Complete example feature.

This module demonstrates:
- FastAPI router configuration
- Dependency injection (database, auth)
- Type-safe request/response handling
- Authentication enforcement
- Error handling
- API documentation with docstrings

Pattern: All API endpoints for a feature live in routes.py
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from .schemas import NoteCreate, NoteListResponse, NoteResponse, NoteUpdate
from .service import create_note, delete_note, get_note, list_notes, update_note

# Create router with prefix and tags
router = APIRouter(
    prefix="/notes",
    tags=["notes"],
)


# Mock authentication dependency (replace with real auth in production)
async def get_current_user_id() -> int:
    """
    Get current authenticated user ID.

    In production, this would:
    - Verify JWT token
    - Extract user ID from token
    - Raise 401 if not authenticated

    For this example, returns hardcoded user ID.
    """
    # TODO: Replace with real authentication
    return 1


@router.post(
    "",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
    description="""
    Create a new note for the authenticated user.

    Security:
    - Requires authentication
    - User can only create notes for themselves
    - Title and content are validated

    Returns:
    - 201: Note created successfully
    - 401: Not authenticated
    - 422: Validation error
    """,
)
async def create_note_endpoint(
    note_data: NoteCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """
    Create a new note.

    Example request:
    ```json
    {
        "title": "My Note",
        "content": "This is the content of my note."
    }
    ```

    Example response:
    ```json
    {
        "id": 1,
        "title": "My Note",
        "content": "This is the content of my note.",
        "owner_id": 1,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
    ```
    """
    note = await create_note(db, note_data, owner_id=user_id)
    return NoteResponse.model_validate(note)


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get a note by ID",
    description="""
    Get a specific note by ID.

    Security:
    - Requires authentication
    - User can only access their own notes (ownership check)

    Returns:
    - 200: Note found
    - 401: Not authenticated
    - 403: Access denied (not the owner)
    - 404: Note not found
    """,
)
async def get_note_endpoint(
    note_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """
    Get a note by ID.

    Example response:
    ```json
    {
        "id": 1,
        "title": "My Note",
        "content": "This is the content of my note.",
        "owner_id": 1,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
    ```
    """
    note = await get_note(db, note_id, owner_id=user_id)
    return NoteResponse.model_validate(note)


@router.get(
    "",
    response_model=NoteListResponse,
    summary="List notes for current user",
    description="""
    List all notes for the authenticated user (paginated).

    Security:
    - Requires authentication
    - User can only see their own notes

    Returns:
    - 200: Notes retrieved
    - 401: Not authenticated
    """,
)
async def list_notes_endpoint(
    page: int = 1,
    page_size: int = 20,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> NoteListResponse:
    """
    List notes for current user.

    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)

    Example response:
    ```json
    {
        "notes": [
            {
                "id": 1,
                "title": "Note 1",
                "content": "Content 1",
                "owner_id": 1,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 20
    }
    ```
    """
    # Limit page_size to max 100
    page_size = min(page_size, 100)

    notes, total = await list_notes(db, owner_id=user_id, page=page, page_size=page_size)

    return NoteListResponse(
        notes=[NoteResponse.model_validate(note) for note in notes],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update a note",
    description="""
    Update an existing note (partial update).

    Security:
    - Requires authentication
    - User can only update their own notes (ownership check)

    Returns:
    - 200: Note updated
    - 401: Not authenticated
    - 403: Access denied (not the owner)
    - 404: Note not found
    - 422: Validation error
    """,
)
async def update_note_endpoint(
    note_id: int,
    note_data: NoteUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """
    Update a note (partial update - only provided fields are updated).

    Example request:
    ```json
    {
        "title": "Updated Title"
    }
    ```

    Example response:
    ```json
    {
        "id": 1,
        "title": "Updated Title",
        "content": "Original content (unchanged)",
        "owner_id": 1,
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:30:00Z"
    }
    ```
    """
    note = await update_note(db, note_id, note_data, owner_id=user_id)
    return NoteResponse.model_validate(note)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="""
    Delete a note permanently.

    Security:
    - Requires authentication
    - User can only delete their own notes (ownership check)

    Returns:
    - 204: Note deleted (no content)
    - 401: Not authenticated
    - 403: Access denied (not the owner)
    - 404: Note not found
    """,
)
async def delete_note_endpoint(
    note_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a note permanently.

    Returns 204 No Content on success.
    """
    await delete_note(db, note_id, owner_id=user_id)
