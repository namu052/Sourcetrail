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
