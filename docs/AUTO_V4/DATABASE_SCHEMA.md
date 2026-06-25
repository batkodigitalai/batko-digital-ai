# DATABASE_SCHEMA

## Ucel

Definovat budoucí databazove schema na konceptualni urovni. Tento dokument nevytvari databazi ani migrace.

## Odpovednost

- Popisuje entity, vztahy a uloziste pro dlouhodoby vyvoj.
- Umoznuje zacit file-based a pozdeji prejit na databazi bez zmeny architektury.
- Oddeluje datovy model od konkretni technologie databaze.

## Vstupy

- `CAR_DATA_MODEL.md`
- `MARKET_ENGINE.md`
- `REPORT_ENGINE.md`
- lead schema z `ARCHITECTURE.md`
- URL a asset registry.

## Vystupy

- konceptualni schema,
- seznam tabulek/kolekci,
- vztahy mezi entitami,
- pravidla pro primarni a externi klice.

## Verejne API

- `get_entity_schema(entity_name)`
- `validate_record(entity_name, record)`
- `map_file_record_to_database(entity_name, record)`
- `get_relationships(entity_name)`

## Datove struktury

```text
EntitySchema
  name
  primaryKey
  fields
  relationships
  indexes
  retentionPolicy

Relationship
  fromEntity
  toEntity
  type
  required
```

## Zavislosti

- `CAR_DATA_MODEL.md`
- `NAMING_STANDARD.md`
- `AUTO_V4_STANDARD.md`

## Poradi implementace

1. Definovat konceptualni entity.
2. Definovat vztahy mezi entitami.
3. Definovat file-based ulozeni.
4. Definovat mapovani na budouci databazi.
5. Az pozdeji vybrat konkretni databazovou technologii.

