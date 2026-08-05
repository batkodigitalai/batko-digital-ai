# BATKO_AUTO_V4 - Sprint 6 Report

Datum: 2026-06-25
Vetev: `feature/BATKO_AUTO_V4`

## Souhrn

Sprint 6 pridal prvni end-to-end capture workflow pro aukci otevrenou v browseru. System umi z aktivni Playwright `Page` vytvorit archiv ve zvolenem adresari a ulozit vsechny zakladni zdrojove artefakty do `01_Source`.

Sprint neobsahuje fotografie, PDF, HAR, network capture, watcher, OCR, SQLite, GUI, AUTO_V4 ani Market Engine.

## Nove moduly

- `src/openlane/capture/__init__.py`
- `src/openlane/capture/models.py`
- `src/openlane/capture/service.py`

## Nove tridy

- `CaptureService`
- `CaptureStatus`
- `ManifestFile`
- `CaptureManifest`
- `CaptureResult`

## Novy workflow

```text
python -m src capture --output-dir <cilovy_adresar>
```

Interni tok:

```text
BrowserFactory / SessionManager
  |
  v
aktivni Playwright Page
  |
  v
CaptureService
  |
  v
AuctionReader + OpenLaneDownloader
  |
  v
01_Source archiv
```

Finalni obsah:

```text
01_Source/
  page.html
  page_url.txt
  page_title.txt
  auction.json
  manifest.json
  capture.log
  full_page.png
```

## Manifest

`manifest.json` obsahuje:

- `capturedAt`,
- `appVersion`,
- `commitHash`,
- `status`,
- `url`,
- `auctionId`,
- `files`,
- `missingRequired`.

Stavy:

- `SUCCESS`: required pole jsou kompletni.
- `PARTIAL`: capture probehl, ale chybi required pole.

Manifest obsahuje SHA256 pro archivni artefakty vytvorene pred manifestem. `manifest.json` nehashuje sam sebe, protoze samo-referencni checksum neni stabilni.

## Testy

Pridane testy:

- `tests/openlane/test_capture_service.py::test_capture_service_creates_archive_manifest_and_checksums`
- `tests/openlane/test_capture_service.py::test_capture_service_marks_partial_when_required_field_is_missing`

Testy overuji:

- vznik adresare `01_Source`,
- vznik vsech pozadovanych souboru,
- odstraneni interniho `_work` adresare,
- stav `SUCCESS`,
- stav `PARTIAL`,
- spravne `auctionId`,
- spravne checksumy SHA256,
- prepsani snapshot cest v `auction.json` na finalni archivni cesty.

## Coverage

Posledni beh:

```text
38 passed
TOTAL coverage: 93%
```

Nove moduly:

- `src/openlane/capture/__init__.py`: 100%
- `src/openlane/capture/models.py`: 100%
- `src/openlane/capture/service.py`: 90%

## Zname omezeni

- CLI capture neni pokryty automatickym testem, protoze vyzaduje realny browser runtime.
- Manifest neobsahuje vlastni SHA256.
- Capture zatim nepodporuje fotografie, PDF, HAR ani network capture.
- Reader stale pracuje primarne se zivou Playwright `Page`, ne offline ze snapshot `page.html`.
- Capture nevytvari databazovy zaznam ani zadny GUI vystup.

## Pripravenost na Sprint 7

Projekt je pripraveny na dalsi krok nad archivnim formatem.

Doporuceni pro Sprint 7:

1. Stabilizovat manifest kontrakt.
2. Pridat offline reader nad ulozenym `page.html`.
3. Pripravit asset registry kontrakt pro fotografie a PDF.
4. Rozhodnout, zda manifest podepisovat externim checksum/signature souborem.
5. Nezacinat Market Engine ani AUTO_V4 vypocty pred stabilni normalizaci dat.
