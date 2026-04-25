"""Minimal graph view with zoom and pan controls."""

from __future__ import annotations

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QMouseEvent, QPainter, QWheelEvent
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView


class GraphView(QGraphicsView):
    """Simple zoomable/pannable QGraphicsView."""

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)
        self._last_pan_pos: QPoint | None = None
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        if event is None:
            return
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        if event.button() == Qt.MouseButton.MiddleButton:
            self._last_pan_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        if self._last_pan_pos is not None:
            delta = event.position().toPoint() - self._last_pan_pos
            self._last_pan_pos = event.position().toPoint()
            h_scroll = self.horizontalScrollBar()
            v_scroll = self.verticalScrollBar()
            if h_scroll is not None:
                h_scroll.setValue(h_scroll.value() - delta.x())
            if v_scroll is not None:
                v_scroll.setValue(v_scroll.value() - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        if self._last_pan_pos is not None:
            self._last_pan_pos = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)
