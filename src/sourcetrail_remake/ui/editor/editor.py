"""QScintilla editor wrapper used by the Phase 2 context workflow."""

from __future__ import annotations

from pathlib import Path

from PyQt6.Qsci import QsciLexerPython, QsciScintilla
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont

EDITOR_FONT_FAMILY = "Consolas"
EDITOR_FONT_SIZE = 10
EDITOR_BACKGROUND = "#ffffff"
EDITOR_FOREGROUND = "#1f2328"
EDITOR_MARGIN_BACKGROUND = "#f6f8fa"
EDITOR_MARGIN_FOREGROUND = "#57606a"
EDITOR_CARET_LINE = "#eef6ff"


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
        lexer = QsciLexerPython(self)
        configure_python_lexer(lexer)
        self.setLexer(lexer)
        self.setMarginsFont(QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE))
        self.setMarginWidth(0, "0000")
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor(EDITOR_MARGIN_BACKGROUND))
        self.setMarginsForegroundColor(QColor(EDITOR_MARGIN_FOREGROUND))
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
