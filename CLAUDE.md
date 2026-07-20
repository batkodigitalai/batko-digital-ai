
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
# CLAUDE.md - projekt auto1

Tento soubor musi obsahovat stejne provozni pojistky jako `CODEX.md`, protoze nektere prace bezi
pres cowork/Claude a nesmi pouzit starsi pravidla.

---

## !! OPENLANE <-> SAUTO MASTER TOOL - POVINNE OD 2026-07-10 !!

Kdyz uzivatel zada hledani obchodni prilezitosti mezi OPENLANE a ceskym trhem,
safe bid, predvyber aut, audit konkretni aukce nebo zakaznicky vystup, cowork/Claude
musi nejdriv otevrit:

```text
docs\auto_arbitrage_finder\portable_master_tool\00_MASTER_PROMPT_OPENLANE_SAUTO.md
```

Rychla copy-paste verze pro Claude, Gemini, Codex nebo jiny model:

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

## !! PROVOZNI INSTRUKCE PRO CLAUDE (doplneno 2026-06-05) !!

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

## !! PRAVIDLO PRO DLOUHE CHATY A CENU PROVOZU !!

Pokud chat zacne byt dlouhy, pomaly, neprehledny nebo zbytecne drahy na dalsi praci, Claude/Codex
ma sam uzivatele upozornit a navrhnout predani do noveho chatu. Pred prechodem vytvorit kratky
souhrn v `docs\PREDAVACI_SOUHRNY\` s nazvem ve formatu `RRRRMMDD HHMM nazev` a zapsat:
- aktualni stav,
- dulezite soubory,
- endpointy/URL,
- otevrene ukoly,
- kriticka pravidla a incidenty.

Novy chat ma pokracovat z tohoto souhrnu, ne z cele dlouhe historie.

## !! SAUTO URL -> CR AUKCE: RYCHLY POSTUP (doplneno 2026-06-06) !!

Kdyz uzivatel posle Sauto detail URL, nejrychlejsi cesta je:

1. Z URL vytahnout numeric ID a nacist `https://www.sauto.cz/api/v1/items/{sauto_id}`.
2. HTML parsovat az jako fallback. Z API se bere cena, VIN, km, vybava, datumy, prodejce a `images`.
3. Pouzit `aukce_system\aukce_CR_TRH_TEMPLATE.html`, protoze jde o realny cesky trh.
4. Fotky ulozit lokalne. Sauto CDN vyzaduje referer a spravne encoded transform:
   `curl.exe -L -A "Mozilla/5.0" -e "https://www.sauto.cz/osobni/detail/..." --url "https:...jpeg?fl=exf%7Cres,1024,768,1%7Cwrm,/watermark/sauto.png,10,10%7Cjpg,80,,1" -o img/foto_01.jpg`
5. Pokud fotka nejde stahnout nebo ma jen stovky bajtu, je to chybova odpoved CDN, ne fotka.
6. Pri tvorbe HTML s ceskou diakritikou nepouzivat PowerShell 5 here-string bez garantovaneho UTF-8. Po ulozeni zkontrolovat, ze nejsou znaky typu `Ä`, `Ĺ`, `Ă`, `Å`.
7. In-app Browser muze blokovat `file://`; kontrolovat pres lokalni server:
   `python -m http.server 8766 --bind 127.0.0.1 --directory "...\\Projects\\auto1"`
8. Pred predanim overit: lokalni URL 200, galerie nacita fotky, verejna GitHub Pages URL 200, prvni JPG 200. Po uploadu pocitat s 10-20 s prodlevou a pouzit cache-busting `?v=YYYYMMDD-HHMM`.

## !! OPENLANE AUKCE - RYCHLE ROI VYHODNOCENI Z URL (doplneno 2026-06-06) !!

Kdyz uzivatel posle URL OPENLANE aukce nebo rekne, ze chce vyhodnotit auto z aukce,
Claude/Codex ma pouzit:

`docs\SOP_OPENLANE_RYCHLE_ROI_VYHODNOCENI.md`

Primarni cil neni marketingovy vystup, ale rychle ekonomicke rozhodnuti podle denniho ROI.

