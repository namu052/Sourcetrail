"""Interactive graphics view for the graph scene."""

from __future__ import annotations

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QMouseEvent, QPainter, QWheelEvent
from PyQt6.QtWidgets import QGraphicsView

from sourcetrail_remake.core.types import NodeId
from sourcetrail_remake.ui.graph.scene import GraphScene


class GraphView(QGraphicsView):
    """Zoomable/pannable view bound to a GraphScene instance."""

    def __init__(self, scene: GraphScene) -> None:
        super().__init__(scene)
        self._last_pan_pos: QPoint | None = None
        self.setObjectName("graph-view")
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setBackgroundBrush(scene.backgroundBrush())

    @property
    def graph_scene(self) -> GraphScene:
        scene = self.scene()
        assert isinstance(scene, GraphScene)
        return scene

    def focus_symbol(self, symbol_id: NodeId, depth: int) -> None:
        self.graph_scene.load_symbol(symbol_id, depth)
        self.fitInView(self.graph_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

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
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
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
