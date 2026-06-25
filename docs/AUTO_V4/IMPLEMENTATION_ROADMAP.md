# IMPLEMENTATION_ROADMAP

## Ucel

Rozdelit BATKO_AUTO_V4 do postupnych implementacnich sprintu tak, aby system vznikal modularne, bez prepisovani architektury a bez rozbijeni existujicich verejnych vystupu.

## Sprint 0 - Projektove kontrakty

### Cil

Dokoncit dokumentacni zaklad, pravidla projektu a hranice modulu.

### Ocekavany vysledek

- hotove dokumenty v `docs/AUTO_V4`,
- kratky `AGENTS.md`,
- potvrzene vlastnictvi odpovednosti jednotlivych modulu,
- jasny zakaz duplicitnich implementaci.

### Zavislosti

- `PROJECT_ANALYSIS.md`
- `ARCHITECTURE.md`

### Odhad slozitosti

Nizka.

### Rizika

- prilis siroka dokumentace bez jasnych priorit,
- nejasne hranice mezi core, engine a report moduly.

## Sprint 1 - Standardy a naming

### Cil

Formalizovat projektove standardy, pojmenovani, cesty a identifikatory.

### Ocekavany vysledek

- finalizovany `AUTO_V4_STANDARD.md`,
- finalizovany `NAMING_STANDARD.md`,
- pravidla pro `carId`, `sourceItemId`, vystupni cesty a archivni cesty,
- zaklad pro pozdejsi validaci.

### Zavislosti

- Sprint 0,
- `AGENTS.md`.

### Odhad slozitosti

Nizka az stredni.

### Rizika

- spatne zvolene ID auta muze pozdeji komplikovat URL a assety,
- ignorovani legacy cest muze ohrozit verejne odkazy.

## Sprint 2 - Datovy model auta

### Cil

Navrhnout a implementovat minimalni datovy model auta bez downloaderu a parseru.

### Ocekavany vysledek

- stabilni `Car`,
- stabilni `Auction`,
- zakladni `Condition`,
- publikacni metadata,
- validacni pravidla pro povinna pole.

### Zavislosti

- Sprint 1,
- `CAR_DATA_MODEL.md`,
- `DATABASE_SCHEMA.md`.

### Odhad slozitosti

Stredni.

### Rizika

- prilis detailni schema pred realnym pouzitim,
- prilis volne schema bez hodnoty pro validaci,
- zamichani HTML vystupu do datoveho modelu.

## Sprint 3 - Konceptualni uloziste a registry

### Cil

Pripravit file-based uloziste pro data, URL a asset registry bez databaze.

### Ocekavany vysledek

- pravidla pro ulozeni dat v `30_DATA`,
- koncept asset registry,
- koncept URL registry,
- mapovani na budouci databazi podle `DATABASE_SCHEMA.md`.

### Zavislosti

- Sprint 2,
- `NAMING_STANDARD.md`,
- `DATABASE_SCHEMA.md`.

### Odhad slozitosti

Stredni.

### Rizika

- predcasny vyber databazove technologie,
- rozpad mezi file-based daty a budouci databazi,
- duplicitni asset evidence.

## Sprint 4 - OPENLANE kontrakt

### Cil

Definovat zdrojovy kontrakt pro OPENLANE/AUTO1 bez implementace downloaderu a parseru.

### Ocekavany vysledek

- `AuctionSourceRecord`,
- mapovani zdrojovych poli na `Car`,
- seznam povinnych a chybejicich poli,
- pravidla pro ulozeni raw referenci.

### Zavislosti

- Sprint 2,
- Sprint 3,
- `OPENLANE_ENGINE.md`,
- `DOWNLOADER.md`.

### Odhad slozitosti

Stredni.

### Rizika

- smichani downloaderu, parseru a normalizace,
- zavislost na aktualni podobe externiho webu,
- nejasna confidence hodnota extrahovanych dat.

## Sprint 5 - Market engine kontrakt

### Cil

Navrhnout minimalni trzni a cenovy model pro rozhodovani o autech.

### Ocekavany vysledek

- `MarketReport`,
- `MarketComparable`,
- zakladni cenove scenare,
- napojeni na report engine.

### Zavislosti

- Sprint 2,
- `MARKET_ENGINE.md`,
- `REPORT_ENGINE.md`.

### Odhad slozitosti

Stredni az vyssi.

### Rizika

- slaba data pro trzni srovnani,
- prilis rucni odhady bez confidence,
- zamena market logiky za obchodni texty.

## Sprint 6 - Core workflow

### Cil

Definovat a implementovat stavovy workflow pro zpracovani auta.

