"""Loguru configuration for BATKO_AUTO_V4."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from src.core.config.models import LoggingConfig


def setup_logging(config: LoggingConfig, project_root: Path | str = ".") -> Path:
    """Configure console and rotating file logging."""
    root = Path(project_root)
    logs_dir = config.logs_dir if config.logs_dir.is_absolute() else root / config.logs_dir
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / config.file_name

    logger.remove()
    logger.add(sys.stderr, level=config.level)
    logger.add(
        log_file,
        level=config.level,
        rotation=config.rotation,
        retention=config.retention,
        encoding="utf-8",
    )
    logger.info("Logging initialized at {}", log_file)
    return log_file


def get_logger(module_name: str):
    """Return a module-bound logger."""
    return logger.bind(module=module_name)