Povinny postup:
1. Pouzit prihlaseny/riceny Chrome s DevTools portem, idealne oddeleny profil na portu 9333.
2. Vycti OPENLANE API: auction, bidpriceinfo pro next bid, transportoptions, damages, SellerExtraInfo.
3. Transport je povinny presny udaj z `transportoptions`; nikdy ho neodhadovat.
4. Technicky report je povinny: pres damage JSONP najit `ReportItems.Url`, stahnout externi PDF report a projit ho.
5. Dohledej 3-5 aktualnich CZ trznich referenci a kurz CNB.
6. Spocitej ROI scenare 20/30/60 dni a max bid.
7. Vystup: `ANO drazit` / `PODMINECNE` / `NE nedrazit`, max bid EUR/Kc, ekonomicka tabulka,
   top 3 rizika a aukcni taktika.

Pokud chybi cena, transport, technicky report nebo trzni reference, verdikt oznacit jako neovereny
a nedoporucovat drazbu naslepo.

Nejdriv udelat rychle ROI sito. Hlubsi HTML nabidky, verejne stranky a marketingove vystupy delat
az po ekonomickem `ANO` nebo `PODMINECNE`.

## !! KRITICKE PRAVIDLO PRO TVORBU NOVYCH AUKCI (doplneno 2026-06-06) !!

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

## !! CR TRH / SAUTO AUKCE - SAMOSTATNY VZOR (doplneno 2026-06-06) !!

Pokud auto uz je v inzerci v CR a uzivatel doda Sauto URL nebo cesky inzerat, pouzit:

`aukce_system\aukce_CR_TRH_TEMPLATE.html`

Archivni kopie:
`aukce_system\20260606 1741 VZOR aukce CR trh realny prijem prodavajiciho a naklad kupujiciho.html`

Nepouzivat pro tento pripad evropsky OPENLANE ekonomicky pohled jako hlavni blok.

Povinne:
1. Vyplnit cenu prodavajiciho a srovnatelne ceny CR trhu: nejnizsi, median, maximum.
2. Vyvolavaci cenu nastavit defaultne o 10 % niz nez nejnizsi srovnatelna cena trhu.
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

## !! POVINNE PRO SAUTO OSLOVENI PRODAVAJICICH (doplneno 2026-06-01) !!

Kazda prace se Sauto oslovovanim musi respektovat:

- `docs\SOP_SAUTO_OSLOVENI.md`
- Google Sheet list `Sauto_Komunikace`
- deduplikaci podle `sauto_id` a `conversation_key = sauto-{id}`
- kontrolu `...?action=sauto_summary` pred dalsi vlnou

Claude/Codex nesmi generovat dalsi vlnu oslovenych inzeratu bez kontroly, ktera Sauto ID uz byla
oslovena. Odpovedi prodavajicich se paruji pres `conversation_key` a mohou byt v samostatnych
radcich pod odeslanim. Po kazde vlne je povinne porovnat pocet nahlasenych odeslani s poctem v
Sheetu a vypsat chybejici ID.

Pri praci se Sauto pouzivat prihlaseny stav v otevrenem prohlizeci. Aktualni prihlaseny ucet pro
Sauto je `batko.digital.ai@gmail.com`; nepouzivat anonymni/neprihlasene pokusy, pokud je tento
prihlaseny kontext dostupny.

Aktualni poznamka 2026-06-01 vecer: uzivatel nahlasil 20 odeslanych nabidek a `sauto_summary`
po doplneni chybejiciho Sauto ID `210268256` (Skoda Kodiaq 2.0 TSI Style) vraci 20. Pred dalsi
vlnou presto vzdy znovu nacist `sauto_summary` a vynechat vsechna uz evidovana ID.

## !! JAK ZJISTIT DATUM INZERÁTU NA SAUTO (nauceno 2026-06-05) !!

Pro uzivatele: Ctrl+U na strance inzeratu → Ctrl+F → hledat `create_date` → vysledek: `"create_date":"2026-03-26T19:47:26"` = datum vlozeni.

Pro Claude: Pouzit Chrome rozsireni (javascript fetch na detail URL, regex `"create_date":"([^"]+)"`) PRED kazdou vlnou osloveni. Nikdy neodhadovat stari z filtru Sauto — vzdy overit create_date. Sauto filtr `stari-inzeratu=mesic` NENI spolehlvy — inzeraty mohou byt nove i kdyz projdou filtrem.

## !! KRITICKA POJISTKA SAUTO - STARI INZERATU (incident 2026-06-01) !!

