# CAR_DATA_MODEL

## Ucel

Definovat jednotny datovy model auta, aukce, stavu vozidla, dokumentu, assetu, cen a publikacnich metadat.

## Odpovednost

- Je zdrojem pravdy pro vsechny moduly pracujici s vozidly.
- Oddeluje data auta od HTML vystupu.
- Umoznuje validaci, scoring, pricing, reporty a generovani nabidek.

## Vstupy

- manualni zadani auta,
- data z OPENLANE/AUTO1,
- budouci downloader,
- budouci parser,
- existujici HTML nabidky jako reference,
- fotky a dokumenty vozidla.

## Vystupy

- normalizovany zaznam auta,
- seznam povinnych a volitelnych poli,
- schema pro validaci,
- metadata pro publikaci.

## Verejne API

- `validate_car(car)`
- `normalize_car(raw_car)`
- `get_car(car_id)`
- `merge_car_patch(car_id, patch)`
- `get_required_fields(context)`

## Datove struktury

```text
Car
  id
  source
  sourceItemId
  make
  model
  variant
  year
  mileageKm
  fuel
  transmission
  powerKw
  vin
  auction
  condition
  pricing
  assets
  documents
  publication

Auction
  platform
  itemId
  url
  country
  currency
  currentBid
  auctionEndAt

Condition
  damageSummary
  serviceHistory
  documentsAvailable
  riskNotes

Publication
  status
  canonicalPath
  generatedAt
  pageTypes
```

## Zavislosti

- `NAMING_STANDARD.md`
- `DATABASE_SCHEMA.md`
- `OPENLANE_ENGINE.md`
- `MARKET_ENGINE.md`
- `REPORT_ENGINE.md`

## Poradi implementace

1. Definovat minimalni `Car`.
2. Pridat `Auction` a `Condition`.
3. Pridat pricing a market vazby.
4. Pridat publikacni metadata.
5. Az potom napojovat downloader, parser a generatory.

