"""Analyze the installed ``requests`` package with Jedi.

The script reports:
- total Python files scanned
- total symbol definitions discovered by Jedi
- unresolved import targets / total import targets as an "unsolved ratio"
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import jedi


@dataclass(slots=True)
class AnalysisTotals:
    """Aggregate counts emitted by the PoC."""

    definitions: int = 0
    import_targets: int = 0
    unresolved_imports: int = 0
    definition_types: Counter[str] = field(default_factory=Counter)
    unresolved_examples: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", default="requests", help="Installed package name to inspect.")
    parser.add_argument(
        "--max-examples",
        type=int,
        default=10,
        help="Maximum unresolved examples to print.",
    )
    return parser.parse_args()


def find_package_root(package_name: str) -> Path:
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        raise SystemExit(f"Unable to locate installed package: {package_name!r}")

    if spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations))).resolve()

    if spec.origin is None:
        raise SystemExit(f"Package {package_name!r} does not expose a filesystem path.")

    return Path(spec.origin).resolve().parent


def build_project(package_root: Path) -> jedi.Project:
    sys_path = [str(package_root.parent), *sys.path]
    return jedi.Project(path=str(package_root.parent), sys_path=sys_path)


def iter_python_files(package_root: Path) -> list[Path]:
    return sorted(path for path in package_root.rglob("*.py") if path.is_file())


def count_definitions(script: jedi.Script, file_path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for name in script.get_names(all_scopes=True, definitions=True, references=False):
        module_path = Path(str(name.module_path)).resolve() if name.module_path else None
        if module_path != file_path.resolve():
            continue
        if name.type == "keyword":
            continue
        counts[name.type] += 1
    return counts


def iter_import_positions(tree: ast.AST) -> list[tuple[int, int, str]]:
    positions: list[tuple[int, int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                line = getattr(alias, "lineno", node.lineno)
                column = getattr(alias, "col_offset", node.col_offset + 7)
                positions.append((line, column, alias.name))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                line = getattr(alias, "lineno", node.lineno)
                column = getattr(alias, "col_offset", node.col_offset + 5)
                positions.append((line, column, alias.name))

    return positions


def is_resolved(script: jedi.Script, line: int, column: int) -> bool:
    try:
        targets = script.goto(
            line=line,
            column=column,
            follow_imports=True,
            follow_builtin_imports=False,
        )
    except Exception:
        targets = []

    if targets:
        return True

    try:
        inferred = script.infer(line=line, column=column)
    except Exception:
        inferred = []

    return bool(inferred)


def analyze_file(
    file_path: Path,
    package_root: Path,
    project: jedi.Project,
    max_examples: int,
) -> AnalysisTotals:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    script = jedi.Script(code=source, path=str(file_path), project=project)

    totals = AnalysisTotals()
    definition_counts = count_definitions(script, file_path)
    totals.definition_types.update(definition_counts)
    totals.definitions += sum(definition_counts.values())

    for line, column, symbol_name in iter_import_positions(tree):
        totals.import_targets += 1
        if is_resolved(script, line, column):
            continue

        totals.unresolved_imports += 1
        if len(totals.unresolved_examples) < max_examples:
            relative_path = file_path.relative_to(package_root)
            totals.unresolved_examples.append(f"{relative_path}:{line}:{symbol_name}")

    return totals


def merge_totals(left: AnalysisTotals, right: AnalysisTotals, max_examples: int) -> AnalysisTotals:
    left.definitions += right.definitions
    left.import_targets += right.import_targets
    left.unresolved_imports += right.unresolved_imports
    left.definition_types.update(right.definition_types)

    remaining = max_examples - len(left.unresolved_examples)
    if remaining > 0:
        left.unresolved_examples.extend(right.unresolved_examples[:remaining])

    return left


def format_breakdown(counter: Counter[str]) -> str:
    ordered = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    return ", ".join(f"{name}={count}" for name, count in ordered)


def main() -> int:
    args = parse_args()
    package_root = find_package_root(args.package)
    project = build_project(package_root)
    python_files = iter_python_files(package_root)

    started_at = time.perf_counter()
    totals = AnalysisTotals()
    for file_path in python_files:
        file_totals = analyze_file(file_path, package_root, project, args.max_examples)
        totals = merge_totals(totals, file_totals, args.max_examples)
    elapsed = time.perf_counter() - started_at

    ratio = 0.0
    if totals.import_targets:
        ratio = totals.unresolved_imports / totals.import_targets

    print(f"package={args.package}")
    print(f"package_root={package_root}")
    print(f"python_files={len(python_files)}")
    print(f"definitions={totals.definitions}")
    print(f"definition_breakdown={format_breakdown(totals.definition_types)}")
    print(f"import_targets={totals.import_targets}")
    print(f"unresolved_imports={totals.unresolved_imports}")
    print(f"unsolved_ratio={ratio:.2%}")
    print(f"elapsed_seconds={elapsed:.2f}")

    if totals.unresolved_examples:
        print("unresolved_examples=")
        for example in totals.unresolved_examples:
            print(f"  - {example}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