Claude/Codex/AI nesmi prodavajicimu tvrdit, ze inzerat je na Sauto "pres mesic", "dlouho",
"stagnuje", "neprodava se" nebo podobne, pokud neni u konkretniho inzeratu overene `create_date`
a spocitany skutecny pocet dni. Filtr Sauto `item_age_cb`, poradi vysledku ani dojem ze stranky
nejsou dukaz stari inzeratu.

Bez overeneho data se pouziva neutralni formulace typu:
`narazil jsem na vas inzerat ... u takoveho auta muze byt bezny inzerat nekdy pomaly`.

Toto pravidlo plati pred kazdym generovanim, kopirovanim nebo odeslanim Sauto osloveni.

## !! POVINNY FORMAT SAUTO KLIKACIHO HTML A KONTROLY VLNY (doplneno 2026-06-05) !!

!! NAUCENO 2026-06-16 — KRITICKE OPRAVY PRO SAUTO VLNY !!

!! KRITICKA CHYBA OPRAVENA 2026-06-16 — SAUTO DETAIL URL (ztracene hodiny uzivatele) !!
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

!! KRITICKA CHYBA OPRAVENA 2026-06-16 — SAUTO DETAIL API !!
Sauto `/api/v1/items/{id}` vraci `d.result.status` — NE `d.data.result.status`.
Kontrola `d.data.result.status` vzdy vraci undefined = vsechna ID se chybne oznaci jako mrtva.
VZDY nejdriv otestovat 1 ID a vypsat `Object.keys(d)` nez provedes hromadnou kontrolu.

!! KRITICKA CHYBA OPRAVENA 2026-06-16 — KOPIRUJ SYNTAX ERROR (ztracene hodiny uzivatele) !!
Edit tool pouzity na velky script blok = zdvojeni klicoveho slova = `async async function kopiruj`.
`async async` je syntax error = CELY script blok prestane fungovat, zadna funkce nefunguje.
NIKDY nepouzivat Edit tool na `<script>` sekci > 50 radku. VZDY Python skript.
Po kazdem generovani HTML vlny POVINNE overit:
  grep "async async" soubor.html  → musi vratit 0 vyskytu
  grep -c "kopirujFallback" soubor.html  → musi vratit 0 (nebo kompletni cisty blok)
  V Chrome konzoli: (function(){try{return typeof kopiruj}catch(e){return e.message}})()  → musi vratit "function"
CDP timeout pri testu clipboard = NORMALNI (ceka na user gesture). Fyzicky klik uzivatele funguje vzdy.

NAZEV SOUBORU: VZDY format `RRRRMMDD HHMM osloveni vlna XXX.html`
Priklad: `20260616 1545 osloveni vlna 010.html`
NIKDY stary format `OSLOVENI_KLIK_YYYYMMDD_VLNA*.html`.

REPLY PANEL: Textarea + tlacitka `Zapsat odeslani do Sheetu` a `Zapsat odpoved do Sheetu`
MUSI BYT NATVRDO V HTML KAZDE KARTY. Nikdy je negenerovat jen pres JS `initReplyPanels()`.
JS muze selhat tisnne a uzivatel panel neuvidi. Hardcode = jedina spolehliava cesta.

HROMADNE TLACITKO: `Zapsat vsechna odeslani do Sheetu` MUSI BYT NA DVOU MISTECH:
1. NAHORE — hned pod progress barem
2. DOLE — za posledni kartou, pred </body>

GENEROVANI HTML: Vzdy Python skript. Nikdy Edit tool na velky soubor (riziko zkraceni/fragmentu).
Po kazdem zapisu zkontrolovat: `tail -5` musi skoncit `</html>`, grep na orphaned fragmenty.

Klikaci HTML pro Sauto vlny musi vychazet z existujiciho funkcniho vzoru:
`docs\OSLOVENI_KLIK_20260605_VLNA5_OPRAVENO.html`
Nesmí se vymyslet novy layout ani odstranit provozni prvky.

Povinne prvky HTML:
- karta pro kazdy inzerat,
- zalozky `Zprava A (plna)` a `Zprava B (zkracena)`,
- tlacitka kopirovani A/B,
- checkbox `Odeslano`,
- odpovedni panel HARDCODED v HTML (textarea + Zapsat odeslani + Zapsat odpoved),
- hromadne tlacitko `Zapsat vsechna odeslani do Sheetu` NAHORE I DOLE,
- Apps Script integrace `sauto_summary`, `ulozOdeslani`, `ulozOdpoved`, `ulozVsechnaOdeslani`,
- viditelny pocet dni v inzerci a datum `create_date` v meta radku karty.

