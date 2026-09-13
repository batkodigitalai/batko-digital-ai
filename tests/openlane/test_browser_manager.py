from pathlib import Path
from unittest.mock import MagicMock

from src.core.config.models import BrowserConfig
from src.openlane.browser import BrowserManager, BrowserMode


def fake_playwright_factory() -> MagicMock:
    page = MagicMock(name="page")
    context = MagicMock(name="context")
    context.pages = []
    context.new_page.return_value = page
    browser = MagicMock(name="browser")
    browser.contexts = []
    browser.new_context.return_value = context
    chromium = MagicMock(name="chromium")
    chromium.launch.return_value = browser
    chromium.connect_over_cdp.return_value = browser
    persistent_context = MagicMock(name="persistent_context")
    persistent_context.pages = [page]
    chromium.launch_persistent_context.return_value = persistent_context
    playwright = MagicMock(name="playwright")
    playwright.chromium = chromium
    return playwright


def test_browser_manager_starts_local_browser() -> None:
    playwright = fake_playwright_factory()
    manager = BrowserManager(config=BrowserConfig(), playwright_factory=lambda: playwright)

    runtime = manager.start(BrowserMode.LOCAL)

    assert runtime.mode is BrowserMode.LOCAL
    assert runtime.browser is playwright.chromium.launch.return_value
    assert runtime.context is runtime.browser.new_context.return_value
    assert runtime.page is runtime.context.new_page.return_value
    playwright.chromium.launch.assert_called_once_with(headless=True, timeout=30000)


def test_browser_manager_connects_existing_chrome() -> None:
    playwright = fake_playwright_factory()
    config = BrowserConfig(browser_mode="existing_chrome", chrome_cdp="http://localhost:9222")
    manager = BrowserManager(config=config, playwright_factory=lambda: playwright)

    runtime = manager.start()

    assert runtime.mode is BrowserMode.EXISTING_CHROME
    assert runtime.owns_browser is False
    playwright.chromium.connect_over_cdp.assert_called_once_with("http://localhost:9222", timeout=30000)


def test_browser_manager_starts_persistent_profile(tmp_path: Path) -> None:
    playwright = fake_playwright_factory()
    config = BrowserConfig(browser_mode="persistent_profile", chrome_profile=Path("profiles/chrome/test"))
    manager = BrowserManager(config=config, project_root=tmp_path, playwright_factory=lambda: playwright)

    runtime = manager.start()

    assert runtime.mode is BrowserMode.PERSISTENT_PROFILE
    assert runtime.browser is None
    assert runtime.context is playwright.chromium.launch_persistent_context.return_value
    playwright.chromium.launch_persistent_context.assert_called_once_with(
        user_data_dir=str(tmp_path / "profiles" / "chrome" / "test"),
        headless=True,
        timeout=30000,
    )


def test_browser_manager_stop_closes_owned_handles() -> None:
    playwright = fake_playwright_factory()
    manager = BrowserManager(config=BrowserConfig(), playwright_factory=lambda: playwright)
    runtime = manager.start(BrowserMode.LOCAL)

    manager.stop(runtime)

    runtime.context.close.assert_called_once()
    runtime.browser.close.assert_called_once()
    playwright.stop.assert_called_once()

