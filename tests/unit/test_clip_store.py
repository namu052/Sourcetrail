"""Unit coverage for Week 21 clip storage."""

from __future__ import annotations

import pytest

from sourcetrail_remake.core.clips import ClipStore


@pytest.mark.unit
def test_clip_store_adds_persists_and_removes(tmp_path) -> None:
    path = tmp_path / ".srm-clips"
    store = ClipStore(path)

    clip_id = store.add("Session cleanup", "def cleanup():\n    pass\n", tags=("TODO",))

    reloaded = ClipStore(path)
    clip = reloaded.get(clip_id)
    assert clip is not None
    assert clip.title == "Session cleanup"
    assert clip.tags == ("TODO",)

    reloaded.remove(clip_id)

    assert reloaded.list() == []


@pytest.mark.unit
def test_clip_store_exports_and_imports_json(tmp_path) -> None:
    source = ClipStore(tmp_path / "source.srm-clips")
    clip_id = source.add("Exported", "x = 1", tags=("TODO",), note="portable")
    export_path = tmp_path / "clips.json"

    source.export_json(export_path)

    target = ClipStore(tmp_path / "target.srm-clips")
    count = target.import_json(export_path)
    clip = target.get(clip_id)

    assert count == 1
    assert clip is not None
    assert clip.title == "Exported"
    assert clip.note == "portable"


@pytest.mark.unit
def test_clip_store_import_can_replace_existing_clips(tmp_path) -> None:
    source = ClipStore(tmp_path / "source.srm-clips")
    source.add("Incoming", "x = 1")
    export_path = tmp_path / "clips.json"
    source.export_json(export_path)

    target = ClipStore(tmp_path / "target.srm-clips")
    target.add("Existing", "y = 2")

    assert target.import_json(export_path, replace=True) == 1
    assert [clip.title for clip in target.list()] == ["Incoming"]
