# BATKO_AUTO_V4 - Architecture Review & Refactoring

Datum: 2026-06-25
Vetev: `feature/BATKO_AUTO_V4`
Sprint: 5.5

## Souhrn

Projekt je po Sprintu 5 pripraveny pro dalsi rozvoj, ale uz ted je videt nekolik mist, ktera by pri dalsich 100 sprintech zacala bobtnat. V tomto sprintu byly provedeny pouze male refaktoringy bez zmeny verejneho API, chovani nebo vystupu testu.

Nebyla implementovana zadna nova domenova funkce. Nebyly pridany fotografie, PDF, parser, AUTO_V4, GUI, databaze ani Market Engine.

## Projite oblasti

- `src/core/config`
- `src/core/logging`
- `src/core/storage`
- `src/core/download`
- `src/domain/models`
- `src/openlane/browser`
- `src/openlane/downloader`
- `src/openlane/reader`
- `tests`
- `docs/AUTO_V4`

## Nalezene problemy

### 1. OPENLANE downloader pouzival privatni storage API

`OpenLaneDownloader` volal `ProjectStorage._resolve`. To porusovalo hranici mezi moduly a vytvarelo riziko, ze zmena internich storage detailu rozbije snapshot system.

Stav: opraveno.

### 2. AuctionReader mel vice odpovednosti v jednom souboru

`AuctionReader` najednou resil:

- DOM extraction script,
- definici povinnych a volitelnych poli,
- primitivni prevody hodnot,
- validaci,
- mapovani do `Car`,
- export `auction.json`.

To jeste neni kriticke, ale pri dalsim rozsireni o realne OPENLANE selectory, fallbacky nebo offline cteni snapshotu by soubor rychle rostl.

Stav: castecne opraveno. Field kontrakt a primitivni prevody byly oddeleny do `src/openlane/reader/fields.py`.

### 3. DownloadManager koncentruje vice lifecycle odpovednosti

`DownloadManager` dnes drzi vytvareni tasku, spousteni, ruseni, pauzu, obnovu, retry a progress. Pro soucasny rozsah je to akceptovatelne, ale pro photo downloader, PDF downloader, watcher a resume download bude vhodne oddelit orchestrace od executor vrstvy.

Stav: ponechano jako technicky dluh. Refaktor by uz byl vetsim zasahem.

### 4. Snapshot nema manifest

Snapshot uklada HTML, title, URL a screenshot, ale zatim nema jednotny manifest se seznamem souboru, checksumy a stavem zachyceni. To bude problem pro HAR, PDF a fotografie, protoze assety budou potrebovat auditovatelny puvod.

Stav: ponechano pro dalsi sprint.

### 5. Reader je zavisly na zive Playwright Page

Auction reader umi cist pouze z aktualne otevrene page. To je v poradku pro MVP, ale parser/reader by pozdeji mel umet pracovat i ze snapshot `page.html`, aby slo opakovane testovat bez browseru.

Stav: ponechano pro Sprint 6+.

### 6. Datumova pole jsou zatim string

`firstRegistration` a `manufactureDate` jsou v `Car` modelu textova pole. Pro import z ruznych zdroju to je zatim bezpecne, ale AUTO_V4 a Market Engine budou casem potrebovat normalizovane datumy nebo samostatnou normalizacni vrstvu.

Stav: ponechano beze zmeny kvuli kompatibilite.

### 7. Browser vrstva muze rust pres hranici SRP

`BrowserManager` a `BrowserFactory` maji spravne oddelene zakladni role, ale pri pridani watcheru, HAR nebo robustniho session recovery nesmi byt tato logika pridana primo do manageru.

Stav: bez zmeny.

## Duplicity

- Primitivni parsovani integer/float hodnot bylo soucasti `AuctionReader`; bylo presunuto do reader field utility modulu.
- Storage path resolving bylo dostupne jen pres privatni `_resolve`; interni pouziti bylo sjednoceno pres verejne `resolve_path`.
- Zatim nebyly nalezeny cyklicke zavislosti mezi `core`, `domain` a `openlane`.
- `core` neimportuje `openlane`, coz je spravne. Smer zavislosti zustava `openlane -> core/domain`.

## Provedene refaktoringy

### 1. Verejne storage path API

Pridano:

- `ProjectStorage.resolve_path(path: Path) -> Path`

Upraveno:

- `ProjectStorage.ensure_project_directories`
- `ProjectStorage.get_car_workspace_paths`
- `OpenLaneDownloader._snapshot_directory`

Privatni `_resolve` zustal zachovan jako delegace, aby se nezmenilo chovani ani pripadna interni kompatibilita.

