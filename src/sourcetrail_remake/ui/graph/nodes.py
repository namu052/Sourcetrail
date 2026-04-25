"""Graph node renderer primitives."""

from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsObject


class ClassContainerItem(QGraphicsObject):
    """Rounded container used for class-like graph nodes."""

    def __init__(self, name: str, member_count: int) -> None:
        super().__init__()
        self.name = name
        self.member_count = member_count
        self._selected = False
        self._bounds = QRectF(0, 0, 240, 132)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

    def boundingRect(self) -> QRectF:
        return self._bounds

    def set_selected_state(self, selected: bool) -> None:
        self._selected = selected
        self.update()

    def paint(
        self,
        painter: QPainter,
        option: object,
        widget: object | None = None,
    ) -> None:
        del option, widget
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        fill = QColor("#fff7d6") if self._selected else QColor("#fffdf7")
        border = QColor("#f59e0b") if self._selected else QColor("#1f2937")
        painter.setBrush(QBrush(fill))
        painter.setPen(QPen(border, 3 if self._selected else 2))
        painter.drawRoundedRect(self._bounds, 14, 14)

        painter.setBrush(QBrush(QColor("#2563eb")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(14, 14, 18, 18)

        painter.setPen(QColor("#111827"))
        painter.drawText(QRectF(42, 10, 150, 28), Qt.AlignmentFlag.AlignVCenter, self.name)

        badge_rect = QRectF(self._bounds.width() - 76, 14, 56, 22)
        painter.setBrush(QBrush(QColor("#dbeafe")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(badge_rect, 11, 11)
        painter.setPen(QColor("#1d4ed8"))
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, str(self.member_count))

        painter.setPen(QColor("#64748b"))
        painter.drawLine(14, 48, int(self._bounds.width()) - 14, 48)
        painter.drawText(
            QRectF(18, 60, self._bounds.width() - 36, 24),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "Class Container",
        )


class NodeRenderer:
    """Factory for graph node items."""

    @staticmethod
    def create_class_container(name: str, member_count: int) -> QGraphicsItem:
        return ClassContainerItem(name, member_count)
