"""Unused variable analysis for semantic editor decoration."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import jedi

from sourcetrail_remake.ui.editor.decorator import Decoration, DecorationKind, SourceRange


@dataclass(frozen=True, slots=True)
class UnusedVariable:
    """A local assignment that has no read reference in its scope."""

    name: str
    range: SourceRange
    scope: str

    def to_decoration(self) -> Decoration:
        return Decoration(
            kind=DecorationKind.UNUSED_VARIABLE,
            range=self.range,
            message=f"Unused variable: {self.name}",
        )


@dataclass(slots=True)
class _Scope:
    name: str
    stores: dict[str, SourceRange]
    loads: set[str]


class UnusedVariableAnalyzer:
    """Find assigned Python names that are never read."""

    def analyze_text(self, source: str, *, path: Path | None = None) -> list[UnusedVariable]:
        """Analyze source text and return unused assignment diagnostics."""
        self._prime_jedi(source, path=path)
        tree = ast.parse(source, filename=str(path) if path is not None else "<string>")
        visitor = _UnusedVisitor()
        visitor.visit(tree)
        return visitor.unused_variables()

    def analyze_file(self, path: Path) -> list[UnusedVariable]:
        source = Path(path).read_text(encoding="utf-8")
        return self.analyze_text(source, path=Path(path).resolve())

    def decorations_for_text(
        self,
        source: str,
        *,
        path: Path | None = None,
    ) -> list[Decoration]:
        return [diagnostic.to_decoration() for diagnostic in self.analyze_text(source, path=path)]

    def _prime_jedi(self, source: str, *, path: Path | None) -> None:
        script = jedi.Script(code=source, path=None if path is None else str(path))
        script.get_names(all_scopes=True, definitions=True, references=True)


class _UnusedVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self._scopes: list[_Scope] = [_Scope("<module>", {}, set())]
        self._completed: list[_Scope] = []

    def unused_variables(self) -> list[UnusedVariable]:
        return [
            UnusedVariable(name=name, range=source_range, scope=scope.name)
            for scope in self._completed + self._scopes
            for name, source_range in scope.stores.items()
            if name not in scope.loads and not _is_intentionally_unused(name)
        ]

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function_scope(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function_scope(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._push_scope("<lambda>")
        self.visit(node.body)
        self._pop_scope()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        self._push_scope(node.name)
        for statement in node.body:
            self.visit(statement)
        self._pop_scope()

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self._record_store(node.id, node)
        elif isinstance(node.ctx, ast.Load):
            self._current.loads.add(node.id)

    def visit_arg(self, node: ast.arg) -> None:
        if node.arg not in {"self", "cls"}:
            self._record_store(node.arg, node)

    @property
    def _current(self) -> _Scope:
        return self._scopes[-1]

    def _visit_function_scope(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        for default in [*node.args.defaults, *node.args.kw_defaults]:
            if default is not None:
                self.visit(default)
        self._push_scope(node.name)
        self.visit(node.args)
        for statement in node.body:
            self.visit(statement)
        self._pop_scope()

    def _record_store(self, name: str, node: ast.AST) -> None:
        if name not in self._current.stores:
            self._current.stores[name] = _range_for_node(node, name)

    def _push_scope(self, name: str) -> None:
        self._scopes.append(_Scope(name, {}, set()))

    def _pop_scope(self) -> None:
        self._completed.append(self._scopes.pop())


def _range_for_node(node: ast.AST, name: str) -> SourceRange:
    line = int(getattr(node, "lineno", 1))
    column = int(getattr(node, "col_offset", 0))
    return SourceRange(
        start_line=line,
        start_column=column,
        end_line=line,
        end_column=column + len(name),
    )


def _is_intentionally_unused(name: str) -> bool:
    return name == "_" or name.startswith("_")
