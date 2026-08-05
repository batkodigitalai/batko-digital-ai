# BATKO_AUTO_V4 - Sprint 2 Report

Datum: 2026-06-25
Vetev: `feature/BATKO_AUTO_V4`

## Souhrn

Sprint 2 pridal pouze browser infrastrukturu pro budouci praci s OPENLANE. Neobsahuje OPENLANE login, downloader, parser, praci s fotografiemi, PDF, GUI, SQLite, AUTO_V4 vypocty, Market Engine, network capture, HAR, resume download ani watcher.

## Nove moduly

- `src/openlane/__init__.py`
- `src/openlane/browser/__init__.py`
- `src/openlane/browser/models.py`
- `src/openlane/browser/playwright_provider.py`
- `src/openlane/browser/profile.py`
- `src/openlane/browser/cdp.py`
- `src/openlane/browser/manager.py`
- `src/openlane/browser/session.py`
- `src/openlane/browser/factory.py`

## Zmeny konfigurace

Do `BrowserConfig` byly pridany polozky:

- `browser_mode`
- `chrome_profile`
- `chrome_cdp`
- `headless`
- `playwright_timeout`
- `download_timeout`

Do `pyproject.toml` byla pridana runtime zavislost:

- `playwright>=1.48`

## Nove tridy

- `BrowserMode`
- `BrowserRuntime`
- `ProfileManager`
- `CDPConnector`
- `BrowserManager`
- `SessionManager`
- `BrowserFactory`

## Verejne schopnosti

### BrowserManager

- umi pripravit local Chromium runtime,
- umi pripravit CDP connection runtime,
- umi pripravit persistent profile runtime,
- umi ukoncit vlastnene browser/context handles.

### SessionManager

- vytvori session,
- ukonci session,
- vrati aktivni page,
- vrati browser context.

### ProfileManager

- zkontroluje existenci profilu,
- vytvori profil,
- nacte profil,
- vrati cestu k profilu.

### CDPConnector

- drzi infrastrukturu pro pripojeni ke spustenemu Chromu pres CDP,
- nepouziva zadne OPENLANE URL,
- neprovadi login.

### BrowserFactory

- podle konfigurace vytvori `BrowserManager`,
- podporuje rezimy `local`, `existing_chrome`, `persistent_profile`.

## Testy

Pridane testy:

- `tests/openlane/test_browser_profile.py`
- `tests/openlane/test_browser_manager.py`
- `tests/openlane/test_browser_session.py`
- `tests/openlane/test_browser_factory.py`
- `tests/openlane/test_cdp_connector.py`

Upravene testy:

- `tests/core/test_config.py`

Posledni beh:

```text
19 passed
TOTAL coverage: 79%
```

Testy jsou pouze unit testy a pouzivaji mocky/fake Playwright objekty. Nepripojuji skutecny Chrome.

## Znama omezeni

- Playwright browser binaries nejsou instalovane timto sprintem.
- CDP endpoint je pouze konfiguracni hodnota, testy ho realne nepouzivaji.
- Persistent profile vytvari pouze adresar a pripravuje Playwright volani.
- Neni implementovan OPENLANE login.
- Neni implementovan downloader.
- Neni implementovan parser.
- Neni implementovana prace s fotografiemi ani PDF.
- Neni implementovan network capture, HAR, watcher ani resume download.
- Browser infrastruktura zatim neni napojena na zadny business workflow.

## Doporuceni pro Sprint 3

1. Nepridavat OPENLANE login, dokud nebude jasny session lifecycle a bezpecnost profilu.
2. Doplnit dokumentaci k browser mode konfiguraci.
3. Pridat integracni smoke test pouze v pripade, ze bude explicitne povolene spusteni lokálního Playwright browseru.
4. Zkontrolovat, zda `download_timeout` patri do browser configu nebo pozdeji do samostatneho downloader configu.
5. Pokud bude Sprint 3 smerovat k downloaderu, nejdrive definovat download job a manifest podle `DOWNLOADER.md`, stale bez parseru.

