"""Project clip storage for temporary code snippets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import NewType
from uuid import uuid4

ClipId = NewType("ClipId", str)


@dataclass(frozen=True, slots=True)
class Clip:
    """A saved code snippet with lightweight metadata."""

    id: ClipId
    title: str
    text: str
    tags: tuple[str, ...]
    note: str
    created_at: str


class ClipStore:
    """JSON-backed clip collection stored per project."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._clips = self._load()

    def add(
        self,
        title: str,
        text: str,
        *,
        tags: tuple[str, ...] = (),
        note: str = "",
    ) -> ClipId:
        """Add a clip and return its generated id."""
        clip_id = ClipId(uuid4().hex)
        title_text = title.strip() or self._fallback_title(text)
        clip = Clip(
            id=clip_id,
            title=title_text,
            text=text,
            tags=tuple(tag.strip() for tag in tags if tag.strip()),
            note=note.strip(),
            created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        self._clips[clip_id] = clip
        self._save()
        return clip_id

    def list(self) -> list[Clip]:
        """Return clips sorted by newest first."""
        return sorted(
            self._clips.values(),
            key=lambda clip: (clip.created_at, clip.id),
            reverse=True,
        )

    def get(self, clip_id: ClipId) -> Clip | None:
        """Return one clip by id."""
        return self._clips.get(clip_id)

    def remove(self, clip_id: ClipId) -> None:
        """Remove a clip if it exists."""
        self._clips.pop(clip_id, None)
        self._save()

    def _load(self) -> dict[ClipId, Clip]:
        if not self.path.exists():
            return {}
        data = json.loads(self.path.read_text(encoding="utf-8"))
        clips: dict[ClipId, Clip] = {}
        for raw in data.get("clips", []):
            clip = Clip(
                id=ClipId(str(raw["id"])),
                title=str(raw["title"]),
                text=str(raw["text"]),
                tags=tuple(str(tag) for tag in raw.get("tags", [])),
                note=str(raw.get("note", "")),
                created_at=str(raw["created_at"]),
            )
            clips[clip.id] = clip
        return clips

    def _save(self) -> None:
        payload = {
            "version": 1,
            "clips": [
                {**asdict(clip), "id": str(clip.id), "tags": list(clip.tags)}
                for clip in self.list()
            ],
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _fallback_title(self, text: str) -> str:
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
        return first_line[:60] if first_line else "Untitled Clip"
