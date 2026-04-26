"""QScintilla editor wrapper used by the Phase 2 context workflow."""

from __future__ import annotations

from pathlib import Path

from PyQt6.Qsci import QsciLexerPython, QsciScintilla
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QWidget

EDITOR_FONT_FAMILY = "Consolas"
EDITOR_FONT_SIZE = 10
EDITOR_BACKGROUND = "#ffffff"
EDITOR_FOREGROUND = "#1f2328"
EDITOR_MARGIN_BACKGROUND = "#f6f8fa"
EDITOR_MARGIN_FOREGROUND = "#57606a"
EDITOR_CARET_LINE = "#eef6ff"
BOOKMARK_MARKER = 8
BOOKMARK_MARGIN = 1
BOOKMARK_MARGIN_WIDTH = 16
BOOKMARK_MARKER_COLOR = "#f2cc60"
BOOKMARK_MARKER_BACKGROUND = "#8250df"


class QScintillaEditor(QsciScintilla):
    """Configured Python editor that emits debounced cursor positions."""

    cursor_moved = pyqtSignal(str, int, int)

    def __init__(self, parent: QWidget | None = None, *, debounce_ms: int = 150) -> None:
        super().__init__(parent)
        self._path: Path | None = None
        self._bookmark_markers: dict[int, int] = {}
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

    def highlight_range(
        self,
        *,
        start_line: int,
        start_column: int,
        end_line: int,
        end_column: int,
    ) -> None:
        """Select a one-based source range in the editor."""
        self.setSelection(
            max(start_line - 1, 0),
            max(start_column, 0),
            max(end_line - 1, 0),
            max(end_column, 0),
        )
        self.ensureLineVisible(max(start_line - 1, 0))

    def _configure_base_editor(self) -> None:
        self.setUtf8(True)
        lexer = QsciLexerPython(self)
        configure_python_lexer(lexer)
        self.setLexer(lexer)
        self.setMarginsFont(QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE))
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(BOOKMARK_MARGIN, BOOKMARK_MARGIN_WIDTH)
        self.setMarginSensitivity(BOOKMARK_MARGIN, True)
        self.setMarginsBackgroundColor(QColor(EDITOR_MARGIN_BACKGROUND))
        self.setMarginsForegroundColor(QColor(EDITOR_MARGIN_FOREGROUND))
        self.markerDefine(QsciScintilla.MarkerSymbol.Bookmark, BOOKMARK_MARKER)
        self.setMarkerForegroundColor(QColor(BOOKMARK_MARKER_COLOR), BOOKMARK_MARKER)
        self.setMarkerBackgroundColor(QColor(BOOKMARK_MARKER_BACKGROUND), BOOKMARK_MARKER)
        self.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor(EDITOR_CARET_LINE))
        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)
        self.setPaper(QColor(EDITOR_BACKGROUND))
        self.setColor(QColor(EDITOR_FOREGROUND))

    def _schedule_cursor_moved(self, _line: int, _index: int) -> None:
        self._debounce_timer.start()

    def _emit_cursor_moved(self) -> None:
        if self._path is None:
            return
        line, column = self.getCursorPosition()
        self.cursor_moved.emit(str(self._path), line + 1, column)

    def add_bookmark_marker(self, line: int) -> None:
        """Show a bookmark marker at a one-based source line."""
        if line <= 0:
            raise ValueError("bookmark marker line must be one-based")
        self.remove_bookmark_marker(line)
        handle = self.markerAdd(line - 1, BOOKMARK_MARKER)
        self._bookmark_markers[line] = int(handle)

    def remove_bookmark_marker(self, line: int) -> None:
        """Remove a bookmark marker from a one-based source line."""
        handle = self._bookmark_markers.pop(line, None)
        if handle is not None:
            self.markerDeleteHandle(handle)

    def set_bookmark_markers(self, lines: list[int] | tuple[int, ...]) -> None:
        """Replace all visible bookmark markers with ``lines``."""
        self.clear_bookmark_markers()
        for line in lines:
            self.add_bookmark_marker(line)

    def clear_bookmark_markers(self) -> None:
        """Remove all visible bookmark markers."""
        self.markerDeleteAll(BOOKMARK_MARKER)
        self._bookmark_markers.clear()

    def bookmark_marker_lines(self) -> tuple[int, ...]:
        """Return one-based lines currently carrying bookmark markers."""
        return tuple(sorted(self._bookmark_markers))


def configure_python_lexer(lexer: QsciLexerPython) -> None:
    """Apply the shared Python syntax palette."""
    base_font = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
    lexer.setDefaultFont(base_font)
    lexer.setDefaultPaper(QColor(EDITOR_BACKGROUND))
    lexer.setDefaultColor(QColor(EDITOR_FOREGROUND))
    lexer.setFont(base_font)
    lexer.setColor(QColor("#0550ae"), QsciLexerPython.Keyword)
    lexer.setColor(QColor("#8250df"), QsciLexerPython.ClassName)
    lexer.setColor(QColor("#6639ba"), QsciLexerPython.FunctionMethodName)
    lexer.setColor(QColor("#0a3069"), QsciLexerPython.DoubleQuotedString)
    lexer.setColor(QColor("#0a3069"), QsciLexerPython.SingleQuotedString)
    lexer.setColor(QColor("#116329"), QsciLexerPython.Comment)
    lexer.setColor(QColor("#953800"), QsciLexerPython.Number)
    lexer.setColor(QColor("#24292f"), QsciLexerPython.Identifier)
    lexer.setColor(QColor("#6e7781"), QsciLexerPython.Operator)
