"""Dock layout persistence helpers."""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QMainWindow


@dataclass(frozen=True, slots=True)
class LayoutSnapshot:
    """Serialized main-window layout payload."""

    geometry: bytes
    state: bytes

    @property
    def is_empty(self) -> bool:
        return not self.geometry and not self.state


class LayoutManager:
    """Save and restore QMainWindow geometry and dock state."""

    def __init__(self, settings: QSettings, *, group: str = "layout") -> None:
        self.settings = settings
        self.group = group

    def save(self, window: QMainWindow, *, name: str = "current") -> LayoutSnapshot:
        snapshot = LayoutSnapshot(
            geometry=bytes(window.saveGeometry()),
            state=bytes(window.saveState()),
        )
        self.settings.beginGroup(self.group)
        self.settings.beginGroup(name)
        self.settings.setValue("geometry", snapshot.geometry)
        self.settings.setValue("state", snapshot.state)
        self.settings.endGroup()
        self.settings.endGroup()
        self.settings.sync()
        return snapshot

    def restore(self, window: QMainWindow, *, name: str = "current") -> bool:
        snapshot = self.load(name=name)
        if snapshot.is_empty:
            return False
        geometry_restored = window.restoreGeometry(snapshot.geometry)
        state_restored = window.restoreState(snapshot.state)
        return bool(geometry_restored and state_restored)

    def load(self, *, name: str = "current") -> LayoutSnapshot:
        self.settings.beginGroup(self.group)
        self.settings.beginGroup(name)
        geometry = _bytes_value(self.settings.value("geometry", b""))
        state = _bytes_value(self.settings.value("state", b""))
        self.settings.endGroup()
        self.settings.endGroup()
        return LayoutSnapshot(geometry=geometry, state=state)


def _bytes_value(value: object) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if hasattr(value, "data"):
        data = value.data()
        return bytes(data)
    return b""
