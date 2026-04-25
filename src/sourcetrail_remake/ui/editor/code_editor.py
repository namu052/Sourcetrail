"""QScintilla bootstrap widget used by the Phase 0 PoC."""

from __future__ import annotations

from PyQt6.Qsci import QsciLexerPython, QsciScintilla
from PyQt6.QtGui import QColor, QFont


def create_code_editor(source_text: str) -> QsciScintilla:
    """Return a configured QScintilla editor for Python text."""
    editor = QsciScintilla()
    editor.setUtf8(True)
    editor.setText(source_text)
    editor.setLexer(QsciLexerPython(editor))
    editor.setMarginsFont(QFont("Consolas", 10))
    editor.setMarginWidth(0, "0000")
    editor.setMarginLineNumbers(0, True)
    editor.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle)
    editor.setCaretLineVisible(True)
    editor.setCaretLineBackgroundColor(QColor("#f4f4f4"))
    editor.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)
    return editor
