
---

## !! AUTOMATICKY REFRESH DEALER POOLU - POVINNE OD 2026-07-18 !!

Refresh dealer poolu se NIKDY nenechava jako ukol uzivateli. Codex/Claude/cowork ho dela SAM
v ramci denni Sauto vlny, jeste PRED generovanim HTML.

Kontrola pred kazdou vlnou:
1. Nacist nejnovejsi `docs\SAUTO_SMALL_DEALERS_*.json`.
2. Spocitat neoslovene dealery. Blocklist = `sent_ids` ze `sauto_summary` + vsechna
   `data-lead-id="dealer-..."` + vsechna Sauto ID karet ze vsech vlnovych HTML v `docs\`.
3. Pokud zbyva mene nez 40 neoslovenych dealeru, spustit refresh OKAMZITE a bez ptani.

Refresh v sandboxu NEFUNGUJE (`scripts\sauto_small_dealer_finder.py` nema sit, urllib hodi 403).
Povinna cesta je finder-lite pres Chrome JS na tabu `sauto.cz` (same-origin fetch):

1. Sken search API: `category_id=838&condition_seo=ojete&item_age_cb=7&sort=create_date_asc`
   `&limit=80&price_from=150000&price_to=1200000&offset=...`
   Sbirat unikatni `premise.id` mimo blocklist a mimo velke retezce
   (AAA Auto, Auto ESA, Das WeltAuto, Mototechna, Automodul).
   Skenovat i hlubsi offsety (klidne do 10000) — pri velkem blocklistu prvnich 1200 inzeratu
   nemusi dat skoro nic (vlna 074: prvnich 1200 = 8 kandidatu, hlubsi sken = 290).
2. Enrichment kazdeho premise_id dotazem `premise_id=<pid>&limit=80`.
   Filtr: sklad 6-40, prumerna cena >= 250 000, score >= 50.
   Score vzorec je zkopirovany z `sauto_small_dealer_finder.py`:
   sklad 30 b + cena 18/8/-18 + stalled 22/14/7 + import 12 + target min(18, n*3) + kapital 18/12/6.
3. Davkovat ~35 fetchu na jedno JS volani (vic = CDP timeout 45 s). Stav drzet ve `window`
   promennych. Po timeoutu NEOPAKOVAT davku — smycka dobehne na pozadi, jen precist stav.
4. Cil je alespon 45 novych dealeru.
5. Vysledky prenest chunk-y (JS tool orezava vystup ~1000 znaku, slice po <= 950; base64 je
   blokovany filtrem, prenaset jen plain text) a v sandboxu sestavit
   `docs\SAUTO_SMALL_DEALERS_RRRRMMDD_REFRESH.json` ve schematu puvodniho finderu:
   `shortlist` + `all_dealers`, `sample_cars` s `url/id/make/model/price/tachometer/days_on_market/create_date`.

Overeny vysledek 2026-07-18 (vlna 074): 1225 inzeratu skenovano, 290 kandidatu po blocklistu,
225 enrichnuto, 50 dealeru vyhovelo (hit rate ~20 %).

Toto pravidlo je zapsane i v promptu scheduled tasku `denni-sauto-vlna-automat` (krok 2).

---

## !! SAUTO HTML NABIDKA PRODEJCUM - POVINNY GATE OD 2026-07-11 !!

Pro kazdou dalsi denni SAUTO HTML nabidku prodejcum musi Codex po vytvoreni draftu VZDY spustit strict builder:

```text
python scripts\sauto_wave45_strict_builder.py --draft "<draft_html>" --out "<final_html>" --wave <XXX> --created-at "<RRRRMMDD HHMM>" --cards 20
```

Pevny layoutovy zdroj je vzor 45:

```text
docs\20260702 0148 045 HTML nabidka prodejcum na SAUTO.html
```

Bez vystupu `OK: SAUTO HTML vytvoreno pres pevny vzor 45.` NESMI Codex rict, ze je hotovo.
Pokud strict builder vypise `CHYBA:`, opravit draft/data a spustit builder znovu.
Finalni odpoved musi uvest, ze builder prosel, a zkontrolovat karty, price-comp bloky, odkazy, UTF-8 a JS funkce.

---
# CODEX.md - napojeni Codexu na projekt auto1

Tento soubor je orientacni mapa pro praci Codexu v existujicim projektu `auto1`.
Projektova historie a struktura vznikla v prostredi Claude, proto ji Codex nema prepisovat ani sjednocovat nasilu.

---

## !! OPENLANE <-> SAUTO MASTER TOOL - POVINNE OD 2026-07-10 !!

Kdyz uzivatel zada hledani obchodni prilezitosti mezi OPENLANE a ceskym trhem,
safe bid, predvyber aut, audit konkretni aukce nebo zakaznicky vystup, Codex
musi nejdriv otevrit:

```text
docs\auto_arbitrage_finder\portable_master_tool\00_MASTER_PROMPT_OPENLANE_SAUTO.md
```

Rychla copy-paste verze pro cowork, Claude, Gemini nebo jiny model:

```text
docs\auto_arbitrage_finder\portable_master_tool\01_COPY_PASTE_PROMPT_SHORT.md
```

Checklist operatora:

```text
docs\auto_arbitrage_finder\portable_master_tool\02_OPERATOR_CHECKLIST.md
```

Sablony vystupu:

```text
docs\auto_arbitrage_finder\portable_master_tool\03_OUTPUT_TEMPLATES.md
```

Pravidlo uspory kreditu:
1. nejdriv levne sito ze seznamu/karet,
2. detail/report jen u top kandidatu,
3. zadne KOUPIT/DRAZIT/PRIHODIT bez reportu, poplatku, dopravy, trhu a rezerv,
4. oddelovat aktivni ROI limit od absolutniho max bidu,
5. zakaznicky vystup delat az po overeni ekonomiky a rizik.

Referencni priklady:

```text
docs\zakaznicke_vystupy\20260706_OPENLANE_AAA_zakaznicky_predvyber.html
docs\zakaznicke_vystupy\20260706_OPENLANE_11204330_Kodiaq_plny_audit_safe_bid.html
```

Pokud jde o OPENLANE/SAUTO arbitraz, tento master tool ma prednost pred starsimi
roztrousenymi prompty. Starsi SOP se pouziji jako podpurne zdroje, ne jako nahrada.

---

## !! KRITICKE POUCENI Z AUK-012 — POVINNE PRO VSECHNY DALSI AUKCE (2026-06-22) !!

### 1. NIKDY negenerovat aukci HTML od nuly — VZDY sablona z AUK-011
Pricina selhani: AUK-012 byl vygenerovan bez sablony. Chybely: Firebase SDK v8 compat,
documents[], b2b-block, calc-block, detailLinkWrap, euAuctionNextBidKc, eurRate.
Opraveno az po nahrani — zpusobilo ztracene kredity a cas uzivatele.
POVINNY POSTUP: Python skript precte AUK-011 index.html jako sablonu a chirurgicky
nahradi jen AUCTION_CONFIG blok + extras-detail + b2b hardcoded hodnoty.

### 2. NEJDRIV zpracovat vsechny nahrane podklady (PDF, docx), PAK generovat
Pricina selhani: nahrany DEKRA, fotoanlage, COC, schadenshistorie a listing.docx
byly ignorovany. Vysledek: "DSG 4x4" misto Frontantrieb/FWD (DEKRA strana 1).
POVINNY POSTUP: pred generovanim AUCTION_CONFIG precist vsechny soubory
a overit pohon, VIN, HU, poskozeni z DEKRA zpravy.

### 3. endTime VZDY z OpenLane stranky aukce — NIKDY odhadovat
Pricina selhani: endTime nastaven na 2026-06-29 misto skutecneho 2026-06-23.
POVINNY POSTUP: generovaci skript musi vypsat endTime jako varovani;
nase verejna aukce = 2h pred koncem OpenLane.

### 4. AUCTION_CONFIG musi byt `var`, ne `const`
`const` neni dostupne jako window.AUCTION_CONFIG → runtime chyby.

### 5. documents[] pouziva klic `file`, ne `url`
AUK-011 JS cte `d.file`; pouzivat `{"label": "...", "file": "docs/soubor.pdf"}`.

---

## !! KRITICKA CHYBA OPRAVENA 2026-06-16 — SAUTO DETAIL URL (ztracene hodiny uzivatele) !!

SPRAVNA URL pro "Otevrit inzerat" tlacitko:
  https://www.sauto.cz/osobni/detail/{make_seo}/{model_seo}/{id}
  Priklad: https://www.sauto.cz/osobni/detail/mazda/cx-3/210324032

SPATNA URL — ABSOLUTNE ZAKAZANA:
  https://www.sauto.cz/inzerce/osobni/{id}   ← otevira VYPIS (search), NE detail!

Slugy make_seo/model_seo z Sauto API: /api/v1/items/{id} → manufacturer_cb.seo_name / model_cb.seo_name
Fetch POUZE pres Chrome JS (sandbox blokuje Sauto API — 403).

GENERATOR pro vsechny dalsi vlny: `docs\gen_vlna_TEMPLATE.py`
  - obsahuje spravnou URL natvrdo
  - pri spusteni ODMITNE zapsat soubor, pokud by HTML obsahovalo spatnou URL /inzerce/osobni/
  - pro vlnu 012+ zkopirovat, zmenit VLNA_CISLO a candidates[]

---

## !! PROVOZNI INSTRUKCE (doplneno 2026-06-05) !!

### Jak se mnou pracuj
- Odpovídej vždy **česky**, anglické termíny jen v závorce
- Přeskakuj preambule, afirmace a závěrečná shrnutí — začni rovnou odpovědí
- Žádné "Skvělá otázka!", "Samozřejmě!", "Rád pomůžu"
- Žádné závěrečné "Dejte vědět, pokud potřebujete cokoliv dalšího"
- Pokud není řečeno jinak, drž odpovědi stručné (do 200 slov nebo odrážky)
- Před každým složitým úkolem se zeptej na upřesňující otázky
- Nikdy neodešli zprávu/email/SMS bez explicitního schválení
- Po každém vytvořeném/upraveném souboru vždy volat present_files

### Délka chatů
Při 15+ výměnách nebo přechodu na nové téma upozorni:
"⚠️ Doporučuji přejít do nového chatu. Napiš 'shrň chat'."

### Sparring / kritický režim
Když řeknu "zaútoč" nebo "najdi slabiny" — hledej aktivně chyby,
špatné předpoklady, rizika. Nepovzbuzuj, nekývej, buď brutálně upřímný.

### Thinking partner
Když řeknu "potřebuji to probrat" — neklaď rady, jen kladem otázky,
dokud sám nedospěju k závěru.

### Plné pokyny a šablony
Viz `docs\CLAUDE_SETUP_INSTRUKCE.md`

### Workflow pro technické úkoly (Explore → Plan → Code → Commit)
Před každým technickým úkolem (oprava chyby, nová funkce, změna HTML):
1. **Explore** — nejdřív prozkoumej relevantní soubory a kontext
2. **Plan** — navrhni plán opravy/změny, počkej na potvrzení
3. **Code** — teprve pak piš kód
4. **Commit/Output** — výstup + kontrola + present_files

Přeskočení Explore→Plan způsobuje, že se řeší špatný problém s jistotou.

---

## !! KNIHOVNA VÝZEV — opakované úkoly v auto1 !!

### KRITICKE PRAVIDLO: nova aukce od 2026-06-06

Od 2026-06-06 je zavazny vzor pro vsechny dalsi verejne aukce:

`aukce_system\aukce_TEMPLATE.html`

Tento soubor je prepsany podle opravene aukce AUK-005:
`aukce_system\20260606_AUK-005_VW_Passat_2023_Business\index.html`

Nikdy uz nepouzivat AUK-003 jako hlavni vzor. AUK-003 obsahoval stare/matouci predvyplnovani formulare a nejasnou DPH/nakladovou logiku.

Rychly a levny postup:
1. Zkopirovat `aukce_TEMPLATE.html` / aktualni opraveny vzor.
2. Menit jen data auta, fotky, dokumenty, rizika, ceny, aukcni ID a Firebase zaznam.
3. Nevymyslet layout, formulare, Sheet URL, Firebase logiku ani obchodni koncept.
4. Formular musi byt pri prvnim verejnem otevreni prazdny; po vlastnim prihodu si smi uzivatel predvyplnit jen svoje vlastni kontaktni udaje z localStorage pro danou aukci.
5. `minIncrement` pouzivat defaultne `1000`, pokud uzivatel nerekne jinak.
6. DPH/naklady drzet jednotne: vyvolavaci cena, prihozy a kalkulacka = bez DPH pro platce DPH; verejne trzni srovnani v CR = orientacne vc. DPH; B2B marze/ROI = bez DPH.
7. Kalkulacka musi ukazovat rozpad: prihoz + dovoz/prepis/priprava/servis bez DPH + zpracovani/provize bez DPH = celkem odhadem bez DPH. Stejna suma nakladu musi byt v B2B bloku.
8. Pred uploadem vzdy overit: `</html>`, pocet fotek v `photos[]` = pocet souboru, zadne zbytky stareho vzoru, zadne osobni predvyplnene udaje.

### CR trh / Sauto aukce - vzor od 2026-06-06

Pokud auto uz je v inzerci v CR a uzivatel doda Sauto URL nebo cesky inzerat, nepouzivat evropsky OPENLANE pohled jako hlavni ekonomiku. Pouzit:

`aukce_system\aukce_CR_TRH_TEMPLATE.html`

Archivni kopie vzoru:
`aukce_system\20260606 1741 VZOR aukce CR trh realny prijem prodavajiciho a naklad kupujiciho.html`

Ucel: aukce pro cesky trh, kde kupujici i prodavajici vidi realne vydaje/prijmy a bod, kde se muze potkat cena.

Povinne:
1. Z URL inzeratu vyplnit cenu prodavajiciho, srovnatelne ceny CR trhu: nejnizsi, median, maximum.
2. Vyvolavaci cenu nastavit defaultne o 10 % niz nez nejnizsi srovnatelna cena na trhu.
3. Vyplnit min/max naklady kupujiciho: prepis, kontrola, servis, znama poskozeni, brzke vydaje, rezerva.
4. Vyplnit denni vicanaklady prodavajiciho: pojisteni, parkovani, financovani, cas, ztrata hodnoty / budouci sleva.
5. Ukazat kupujicimu celkove porizeni pri min/max nakladech proti nejnizsi, medianove a maximalni cene trhu.
6. Ukazat prodavajicimu graf 0/30/60/90 dni: kolik realne zustane z pozadovane ceny po nakladech cekani.
7. Vyznačit orientacni idealni cenu / den, kde se potkava zajem kupujiciho a prodavajiciho.
8. DPH resit podle rezimu konkretniho inzeratu: platce porovnava bez DPH, neplatce vc. DPH.
9. V casti pro prodavajiciho musi byt vyrazne motto:
   `Nejdrazsi auto byva casto to, ktere se neproda vcas.`
10. Zachovat rozklikavaci edukacni blok pro prodavajiciho:
    - kratke vysvetleni musi byt viditelne/otevrene,
    - cele vysvetleni musi byt v dalsim rozkliknuti,
    - text musi rikat, ze samotne prani prodavajiciho prodat za urcitou cenu neni obchodni argument,
      pokud kupujici vidi srovnatelne levnejsi auto.
11. Audio prvky se nesmi zobrazovat, dokud nejsou skutecne vyplnene soubory:
    `sellerEducationAudio.shortSrc` a/nebo `sellerEducationAudio.longSrc`.
    Pokud jsou prazdne, zadne rozkliknuti pro zvuk se na verejne strance nezobrazi.
12. Denni ztrata prodavajiciho musi samostatne obsahovat `priceAgingLoss` =
    pokles hodnoty auta starnutim na trhu / budouci sleva. Ve vystupu musi byt videt rozpad:
    pokles hodnoty auta za den + ostatni denni naklady + celkem za den + dopad 30/60/90 dni.

### Sauto URL -> CR aukce: rychly technicky workflow (nauceno 2026-06-06)

Kdyz uzivatel posle primo Sauto detail URL typu:
`https://www.sauto.cz/osobni/detail/.../210458921`

