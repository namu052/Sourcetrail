"""Shortcut inventory and conflict checks for Qt widgets."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget


@dataclass(frozen=True, slots=True)
class ShortcutBinding:
    """One active shortcut binding discovered in a widget tree."""

    sequence: str
    owner: str
    source: str


@dataclass(frozen=True, slots=True)
class ShortcutConflict:
    """A duplicate key sequence and the bindings that share it."""

    sequence: str
    bindings: tuple[ShortcutBinding, ...]


def collect_shortcut_bindings(root: QWidget) -> tuple[ShortcutBinding, ...]:
    """Collect non-empty QAction and QShortcut key sequences under a widget."""
    bindings: list[ShortcutBinding] = []
    for action in root.findChildren(QAction):
        for sequence in action.shortcuts() or [action.shortcut()]:
            binding = _binding_from_sequence(sequence, _owner_name(action), "QAction")
            if binding is not None:
                bindings.append(binding)
    for shortcut in root.findChildren(QShortcut):
        binding = _binding_from_sequence(shortcut.key(), _owner_name(shortcut), "QShortcut")
        if binding is not None:
            bindings.append(binding)
    return tuple(bindings)


def find_shortcut_conflicts(bindings: Iterable[ShortcutBinding]) -> tuple[ShortcutConflict, ...]:
    """Return duplicate key sequences from an existing shortcut inventory."""
    grouped: dict[str, list[ShortcutBinding]] = defaultdict(list)
    for binding in bindings:
        grouped[binding.sequence].append(binding)
    return tuple(
        ShortcutConflict(sequence=sequence, bindings=tuple(items))
        for sequence, items in sorted(grouped.items())
        if len(items) > 1
    )


def assert_no_shortcut_conflicts(root: QWidget) -> None:
    """Raise AssertionError when a widget tree has duplicate key sequences."""
    conflicts = find_shortcut_conflicts(collect_shortcut_bindings(root))
    if conflicts:
        details = "; ".join(
            f"{conflict.sequence}: {', '.join(item.owner for item in conflict.bindings)}"
            for conflict in conflicts
        )
        raise AssertionError(f"duplicate shortcuts detected: {details}")


def _binding_from_sequence(
    sequence: QKeySequence,
    owner: str,
    source: str,
) -> ShortcutBinding | None:
    text = sequence.toString()
    if not text:
        return None
    return ShortcutBinding(sequence=text, owner=owner, source=source)


def _owner_name(item: object) -> str:
    object_name_getter = getattr(item, "objectName", None)
    if callable(object_name_getter):
        object_name = str(object_name_getter())
        if object_name:
            return object_name
    text_getter = getattr(item, "text", None)
    if callable(text_getter):
        text = str(text_getter()).replace("&", "")
        if text:
            return text
    return item.__class__.__name__
