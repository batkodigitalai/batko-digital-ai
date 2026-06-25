# BATKO_AUTO_V4 - Architektura systemu

Datum navrhu: 2026-06-25
Vetev: `feature/BATKO_AUTO_V4`
Navazuje na: `docs/AUTO_V4/PROJECT_ANALYSIS.md`

## 1. Cil architektury

BATKO_AUTO_V4 ma prevest soucasny rucne skladany system statickych HTML nabidek do modularniho, datove rizeneho a bezpecne publikovatelneho systemu.

Hlavni cil:

- zachovat existujici verejne URL a nerozbit produkcni vystupy,
- prestat kopirovat HTML/CSS/JS mezi nabidkami,
- zavest jeden datovy model auta a nabidky,
- generovat vystupy z dat a sablon,
- sjednotit lead capture,
- oddelit data, assety, sablony, validaci, publikaci a archiv,
- umoznit postupny vyvoj bez pozdejsiho prepisovani zakladu.

## 2. Architektonicky princip

System bude file-based modularni pipeline. Zdroj pravdy nebude HTML soubor, ale normalizovana data a registry.

```text
Vstupy
  AUTO1 / OPENLANE / email / manualni zadani / fotky
        |
        v
30_DATA - normalizovana data auta, cen, produktu a leadu
        |
        v
Moduly: validace -> scoring -> pricing -> content -> output
        |
        v
40_OUTPUT / nabidky - generovane staticke vystupy
        |
        v
GitHub Pages + unified lead capture
        |
        v
Google Apps Script / Google Sheets / e-mail / budouci CRM
```

Zakladni pravidlo: zadny modul nesmi zapisovat primo do verejne produkce bez validace, registru URL a moznosti rollbacku.

## 3. Navrzena struktura systemu

```text
00_SYSTEM/
  rules/
  registries/
  standards/

10_CONTENT_ENGINE/
  templates/
  blocks/
  copy/
  prompts/

20_AUTOMATION/
  parsers/
  normalizers/
  validators/
  generators/
  publishers/
  reports/

30_DATA/
  cars/
  auctions/
  pricing/
  products/
  leads/
  registries/

40_OUTPUT/
  generated/
  public/
  previews/

50_ASSETS/
  cars/
  brand/
  shared/

60_ARCHIVE/
  snapshots/
  legacy/
  reports/

90_LAB/
  experiments/
  simulators/

docs/AUTO_V4/
  PROJECT_ANALYSIS.md
  ARCHITECTURE.md
```

## 4. Modulovy prehled

### 4.1 `system-rules`

Ucel:

Centralni pravidla pro cely system. Definuje, co je produkce, co je archiv, jak se smi pracovat s verejnymi URL, jak se pojmenovavaji soubory a jake standardy musi splnit data.

Vstupy:

- soucasne dokumenty v `00_SYSTEM`,
- rucne doplnene bezpecnostni zasady,
- seznam produkcnich URL,
- pravidla GitHub Pages publikace.

Vystupy:

- strojove citelne a lidsky citelne standardy,
- pravidla pro validatory,
- seznam zakazanych operaci,
- rozhodovaci pravidla pro publikaci.

Zavislosti:

- zadne technicke zavislosti,
- navazuje na `url-registry`, `data-model`, `publisher`.

Verejne API:

- `get_rules(scope)`
- `is_public_path(path)`
- `requires_snapshot(path)`
- `can_publish(change_set)`
- `get_naming_policy(entity_type)`

Datove struktury:

```text
SystemRule
  id
  name
  scope
  severity
  description
  appliesTo
  enforcementMode

NamingPolicy
  entityType
  pattern
  examples
  forbiddenPatterns
```

Budouci rozsireni:

- automaticka kontrola pravidel v CI,
- ruzne rezimy: `draft`, `preview`, `public`, `archive`,
- schvalovaci workflow pro produkcni zmeny.

### 4.2 `url-registry`

Ucel:

Jeden zdroj pravdy pro verejne URL, legacy vystupy, redirecty a publikacni status. Chrani hlavni pravidlo projektu: stare verejne odkazy se nesmi rozbit.

Vstupy:

- existujici `nabidky/index.html`,
- soubory v `nabidky/*`,
- vystupy v `40_OUTPUT`,
- rucne potvrzene produkcni URL.

Vystupy:

- registr URL,
- status kazde URL: `public`, `preview`, `legacy`, `archive`, `deprecated`,
- seznam zmen vyzadujicich redirect nebo archiv,
- podklady pro generator indexu.

Zavislosti:

- `system-rules`,
- `output-validator`,
- `publisher`.

Verejne API:

- `register_url(url_record)`
- `get_url_status(path_or_url)`
- `assert_url_safe(change_set)`
- `list_public_urls(filter)`
- `resolve_canonical_url(entity_id, page_type)`

Datove struktury:

```text
UrlRecord
  id
  entityId
  pageType
  path
  publicUrl
  status
  createdAt
  lastVerifiedAt
  replacementUrl
  notes
```

Budouci rozsireni:

- automaticka kontrola 404,
- generovani redirect mapy,
- integrace s GitHub Pages deploymentem,
- historie zmen URL.

### 4.3 `data-model`

Ucel:

Definuje jednotne datove struktury pro auto, aukci, pricing, scoring, produkty, assety a leady. Je to zaklad, na kterem stoji vsechny dalsi moduly.

Vstupy:

- existujici HTML nabidky,
- data z AUTO1/OPENLANE,
- manualni zadani,
- pozdeji email parsery,
- cenove a produktove konfigurace.

Vystupy:

- normalizovana data v `30_DATA`,
- validovatelne JSON/CSV struktury,
- datove kontrakty pro generator, scoring a lead modul.

Zavislosti:

- `system-rules`,
- `taxonomy`,
- `asset-registry`.

Verejne API:

- `validate_car(car)`
- `normalize_car(raw_input)`
- `get_car(car_id)`
- `list_cars(filter)`
- `merge_car_update(car_id, patch)`

Datove struktury:

```text
Car
  id
  source
  sourceItemId
  make
  model
  variant
  year
  mileageKm
  fuel
  transmission
  powerKw
  vin
  auction
  pricing
  condition
  assets
  documents
  scoring
  publication

Auction
  platform
  itemId
  url
  startAt
  endAt
  country
  currency
  currentBid
  buyNowPrice

Publication
  status
  publicPath
  canonicalUrl
  generatedAt
  pageTypes
```

Budouci rozsireni:

- schema verze,
- import/export CSV,
- datove migrace,
- napojeni na externi aukcni API,
- historie zmen auta.

### 4.4 `taxonomy`

Ucel:

Sjednocuje ciselniky, nazvy stavu, typy produktu, typy stran, zdroje, statusy a segmenty zakazniku.

Vstupy:

- existujici nazvy stran a produktu v `nabidky`,
- pravidla z `data-standard.md`,
- obchodni terminologie.

Vystupy:

- stabilni ciselniky,
- mapovani starych nazvu na nove,
- kontrola povolenych hodnot.

Zavislosti:

- `data-model`,
- `content-engine`,
- `lead-schema`.

Verejne API:

- `get_allowed_values(type)`
- `normalize_value(type, value)`
- `get_page_type_config(page_type)`
- `get_product_config(product_code)`

Datove struktury:

```text
TaxonomyItem
  type
  code
  label
  description
  aliases
  active

PageType
  code
  label
  requiredBlocks
  outputPattern
```

Budouci rozsireni:

- lokalizace,
- ruzne segmenty B2B/B2C,
- mapping pro CRM.

### 4.5 `asset-registry`

Ucel:

Centralni evidence obrazku, log, dokumentu a dalsich souboru. Resi duplicity fotek a vazbu assetu na konkretni auta a vystupy.

Vstupy:

- soucasne `nabidky/*/img`,
- budouci fotky z aukci,
- brand assety,
- dokumenty k autum.

Vystupy:

