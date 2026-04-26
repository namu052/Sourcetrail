"""Deprecation pattern analysis for semantic editor decoration."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from sourcetrail_remake.core.diagnostics import Decoration, DecorationKind, SourceRange


@dataclass(frozen=True, slots=True)
class DeprecationFinding:
    """A deprecated declaration, warning emission, or deprecated call site."""

    name: str
    range: SourceRange
    reason: str

    def to_decoration(self) -> Decoration:
        return Decoration(
            kind=DecorationKind.DEPRECATED,
            range=self.range,
            message=f"Deprecated {self.name}: {self.reason}",
        )


class DeprecationAnalyzer:
    """Find Python deprecation declarations and call sites."""

    def analyze_file(self, path: Path) -> list[DeprecationFinding]:
        return self.analyze_text(Path(path).read_text(encoding="utf-8"), path=Path(path))

    def analyze_text(
        self,
        source: str,
        *,
        path: Path | None = None,
    ) -> list[DeprecationFinding]:
        tree = ast.parse(source, filename=str(path) if path is not None else "<string>")
        visitor = _DeprecationVisitor()
        visitor.visit(tree)
        return visitor.findings()

    def decorations_for_text(
        self,
        source: str,
        *,
        path: Path | None = None,
    ) -> list[Decoration]:
        return [finding.to_decoration() for finding in self.analyze_text(source, path=path)]


class _DeprecationVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self._deprecated_names: set[str] = set()
        self._findings: list[DeprecationFinding] = []

    def findings(self) -> list[DeprecationFinding]:
        return self._findings

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_declaration(node.name, node, node.decorator_list)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_declaration(node.name, node, node.decorator_list)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._visit_declaration(node.name, node, node.decorator_list)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _call_name(node.func)
        if call_name in {"warnings.warn", "warn"} and _has_deprecation_warning(node):
            self._findings.append(
                DeprecationFinding(
                    name="DeprecationWarning",
                    range=_range_for_node(node, "warnings.warn"),
                    reason="emits DeprecationWarning",
                )
            )
        elif call_name is not None:
            name = call_name.rsplit(".", maxsplit=1)[-1]
            if name not in self._deprecated_names:
                self.generic_visit(node)
                return
            self._findings.append(
                DeprecationFinding(
                    name=name,
                    range=_range_for_node(node.func, name),
                    reason="calls deprecated symbol",
                )
            )
        self.generic_visit(node)

    def _visit_declaration(
        self,
        name: str,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
        decorators: list[ast.expr],
    ) -> None:
        if not any(_is_deprecated_decorator(decorator) for decorator in decorators):
            return
        self._deprecated_names.add(name)
        self._findings.append(
            DeprecationFinding(
                name=name,
                range=_range_for_node(node, name),
                reason="decorated as deprecated",
            )
        )


def _is_deprecated_decorator(node: ast.expr) -> bool:
    name = _call_name(node.func) if isinstance(node, ast.Call) else _call_name(node)
    if name is None:
        return False
    parts = {part.lower() for part in name.split(".")}
    return "deprecated" in parts or any(part.endswith("deprecated") for part in parts)


def _has_deprecation_warning(node: ast.Call) -> bool:
    candidates = [*node.args, *(keyword.value for keyword in node.keywords)]
    return any(_call_name(candidate) == "DeprecationWarning" for candidate in candidates)


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return node.attr if parent is None else f"{parent}.{node.attr}"
    return None


def _range_for_node(node: ast.AST, name: str) -> SourceRange:
    line = int(getattr(node, "lineno", 1))
    column = int(getattr(node, "col_offset", 0))
    return SourceRange(line, column, line, column + len(name))
