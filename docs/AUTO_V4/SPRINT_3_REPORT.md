# BATKO_AUTO_V4 - Sprint 3 Report

Datum: 2026-06-25
Vetev: `feature/BATKO_AUTO_V4`

## Souhrn

Sprint 3 pridal univerzalni download infrastrukturu v `src/core/download/`. Implementace neresi konkretni downloader, nepristupuje k siti, nepouziva Playwright download, nepracuje s OPENLANE, fotografiemi, PDF, HTML, HAR, parserem, loginem, CDP, databazi ani GUI.

## Nove moduly

- `src/core/download/__init__.py`
- `src/core/download/models.py`
- `src/core/download/progress.py`
- `src/core/download/events.py`
- `src/core/download/queue.py`
- `src/core/download/manager.py`
- `src/core/download/retry.py`
- `src/core/download/checksum.py`

## Nove tridy

- `DownloadStatus`
- `DownloadJob`
- `DownloadResult`
- `DownloadProgress`
- `DownloadEventType`
- `DownloadEvent`
- `DownloadQueue`
- `DownloadManager`
- `RetryPolicy`

## Nove utility

- `calculate_sha256`
- `calculate_md5`
- `calculate_crc32`

## Implementovane schopnosti

### DownloadManager

- vytvori download task,
- pripravi cilovy adresar pres existujici `ProjectStorage`,
- spusti task bez realneho stahovani,
- zrusi task,
- pozastavi task,
- obnovi task,
- sleduje stav tasku,
- emituje udalosti,
- aktualizuje progress.

### DownloadQueue

- FIFO pro stejnou prioritu,
- priorita pres nizsi cislo jako vyssi prioritu,
- retry requeue s navysenim `retry_count`.

### DownloadEvents

- `started`
- `finished`
- `cancelled`
- `failed`
- `retry`
- `progress`

### RetryPolicy

- obecne `can_retry`,
- vypocet dalsiho delaye,
- bez napojeni na konkretni downloader.

### Progress

- procenta 0-100,
- ETA,
- rychlost,
- zbyvajici velikost,
- stazena velikost,
- celkova velikost.

## Testy

Pridane testy:

- `tests/core/test_download_models.py`
- `tests/core/test_download_queue.py`
- `tests/core/test_download_manager.py`
- `tests/core/test_download_checksum_retry.py`

Posledni beh:

```text
32 passed
TOTAL coverage: 86%
```

Testy jsou pouze unit testy. Nepouzivaji sit, Chrome, CDP, Playwright download ani OPENLANE.

## Coverage

Celkovy coverage po Sprintu 3:

```text
TOTAL 86%
```

Core download moduly:

- `checksum.py`: 100%
- `events.py`: 100%
- `models.py`: 100%
- `progress.py`: 100%
- `queue.py`: 100%
- `retry.py`: 100%
- `manager.py`: 96%

## Znama omezeni

- `run_task` pouze meni stav tasku a emituje udalosti; nestahuje data.
- Neexistuje konkretni downloader backend.
- Neexistuje download manifest persistence.
- Neexistuje paralelni worker.
- Neexistuje rate limiting.
- Neexistuje resume realneho souboru.
- Neexistuje network capture ani HAR.
- Checksum utility pocitaji hashe pouze pro existujici lokalni soubor.
- Retry policy nevykonava sleep ani scheduling.

## Pripravenost na Sprint 4

Sprint 4 muze bez prepisu navazat jednim z techto smeru:

1. Definovat download manifest a jeho file-based uloziste.
2. Pridat worker rozhrani pro konkretni downloader implementaci, stale bez OPENLANE.
3. Pridat integraci download tasku do workflow v `AUTO_V4_CORE`.
4. Pridat persistentni audit udalosti.
5. Pridat konfiguraci retry a download queue do `AppConfig`.

Doporuceni: pred implementaci konkretniho OPENLANE downloaderu nejdrive doplnit manifest a worker rozhrani, aby se sitova cast nedostala primo do `DownloadManager`.

