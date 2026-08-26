import json
from pathlib import Path

import pytest

from src.core.storage import ProjectStorage
from src.openlane.downloader import OpenLaneDownloader
from src.openlane.reader import AuctionReader, FieldRequirement


def test_auction_reader_smoke_with_local_fixture(tmp_path: Path) -> None:
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    fixture = Path(__file__).resolve().parents[1] / "fixtures" / "openlane_auction_reader.html"

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(fixture.as_uri())
            storage = ProjectStorage(project_root=tmp_path)
            downloader = OpenLaneDownloader(storage=storage)
            reader = AuctionReader(downloader=downloader)

            result = reader.read_current_auction(page, snapshot_id="11004535")

            browser.close()
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            pytest.skip("Playwright Chromium browser is not installed in this environment")
        raise

    car = result.car
    assert car.source_item_id == "11004535"
    assert car.id == "openlane_11004535"
    assert car.make == "Volkswagen"
    assert car.model == "Passat"
    assert car.variant == "Variant 2.0 TDI Business"
    assert car.vin == "WVWZZZ3CZLE123456"
    assert car.first_registration == "2021-05-17"
    assert car.manufacture_date == "2021-03-01"
    assert car.mileage_km == 82450
    assert car.power_kw == 147
    assert car.fuel == "Diesel"
    assert car.transmission == "Automatic"
    assert car.color == "Blue metallic"
    assert car.auction is not None
    assert car.auction.reference == "OL-REF-11004535"
    assert car.auction.current_bid == 18500
    assert car.auction.currency == "EUR"
    assert car.auction.vat_mode == "VAT deductible"
    assert car.auction.country == "Germany"
    assert car.auction.location == "DE - Berlin"

    assert result.validation.is_valid is True
    assert result.validation.missing_required() == []
    auction_id_validation = next(field for field in result.validation.fields if field.field == "auction_id")
    assert auction_id_validation.requirement is FieldRequirement.REQUIRED
    assert auction_id_validation.present is True

    assert result.auction_json_path.exists()
    payload = json.loads(result.auction_json_path.read_text(encoding="utf-8"))
    assert payload["car"]["sourceItemId"] == "11004535"
    assert payload["car"]["auction"]["reference"] == "OL-REF-11004535"
    assert payload["validation"]["isValid"] is True
    assert payload["snapshot"]["snapshotId"] == "11004535"

