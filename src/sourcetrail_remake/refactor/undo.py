"""Undo journal for file-based refactor operations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class UndoEntry:
    """One backed-up file before a refactor write."""

    path: Path
    old_text: str


@dataclass(frozen=True, slots=True)
class UndoRecord:
    """Persisted undo transaction metadata."""

    token: str
    journal_path: Path
    entries: tuple[UndoEntry, ...]


class UndoJournal:
    """Store and restore refactor file backups under .srm-undo."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.undo_dir = self.project_root / ".srm-undo"

    def backup(self, entries: tuple[UndoEntry, ...]) -> UndoRecord:
        self.undo_dir.mkdir(exist_ok=True)
        token = datetime.now(UTC).strftime("%Y%m%dT%H%M%S") + f"-{uuid4().hex[:8]}"
        journal_path = self.undo_dir / f"{token}.json"
        payload = {
            "token": token,
            "created_at": datetime.now(UTC).isoformat(),
            "entries": [
                {
                    "path": entry.path.resolve().relative_to(self.project_root).as_posix(),
                    "old_text": entry.old_text,
                }
                for entry in entries
            ],
        }
        journal_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return UndoRecord(token=token, journal_path=journal_path, entries=entries)

    def restore(self, record: UndoRecord) -> None:
        for entry in record.entries:
            entry.path.write_text(entry.old_text, encoding="utf-8")

    def load(self, token: str) -> UndoRecord:
        journal_path = self.undo_dir / f"{token}.json"
        payload = json.loads(journal_path.read_text(encoding="utf-8"))
        entries = tuple(
            UndoEntry(path=self.project_root / item["path"], old_text=str(item["old_text"]))
            for item in payload["entries"]
        )
        return UndoRecord(token=str(payload["token"]), journal_path=journal_path, entries=entries)
