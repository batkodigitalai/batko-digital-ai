# BATKO_AUTO_V4 - Sprint 5 Report

Datum: 2026-06-25
Vetev: `feature/BATKO_AUTO_V4`

## Souhrn

Sprint 5 pridal OPENLANE Auction Reader MVP. Reader pracuje pouze s DOM aktualne otevrene aukcni stranky, vytvori snapshot pomoci existujiciho snapshot systemu a ulozi zakladni aukcni data do jednotneho `Car` modelu. Vystupem je `auction.json`.

Neobsahuje fotografie, PDF, HAR, network capture, GUI, SQLite, AUTO_V4 vypocty, Market Engine, OCR ani watcher.

## Nove implementovane tridy

- `AuctionReader`
- `FieldRequirement`
- `FieldValidation`
- `ReadValidation`
- `AuctionReadResult`

Rozsirene existujici modely:

- `Car`
- `Auction`

## Mapovana pole

```text
auction_id          -> Car.sourceItemId
auction_id          -> Car.auction.itemId
reference           -> Car.auction.reference
URL                 -> Car.auction.url
title               -> snapshot/export metadata
znacka              -> Car.make
model               -> Car.model
varianta            -> Car.variant
VIN                 -> Car.vin
prvni registrace    -> Car.firstRegistration
datum vyroby        -> Car.manufactureDate
najezd              -> Car.mileageKm
vykon               -> Car.powerKw
palivo              -> Car.fuel
prevodovka          -> Car.transmission
barva               -> Car.color
aktualni cena       -> Car.auction.currentBid
mena                -> Car.auction.currency
rezim DPH           -> Car.auction.vatMode
zeme                -> Car.auction.country
lokace vozidla      -> Car.auction.location
```

## Fixture

- `tests/fixtures/openlane_auction_reader.html`

Fixture obsahuje lokální OPENLANE-like DOM s atributy `data-openlane-field`. Test nepouziva internet a nepripojuje se na OPENLANE.

## Testy

Pridany test:

- `tests/openlane/test_auction_reader.py::test_auction_reader_smoke_with_local_fixture`

Test overuje:

- nacteni vsech pozadovanych poli,
- mapovani do `Car`,
- vytvoreni `auction.json`,
- propojeni se snapshotem,
- validaci required/optional poli.

## Coverage

Posledni beh:

```text
35 passed
TOTAL coverage: 96%
```

Nove moduly:

- `src/openlane/reader/__init__.py`: 100%
- `src/openlane/reader/models.py`: 100%
- `src/openlane/reader/reader.py`: 93%

## Vytvorene soubory

- `src/openlane/reader/__init__.py`
- `src/openlane/reader/models.py`
- `src/openlane/reader/reader.py`
- `tests/fixtures/openlane_auction_reader.html`
- `tests/openlane/test_auction_reader.py`
- `docs/AUTO_V4/SPRINT_5_REPORT.md`

## Aktualizovane soubory

- `src/domain/models/car.py`
- `docs/AUTO_V4/OPENLANE_ENGINE.md`
- `docs/AUTO_V4/CAR_DATA_MODEL.md`

## Znama omezeni

- Reader pouziva jednoduchy DOM kontrakt `data-openlane-field`.
- Reader neparsuje realne OPENLANE layout varianty mimo tento kontrakt.
- Reader nestahuje fotografie ani PDF.
- Reader nepouziva network capture ani HAR.
- Reader nevykonava obchodni vyhodnoceni.
- `auction.json` zatim nema checksumy snapshot souboru.
- Validace rozlisuje required/optional/unknown, ale nema zatim severity ani recovery navrhy.

## Pripravenost na Sprint 6

Sprint 6 muze navazat temito kroky:

1. Pridat robustnejsi mapping DOM selectoru pro realne OPENLANE layouty.
2. Oddelit field mapping do konfigurace, aby nebyl napevno v readeru.
3. Pridat snapshot manifest s checksumy.
4. Pridat cteni ze snapshot `page.html`, aby parser/reader nemusel pracovat se zivou page.
5. Pridat report missing fields pro rucni doplneni.

## Architektonicka seberevize

### Co je pripravene pro dalsi rozsireni

- Browser Foundation uz umi dodat aktivni `Page`.
- Snapshot system uklada DOM, URL, title a screenshot.
- Download Infrastructure umi pripravit cilove adresare a task lifecycle.
- `AuctionReader` vraci jednotny `Car` model a nevytvari paralelni model vozidla.
- `auction.json` ma jasnou strukturu: `schemaVersion`, `snapshot`, `validation`, `car`.
- Validace required/optional/unknown je oddelena od mapovani do `Car`.

### Co refaktorovat pred Sprintem 6

- Presunout `FIELD_REQUIREMENTS` a DOM field mapping do samostatne konfigurace nebo mapovaciho modulu.
- Nahradit pouziti jednoducheho `data-openlane-field` kontraktu realnym selector mappingem az po analyzu ulozenych snapshotu.
- Pridat verejnou storage metodu pro snapshot/raw cesty, aby `OpenLaneDownloader` nepouzival interní `_resolve`.
- Rozhodnout, zda `firstRegistration` a `manufactureDate` maji zustat stringy nebo prejit na typ `date`.