Postup pro zrychleni:
1. Z URL vytahnout numeric ID a nejdriv nacist detail pres API:
   `https://www.sauto.cz/api/v1/items/{sauto_id}`
2. Z `result` brat data auta, cenu, VIN, vybavu, datumy, prodejce a pole `images`. HTML stranku parsovat az jako fallback.
3. Pro CR/Sauto aukci kopirovat `aukce_system\aukce_CR_TRH_TEMPLATE.html`, ne evropsky OPENLANE vzor.
4. Fotky nehotlinkovat. Stahnout je lokalne do `img\foto_01.jpg` atd. Sauto CDN muze vratit 400/401, pokud chybi referer nebo je spatne zakodovany transform. Funkcni tvar:
   `curl.exe -L -A "Mozilla/5.0" -e "https://www.sauto.cz/osobni/detail/..." --url "https:...jpeg?fl=exf%7Cres,1024,768,1%7Cwrm,/watermark/sauto.png,10,10%7Cjpg,80,,1" -o img/foto_01.jpg`
5. Po stazeni fotek overit, ze soubory nejsou jen chybova odpoved 100-500 B a ze `photos[]` odpovida skutecnemu poctu fotek.
6. Ceske texty/diakritiku nevkladat pres PowerShell 5 here-string bez jisteho UTF-8. Pri spatnem zapisu vznikne mojibake (`Ä`, `Ĺ`, `Ă`, `Å`). Pouzit `apply_patch`, UTF-8 aware editor nebo explicitni UTF-8 zapis a po ulozeni vizualne zkontrolovat stranku.
7. In-app Browser nemusi otevrit `file://`. Pro kontrolu spustit lokalni server z korene `auto1`:
   `python -m http.server 8766 --bind 127.0.0.1 --directory "C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1"`
   a otevrit `http://127.0.0.1:8766/aukce_system/SLOZKA/index.html`.
8. Kdyz lokalni URL vraci 404, skoro vzdy bezi server na spatnem portu nebo ze spatneho rootu. Overit `curl.exe -I` a pripadne pouzit jiny port.
9. Po uploadu na GitHub Pages muze byt kratce 404. Pockat 10-20 s, pridat cache-busting `?v=YYYYMMDD-HHMM` a overit HTML i prvni JPG pres `curl.exe -I`.

### OPENLANE aukce — rychle ROI vyhodnoceni z URL