Pred kazdou novou vlnou je povinne:
1. Nacist zive `Sauto_Komunikace` / `sauto_summary` a vyloucit vsechna drive zpracovana `sauto_id`.
2. U kazdeho noveho kandidata overit detailni `create_date` z Sauto detail API nebo zdroje stranky
   regexem `"create_date":"([^"]+)"`.
3. Spocitat skutecny pocet dni proti aktualnimu datu.
4. Zaradit jen inzeraty s poctem dni striktne `> 30`; hodnota `30` nestaci.
5. Do HTML uvadet pocet dni v inzerci a datum vlozeni.
6. Ulozit audit vybranych ID, create_date a dni, aby slo zpetne zkontrolovat zdroj.

Po odeslani vlny je povinne:
1. Znovu nacist `sauto_summary`.
2. Porovnat vsechna ID z HTML/auditu proti `sent_ids`.
3. Vypsat chybejici ID, pokud nejake chybi.
4. Pokud vse sedi, nahlasit pocet odeslanych a potvrdit, ze nova ID nebyla v Sheetu pred vlnou.

## Studijni materialy

- Studijni/konkurencni materialy patri do `docs\STUDIJNI_MATERIALY\`.
- Kazdy novy studijni material se povinne pojmenovava ve formatu `RRRRMMDD HHMM nazev`, napr.
  `20260601 1825 Automato jak nenaletet pri koupi ojeteho auta.md`.
- Nekopirovat texty konkurence, pouzit jen jako inspiraci pro strukturu, argumentaci a duveru.

## !! POVINNE PRED KAZDYM UPLOADEM AUKCE (nauceno 2026-06-01) !!

1. `tail -5 index.html` — musi skoncit `</html>`. Pokud ne, soubor je uriznuty — NENAHRÁVAT.
2. Vsechny `document.getElementById()` v `initPage()` musi mit null-check pres `setEl()`.
3. Po zmene HTML modelu prohledat JS pro reference na odstranene elementy.
4. Bez teto kontroly zpusobi upload nefunkcni galerii a ztratu casu uzivatele.
TOTO PRAVIDLO PLATI PRO CLAUDE, CODEX I JAKEHOKOLIV DALSIHO AGENTA.

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

## Zavazna pravidla pro nabidky aut

1. Finalni denni `_K.html` musi vychazet z Passat vzoru:
   `nabidky_aut\20260523_auto1_11004535_VW_Passat_Variant\nabidka_VW_Passat_Variant_11004535_KONVERZE.html`.
2. Nemeni se koncept a obsahove bloky pod fotografiemi; meni se pouze data auta, ID, ceny, rizika,
   aukcni udaje, fotky a jejich skutecny pocet.
3. Verejne HTML nesmi viditelne uvadet nazev aukcni platformy. Pouzivat obecne oznaceni typu
   `evropska aukce` nebo `evropsky aukcni zdroj`; cislo aukce/reference zustava.
4. Konec aukce se nesmi hadat. Musi byt z explicitni stranky aukce, ze screenshotu se znamym casem,
   nebo z uzivatelem potvrzeneho casu.
5. Kazde publikovane HTML musi mit jednotnou paticku, identifikaci zpracovatele a upozorneni na
   ochranu osobnich udaju podle Passat vzoru.
6. Galerie musi odpovidat skutecnym lokalnim fotkam. Pocet hlavich fotek, nahledu a pocitadlo
   galerie musi presne odpovidat poctu souboru v `img`; nesmi zustat odkazy na neexistujici fotky.
7. Kazdy lead musi v Google tabulce i telefonni zprave rikat, ktere tlacitko ho odeslalo a co je
   navazujici ukol. `formType`, `source` nebo `note` musi obsahovat konkretni tlacitko, sekci a ukol.
8. Odemykaci modal musi jit pouzit opakovane: pri kazdem otevreni resetovat formular, skryt stav
   uspechu a nastavit aktualni cil odemceni.
9. Pred kazdym uploadem aukce POVINNE: `tail -5 index.html` musi skoncit `</html>`. Vsechny
   `document.getElementById()` v `initPage()` musi mit null-check (helper `setEl()`). Po zmene
   HTML modelu prohledat JS pro reference na odstranene elementy. Bez teto kontroly NENAHRÁVAT.
10. Upload je zakazan, pokud chybi footer/privacy, galerie nesedi na skutecny pocet fotek, leady
   neposilaji jasny ukol, aukcni konec neni jisty, nebo zustaly zbytky stareho auta.
10. Zpracovani leadu musi byt zastavene na schvaleni uzivatele. AI/Codex/Claude smi pripravit
    podklady a koncept, ale nesmi odeslat email, SMS ani klientskou zpravu bez vyslovneho aktualniho
    schvaleni.
11. Kazdy krok s leadem se zapisuje do Google Sheet: prijato, slouceno, podklady pripraveny,
    koncept pripraven, ceka na schvaleni, odeslano. Povinna pole: tlacitko, sekce, ukol,
    stav_zpracovani, schvaleni, draft_id, podklady, odeslano.
12. Duplicitni leady stejne osoby ke stejnemu autu se slucuji podle emailu/telefonu/ID auta.
    `specs` znamena technicke podrobnosti/stav, `eq` kompletni vybavu, `docs` dokumentaci.
    Klient dostane jeden slouceny follow-up, ne samostatnou odpoved za kazde kliknuti.
13. Zakaznicke prilohy nesmi obsahovat lokalni cesty, `file:///`, `C:\Users`, interni zdroj leadu
    nebo interni kody `specs/eq`. Pokud se HTML v Gmailu zobrazuje jako zdrojovy kod, neposilat ho
    klientovi; pouzit PDF bez hlavice/paticky prohlizece nebo verejny odkaz.
