from pathlib import Path

from src.core.config.models import BrowserConfig
from src.openlane.browser import BrowserFactory, BrowserManager


def test_browser_factory_creates_manager(tmp_path: Path) -> None:
    config = BrowserConfig(browser_mode="local")
    factory = BrowserFactory(config=config, project_root=tmp_path, playwright_factory=lambda: object())

    manager = factory.create()

    assert isinstance(manager, BrowserManager)
    assert manager.config is config
    assert manager.project_root == tmp_path