```
Role: jsi analytik aukcnich aut pro rychle ekonomicke rozhodnuti.
Spoustec: uzivatel posle URL OPENLANE aukce nebo rekne "vyhodnot auto z aukce".
Ridici SOP: docs\SOP_OPENLANE_RYCHLE_ROI_VYHODNOCENI.md
Primarni cil: rozhodnout podle denniho ROI 0,5 %.
Sekundarni cil: cilovy zisk min. 30 000 Kc.

Postup:
1. Pouzij prihlaseny/riceny Chrome s DevTools portem, idealne oddeleny profil na portu 9333.
2. Vycti OPENLANE API: auction, bidpriceinfo pro next bid, transportoptions, damages, SellerExtraInfo.
3. Transport je povinny presny udaj z transportoptions; nikdy ho neodhaduj.
4. Technicky report je povinny: pres damage JSONP najdi ReportItems.Url, stahni externi PDF report a projdi ho.
5. Dohledej 3-5 aktualnich CZ trznich referenci a kurz CNB.
6. Spocitej ROI scenare 20/30/60 dni a max bid.
7. Vystup: ANO / PODMINECNE / NE, max bid EUR/Kc, tabulka nakladu, top 3 rizika, taktika aukce.

Pokud chybi cena, transport, report nebo trzni reference, oznac verdikt jako neovereny a nedoporucuj drazbu naslepo.
Nejdriv udelej rychle ROI sito; hlubsi marketingove vystupy delat az po ekonomickem "ANO/PODMINECNE".
```

---

### Nové auto z aukce

```
Role: jsi zkušený analytik ojetých aut a konverzní copywriter.
Úkol: připrav podklady pro nové auto z OPENLANE aukce.
Vstupy: [docx listing] + [md inspekční zpráva] + [opravy Kč]
Postup:
1. Přečti si soubory sám — neptej se na ruční zadávání dat
2. Fetchni kurz EUR/CZK z cnb.cz/denni_kurz.txt
3. Vyhledej tržní ceny na sauto.cz přes WebSearch
4. Vypočti feeCorrection = OL_Kč − (EUR × kurz)
5. Vypiš POUZE JSON blok pro ROI nástroj — žádné komentáře
Formát: čistý JSON, žádný text před ani po
```

---

### Sauto oslovení — příprava vlny

```
Role: jsi obchodní asistent pro nákup ojetých aut.
Úkol: připrav novou vlnu oslovení prodávajících na Sauto.
Omezení:
- NEJDŘÍV načti Sauto_Komunikace Sheet a vyluč všechna sauto_id se stavem ODESLANO
- U každého kandidáta ověř create_date přes Chrome JS (regex "create_date":"([^"]+)")
- Zařaď jen inzeráty STRIKTNĚ > 30 dní (hodnota 30 nestačí)
- Vycházej z existujícího HTML vzoru OSLOVENI_KLIK_YYYYMMDD_VLNA*.html
- Neuváděj stáří inzerátu bez ověřeného create_date
Výstup: HTML soubor s kartami + audit ID/create_date/dni
```

---

### Konverzní HTML nabídka auta

```
Role: jsi konverzní copywriter a frontend developer.
Úkol: vytvoř konverzní HTML stránku pro auto ID [X].
Omezení:
- Vycházej VÝHRADNĚ z Passat vzoru: nabidky_aut\20260523_auto1_11004535_VW_Passat_Variant\nabidka_VW_Passat_Variant_11004535_KONVERZE.html
- Měň jen: data auta, ID, ceny, rizika, aukcní údaje, fotky, počty
- Neměň: koncept, obsahové bloky, formuláře, CTA, kaskádu služeb
- Nikdy neuváděj viditelný název aukcní platformy (jen "evropská aukce")
- Před výstupem hledej zbytky vzoru: staré ID, Passat, KONVERZE v názvu
- Konec aukce NESMÍ se hádat — jen z aukcní stránky nebo od uživatele
Formát: jeden HTML soubor, název nabidka_Znacka_Model_ID_K.html
```

---

### Aukce — kompletní dokončení

```
Role: jsi technický projektový manažer.
Úkol: dokonči aukci AUK-XXX pro auto [X] — splň CELÝ kontrolní seznam sám.
Povinné kroky (všechny, bez výjimky):
1. Vyplnit AUCTION_CONFIG v index.html (všechna pole)
2. Ověřit photos[] = skutečný počet souborů v img\
3. Aktualizovat upload_aukce.bat na novou složku
4. Spustit upload
5. Firebase PATCH na /auctions/AUK-XXX.json přes Chrome JS fetch()
6. Ověřit live URL — countdown + název auta
7. Prezentovat soubory přes present_files
Žádné úkoly uživateli — vše dělám sám.
```

---

### Stress-test nápadu / plánu

```
Nepovzbuzuj mě. Zaútoč na tento plán:
[popis]
Hledej: slabé předpoklady, chybějící logiku, tržní rizika, důvody proč to selže.
Buď brutálně upřímný — ne podporující.
Max 10 odrážek, seřazené od největšího rizika.
```

---

### Pochopení nového tématu

```
Vysvětli [téma] prostým jazykem a konkrétní analogií.
Předpokládej: nemám žádné zkušenosti v tomto oboru.
Pokud použiješ žargon, zastav se a najdi jednodušší způsob.
Max 150 slov, pak se zeptej jestli chci detail.
```

---

### Lead z nabídky auta — zpracování

```
Role: jsi obchodní asistent, zpracuješ lead ze stránky.
Úkol: připrav koncept odpovědi pro leady od [jméno/email].
Postup:
1. Seskup duplicitní požadavky stejné osoby (email + telefon + ID auta)
2. Identifikuj tlačítko: specs/eq/docs/odemknutí
3. Připrav POUZE relevantní zákaznické podklady
4. Zapiš do Sheetu stav KONCEPT_PRIPRAVEN
5. Ukaž mi koncept — NEPOSÍLEJ bez mého schválení
Omezení: žádné lokální cesty, žádné interní kódy v příloze pro klienta
```

---

### OpenLane výběr aut — standardní tabulka

```
Role: jsi analytik ojetých aut pro nákup z aukce.
Úkol: vyber vhodná auta z aktuální OpenLane nabídky.
Povinný výstup: tabulka PŘESNĚ 16 sloupců v tomto pořadí:
1. ID aukce
2. Typ / model
3. Konec aukce (datum)
4. Zbývající čas
5. Aktuální bid (EUR)
6. Odhad vydražení (EUR)
7. CZ tržní cena (Kč) — z WebSearch sauto.cz
8. CZ cena −3% (Kč)
9. Průměrná doba prodeje (dny)
10. ROI/den (%)
11. Náklady min (Kč)
12. Náklady max (Kč)
13. Max. bid na 30k zisk (EUR)
14. Max. bid na 20k zisk (EUR)
15. Poznámka / riziko
16. Doporučení (KOUPIT / ZVÁŽIT / PŘESKOČIT)
Bez tohoto formátu výstup nevypisovat — doplnit chybějící data nebo označit N/A.
Kurz EUR/CZK: fetchnout z cnb.cz/denni_kurz.txt.
Tržní ceny: WebSearch na sauto.cz pro každý model.
```

---

### Stažení fotek z Chrome cache

```
Role: jsi technický asistent pro přípravu podkladů nového auta.
Úkol: stáhni fotky auta ID [X] z přihlášeného Chrome.
Postup:
1. Nkoušet nepřihlášený in-app browser — pokud nemá sdílenou session, přejít na krok 2
2. Číst Chrome cache: C:\Users\tomas\AppData\Local\Google\Chrome\User Data\Default\Cache\Cache_Data
3. Hledat URL tvaru: https://images.openlane.eu/carimgs/*/general/*.jpg
4. Vybrat nejnovější skupinu podle času otevření stránky a počtu fotek
5. Pokud je skupin více, vytvořit contact sheet pro vizuální ověření správného auta
6. Zkopírovat JPEG soubory → img\foto_01.jpg, img\foto_02.jpg, ...
7. Vytvořit nebo aktualizovat uuids.txt a STAHNI_FOTKY.ps1
8. Aktualizovat HTML galerii na skutečný počet fotek
9. Zavolat present_files na uuids.txt a STAHNI_FOTKY.ps1
Omezení: nikdy nepřepisovat existující fotky bez pokynu uživatele.
O spolupráci požádat jen tehdy, když je nutné otevřít Chrome nebo dodat přístup.
```

---

### Forenzní audit vozu — spuštění

```
Role: jsi forenzní analytik ojetých aut (produkt Batko Digital AI).
Úkol: proveď kompletní forenzní audit vozu.
Vstupy: VIN + [volitelně: odkaz na inzerát, fotky, inspekční zpráva, servisní kniha]
Postup — 4 fáze (viz docs\PROMPTY_FORENZNI_AUDIT_VOZU.md):
1. AUDIT-CORE — VIN + právní + historická + tržní vrstva, skóre 0-100, verdikt BUY/HOLD/REJECT
2. REPORT-PDF — zákaznický PDF text (bezpečné části: verdikt, skóre, plusy, rizika, další krok)
3. SALES-COPY — inzerát, landing page text, PPC copy (jen na pokyn)
4. LEAD-HANDLER — zpracování poptávky, draft odpovědi, zápis do LEADS_MASTER (čeká na schválení)
Omezení:
- Nesmí obsahovat interní zdroje, Sheet/Drive workflow, lokální cesty, pracovní poznámky
- Klientský výstup nesmí budit dojem fyzické inspekce — jde o vzdálený prescreen
- Ceny balíčků: Základ 1490 Kč (24h) / Express 2490 Kč (3h) / Premium 3490 Kč
- LEAD-HANDLER neodesílá bez explicitního schválení uživatele
Začni fází 1, pokud uživatel neřekne jinak.
```

---

## !! PRAVIDLO PRO DLOUHE CHATY A CENU PROVOZU !!