- registr assetu,
- deduplikacni report,
- stabilni cesty k assetum,
- galerie pro generator.

Zavislosti:

- `data-model`,
- `output-generator`,
- `archive-manager`.

Verejne API:

- `register_asset(asset)`
- `find_duplicates(asset_or_hash)`
- `get_assets_for_car(car_id)`
- `build_gallery(car_id, options)`
- `resolve_asset_path(asset_id)`

Datove struktury:

```text
Asset
  id
  carId
  type
  role
  path
  originalSourceUrl
  hash
  width
  height
  sizeBytes
  status
  altText

Gallery
  carId
  images
  primaryImageId
  fallbackPolicy
```

Budouci rozsireni:

- automaticka komprese obrazku,
- generovani thumbnailu,
- alt text generator,
- CDN nebo oddelene asset repo.

### 4.6 `pricing-engine`

Ucel:

Jednotny vypocet ekonomiky auta: nakupni cena, aukcni poplatky, doprava, opravy, DPH, prodejni cena, marze, rizikova rezerva a doporuceny max bid.

Vstupy:

- `Car`,
- `Auction`,
- kurz meny,
- konfigurace poplatku,
- odhad oprav,
- obchodni model: FO, ICO, agenturni nakup, mentoring, premium.

Vystupy:

- pricing report,
- hodnoty pro nabidku,
- hodnoty pro scoring,
- podklady pro CTA a obchodni argumentaci.

Zavislosti:

- `data-model`,
- `taxonomy`,
- `config-registry`.

Verejne API:

- `calculate_pricing(car, scenario)`
- `calculate_max_bid(target_margin, scenario)`
- `compare_scenarios(car)`
- `get_pricing_summary(car_id)`

Datove struktury:

```text
PricingScenario
  code
  buyerType
  currency
  purchasePrice
  buyerFee
  transportCost
  repairEstimate
  vatMode
  salePrice
  margin
  marginPercent
  riskReserve
  recommendedMaxBid

FeeConfig
  platform
  buyerFeeRules
  transportRules
  vatRules
```

Budouci rozsireni:

- aktualni kurz EUR/CZK,
- ruzne zeme dopravy,
- historicka porovnani prodejnich cen,
- simulace vice cenovych variant.

### 4.7 `scoring-engine`

Ucel:

Oddelene vyhodnocuje technickou, financni a obchodni atraktivitu auta. Vystupem je srozumitelne doporuceni pro nabidku a interni rozhodovani.

Vstupy:

- `Car`,
- `PricingScenario`,
- condition report,
- historie skod,
- fotky a dokumenty,
- trzni kontext.

Vystupy:

- celkove skore,
- rizikove faktory,
- doporuceni koupit/nekoupit/podminene,
- checklist pred nakupem,
- textove bloky pro obsah.

Zavislosti:

- `data-model`,
- `pricing-engine`,
- `content-engine`.

Verejne API:

- `score_car(car, pricing)`
- `get_risk_factors(car_id)`
- `generate_buy_recommendation(score)`
- `build_inspection_checklist(car_id)`

Datove struktury:

```text
ScoreReport
  carId
  totalScore
  technicalScore
  financialScore
  marketScore
  confidence
  verdict
  riskFactors
  checklist
  generatedAt

RiskFactor
  code
  severity
  title
  description
  mitigation
```

Budouci rozsireni:

- AI asistovana analyza condition reportu,
- historicke porovnani podobnych aut,
- samoucici vahy scoringu podle realnych vysledku prodeje.

### 4.8 `content-engine`

Ucel:

Generuje strukturovany obsah z dat: headline, sekce nabidky, CTA, vysvetleni produktu, social posty, emaily a landing page copy.

Vstupy:

- `Car`,
- `PricingScenario`,
- `ScoreReport`,
- promptove protokoly,
- sablony a obsahove bloky.

Vystupy:

- obsahove bloky pro HTML generator,
- texty pro B2B/B2C,
- social posty,
- email follow-up,
- meta title a meta description.

Zavislosti:

