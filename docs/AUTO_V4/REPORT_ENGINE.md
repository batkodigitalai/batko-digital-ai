# REPORT_ENGINE

## Ucel

Definovat modul pro tvorbu analyz, reportu, vystupnich shrnuti a kontrolnich prehledu.

## Odpovednost

- Sklada reporty z dat auta, trhu, scoringu, validace a publikacnich metadat.
- Oddeluje obsah reportu od HTML stran.
- Poskytuje jednotne vystupy pro interni i verejne pouziti.

## Vstupy

- `Car`,
- market report,
- scoring report,
- validation report,
- asset registry,
- URL registry.

## Vystupy

- interni report,
- verejny report,
- readiness report,
- rizikovy report,
- podklady pro generovani nabidky.

## Verejne API

- `build_car_report(car_id, report_type)`
- `build_readiness_report(car_id)`
- `build_risk_report(car_id)`
- `build_public_summary(car_id)`
- `export_report(report_id, format)`

## Datove struktury

```text
Report
  id
  reportType
  entityId
  status
  sections
  generatedAt
  warnings

ReportSection
  id
  title
  content
  sourceReferences
  visibility
```

## Zavislosti

- `CAR_DATA_MODEL.md`
- `MARKET_ENGINE.md`
- `OPENLANE_ENGINE.md`
- `DATABASE_SCHEMA.md`
- `TESTING_STANDARD.md`

## Poradi implementace

1. Definovat typy reportu.
2. Definovat sekce reportu.
3. Definovat readiness report.
4. Definovat rizikovy report.
5. Pozdeji pridat exporty do HTML/PDF/Markdown.

