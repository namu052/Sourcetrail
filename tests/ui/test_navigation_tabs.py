"""Qt coverage for the Week 7 symbol tab bar."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.core.event_bus import EventBus
from sourcetrail_remake.core.types import EdgeType, NodeType, SourceLocation
from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.ui.main_window import create_main_window
from sourcetrail_remake.ui.navigation.tabs import SymbolTabBar


@pytest.mark.ui
def test_symbol_tab_bar_tracks_multiple_symbols(qtbot) -> None:
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"navigation-tabs-{uuid4().hex}.srctrldb"
    try:
        with DatabaseWriter(db_path) as writer:
            writer.initialize_schema()
            file_id = writer.record_file(
                Path("tests/fixtures/sample-minimal/session_manager.py").resolve(),
                (
                    "class SessionManager:\n"
                    "    def cleanup_expired(self) -> None:\n"
                    "        notify()\n"
                ),
            )
            class_id = writer.record_symbol(
                "SessionManager",
                NodeType.NODE_CLASS,
                file_id,
                SourceLocation.from_name(line=1, column=6, name="SessionManager"),
                qualified_name="session_manager.SessionManager",
            )
            method_id = writer.record_symbol(
                "cleanup_expired",
                NodeType.NODE_METHOD,
                file_id,
                SourceLocation.from_name(line=2, column=8, name="cleanup_expired"),
                qualified_name="session_manager.SessionManager.cleanup_expired",
            )
            writer.record_edge(class_id, method_id, EdgeType.EDGE_MEMBER, file=file_id)

        reader = DatabaseReader(db_path)
        window = create_main_window(EventBus(), reader=reader, initial_symbol_id=class_id)
        qtbot.addWidget(window)
        window.show()

        tabs = window.findChild(SymbolTabBar, "symbol-tab-bar")
        assert tabs is not None
        assert tabs.count() == 1
        assert tabs.tabText(0) == "SessionManager"

        window.focus_symbol(method_id)

        assert tabs.count() == 2
        assert tabs.tabText(tabs.currentIndex()) == "cleanup_expired"
        assert "cleanup_expired" in window.selection_fqn_label.text()
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