- `data-model`,
- `pricing-engine`,
- `scoring-engine`,
- `taxonomy`,
- `template-engine`.

Verejne API:

- `build_offer_copy(car_id, audience)`
- `build_page_blocks(car_id, page_type)`
- `build_social_post(car_id, channel)`
- `build_cta(product_code, audience)`
- `build_meta(page_context)`

Datove struktury:

```text
ContentBlock
  id
  blockType
  audience
  title
  body
  cta
  dataBindings

CopyVariant
  id
  audience
  tone
  pageType
  blocks
```

Budouci rozsireni:

- A/B varianty,
- jazykove mutace,
- napojeni na AI generovani,
- knihovna overenych CTA.

### 4.9 `template-engine`

Ucel:

Oddeluje sablony stran od dat. Vytvari jednotnou skladbu stran bez kopirovani inline HTML struktur mezi vystupy.

Vstupy:

- obsahove bloky,
- `Car`,
- galerie z `asset-registry`,
- konfigurace page type,
- layout sablony.

Vystupy:

- renderovatelny page model,
- HTML dokument pro generator,
- seznam potrebnych assetu,
- seznam internich odkazu.

Zavislosti:

- `content-engine`,
- `asset-registry`,
- `taxonomy`,
- `lead-client-v4`.

Verejne API:

- `render_page(page_context)`
- `render_block(block, data)`
- `list_required_assets(page_context)`
- `get_template(page_type, version)`

Datove struktury:

```text
PageContext
  carId
  pageType
  audience
  templateVersion
  contentBlocks
  assets
  leadForms
  navigation

RenderedPage
  path
  html
  assets
  links
  metadata
```

Budouci rozsireni:

- vice layoutu,
- komponentni knihovna,
- tiskova/PDF verze,
- preview rezim.

### 4.10 `lead-schema`

Ucel:

Definuje jednotny payload pro vsechny formulare, bez ohledu na to, jestli lead prichazi z nabidky, landing page, modal okna nebo objednavky.

Vstupy:

- pole formularu,
- kontext stranky,
- UTM parametry,
- produkt/sluzba,
- carId a pageType.

Vystupy:

- validovany lead payload,
- mapovani pro Google Sheets,
- mapovani pro notifikacni e-mail,
- priprava na CRM.

Zavislosti:

- `taxonomy`,
- `data-model`,
- `lead-client-v4`,
- `lead-backend`.

Verejne API:

- `validate_lead_payload(payload)`
- `normalize_lead_payload(raw_payload)`
- `map_lead_to_sheet_row(payload)`
- `map_lead_to_notification(payload)`

Datove struktury:

```text
Lead
  id
  createdAt
  source
  pageUrl
  pageType
  carId
  productCode
  audience
  name
  email
  phone
  company
  message
  consent
  utm
  rawPayload

Utm
  source
  medium
  campaign
  content
  term
```

Budouci rozsireni:

- GDPR consent evidence,
- lead scoring,
- CRM synchronizace,
- deduplikace kontaktu.

### 4.11 `lead-client-v4`

Ucel:

Jednotny front-end klient pro odesilani leadu ze vsech statickych stran. Nahrazuje inline `fetch()` ve vystupech a navazuje na existujici `lead-client.js`.

Vstupy:

- HTML formular,
- konfigurace endpointu,
- `Lead` schema,
- page context.

Vystupy:

- odeslany lead do backendu,
- lokalni stav odeslani,
- success/error UX signal pro stranku,
- analytics event.

Zavislosti:

- `lead-schema`,
- `config-registry`,
- `lead-backend`.

Verejne API:

- `bind_form(form_id, options)`
- `submit_lead(payload)`
- `collect_page_context()`
- `collect_utm()`
- `handle_submit_result(result)`

Datove struktury:

```text
LeadClientConfig
  endpoint
  defaultSource
  pageType
  carId
  productCode
  successBehavior
  errorBehavior
```

Budouci rozsireni:

- offline retry,
- spam protection,
- analytics integrace,
- vice backend endpointu podle prostredi.

