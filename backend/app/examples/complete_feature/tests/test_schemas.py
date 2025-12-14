"""
Test note schemas (Pydantic validation).

This module demonstrates:
- Testing Pydantic validators
- Testing security validation (XSS prevention)
- Testing input validation (length limits)
- Using pytest.raises for expected failures
"""

import pytest
from pydantic import ValidationError

from app.examples.complete_feature.schemas import NoteCreate, NoteUpdate


class TestNoteCreate:
    """Test NoteCreate schema validation."""

    def test_valid_note_creation(self) -> None:
        """Test that valid note data passes validation."""
        note_data = NoteCreate(title="Test Note", content="Test content")

        assert note_data.title == "Test Note"
        assert note_data.content == "Test content"

    def test_title_strips_whitespace(self) -> None:
        """Test that title whitespace is stripped."""
        note_data = NoteCreate(title="  Test Note  ", content="Content")

        assert note_data.title == "Test Note"

    def test_content_strips_whitespace(self) -> None:
        """Test that content whitespace is stripped."""
        note_data = NoteCreate(title="Title", content="  Test content  ")

        assert note_data.content == "Test content"

    def test_empty_title_raises_error(self) -> None:
        """Test that empty title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(title="", content="Content")

        errors = exc_info.value.errors()
        assert any("Title cannot be empty" in str(err) for err in errors)

    def test_whitespace_only_title_raises_error(self) -> None:
        """Test that whitespace-only title raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(title="   ", content="Content")

        errors = exc_info.value.errors()
        assert any("Title cannot be empty" in str(err) for err in errors)

    def test_title_too_long_raises_error(self) -> None:
        """Test that title exceeding 200 characters raises error."""
        long_title = "a" * 201

        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(title=long_title, content="Content")

        errors = exc_info.value.errors()
        assert any("cannot exceed 200 characters" in str(err) for err in errors)

    def test_empty_content_raises_error(self) -> None:
        """Test that empty content raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(title="Title", content="")

        errors = exc_info.value.errors()
        assert any("Content cannot be empty" in str(err) for err in errors)

    def test_content_too_long_raises_error(self) -> None:
        """Test that content exceeding 10,000 characters raises error."""
        long_content = "a" * 10_001

        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(title="Title", content=long_content)

        errors = exc_info.value.errors()
        assert any("cannot exceed 10,000 characters" in str(err) for err in errors)

    @pytest.mark.security
    def test_html_in_title_raises_error(self) -> None:
        """Test that HTML tags in title are rejected (XSS prevention)."""
        html_titles = [
            "<script>alert('XSS')</script>",
            "<p>Hello</p>",
            "Title<br>Break",
            "<img src=x onerror=alert('XSS')>",
        ]

        for html_title in html_titles:
            with pytest.raises(ValidationError) as exc_info:
                NoteCreate(title=html_title, content="Content")

            errors = exc_info.value.errors()
            assert any("HTML tags not allowed" in str(err) for err in errors)

    @pytest.mark.security
    def test_script_keyword_in_title_raises_error(self) -> None:
        """Test that 'script' keyword in title is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            NoteCreate(title="JavaScript code", content="Content")

        errors = exc_info.value.errors()
        assert any("HTML tags not allowed" in str(err) for err in errors)


class TestNoteUpdate:
    """Test NoteUpdate schema validation."""

    def test_partial_update_with_title_only(self) -> None:
        """Test updating only title."""
        update_data = NoteUpdate(title="New Title")

        assert update_data.title == "New Title"
        assert update_data.content is None

    def test_partial_update_with_content_only(self) -> None:
        """Test updating only content."""
        update_data = NoteUpdate(content="New content")

        assert update_data.title is None
        assert update_data.content == "New content"

    def test_empty_update(self) -> None:
        """Test that empty update (no fields) is valid."""
        update_data = NoteUpdate()

        assert update_data.title is None
        assert update_data.content is None

    def test_title_validation_applies(self) -> None:
        """Test that title validation is applied in updates."""
        with pytest.raises(ValidationError) as exc_info:
            NoteUpdate(title="<script>alert('XSS')</script>")

        errors = exc_info.value.errors()
        assert any("HTML tags not allowed" in str(err) for err in errors)

    def test_content_validation_applies(self) -> None:
        """Test that content validation is applied in updates."""
        long_content = "a" * 10_001

        with pytest.raises(ValidationError) as exc_info:
            NoteUpdate(content=long_content)

        errors = exc_info.value.errors()
        assert any("cannot exceed 10,000 characters" in str(err) for err in errors)
