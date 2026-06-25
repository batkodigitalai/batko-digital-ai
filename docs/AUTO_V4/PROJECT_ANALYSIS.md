# BATKO_AUTO_V4 - Faze 0 - Analyza projektu

Datum analyzy: 2026-06-25
Vetev: `feature/BATKO_AUTO_V4`
Repozitar: `batkodigitalai/batko-digital-ai`

## 1. Shrnutí

Repozitar je dnes centralni rozcestnik a staticky publikacni system pro batko.digital.ai. Nejde o klasickou aplikaci s build procesem, backendem a testy. Vetsina obsahu je tvorena Markdown dokumentaci, statickymi HTML vystupy, fotkami aut a jednim Google Apps Script webhookem pro leady.

Soucasna struktura uz ma spravne pojmenovane vrstvy: system, content engine, automation, data, output, assets, archive a lab. Prakticka implementace je ale stale prevazne rucni: hotove HTML soubory obsahuji inline CSS, inline JavaScript, opakovane formulare, opakovane Google Apps Script endpointy a duplicitni obrazky.

Nejvetsi prilezitost pro AUTO_V4 je nevytvaret dalsi samostatne HTML kopie, ale zavest datovy model auta, sablony, generator, jednotny lead klient, asset registr a bezpecny publikacni pipeline.

## 2. Strom projektu

```text
.
|-- 00_SYSTEM/
|   |-- README.md
|   |-- data-standard.md
|   |-- migration-plan.md
|   |-- repo-mapa.md
|   `-- url-registr.md
|-- 10_CONTENT_ENGINE/
|   |-- README.md
|   `-- templates/
|       |-- facebook-post-template.md
|       `-- landing-page-template.md
|-- 20_AUTOMATION/
|   |-- README.md
|   |-- pipeline-plan.md
|   |-- email-parsers/
|   |   `-- README.md
|   `-- generators/
|       `-- README.md
|-- 30_DATA/
|   `-- README.md
|-- 40_OUTPUT/
|   |-- README.md
|   |-- auto-lead-system/
|   |   |-- README.md
|   |   |-- config.example.js
|   |   |-- config.js
|   |   |-- index.html
|   |   |-- landing_B2B.html
|   |   |-- landing_B2C.html
|   |   |-- lead-client.js
|   |   `-- apps_script/
|   |       `-- lead_webhook.gs
|   `-- mercedes-glc-landing/
|       |-- README.md
|       |-- index.html
|       |-- script.js
|       `-- style.css
|-- 50_ASSETS/
|   `-- README.md
|-- 60_ARCHIVE/
|   `-- README.md
|-- 90_LAB/
|   `-- README.md
|-- docs/
|   `-- AUTO_V4/
|       `-- PROJECT_ANALYSIS.md
|-- nabidky/
|   |-- index.html
|   |-- 20260520_auto1_10974215_VW_Passat_B8/
|   |   |-- 9 HTML souboru nabidek, hodnoceni a objednavky
|   |   `-- img/ 10 JPG
|   |-- 20260521_auto1_10989369_VW_Passat/
|   |   |-- 1 konverzni HTML
|   |   `-- img/ 10 JPG
|   |-- 20260521_auto1_10989369_VW_Passat_Conceptline/
|   |   |-- 9 HTML souboru nabidek, hodnoceni a objednavky
|   |   `-- img/ 10 JPG
|   |-- 20260522_auto1_11004532_VW_Golf_Variant/
|   |   |-- 1 konverzni HTML
|   |   `-- img/ 19 JPG
|   |-- 20260522_auto1_12345678_Skoda_Superb/
|   |   `-- index.html
|   `-- 20260523_auto1_11004535_VW_Passat_Variant/
|       |-- 1 konverzni HTML
|       `-- img/ 41 JPG
|-- prompty/
|   `-- Persuasion_Power_Protocol_v1.md
|-- simulators/
|   `-- 20260330_1500_auto1_24h_octavia_tiguan_golf_aj.html
`-- README.md
```

