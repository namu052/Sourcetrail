"""Phase 2 MVP integration coverage against the sample Django fixture."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from sourcetrail_remake.db.reader import DatabaseReader
from sourcetrail_remake.db.writer import DatabaseWriter
from sourcetrail_remake.indexer.relation_query import RelationQuery
from sourcetrail_remake.indexer.service import IndexerService
from sourcetrail_remake.ui.editor.decorator import DecorationKind
from sourcetrail_remake.ui.editor.semantic import SemanticDecorationService


@pytest.mark.integration
def test_phase2_mvp_indexes_django_fixture_and_runs_semantic_decoration() -> None:
    project_root = Path("tests/fixtures/sample-django").resolve()
    temp_root = Path(".tmp-test-artifacts").resolve()
    temp_root.mkdir(parents=True, exist_ok=True)
    db_path = temp_root / f"phase2-django-{uuid4().hex}.srctrldb"
    progress_events: list[tuple[int, int]] = []
    try:
        service = IndexerService(project_root, "shallow")
        with DatabaseWriter(db_path) as writer:
            result = service.index(
                writer,
                lambda current, total: progress_events.append((current, total)),
            )

        reader = DatabaseReader(db_path)
        profile_id = reader.find_symbol_id("blog.models.UserProfile")
        payload_id = reader.find_symbol_id("blog.views.build_payload")
        assert result.files_indexed == 3
        assert profile_id is not None
        assert payload_id is not None
        assert progress_events[-1] == (3, 3)

        relations = RelationQuery(db_path).get_references(profile_id)
        assert any("UserProfile" in occurrence.label for occurrence in relations)

        decorations = SemanticDecorationService.create_default().analyze_text(
            "from deprecated import deprecated\n"
            "@deprecated\n"
            "def old_view():\n"
            "    pass\n"
            "def view(request):\n"
            "    unused_context = {}\n"
            "    return missing_response(request)\n"
        )
        assert {decoration.kind for decoration in decorations} >= {
            DecorationKind.UNUSED_VARIABLE,
            DecorationKind.UNDEFINED_REFERENCE,
            DecorationKind.DEPRECATED,
        }
    finally:
        try:
            db_path.unlink(missing_ok=True)
        except PermissionError:
            pass
