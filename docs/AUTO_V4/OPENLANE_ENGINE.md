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