## 3. Technologie projektu

- Staticke HTML publikovane pravdepodobne pres GitHub Pages.
- CSS: prevazne inline `<style>` v HTML, jedna samostatna `style.css` u Mercedes landing page.
- JavaScript: vanilla JS, prevazne inline v HTML, plus `lead-client.js` a `script.js`.
- Google Apps Script: `lead_webhook.gs` jako jednoduchy backend pro zapis leadu do Google Sheets a odesilani e-mailu.
- Google Sheets jako uloziste leadu.
- Google Forms iframe u Mercedes landing page.
- Externi sluzby/odkazy: GitHub Pages, OPENLANE/AUTO1 odkazy, Calendly, Google Forms, Google Apps Script.
- Markdown pro dokumentaci, sablony a procesni popis.
- Nejsou nalezeny: `package.json`, lock file, Python requirements, Dockerfile, test framework, CI konfigurace.

## 4. Existujici moduly a oblasti

### 00_SYSTEM

Ridici dokumentace: mapa repozitaru, URL registr, migracni plan a datovy standard. Je to nejdulezitejsi existujici pravidlova vrstva. Obsahuje principy "nerozbijet verejne URL", "produkce oddelene od experimentu" a navrh vrstev.

### 10_CONTENT_ENGINE

Zatim hlavne dokumentacni vrstva. Obsahuje jednoduche Markdown sablony pro landing page a Facebook post. Dobre misto pro budouci obsahove bloky, copy moduly, CTA, scoring texty a sablony nabidek.

### 20_AUTOMATION

Zatim planovaci vrstva. Ma README pro generatory a email parsers, ale neobsahuje realne skripty/generatory. Pipeline plan popisuje smer: CSV auta -> AI scoring -> posty -> landing page -> GitHub Pages.

### 30_DATA

Zatim prazdna datova vrstva s README. V projektu nejsou strukturovana vstupni data aut ve forme CSV/JSON. Soucasna data jsou zapecena primo v HTML.

### 40_OUTPUT

Hotove vystupy. Obsahuje `auto-lead-system` a `mercedes-glc-landing`. Tato vrstva ma nejblize k opakovane pouzitelnemu runtime, hlavne kvuli `lead-client.js` a `lead_webhook.gs`.

### 50_ASSETS

Zatim jen README. Realne assety jsou misto toho ulozene lokalne u jednotlivych nabidek v `nabidky/*/img`.

### 60_ARCHIVE

Zatim jen README. Archivni princip existuje, ale historicke vystupy nejsou presunute ani klasifikovane.

### 90_LAB

Zatim jen README. Simulator je samostatne v `simulators`, tedy mimo deklarovanou lab vrstvu.

### nabidky

Nejvetsi obsahova oblast. Obsahuje index a vice slozek pro konkretni auta. Vystupy jsou rucne nebo poloautomaticky generovane staticke HTML nabidky, objednavky, hodnoceni a konverzni stranky.

### simulators

Jedna velka samostatna HTML aplikace pro simulaci AUTO1 aukce. Obsahuje vlastni inline CSS a JS. Funkcne patri do LAB nebo budouci aplikacni vrstvy, ale dnes stoji bokem.

### prompty

Jedna promptova metodika pro presvedcovaci texty. Je znovupouzitelna pro copywriting nabidek, landing pages a reklam.

## 5. Znovupouzitelne casti