14. Verejny trychtyr sluzeb `verejny_trychtyr_auto_sluzby_11004535.html` zapisuje leady do Sheet
    a uklada mensi prilohy do Google Drive slozky `AUTO_LEADS_PODKLADY`.
    Provozni manual je `docs\PROVOZNI_MANUAL_VEREJNY_TRYCHTYR_A_DRIVE.md`.
    Spravny Drive odkaz je `https://drive.google.com/drive/folders/1qYPccoGlbf1UhC_D8wLnhfoq9dT-xExt`.
    Zakaznikovi se nezobrazuji interni technicke informace o Drive/Sheet zapisu; vidi jen bezpecny
    text, ze muze prilozit mensi soubory nebo vlozit sdileny odkaz.
15. Publikovana verejna URL trychtyre je
    `https://batkodigitalai.github.io/batko-digital-ai/nabidky/20260526_auto1_11004535_VW_Passat_Sluzby/verejny_trychtyr_auto_sluzby_11004535.html`.
    Publikovatelna kopie je v `nabidky_aut\20260526_auto1_11004535_VW_Passat_Sluzby\` a ma
    relativni cesty k fotkam `img/foto_XX.jpg`. Pro nahrani jedne slozky na GitHub Pages je
    pripraven skript `scripts\upload_single_folder_to_github.js`.
16. Univerzalni landing page pro kontrolu auta pred koupi je
    `nabidky_aut\20260527_auto1_univerzalni_kontrola_auta_pred_koupi\kontrola_auta_pred_koupi.html`.
    Verejna URL je
    `https://batkodigitalai.github.io/batko-digital-ai/nabidky/20260527_auto1_univerzalni_kontrola_auta_pred_koupi/kontrola_auta_pred_koupi.html`.
    Stranka umi parametry `refUrl`, `refImg`, `refVehicle`, `utm_source`, `utm_medium`,
    `utm_campaign`, `utm_content`. Pozicovani musi zustat cestne: nejde o fyzickou prohlidku,
    ale o prvni vzdaleny prescreen pred cestou, vyjednavanim nebo objednanim mechanika.
    Platby jsou zatim rucni po potvrzeni: klient odeslanim formulare nic neplati, nejdrive se
    potvrdi rozsah a cena, potom se posilaji platebni udaje nebo QR platba; prace zacina az po
    zaplaceni.
    Stranka muze obsahovat verejnou ukazku vystupu, aby klient videl, co si objednava. Ukazka smi
    obsahovat jen zakaznicky bezpecne casti: verdikt, skore, hlavni plusy, rizika, co doplnit a
    dalsi krok. Nesmí obsahovat interni zdroje, Sheet/Drive workflow, interni kody, lokalni cesty,
    pracovni poznamky, marze, interní rozhodovaci postupy ani nic, co by klientovi davalo mylny
    pocit finalni fyzicke kontroly.
    Zakaznicke potvrzeni po odeslani nesmi obsahovat technicke formulace typu "lokalni stranka",
    "zapis nejde potvrdit" nebo "e-mail se neotevira"; v pripade nejednoznacne odpovedi formulare
    se klientovi ukazuje jen klidne `Poptavka byla odeslana ke zpracovani.`
