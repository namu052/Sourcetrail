"""Preferences dialog for semantic decoration toggles."""

from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QWidget

from sourcetrail_remake.core.diagnostics import DecorationKind


@dataclass(frozen=True, slots=True)
class DecorationPreferences:
    """Persistable semantic decoration preferences."""

    unused_variable: bool = True
    undefined_reference: bool = True
    deprecated: bool = True
    type_hint: bool = True

    def enabled_kinds(self) -> frozenset[DecorationKind]:
        enabled: set[DecorationKind] = set()
        if self.unused_variable:
            enabled.add(DecorationKind.UNUSED_VARIABLE)
        if self.undefined_reference:
            enabled.add(DecorationKind.UNDEFINED_REFERENCE)
        if self.deprecated:
            enabled.add(DecorationKind.DEPRECATED)
        if self.type_hint:
            enabled.add(DecorationKind.TYPE_HINT)
        return frozenset(enabled)

    @classmethod
    def from_enabled(cls, enabled: frozenset[DecorationKind]) -> DecorationPreferences:
        return cls(
            unused_variable=DecorationKind.UNUSED_VARIABLE in enabled,
            undefined_reference=DecorationKind.UNDEFINED_REFERENCE in enabled,
            deprecated=DecorationKind.DEPRECATED in enabled,
            type_hint=DecorationKind.TYPE_HINT in enabled,
        )


class PreferencesDialog(QDialog):
    """Checkbox-based preferences dialog for SyntaxDecorator options."""

    def __init__(
        self,
        preferences: DecorationPreferences | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setObjectName("preferences-dialog")
        self._build_ui(preferences or DecorationPreferences())

    def preferences(self) -> DecorationPreferences:
        return DecorationPreferences(
            unused_variable=self.unused_variable_checkbox.isChecked(),
            undefined_reference=self.undefined_reference_checkbox.isChecked(),
            deprecated=self.deprecated_checkbox.isChecked(),
            type_hint=self.type_hint_checkbox.isChecked(),
        )

    def _build_ui(self, preferences: DecorationPreferences) -> None:
        layout = QFormLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.unused_variable_checkbox = _checkbox(
            "Unused variables",
            "preference-unused-variable-checkbox",
            preferences.unused_variable,
        )
        self.undefined_reference_checkbox = _checkbox(
            "Undefined references",
            "preference-undefined-reference-checkbox",
            preferences.undefined_reference,
        )
        self.deprecated_checkbox = _checkbox(
            "Deprecated calls",
            "preference-deprecated-checkbox",
            preferences.deprecated,
        )
        self.type_hint_checkbox = _checkbox(
            "Type hints",
            "preference-type-hint-checkbox",
            preferences.type_hint,
        )

        layout.addRow(self.unused_variable_checkbox)
        layout.addRow(self.undefined_reference_checkbox)
        layout.addRow(self.deprecated_checkbox)
        layout.addRow(self.type_hint_checkbox)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)


def _checkbox(label: str, object_name: str, checked: bool) -> QCheckBox:
    checkbox = QCheckBox(label)
    checkbox.setObjectName(object_name)
    checkbox.setChecked(checked)
    return checkbox