- `00_SYSTEM/data-standard.md`: dobry zaklad pro datovy model auta, obsahu, analyz a assetu.
- `00_SYSTEM/url-registr.md`: zaklad pro ochranu verejnych URL a redirect strategii.
- `20_AUTOMATION/pipeline-plan.md`: konceptualni mapa budouci pipeline.
- `10_CONTENT_ENGINE/templates/landing-page-template.md`: zaklad sekci pro landing page.
- `10_CONTENT_ENGINE/templates/facebook-post-template.md`: zaklad pro social post generator.
- `prompty/Persuasion_Power_Protocol_v1.md`: copywriting pravidla pro konverzni texty.
- `40_OUTPUT/auto-lead-system/lead-client.js`: nejlepsi existujici kandidat na jednotne odesilani leadu z formularu.
- `40_OUTPUT/auto-lead-system/apps_script/lead_webhook.gs`: existujici backend pro lead capture.
- `40_OUTPUT/auto-lead-system/landing_B2B.html` a `landing_B2C.html`: pouzitelne jako obsahove a layoutove reference pro segmentaci B2B/B2C.
- `40_OUTPUT/mercedes-glc-landing/style.css`: nejcistsi existujici oddeleni CSS mimo HTML.
- `nabidky/index.html`: existujici verejny rozcestnik nabidek.
- `simulators/20260330_1500_auto1_24h_octavia_tiguan_golf_aj.html`: funkcni prototyp pro aukcni simulaci a kalkulacni logiku, vhodny k pozdejsimu rozdeleni na data, logiku a UI.

## 6. Duplicity

### Duplicity v HTML sablonach

- Nabidky v `nabidky/*` opakuji stejne typy stran: hlavni nabidka, analyza, FO preprodej, ICO preprodej, agenturni nakup, mentoring, premium full, hodnoceni, objednavka.
- Kazda z techto stran obsahuje vlastni inline CSS misto sdileneho stylesheetu.
- Galerie aut se opakuji jako rucne vypsane `<img>` tagy.
- Inline JS pro galerii, modal, formular a odesilani leadu je kopirovany mezi strankami.
- Konverzni stranky `*_KONVERZE.html` maji podobnou strukturu: hero, galerie, uzamcene casti, modal lead, audit/objednavka, inline submit logika.

### Duplicity v leadech

- Existuje jednotny `40_OUTPUT/auto-lead-system/lead-client.js`, ale mnoho stran v `nabidky` ma vlastni `fetch()` na stejny Google Apps Script endpoint.
- Apps Script URL je natvrdo uvedena v `config.js`, `index.html` v auto-lead-systemu a v mnoha HTML souborech v `nabidky`.
- `localStorage` se pouziva ve vice formularich pod ruznymi klici a ruznymi payload strukturami.

### Duplicity v obrazcich

- `nabidky/20260521_auto1_10989369_VW_Passat/img/foto_01.jpg` az `foto_10.jpg` jsou binarne identicke s `nabidky/20260521_auto1_10989369_VW_Passat_Conceptline/img/foto_01.jpg` az `foto_10.jpg`.
- `nabidky/20260522_auto1_11004532_VW_Golf_Variant/img/9ac65e85-f20a-47fa-9667-8de186e67197.jpg` je duplicitni s variantou `(1).jpg`.
- Assety jsou ukladane do jednotlivych vystupu misto centralniho asset registru.

### Duplicity v datech

- Udaje o autech, cenach, produktech, kontaktech, IČO/DIČ a URL se opakuji primo v HTML.
- Stejne kontaktni udaje jsou rozesete ve footerech a formularich.
- Verejny Apps Script endpoint je opakovane zapsany v kodu.

## 7. Zastarale nebo problematicke casti

- Dokumentace v nekterych vystupech PowerShellu ukazuje poskozene ceske znaky, pravdepodobne kvuli historickemu encodingu nebo zpusobu cteni souboru. Je potreba sjednotit UTF-8.
- `40_OUTPUT/auto-lead-system/index.html` obsahuje pouze radek `const API_URL = ...`, tedy nevypada jako platna HTML index stranka.
- `nabidky/20260522_auto1_12345678_Skoda_Superb/index.html` ma jen 20 bajtu, pravdepodobne placeholder.
- Mercedes landing page obsahuje TODO poznamky: overit Calendly URL, nahradit placeholdery fotek, doplnit realny backend formulare.
- `40_OUTPUT/mercedes-glc-landing/script.js` podle README pouze predstira odeslani formulare, pokud neni nahrazen Google Form iframe.
- Simulator je velky monoliticky HTML soubor s inline CSS/JS; funkcni, ale tezko udrzovatelny.
- `20_AUTOMATION/generators` a `email-parsers` jsou zatim pouze README bez implementace.
- `30_DATA`, `50_ASSETS`, `60_ARCHIVE`, `90_LAB` jsou koncepcne zalozene, ale prakticky prazdne.

