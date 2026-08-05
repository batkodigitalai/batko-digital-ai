"""Selector registry and validator for real OPENLANE pages."""

from __future__ import annotations

import json
from pathlib import Path

from src.core.logging import get_logger
from src.openlane.real.models import SelectorCheck, SelectorConfig, SelectorValidationReport, SelectorVersion

DEFAULT_SELECTOR_PATH = Path("config/selectors.yaml")

logger = get_logger(__name__)


class SelectorRegistry:
    """Load versioned OPENLANE selectors from config/selectors.yaml."""

    def __init__(self, project_root: Path | str = ".", selector_path: Path | str = DEFAULT_SELECTOR_PATH) -> None:
        self.project_root = Path(project_root)
        self.selector_path = self._resolve(selector_path)
        self.config = self._load()

    def get(self, version: str = "v1") -> SelectorVersion:
        """Return selectors for one OPENLANE compatibility version."""
        try:
            return self.config.versions[version]
        except KeyError as exc:
            raise KeyError(f"Unknown OPENLANE selector version: {version}") from exc

    def versions(self) -> list[str]:
        """Return supported selector versions."""
        return list(self.config.versions)

    def _load(self) -> SelectorConfig:
        data = json.loads(self.selector_path.read_text(encoding="utf-8"))
        logger.info("Loaded OPENLANE selector registry {}", self.selector_path)
        return SelectorConfig.model_validate(data)

    def _resolve(self, path: Path | str) -> Path:
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return self.project_root / candidate


class SelectorValidator:
    """Check configured selectors against a Playwright page."""

    def __init__(self, registry: SelectorRegistry) -> None:
        self.registry = registry

    def validate(self, page, version: str = "v1") -> SelectorValidationReport:
        """Return a selector existence report for the active page."""
        selectors = self.registry.get(version)
        checks: list[SelectorCheck] = []
        for selector in selectors.auction_markers:
            checks.append(self._check(page, version, "auctionMarkers", "auction", selector))
        for field, field_selectors in selectors.fields.items():
            for selector in field_selectors:
                checks.append(self._check(page, version, "fields", field, selector))
        report = SelectorValidationReport(
            selectorFile=self.registry.selector_path,
            activeVersion=version,
            checks=checks,
        )
        logger.info(
            "Selector validation for {}: {} present, {} missing",
            version,
            len(report.existing_selectors()),
            len(report.missing_selectors()),
        )
        return report

    @staticmethod
    def _check(page, version: str, group: str, name: str, selector: str) -> SelectorCheck:
        try:
            count = page.locator(selector).count()
        except Exception:
            count = 0
        return SelectorCheck(version=version, group=group, name=name, selector=selector, count=count)
