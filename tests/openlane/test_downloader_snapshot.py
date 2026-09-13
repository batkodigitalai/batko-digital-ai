from pathlib import Path

import pytest

from src.core.storage import ProjectStorage
from src.openlane.downloader import OpenLaneDownloader


def test_openlane_downloader_metadata_with_mock_page() -> None:
    class MockPage:
        url = "https://www.openlane.eu/en/item/11004535"

        def title(self) -> str:
            return "OPENLANE Auction"

        def evaluate(self, script: str) -> str | None:
            return None

    downloader = OpenLaneDownloader(storage=ProjectStorage())

    metadata = downloader.get_page_metadata(MockPage())

    assert metadata.auction_id == "11004535"
    assert metadata.page_id == "11004535"
    assert downloader.is_openlane_auction_page(MockPage()) is True


def test_openlane_downloader_snapshot_smoke(tmp_path: Path) -> None:
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "openlane_snapshot.html"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(fixture.as_uri())
            downloader = OpenLaneDownloader(storage=ProjectStorage(project_root=tmp_path))

            assert downloader.is_openlane_auction_page(page) is True
            snapshot = downloader.create_snapshot(page, snapshot_id="11004535")

            browser.close()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium browser is not installed in this environment")
        raise

    assert snapshot.directory.exists()
    assert (snapshot.directory / "page.html").exists()
    assert (snapshot.directory / "page_title.txt").read_text(encoding="utf-8") == "OPENLANE Test Auction 11004535"
    assert (snapshot.directory / "page_url.txt").read_text(encoding="utf-8") == fixture.as_uri()
    assert (snapshot.directory / "full_page.png").exists()
    assert snapshot.metadata.auction_id == "11004535"

