"""Fast per-file symbol outline extracted from Python source."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path
from typing import Any

import parso

from sourcetrail_remake.core.types import AccessKind, NodeType


class SymbolSortMode(StrEnum):
    """Supported ordering modes for the Symbol Window."""

    DECLARATION = "declaration"
    ALPHABETICAL = "alphabetical"


class SymbolIconKind(StrEnum):
    """Presentation-neutral icon keys used by the UI model."""

    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    FIELD = "field"
    PROPERTY = "property"
    STATIC = "static"
    VARIABLE = "variable"


@dataclass(frozen=True, slots=True)
class SymbolOutlineItem:
    """A symbol entry shown in the current-file outline."""

    name: str
    qualified_name: str
    node_type: NodeType
    line: int
    column: int
    end_line: int
    parent_qualified_name: str | None = None
    access: AccessKind = AccessKind.ACCESS_PUBLIC
    icon_kind: SymbolIconKind = SymbolIconKind.VARIABLE
    children: tuple[SymbolOutlineItem, ...] = ()

    @property
    def indented_name(self) -> str:
        depth = max(self.qualified_name.count(".") - 1, 0)
        return f"{'  ' * depth}{self.name}"


@dataclass(frozen=True, slots=True)
class _CacheEntry:
    mtime_ns: int
    size: int
    symbols: tuple[SymbolOutlineItem, ...]


class SymbolIndex:
    """Memory cache for file outlines used by the Symbol Window."""

    def __init__(self) -> None:
        self._cache: dict[Path, _CacheEntry] = {}

    def load_file(
        self,
        file: str | Path,
        *,
        sort_mode: SymbolSortMode = SymbolSortMode.DECLARATION,
        force: bool = False,
    ) -> tuple[SymbolOutlineItem, ...]:
        """Return a cached outline for a file, refreshing if the file changed."""
        path = Path(file).resolve()
        stat = path.stat()
        cached = self._cache.get(path)
        if (
            not force
            and cached is not None
            and cached.mtime_ns == stat.st_mtime_ns
            and cached.size == stat.st_size
        ):
            return self._sort_symbols(cached.symbols, sort_mode)

        source = path.read_text(encoding="utf-8")
        module: Any = parso.parse(source)  # type: ignore[no-untyped-call]
        module_name = path.stem if path.stem != "__init__" else path.parent.name
        symbols = tuple(self._walk_scope(module, module_name=module_name, owners=()))
        self._cache[path] = _CacheEntry(stat.st_mtime_ns, stat.st_size, symbols)
        return self._sort_symbols(symbols, sort_mode)

    def refresh_file(
        self,
        file: str | Path,
        *,
        sort_mode: SymbolSortMode = SymbolSortMode.DECLARATION,
    ) -> tuple[SymbolOutlineItem, ...]:
        """Force a re-parse for a file."""
        return self.load_file(file, sort_mode=sort_mode, force=True)

    def invalidate(self, file: str | Path) -> None:
        """Drop a cached outline."""
        self._cache.pop(Path(file).resolve(), None)

    def is_cached(self, file: str | Path) -> bool:
        """Return whether a resolved file currently has a cache entry."""
        return Path(file).resolve() in self._cache

    def _walk_scope(
        self,
        node: Any,
        *,
        module_name: str,
        owners: tuple[SymbolOutlineItem, ...],
    ) -> list[SymbolOutlineItem]:
        symbols: list[SymbolOutlineItem] = []
        for child in getattr(node, "children", []):
            child_type = getattr(child, "type", None)
            if child_type == "decorated":
                symbols.extend(
                    self._walk_decorated(child, module_name=module_name, owners=owners)
                )
            elif child_type == "classdef":
                symbols.append(self._build_class(child, module_name=module_name, owners=owners))
            elif child_type == "funcdef":
                symbols.append(
                    self._build_function(
                        child,
                        module_name=module_name,
                        owners=owners,
                        decorators=(),
                    )
                )
            elif child_type == "simple_stmt":
                assignment = self._build_assignment(child, module_name=module_name, owners=owners)
                if assignment is not None:
                    symbols.append(assignment)
        return symbols

    def _walk_decorated(
        self,
        node: Any,
        *,
        module_name: str,
        owners: tuple[SymbolOutlineItem, ...],
    ) -> list[SymbolOutlineItem]:
        children = list(getattr(node, "children", []))
        decorators = tuple(
            self._decorator_name(child)
            for child in children
            if getattr(child, "type", None) == "decorator"
        )
        decorated = children[-1] if children else None
        if decorated is None:
            return []
        if getattr(decorated, "type", None) == "funcdef":
            return [
                self._build_function(
                    decorated,
                    module_name=module_name,
                    owners=owners,
                    decorators=decorators,
                )
            ]
        if getattr(decorated, "type", None) == "classdef":
            return [self._build_class(decorated, module_name=module_name, owners=owners)]
        return self._walk_scope(decorated, module_name=module_name, owners=owners)

    def _build_class(
        self,
        node: Any,
        *,
        module_name: str,
        owners: tuple[SymbolOutlineItem, ...],
    ) -> SymbolOutlineItem:
        name_node = node.name
        qualified_name = self._qualified_name(module_name, owners, str(name_node.value))
        shell = SymbolOutlineItem(
            name=str(name_node.value),
            qualified_name=qualified_name,
            node_type=NodeType.NODE_CLASS,
            line=int(name_node.start_pos[0]),
            column=int(name_node.start_pos[1]),
            end_line=int(node.end_pos[0]),
            parent_qualified_name=owners[-1].qualified_name if owners else None,
            access=self._access_for_name(str(name_node.value)),
            icon_kind=SymbolIconKind.CLASS,
        )
        children = tuple(
            self._walk_scope(node.children[-1], module_name=module_name, owners=(*owners, shell))
        )
        return replace(shell, children=children)

    def _build_function(
        self,
        node: Any,
        *,
        module_name: str,
        owners: tuple[SymbolOutlineItem, ...],
        decorators: tuple[str, ...],
    ) -> SymbolOutlineItem:
        name_node = node.name
        name = str(name_node.value)
        in_class = bool(owners and owners[-1].node_type == NodeType.NODE_CLASS)
        icon_kind = self._function_icon_kind(decorators, in_class)
        node_type = NodeType.NODE_FIELD if icon_kind == SymbolIconKind.PROPERTY else (
            NodeType.NODE_METHOD if in_class else NodeType.NODE_FUNCTION
        )
        qualified_name = self._qualified_name(module_name, owners, name)
        shell = SymbolOutlineItem(
            name=name,
            qualified_name=qualified_name,
            node_type=node_type,
            line=int(name_node.start_pos[0]),
            column=int(name_node.start_pos[1]),
            end_line=int(node.end_pos[0]),
            parent_qualified_name=owners[-1].qualified_name if owners else None,
            access=self._access_for_name(name),
            icon_kind=icon_kind,
        )
        children = tuple(
            self._walk_scope(node.children[-1], module_name=module_name, owners=(*owners, shell))
        )
        return replace(shell, children=children)

    def _build_assignment(
        self,
        node: Any,
        *,
        module_name: str,
        owners: tuple[SymbolOutlineItem, ...],
    ) -> SymbolOutlineItem | None:
        target = self._assignment_target(node)
        if target is None:
            return None
        name, line, column = target
        qualified_name = self._qualified_name(module_name, owners, name)
        in_class = bool(owners and owners[-1].node_type == NodeType.NODE_CLASS)
        return SymbolOutlineItem(
            name=name,
            qualified_name=qualified_name,
            node_type=NodeType.NODE_FIELD if in_class else NodeType.NODE_GLOBAL_VARIABLE,
            line=line,
            column=column,
            end_line=line,
            parent_qualified_name=owners[-1].qualified_name if owners else None,
            access=self._access_for_name(name),
            icon_kind=SymbolIconKind.FIELD if in_class else SymbolIconKind.VARIABLE,
        )

    def _assignment_target(self, node: Any) -> tuple[str, int, int] | None:
        children = list(getattr(node, "children", []))
        if not children:
            return None
        statement = children[0]
        if getattr(statement, "type", None) != "expr_stmt":
            return None
        statement_children = list(getattr(statement, "children", []))
        if not statement_children:
            return None
        target = statement_children[0]
        if getattr(target, "type", None) == "name":
            return str(target.value), int(target.start_pos[0]), int(target.start_pos[1])
        return None

    def _decorator_name(self, node: Any) -> str:
        values: list[str] = []
        self._collect_leaf_values(node, values)
        return "".join(value for value in values if value not in {"@", "\n"}).strip()

    def _collect_leaf_values(self, node: Any, values: list[str]) -> None:
        children = getattr(node, "children", None)
        if children is None:
            value = getattr(node, "value", None)
            if value is not None:
                values.append(str(value))
            return
        for child in children:
            self._collect_leaf_values(child, values)

    def _function_icon_kind(
        self,
        decorators: tuple[str, ...],
        in_class: bool,
    ) -> SymbolIconKind:
        if any(name.endswith("property") for name in decorators):
            return SymbolIconKind.PROPERTY
        if any(
            name.endswith("staticmethod") or name.endswith("classmethod") for name in decorators
        ):
            return SymbolIconKind.STATIC
        return SymbolIconKind.METHOD if in_class else SymbolIconKind.FUNCTION

    def _access_for_name(self, name: str) -> AccessKind:
        if name.startswith("__") and not name.endswith("__"):
            return AccessKind.ACCESS_PRIVATE
        if name.startswith("_") and not name.startswith("__"):
            return AccessKind.ACCESS_PROTECTED
        return AccessKind.ACCESS_PUBLIC

    def _qualified_name(
        self,
        module_name: str,
        owners: tuple[SymbolOutlineItem, ...],
        name: str,
    ) -> str:
        if owners:
            return f"{owners[-1].qualified_name}.{name}"
        return f"{module_name}.{name}"

    def _sort_symbols(
        self,
        symbols: tuple[SymbolOutlineItem, ...],
        sort_mode: SymbolSortMode,
    ) -> tuple[SymbolOutlineItem, ...]:
        def sort_children(item: SymbolOutlineItem) -> SymbolOutlineItem:
            return replace(item, children=self._sort_symbols(item.children, sort_mode))

        items = tuple(sort_children(item) for item in symbols)
        if sort_mode == SymbolSortMode.ALPHABETICAL:
            return tuple(sorted(items, key=lambda item: (item.name.lower(), item.line)))
        return tuple(sorted(items, key=lambda item: item.line))
