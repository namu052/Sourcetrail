"""Graph edge rendering primitives."""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, sin
from typing import NewType

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import QGraphicsPathItem

from sourcetrail_remake.core.types import EdgeId, EdgeType, GraphEdgeRecord, NodeId

BundledEdgeId = NewType("BundledEdgeId", int)


@dataclass(slots=True, frozen=True)
class BundledEdgeRecord:
    id: BundledEdgeId
    source: NodeId
    target: NodeId
    edge_type: EdgeType
    bundle_count: int
    edge_ids: tuple[EdgeId, ...]


class RenderedEdgeItem(QGraphicsPathItem):
    """Bezier edge with a directional arrow head."""

    def __init__(
        self,
        start: QPointF,
        end: QPointF,
        edge_type: EdgeType,
        *,
        offset: float = 0.0,
        bundle_count: int = 1,
    ) -> None:
        self.edge_type = edge_type
        self.offset = offset
        self.bundle_count = bundle_count
        self.color, self.pen_style = _edge_style(edge_type)
        path = _build_edge_path(start, end, offset=offset)
        super().__init__(path)
        self.arrow_head = _build_arrow_head(path)
        self.setPen(QPen(self.color, 4 if bundle_count > 1 else 3, self.pen_style))
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
        if self.bundle_count > 1:
            midpoint = self.path().pointAtPercent(0.5)
            painter.setBrush(QColor("#ffffff"))
            painter.setPen(QPen(self.color, 2))
            painter.drawEllipse(midpoint, 10, 10)
            painter.drawText(
                midpoint.x() - 5,
                midpoint.y() + 4,
                str(self.bundle_count),
            )


class EdgeRenderer:
    """Factory for graph edge items."""

    @staticmethod
    def create_edge(
        start: QPointF,
        end: QPointF,
        edge_type: EdgeType,
        *,
        offset: float = 0.0,
        bundle_count: int = 1,
    ) -> QGraphicsPathItem:
        return RenderedEdgeItem(start, end, edge_type, offset=offset, bundle_count=bundle_count)

    @staticmethod
    def bundle_parallel_edges(edges: tuple[GraphEdgeRecord, ...]) -> tuple[BundledEdgeRecord, ...]:
        buckets: dict[tuple[int, int], list[GraphEdgeRecord]] = {}
        for edge in edges:
            buckets.setdefault((int(edge.source), int(edge.target)), []).append(edge)

        bundled: list[BundledEdgeRecord] = []
        for index, key in enumerate(sorted(buckets), start=1):
            bucket = tuple(
                sorted(
                    buckets[key],
                    key=lambda edge: (int(edge.edge_type), int(edge.id)),
                )
            )
            representative = max(bucket, key=lambda edge: _edge_priority(edge.edge_type))
            bundled.append(
                BundledEdgeRecord(
                    id=BundledEdgeId(index),
                    source=representative.source,
                    target=representative.target,
                    edge_type=representative.edge_type,
                    bundle_count=len(bucket),
                    edge_ids=tuple(edge.id for edge in bucket),
                )
            )
        return tuple(bundled)


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


def _edge_priority(edge_type: EdgeType) -> int:
    if edge_type == EdgeType.EDGE_CALL:
        return 3
    if edge_type == EdgeType.EDGE_USAGE:
        return 2
    if edge_type == EdgeType.EDGE_MEMBER:
        return 1
    return 0
