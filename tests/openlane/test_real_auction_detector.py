from pathlib import Path

import pytest

from src.openlane.real import OpenLaneAuctionDetectionError, RealAuctionDetector, SelectorRegistry, SelectorValidator


def test_selector_registry_loads_compatibility_versions() -> None:
    registry = SelectorRegistry(project_root=Path(__file__).resolve().parents[2])

    assert registry.versions() == ["v1", "v2", "v3"]
    assert registry.get("v1").fields["auction_id"]
    assert registry.get("v2").auction_markers
    assert registry.get("v3").url_patterns == ["openlane"]


def test_selector_validator_reports_existing_selectors_with_fixture() -> None:
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    project_root = Path(__file__).resolve().parents[2]
    fixture = project_root / "tests" / "fixtures" / "openlane_auction_reader.html"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(fixture.as_uri())

            report = SelectorValidator(SelectorRegistry(project_root=project_root)).validate(page)

            browser.close()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium browser is not installed in this environment")
        raise

    existing = {(check.group, check.name, check.selector) for check in report.existing_selectors()}
    assert ("auctionMarkers", "auction", "[data-openlane-auction-id]") in existing
    assert ("fields", "auction_id", "[data-openlane-field='auction_id']") in existing
    assert ("fields", "reference", "[data-openlane-field='reference']") in existing


def test_real_auction_detector_reads_metadata_from_fixture() -> None:
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    project_root = Path(__file__).resolve().parents[2]
    fixture = project_root / "tests" / "fixtures" / "openlane_auction_reader.html"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(fixture.as_uri())

            result = RealAuctionDetector(project_root=project_root).detect(page)

            browser.close()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium browser is not installed in this environment")
        raise

    assert result.auction_id == "11004535"
    assert result.reference == "OL-REF-11004535"
    assert result.title == "Volkswagen Passat Variant 2.0 TDI Business"
    assert result.url == fixture.as_uri()
    assert result.selector_version == "v1"
    assert result.selector_report.existing_selectors()


def test_real_auction_detector_returns_clear_error_for_non_auction(tmp_path: Path) -> None:
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content("<html><head><title>Not an auction</title></head><body>No auction here</body></html>")

            with pytest.raises(OpenLaneAuctionDetectionError, match="nevypada jako aukce OPENLANE"):
                RealAuctionDetector(project_root=Path(__file__).resolve().parents[2]).detect(page)

            browser.close()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium browser is not installed in this environment")
        raise
