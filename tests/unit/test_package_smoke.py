"""Package smoke tests."""

from __future__ import annotations

import pytest

from sourcetrail_remake import __version__


@pytest.mark.unit
def test_package_version_is_exposed() -> None:
    assert __version__ == "0.1.0"
