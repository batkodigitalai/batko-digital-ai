"""Configuration manager for first-run defaults and persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loguru import logger

from src.core.config.models import AppConfig

DEFAULT_CONFIG_PATH = Path("config/auto_v4_config.json")


class ConfigManager:
    """Load, create, and save application configuration."""

    def __init__(self, project_root: Path | str = ".", config_path: Path | str | None = None) -> None:
        self.project_root = Path(project_root)
        self.config_path = self._resolve_path(config_path or DEFAULT_CONFIG_PATH)

    def load(self) -> AppConfig:
        """Load config, creating a default file on first run."""
        if not self.config_path.exists():
            logger.info("Config file not found, creating default config at {}", self.config_path)
            config = AppConfig()
            self.save(config)
            return config

        logger.info("Loading config from {}", self.config_path)
        data = json.loads(self.config_path.read_text(encoding="utf-8"))
        return AppConfig.model_validate(data)

    def save(self, config: AppConfig) -> None:
        """Persist config to disk."""
        logger.info("Saving config to {}", self.config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(self._json_ready(config), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def _resolve_path(self, path: Path | str) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return self.project_root / candidate

    @staticmethod
    def _json_ready(config: AppConfig) -> dict[str, Any]:
        return config.model_dump(mode="json")


def load_config(project_root: Path | str = ".", config_path: Path | str | None = None) -> AppConfig:
    """Convenience loader for the application config."""
    return ConfigManager(project_root=project_root, config_path=config_path).load()


def save_config(config: AppConfig, project_root: Path | str = ".", config_path: Path | str | None = None) -> None:
    """Convenience saver for the application config."""
    ConfigManager(project_root=project_root, config_path=config_path).save(config)

