"""Render a simple QScintilla editor and save an offscreen screenshot."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QStatusBar

from sourcetrail_remake.ui.editor.code_editor import create_code_editor

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "sample-minimal" / "session_manager.py"
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
SCREENSHOT_PATH = ARTIFACT_DIR / "editor_hello.png"
SAVE_COPY_PATH = ARTIFACT_DIR / "editor_saved_copy.py"


def word_under_cursor(line_text: str, column: int) -> str:
    for match in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*", line_text):
        if match.start() <= column <= match.end():
            return match.group(0)
    return ""


class EditorHelloWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PoC 02 - QScintilla Hello Editor")
        self.resize(1280, 720)
        self.editor = create_code_editor(FIXTURE.read_text(encoding="utf-8"))
        self.setCentralWidget(self.editor)
        status = QStatusBar()
        self.cursor_label = QLabel("cursor: line 1, column 0")
        status.addPermanentWidget(self.cursor_label)
        self.setStatusBar(status)

        self.editor.cursorPositionChanged.connect(self.update_cursor_status)
        self.update_cursor_status(0, 0)

    def update_cursor_status(self, line: int, index: int) -> None:
        line_text = self.editor.text(line)
        word = word_under_cursor(line_text, index)
        self.cursor_label.setText(f"cursor: line {line + 1}, column {index} word={word!r}")

    def save_copy(self) -> None:
        SAVE_COPY_PATH.write_text(self.editor.text(), encoding="utf-8")


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication([sys.argv[0]])
    window = EditorHelloWindow()
    window.show()

    def capture() -> None:
        window.save_copy()
        window.grab().save(str(SCREENSHOT_PATH))
        app.quit()

    QTimer.singleShot(250, capture)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
