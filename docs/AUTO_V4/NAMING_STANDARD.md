# NAMING_STANDARD

## Ucel

Definovat jednotne pojmenovani souboru, adresaru, entit, identifikatoru, modulu, API metod a vystupu.

## Odpovednost

- Brani chaosu v cestach a nazvech.
- Umoznuje stabilni generovani vystupu.
- Podporuje audit, archivaci a ochranu URL.

## Vstupy

- aktualni struktura repozitare,
- `PROJECT_ANALYSIS.md`,
- `ARCHITECTURE.md`,
- verejne URL v `nabidky`,
- budouci datove entity.

## Vystupy

- pravidla pojmenovani,
- vzory cest,
- zakazane nazvy,
- mapovani legacy nazvu.

## Verejne API

- `build_car_id(source, item_id)`
- `build_output_path(entity, page_type)`
- `validate_name(name, type)`
- `normalize_slug(value)`
- `resolve_legacy_name(path)`

## Datove struktury

```text
NamingRule
  type
  pattern
  example
  forbiddenExamples
  notes

PathPattern
  entityType
  baseDir
  pattern
  publicStable
```

## Zavislosti

- `AUTO_V4_STANDARD.md`
- `CAR_DATA_MODEL.md`
- `DATABASE_SCHEMA.md`

## Poradi implementace

1. Definovat nazvy modulu.
2. Definovat ID auta a aukce.
3. Definovat cesty vystupu.
4. Definovat archivni cesty.
5. Pozdeji pridat automatickou validaci nazvu.

