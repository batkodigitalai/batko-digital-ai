# MARKET_ENGINE

## Ucel

Definovat modul pro trzni kontext, porovnani cen, odhad prodejni ceny, marze a obchodni atraktivity vozidla.

## Odpovednost

- Oddeluje trzni analyzu od dat auta.
- Poskytuje vstupy pro pricing, scoring a reporty.
- Umoznuje porovnavat vice scenaru prodeje.

## Vstupy

- `Car`,
- historicke srovnatelne nabidky,
- rucne zadane trzni ceny,
- kurz meny,
- naklady a poplatky,
- segment trhu.

## Vystupy

- market report,
- doporucena prodejni cena,
- rozmezi marze,
- odhad rizika,
- podklady pro `REPORT_ENGINE`.

## Verejne API

- `estimate_market_price(car)`
- `compare_market_candidates(car, candidates)`
- `calculate_margin_scenario(car, scenario)`
- `build_market_report(car_id)`
- `get_market_confidence(report)`

## Datove struktury

```text
MarketComparable
  id
  make
  model
  year
  mileageKm
  price
  source
  url
  relevanceScore

MarketReport
  carId
  estimatedSalePrice
  lowPrice
  highPrice
  confidence
  comparables
  risks
```

## Zavislosti

- `CAR_DATA_MODEL.md`
- `DATABASE_SCHEMA.md`
- `REPORT_ENGINE.md`
- `AUTO_V4_CORE.md`

## Poradi implementace

1. Definovat manualni market report.
2. Pridat porovnatelna auta.
3. Pridat scenare marze.
4. Pridat confidence score.
5. Pozdeji napojit externi zdroje trhu.

