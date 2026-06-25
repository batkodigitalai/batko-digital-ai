import json
from pathlib import Path

import pytest

from src.core.download import calculate_sha256
from src.openlane.capture import CaptureService, CaptureStatus


def test_capture_service_creates_archive_manifest_and_checksums(tmp_path: Path) -> None:
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "openlane_auction_reader.html"
    capture_dir = tmp_path / "capture"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(fixture.as_uri())

            result = CaptureService(project_root=tmp_path).capture(page, output_dir=capture_dir)

            browser.close()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium browser is not installed in this environment")
        raise

    source_dir = capture_dir / "01_Source"
    expected_files = {
        "page.html",
        "page_url.txt",
        "page_title.txt",
        "auction.json",
        "manifest.json",
        "capture.log",
        "full_page.png",
    }

    assert result.source_dir == source_dir
    assert source_dir.exists()
    assert {path.name for path in source_dir.iterdir()} == expected_files
    assert not (capture_dir / "_work").exists()

    manifest = json.loads((source_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == CaptureStatus.SUCCESS.value
    assert manifest["auctionId"] == "11004535"
    assert manifest["url"] == fixture.as_uri()
    assert manifest["missingRequired"] == []
    assert manifest["appVersion"] == "0.1.0"
    assert manifest["capturedAt"]
    assert "commitHash" in manifest

    manifest_files = {entry["path"]: entry for entry in manifest["files"]}
    assert set(manifest_files) == expected_files - {"manifest.json"}
    for relative_path, entry in manifest_files.items():
        file_path = source_dir / relative_path
        assert entry["sha256"] == calculate_sha256(file_path)
        assert entry["sizeBytes"] == file_path.stat().st_size

    auction_payload = json.loads((source_dir / "auction.json").read_text(encoding="utf-8"))
    assert auction_payload["validation"]["isValid"] is True
    assert auction_payload["snapshot"]["directory"] == str(source_dir)
    assert auction_payload["snapshot"]["htmlPath"] == str(source_dir / "page.html")


def test_capture_service_marks_partial_when_required_field_is_missing(tmp_path: Path) -> None:
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    capture_dir = tmp_path / "partial-capture"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(
                """
                <!doctype html>
                <html>
                  <head>
                    <title>OPENLANE Partial Auction</title>
                    <meta name="auction-id" content="22004535" />
                  </head>
                  <body>
                    <div data-openlane-field="make">Skoda</div>
                    <div data-openlane-field="mileage_km">42 000 km</div>
                  </body>
                </html>
                """
            )

            result = CaptureService(project_root=tmp_path).capture(page, output_dir=capture_dir)

            browser.close()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium browser is not installed in this environment")
        raise

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == CaptureStatus.PARTIAL.value
    assert "model" in manifest["missingRequired"]
    assert result.read_result.validation.is_valid is False
