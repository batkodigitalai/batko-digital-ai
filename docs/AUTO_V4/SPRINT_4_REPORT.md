# BATKO_AUTO_V4 - Sprint 4 Report

Datum: 2026-06-25
Vetev: `feature/BATKO_AUTO_V4`

## Souhrn

Sprint 4 pridal prvni OPENLANE downloader MVP pro praci s jiz otevrenou Playwright `Page`. Downloader pouze overi, ze stranka vypada jako OPENLANE aukce, nacte zakladni metadata a ulozi snapshot DOMu, URL, titulku a full-page screenshotu.

Neobsahuje login, parser, scraping obchodnich dat, fotografie, PDF, HAR, network capture, databazi, GUI ani AUTO_V4 vypocty.

## Nove tridy

- `OpenLaneDownloader`
- `PageMetadata`
- `PageSnapshot`

## Nove testy

- `tests/openlane/test_downloader_snapshot.py::test_openlane_downloader_metadata_with_mock_page`
- `tests/openlane/test_downloader_snapshot.py::test_openlane_downloader_snapshot_smoke`

Smoke test:

- otevira lokalni fixture `tests/fixtures/openlane_snapshot.html`,
- nepouziva internet,
- nepripojuje se na OPENLANE,
- vytvari snapshot do docasneho storage adresare,
- overuje vznik `page.html`, `page_title.txt`, `page_url.txt`, `full_page.png`.

## Coverage

Posledni beh:

```text
34 passed
TOTAL coverage: 88%
```

Nove moduly:

- `src/openlane/downloader/__init__.py`: 100%
- `src/openlane/downloader/models.py`: 100%
- `src/openlane/downloader/downloader.py`: 99%

## Seznam vytvorenych souboru

- `src/openlane/downloader/__init__.py`
- `src/openlane/downloader/models.py`
- `src/openlane/downloader/downloader.py`
- `tests/fixtures/openlane_snapshot.html`
- `tests/openlane/test_downloader_snapshot.py`
- `docs/AUTO_V4/SPRINT_4_REPORT.md`

## Aktualizovane soubory

- `docs/AUTO_V4/DOWNLOADER.md`

## Vystupy snapshotu

Snapshot uklada:

- `page.html`
- `page_title.txt`
- `page_url.txt`
- `full_page.png`

Snapshot metadata:

- `url`
- `title`
- `timestamp`
- `pageId`
- `auctionId`

## Znama omezeni

- Downloader pracuje jen s jiz otevrenou `Page`.
- Downloader sam neotevira OPENLANE.
- Downloader neprovadi login.
- Downloader neparsuje obchodni data.
- Screenshot pouziva Playwright `page.screenshot`.
- Snapshot manifest zatim neni persistovan jako samostatny JSON.
- Checksumy snapshot souboru zatim nejsou soucasti `PageSnapshot`.
- Neni implementovano stahovani fotografii ani PDF.

## Pripravenost pro Sprint 5

Sprint 5 muze navazat bez prepisu temito kroky:

1. Pridat snapshot manifest pro ulozene soubory.
2. Doplnit checksumy pro `page.html`, `page_title.txt`, `page_url.txt`, `full_page.png`.
3. Zavest audit udalosti snapshotu pres Download Infrastructure.
4. Pripravit parser kontrakt, ktery bude cist ulozene `page.html`, ne zivou Playwright page.
5. Zachovat pravidlo: parser nesmi byt soucast `OpenLaneDownloader`.

