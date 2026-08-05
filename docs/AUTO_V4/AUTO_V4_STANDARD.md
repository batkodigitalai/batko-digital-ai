# AUTO_V4_STANDARD

## Ucel

Definovat hlavni standardy systemu BATKO_AUTO_V4: modularitu, datovy tok, ochranu verejnych URL, kvalitu vystupu a pravidla pro dlouhodoby vyvoj.

## Odpovednost

- Urcuje zavazna pravidla pro vsechny moduly AUTO_V4.
- Sjednocuje architektonicke principy z `ARCHITECTURE.md`.
- Brani duplicitnim implementacim a nahodnemu kopirovani logiky.

## Vstupy

- `PROJECT_ANALYSIS.md`
- `ARCHITECTURE.md`
- `NAMING_STANDARD.md`
- `TESTING_STANDARD.md`
- existujici dokumentace v `00_SYSTEM`

## Vystupy

- soubor projektovych pravidel,
- definice povolenych vrstev,
- pravidla pro nove moduly,
- pravidla pro zmeny verejnych vystupu.

## Verejne API

- `get_project_rules(scope)`
- `validate_module_boundary(module_name, change)`
- `assert_no_duplicate_module(responsibility)`
- `assert_public_url_safety(change_set)`

## Datove struktury

```text
ProjectRule
  id
  title
  scope
  severity
  description
  enforcement

ModuleBoundary
  moduleName
  owns
  mustNotOwn
  allowedDependencies
```

## Zavislosti

- `NAMING_STANDARD.md`
- `TESTING_STANDARD.md`
- `ARCHITECTURE.md`

## Poradi implementace

1. Sepsat zavazna pravidla.
2. Navazat pravidla na naming a test standard.
3. Pouzit pravidla pri navrhu prvnich modulovych kontraktu.
4. Pozdeji pridat automatickou kontrolu pravidel.

