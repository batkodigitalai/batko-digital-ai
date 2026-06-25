"""Command line entrypoint for `python -m src`."""

from __future__ import annotations

from pathlib import Path

from src import __version__
from src.core.config import load_config
from src.core.logging import setup_logging
from src.core.storage import ProjectStorage


def main() -> int:
    """Initialize the foundation runtime and exit cleanly."""
    project_root = Path.cwd()
    config = load_config(project_root=project_root)
    setup_logging(config.logging)
    storage = ProjectStorage(project_root=project_root, config=config.storage)
    storage.ensure_project_directories()
    print(f"BATKO_AUTO_V4 version {__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

