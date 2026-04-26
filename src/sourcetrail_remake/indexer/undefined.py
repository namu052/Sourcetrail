"""Undefined reference analysis for semantic editor decoration."""

from __future__ import annotations

import ast
import builtins
from dataclasses import dataclass
from pathlib import Path

import jedi

from sourcetrail_remake.core.diagnostics import Decoration, DecorationKind, SourceRange


@dataclass(frozen=True, slots=True)
class UndefinedReference:
    """A name load that cannot be resolved in the local source context."""

    name: str
    range: SourceRange

    def to_decoration(self) -> Decoration:
        return Decoration(
            kind=DecorationKind.UNDEFINED_REFERENCE,
            range=self.range,
            message=f"Undefined reference: {self.name}",
        )


class UndefinedReferenceAnalyzer:
    """Detect unresolved Python names for red squiggle editor decoration."""

    def analyze_file(self, path: Path) -> list[UndefinedReference]:
        return self.analyze_text(Path(path).read_text(encoding="utf-8"), path=Path(path))

    def analyze_text(
        self,
        source: str,
        *,
        path: Path | None = None,
    ) -> list[UndefinedReference]:
        self._prime_jedi(source, path=path)
        tree = ast.parse(source, filename=str(path) if path is not None else "<string>")
        visitor = _UndefinedVisitor()
        visitor.visit(tree)
        return visitor.undefined_references()

    def decorations_for_text(
        self,
        source: str,
        *,
        path: Path | None = None,
    ) -> list[Decoration]:
        return [reference.to_decoration() for reference in self.analyze_text(source, path=path)]

    def _prime_jedi(self, source: str, *, path: Path | None) -> None:
        script = jedi.Script(code=source, path=None if path is None else str(path))
        script.get_names(all_scopes=True, definitions=True, references=True)


class _UndefinedVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self._defined_stack: list[set[str]] = [set(dir(builtins))]
        self._references: list[UndefinedReference] = []

    def undefined_references(self) -> list[UndefinedReference]:
        return self._references

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function_scope(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function_scope(node)

    def _visit_function_scope(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._define(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        self._push_scope()
        for arg in _iter_args(node.args):
            self._define(arg.arg)
        for statement in node.body:
            self.visit(statement)
        self._pop_scope()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._define(node.name)
        for base in node.bases:
            self.visit(base)
        for decorator in node.decorator_list:
            self.visit(decorator)
        self._push_scope()
        for statement in node.body:
            self.visit(statement)
        self._pop_scope()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._define((alias.asname or alias.name).split(".", maxsplit=1)[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name != "*":
                self._define(alias.asname or alias.name)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self._define(node.id)
            return
        if isinstance(node.ctx, ast.Load) and not self._is_defined(node.id):
            self._references.append(
                UndefinedReference(
                    name=node.id,
                    range=SourceRange(
                        node.lineno,
                        node.col_offset,
                        node.lineno,
                        node.col_offset + len(node.id),
                    ),
                )
            )

    def _define(self, name: str) -> None:
        self._defined_stack[-1].add(name)

    def _is_defined(self, name: str) -> bool:
        return any(name in scope for scope in reversed(self._defined_stack))

    def _push_scope(self) -> None:
        self._defined_stack.append(set())

    def _pop_scope(self) -> None:
        self._defined_stack.pop()


def _iter_args(arguments: ast.arguments) -> list[ast.arg]:
    return [
        *arguments.posonlyargs,
        *arguments.args,
        *arguments.kwonlyargs,
        *([] if arguments.vararg is None else [arguments.vararg]),
        *([] if arguments.kwarg is None else [arguments.kwarg]),
    ]