17. Interni ROI nastroj — sablona je `interni_roi_nastroj_TEMPLATE.html`, ktera ma JSON import panel
    nahore (panel "Rychle nacteni dat"). Postup viz `SOP_ROI_NASTROJ.md`.
    Uzivatel hodi do chatu *.docx (OPENLANE listing) + *.md (inspekcni zprava) + OPRAVY Kc.
    Claude si soubory precte sam (neptejte se na rucni zadavani dat), fetchne kurz EUR/CZK z CNB
    (cnb.cz/denni_kurz.txt), zjisti trzni ceny pres WebSearch na sauto.cz, dopocita fee correction
    a vypise POUZE JSON blok — zadne dalsi komentare. Uzivatel vlozi JSON do sablony, klikne Nacist.
    Pevne defaulty (registrace 7500, priprava 8000, servis 12000, rezerva reklamace 25000,
    jina rezerva 10000, cilovy zisk 30000, vynos/den 0.50%) se meni jen na explicitni pokyn.
    Cilovy zisk je pseudonaklad v kalkulaci max. nabidky v aukci.
    Vzorovy vyplneny soubor: `interni_roi_nastroj_11008921_Skoda_Octavia.html`.
18. Forenzni rozhodovaci audit vozu — 4 servisni prompty (AUDIT-CORE, REPORT-PDF, SALES-COPY,
    LEAD-HANDLER) jsou v `docs\PROMPTY_FORENZNI_AUDIT_VOZU.md`.
    Produkt: vzdálená analyza VIN + pravni + historicka + trzni vrstva, verdikt BUY/HOLD/REJECT,
    skore 0-100, balicky 1490/2490/3490 Kc. Neni fyzicka inspekce.
