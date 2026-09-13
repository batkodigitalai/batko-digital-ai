"""Browser manager factory."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.core.config.models import BrowserConfig
from src.core.logging import get_logger
from src.openlane.browser.manager import BrowserManager
from src.openlane.browser.models import BrowserMode
from src.openlane.browser.playwright_provider import start_sync_playwright
from src.openlane.browser.profile import ProfileManager

logger = get_logger(__name__)


class BrowserFactory:
    """Create browser managers for the configured browser mode."""

    def __init__(
        self,
        config: BrowserConfig,
        project_root: Path | str = ".",
        playwright_factory: Callable[[], Any] = start_sync_playwright,
    ) -> None:
        self.config = config
        self.project_root = Path(project_root)
        self.playwright_factory = playwright_factory

    def create(self) -> BrowserManager:
        """Create a BrowserManager for local, CDP, or persistent profile mode."""
        mode = BrowserMode(self.config.browser_mode)
        logger.info("Creating BrowserManager for {} mode", mode.value)
        profile_manager = ProfileManager(self.project_root, self.config)
        return BrowserManager(
            config=self.config,
            project_root=self.project_root,
            playwright_factory=self.playwright_factory,
            profile_manager=profile_manager,
        )

