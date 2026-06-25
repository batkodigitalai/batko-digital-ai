# OPENLANE_ENGINE

## Ucel

Definovat modul pro praci se zdroji OPENLANE/AUTO1 na urovni datoveho kontraktu. Tento dokument neni implementaci downloaderu ani parseru.

## Odpovednost

- Popisuje, jaka data system potrebuje ze zdroju OPENLANE/AUTO1.
- Definuje hranici mezi downloaderem, parserem a normalizaci auta.
- Sjednocuje identifikatory aukci a zdrojovych polozek.

## Vstupy

- URL aukce,
- item ID,
- metadata aukce,
- raw HTML/PDF/email data z budoucich modulu,
- manualne opsane udaje.

## Vystupy

- normalizovany `AuctionSourceRecord`,
- zdrojova metadata pro `Car`,
- seznam chybejicich poli,
- varovani k neoverenym datum.

## Verejne API

- `create_source_record(input)`
- `validate_source_record(record)`
- `map_source_to_car(record)`
- `get_missing_openlane_fields(record)`
- `build_source_reference(record)`

## Datove struktury

```text
AuctionSourceRecord
  source
  itemId
  url
  title
  country
  currency
  auctionEndAt
  rawDataReference
  extractedFields
  confidence

OpenlaneFieldMap
  sourceField
  targetField
  required
  transformRule
```

## Zavislosti

- `CAR_DATA_MODEL.md`
- `DOWNLOADER.md`
- `NAMING_STANDARD.md`
- `AUTO_V4_STANDARD.md`

## Poradi implementace

1. Definovat zdrojovy zaznam aukce.
2. Definovat mapovani na `Car`.
3. Pridat validaci chybejicich poli.
4. Az pozdeji pripojit downloader.
5. Az po downloaderu pripojit parser.

## Sprint 5 - Auction Reader MVP

Sprint 5 zavadi DOM-only reader pro jiz otevrenou aukcni stranku.

Pravidla:

- reader prijima existujici Playwright `Page`,
- reader neprovadi login,
- reader neotevira OPENLANE,
- reader nestahuje fotografie ani PDF,
- reader nepouziva HAR ani network capture,
- reader nevyhodnocuje obchodni data,
- reader uklada vysledek do `auction.json`.

## Mapovani poli OPENLANE -> Car

```text
auction_id          -> Car.sourceItemId
auction_id          -> Car.auction.itemId
reference           -> Car.auction.reference
URL                 -> Car.auction.url
title               -> export metadata / snapshot title
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

## Validace poli

Kazde pole je oznaceno jako:

- `required`
- `optional`
- `unknown`

Required pole ve Sprintu 5:

- `auction_id`
- `url`
- `title`
- `make`
- `model`
- `mileage_km`

Optional pole ve Sprintu 5:

- `reference`
- `variant`
- `vin`
- `first_registration`
- `manufacture_date`
- `power_kw`
- `fuel`
- `transmission`
- `color`
- `current_price`
- `currency`
- `vat_mode`
- `country`
- `location`

Unknown pole zustavaji v validation reportu, ale nemapuji se automaticky do `Car`.
