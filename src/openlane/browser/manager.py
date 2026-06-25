"""Browser startup manager for local, CDP, and persistent profile modes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.core.config.models import BrowserConfig
from src.core.logging import get_logger
from src.openlane.browser.cdp import CDPConnector
from src.openlane.browser.models import BrowserMode, BrowserRuntime
from src.openlane.browser.playwright_provider import start_sync_playwright
from src.openlane.browser.profile import ProfileManager

logger = get_logger(__name__)


class BrowserManager:
    """Create browser runtimes without OPENLANE-specific behavior."""

    def __init__(
        self,
        config: BrowserConfig | None = None,
        project_root: Path | str = ".",
        playwright_factory: Callable[[], Any] = start_sync_playwright,
        profile_manager: ProfileManager | None = None,
    ) -> None:
        self.config = config or BrowserConfig()
        self.project_root = Path(project_root)
        self.playwright_factory = playwright_factory
        self.profile_manager = profile_manager or ProfileManager(self.project_root, self.config)

    def start(self, mode: BrowserMode | str | None = None) -> BrowserRuntime:
        """Start a browser runtime for the selected mode."""
        selected_mode = BrowserMode(mode or self.config.browser_mode)
        logger.info("Starting browser runtime in {} mode", selected_mode.value)
        if selected_mode is BrowserMode.LOCAL:
            return self.start_local_browser()
        if selected_mode is BrowserMode.EXISTING_CHROME:
            return self.connect_existing_chrome()
        if selected_mode is BrowserMode.PERSISTENT_PROFILE:
            return self.start_persistent_profile()
        raise ValueError(f"Unsupported browser mode: {selected_mode}")

    def start_local_browser(self) -> BrowserRuntime:
        """Launch a local Chromium browser."""
        playwright = self.playwright_factory()
        browser = playwright.chromium.launch(
            headless=self.config.headless,
            timeout=self.config.playwright_timeout,
        )
        context = browser.new_context()
        page = context.new_page()
        logger.info("Started local Chromium browser")
        return BrowserRuntime(
            mode=BrowserMode.LOCAL,
            playwright=playwright,
            browser=browser,
            context=context,
            page=page,
            owns_browser=True,
            owns_context=True,
        )

    def connect_existing_chrome(self) -> BrowserRuntime:
        """Connect to an already running Chrome through CDP."""
        playwright, browser = CDPConnector(self.config, self.playwright_factory).connect()
        context = browser.contexts[0] if getattr(browser, "contexts", []) else browser.new_context()
        page = context.pages[0] if getattr(context, "pages", []) else context.new_page()
        logger.info("Connected to existing Chrome over CDP")
        return BrowserRuntime(
            mode=BrowserMode.EXISTING_CHROME,
            playwright=playwright,
            browser=browser,
            context=context,
            page=page,
            owns_browser=False,
            owns_context=False,
        )

    def start_persistent_profile(self) -> BrowserRuntime:
        """Launch Chromium with a persistent profile directory."""
        playwright = self.playwright_factory()
        profile_path = self.profile_manager.load_profile()
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=self.config.headless,
            timeout=self.config.playwright_timeout,
        )
        page = context.pages[0] if getattr(context, "pages", []) else context.new_page()
        logger.info("Started Chromium with persistent profile {}", profile_path)
        return BrowserRuntime(
            mode=BrowserMode.PERSISTENT_PROFILE,
            playwright=playwright,
            browser=None,
            context=context,
            page=page,
            owns_browser=False,
            owns_context=True,
        )

    def stop(self, runtime: BrowserRuntime | None) -> None:
        """Close owned handles for a browser runtime."""
        if runtime is None:
            return
        logger.info("Stopping browser runtime in {} mode", runtime.mode.value)
        if runtime.owns_context and runtime.context is not None:
            runtime.context.close()
        if runtime.owns_browser and runtime.browser is not None:
            runtime.browser.close()
        if runtime.playwright is not None:
            runtime.playwright.stop()

