"""Chrome DevTools Protocol connection infrastructure."""

from __future__ import annotations

from typing import Any, Callable

from src.core.config.models import BrowserConfig
from src.core.logging import get_logger

logger = get_logger(__name__)


class CDPConnector:
    """Prepare connections to an already running Chrome via CDP."""

    def __init__(self, config: BrowserConfig, playwright_factory: Callable[[], Any]) -> None:
        self.config = config
        self.playwright_factory = playwright_factory

    def connect(self) -> tuple[Any, Any]:
        """Connect to Chrome via CDP and return Playwright plus browser handles."""
        logger.info("Connecting to existing Chrome over CDP at {}", self.config.chrome_cdp)
        playwright = self.playwright_factory()
        browser = playwright.chromium.connect_over_cdp(
            self.config.chrome_cdp,
            timeout=self.config.playwright_timeout,
        )
        return playwright, browser

