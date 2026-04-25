"""Small Jedi wrapper for Phase 0 PoCs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import jedi


@dataclass(slots=True, frozen=True)
class ResolvedSymbol:
    """Simplified symbol definition returned by Jedi."""

    name: str
    symbol_type: str
    line: int
    column: int


class JediResolver:
    """Wrap common Jedi calls behind a single module boundary."""

    def __init__(self, project_root: Path):
        self.project = jedi.Project(path=str(project_root), sys_path=[str(project_root)])

    def collect_definitions(self, source: str, path: Path) -> list[ResolvedSymbol]:
        script = jedi.Script(code=source, path=str(path), project=self.project)
        definitions: list[ResolvedSymbol] = []
        for name in script.get_names(all_scopes=True, definitions=True, references=False):
            if name.type == "keyword" or name.line is None or name.column is None:
                continue
            definitions.append(
                ResolvedSymbol(
                    name=name.name,
                    symbol_type=name.type,
                    line=name.line,
                    column=name.column,
                )
            )
        return definitions
