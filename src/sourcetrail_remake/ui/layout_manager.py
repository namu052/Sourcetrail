"""Dock layout persistence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from PyQt6.QtCore import QByteArray, QSettings, Qt
from PyQt6.QtWidgets import QDockWidget, QMainWindow, QSplitter, QWidget


class LayoutPreset(StrEnum):
    """Built-in dock layout presets."""

    READING = "reading"
    GRAPH_CENTRIC = "graph_centric"
    REFACTOR = "refactor"
    CUSTOM = "custom"
    DEFAULT = "default"
    SOURCE_INSIGHT = "source_insight"
    WIDE = "wide"


@dataclass(frozen=True, slots=True)
class DockPlacement:
    """Dock object placement for a preset."""

    object_name: str
    area: Qt.DockWidgetArea
    visible: bool = True


@dataclass(frozen=True, slots=True)
class LayoutPresetSpec:
    """Named dock placement preset."""

    name: LayoutPreset
    placements: tuple[DockPlacement, ...]
    dock_sizes: tuple[int, ...] = ()
    secondary_editor_visible: bool = False
    central_sizes: tuple[int, ...] = ()


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
            geometry=_bytes_value(window.saveGeometry()),
            state=_bytes_value(window.saveState()),
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

    def apply_preset(self, window: QMainWindow, preset: LayoutPreset) -> None:
        for placement in PRESET_SPECS[preset].placements:
            dock = window.findChild(QDockWidget, placement.object_name)
            if dock is not None:
                window.addDockWidget(placement.area, dock)
                dock.setVisible(placement.visible)
        self._resize_matching_docks(window, PRESET_SPECS[preset])
        self._apply_central_editor_split(window, PRESET_SPECS[preset])

    def load(self, *, name: str = "current") -> LayoutSnapshot:
        self.settings.beginGroup(self.group)
        self.settings.beginGroup(name)
        geometry = _bytes_value(self.settings.value("geometry", b""))
        state = _bytes_value(self.settings.value("state", b""))
        self.settings.endGroup()
        self.settings.endGroup()
        return LayoutSnapshot(geometry=geometry, state=state)

    def _resize_matching_docks(self, window: QMainWindow, spec: LayoutPresetSpec) -> None:
        if not spec.dock_sizes:
            return
        docks = [
            dock
            for placement in spec.placements
            if (dock := window.findChild(QDockWidget, placement.object_name)) is not None
        ]
        if len(docks) != len(spec.dock_sizes):
            return
        window.resizeDocks(docks, list(spec.dock_sizes), Qt.Orientation.Horizontal)

    def _apply_central_editor_split(self, window: QMainWindow, spec: LayoutPresetSpec) -> None:
        secondary_editor = window.findChild(QWidget, "refactor-secondary-editor")
        if secondary_editor is not None:
            secondary_editor.setVisible(spec.secondary_editor_visible)
        splitter = window.findChild(QSplitter, "central-editor-splitter")
        if splitter is not None and spec.central_sizes:
            splitter.setSizes(list(spec.central_sizes))


def _bytes_value(value: object) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bytearray):
        return bytes(value)
    if isinstance(value, QByteArray):
        return bytes(value.data())
    return b""


PRESET_SPECS: dict[LayoutPreset, LayoutPresetSpec] = {
    LayoutPreset.READING: LayoutPresetSpec(
        name=LayoutPreset.READING,
        placements=(
            DockPlacement("graph-overview-dock", Qt.DockWidgetArea.LeftDockWidgetArea),
            DockPlacement("context-window-dock", Qt.DockWidgetArea.RightDockWidgetArea),
            DockPlacement("symbol-window-dock", Qt.DockWidgetArea.RightDockWidgetArea),
            DockPlacement("relation-window-dock", Qt.DockWidgetArea.RightDockWidgetArea),
            DockPlacement("graph-selection-dock", Qt.DockWidgetArea.RightDockWidgetArea),
            DockPlacement("graph-log-dock", Qt.DockWidgetArea.BottomDockWidgetArea, visible=False),
        ),
        dock_sizes=(220, 360, 360, 360, 280, 120),
    ),
    LayoutPreset.GRAPH_CENTRIC: LayoutPresetSpec(
        name=LayoutPreset.GRAPH_CENTRIC,
        placements=(
            DockPlacement("graph-overview-dock", Qt.DockWidgetArea.LeftDockWidgetArea, visible=True),
            DockPlacement(
                "graph-selection-dock",
                Qt.DockWidgetArea.RightDockWidgetArea,
                visible=True,
            ),
            DockPlacement("relation-window-dock", Qt.DockWidgetArea.RightDockWidgetArea, True),
            DockPlacement("context-window-dock", Qt.DockWidgetArea.BottomDockWidgetArea, False),
            DockPlacement("symbol-window-dock", Qt.DockWidgetArea.BottomDockWidgetArea, False),
            DockPlacement("graph-log-dock", Qt.DockWidgetArea.BottomDockWidgetArea, visible=True),
        ),
        dock_sizes=(180, 260, 320, 120, 120, 220),
    ),
    LayoutPreset.REFACTOR: LayoutPresetSpec(
        name=LayoutPreset.REFACTOR,
        placements=(
            DockPlacement("graph-overview-dock", Qt.DockWidgetArea.LeftDockWidgetArea, False),
            DockPlacement("graph-selection-dock", Qt.DockWidgetArea.RightDockWidgetArea, True),
            DockPlacement("relation-window-dock", Qt.DockWidgetArea.RightDockWidgetArea, True),
            DockPlacement("context-window-dock", Qt.DockWidgetArea.BottomDockWidgetArea, True),
            DockPlacement("symbol-window-dock", Qt.DockWidgetArea.LeftDockWidgetArea, True),
            DockPlacement("graph-log-dock", Qt.DockWidgetArea.BottomDockWidgetArea, False),
        ),
        dock_sizes=(120, 280, 320, 260, 260, 120),
        secondary_editor_visible=True,
        central_sizes=(1, 1),
    ),
    LayoutPreset.CUSTOM: LayoutPresetSpec(
        name=LayoutPreset.CUSTOM,
        placements=(),
    ),
    LayoutPreset.DEFAULT: LayoutPresetSpec(
        name=LayoutPreset.DEFAULT,
        placements=(
            DockPlacement("graph-overview-dock", Qt.DockWidgetArea.LeftDockWidgetArea),
            DockPlacement("graph-selection-dock", Qt.DockWidgetArea.RightDockWidgetArea),
            DockPlacement("graph-log-dock", Qt.DockWidgetArea.BottomDockWidgetArea),
        ),
    ),
    LayoutPreset.SOURCE_INSIGHT: LayoutPresetSpec(
        name=LayoutPreset.SOURCE_INSIGHT,
        placements=(
            DockPlacement("context-window-dock", Qt.DockWidgetArea.LeftDockWidgetArea),
            DockPlacement("symbol-window-dock", Qt.DockWidgetArea.RightDockWidgetArea),
            DockPlacement("relation-window-dock", Qt.DockWidgetArea.RightDockWidgetArea),
        ),
    ),
    LayoutPreset.WIDE: LayoutPresetSpec(
        name=LayoutPreset.WIDE,
        placements=(
            DockPlacement("context-window-dock", Qt.DockWidgetArea.BottomDockWidgetArea),
            DockPlacement("symbol-window-dock", Qt.DockWidgetArea.LeftDockWidgetArea),
            DockPlacement("relation-window-dock", Qt.DockWidgetArea.RightDockWidgetArea),
            DockPlacement("graph-log-dock", Qt.DockWidgetArea.BottomDockWidgetArea),
        ),
    ),
}
