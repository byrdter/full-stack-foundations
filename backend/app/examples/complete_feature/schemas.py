"""
Note schemas - Complete example feature.

This module demonstrates:
- Pydantic BaseModel for validation
- field_validator for custom validation
- Security validation (length limits, HTML prevention)
- Request vs Response schemas
- Type-safe field definitions

Pattern: All request/response schemas for a feature live in schemas.py
"""

from pydantic import BaseModel, field_validator


class NoteCreate(BaseModel):
    """
    Request schema for creating a new note.

    Security:
        - Title limited to 200 characters
        - Content limited to 10,000 characters
        - HTML tags rejected to prevent XSS
    """

    title: str
    content: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """
        Validate note title.

        Raises:
            ValueError: If title is empty, too long, or contains HTML
        """
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")

        if len(v) > 200:
            raise ValueError("Title cannot exceed 200 characters")

        # Prevent HTML/script injection
        if "<" in v or ">" in v or "script" in v.lower():
            raise ValueError("HTML tags not allowed in title")

        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """
        Validate note content.

        Raises:
            ValueError: If content is empty or too long
        """
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")

        if len(v) > 10_000:
            raise ValueError("Content cannot exceed 10,000 characters")

        return v.strip()


class NoteUpdate(BaseModel):
    """
    Request schema for updating an existing note.

    Security:
        - All fields optional (partial updates)
        - Same validation as NoteCreate
    """

    title: str | None = None
    content: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Validate title if provided."""
        if v is None:
            return v

        if not v.strip():
            raise ValueError("Title cannot be empty")

        if len(v) > 200:
            raise ValueError("Title cannot exceed 200 characters")

        if "<" in v or ">" in v or "script" in v.lower():
            raise ValueError("HTML tags not allowed in title")

        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str | None) -> str | None:
        """Validate content if provided."""
        if v is None:
            return v

        if not v.strip():
            raise ValueError("Content cannot be empty")

        if len(v) > 10_000:
            raise ValueError("Content cannot exceed 10,000 characters")

        return v.strip()


class NoteResponse(BaseModel):
    """
    Response schema for note data.

    Pattern:
        - Includes all fields safe to expose to client
        - Excludes internal fields (password_hash, etc.)
        - Includes timestamps for client display
    """

    id: int
    title: str
    content: str
    owner_id: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class NoteListResponse(BaseModel):
    """
    Response schema for paginated list of notes.

    Pattern:
        - Wraps list of notes
        - Includes pagination metadata
    """

    notes: list[NoteResponse]
    total: int
    page: int
    page_size: int
