"""Demo graph scene for the Phase 0 PoC."""

from __future__ import annotations

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
)


class GraphScene(QGraphicsScene):
    """Scene that draws a small static graph inspired by the Phase 0 mock."""

    def populate_demo_graph(self) -> None:
        self.clear()
        self.setBackgroundBrush(QBrush(QColor("#fbfbfd")))

        nodes = {
            "SessionManager": QPointF(20, 20),
            "Session": QPointF(350, 20),
            "unsolved": QPointF(680, 20),
        }
        for name, pos in nodes.items():
            self._add_container(name, pos, hatched=name == "unsolved")

        self._add_edge(
            QPointF(280, 120),
            QPointF(350, 120),
            QColor("#f97316"),
            Qt.PenStyle.SolidLine,
        )
        self._add_edge(
            QPointF(610, 120),
            QPointF(680, 120),
            QColor("#2563eb"),
            Qt.PenStyle.DashLine,
        )

    def _add_container(self, title: str, top_left: QPointF, hatched: bool) -> None:
        rect_item = QGraphicsRectItem(top_left.x(), top_left.y(), 250, 220)
        rect_item.setPen(QPen(QColor("#1f2937"), 2))
        if hatched:
            rect_item.setBrush(QBrush(QColor("#d1d5db"), Qt.BrushStyle.BDiagPattern))
        else:
            rect_item.setBrush(QBrush(QColor("#ffffff")))
        self.addItem(rect_item)

        title_item = QGraphicsSimpleTextItem(title)
        title_item.setPos(top_left.x() + 12, top_left.y() + 10)
        self.addItem(title_item)

        members = ["get_session", "cleanup_expired", "last_active", "is_expired", "unsolved"]
        for index, member in enumerate(members):
            member_item = QGraphicsSimpleTextItem(member)
            member_item.setPos(top_left.x() + 16, top_left.y() + 50 + index * 28)
            self.addItem(member_item)

    def _add_edge(self, start: QPointF, end: QPointF, color: QColor, style: Qt.PenStyle) -> None:
        path = QPainterPath(start)
        mid_x = (start.x() + end.x()) / 2
        path.cubicTo(QPointF(mid_x, start.y()), QPointF(mid_x, end.y()), end)
        edge = QGraphicsPathItem(path)
        edge.setPen(QPen(color, 3, style))
        self.addItem(edge)
