"""UI coverage for semantic decoration preferences."""

from __future__ import annotations

import pytest
from PyQt6.QtWidgets import QCheckBox

from sourcetrail_remake.core.diagnostics import DecorationKind
from sourcetrail_remake.ui.dialogs.preferences import (
    DecorationPreferences,
    PreferencesDialog,
)


@pytest.mark.ui
def test_decoration_preferences_round_trip_enabled_kinds() -> None:
    preferences = DecorationPreferences.from_enabled(
        frozenset({DecorationKind.UNUSED_VARIABLE, DecorationKind.DEPRECATED})
    )

    assert preferences.unused_variable is True
    assert preferences.undefined_reference is False
    assert preferences.enabled_kinds() == frozenset(
        {DecorationKind.UNUSED_VARIABLE, DecorationKind.DEPRECATED}
    )


@pytest.mark.ui
def test_preferences_dialog_exposes_decoration_checkboxes(qtbot) -> None:
    dialog = PreferencesDialog(
        DecorationPreferences(unused_variable=True, undefined_reference=False)
    )
    qtbot.addWidget(dialog)

    undefined_checkbox = dialog.findChild(
        QCheckBox,
        "preference-undefined-reference-checkbox",
    )
    assert undefined_checkbox is not None
    assert not undefined_checkbox.isChecked()

    undefined_checkbox.setChecked(True)
    assert dialog.preferences().undefined_reference is True
