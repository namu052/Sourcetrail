"""Render a small graph mock and save an offscreen screenshot."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow

from sourcetrail_remake.ui.graph.scene import GraphScene
from sourcetrail_remake.ui.graph.view import GraphView

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
SCREENSHOT_PATH = ARTIFACT_DIR / "graph_hello.png"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication([sys.argv[0]])

    scene = GraphScene()
    scene.populate_demo_graph()
    view = GraphView(scene)
    view.setSceneRect(scene.itemsBoundingRect().adjusted(-20, -20, 20, 20))

    window = QMainWindow()
    window.setWindowTitle("PoC 03 - Graph Hello")
    window.resize(1200, 520)
    window.setCentralWidget(view)
    window.show()

    def capture() -> None:
        window.grab().save(str(SCREENSHOT_PATH))
        app.quit()

    QTimer.singleShot(250, capture)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
