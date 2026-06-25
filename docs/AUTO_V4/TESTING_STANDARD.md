# TESTING_STANDARD

## Ucel

Definovat pravidla testovani pro budouci implementaci AUTO_V4. Tento dokument nevytvari zadne testy.

## Odpovednost

- Vymezuje povinne typy testu pro moduly.
- Chrani datove kontrakty, verejna API a publikacni bezpecnost.
- Zakazuje implementaci modulu bez odpovidajici testovaci strategie.

## Vstupy

- `AUTO_V4_STANDARD.md`
- `ARCHITECTURE.md`
- navrhy verejnych API,
- datove struktury modulu,
- publikacni pravidla.

## Vystupy

- testovaci pravidla,
- minimalni coverage ocekavani,
- seznam testovacich kategorii,
- akceptacni kriteria pro moduly.

## Verejne API

- `define_test_contract(module_name)`
- `validate_test_coverage(module_name)`
- `assert_public_api_tests(module_name)`
- `assert_data_schema_tests(entity_name)`

## Datove struktury

```text
TestContract
  moduleName
  requiredUnitTests
  requiredIntegrationTests
  requiredValidationTests
  criticalScenarios

AcceptanceCriterion
  id
  moduleName
  description
  required
```

## Zavislosti

- `AUTO_V4_STANDARD.md`
- `CAR_DATA_MODEL.md`
- `DATABASE_SCHEMA.md`
- `NAMING_STANDARD.md`

## Poradi implementace

1. Definovat testovaci kategorie.
2. Definovat test contracts pro datove modely.
3. Definovat test contracts pro engine moduly.
4. Definovat test contracts pro publikaci.
5. Az potom psat konkretni testy pri implementaci modulu.

