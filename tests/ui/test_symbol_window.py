"""UI coverage for the D51-D60 Symbol Window."""

from __future__ import annotations

from pathlib import Path

import pytest
from PyQt6.QtCore import Qt

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.indexer.symbol_index import SymbolIndex
from sourcetrail_remake.ui.panels.symbol_window import SymbolWindow


@pytest.mark.ui
def test_symbol_window_loads_current_file_outline(qtbot, tmp_path: Path) -> None:
    source = _write_source(tmp_path, "class Zebra:\n    def roam(self):\n        pass\n")
    event_bus = EventBus()
    window = SymbolWindow(event_bus, SymbolIndex())
    qtbot.addWidget(window)

    event_bus.file_opened.emit(str(source), 1)

    assert window.model.rowCount() == 1
    class_index = window.model.index(0, 0)
    assert class_index.data() == "Zebra"
    assert window.model.rowCount(class_index) == 1
    assert window.model.index(0, 0, class_index).data() == "roam"
    assert not window.model.index(0, 0).data(Qt.ItemDataRole.DecorationRole).isNull()


@pytest.mark.ui
def test_symbol_window_filters_and_sorts(qtbot, tmp_path: Path) -> None:
    source = _write_source(
        tmp_path,
        "def beta():\n    pass\n\ndef alpha():\n    pass\n",
    )
    event_bus = EventBus()
    window = SymbolWindow(event_bus, SymbolIndex())
    qtbot.addWidget(window)
    event_bus.file_opened.emit(str(source), 1)

    window.filter_edit.setText("alp")
    assert window.proxy_model.rowCount() == 1
    assert window.proxy_model.index(0, 0).data() == "alpha"

    window.filter_edit.clear()
    window.sort_combo.setCurrentIndex(1)
    assert window.proxy_model.index(0, 0).data() == "alpha"
    assert window.proxy_model.index(1, 0).data() == "beta"


@pytest.mark.ui
def test_symbol_window_double_click_emits_file_opened(qtbot, tmp_path: Path) -> None:
    source = _write_source(tmp_path, "def jump():\n    pass\n")
    event_bus = EventBus()
    window = SymbolWindow(event_bus, SymbolIndex())
    qtbot.addWidget(window)
    event_bus.file_opened.emit(str(source), 1)

    with qtbot.waitSignal(event_bus.file_opened) as signal:
        window._open_index(window.proxy_model.index(0, 0))

    assert signal.args == [str(source), 1]


@pytest.mark.ui
def test_symbol_window_reindexes_on_file_saved(qtbot, tmp_path: Path) -> None:
    source = _write_source(tmp_path, "def before():\n    pass\n")
    event_bus = EventBus()
    window = SymbolWindow(event_bus, SymbolIndex())
    qtbot.addWidget(window)
    event_bus.file_opened.emit(str(source), 1)
    assert window.proxy_model.index(0, 0).data() == "before"

    source.write_text("def after():\n    pass\n", encoding="utf-8")
    event_bus.file_saved.emit(str(source))

    assert window.proxy_model.index(0, 0).data() == "after"


@pytest.mark.ui
def test_symbol_window_shows_access_levels(qtbot, tmp_path: Path) -> None:
    source = _write_source(
        tmp_path,
        "\n".join(
            [
                "class Access:",
                "    def _protected(self):",
                "        pass",
                "    def __private(self):",
                "        pass",
                "",
            ]
        ),
    )
    event_bus = EventBus()
    window = SymbolWindow(event_bus, SymbolIndex())
    qtbot.addWidget(window)
    event_bus.file_opened.emit(str(source), 1)

    class_index = window.model.index(0, 0)
    protected = window.model.index(0, 2, class_index)
    private = window.model.index(1, 2, class_index)

    assert protected.data() == "protected"
    assert private.data() == "private"


def _write_source(tmp_path: Path, source: str) -> Path:
    path = tmp_path / "sample.py"
    path.write_text(source, encoding="utf-8")
    return path