### 4.12 `lead-backend`

Ucel:

Serverova cast lead capture. V prvni verzi muze zustat Google Apps Script, ale musi respektovat jednotne schema a stabilni mapovani do Google Sheets.

Vstupy:

- `Lead` payload,
- konfigurace Google Sheet,
- notifikacni pravidla.

Vystupy:

- radek v Google Sheets,
- notifikacni e-mail,
- auto-reply,
- odpoved klientovi.

Zavislosti:

- `lead-schema`,
- `config-registry`,
- Google Apps Script,
- Google Sheets,
- MailApp.

Verejne API:

- `receive_lead(request)`
- `validate_request(request)`
- `append_to_sheet(lead)`
- `notify_owner(lead)`
- `send_auto_reply(lead)`

Datove struktury:

```text
LeadBackendConfig
  sheetId
  sheetName
  notifyEmail
  autoReplyEnabled
  allowedOrigins
  schemaVersion
```

Budouci rozsireni:

- CRM webhook,
- anti-spam kontrola,
- double opt-in,
- audit log,
- oddeleni B2B/B2C sheetu.

### 4.13 `output-generator`

Ucel:

Orchestruje tvorbu vystupu. Vezme data, scoring, pricing, obsah, sablony a assety a pripravi staticke soubory do preview nebo public vrstvy.

Vstupy:

- `Car`,
- `PricingScenario`,
- `ScoreReport`,
- `PageContext`,
- sablony,
- registr URL.

Vystupy:

- HTML stranky,
- index stranky,
- manifest vystupu,
- seznam zmen pro validaci.

Zavislosti:

- `data-model`,
- `pricing-engine`,
- `scoring-engine`,
- `content-engine`,
- `template-engine`,
- `asset-registry`,
- `url-registry`.

Verejne API:

- `generate_offer(car_id, options)`
- `generate_page(page_context)`
- `generate_index(scope)`
- `build_output_manifest(run_id)`

Datove struktury:

```text
OutputManifest
  runId
  generatedAt
  sourceData
  pages
  assets
  links
  warnings

GeneratedFile
  path
  type
  sourceEntityId
  checksum
  publicUrl
```

Budouci rozsireni:

- PDF export,
- email export,
- social image export,
- hromadne generovani nabidek.

### 4.14 `output-validator`

Ucel:

Kontroluje, ze vystupy jsou bezpecne publikovatelne: existuji titulky, meta popisy, obrazky, odkazy, lead formulare, zadne zakazane endpointy a zadne rozbite verejne URL.

Vstupy:

- `OutputManifest`,
- vygenerovane HTML,
- `url-registry`,
- `asset-registry`,
- pravidla systemu.

Vystupy:

- validation report,
- blokujici chyby,
- varovani,
- seznam oprav pred publikaci.

Zavislosti:

- `system-rules`,
- `url-registry`,
- `asset-registry`,
- `lead-schema`.

Verejne API:

- `validate_output(manifest)`
- `validate_links(page)`
- `validate_assets(page)`
- `validate_lead_forms(page)`
- `assert_publishable(manifest)`

Datove struktury:

```text
ValidationReport
  runId
  status
  errors
  warnings
  checkedFiles
  checkedUrls

ValidationIssue
  severity
  code
  file
  location
  message
  suggestedFix
```

Budouci rozsireni:

- HTML validator,
- Lighthouse kontrola,
- mobilni screenshot kontrola,
- automaticka kontrola externich odkazu.

### 4.15 `publisher`

Ucel:

Bezpecne presouva validovane vystupy do publikacni vrstvy. Nikdy nema publikovat bez validace a URL registru.

Vstupy:

- validovany `OutputManifest`,
- cil publikace,
- URL registr,
- snapshot plan.

Vystupy:

- publikovane soubory,
- aktualizovany URL registr,
- publish report,
- rollback informace.

Zavislosti:

- `output-validator`,
- `url-registry`,
- `archive-manager`,
- `system-rules`.

Verejne API:

