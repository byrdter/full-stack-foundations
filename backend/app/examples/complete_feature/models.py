"""
Note models - Complete example feature.

This module demonstrates:
- SQLAlchemy 2.0 style with Mapped types
- TimestampMixin for automatic timestamps
- Foreign key relationships
- Type-safe column definitions
- Ownership tracking for authorization

Pattern: All database models for a feature live in models.py
"""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.models import TimestampMixin


class Note(Base, TimestampMixin):
    """
    Note model representing a user's text note.

    Security:
        - owner_id tracks ownership for authorization
        - title and content should be sanitized before display (XSS prevention)

    Lifecycle:
        - created_at: Automatically set on INSERT (via TimestampMixin)
        - updated_at: Automatically updated on UPDATE (via TimestampMixin)
    """

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Note(id={self.id}, title='{self.title[:30]}', owner_id={self.owner_id})>"
        )