### 2. Oddeleni OPENLANE reader field kontraktu

Pridano:

- `src/openlane/reader/fields.py`

Obsahuje:

- `DOM_FIELD_ATTRIBUTE`
- `DOM_FIELD_SELECTOR`
- `FIELD_REQUIREMENTS`
- `build_dom_extraction_script`
- `parse_int`
- `parse_float`

`AuctionReader` zustal verejnym vstupem pro cteni aukce a stale vraci stejny `AuctionReadResult`.

### 3. Test storage API

Pridan test:

- `tests/core/test_storage.py::test_resolve_path_keeps_absolute_and_resolves_relative`

Test overuje, ze nove verejne API zachovava puvodni chovani pro relativni i absolutni cesty.

## Technicky dluh

- `DownloadManager` bude pred realnym stahovanim potrebovat jasne oddelit task orchestration, execution adaptery a persistenci stavu.
- `AuctionReader._export` porad zapisuje JSON primo. Pozdeji muze vzniknout `AuctionExportWriter`, ale ted by to byl zbytecny zasah.
- Snapshot nema manifest ani checksumy.
- Neni definovan asset registry kontrakt pro fotografie, PDF a HAR.
- Neni offline reader nad ulozenym `page.html`.
- `Car` model zatim nema normalizacni vrstvy pro datumy, meny a zeme.
- Coverage CLI vstupu `python -m src` je stale nizke, protoze `src/__main__.py` neni testovany.

## Rizika pro budouci moduly

### Downloader fotografii

Riziko je michani asset download logiky primo do `OpenLaneDownloader`. Fotografie maji mit vlastni modul, vlastni vystupni strukturu a zapis do asset registry, ne byt soucasti aukcniho readeru.

### Downloader PDF

PDF bude potrebovat document metadata, checksum, puvodni URL a vazbu na snapshot. Bez manifestu bude slozite overit, ktere soubory patri ke ktere aukci.

### HAR a network capture

HAR nesmi byt pridany do `AuctionReader`. Patri do samostatne browser/capture infrastruktury, ktera pouze dodava artefakty dalsim modulum.

### Watcher

Watcher bude potrebovat udalosti, opakovatelnost a stav mezi behy. Soucasna download infrastruktura ma event model, ale nema persistenci stavu.

### AUTO_V4

AUTO_V4 vypocty nesmi cist DOM ani Playwright Page. Maji konzumovat pouze normalizovany `Car` model, `auction.json` a budouci trzni vstupy.

### Market Engine

Market Engine bude potrebovat jasne oddelena vstupni data, cenove zdroje, datumy a meny. Soucasne stringove hodnoty jsou vhodne pro import, ne pro finalni vypocty.

## Doporuceni

1. Ve Sprintu 6 nejprve pridat snapshot manifest s checksumy.
2. Potom pridat offline reader nad ulozenym HTML snapshotem.
3. Selector mapping pro realny OPENLANE drzet mimo `AuctionReader`.
4. Pro fotografie a PDF vytvorit samostatne download adaptery, ktere pouzivaji `DownloadManager`, ale nemeni ho na OPENLANE-specializovanou tridu.
5. Pred AUTO_V4 pridat normalizacni vrstvu pro datumy, meny, zeme a jednotky.
6. Watcher resit az po stabilnim manifestu a jasnem stavu download tasku.

## Pripravenost na Sprint 6

Projekt je pripraveny na Sprint 6, pokud Sprint 6 zustane v logickem smeru: manifest, offline snapshot reader, robustnejsi DOM mapping nebo prvni asset registry kontrakt. Nedoporucuje se jeste zacinat s AUTO_V4 vypocty nebo Market Engine, protoze datova normalizace a snapshot audit trail nejsou hotove.

## Testy

Baseline pred refaktoringem:

```text
35 passed
TOTAL coverage: 96%
```

Po refaktoringu storage API:

```text
36 passed
TOTAL coverage: 96%
```

Po refaktoringu reader field kontraktu:

```text
36 passed
TOTAL coverage: 96%
```

## Hodnoceni

| Oblast               | Stav                                      | Znamka |
| -------------------- | ----------------------------------------- | ------ |
| Architektura         | Stabilni zaklad, par rustovych rizik      | B+     |
| Testy                | Zelene, dobre pokryti core/openlane MVP   | A-     |
| Rozsiritelnost       | Dobra, potrebuje manifest a adaptery      | B      |
| Modularity           | Zlepsena, smer zavislosti je spravny      | B+     |
| Dokumentace          | Prubezna a navazuje na sprinty            | A-     |
| Celkova pripravenost | Pripraveno na Sprint 6 s jasnymi hranicemi | B+     |
