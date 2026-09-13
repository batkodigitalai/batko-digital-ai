"""Storage directory creation for project and car workspaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.core.config.models import StorageConfig
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class CarWorkspacePaths:
    """Resolved directories for one car workspace."""

    car_id: str
    data_dir: Path
    raw_dir: Path
    reports_dir: Path
    assets_dir: Path
    images_dir: Path
    documents_dir: Path
    output_dir: Path
    archive_dir: Path


class ProjectStorage:
    """Create and resolve project storage paths."""

    def __init__(self, project_root: Path | str = ".", config: StorageConfig | None = None) -> None:
        self.project_root = Path(project_root)
        self.config = config or StorageConfig()

    def ensure_project_directories(self) -> list[Path]:
        """Create top-level storage directories required by Sprint 1."""
        directories = [
            self.resolve_path(self.config.data_dir),
            self.resolve_path(self.config.cars_dir),
            self.resolve_path(self.config.raw_dir),
            self.resolve_path(self.config.assets_dir),
            self.resolve_path(self.config.output_dir),
            self.resolve_path(self.config.previews_dir),
            self.resolve_path(self.config.archive_dir),
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info("Ensured project directory {}", directory)
        return directories

    def create_car_workspace(self, car_id: str) -> CarWorkspacePaths:
        """Create all directories for a car workspace and return their paths."""
        paths = self.get_car_workspace_paths(car_id)
        for directory in [
            paths.data_dir,
            paths.raw_dir,
            paths.reports_dir,
            paths.assets_dir,
            paths.images_dir,
            paths.documents_dir,
            paths.output_dir,
            paths.archive_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info("Ensured car workspace directory {}", directory)
        return paths

    def get_car_workspace_paths(self, car_id: str) -> CarWorkspacePaths:
        """Resolve all directories for a car workspace without creating them."""
        car_data_dir = self.resolve_path(self.config.cars_dir) / car_id
        car_assets_dir = self.resolve_path(self.config.assets_dir) / car_id
        return CarWorkspacePaths(
            car_id=car_id,
            data_dir=car_data_dir,
            raw_dir=car_data_dir / "raw",
            reports_dir=car_data_dir / "reports",
            assets_dir=car_assets_dir,
            images_dir=car_assets_dir / "images",
            documents_dir=car_assets_dir / "documents",
            output_dir=self.resolve_path(self.config.previews_dir) / car_id,
            archive_dir=self.resolve_path(self.config.archive_dir) / car_id,
        )

    def resolve_path(self, path: Path) -> Path:
        """Resolve a storage path against the project root when relative."""
        if path.is_absolute():
            return path
        return self.project_root / path

    def _resolve(self, path: Path) -> Path:
        return self.resolve_path(path)
