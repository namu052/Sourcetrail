"""Tracking utilities for unresolved Python references."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sourcetrail_remake.core.types import EdgeType, FileId, NodeId, SourceLocation
from sourcetrail_remake.db.writer import DatabaseWriter


@dataclass(slots=True, frozen=True)
class UnsolvedSymbol:
    context_node: NodeId
    name: str
    node_id: NodeId


class UnsolvedSymbolTracker:
    """Deduplicate unresolved references and persist them with explicit nodes."""

    def __init__(self) -> None:
        self._entries: dict[tuple[int, str], UnsolvedSymbol] = {}

    @property
    def count(self) -> int:
        return len(self._entries)

    def register(
        self,
        writer: DatabaseWriter,
        *,
        context_node: NodeId,
        name: str,
        file: FileId,
        location: SourceLocation,
        edge_type: EdgeType = EdgeType.EDGE_USAGE,
        reason: str = "unresolved_reference",
        metadata: dict[str, Any] | None = None,
    ) -> NodeId:
        key = (int(context_node), name)
        payload = {"reason": reason, "context_node": int(context_node)}
        if metadata is not None:
            payload.update(metadata)
        node_id = writer.record_unsolved(
            context_node,
            name,
            file=file,
            location=location,
            metadata=payload,
        )
        if key not in self._entries:
            self._entries[key] = UnsolvedSymbol(context_node=context_node, name=name, node_id=node_id)
        writer.record_edge(context_node, node_id, edge_type, file=file, location=location)
        return node_id

    def snapshot(self) -> tuple[UnsolvedSymbol, ...]:
        return tuple(self._entries.values())