- `prepare_publish(manifest)`
- `publish(manifest, target)`
- `create_snapshot(paths)`
- `rollback(publish_id)`
- `generate_publish_report(publish_id)`

Datove struktury:

```text
PublishPlan
  id
  sourceManifestId
  target
  filesToAdd
  filesToUpdate
  filesToArchive
  requiredSnapshots

PublishReport
  publishId
  status
  publishedFiles
  skippedFiles
  snapshotId
  warnings
```

Budouci rozsireni:

- GitHub Actions publish,
- manual approval step,
- staging/prod vetve,
- automaticky changelog.

### 4.16 `archive-manager`

Ucel:

Udrzuje historii vystupu, snapshoty a legacy obsah. Umoznuje uklid bez mazani hodnotnych nebo verejnych souboru.

Vstupy:

- soubory k archivaci,
- publish plan,
- URL registr,
- metadata vystupu.

Vystupy:

- snapshot,
- archivni zaznam,
- rollback body,
- audit historie.

Zavislosti:

- `url-registry`,
- `publisher`,
- `system-rules`.

Verejne API:

- `create_snapshot(paths, reason)`
- `archive_output(path, metadata)`
- `get_snapshot(snapshot_id)`
- `restore_snapshot(snapshot_id)`
- `list_archived_outputs(filter)`

Datove struktury:

```text
Snapshot
  id
  createdAt
  reason
  paths
  checksums
  relatedPublishId

ArchiveRecord
  id
  originalPath
  archivePath
  entityId
  status
  archivedAt
  notes
```

Budouci rozsireni:

- komprimovane archivy,
- diff mezi verzemi,
- automaticke archivacni politiky,
- knowledge base nad historickymi analyzami.

### 4.17 `parser-ingestion`

Ucel:

Prevadi vstupy z emailu, aukcnich stran, CSV nebo manualnich poznamek do normalizovanych dat.

Vstupy:

- AUTO1/OPENLANE email,
- CSV export,
- manualni text,
- URL aukce,
- JSON ze simulatoru.

Vystupy:

- raw import record,
- normalizovany `Car`,
- seznam nejistych poli k rucnimu doplneni.

Zavislosti:

- `data-model`,
- `taxonomy`,
- `asset-registry`.

Verejne API:

- `parse_email(raw_email)`
- `parse_csv(row)`
- `parse_manual_input(text)`
- `normalize_import(raw_record)`
- `report_missing_fields(car)`

Datove struktury:

```text
ImportRecord
  id
  source
  receivedAt
  rawContent
  extractedFields
  confidence
  missingFields

ImportResult
  importId
  car
  warnings
  requiredManualReview
```

Budouci rozsireni:

- Gmail integrace,
- OCR z PDF condition reportu,
- parser aukcnich screenshotu,
- automaticke stahovani fotek.

### 4.18 `config-registry`

Ucel:

Centralni konfigurace endpointu, prostredi, kurzovych hodnot, kontaktu, produktu, defaultnich cest a feature flags.

Vstupy:

- rucni konfigurace,
- prostredi `dev`, `preview`, `public`,
- obchodni nastaveni.

Vystupy:

- konfigurace pro moduly,
- konfigurace pro lead klient,
- hodnoty pro pricing.

Zavislosti:

- `system-rules`,
- `taxonomy`.

Verejne API:

- `get_config(scope, environment)`
- `get_endpoint(name, environment)`
- `get_contact_profile(profile_id)`
- `get_feature_flag(flag_name)`

Datove struktury:

```text
ConfigValue
  key
  environment
  value
  secret
  description

ContactProfile
  id
  name
  email
  phone
  company
  ico
  dic
```

Budouci rozsireni:

- oddeleni tajnych hodnot mimo repo,
- vice brand profilu,
- konfigurace pro klienty/partnery.

### 4.19 `reporting`

Ucel:

Vytvari prehledy o stavu systemu: data completeness, duplicity assetu, publikovane URL, leady, vygenerovane vystupy a rizika.

Vstupy:

- registry,
- validation reporty,
- lead data,
- publish reporty,
- asset registry.

