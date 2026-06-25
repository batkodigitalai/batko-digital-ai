# DOWNLOADER

## Ucel

Definovat budouci modul pro stahovani zdrojovych dat a assetu. Tento dokument neimplementuje downloader.

## Odpovednost

- Popisuje hranice downloaderu.
- Downloader pouze ziskava raw data, neprovadi obchodni logiku.
- Parser a normalizace patri do jinych modulu.

## Vstupy

- URL aukce,
- seznam asset URL,
- konfigurace zdroje,
- cilove uloziste raw dat,
- pravidla rate limitu a bezpecnosti.

## Vystupy

- raw HTML/PDF/image soubory,
- download manifest,
- stav stazeni,
- chyby a varovani.

## Verejne API

- `create_download_job(source_ref)`
- `run_download_job(job_id)`
- `get_download_status(job_id)`
- `list_downloaded_assets(job_id)`
- `build_download_manifest(job_id)`

## Datove struktury

```text
DownloadJob
  id
  source
  sourceUrl
  status
  requestedAssets
  downloadedFiles
  errors
  createdAt

DownloadManifest
  jobId
  files
  checksums
  sourceReferences
  warnings
```

## Zavislosti

- `OPENLANE_ENGINE.md`
- `CAR_DATA_MODEL.md`
- `NAMING_STANDARD.md`
- `AUTO_V4_STANDARD.md`

## Poradi implementace

1. Definovat download job.
2. Definovat manifest.
3. Definovat uloziste raw dat.
4. Definovat bezpecnostni pravidla.
5. Az v pozdejsi fazi implementovat konkretni stahovani.

## Sprint 4 - Page snapshot

Sprint 4 zavadi prvni funkcni, ale porad velmi omezeny downloader MVP:

- pracuje pouze s jiz otevrenou Playwright `Page`,
- neprovadi login,
- neotevira OPENLANE URL,
- nestahuje fotografie,
- nestahuje PDF,
- nepouziva HAR ani network capture,
- neparsuje obchodni data.

### Snapshot flow

```text
SessionManager poskytne aktivni Page
        |
        v
OpenLaneDownloader overi, ze stranka vypada jako OPENLANE aukce
        |
        v
OpenLaneDownloader vytvori PageMetadata
        |
        v
DownloadManager pripravi cilovy adresar
        |
        v
Snapshot ulozi:
  page.html
  page_title.txt
  page_url.txt
  full_page.png
```

### PageMetadata

```text
PageMetadata
  url
  title
  timestamp
  pageId
  auctionId
```

### PageSnapshot

```text
PageSnapshot
  snapshotId
  directory
  metadata
  htmlPath
  titlePath
  urlPath
  screenshotPath
```

## Využiti ve Sprintu 5

Sprint 5 muze navazat na snapshot jako na raw vstup:

1. Definovat manifest snapshotu.
2. Pridat checksumy pro ulozene soubory.
3. Pridat audit udalosti snapshotu.
4. Pripravit parser kontrakt, ktery bude cist pouze ulozene `page.html`, ne zivou stranku.
5. Zachovat pravidlo: parser nesmi byt soucast downloaderu.

## Sprint 6 - Capture archiv

Sprint 6 pridava end-to-end capture workflow nad jiz existujicim snapshotem a readerem.

Pravidla:

- capture pracuje s jiz otevrenou Playwright `Page`,
- neprovadi login,
- nestahuje fotografie,
- nestahuje PDF,
- nepouziva HAR ani network capture,
- nevykonava AUTO_V4 ani Market Engine.

### Capture workflow

```text
Aktivni Page
  |
  v
CaptureService vytvori capture adresar
  |
  v
AuctionReader vytvori snapshot a auction.json
  |
  v
CaptureService zabali finalni archiv do 01_Source
  |
  v
manifest.json + capture.log
```

### Finalni soubory v `01_Source`

```text
page.html
page_url.txt
page_title.txt
auction.json
manifest.json
capture.log
full_page.png
```

### Manifest

`manifest.json` obsahuje:

- datum a cas capture,
- verzi aplikace,
- commit hash, pokud je dostupny,
- URL,
- `auction_id`,
- stav `SUCCESS` nebo `PARTIAL`,
- chybejici required pole,
- seznam vytvorenych archivnich souboru,
- SHA256 pro archivni artefakty vytvorene pred manifestem.

`manifest.json` neobsahuje vlastni SHA256, protoze checksum souboru nelze stabilne ulozit do stejneho souboru, ktery se hashovanim meni.
