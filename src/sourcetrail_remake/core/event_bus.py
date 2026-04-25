"""Qt signal hub used to decouple UI panels and services."""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal


class EventBus(QObject):
    """Central signal bus for the Phase 0 shell."""

    symbol_selected = pyqtSignal(object)
    symbol_hovered = pyqtSignal(object)
    symbol_deselected = pyqtSignal()

    file_opened = pyqtSignal(object)
    file_closed = pyqtSignal(object)
    cursor_moved = pyqtSignal(object, int, int)

    indexing_started = pyqtSignal(object)
    indexing_progress = pyqtSignal(int, int)
    indexing_completed = pyqtSignal(object)
    indexing_failed = pyqtSignal(str)

    relation_lock_toggled = pyqtSignal(int, bool)
    context_follow_toggled = pyqtSignal(bool)
    layout_changed = pyqtSignal(str)

    bookmark_added = pyqtSignal(object)
    clip_added = pyqtSignal(str)
