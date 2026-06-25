from pathlib import Path

from src.core.config.models import StorageConfig
from src.core.storage import ProjectStorage, build_car_id, normalize_slug


def test_normalize_slug() -> None:
    assert normalize_slug("OPENLANE #11004535") == "openlane_11004535"
    assert normalize_slug("   ") == "unknown"


def test_build_car_id() -> None:
    assert build_car_id("OPENLANE", "11004535") == "openlane_11004535"


def test_ensure_project_directories(tmp_path: Path) -> None:
    storage = ProjectStorage(project_root=tmp_path, config=StorageConfig())
    directories = storage.ensure_project_directories()

    assert directories
    assert all(directory.exists() for directory in directories)
    assert (tmp_path / "30_DATA" / "cars").exists()
    assert (tmp_path / "50_ASSETS" / "cars").exists()


def test_create_car_workspace_creates_all_directories(tmp_path: Path) -> None:
    storage = ProjectStorage(project_root=tmp_path, config=StorageConfig())
    paths = storage.create_car_workspace("openlane_11004535")

    assert paths.data_dir == tmp_path / "30_DATA" / "cars" / "openlane_11004535"
    assert paths.raw_dir.exists()
    assert paths.reports_dir.exists()
    assert paths.images_dir.exists()
    assert paths.documents_dir.exists()
    assert paths.output_dir.exists()
    assert paths.archive_dir.exists()

