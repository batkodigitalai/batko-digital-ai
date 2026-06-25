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