19. Aukcni system — slozka `aukce_system\`. Provozni manual: `aukce_system\PROVOZNI_MANUAL_AUKCE.md`.
    Admin panel (`aukce_admin.html`) pouziva Firebase REST API pres fetch() — NIKDY Firebase SDK.
    Duvod: SDK hazi vyjimku z file:/// a zpusobi DEMO rezim (localStorage misto Firebase).
    REST_BASE = `https://batko-aukce-default-rtdb.europe-west1.firebasedatabase.app`
    Verejne aukcni stranky (index.html) pouzivaji REST polling kazde 4s.
    Bidy zapisuji pouze verejne formulare na index.html — admin panel bidy jen cte a spravuje stav.
    Konec aukce NESMI se hadat — viz pravidlo 4 nahore.
    endTime v AUCTION_CONFIG (index.html) je pouze fallback — Firebase endTime ma VZDY prednost
    a VZDY prepise lokalni hodnotu (podminku `> Date.now()` NEPOUZIVAT — zahazovala by spravny cas).
    initExtras() a vsechny funkce co pristupuji k DOM elementum musi mit null-checky nebo try/catch
    — jinak pad zastavi setInterval a countdown zamrzne.
    Tlacitko 🗑 pro smazani prihozu je v poslednim sloupci tabulky v admin panelu (scrollovat doprava).
    Upload nove/opravene aukce: `upload_aukce.bat` dvojklikem v `auto1\`.
## !! KRITICKE PRAVIDLO UPLOADU — RYCHLOST A CENA (nauceno 2026-06-16, incident AUK-010) !!

NIKDY nepouzivat chunked JS upload pres Chrome MCP pro binarne soubory (PDF, obrazky).
NIKDY nespoustet GitHub API volani ze sandboxu (OSError 403 Forbidden — sandbox je za proxy).
VZDY pouzit Python skript na pocitaci uzivatele pro upload souboru.

Poloautomat (standardni postup):
1. Claude pripravi: index.html + katalog_eu.html + upload_aukce.bat + upload_aukce_docs.py
2. Uzivatel spusti: upload_aukce.bat (dvojklik) — nahrani HTML + fotky
3. Uzivatel spusti: upload_aukce_docs.bat (dvojklik) — nahrani PDFs
4. Claude dokoncí: Firebase PATCH pres Chrome MCP fetch() + overeni live URL

Duvody:
- Sandbox → GitHub API vraci 403 (proxy blokuje) — NELZE
- Chrome MCP chunked JS → 10x vice tool calu, 10x drazsi — ZAKAZ
- Python na PC uzivatele → prochazi primo, upload za sekundy — JEDINA SPRAVNA CESTA

Pevna pravidla:
- Python skript pro vsechny soubory (HTML, PDF, img) — KRITICKE
- Nikdy chunked JS upload pres Chrome — ZAKAZ
- Firebase PATCH vzdy pres Chrome MCP fetch() (sandbox nefunguje)
- Overit kazdy PDF: HTTP 200 + prvni bajty %PDF- — POVINNE
- 1 session = 1 aukce, neprenasej velky kontext pres reset

Automat (budoucnost):
- GitHub Actions workflow spousteny commitem
- Claude pripravi soubory a commitne pres GitHub API z Chrome
- Actions deployuje automaticky, Firebase PATCH jako krok
- Uzivatel nespousti zadne bat soubory

20. POVINNY KONTROLNI SEZNAM pro dokonceni aukce (Claude musi splnit VSE sam, bez ukolu uzivatel):
    [ ] AUCTION_CONFIG v index.html vypln (auctionId, auto, ceny, fotky, rizika, specifikace)
    [ ] photos[] obsahuje spravny pocet souboru odpovidajici skutecnym fotkam v img\
    [ ] upload_aukce.bat aktualizovat na novou slozku
    [ ] Spustit upload (upload_aukce.bat) — nebo to udelat pres GitHub API
    [ ] Vytvorit aukci v Firebase pres REST API PATCH na /auctions/AUK-XXX.json
        (REST_BASE/auctions/AUK-XXX.json, metoda PATCH, stejny endTime jako v index.html)
    [ ] Overit live URL: nactit stranku, zkontrolovat countdown a nazev auta
    [ ] Prezentovat soubory uzivatel (present_files na index.html a upload_aukce.bat)

## Sauto -> Diagnóza neprodaného auta -> Stripe trychtýř (funkční stav 2026-06-17)

Veřejná Streamlit aplikace:
`https://batkodigitalai-bat-90-labcar-sale-diagnosis-streamlitapp-3hw8bj.streamlit.app/`

Stripe Payment Link:
`https://buy.stripe.com/9B6cN61bIcyH7l95sv3VC03`

Aktuální klikací HTML vlna:
`C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1\docs\20260617 1048 osloveni vlna 012.html`

Správný obchodní postup:
1. Otevřít původní inzerát a ověřit, že je stále živý.
2. Kliknout `Diagnóza auta` a ověřit, že veřejný Streamlit načetl konkrétní auto.
3. Prodávajícímu nejdřív poslat lidské oslovení, ne platební odkaz. Cíl první zprávy je reakce/souhlas.
4. Po kladné reakci poslat odkaz na diagnostiku konkrétního auta.
5. Ve Streamlitu zákazník zadá jméno, e-mail, telefon a souhlas; známá data auta se z URL znovu neptají.
6. Bezplatný předverdikt je lead magnet, plná diagnóza je placená za 199 Kč včetně DPH.
7. Stripe link se nevyrábí zvlášť pro každé auto. Appka k jednomu Payment Linku přidává `client_reference_id=[lead_id]`, `prefilled_email`, `utm_source`, `utm_content`.
8. Po platbě dohledat zákazníka podle e-mailu a `client_reference_id`; výstup poslat na e-mail nebo navázat ručně.
9. Navazující nabídka: přepis inzerátu 790 Kč včetně DPH, cenové srovnání a taktika 1 490 Kč včetně DPH, kompletní prodejní balíček 2 490 Kč včetně DPH.
10. Po každém oslovení zaškrtnout `Odesláno`; na konci vlny zapsat odeslání do Sheetu.

Nikdy neříkat hotovo, dokud neprojde anonymní smoke test:
- veřejná Streamlit URL se otevře v anonymním okně bez přihlášení,
- URL s parametry zobrazí správný model/cenu/nájezd/dny,
- Stripe checkout ukáže produkt `Plná diagnóza neprodaného auta` za 199 Kč,
- platební URL obsahuje `client_reference_id`,
- HTML vlna neobsahuje `localhost:8501`.

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
