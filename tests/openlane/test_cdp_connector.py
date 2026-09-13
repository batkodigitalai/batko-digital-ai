from unittest.mock import MagicMock

from src.core.config.models import BrowserConfig
from src.openlane.browser import CDPConnector


def test_cdp_connector_uses_configured_endpoint() -> None:
    browser = MagicMock(name="browser")
    chromium = MagicMock(name="chromium")
    chromium.connect_over_cdp.return_value = browser
    playwright = MagicMock(name="playwright")
    playwright.chromium = chromium
    config = BrowserConfig(chrome_cdp="http://127.0.0.1:9333", playwright_timeout=1234)

    connector = CDPConnector(config=config, playwright_factory=lambda: playwright)
    returned_playwright, returned_browser = connector.connect()

    assert returned_playwright is playwright
    assert returned_browser is browser
    chromium.connect_over_cdp.assert_called_once_with("http://127.0.0.1:9333", timeout=1234)

