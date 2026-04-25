"""Application configuration helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtWidgets import QApplication


@dataclass(slots=True, frozen=True)
class AppConfig:
    """Static application metadata for the Phase 0 shell."""

    organization_name: str = "Sourcetrail_Remake"
    application_name: str = "Sourcetrail_Remake"
    main_window_title: str = "Sourcetrail_Remake"
    appdata_subdir: str = "Sourcetrail_Remake"

    @property
    def appdata_path(self) -> Path:
        base = Path.home() / "AppData" / "Roaming"
        return base / self.appdata_subdir


DEFAULT_CONFIG = AppConfig()


def configure_qt_application(app: QApplication, config: AppConfig = DEFAULT_CONFIG) -> None:
    """Apply basic Qt metadata to the QApplication instance."""
    app.setOrganizationName(config.organization_name)
    app.setApplicationName(config.application_name)