Pokud chat zacne byt dlouhy, pomaly, neprehledny nebo zbytecne drahy na dalsi praci, Codex/Claude
ma sam uzivatele upozornit a navrhnout predani do noveho chatu. Pred prechodem vytvorit kratky
souhrn v `docs\PREDAVACI_SOUHRNY\` s nazvem ve formatu `RRRRMMDD HHMM nazev` a zapsat aktualni
stav, dulezite soubory, endpointy/URL, otevrene ukoly, kriticka pravidla a incidenty.

Novy chat ma pokracovat z tohoto souhrnu, ne z cele dlouhe historie.

## !! POVINNE PRED KAZDYM UPLOADEM AUKCE (nauceno 2026-06-01) !!

1. `tail -5 index.html` — musi skoncit `</html>`. Pokud ne, soubor je uriznuty — NENAHRÁVAT.
2. Vsechny `document.getElementById()` v `initPage()` musi mit null-check pres `setEl()`.
3. Po zmene HTML modelu prohledat JS pro reference na odstranene elementy.
4. Bez teto kontroly zpusobi upload nefunkcni galerii a ztratu casu uzivatele.
TOTO PRAVIDLO PLATI I PRO CLAUDE, CODEX I JAKEHOKOLIV DALSIHO AGENTA.

## !! NIKDY NEPREPISOVAT UZ SDILENE VEREJNE URL (incident 2026-06-01) !!

Pred kazdym uploadem na GitHub Pages musi Claude/Codex zkontrolovat, jestli cilova verejna URL
uz mohla byt sdilena klientum, v inzerci, v e-mailu, ve WhatsAppu nebo v dokumentaci. Pokud ano,
nesmi se jeji obsah zmenit na jiny produkt, jinou nabidku nebo testovaci variantu bez vyslovneho
aktualniho pokynu uzivatele.

Nove produkty, testy, uzkoproduktove kopie a kampane se publikuji na novou HTML adresu nebo do nove
slozky. Stara stabilni URL smi zustat jen jako puvodni obsah, pripadne se meni az po jasnem pokynu.

Povinna kontrola pred i po uploadu:
- pred uploadem zapsat, ktere verejne URL se meni a ktere musi zustat beze zmeny,
- po uploadu overit stare i nove URL pres HTTP status a velikost/obsah,
- pokud se omylem prepsala stara URL, okamzite ji vratit z posledni spravne verze a znovu overit.

Toto pravidlo plati pro vsechny verejne HTML stranky, nejen pro aukce.

## !! POVINNA PATICKA, IDENTIFIKACE A DPH NA VEREJNYCH STRANKACH (incident 2026-06-01) !!

Kazda verejna HTML stranka, landing page, nabidka, objednavka, rychly produkt nebo testovaci kampan
musi pred uploadem obsahovat plnou zakaznickou paticku. Upload je zakazan, pokud chybi:

- `Ing. Jaroslav Batko-Linet | Batko Digital AI`
- `ICO: 14600153`
- `DIC: CZ5912280418`
- informace `Platce DPH`
- adresa `Liskovec 170, 273 51 Velke Pritocno`
- kontaktni e-mail `batko.digital.ai@gmail.com`
- osobni e-mail jen pokud je potreba `jaroslav.batko@gmail.com` (nepouzivat starou chybnou variantu `.gmail.cz`)
- telefon `+420 725 360 151`
- autoritativni zdroj profilu `assets/company_profile/company_profile_canonical.json`
- zakladni text o ochrane osobnich udaju a ucelu zpracovani poptavky
- jasne vymezeni, co sluzba je a neni, pokud jde o zakaznickou nabidku

Kazda viditelna cena sluzby musi rikat, zda je `vc. DPH` nebo `bez DPH`. Pokud uzivatel nerekne
jinak, zakaznicke ceny typu `790 Kc` se uvadeji jako `790 Kc vc. DPH`. Stejna informace musi byt
i v datech odesilanych do Sheetu (`selected_service`, `budget`, `lead_task`, `note`), aby bylo
zpetne jasne, co klient videl a co se ma vyridit.

## !! GOOGLE SHEET — POVINNE CIST PRIMO, NIKDY SE NEPTAT (nauceno 2026-06-05) !!

Google Sheet AUTO_LEADS_MASTER je dostupny primo pres MCP (Google Drive connector, server
11cd8c15-6583-4cca-a55d-c1893130a036). Claude/Codex ho MUSI cist primo — nikdy se neptat
uzivatele na obsah Sheetu.

**URL:** https://docs.google.com/spreadsheets/d/1Jqb_pYefrMh7-RP80ylSftfAFhyK8NPLyC951b_qhrE/edit

**Listy:**
- `List 1` — hlavni leady (nabidky aut, aukce, objednavky)
- `CarCheck_Objednavky` — objednavky CarCheck / predfiltr 790 Kc
- `Sauto_Komunikace` — evidence Sauto oslovavani prodejcu

**Pred kazdou vlnou Sauto osloveni POVINNE:**
1. Precist `Sauto_Komunikace` — sloupec `sauto_id`
2. Vyloucit vsechna ID ktera maji `stav_osloveni = ODESLANO`
3. Teprve pak generovat nebo odesilat zpravy

Pri praci se Sauto pouzivat prihlaseny stav v otevrenem prohlizeci. Aktualni prihlaseny ucet pro
Sauto je `batko.digital.ai@gmail.com`; nepouzivat anonymni/neprihlasene pokusy, pokud je tento
prihlaseny kontext dostupny.

Porouseni tohoto pravidla = zbytecne kredity a duplicitni osloveni. Pravidlo plati
pro Claude i Codex i jakehokoliv dalsiho agenta.

## Zdroj pravdy

Hlavni projektova slozka:

`C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1\`

Aktualni workflow pro nabidky aut je popsany hlavne v:

- `SOP_NABIDKA_AUTA.md`
- `POSTUP_NOVE_AUTO.md`
- `sablony\auto_data_VZOR.json`
- `generuj_nabidky.py`
- `upload_na_web.py`
- `nabidky_aut\`
- `docs\SOP_SAUTO_OSLOVENI.md` - Sauto osloveni prodavajicich, evidence ve Sheetu,
  deduplikace podle `sauto_id` / `conversation_key` a testovani ceny zpravy.
- `docs\SOP_OPENLANE_RYCHLE_ROI_VYHODNOCENI.md` - rychle vyhodnoceni OPENLANE aukce z URL,
  primarne podle denniho ROI, s povinnym transportem a technickym reportem.
- `docs\STUDIJNI_MATERIALY\` - slozka pro studijni/konkurencni materialy. Kazdy novy material
  se povinne pojmenovava ve formatu `RRRRMMDD HHMM nazev`, napr.
  `20260601 1825 Automato jak nenaletet pri koupi ojeteho auta.md`.

Jak zjistit datum vložení inzerátu na Sauto (pro uživatele i Claude):
- Otevřít inzerát na Sauto
- Stisknout Ctrl+U (zobrazit zdrojový kód stránky)
- Stisknout Ctrl+F a hledat: create_date
- Výsledek vypadá takto: "create_date":"2026-03-26T19:47:26"
- Datum před "T" je datum vložení inzerátu
- Claude získává create_date přes Chrome rozšíření (javascript fetch na detail stránce,
  regex "create_date":"([^"]+)") — toto je POVINNÝ postup před každou vlnou oslovení.
  Claude nesmí odhadovat stáří inzerátu z filtru Sauto — musí ověřit create_date.

Kriticka pojistka Sauto po incidentu 2026-06-01:
- Nikdy netvrdit prodavajicimu, ze inzerat je na Sauto "pres mesic", "dlouho", "stagnuje"
  nebo ze se "neprodava", pokud neni u konkretniho inzeratu overene `create_date` a spocitany
  skutecny pocet dni.
- Filtr Sauto `item_age_cb`, poradi vysledku ani dojem ze stranky nejsou dukaz stari inzeratu.
- Bez overeneho data pouzit neutralni formulaci: `narazil jsem na vas inzerat... u takoveho
  auta muze byt bezny inzerat nekdy pomaly`.

Povinny format Sauto klikaciho HTML a kontroly vlny:

!! NAUCENO 2026-06-16 — KRITICKE OPRAVY !!

!! KRITICKA CHYBA OPRAVENA 2026-06-16 — SAUTO DETAIL API STRUKTURA !!

Sauto detail API `https://www.sauto.cz/api/v1/items/{id}` vraci:
  `d.result.status` — SPRAVNE
  `d.data.result.status` — SPATNE, d.data neexistuje, vzdy vraci undefined = false-positive "mrtvy"

Kontrola zivosti inzeratu MUSI pouzivat `d.result && d.result.status === 'active'`.
Pouziti `d.data.result.status` zpusobile chybne oznaceni VSECH 20 ZIVYCH ID jako "mrtve"
a zbytecne prepracovani vlny na cizich ID. Tato chyba nesmi se opakovat.
Pred kazdou hromadnou kontrolou: vzdy nejdriv otestovat na 1 ID a vypsat `Object.keys(d)` pro ladeni struktury.

NAZEV SOUBORU: Vzdy `RRRRMMDD HHMM osloveni vlna XXX.html` (napr. `20260616 1545 osloveni vlna 010.html`).
NIKDY nepouzivat stary format `OSLOVENI_KLIK_YYYYMMDD_VLNA*.html` — matouci, nesystemove.

REPLY PANEL: Textarea a tlacitka `Zapsat odeslani do Sheetu` + `Zapsat odpoved do Sheetu`
MUSI BYT NATVRDO V HTML kazde karty. NIKDY je negenerovat jen pres JS `initReplyPanels()` —
JS muze tisnout chybu bez varovani a uzivatel panel neuvidi. Hardcode je jedina spolehliava cesta.

