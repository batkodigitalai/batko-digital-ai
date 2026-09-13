from pathlib import Path

from src.core.config.models import BrowserConfig
from src.openlane.browser import ProfileManager


def test_profile_manager_creates_and_loads_profile(tmp_path: Path) -> None:
    config = BrowserConfig(chrome_profile=Path("profiles/chrome/test"))
    manager = ProfileManager(project_root=tmp_path, config=config)

    assert manager.profile_exists() is False

    profile_path = manager.create_profile()

    assert profile_path == tmp_path / "profiles" / "chrome" / "test"
    assert profile_path.exists()
    assert manager.profile_exists() is True
    assert manager.load_profile() == profile_path


def test_profile_manager_resolves_named_profile(tmp_path: Path) -> None:
    config = BrowserConfig(chrome_profile=Path("profiles/chrome/default"))
    manager = ProfileManager(project_root=tmp_path, config=config)

    assert manager.get_profile_path("work") == tmp_path / "profiles" / "chrome" / "work"