## 8. Vztahy mezi castmi

- `00_SYSTEM` definuje pravidla pro vsechny ostatni vrstvy.
- `10_CONTENT_ENGINE` ma poskytovat sablony pro `40_OUTPUT` a `nabidky`, ale dnes se pouziva spis manualne.
- `20_AUTOMATION` ma v budoucnu generovat vystupy z `30_DATA` do `40_OUTPUT` a `nabidky`.
- `30_DATA` by melo byt zdrojem pravdy pro auta, ale dnes jsou data ulozena primo v HTML.
- `40_OUTPUT/auto-lead-system` souvisi s formulari v `nabidky`, protoze sdileji stejny Google Apps Script endpoint.
- `nabidky` jsou verejne vystupy a musi respektovat pravidlo nerozbit existujici GitHub Pages URL.
- `50_ASSETS` by melo byt centralni misto pro obrazky, ale realne jsou obrazky v `nabidky/*/img`.
- `simulators` logicky patri k `90_LAB` nebo k budouci aplikacni vrstve AUTO tools.
- `prompty` souvisi s content engine a generatorovou vrstvou.

## 9. Soucasna architektura

```text
Rucni vstup / AI vystup
        |
        v
Staticke HTML soubory v nabidky/ a 40_OUTPUT/
        |
        +--> GitHub Pages verejne URL
        |
        +--> Inline formulare / lead-client.js
                 |
                 v
           Google Apps Script
                 |
                 +--> Google Sheets
                 +--> MailApp notifikace
```

Charakter architektury:

- file-based staticky web,
- bez build kroku,
- bez centralniho datoveho zdroje,
- bez testu,
- bez validace generovanych vystupu,
- s castecne existujici lead infrastrukturou,
- s vysokou mirou kopirovani HTML/CSS/JS.

## 10. Nejvetsi rizika

1. Rozbiti verejnych URL pri presunech souboru v `nabidky` nebo `40_OUTPUT`.
2. Nekonzistentni lead capture kvuli vice ruznym formularum a inline `fetch()` implementacim.
3. Verejny Apps Script endpoint je natvrdo ve vice souborech; zmena endpointu vyzaduje rucni upravu mnoha mist.
4. Data aut jsou zapecena v HTML, nejde je spolehlive validovat, znovu pouzit ani prepojit.
5. Duplicita obrazku zvetsuje repo a ztezuje spravu assetu.
6. Inline CSS/JS ve velkych HTML souborech komplikuje opravy a zvysuje riziko regrese.
7. Chybi testy a automaticka kontrola odkazu, formularu a HTML validity.
8. Chybi jasne oddeleni produkce, archivu a experimentu v realnych souborech.
9. Encoding ceskych textu muze zpusobovat necitelne dokumenty nebo rozbite publikovane texty.
10. Monoliticky simulator muze obsahovat cennou logiku, ale bez rozdeleni se spatne znovu pouziva.

## 11. Navrh nove architektury AUTO_V4

Navrh bez okamzite implementace:

```text
30_DATA/
  cars/
    YYYYMMDD_source_carId.json
  leads/
  pricing/
  products/

50_ASSETS/
  cars/
    carId/
      foto_01.jpg
      ...
  brand/

10_CONTENT_ENGINE/
  templates/
  blocks/
  copy/
  prompts/

20_AUTOMATION/
  generators/
  validators/
  parsers/
  publishers/

40_OUTPUT/
  generated/
  public/

nabidky/
  stable public URLs only

docs/
  AUTO_V4/
```

