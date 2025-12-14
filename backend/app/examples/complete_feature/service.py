"""
Note service - Complete example feature.

This module demonstrates:
- Complete logging lifecycle (started, completed, failed)
- Error handling with proper logging
- Type-safe function signatures
- Database operations with SQLAlchemy 2.0
- Authorization checks
- Proper exception handling

Pattern: All business logic for a feature lives in service.py
"""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

from .models import Note
from .schemas import NoteCreate, NoteUpdate

logger = get_logger(__name__)


async def create_note(
    db: AsyncSession, note_data: NoteCreate, owner_id: int
) -> Note:
    """
    Create a new note.

    Args:
        db: Database session
        note_data: Note creation data
        owner_id: ID of the user creating the note

    Returns:
        Created note

    Raises:
        Exception: If database operation fails

    Example:
        >>> note = await create_note(db, NoteCreate(title="Test", content="Hello"), 1)
        >>> note.title
        'Test'
    """
    # Logging lifecycle: START
    logger.info(
        "note.create_started",
        owner_id=owner_id,
        title_length=len(note_data.title),
        content_length=len(note_data.content),
    )

    try:
        # Create note
        note = Note(
            title=note_data.title,
            content=note_data.content,
            owner_id=owner_id,
        )

        db.add(note)
        await db.commit()
        await db.refresh(note)

        # Logging lifecycle: SUCCESS
        logger.info(
            "note.create_completed",
            note_id=note.id,
            owner_id=owner_id,
        )

        return note

    except Exception as e:
        await db.rollback()

        # Logging lifecycle: FAILURE
        logger.error(
            "note.create_failed",
            owner_id=owner_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise


async def get_note(db: AsyncSession, note_id: int, owner_id: int) -> Note:
    """
    Get a note by ID (with ownership check).

    Args:
        db: Database session
        note_id: Note ID
        owner_id: ID of the user requesting the note

    Returns:
        Note if found and owned by user

    Raises:
        HTTPException: If note not found or access denied

    Security:
        - Authorization check: User must own the note
        - Logs access denied attempts
    """
    logger.info("note.get_started", note_id=note_id, owner_id=owner_id)

    try:
        stmt = select(Note).where(Note.id == note_id)
        result = await db.execute(stmt)
        note = result.scalar_one_or_none()

        if note is None:
            logger.warning(
                "note.get_failed",
                note_id=note_id,
                owner_id=owner_id,
                reason="not_found",
            )
            raise HTTPException(status_code=404, detail="Note not found")

        # Authorization check
        if note.owner_id != owner_id:
            logger.warning(
                "authorization.access_denied",
                note_id=note_id,
                owner_id=owner_id,
                actual_owner_id=note.owner_id,
                action="get_note",
            )
            raise HTTPException(status_code=403, detail="Access denied")

        logger.info("note.get_completed", note_id=note_id, owner_id=owner_id)

        return note

    except HTTPException:
        # Re-raise HTTP exceptions (already logged above)
        raise

    except Exception as e:
        logger.error(
            "note.get_failed",
            note_id=note_id,
            owner_id=owner_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise


async def list_notes(
    db: AsyncSession, owner_id: int, page: int = 1, page_size: int = 20
) -> tuple[list[Note], int]:
    """
    List notes for a user (paginated).

    Args:
        db: Database session
        owner_id: ID of the user
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Tuple of (notes list, total count)

    Example:
        >>> notes, total = await list_notes(db, owner_id=1, page=1, page_size=10)
        >>> len(notes) <= 10
        True
    """
    logger.info(
        "note.list_started",
        owner_id=owner_id,
        page=page,
        page_size=page_size,
    )

    try:
        # Get total count
        count_stmt = select(func.count()).where(Note.owner_id == owner_id)
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()

        # Get paginated notes
        offset = (page - 1) * page_size
        stmt = (
            select(Note)
            .where(Note.owner_id == owner_id)
            .order_by(Note.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        notes = list(result.scalars().all())

        logger.info(
            "note.list_completed",
            owner_id=owner_id,
            total=total,
            page=page,
            returned_count=len(notes),
        )

        return notes, total

    except Exception as e:
        logger.error(
            "note.list_failed",
            owner_id=owner_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise


async def update_note(
    db: AsyncSession, note_id: int, note_data: NoteUpdate, owner_id: int
) -> Note:
    """
    Update a note.

    Args:
        db: Database session
        note_id: Note ID
        note_data: Note update data
        owner_id: ID of the user updating the note

    Returns:
        Updated note

    Raises:
        HTTPException: If note not found or access denied

    Security:
        - Authorization check: User must own the note
    """
    logger.info(
        "note.update_started",
        note_id=note_id,
        owner_id=owner_id,
    )

    try:
        # Get note (includes ownership check)
        note = await get_note(db, note_id, owner_id)

        # Update fields
        update_data = note_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(note, field, value)

        # Update timestamp
        note.updated_at = datetime.utcnow()  # type: ignore[attr-defined]

        await db.commit()
        await db.refresh(note)

        # Audit log
        logger.info(
            "audit.note_updated",
            note_id=note_id,
            owner_id=owner_id,
            updated_fields=list(update_data.keys()),
        )

        logger.info("note.update_completed", note_id=note_id, owner_id=owner_id)

        return note

    except HTTPException:
        # Re-raise HTTP exceptions (already logged)
        raise

    except Exception as e:
        await db.rollback()

        logger.error(
            "note.update_failed",
            note_id=note_id,
            owner_id=owner_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise


async def delete_note(db: AsyncSession, note_id: int, owner_id: int) -> None:
    """
    Delete a note.

    Args:
        db: Database session
        note_id: Note ID
        owner_id: ID of the user deleting the note

    Raises:
        HTTPException: If note not found or access denied

    Security:
        - Authorization check: User must own the note
        - Audit log: Deletion is logged
    """
    logger.info("note.delete_started", note_id=note_id, owner_id=owner_id)

    try:
        # Get note (includes ownership check)
        note = await get_note(db, note_id, owner_id)

        await db.delete(note)
        await db.commit()

        # Audit log
        logger.info(
            "audit.note_deleted",
            note_id=note_id,
            owner_id=owner_id,
            title=note.title,
        )

        logger.info("note.delete_completed", note_id=note_id, owner_id=owner_id)

    except HTTPException:
        # Re-raise HTTP exceptions (already logged)
        raise

    except Exception as e:
        await db.rollback()

        logger.error(
            "note.delete_failed",
            note_id=note_id,
            owner_id=owner_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise
