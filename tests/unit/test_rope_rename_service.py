"""Unit tests for RopeRenameService smart rename flows."""

from __future__ import annotations

from pathlib import Path

import pytest

from sourcetrail_remake.core.types import NodeId, NodeType, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.refactor.rename import RopeRenameService


@pytest.mark.unit
@pytest.mark.parametrize(
    ("source", "name", "node_type", "line", "column", "new_name", "expected"),
    [
        (
            "value = 1\nprint(value)\n",
            "value",
            NodeType.NODE_GLOBAL_VARIABLE,
            1,
            0,
            "total",
            "total",
        ),
        (
            "def greet():\n    return 1\n\nanswer = greet()\n",
            "greet",
            NodeType.NODE_FUNCTION,
            1,
            4,
            "build_answer",
            "build_answer()",
        ),
        (
            "class Session:\n    pass\n\nitem = Session()\n",
            "Session",
            NodeType.NODE_CLASS,
            1,
            6,
            "UserSession",
            "UserSession()",
        ),
        (
            "import helpers\n\nvalue = helpers.make_value()\n",
            "helpers",
            NodeType.NODE_MODULE,
            1,
            7,
            "project_helpers",
            "project_helpers.make_value()",
        ),
    ],
)
def test_rope_rename_service_applies_symbol_kinds(
    tmp_path: Path,
    source: str,
    name: str,
    node_type: NodeType,
    line: int,
    column: int,
    new_name: str,
    expected: str,
) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    target = project_root / "module.py"
    target.write_text(source, encoding="utf-8")
    (project_root / "helpers.py").write_text("def make_value():\n    return 1\n", encoding="utf-8")
    db_path = tmp_path / "project.srctrldb"
    node_id = _record_symbol(db_path, target, name, node_type, line, column)
    reindexed: list[tuple[Path, ...]] = []

    service = RopeRenameService(project_root, db_path, reindex_callback=reindexed.append)
    preview = service.preview(node_id, new_name)
    result = service.apply(preview)

    assert expected in target.read_text(encoding="utf-8")
    assert result.changed_files == preview.affected_files
    assert reindexed == [preview.affected_files]

    service.undo(result)
    assert target.read_text(encoding="utf-8") == source


@pytest.mark.unit
def test_rope_rename_service_tracks_override_methods(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    target = project_root / "models.py"
    source = (
        "class Base:\n"
        "    def render(self):\n"
        "        return 'base'\n\n"
        "class Child(Base):\n"
        "    def render(self):\n"
        "        return 'child'\n\n"
        "value = Child().render()\n"
    )
    target.write_text(source, encoding="utf-8")
    db_path = tmp_path / "project.srctrldb"
    node_id = _record_symbol(db_path, target, "render", NodeType.NODE_METHOD, 2, 8)

    service = RopeRenameService(project_root, db_path)
    preview = service.preview(node_id, "draw")
    result = service.apply(preview)
    renamed = target.read_text(encoding="utf-8")

    assert "def draw(self)" in renamed
    assert "Child().draw()" in renamed
    assert "def render(self)" not in renamed

    service.undo(result)
    assert target.read_text(encoding="utf-8") == source


def _record_symbol(
    db_path: Path,
    target: Path,
    name: str,
    node_type: NodeType,
    line: int,
    column: int,
) -> NodeId:
    with DatabaseWriter(db_path) as writer:
        writer.initialize()
        file_id = writer.record_file(target)
        return writer.record_symbol(
            name,
            node_type,
            file_id,
            SourceLocation.from_name(line=line, column=column, name=name),
            qualified_name=f"module.{name}",
        )