Vystupy:

- audit reporty,
- seznam chyb,
- stav pripravenosti auta k publikaci,
- metriky konverzi.

Zavislosti:

- `url-registry`,
- `asset-registry`,
- `lead-schema`,
- `output-validator`,
- `publisher`.

Verejne API:

- `build_system_report()`
- `build_car_readiness_report(car_id)`
- `build_asset_duplicate_report()`
- `build_lead_report(period)`
- `build_url_health_report()`

Datove struktury:

```text
SystemReport
  generatedAt
  summary
  modules
  risks
  actionItems

ReadinessReport
  carId
  status
  missingData
  validationIssues
  recommendedNextStep
```

Budouci rozsireni:

- dashboard,
- pravidelny e-mail report,
- business metriky,
- konverzni funnel.

### 4.20 `lab-simulator-adapter`

Ucel:

Oddeli hodnotnou logiku ze soucasneho aukcniho simulatoru od monoliticke HTML stranky a umozni ji pozdeji pouzit pro pricing, max bid a scenare.

Vstupy:

- data simulatoru,
- `Car`,
- `PricingScenario`,
- aukcni parametry.

Vystupy:

- simulacni scenare,
- max bid doporuceni,
- vystupy pro interni analyzu,
- podklady pro scoring.

Zavislosti:

- `pricing-engine`,
- `scoring-engine`,
- `data-model`.

Verejne API:

- `simulate_auction(car_id, scenario)`
- `compare_bid_strategies(car_id)`
- `estimate_profit_range(car_id)`
- `export_simulation_result(result)`

Datove struktury:

```text
AuctionSimulation
  id
  carId
  scenario
  competitors
  maxBid
  result
  profitEstimate

BidStrategy
  code
  maxBid
  timing
  riskLevel
```

Budouci rozsireni:

- Monte Carlo simulace,
- historicka data aukci,
- interaktivni interni nastroj,
- napojeni na realne pricing reporty.

## 5. Hlavni datove entity

```text
Car
Auction
Condition
PricingScenario
ScoreReport
Asset
Gallery
Product
ContentBlock
PageContext
RenderedPage
OutputManifest
UrlRecord
Lead
ValidationReport
PublishPlan
Snapshot
ImportRecord
SystemReport
```

Vztahy:

- `Car` ma jednu nebo vice `Auction`.
- `Car` ma vice `Asset`.
- `Car` ma vice `PricingScenario`.
- `Car` ma jeden aktualni `ScoreReport`.
- `PageContext` spojuje `Car`, `ContentBlock`, `Asset`, `LeadForm` a `UrlRecord`.
- `RenderedPage` vznikne z `PageContext`.
- `OutputManifest` sdruzuje vice `RenderedPage`.
- `ValidationReport` schvaluje nebo blokuje `OutputManifest`.
- `PublishPlan` vychazi z validovaneho `OutputManifest`.
- `Lead` odkazuje na `Car`, `PageType`, `Product` a `UrlRecord`.

## 6. Toky systemu

### 6.1 Tok vytvoreni nove nabidky

```text
Import vstupu
  -> parser-ingestion
  -> data-model
  -> asset-registry
  -> pricing-engine
  -> scoring-engine
  -> content-engine
  -> template-engine
  -> output-generator
  -> output-validator
  -> publisher
  -> url-registry
```

### 6.2 Tok leadu

```text
Staticka stranka
  -> lead-client-v4
  -> lead-schema validation
  -> lead-backend
  -> Google Sheets
  -> e-mail notifikace
  -> budouci CRM
```

### 6.3 Tok bezpecne publikace

```text
Generated preview
  -> output-validator
  -> url-registry check
  -> archive-manager snapshot
  -> publisher
  -> publish report
```

### 6.4 Tok archivace

```text
Stary vystup
  -> url-registry status check
  -> snapshot
  -> archive-manager
  -> redirect/replacement metadata
  -> reporting
```

## 7. Poradi implementace

### Faze 1 - Zakladni kontrakty

