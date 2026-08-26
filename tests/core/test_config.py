from pathlib import Path

from src.core.config import AppConfig, ConfigManager, load_config, save_config


def test_load_config_creates_default_file(tmp_path: Path) -> None:
    config_path = Path("config/test_config.json")
    config = load_config(project_root=tmp_path, config_path=config_path)

    assert isinstance(config, AppConfig)
    assert config.project_name == "BATKO_AUTO_V4"
    assert config.browser.browser_mode == "local"
    assert config.browser.headless is True
    assert (tmp_path / config_path).exists()


def test_config_manager_saves_changes(tmp_path: Path) -> None:
    manager = ConfigManager(project_root=tmp_path, config_path="config/test_config.json")
    config = manager.load()
    config.environment = "test"

    manager.save(config)
    loaded = manager.load()

    assert loaded.environment == "test"


def test_save_config_helper_persists_config(tmp_path: Path) -> None:
    config = AppConfig(environment="ci")
    save_config(config, project_root=tmp_path, config_path="config/helper_config.json")

    loaded = load_config(project_root=tmp_path, config_path="config/helper_config.json")

    assert loaded.environment == "ci"
