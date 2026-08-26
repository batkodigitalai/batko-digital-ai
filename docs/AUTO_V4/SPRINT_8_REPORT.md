# BATKO_AUTO_V4 - Sprint 8 Report

Datum: 2026-06-25
Vetev: `feature/BATKO_AUTO_V4`

## Souhrn

Sprint 8 pridal prvni vrstvu pro realnou OPENLANE integraci nad jiz prihlasenym Chromem. System umi pripojit existujici browser session pres Browser Foundation, overit aktualni page pomoci selector registry, zjistit zakladni metadata aukce a vypsat je do logu/CLI.

Sprint neimplementuje fotografie, PDF, HAR, AUTO_V4, Market Engine, watcher, GUI, SQLite, OCR ani parser obchodnich dat.

## Nove moduly

- `src/openlane/real/__init__.py`
- `src/openlane/real/detector.py`
- `src/openlane/real/models.py`
- `src/openlane/real/selectors.py`

## Nove konfigurace

- `config/selectors.yaml`

Soubor je YAML-kompatibilni JSON, aby nebyla potreba nova runtime zavislost.

## Nove tridy

- `RealAuctionDetector`
- `SelectorRegistry`
- `SelectorValidator`
- `RealAuctionDetection`
- `SelectorValidationReport`
- `SelectorCheck`
- `SelectorConfig`
- `SelectorVersion`
- `OpenLaneAuctionDetectionError`

## CLI smoke workflow

```text
python -m src detect-auction --browser-mode existing_chrome
```

Volitelne:

```text
python -m src detect-auction --browser-mode existing_chrome --selector-version v1
```

Prikaz:

1. pouzije existujici Chrome session pres CDP,
2. vezme aktualni page,
3. nacte `config/selectors.yaml`,
4. spusti selector validation,
5. detekuje `title`, `auction_id`, `reference`, `url`,
6. nic nestahuje.

## Ktere selektory funguji

Na lokalni OPENLANE-like fixture jsou overene tyto `v1` selektory:

```text
[data-openlane-auction-id]
[data-openlane-field='auction_id']
[data-openlane-field='reference']
[data-openlane-field='title']
h1
meta[name='auction-id']
```

Tyto selektory jsou bezpecne pro dosavadni testovaci kontrakt a pro diagnostiku realne stranky, pokud OPENLANE obsahuje podobne datove atributy nebo standardni nadpis/meta informaci.

## Ktere selektory jsou rizikove

Rizikove jsou hlavne fallbacky:

```text
h1
[data-reference]
[data-auction-reference]
[data-testid='...']
[data-cy='...']
```

Duvody:

- `h1` muze byt obecny nadpis stranky, ne vozidla.
- `data-testid` a `data-cy` se casto meni mezi buildy.
- reference muze byt zobrazena jako text bez stabilniho atributu.
- realny OPENLANE muze pouzivat lazy-rendered komponenty nebo iframe.

## Compatibility Layer

Registry je pripravene pro vice verzi:

- `v1`: aktualni pouzitelna sada a testovaci kontrakt.
- `v2`: priprava pro layout s `data-testid`.
- `v3`: priprava pro layout s `data-cy`.

Detektor bere `selector_version`, takze budoucnost lze resit pridanim nebo upravou konfigurace bez prepisovani detectoru.

## Selector Validator

`SelectorValidator` vraci report s:

- verzi selectoru,
- cestou k selector registry,
- skupinou selectoru,
- nazvem pole,
- samotnym selectorem,
- poctem nalezenych prvku.

Report pomaha rychle zjistit, ktere casti selector registry prestaly fungovat po zmene OPENLANE.

## Testy

Pridane testy:

- `tests/openlane/test_real_auction_detector.py::test_selector_registry_loads_compatibility_versions`
- `tests/openlane/test_real_auction_detector.py::test_selector_validator_reports_existing_selectors_with_fixture`
- `tests/openlane/test_real_auction_detector.py::test_real_auction_detector_reads_metadata_from_fixture`
- `tests/openlane/test_real_auction_detector.py::test_real_auction_detector_returns_clear_error_for_non_auction`

Posledni beh:

```text
43 passed
TOTAL coverage: 92%
```

## Real smoke test

Automaticke testy se nepripojuji na internet ani na skutecny OPENLANE. Real smoke test je pripraveny pres CLI a ma se spustit pouze ve chvili, kdy je v prihlasenem Chromu otevrena aukce a Chrome bezi s CDP endpointem.

## Jak pripravit system na zmeny OPENLANE

1. Nepridavat CSS selektory do kodu.
2. Pro kazdy novy layout pridat novou verzi v `config/selectors.yaml`.
3. Ukladat selector validation report z realnych smoke testu.
4. Pred downloaderem/capture spoustet `RealAuctionDetector`.
5. Po ziskani realnych snapshotu doplnit stabilnejsi markery pro `auction_id` a `reference`.
6. Drzet parser obchodnich dat oddelene od detectoru.

## Zname omezeni

- Real CDP smoke test nebyl spusten automaticky v test suite.
- `selectors.yaml` zatim obsahuje pripravu pro `v2/v3`, ale realne overena je pouze `v1` fixture sada.
- Detekce reference zavisi na tom, zda je reference v DOM dostupna stabilnim selectorem.
- Detektor nic nestahuje a nijak nepracuje s fotografiemi.
