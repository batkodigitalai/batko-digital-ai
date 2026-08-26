"""Persistent Chrome profile management."""

from __future__ import annotations

from pathlib import Path

from src.core.config.models import BrowserConfig
from src.core.logging import get_logger

logger = get_logger(__name__)


class ProfileManager:
    """Manage browser profile directories without performing login."""

    def __init__(self, project_root: Path | str = ".", config: BrowserConfig | None = None) -> None:
        self.project_root = Path(project_root)
        self.config = config or BrowserConfig()

    def profile_exists(self, profile_name: str | None = None) -> bool:
        """Return whether a profile directory exists."""
        exists = self.get_profile_path(profile_name).exists()
        logger.info("Profile exists check: {} -> {}", self.get_profile_path(profile_name), exists)
        return exists

    def create_profile(self, profile_name: str | None = None) -> Path:
        """Create a profile directory if missing."""
        profile_path = self.get_profile_path(profile_name)
        profile_path.mkdir(parents=True, exist_ok=True)
        logger.info("Created browser profile directory {}", profile_path)
        return profile_path

    def load_profile(self, profile_name: str | None = None) -> Path:
        """Return an existing profile path, creating it if needed."""
        profile_path = self.create_profile(profile_name)
        logger.info("Loaded browser profile {}", profile_path)
        return profile_path

    def get_profile_path(self, profile_name: str | None = None) -> Path:
        """Resolve a profile path."""
        base_path = self.config.chrome_profile
        if not base_path.is_absolute():
            base_path = self.project_root / base_path
        if profile_name:
            return base_path.parent / profile_name
        return base_path

