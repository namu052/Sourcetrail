"""Week 22 rename regression coverage for representative Python projects."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from sourcetrail_remake.core.types import NodeId, NodeType, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.refactor.rename import RopeRenameService


@pytest.mark.integration
@pytest.mark.parametrize(
    (
        "fixture_name",
        "target_file",
        "symbol_name",
        "node_type",
        "line",
        "column",
        "new_name",
        "changed_file",
        "expected_text",
    ),
    [
        (
            "sample-django",
            "blog/models.py",
            "UserProfile",
            NodeType.NODE_CLASS,
            4,
            6,
            "AccountProfile",
            "blog/views.py",
            "profile: AccountProfile",
        ),
        (
            "sample-requests",
            "client.py",
            "fetch_status",
            NodeType.NODE_FUNCTION,
            4,
            4,
            "fetch_status_code",
            "api.py",
            "fetch_status_code(url)",
        ),
        (
            "sample-flask",
            "services.py",
            "get_health_payload",
            NodeType.NODE_FUNCTION,
            1,
            4,
            "build_health_payload",
            "app.py",
            "build_health_payload()",
        ),
    ],
)
def test_week22_rename_regressions_cover_common_framework_fixtures(
    tmp_path: Path,
    fixture_name: str,
    target_file: str,
    symbol_name: str,
    node_type: NodeType,
    line: int,
    column: int,
    new_name: str,
    changed_file: str,
    expected_text: str,
) -> None:
    source_root = Path(__file__).parents[1] / "fixtures" / fixture_name
    project_root = tmp_path / fixture_name
    shutil.copytree(source_root, project_root)
    target = project_root / target_file
    db_path = tmp_path / f"{fixture_name}.srctrldb"
    node_id = _record_symbol(db_path, project_root, target, symbol_name, node_type, line, column)
    before = {
        path.relative_to(project_root): path.read_text(encoding="utf-8")
        for path in project_root.rglob("*.py")
    }

    service = RopeRenameService(project_root, db_path)
    preview = service.preview(node_id, new_name)
    result = service.apply(preview)

    changed_text = (project_root / changed_file).read_text(encoding="utf-8")
    assert expected_text in changed_text
    assert target in preview.affected_files
    assert result.changed_files == preview.affected_files

    service.undo(result)
    after = {
        path.relative_to(project_root): path.read_text(encoding="utf-8")
        for path in project_root.rglob("*.py")
    }
    assert after == before


def _record_symbol(
    db_path: Path,
    project_root: Path,
    target: Path,
    name: str,
    node_type: NodeType,
    line: int,
    column: int,
) -> NodeId:
    with DatabaseWriter(db_path) as writer:
        writer.initialize()
        file_id = writer.record_file(target)
        for path in project_root.rglob("*.py"):
            if path != target:
                writer.record_file(path)
        return writer.record_symbol(
            name,
            node_type,
            file_id,
            SourceLocation.from_name(line=line, column=column, name=name),
            qualified_name=f"{target.stem}.{name}",
        )