HROMADNE TLACITKO: `Zapsat vsechna odeslani do Sheetu` musi byt NAHORE (u progress baru)
I DOLE (za posledni kartou, pred </body>). Uzivatel po odeslani 20 zprav nechce scrollovat nahoru.

GENEROVANI HTML: Vzdy Python skript (garantuje UTF-8 a integritu). Nikdy nepouzivat Edit tool
na velky HTML soubor — muze soubor zkratit nebo zanechat siroky fragment.
Po kazdem zapisu overit: tail posledni radky musi skoncit `</html>`, grep na orphaned fragmenty.

!! KRITICKA POJISTKA — KOPIRUJ SYNTAX ERROR (incident 2026-06-16, ztracene hodiny uzivatele) !!
Edit tool pouzity na `<script>` sekci zdvojil klic. slovo: `async async function kopiruj`.
`async async` = JavaScript syntax error = CELY script blok nefunguje (ani switchTab, markSent atd.).
POVINNE OVERENI po kazdem generovani/oprave HTML vlny:
  1. grep "async async" soubor.html  → musi vratit 0 vyskytu (chyba = NENAHRÁVAT)
  2. grep -c "kopirujFallback" soubor.html  → musi byt 0
  3. Chrome konzole: (function(){try{return typeof kopiruj}catch(e){return e.message}})()  → "function"
  4. CDP timeout clipboard testu = normalni (ceka user gesture). Fyzicky klik uzivatele funguje vzdy.
NIKDY nepouzivat Edit tool na `<script>` sekci > 50 radku — vzdy Python skript.

- Klikaci HTML pro Sauto vlny musi vychazet z funkcniho vzoru
  `docs\OSLOVENI_KLIK_20260605_VLNA5_OPRAVENO.html` nebo posledni spravne vlny.
- Nesmí se vymyslet novy layout ani odstranit provozni prvky: karty inzeratu, zalozky
  `Zprava A (plna)` / `Zprava B (zkracena)`, kopirovani A/B, checkbox `Odeslano`,
  odpovedni panel (hardcoded!), hromadne zapsani do Sheetu nahore+dole, Apps Script funkce
  `sauto_summary`, `ulozOdeslani`, `ulozOdpoved`, `ulozVsechnaOdeslani`.
- Kazda karta musi viditelne obsahovat pocet dni v inzerci a datum `create_date`.
- Pred generovanim se vzdy cte zivy `Sauto_Komunikace` / `sauto_summary` a vylouci se
  vsechna drive zpracovana `sauto_id`.
- U kazdeho noveho kandidata se overi detailni `create_date` z Sauto detail API nebo zdroje
  stranky regexem `"create_date":"([^"]+)"`, spocita se skutecny pocet dni a do vlny smi
  jen inzeraty striktne `> 30` dni. Hodnota `30` nestaci.
- Ke kazde vlne ulozit audit vybranych ID, create_date a dni.
- Po odeslani vlny znovu nacist `sauto_summary`, porovnat vsechna ID z HTML/auditu proti
  `sent_ids` a vypsat chybejici ID. Pokud nic nechybi, potvrdit pocet odeslanych.

Interni rozhodovaci nastroje:

- `20260526 ut auto interni_roi_nastroj_11004535.html` - lokalni HTML kalkulator pro VW Passat Variant
  #11004535; slouzi pro rychle testovani vstupu, vystupu, trzniho pasma CR, maximalniho bezpecneho bidu,
  zisku a ROI za den. Soubor je internni analyticky nastroj, ne verejna konverzni nabidka.

Verejny trychtyr sluzeb a Drive upload priloh:

- `verejny_trychtyr_auto_sluzby_11004535.html` - lokalni verejna zakaznicka stranka pro ukazkove auto
  a poptavku sluzeb. Nepouziva plny nazev aukcni platformy, jen `OL` a referencni ID.
- `docs\PROVOZNI_MANUAL_VEREJNY_TRYCHTYR_A_DRIVE.md` - provozni navod: kde je stranka, kam se
  ukladaji prilohy, jak funguje Google Sheet zapis, Drive slozka a jak postupovat pri novem leadu.
- Publikovana GitHub Pages URL:
  `https://batkodigitalai.github.io/batko-digital-ai/nabidky/20260526_auto1_11004535_VW_Passat_Sluzby/verejny_trychtyr_auto_sluzby_11004535.html`.
- Publikovatelna kopie s webovymi cestami k fotkam je ve slozce
  `nabidky_aut\20260526_auto1_11004535_VW_Passat_Sluzby\`.
- Pro upload jedne slozky na GitHub Pages lze pouzit
  `scripts\upload_single_folder_to_github.js`; skript cte existujici `.github_config.json`,
  token nevypisuje a nahraje jen zadanou slozku.
- Univerzalni landing page pro kontrolu auta pred koupi:
  `nabidky_aut\20260527_auto1_univerzalni_kontrola_auta_pred_koupi\kontrola_auta_pred_koupi.html`.
  Verejna URL:
  `https://batkodigitalai.github.io/batko-digital-ai/nabidky/20260527_auto1_univerzalni_kontrola_auta_pred_koupi/kontrola_auta_pred_koupi.html`.
  Stranka umi parametry `refUrl`, `refImg`, `refVehicle`, `utm_source`, `utm_medium`,
  `utm_campaign`, `utm_content`; predvyplni auto, obrazek, formular a zapise zdroj leadu do Sheet.
  Pozicovani je cestne: nejde o fyzickou prohlidku, ale o prvni vzdaleny prescreen pred cestou,
  vyjednavanim nebo objednanim mechanika.
  Platby jsou zatim rucni po potvrzeni: klient odeslanim formulare nic neplati, nejdrive se potvrdi
  rozsah a cena, potom se posilaji platebni udaje nebo QR platba; prace zacina az po zaplaceni.
  Stranka muze obsahovat verejnou ukazku vystupu, aby klient videl, co si objednava. Ukazka smi
  obsahovat jen zakaznicky bezpecne casti: verdikt, skore, hlavni plusy, rizika, co doplnit a
  dalsi krok. Nesmí obsahovat interni zdroje, Sheet/Drive workflow, interni kody, lokalni cesty,
  pracovni poznamky, marze, interní rozhodovaci postupy ani nic, co by klientovi davalo mylny
  pocit finalni fyzicke kontroly.
  Zakaznicke potvrzeni po odeslani nesmi obsahovat technicke formulace typu "lokalni stranka",
  "zapis nejde potvrdit" nebo "e-mail se neotevira"; v pripade nejednoznacne odpovedi formulare
  se klientovi ukazuje jen klidne `Poptavka byla odeslana ke zpracovani.`
- Drive slozka pro prilohy: `AUTO_LEADS_PODKLADY`,
  URL `https://drive.google.com/drive/folders/1qYPccoGlbf1UhC_D8wLnhfoq9dT-xExt`.
- Apps Script backend: `github_repo\apps_script\lead_webhook.gs`, endpoint v6 podporuje Drive prilohy.

Pred zmenami workflow nebo generatoru vzdy nejdrive precist relevantni SOP a existujici priklady v `nabidky_aut`.
Pokud je mezi soubory rozpor, plati novejsi `SOP_NABIDKA_AUTA.md` a konkretni pokyn uzivatele v aktualni konverzaci.

Zavazny aktualni vizualni a strukturalni vzor konverzni stranky je posledni dobra stranka Passatu:

`nabidky_aut\20260523_auto1_11004535_VW_Passat_Variant\nabidka_VW_Passat_Variant_11004535_KONVERZE.html`

Tento soubor slouzi jako vzhledovy a funkcni template. Pri novych autech se nesmi vymyslet novy layout,
nova struktura, nove formulare ani vlastni marketingovy koncept. Meni se pouze konkretni data auta,
fotky, texty, ceny, rizika, aukcni udaje a identifikace zdroje.

Pro publikovatelny denni `_K.html` plati jeste prisnejsi pravidlo: finalni soubor musi vzniknout
z kopie Passat HTML vzoru a nahrazenim povolenych konkretni hodnot. Obecny vystup `generuj_nabidky.py`
muze slouzit jako pomocny zdroj dat nebo pro zakazkovou sadu stranek, ale nesmi byt automaticky povazovan
za finalni konverzni stranku, pokud neprosel porovnanim struktury proti Passat vzoru.

Urgency nadpis v cervenem bloku nesmi mit natvrdo napsane cislo dni. Musi se dynamicky pocitat
ze skutecneho konce aukce (`auctionEnd`) a pouzit spravny cesky tvar `den/dny/dni`, pripadne
`mene nez 24 hodin` pri poslednim dni.

Konec aukce je kriticky obchodni udaj a nesmi se nikdy hadat. Povolenym zdrojem je pouze:
explicitni konec aukce z aukcni stranky, screenshot se zbyvajicim casem a znamym casem porizeni,
nebo uzivatelem potvrzeny konkretni cas. Pokud je konec aukce nejisty, stranka se nesmi publikovat
a v HTML se nesmi nastavovat vymysleny `auctionEnd`.

U identifikace zpracovatele na konci stranky musi byt kratke ujisteni o ochrane osobnich udaju:
formulare se pouziji jen pro vyrizeni poptavky/nabidky a komunikaci, udaje se zpracovavaji duverne
v souladu s platnymi predpisy a neprodavaji ani nepredavaji tretim osobam bez pravniho duvodu
nebo souhlasu klienta.

Povinna paticka, identifikace zpracovatele a upozorneni na ochranu osobnich udaju musi byt jednotne
podle Passat vzoru. Pokud se publikuje jen denni `_K.html`, musi mit presne tento pravni/footer blok.
Pokud se publikuji i vedlejsi stranky (analyza, FO, ICO, agent, mentoring, premium, hodnoceni,
objednavka), musi mit stejne jednotnou paticku, stejne povinne udaje a stejne upozorneni na ochranu
osobnich udaju. Vedlejsi stranka bez sjednocene paticky/privacy bloku se nesmi publikovat.

