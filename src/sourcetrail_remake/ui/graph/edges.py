"""Graph edge rendering primitives."""

from __future__ import annotations

from math import atan2, cos, sin

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import QGraphicsPathItem

from sourcetrail_remake.core.types import EdgeType


class RenderedEdgeItem(QGraphicsPathItem):
    """Bezier edge with a directional arrow head."""

    def __init__(
        self,
        start: QPointF,
        end: QPointF,
        edge_type: EdgeType,
        *,
        offset: float = 0.0,
    ) -> None:
        self.edge_type = edge_type
        self.offset = offset
        self.color, self.pen_style = _edge_style(edge_type)
        path = _build_edge_path(start, end, offset=offset)
        super().__init__(path)
        self.arrow_head = _build_arrow_head(path)
        self.setPen(QPen(self.color, 3, self.pen_style))
        self.setZValue(-1)

    def paint(
        self,
        painter: QPainter,
        option: object,
        widget: object | None = None,
    ) -> None:
        super().paint(painter, option, widget)
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(self.arrow_head)


class EdgeRenderer:
    """Factory for graph edge items."""

    @staticmethod
    def create_edge(
        start: QPointF,
        end: QPointF,
        edge_type: EdgeType,
        *,
        offset: float = 0.0,
    ) -> QGraphicsPathItem:
        return RenderedEdgeItem(start, end, edge_type, offset=offset)


def _build_edge_path(start: QPointF, end: QPointF, *, offset: float) -> QPainterPath:
    path = QPainterPath(start)
    mid_x = (start.x() + end.x()) / 2
    control_offset = abs(end.x() - start.x()) * 0.2 + offset
    path.cubicTo(
        QPointF(mid_x + control_offset, start.y()),
        QPointF(mid_x - control_offset, end.y()),
        end,
    )
    return path


def _build_arrow_head(path: QPainterPath) -> QPolygonF:
    end = path.pointAtPercent(1.0)
    tangent = path.angleAtPercent(0.97)
    angle_radians = atan2(-sin(tangent), cos(tangent))
    size = 10.0
    left = QPointF(
        end.x() - cos(angle_radians - 0.45) * size,
        end.y() + sin(angle_radians - 0.45) * size,
    )
    right = QPointF(
        end.x() - cos(angle_radians + 0.45) * size,
        end.y() + sin(angle_radians + 0.45) * size,
    )
    return QPolygonF([end, left, right])


def _edge_style(edge_type: EdgeType) -> tuple[QColor, Qt.PenStyle]:
    if edge_type == EdgeType.EDGE_CALL:
        return QColor("#f97316"), Qt.PenStyle.SolidLine
    if edge_type == EdgeType.EDGE_USAGE:
        return QColor("#2563eb"), Qt.PenStyle.SolidLine
    if edge_type == EdgeType.EDGE_MEMBER:
        return QColor("#64748b"), Qt.PenStyle.DashLine
    return QColor("#475569"), Qt.PenStyle.DotLine