Doporuceny tok:

```text
AUTO1/OPENLANE/email/manual input
        |
        v
Normalized car JSON/CSV in 30_DATA
        |
        v
Validation + scoring
        |
        v
Template generator
        |
        v
Generated static pages
        |
        v
Link registry + safety check
        |
        v
GitHub Pages publish
        |
        v
Unified lead capture
```

## 12. Doporucene nove moduly

Tyto moduly doporucuji vytvorit az v dalsi fazi, ne v teto analyze:

- `car-data-model`: jednotny JSON/CSV standard pro auto, aukci, ceny, naklady, fotky, dokumenty, rizika a scoring.
- `asset-registry`: evidence fotek a jejich vazba na `carId`, vcetne detekce duplicit.
- `offer-template-engine`: generator HTML stran z dat a sablon.
- `lead-client-v4`: jednotny klient pro vsechny formulare, nad aktualnim `lead-client.js`.
- `lead-schema`: jednotny payload pro Google Apps Script, Sheets a pozdeji CRM.
- `url-registry-validator`: kontrola, ze zmeny nerozbiji existujici verejne URL.
- `html-output-validator`: kontrola existence titulku, meta description, formulare, lead endpointu, obrazku a internich odkazu.
- `pricing-engine`: vypocet nakupni ceny, buyer fee, dopravy, oprav, DPH, prodejni ceny a marze.
- `scoring-engine`: oddelena logika pro technicke, financni a obchodni hodnoceni auta.
- `email-parser`: parser AUTO1/OPENLANE emailu do normalizovaneho datoveho formatu.
- `archive-manager`: pravidla pro presun historickych vystupu bez rozbiti verejnych odkazu.
- `public-index-generator`: generator `nabidky/index.html` z registru nabidek.

## 13. Doporuceni dalsiho postupu

1. Nehybat s verejnymi soubory v `nabidky` bez URL registru a kontroly redirectu.
2. Nejdrive formalizovat datovy model auta v `30_DATA`, protoze bez toho budou dalsi HTML kopie znovu duplikovat chaos.
3. Sjednotit lead payload a vybrat jeden zdroj pravdy pro Apps Script endpoint.
4. Vytvorit katalog existujicich verejnych URL a oznacit, co je produkce, archiv a experiment.
5. Udelat asset audit: duplicitni fotky, chybejici fotky, placeholdery, externi fallbacky.
6. Rozhodnout, zda `nabidky` zustane public legacy vrstva a nove vystupy pujdou do `40_OUTPUT/generated`, nebo zda se generator bude trefovat primo do `nabidky`.
7. V dalsi fazi navrhnout minimalni generator pouze pro jednu novou testovaci nabidku, bez prepisu existujicich URL.
8. Az po validaci generatoru migrovat opakovane HTML casti: galerie, produktove bloky, formular, footer, lead modal.
9. Zavadet automatizaci po malych krocich: validace dat -> generator -> kontrola odkazu -> publikace.
10. Pred jakoukoli produkcni zmenou udelat snapshot/archiv dotcenych stran.

## 14. Zaverecne hodnoceni

Repozitar ma spravny strategicky smer, ale implementacne je stale ve fazi rucne skladanych statickych vystupu. Pro AUTO_V4 je nejvetsi hodnota v tom, ze uz existuji realne priklady nabidek, lead infrastruktura a jasna pravidla ochrany URL. Nejvetsi slabina je absence centralnich dat a generatoru.

Dalsi faze by nemela zacit "novou aplikaci", ale stabilizaci zakladu: data, URL registr, lead schema, asset registry a sablonovy generator. Tim se zachova existujici verejna hodnota a zaroven se prestane nasobit duplicita.
