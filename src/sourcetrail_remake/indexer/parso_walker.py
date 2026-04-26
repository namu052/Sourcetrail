"""Parso-backed AST walker for extracting project symbols."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import parso

from sourcetrail_remake.core.types import (
    NodeType,
    ParsedModule,
    ParsedSymbol,
    SourceLocation,
)


class ParsoWalker:
    """Extract module, class, function, and field-like symbols from Python files."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()

    def parse_module(self, path: Path) -> ParsedModule:
        resolved_path = Path(path).resolve()
        source = resolved_path.read_text(encoding="utf-8")
        module: Any = parso.parse(source)  # type: ignore[no-untyped-call]
        symbols: list[ParsedSymbol] = []
        keyword_argument_labels: set[tuple[int, int]] = set()
        module_name = self._module_name(resolved_path)
        self._walk_children(
            module.children, module_path=resolved_path, module_name=module_name, symbols=symbols
        )
        self._collect_keyword_argument_labels(module, keyword_argument_labels)
        return ParsedModule(
            path=resolved_path,
            source=source,
            symbols=tuple(symbols),
            keyword_argument_labels=frozenset(keyword_argument_labels),
        )

    def walk_project(self, paths: list[Path]) -> list[ParsedModule]:
        return [self.parse_module(path) for path in paths]

    def _walk_children(
        self,
        children: list[Any],
        *,
        module_path: Path,
        module_name: str,
        symbols: list[ParsedSymbol],
        owners: tuple[ParsedSymbol, ...] = (),
    ) -> None:
        for child in children:
            child_type = getattr(child, "type", None)
            if child_type == "decorated":
                self._walk_children(
                    [child.children[-1]],
                    module_path=module_path,
                    module_name=module_name,
                    symbols=symbols,
                    owners=owners,
                )
                continue
            if child_type == "classdef":
                symbol = self._build_symbol(
                    module_path=module_path,
                    module_name=module_name,
                    name=child.name.value,
                    node_type=NodeType.NODE_CLASS,
                    line=child.name.start_pos[0],
                    column=child.name.start_pos[1],
                    scope_end_line=child.end_pos[0],
                    scope_end_column=child.end_pos[1],
                    owners=owners,
                )
                symbols.append(symbol)
                self._walk_children(
                    child.children[-1].children,
                    module_path=module_path,
                    module_name=module_name,
                    symbols=symbols,
                    owners=(*owners, symbol),
                )
                continue
            if child_type == "funcdef":
                node_type = (
                    NodeType.NODE_METHOD
                    if owners and owners[-1].node_type == NodeType.NODE_CLASS
                    else NodeType.NODE_FUNCTION
                )
                symbol = self._build_symbol(
                    module_path=module_path,
                    module_name=module_name,
                    name=child.name.value,
                    node_type=node_type,
                    line=child.name.start_pos[0],
                    column=child.name.start_pos[1],
                    scope_end_line=child.end_pos[0],
                    scope_end_column=child.end_pos[1],
                    owners=owners,
                )
                symbols.append(symbol)
                self._walk_children(
                    child.children[-1].children,
                    module_path=module_path,
                    module_name=module_name,
                    symbols=symbols,
                    owners=(*owners, symbol),
                )
                continue
            if child_type == "simple_stmt":
                assignment_symbol = self._build_assignment_symbol(
                    child,
                    module_path=module_path,
                    module_name=module_name,
                    owners=owners,
                )
                if assignment_symbol is not None:
                    symbols.append(assignment_symbol)

    def _build_assignment_symbol(
        self,
        node: Any,
        *,
        module_path: Path,
        module_name: str,
        owners: tuple[ParsedSymbol, ...],
    ) -> ParsedSymbol | None:
        if owners and owners[-1].node_type not in {NodeType.NODE_CLASS}:
            return None
        children = getattr(node, "children", [])
        if not children:
            return None
        statement = children[0]
        if getattr(statement, "type", None) != "expr_stmt":
            return None
        statement_children = getattr(statement, "children", [])
        if not statement_children:
            return None
        target = statement_children[0]
        if getattr(target, "type", None) != "name":
            return None

        node_type = NodeType.NODE_FIELD if owners else NodeType.NODE_GLOBAL_VARIABLE
        return self._build_symbol(
            module_path=module_path,
            module_name=module_name,
            name=target.value,
            node_type=node_type,
            line=target.start_pos[0],
            column=target.start_pos[1],
            scope_end_line=target.end_pos[0],
            scope_end_column=target.end_pos[1],
            owners=owners,
        )

    def _build_symbol(
        self,
        *,
        module_path: Path,
        module_name: str,
        name: str,
        node_type: NodeType,
        line: int,
        column: int,
        scope_end_line: int,
        scope_end_column: int,
        owners: tuple[ParsedSymbol, ...],
    ) -> ParsedSymbol:
        parent = owners[-1] if owners else None
        qualified_parts = [module_name]
        if parent is not None:
            qualified_parts.append(parent.qualified_name.removeprefix(f"{module_name}."))
        qualified_parts.append(name)
        qualified_name = ".".join(part for part in qualified_parts if part)
        location = SourceLocation.from_name(line=line, column=column, name=name)
        return ParsedSymbol(
            path=module_path,
            name=name,
            qualified_name=qualified_name,
            node_type=node_type,
            location=location,
            scope_end_line=scope_end_line,
            scope_end_column=scope_end_column,
            parent_qualified_name=parent.qualified_name if parent is not None else None,
        )

    def _module_name(self, path: Path) -> str:
        relative = path.relative_to(self.project_root)
        parts = list(relative.parts)
        stem = Path(parts[-1]).stem
        if stem == "__init__":
            module_parts = parts[:-1]
        else:
            module_parts = [*parts[:-1], stem]
        return ".".join(module_parts) if module_parts else self.project_root.name

    def _collect_keyword_argument_labels(
        self,
        node: Any,
        keyword_argument_labels: set[tuple[int, int]],
    ) -> None:
        if getattr(node, "type", None) == "argument":
            children = getattr(node, "children", [])
            if (
                len(children) >= 2
                and getattr(children[0], "type", None) == "name"
                and getattr(children[1], "value", None) == "="
            ):
                keyword_argument_labels.add(tuple(children[0].start_pos))
        for child in getattr(node, "children", []):
            self._collect_keyword_argument_labels(child, keyword_argument_labels)
