"""QScintilla editor wrapper used by the Phase 2 context workflow."""

from __future__ import annotations

from pathlib import Path

from PyQt6.Qsci import QsciLexerPython, QsciScintilla
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont


class QScintillaEditor(QsciScintilla):
    """Configured Python editor that emits debounced cursor positions."""

    cursor_moved = pyqtSignal(str, int, int)

    def __init__(self, parent: object | None = None, *, debounce_ms: int = 150) -> None:
        super().__init__(parent)
        self._path: Path | None = None
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(debounce_ms)
        self._debounce_timer.timeout.connect(self._emit_cursor_moved)
        self._configure_base_editor()
        self.cursorPositionChanged.connect(self._schedule_cursor_moved)

    @property
    def path(self) -> Path | None:
        return self._path

    def load_file(self, path: Path) -> None:
        """Load UTF-8 source text from disk."""
        self._path = Path(path).resolve()
        self.setText(self._path.read_text(encoding="utf-8"))
        self.setModified(False)
        self.setCursorPosition(0, 0)
        self._emit_cursor_moved()

    def load_text(self, source_text: str, *, path: Path | None = None) -> None:
        """Load source text without requiring an on-disk file."""
        self._path = None if path is None else Path(path).resolve()
        self.setText(source_text)
        self.setModified(False)
        self.setCursorPosition(0, 0)
        self._emit_cursor_moved()

    def goto_line(self, line: int) -> None:
        """Move the caret to a one-based line number."""
        zero_based_line = max(line - 1, 0)
        self.setCursorPosition(zero_based_line, 0)
        self.ensureLineVisible(zero_based_line)
        self.setFocus()
        self._emit_cursor_moved()

    def _configure_base_editor(self) -> None:
        self.setUtf8(True)
        self.setLexer(QsciLexerPython(self))
        self.setMarginsFont(QFont("Consolas", 10))
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)
        self.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#f4f4f4"))
        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)

    def _schedule_cursor_moved(self, _line: int, _index: int) -> None:
        self._debounce_timer.start()

    def _emit_cursor_moved(self) -> None:
        if self._path is None:
            return
        line, column = self.getCursorPosition()
        self.cursor_moved.emit(str(self._path), line + 1, column)