1. `system-rules`
2. `taxonomy`
3. `data-model`
4. `config-registry`
5. `url-registry`

Proc:

Bez techto kontraktu by dalsi moduly jen kodifikovaly soucasny chaos. Nejdrive musi byt jasne, co je auto, co je produkt, co je URL, co je public a jake hodnoty jsou povolene.

### Faze 2 - Evidence a validace

6. `asset-registry`
7. `lead-schema`
8. `output-validator`
9. `reporting`

Proc:

Pred generovanim novych vystupu je potreba umet poznat, co chybi, co je duplicitni, co je rozbite a co by ohrozilo produkcni URL.

### Faze 3 - Obchodni logika

10. `pricing-engine`
11. `scoring-engine`
12. `content-engine`

Proc:

Az kdyz jsou data stabilni, ma smysl stavet vypocty, hodnoceni a obsah. Tyto moduly budou vyuzivat stejne datove struktury a nebudou zavisle na finalnim HTML.

### Faze 4 - Generovani vystupu

13. `template-engine`
14. `output-generator`
15. `lead-client-v4`

Proc:

Sablony a generator maji prijit az po datovych kontraktech, jinak by se musely prepisovat. Lead klient se zavede soucasne s novymi vystupy, aby nevznikala dalsi inline odesilani.

### Faze 5 - Publikace a archiv

16. `archive-manager`
17. `publisher`
18. `lead-backend`

Proc:

Publikace musi byt az po validaci a snapshot strategii. Lead backend lze ze zacatku ponechat jako kompatibilni Google Apps Script, ale musi prijmout nove lead schema.

### Faze 6 - Automaticke vstupy a rozsireni

19. `parser-ingestion`
20. `lab-simulator-adapter`

Proc:

Parsery a simulator maji nejvetsi nejistotu. Je lepsi je pripojit az ve chvili, kdy existuje stabilni datovy model, pricing a scoring.

## 8. Minimalni vertikala pro prvni funkcni verzi

Prvni funkcni verze nemusi obsahovat vsechny moduly. Minimalni bezpecna vertikala:

```text
data-model
taxonomy
url-registry
asset-registry
lead-schema
pricing-engine
scoring-engine
content-engine
template-engine
output-generator
output-validator
```

Prvni testovaci vystup:

- jedno nove auto,
- nova preview URL,
- zadny prepis existujicich `nabidky/*`,
- lead formular podle `lead-schema`,
- vygenerovany manifest,
- validation report.

## 9. Zasady pro vyvoj bez prepisovani architektury

1. Nezacinat generatorem HTML. Zacinat datovym modelem.
2. Kazdy modul musi mit jasne vstupy a vystupy.
3. Verejne URL jsou data, ne vedlejsi efekt.
4. HTML je vystup, ne zdroj pravdy.
5. Assety patri do registru, ne nahodne do vystupnich slozek.
6. Lead payload musi byt stejny pro vsechny formulare.
7. Publikace musi byt oddelena od generovani.
8. Archivace musi byt soucast publikace, ne dodatecny uklid.
9. Simulator a experimenty zustavaji v LAB, dokud nemaji stabilni kontrakt.
10. Kazda nova automatizace musi mit dry-run rezim a report.

## 10. Doporučeny cilovy stav

BATKO_AUTO_V4 bude mit jasne oddelene vrstvy:

- `30_DATA` jako zdroj pravdy,
- `50_ASSETS` jako zdroj obrazku a dokumentu,
- `10_CONTENT_ENGINE` jako zdroj sablon a copy,
- `20_AUTOMATION` jako pipeline moduly,
- `40_OUTPUT` jako generovane vystupy,
- `nabidky` jako stabilni verejna vrstva,
- `60_ARCHIVE` jako historie a rollback,
- `00_SYSTEM` jako pravidla a registry.

Takova architektura umozni postupne pridavat parsery, AI generovani, CRM, dashboardy nebo aukcni simulace bez toho, aby se znovu prepisovaly zakladni datove struktury a publikacni pravidla.
