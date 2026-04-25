"""Shared domain types used by the Python rewrite."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Literal, NewType

NodeId = NewType("NodeId", int)
EdgeId = NewType("EdgeId", int)
FileId = NewType("FileId", int)
LocationId = NewType("LocationId", int)
ProjectId = NewType("ProjectId", int)
type PathLike = str | Path
type IndexingMode = Literal["shallow", "deep"]


class NodeType(IntEnum):
    NODE_SYMBOL = 1 << 0
    NODE_TYPE = 1 << 1
    NODE_BUILTIN_TYPE = 1 << 2
    NODE_MODULE = 1 << 3
    NODE_NAMESPACE = 1 << 4
    NODE_PACKAGE = 1 << 5
    NODE_STRUCT = 1 << 6
    NODE_CLASS = 1 << 7
    NODE_INTERFACE = 1 << 8
    NODE_ANNOTATION = 1 << 9
    NODE_GLOBAL_VARIABLE = 1 << 10
    NODE_FIELD = 1 << 11
    NODE_FUNCTION = 1 << 12
    NODE_METHOD = 1 << 13
    NODE_ENUM = 1 << 14
    NODE_ENUM_CONSTANT = 1 << 15
    NODE_TYPEDEF = 1 << 16
    NODE_TYPE_PARAMETER = 1 << 17
    NODE_FILE = 1 << 18
    NODE_MACRO = 1 << 19
    NODE_UNION = 1 << 20


class EdgeType(IntEnum):
    EDGE_UNDEFINED = 0
    EDGE_MEMBER = 1 << 0
    EDGE_TYPE_USAGE = 1 << 1
    EDGE_USAGE = 1 << 2
    EDGE_CALL = 1 << 3
    EDGE_INHERITANCE = 1 << 4
    EDGE_OVERRIDE = 1 << 5
    EDGE_TYPE_ARGUMENT = 1 << 6
    EDGE_TEMPLATE_SPECIALIZATION = 1 << 7
    EDGE_INCLUDE = 1 << 8
    EDGE_IMPORT = 1 << 9
    EDGE_BUNDLED_EDGES = 1 << 10
    EDGE_MACRO_USAGE = 1 << 11
    EDGE_ANNOTATION_USAGE = 1 << 12


class DefinitionKind(IntEnum):
    DEFINITION_NONE = 0
    DEFINITION_IMPLICIT = 1
    DEFINITION_EXPLICIT = 2


class SourceLocationType(IntEnum):
    LOCATION_TOKEN = 0
    LOCATION_SCOPE = 1
    LOCATION_QUALIFIER = 2
    LOCATION_LOCAL_SYMBOL = 3
    LOCATION_SIGNATURE = 4
    LOCATION_COMMENT = 5
    LOCATION_ERROR = 6
    LOCATION_FULLTEXT_SEARCH = 7
    LOCATION_SCREEN_SEARCH = 8
    LOCATION_UNSOLVED = 9


class AccessKind(IntEnum):
    ACCESS_NONE = 0
    ACCESS_PUBLIC = 1
    ACCESS_PROTECTED = 2
    ACCESS_PRIVATE = 3
    ACCESS_DEFAULT = 4
    ACCESS_TEMPLATE_PARAMETER = 5
    ACCESS_TYPE_PARAMETER = 6


@dataclass(slots=True, frozen=True)
class SourceLocation:
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    type: SourceLocationType = SourceLocationType.LOCATION_TOKEN

    @classmethod
    def from_name(
        cls,
        *,
        line: int,
        column: int,
        name: str,
        location_type: SourceLocationType = SourceLocationType.LOCATION_TOKEN,
    ) -> SourceLocation:
        return cls(
            start_line=line,
            start_column=column,
            end_line=line,
            end_column=column + len(name),
            type=location_type,
        )


@dataclass(slots=True, frozen=True)
class ParsedSymbol:
    path: Path
    name: str
    qualified_name: str
    node_type: NodeType
    location: SourceLocation
    scope_end_line: int
    scope_end_column: int
    parent_qualified_name: str | None = None
    access: AccessKind | None = None

    def contains(self, *, line: int, column: int) -> bool:
        starts_before = (line, column) >= (self.location.start_line, self.location.start_column)
        ends_after = (line, column) < (self.scope_end_line, self.scope_end_column)
        return starts_before and ends_after


@dataclass(slots=True, frozen=True)
class ParsedModule:
    path: Path
    source: str
    symbols: tuple[ParsedSymbol, ...]
    keyword_argument_labels: frozenset[tuple[int, int]]


@dataclass(slots=True, frozen=True)
class NameOccurrence:
    path: Path
    name: str
    symbol_type: str
    location: SourceLocation
    is_definition: bool
    qualified_name: str | None = None


@dataclass(slots=True, frozen=True)
class ResolvedTarget:
    name: str
    symbol_type: str
    qualified_name: str | None
    path: Path | None
    line: int | None
    column: int | None
    is_builtin: bool = False


@dataclass(slots=True, frozen=True)
class DatabaseSummary:
    files: int
    symbols: int
    edges: int
    locations: int
    occurrences: int
    unsolved: int


@dataclass(slots=True, frozen=True)
class GraphNodeRecord:
    id: NodeId
    serialized_name: str
    display_name: str
    node_type: NodeType
    member_count: int
    is_unsolved: bool = False
    parent_id: NodeId | None = None


@dataclass(slots=True, frozen=True)
class GraphEdgeRecord:
    id: EdgeId
    source: NodeId
    target: NodeId
    edge_type: EdgeType


@dataclass(slots=True, frozen=True)
class GraphNeighborhood:
    root_id: NodeId
    depth: int
    nodes: tuple[GraphNodeRecord, ...]
    edges: tuple[GraphEdgeRecord, ...]


@dataclass(slots=True, frozen=True)
class IndexResult:
    project_root: Path
    mode: IndexingMode
    files_indexed: int
    symbols_recorded: int
    edges_recorded: int
    unsolved_symbols: int
    external_symbols: int
    locations_recorded: int
    duration_seconds: float