### Ocekavany vysledek

- workflow pro nove auto,
- stavy: draft, data_ready, market_ready, report_ready, ready_for_output,
- seznam dalsich kroku,
- audit rozhodnuti.

### Zavislosti

- Sprint 2,
- Sprint 4,
- Sprint 5,
- `AUTO_V4_CORE.md`.

### Odhad slozitosti

Stredni.

### Rizika

- core modul zacne obsahovat specializovanou logiku,
- prilis mnoho stavu,
- chybejici audit rozhodnuti.

## Sprint 7 - Report engine

### Cil

Vytvorit zakladni reportovaci kontrakty a prvni textove reporty nad daty.

### Ocekavany vysledek

- readiness report,
- risk report,
- public summary,
- interni report pro auto.

### Zavislosti

- Sprint 5,
- Sprint 6,
- `REPORT_ENGINE.md`.

### Odhad slozitosti

Stredni.

### Rizika

- reporty zacnou suplovat HTML generator,
- chybejici vazba na zdrojova data,
- nejasne oddeleni interni a verejne casti reportu.

## Sprint 8 - Testovaci standard a prvni test contracts

### Cil

Zavest testovaci pravidla pro budouci implementaci modulu.

### Ocekavany vysledek

- test contract pro `Car`,
- test contract pro naming,
- test contract pro workflow,
- test contract pro report engine.

### Zavislosti

- Sprint 1,
- Sprint 2,
- Sprint 6,
- `TESTING_STANDARD.md`.

### Odhad slozitosti

Stredni.

### Rizika

- testy se budou psat az po implementaci,
- test contracts budou prilis obecne,
- vynechani testu ochrany verejnych URL.

## Sprint 9 - Downloader priprava

### Cil

Pripravit technicky plan downloaderu bez jeho implementace.

### Ocekavany vysledek

- download job kontrakt,
- download manifest,
- pravidla pro raw uloziste,
- bezpecnostni a rate-limit pravidla.

### Zavislosti

- Sprint 4,
- `DOWNLOADER.md`,
- `OPENLANE_ENGINE.md`.

### Odhad slozitosti

Stredni.

### Rizika

- predcasne programovani downloaderu,
- ignorovani pravnich/technickych limitu zdroje,
- smichani stahovani s parsingem.

## Sprint 10 - Minimalni end-to-end bez downloaderu

### Cil

Overit, ze system funguje rucne od dat auta po report, stale bez downloaderu, GUI, parseru a plneho AUTO_V4 generatoru.

### Ocekavany vysledek

- jedno rucne zadane auto podle `Car`,
- market report,
- workflow stav,
- readiness report,
- zadny zapis do produkcnich HTML vystupu.

### Zavislosti

- Sprint 2,
- Sprint 5,
- Sprint 6,
- Sprint 7,
- Sprint 8.

### Odhad slozitosti

Vyssi.

### Rizika

- snaha predcasne generovat verejne stranky,
- obchazeni validace,
- vznik paralelnich datovych struktur.

## Sprint 11 - Publikacni a vystupni priprava

### Cil

Pripravit budoucí napojeni na vystupy bez implementace plneho HTML generatoru.

### Ocekavany vysledek

- definice output manifestu,
- pravidla pro preview vystupy,
- pravidla pro ochranu `nabidky`,
- zaklad pro validaci pred publikaci.

### Zavislosti

- Sprint 3,
- Sprint 7,
- Sprint 8,
- `AUTO_V4_STANDARD.md`.

### Odhad slozitosti

Stredni.

### Rizika

- prime zapisovani do `nabidky`,
- chybejici snapshot strategie,
- nejasny rozdil mezi preview a public.

## Sprint 12 - Rozsireni po stabilizaci

### Cil

Az po stabilnim zakladu rozhodnout o implementaci downloaderu, parseru, generatoru, GUI nebo integraci CRM.

### Ocekavany vysledek

- rozhodnuti o dalsi priorite,
- presny rozsah dalsi faze,
- navazujici test contracts,
- zadne prepisovani zakladni architektury.

### Zavislosti

- Sprint 10,
- Sprint 11.

### Odhad slozitosti

Vyssi.

### Rizika

- prilis mnoho smeru najednou,
- implementace GUI pred datovym jadrem,
- zavislost na externich sluzbach pred stabilni validaci.

## Doporučene pravidlo rizeni sprintu

Kazdy sprint musi koncit dokumentovanym stavem:

- co vzniklo,
- co nevzniklo,
- jake API je stabilni,
- jake datove struktury jsou stabilni,
- jake testy budou povinne pri implementaci,
- co je blokovane.