## Kriticke pravidlo po incidentu 2026-05-24

Pri prevodu Passat vzoru na nove auto je zakazane tvrdit, ze vystup odpovida vzoru, dokud neni
provedena kontrola proti samotnemu HTML vzoru. AI nesmi uzivat formulace typu "je to 1:1",
"presne podle vzoru" nebo "dodrzeno", pokud neprobehla technicka kontrola struktury a zakazanych
zbytku.

Pro konverzni HTML plati:

- vychozi soubor je vzdy Passat vzor, ne predchozi spatne vygenerovana verze noveho auta,
- zachovat stejne poradi a typy sekci jako Passat,
- zachovat i koncept a obsahove bloky pod fotografiemi podle Passat vzoru; nesmi se zkratit,
  preskladat ani nahradit obecnym generatorovym konceptem,
- nemenit obchodni system, formulare, CTA, kaskadu sluzeb ani obecne sablonove texty,
- menit jen konkretni fakta daneho auta: nazev, technicke parametry, ceny, aukcni udaje, rizika,
  ID, URL, pocet a poradi fotek,
- nevkladat nove sekce, napriklad vlastni "ekonomika obchodu podle postupu", pokud nejsou ve vzoru,
- nikdy nevkladat viditelny nazev aukcni platformy do verejneho HTML; pouzit obecne oznaceni
  jako "evropska aukce", "evropsky aukcni zdroj", "nemecka aukce" nebo
  "registrovany evropsky aukcni zdroj",
- cislo aukce / reference se musi vzdy zachovat pro internni identifikaci, napr. `Ref.: #11005973`,
- paticka, identifikace zpracovatele a privacy text musi byt stejneho konceptu jako Passat vzor
  na vsech publikovanych HTML stranach,
- pokud je fakt nejisty, napsat neutralni overovaci formulaci ve stejne strukture, ne vymyslet detail,
- po vygenerovani povinne hledat zbytky vzoru a zakazane vyrazy: stare ID, stary model, Passat,
  KONVERZE v novem nazvu, nazev aukcni platformy ve viditelnem textu, rozbita diakritika,
  anglicke popisky, chybejici nebo odlisny privacy/footer blok.

Pokud se pri kontrole najde chyba, nesmi se publikovat. Nejdrive se musi HTML znovu postavit z Passat
vzoru a znovu zkontrolovat.

Po namitce uzivatele, po zjisteni chyby nebo pri nejistote o kritickem udaji se nesmi pokracovat
v opravach, generovani ani uploadu bez vyslovneho aktualniho pokynu uzivatele.

## Rychly workflow pro fotky z prihlaseneho Chrome

Kdyz uzivatel doda URL auta a ma auto otevrene v prihlasenem Chrome, nejrychlejsi vychozi postup je:

1. Nezkouset zbytecne neprihlaseny in-app browser, pokud nema sdilenou session.
2. Cist Chrome cache ve slozce `C:\Users\tomas\AppData\Local\Google\Chrome\User Data\Default\Cache\Cache_Data`.
3. Hledat URL tvaru `https://images.openlane.eu/carimgs/*/general/*.jpg`.
4. Vybrat nejnovejsi skupinu podle casu otevreni stranky, poctu fotek a vizualni shody s autem.
5. Zkopirovat skutecne JPEG soubory z cache do `img\foto_01.jpg`, `img\foto_02.jpg`, ...
6. Vytvorit nebo aktualizovat `uuids.txt` a `STAHNI_FOTKY.ps1`.
7. Udelat rychly contact sheet pro kontrolu poradi a shody auta, pokud je skupin vice.
8. Do HTML vlozit jen lokalni fotky a galerii nastavit na skutecny pocet fotek.

## Aktualni obchodni logika nabidek

Standardni denni prace neni vyrabet vsech 10 HTML stranek pro kazde auto.

Cil standardniho rychleho vystupu je:

- rychle vybrat vhodne auto
- stahnout lokalni fotky
- vytvorit jednu silnou konverzni HTML stranku
- publikovat ji jako test poptavky / zajmu
- minimalizovat cas a cenu vystupu

Kompletni sada dalsich HTML stranek se dodelava az ve chvili, kdy se z konverzni stranky objevi konkretni zajemce nebo konkretni pozadavek klienta.

Navazujici zakazkove stranky mohou byt podle situace:

- hlavni detailni nabidka
- analyza auta
- varianta pro FO
- varianta pro ICO
- agenturni nakup
- mentoring
- premium full
- hodnoceni
- objednavka

Aktualni nazev standardni konverzni stranky je:

`nabidka_Znacka_Model_ID_K.html`

Priklad:

`nabidka_Skoda_Octavia_RS_10997205_K.html`

Starsi nazev `*_KONVERZE.html` uz nepouzivat pro nove vystupy, pokud ho uzivatel vyslovne nevyzada.
Pokud existuje historicky soubor s koncovkou `KONVERZE`, brat ho jen jako obsahovy/vzhledovy vzor, ne jako pravidlo pro novy nazev.

## Role Codexu

Codex je vhodny hlavne pro:

- upravy a kontrolu Python skriptu
- generovani a validaci HTML vystupu
- kontrolu struktury slozek a dat
- opravy workflow kolem `data.json`, fotek, generatoru a uploadu
- lokalni technickou diagnostiku
- setrne doplneni dokumentace, kdyz usnadni opakovani procesu

Claude muze dal zustat silny prostor pro:

- obchodni a marketingove texty
- argumentaci nabidek
- analyzy trhu a sluzeb
- dlouhe obsahove koncepty

Spolecny zdroj pravdy zustava tato slozka `auto1`; nema vznikat oddeleny paralelni "GPT svet" se stejnymi daty.

## Pravidla prace

1. Nemenit historickou strukturu bez vyslovneho zadani.
2. Nepresouvat ani nemazat soubory bez predchoziho planu a potvrzeni.
3. Neprepisovat rucne generovane nebo uz nahrane vystupy, pokud neni jasne, ze jde o regeneraci.
4. Nikdy neprepisovat existujici fotky auta v `img`, pokud uzivatel nerekne jinak.
5. HTML nabidky generovat pres `generuj_nabidky.py`, ne rucnim skladanim celeho HTML.
6. Pri praci s novym autem drzet aktualni postup ze `SOP_NABIDKA_AUTA.md`.
7. Citlive konfigurace jako `.github_config.json` necist ani neupravovat, pokud to neni nezbytne pro konkretni diagnostiku.
8. Pred uploadem na web zkontrolovat, ze existuje `data.json`, vygenerovane HTML a lokalni fotky v `img`.
9. Konverzni HTML pro publikaci musi byt cesky a s ceskou diakritikou. Nepouzivat anglicke popisky typu `LOCK`, `Lead`, `Submit`, `Source`, pokud existuje cesky ekvivalent.
10. Pri tvorbe konverzni stranky zachovat strukturu posledniho dobreho vzoru do detailu: price hero, countdown/urgency blok, galerie, duvody vyberu, zamcene sekce, audit CTA, lead formular, kaskada sluzeb, identifikace zpracovatele a funkcni JavaScript.
11. AI se nesmi odchylit od presneho vzoru kvuli kreativite. Cilem je konzistence vystupu mezi auty, ne originalita kazde stranky.
12. Fotky auta stahnout samostatne jakoukoli funkcni metodou: z otevreneho Chrome, z Chrome cache, z OPENLANE image URL, pres `STAHNI_FOTKY.ps1`, pres skript nebo rucne ulozene URL. O spolupraci uzivatele pozadat jen tehdy, kdyz je nutne otevrit Chrome, prihlasit se do OPENLANE, obnovit stranku nebo dodat pristup k fotkam.
13. Pri extrakci fotek vzdy vytvorit nebo aktualizovat `uuids.txt` a `STAHNI_FOTKY.ps1`. Fotky ulozit do `img\foto_01.jpg`, `img\foto_02.jpg`, ... ve stejnem poradi, v jakem jsou v OPENLANE galerii nebo v extrahovanem seznamu. Po stazeni aktualizovat HTML galerii na skutecny pocet fotek.
14. Verejne HTML nesmi viditelne uvadet nazev aukcni platformy. Verejny text ma pouzivat pouze obecne oznaceni aukce; cislo aukce/reference musi zustat zachovane.
15. Upload je zakazan, pokud neni jisty konec aukce, pokud `_K.html` nevychazi ze skutecneho Passat vzoru, nebo pokud nebyla provedena kontrola struktury a zakazanych zbytku.
16. Upload je zakazan, pokud kterakoli publikovana HTML stranka nema jednotnou paticku,
    identifikaci zpracovatele a upozorneni na ochranu osobnich udaju podle Passat vzoru.
17. Vedlejsi HTML stranky z generatoru nejsou automaticky publikovatelne. Pred publikaci se musi
    sjednotit jejich footer/privacy blok a zkontrolovat, ze neobsahuji viditelny nazev aukcni platformy.
18. Upload je zakazan, pokud HTML galerie obsahuje odkazy na neexistujici lokalni fotky. Pocet
    hlavich fotek, pocet nahledu a pocitadlo galerie musi presne odpovidat poctu souboru v `img`.
19. Kazdy lead z konverzni HTML musi v Google tabulce i v telefonni zprave jasne rikat, ktere
    tlacitko ho odeslalo a co je navazujici ukol. U odemykani musi `formType`, `source` nebo `note`
    obsahovat konkretni text tlacitka, sekci a ukol; obecne kody typu `F-Odemceni / eq` nestaci.
