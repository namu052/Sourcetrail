"""QScintilla bootstrap helper used by tests and the Phase 0 PoC."""

from __future__ import annotations

from PyQt6.Qsci import QsciScintilla

from sourcetrail_remake.ui.editor.editor import QScintillaEditor


def create_code_editor(source_text: str) -> QsciScintilla:
    """Return a configured QScintilla editor for Python text."""
    editor = QScintillaEditor()
    editor.load_text(source_text)
    return editor
