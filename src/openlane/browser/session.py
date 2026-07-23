"""Browser session management."""

from __future__ import annotations

from src.core.logging import get_logger
from src.openlane.browser.manager import BrowserManager
from src.openlane.browser.models import BrowserMode, BrowserRuntime

logger = get_logger(__name__)


class SessionManager:
    """Manage one active browser session."""

    def __init__(self, browser_manager: BrowserManager) -> None:
        self.browser_manager = browser_manager
        self._runtime: BrowserRuntime | None = None

    def create_session(self, mode: BrowserMode | str | None = None) -> BrowserRuntime:
        """Create and store a browser session."""
        if self._runtime is not None:
            logger.info("Replacing existing browser session")
            self.end_session()
        self._runtime = self.browser_manager.start(mode)
        logger.info("Created browser session in {} mode", self._runtime.mode.value)
        return self._runtime

    def end_session(self) -> None:
        """End the active browser session if present."""
        if self._runtime is None:
            logger.info("No active browser session to end")
            return
        self.browser_manager.stop(self._runtime)
        logger.info("Ended browser session in {} mode", self._runtime.mode.value)
        self._runtime = None

    def get_active_page(self):
        """Return the active Playwright page handle."""
        if self._runtime is None:
            raise RuntimeError("No active browser session")
        return self._runtime.page

    def get_browser_context(self):
        """Return the active Playwright browser context handle."""
        if self._runtime is None:
            raise RuntimeError("No active browser session")
        return self._runtime.context