20. Odemykaci modal musi jit pouzit opakovane. Pri kazdem otevreni se musi znovu zobrazit formular,
    skryt stav uspechu a nastavit aktualni cil odemceni, aby druhe tlacitko neselhalo po prvnim
    uspesnem odeslani.

## Typicky postup pro existujici auto

1. Najit slozku auta v `nabidky_aut\`.
2. Zjistit, jestli jde o rychly konverzni vystup, nebo zakazkovou kompletaci.
3. Pokud existuje `data.json`, precist ho jako zdroj opakovatelne regenerace.
4. Zkontrolovat, zda existuje `img\` a fotky.
5. Spustit nebo upravit generator jen pokud je to potreba.
6. Po regeneraci zkontrolovat cilove HTML soubory.
7. Upload na GitHub Pages delat pres existujici upload batch nebo `upload_na_web.py`, podle situace.

## Typicky postup pro nove auto

1. Vychazet ze `SOP_NABIDKA_AUTA.md`.
2. Vytvorit novou slozku v `nabidky_aut\YYYYMMDD_auto1_ID_Znacka_Model\`.
3. Respektovat rucni nebo samostatny krok stazeni fotek.
4. Pro standardni denni praci staci jedna konverzni HTML stranka s koncovkou `_K.html`.
5. `data.json` a kompletni sada stranek se pripravuji hlavne pro opakovatelnou regeneraci nebo zakazkovou kompletaci po projevenem zajmu.
6. Pred uploadem udelat rychlou kontrolu vystupu.
7. Pred uploadem zkontrolovat, ze finalni HTML neobsahuje zbytky vzoroveho auta, napriklad stare ID, stary model, `KONVERZE` v nazvu noveho souboru, rozbitou diakritiku nebo anglicke viditelne popisky.

## Poznamky ke kodovani

Nektere starsi markdown vystupy se mohou v terminalu zobrazovat s rozbitou diakritikou. Pri editaci dokumentace postupovat opatrne a nemenit kodovani souboru zbytecne.

Nove technicke soubory pro Codex psat radeji ASCII, pokud neni dobry duvod pouzit cestinu s diakritikou.

## Interni ROI nastroj — rychle vyplneni pres JSON

Postup je v `SOP_ROI_NASTROJ.md`. Kratke shrnutí pro Codex:

Sablona: `interni_roi_nastroj_TEMPLATE.html` (ma JSON import panel nahore).
Vzor vyplneneho: `interni_roi_nastroj_11008921_Skoda_Octavia.html`.

Uzivatel da do chatu: *.docx (OPENLANE listing) + *.md (inspekcni zprava) + OPRAVY Kc.
Claude si soubory precte sam. Nikdy nezada data rucne — cteme vzdy ze souboru.

Claude provede automaticky:
- cte docx + md
- fetch kurzu EUR/CZK z CNB (cnb.cz/denni_kurz.txt)
- fetch trznich cen sauto.cz pres WebSearch
- dopocet feeCorrection = OL_KČ − (EUR × kurz)
- vypise POUZE JSON blok (zadne dalsi komentare)

Uzivatel: vlozi JSON do TEMPLATE.html → klikne Nacist → hotovo.
Persistence: Ctrl+S v prohlizeci NEBO Claude bake soubor na pozadani.

## Aukcni system — architektura a pravidla

Slozka: `aukce_system\`

Klicove soubory:
- `aukce_admin.html` — lokalní admin panel (spousti se z file:///, NENAHRÁVAT na web)
- `aukce_TEMPLATE.html` — sablona pro novou verejnou aukcni stranku
- `20260529_AUK-TEST-001_VW_Passat_2023\index.html` — testovaci verejná stránka (live na GitHub Pages)

Firebase projekt: `batko-aukce`
DB URL: `https://batko-aukce-default-rtdb.europe-west1.firebasedatabase.app`
Sablona verejne URL: `https://batkodigitalai.github.io/batko-digital-ai/nabidky/SLOZKA/index.html`

### Architektonická pravidla

1. Admin panel pouziva Firebase REST API pres fetch() — NIKDY Firebase JavaScript SDK.
   Duvod: SDK WebSocket selha z file:/// a zpusobi DEMO rezim (localStorage).
   REST_BASE je hardcoded v aukce_admin.html; meni se jen pri zmente projektu.

2. endTime v AUCTION_CONFIG (index.html) je POUZE fallback. Firebase endTime ma VZDY prednost
   a VZDY prepise lokalni hodnotu. Podminku `> Date.now()` NEPOUZIVAT pri nacitani Firebase endTime
   — zahazovala by spravny cas kdyz je aukce skoro u konce nebo uz skoncila.

3. initExtras() a vsechny funkce pristupujici k DOM elementum musi mit null-checky nebo try/catch.
   Duvod: nektery element nemusi existovat v dane sablone. Uncaught TypeError zastavi cely skript
   vcetne setInterval pro countdown.

4. renderBids (admin panel) musi pouzivat Object.entries(a.bids).map(([k,v])=>({...v,_key:k}))
   misto Object.values — jinak bidy nemaji Firebase klic a tlacitko mazani nefunguje.

5. Tlacitko mazani prihozu (🗑) je v poslednim sloupci tabulky v admin panelu — scrollovat doprava.

2. Verejná aukcní stranka (index.html) pouziva REST API polling kazde 4s pro nacitani bidu.
   Pattern: fetch(`${REST_BASE}/auctions/${ID}/bids.json?_=${Date.now()}`)
   Duvod: Firebase SDK .on('value') listener selhal na GitHub Pages (cached IndexedDB, nefunkcni WS).

3. Bidy odesilaji POUZE verejne formulare na index.html → Firebase REST POST.
   Admin panel bidy nepridava — pouze ctete, spravuje stav, exportuje CSV.

4. DEMO rezim (localStorage) se aktivuje automaticky kdyz Firebase REST neni dostupny.
   Poznat: zlute upozorneni "DEMO REZIM" v hlavicce Firebase panelu.

5. Firebase bezpecnostni pravidla jsou zatim `.read: true, .write: true`.
   Deadline pro produkci: 28.6.2026.

### Postup pri vytvareni nové aukce

Provozni manual: `aukce_system\PROVOZNI_MANUAL_AUKCE.md`

Zkracene kroky:
1. Otevrit `aukce_admin.html` v prohlizeci (file:///)
2. Prihlasit se heslem
3. Vyplnit formular Nová aukce — povinne: ID, konec aukce (NESMÍ se hádat!), vyvolávací cena
4. Kliknout Vytvořit / Uložit aukci → ulozi do Firebase
5. Duplikovat slozku TEMPLATE do `aukce_system\YYYYMMDD_ID_Znacka_Model\`
6. V index.html nastavit AUCTION_CONFIG.auctionId = nové ID
7. Nahrát na GitHub Pages pres upload skript
8. Otevrit verejnou URL — mela by ukazovat vyvolavaci cenu a odpocet

Pevne defaulty (menit jen na pokyn): registrace 7500, priprava 8000,
servis 12000, rez.reklamace 25000, jina rez. 10000, cilovy zisk 30000,
vynos/den 0.50%, dny 20/30/60.

Cilovy zisk = pseudonaklad: max_bid = prodejni_cena_netto − naklady − cilovy_zisk.
Ovlivnuje safeBid, verdikt (KOUPIT/PODMÍNEČNĚ/NEKOUPIT) a barevnost tabulek.
Skutecne zisky v tabulce se jeho zmenou nemeni.

## Lead approval gate

Pri jakemkoli leadu z nabidky auta plati povinny automatizovany postup:

1. Seskupit duplicitni pozadavky stejne osoby podle emailu, telefonu a ID auta.
2. Rozpoznat puvod tlacitka: `specs` = technicke podrobnosti/stav, `eq` = kompletni vybava,
   `docs` = dokumentace/historie.
3. Pripravit jen relevantni zakaznicke podklady; neposilat pet odpovedi na pet duplicitnich kliknuti.
4. Vytvorit koncept odpovedi a zapsat do Sheet stav `KONCEPT_PRIPRAVEN`.
5. Zapsat do Sheet `CEKA_NA_SCHVALENI` a uzivateli jasne ukazat, co je pripravene.
6. Odeslat az po vyslovnem aktualnim pokynu uzivatele. Po odeslani zapsat `ODESLANO`.

Zakaznicke prilohy se neposilaji jako HTML soubory, pokud by se v Gmailu mohly otevrit jako zdrojovy
kod. Pro klienta se pouziva PDF nebo verejny odkaz. PDF nesmi obsahovat lokalni cesty typu
`C:\Users`, `file:///`, interni kody `specs/eq`, ani interni zdroj leadu.

Kazdy krok prace s leadem se zapisuje do Google Sheet: `stav_zpracovani`, `schvaleni`, `draft_id`,
`podklady`, `odeslano`, plus konkretni tlacitko, sekce a ukol.

Pro verejny trychtyr `verejny_trychtyr_auto_sluzby_11004535.html` plati navic:

- formular muze prijimat az 5 mensich priloh dohromady cca do 8 MB,
- prilohy se ukladaji do Google Drive slozky `AUTO_LEADS_PODKLADY`,
- do Sheet sloupce `podklady` se zapisuje odkaz na konkretni Drive podslozku a soubory,
- viditelny zakaznicky text nesmi rikat technicke interni detaily typu "soubory se ulozi do
  Google Drive a do tabulky se zapise odkaz",
- po zmene Apps Scriptu je potreba `clasp push` a aktualizace existujiciho deploymentu,
- detailni postup je v `docs\PROVOZNI_MANUAL_VEREJNY_TRYCHTYR_A_DRIVE.md`.

---

## Forenzni rozhodovaci audit vozu

4 servisni prompty jsou v `docs\PROMPTY_FORENZNI_AUDIT_VOZU.md`:
- AUDIT-CORE: provedeni auditu (VIN + pravni + historicka + trzni vrstva, skore 0-100, BUY/HOLD/REJECT)
- REPORT-PDF: prevod auditu na zakaznicky PDF text
- SALES-COPY: generovani inzeratu, landing page textu, PPC
- LEAD-HANDLER: zpracovani poptavky, draft odpovedi, zapis do LEADS_MASTER (ceka na schvaleni)

Balicky: Zaklad 1490 Kc (24h) / Express 2490 Kc (3h) / Premium 3490 Kc.
Neni fyzicka inspekce — prvni rozhodovaci vrstva pred cesti za autem.

---

## POVINNY KONTROLNI SEZNAM pro dokonceni aukce

Claude/Codex musi splnit VSE sam — zadne ukoly uzivatel. Po kazde aukci zkontrolovat:

0. KONTROLA SOUBORU pred uploadem — POVINNE (2026-06-01 lesson):
   a) `tail -5 index.html` musi skoncit `</html>` — nikdy uprostred kodu.
   b) Vsechny `document.getElementById()` v `initPage()` musi mit null-check pres helper `setEl()`.
   c) Po kazde zmene HTML modelu prohledat JS pro reference na odstranene elementy.
   BEZ TETO KONTROLY NENAHRÁVAT — zpusobuje nefunkcni galerii a ztratu casu uzivatele.
