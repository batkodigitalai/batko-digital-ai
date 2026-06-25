"""Command line entrypoint for `python -m src`."""

from __future__ import annotations

import argparse
from pathlib import Path

from src import __version__
from src.core.config import load_config
from src.core.logging import setup_logging
from src.core.storage import ProjectStorage
from src.openlane.browser import BrowserFactory, SessionManager
from src.openlane.capture import CaptureService


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(prog="python -m src")
    subparsers = parser.add_subparsers(dest="command")

    capture = subparsers.add_parser("capture", help="Capture the active OPENLANE auction page")
    capture.add_argument("--output-dir", type=Path, default=None, help="Target capture archive directory")
    capture.add_argument("--browser-mode", default=None, help="Override configured browser mode")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Initialize the foundation runtime and exit cleanly."""
    parser = build_parser()
    args = parser.parse_args(argv)
    project_root = Path.cwd()
    config = load_config(project_root=project_root)
    setup_logging(config.logging)
    storage = ProjectStorage(project_root=project_root, config=config.storage)
    storage.ensure_project_directories()

    if args.command == "capture":
        browser_manager = BrowserFactory(config.browser, project_root=project_root).create()
        session_manager = SessionManager(browser_manager)
        runtime = session_manager.create_session(args.browser_mode)
        try:
            result = CaptureService(project_root=project_root).capture(runtime.page, output_dir=args.output_dir)
        finally:
            session_manager.end_session()
        print(f"Capture status {result.manifest.status.value}: {result.source_dir}")
        return 0

    print(f"BATKO_AUTO_V4 version {__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