1. AUCTION_CONFIG v index.html — vyplnit: auctionId, make, model, year, km, color, engine,
   transmission, startPrice, minIncrement, endTime (NIKDY hadat — z aukcni stranky nebo potvrdit
   uzivatel), auctionRef, rizika (max 4), specifikace, photos[].
2. photos[] — presne odpovidat skutecnemu poctu souboru v img\; zadne chybejici nebo navic.
3. upload_aukce.bat — aktualizovat cestu na novou slozku pred kazdym uplodem.
4. Spustit upload — dvojklik na upload_aukce.bat nebo GitHub API.

!! KRITICKE PRAVIDLO UPLOADU (nauceno 2026-06-16, incident AUK-010) !!
NIKDY nepouzivat chunked JS upload pres Chrome MCP pro soubory.
NIKDY nespoustet GitHub API ze sandboxu — vraci 403 Forbidden (proxy blokuje).
VZDY pripravit Python skripty na PC uzivatele.

Poloautomat — jedina spravna cesta v Codexu (bez Chrome MCP):
  a) Codex pripravi HTML + 3 skripty:
       upload_aukce.bat       → nahrani HTML + fotky na GitHub
       upload_aukce_docs.py   → nahrani PDFs na GitHub
       firebase_patch.py      → PATCH zaznamu aukce do Firebase
  b) Uzivatel spusti upload_aukce.bat (dvojklik)
  c) Uzivatel spusti upload_aukce_docs.bat (dvojklik)
  d) Uzivatel spusti firebase_patch.py (python firebase_patch.py nebo bat obal)
  e) Codex overi live URL pres fetch nebo vypise URL k rucni kontrole

Proc Python skript i pro Firebase:
  - Codex nema Chrome MCP → nemuzе volat fetch() v prohlizeci
  - Python na PC uzivatele dosahne Firebase REST API bez proxy
  - firebase_patch.py = jednoduchy urllib.request PATCH na /auctions/AUK-XXX.json

Sablona firebase_patch.py:
  import json, urllib.request
  TOKEN_NOT_NEEDED = True  # Firebase REST nevyzaduje token pro public DB
  REST_BASE = "https://batko-aukce-default-rtdb.europe-west1.firebasedatabase.app"
  AUCTION_ID = "AUK-XXX"
  DATA = { "status":"active", "endTime":"...", "startPrice":..., ... }
  req = urllib.request.Request(f"{REST_BASE}/auctions/{AUCTION_ID}.json",
    data=json.dumps(DATA).encode(), method="PATCH")
  req.add_header("Content-Type","application/json")
  with urllib.request.urlopen(req) as r: print(r.status, r.read()[:100])

Duvody:
  - Sandbox/bash → GitHub 403 — NEFUNGUJE
  - Chrome chunked JS upload → 10x drazsi, 10x pomalejsi — ZAKAZ
  - Python na PC → sekundy, spolehlivost 100%

Overeni po uploadu (povinne):
  - fetch PDF → HTTP 200 + magic bajty %PDF-
  - fetch index.html → titulek OK, countdown bezi, pocet dokumentu OK
  - Firebase GET → status:active, endTime spravny

5. Firebase PATCH — vytvorit zaznam aukce pres REST API:
   PATCH https://batko-aukce-default-rtdb.europe-west1.firebasedatabase.app/auctions/AUK-XXX.json
   Povinne pole: make, model, year, km, startPrice, minIncrement, endTime (ISO 8601),
   status:"active", createdAt, ref, sheetUrl.
   Sandbox ma proxy — pouzit mcp__Claude_in_Chrome__javascript_tool s fetch() PATCH.
6. Overit live URL — nactit stranku, zkontrolovat ze countdown odpovida Firebase endTime
   a ze nazev auta je spravny.
7. Prezentovat soubory — volat present_files na index.html a upload_aukce.bat.

## Sauto -> Diagnóza neprodaného auta -> Stripe trychtýř (funkční stav 2026-06-17)

Funkční veřejná aplikace:
`https://batkodigitalai-bat-90-labcar-sale-diagnosis-streamlitapp-3hw8bj.streamlit.app/`

Stripe Payment Link:
`https://buy.stripe.com/9B6cN61bIcyH7l95sv3VC03`

Aktuální interní HTML vlna:
`C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1\docs\20260617 1048 osloveni vlna 012.html`

Provozní pravidla:
1. Nejprve otevřít původní Sauto inzerát a ověřit, že stále existuje, cena/nájezd sedí a nejde o nevhodný kontakt.
2. Kliknout v HTML kartě na `Diagnóza auta` a ověřit, že Streamlit načetl `model`, `price`, `km`, `days`, `sauto_id`.
3. První zpráva prodávajícímu nesmí tlačit rovnou Stripe. Cíl první zprávy je získat reakci/souhlas: „Můžu vám poslat krátký nezávazný pohled?“
4. Po kladné reakci poslat odkaz na veřejnou diagnostiku konkrétního auta.
5. Prodávající ve Streamlitu doplní jen neznámé odpovědi, zadá jméno, e-mail, telefon a souhlas. Známá data auta se znovu neptají.
6. Bezplatný předverdikt je lead magnet. Plná diagnóza stojí 199 Kč včetně DPH.
7. Jeden Stripe Payment Link platí pro všechny inzeráty. Appka k němu přidává `client_reference_id=[lead_id]`, `prefilled_email`, `utm_source`, `utm_content`, takže není potřeba ručně vyrábět Stripe link pro každé auto.
8. Po zaplacení dohledat platbu ve Stripe podle e-mailu a `client_reference_id`; výsledek poslat na e-mail / navázat osobně.
9. Navazující nabídka po předverdiktu nebo platbě: přepis inzerátu 790 Kč včetně DPH, cenové srovnání a taktika 1 490 Kč včetně DPH, kompletní prodejní balíček 2 490 Kč včetně DPH.
10. Po odeslání oslovení v HTML zaškrtnout `Odesláno`; na konci kliknout `Zapsat všechna odeslání do Sheetu`, aby se stejný `sauto_id` neoslovoval znovu.

Povinné kontroly před tvrzením „hotovo“:
- Anonymní Chrome/inkognito otevře veřejnou Streamlit URL bez loginu.
- Odkaz s parametry auta zobrazí správný model, cenu, nájezd a dny v inzerci.
- Stripe checkout ukáže produkt `Plná diagnóza neprodaného auta` za 199 Kč a URL obsahuje `client_reference_id`.
- HTML vlna nesmí obsahovat `localhost:8501`; `DIAGNOSIS_APP_URL` musí mířit na veřejnou Streamlit URL.

## Cenové srovnání podobných aut v Sauto vlně (funkční od 2026-06-17)

Skript:
`C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1\scripts\sauto_price_comps_for_wave.py`

Aktuální ověřený příkaz pro vlnu 012:
`python "C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1\scripts\sauto_price_comps_for_wave.py" "C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1\docs\20260617 1048 osloveni vlna 012.html" --limit 20`

Co to dělá:
- vezme Sauto ID z HTML karet,
- stáhne detail auta z `https://www.sauto.cz/api/v1/items/{id}`,
- hledá podobné aktivní nabídky přes Sauto search API s funkčním filtrem `phrase=[model]`,
- lokálně nechá jen stejnou značku/model a blízký rok/nájezd,
- vloží do každé karty blok `Cenové srovnání podobných aut`,
- uloží audit JSON vedle HTML: `*_price_comps.json`,
- před první úpravou vytvoří zálohu `*_BACKUP_BEFORE_PRICE_COMPS.html`.

Důležité: Sauto API ignoruje některé filtry a vrací `unsupported_filters`. Nepoužívat slepě `manufacturer_cb` / `model_cb`; ověřený funkční filtr pro hledání je `phrase`. Výsledky jsou orientační tržní signál, ne garance prodeje. Když skript u vzácného auta napíše, že není dost podobných nabídek, je lepší to nechat tak než vymýšlet falešné procento.
