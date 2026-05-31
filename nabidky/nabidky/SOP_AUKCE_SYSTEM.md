# SOP — Internetový aukční systém vozidel
_BATKO.DIGITAL.AI | Ing. Jaroslav Batko – Linet | IČO 14600153_
_Verze: 2026-05-29_

---

## JAK SYSTÉM FUNGUJE

Ty vybereš auto z evropské aukce → vytvoříš svoji českou aukci → zákazníci přehazují na stránce → vítěz platí zálohu → teprve pak jdeš kupovat auto na evropské aukci za vítězovu cenu.

**Výhoda:** nepotřebuješ vlastní kapitál. Auto jdeš koupit až když máš zákazníka s podepsaným závazkem a složenou zálohou.

---

## SOUBORY SYSTÉMU

```
aukce_system/
  aukce_TEMPLATE.html   ← veřejná dražební stránka (kopíruj pro každé auto)
  aukce_admin.html      ← správa aukcí, live bidy, zrušení/ukončení
  SOP_AUKCE_SYSTEM.md   ← tento manuál
```

---

## KROK 1 — JEDNORÁZOVÉ NASTAVENÍ FIREBASE (5 minut)

Firebase = databáze v reálném čase. Zdarma, bez serveru.

1. Jdi na **console.firebase.google.com** → přihlás se Google účtem
2. **Vytvořit projekt** → název: `batko-aukce` → pokračovat
3. V menu vlevo: **Realtime Database** → Vytvořit databázi → vybrat `europe-west1` → **Testovací režim** (spustí se s otevřenými pravidly, do 30 dnů změníš)
4. V menu vlevo: **Nastavení projektu** (ozubené kolo) → záložka **Obecné** → sjeď dolů → **Vaše aplikace** → ikona `</>` (web) → zaregistruj aplikaci → zobrazí se konfigurační objekt

Konfigurační objekt vypadá takto:
```js
{
  apiKey: "AIza...",
  authDomain: "batko-aukce.firebaseapp.com",
  databaseURL: "https://batko-aukce-default-rtdb.europe-west1.firebasedatabase.app",
  projectId: "batko-aukce",
  storageBucket: "batko-aukce.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123:web:abc"
}
```

5. Otevři `aukce_admin.html` v prohlížeči → vyplň Firebase konfiguraci → **Uložit a připojit**
6. Pokud uvidíš ✅ Připojeno — Firebase je nastavený. Hotovo jednou provždy.

**Heslo do admin panelu:** Aktuálně `123` — **ZMĚŇ!**
Jdi na https://emn178.github.io/online-tools/sha256.html → zadej své heslo → zkopíruj hash → vlož do `aukce_admin.html` na řádek `const PASS_HASH = '...'`

---

## KROK 2 — NASTAVENÍ DATABÁZOVÝCH PRAVIDEL

Po 30 dnech testovacího režimu musíš nastavit pravidla. V Firebase Console → Realtime Database → Pravidla:

```json
{
  "rules": {
    "auctions": {
      "$auctionId": {
        ".read": true,
        "bids": {
          ".write": true,
          ".read": true
        },
        "status": {
          ".read": true
        },
        "cancelReason": {
          ".read": true
        }
      }
    }
  }
}
```

(Admin panel může zapsat díky admin SDK nebo přes tvůj přihlášený účet — pro MVP stačí testovací režim.)

---

## KROK 3 — SPUŠTĚNÍ NOVÉ AUKCE

### A) Připrav stránku pro zákazníky

1. **Zkopíruj** `aukce_TEMPLATE.html` → přejmenuj na `aukce_AUK-XXX.html`
2. Otevři soubor a **vyplň AUCTION_CONFIG** na začátku:

```js
const AUCTION_CONFIG = {
  auctionId:    "AUK-002",          // stejné ID jako v admin panelu
  make:         "Škoda",
  model:        "Octavia RS",
  year:         2022,
  engine:       "2.0 TSI 180 kW",
  km:           45000,
  endTime:      "2026-06-15T18:00:00",  // SKUTEČNÝ čas — NESMÍ SE HÁDAT!
  startPrice:   380000,
  minIncrement: 1000,
  photos: ["img/foto_01.jpg", "img/foto_02.jpg"],
  risks: ["...", "..."],
  specs: { "Rok": "2022", "Motor": "2.0 TSI 180 kW", ... },
  firebase: { /* viz krok 1 */ },
  sheetUrl: "https://script.google.com/macros/s/TVOJE_ID/exec"
};
```

3. Přidej fotky do složky `img/` (relativní cesty)
4. **Publikuj** na GitHub Pages nebo pošli zákazníkům přímo soubor/odkaz

### B) Vytvoř aukci v admin panelu

1. Otevři `aukce_admin.html`
2. Přihlás se heslem
3. Vyplň formulář **Nová aukce** se stejným `auctionId` jako v HTML souboru
4. Klikni **Vytvořit / Uložit aukci**
5. Aukce se okamžitě zobrazí v seznamu

---

## KROK 4 — SLEDOVÁNÍ AUKCE

- V `aukce_admin.html` klikni na aukci v seznamu → vidíš live bidy
- Tabulka se aktualizuje v reálném čase
- Vidíš: jméno, e-mail, telefon, výši příhozu, čas

---

## KROK 5 — UKONČENÍ AUKCE

### Varianta A — normální konec (čas vyprší)
- Veřejná stránka automaticky zobrazí "Aukce uzavřena"
- V admin panelu klikni **Ukončit a vybrat vítěze** → zobrazí se údaje vítěze → aukce se nastaví na `ended`
- Kontaktuj vítěze do 24 hodin

### Varianta B — zrušení (auto se nepodaří zajistit)
- V admin panelu klikni **Zrušit aukci**
- Zadej důvod (zobrazí se na veřejné stránce)
- Veřejná stránka okamžitě zobrazí "Aukce zrušena"
- Kontaktuj všechny uchazeče e-mailem

---

## KROK 6 — PO VYHRANÍ AUKCE

Použij prompty z `docs/PROMPTY_FORENZNI_AUDIT_VOZU.md`:

**PROMPT 4 — ZPRACOVÁNÍ POPTÁVKY** → vložit data vítěze jako lead a připravit odpověď / follow-up e-mail

Postup:
1. Kontaktuj vítěze (e-mail + telefon)
2. Pošli platební instrukce pro zálohu (obvykle 10 000 Kč)
3. Po přijetí zálohy jdi do evropské aukce a přihazuj max. do výše vítězovy nabídky
4. Pokud vyhraješ — informuj zákazníka, domluvte předání
5. Pokud prohraneš — vrať zálohu, informuj zákazníka

**Pro analýzu auta před spuštěním aukce** → použij VYVÁŽENÝ MASTER PROMPT (viz `20260512.../07_Rychla_Analyza_Interni.docx.md`)

---

## EXPORT BIDŮ

V admin panelu → vybraná aukce → **Export bidů (CSV)** → otevři v Excelu (kódování UTF-8 s BOM).

---

## ŠKÁLOVATELNOST — CO PŘIDAT PŘÍŠTĚ

| Funkce | Kdy | Jak |
|---|---|---|
| E-mail notifikace "jsi přehozený" | Jakmile bude zájem | Firebase Functions + SendGrid (zdarma do 100/den) |
| Více aukcí najednou | Hned jde | Každá aukce má vlastní `auctionId` — funguje paralelně |
| Automatické ukončení | 3. aukce | Firebase Functions s časovačem |
| Záloha přes platební bránu | Po ověření konceptu | Stripe nebo GoPay (webhook do Firebase) |
| Admin přihlášení přes Google | Po MVP | Firebase Authentication |

---

## PROMPTY K POUŽITÍ (z pinned Dashboard)

### Pro analýzu auta před aukcí
Použij **VYVÁŽENÝ MASTER PROMPT PRO DOVOZ AUTA Z AUKCE** — dá ti doporučený bid a absolutní strop. Tvůj strop v české aukci = evropský absolutní strop mínus tvoje odměna a náklady.

### Pro zpracování vítěze
Použij **PROMPT 4 — ZPRACOVÁNÍ POPTÁVKY** z `PROMPTY_FORENZNI_AUDIT_VOZU.md` — extrahuje data vítěze, připraví follow-up.

### Pro případ že vítěz chce audit vozidla
Nabídni mu **Rychlý předfiltr (790 Kč)** nebo **Hloubkový audit (3 490 Kč)** dle ceníku.

---

## PRAVIDLA (z CLAUDE.md)

- ❌ Neuvádět název evropské aukční platformy na veřejné stránce → použít "evropský aukcní zdroj"
- ❌ Nehádat čas konce aukce → musí být z reálné stránky nebo screenshotu
- ✅ Footer + GDPR na každé stránce (je v šabloně)
- ✅ Zálohu zákazník platí až po výhře a po tvém potvrzení
- ✅ Každý lead (bid) jde do Google Sheet jako záloha

---

## CO JE NOVÉ VE VERZI 2

### Veřejná stránka (aukce_TEMPLATE.html)
| Nová sekce | Co dělá | Proč |
|---|---|---|
| **Tržní srovnání** | Zobrazí tržní cenu CZ, úsporu, náklady dovozu | Zákazník ví proč přihodit — konverze ↑ |
| **Datum doručení** | Konec aukce + 14–21 dní + 5 dní = konkrétní datum | Zákazník si naplánuje — urgency ↑ |
| **Skóre vozu 0–100** | Automaticky z roku, km, značky | Důvěra — ukazuje že auto je prověřené |
| **Provizní kalkulačka** | Zákazník zadá svůj bid → vidí all-in cenu | Transparentnost → méně dotazů |
| **B2B blok** | Marže pro autobazary, ROI/den | Targeting 170 firem z autobazary.csv |
| **Odkaz na _K.html** | Propojení s existujícími nabídkovými stránkami | Trychtýř: detail → aukce |
| **Lead pipeline pole** | Bidy jdou do Sheetu s formType, tlacitko, sekce, ukol, stav_zpracovani=PRIJATO | Integrace s existujícím systémem |

### Admin panel (aukce_admin.html)
| Nová funkce | Co dělá |
|---|---|
| **ROI kalkulačka** | Zadáš bidEur, kurz, opravy, tržní cena → spočítá reserve price a max. bid CZ |
| **Reserve price (skrytý floor)** | Zákazníci nevidí; aukce se auto-zruší pokud nikdo nepřehodí |
| **Auto-zrušení pod rezervou** | Při ukončení aukce systém zkontroluje floor — zruší bez odhalení čísla |
| **Vítěz → Sheet pipeline** | stav CEKA_NA_SCHVALENI + všechna povinná pole z POSTUP_LEADS.md |
| **Export CSV s metadaty** | Obsahuje ROI data, reserve price, stav pipeline každého biddera |
| **Live stats panel** | Reserve naplněna ✅/❌, zbývající čas, nákupní cena z ROI kalkulačky |

### Jak vyplnit nová pole v AUCTION_CONFIG
```js
roi: {
  marketPriceCZ:  450000,  // z tipcars.com / AutoScout24
  transportCZ:    8000,    // skutečná cena dopravy
  registrationCZ: 7500,    // přepis + poplatky
  stkCZ:          1200,    // STK
  deliveryDaysMin: 14,
  deliveryDaysMax: 21,
  carScore:       72,      // spočítej: stáří×15 + km/170k×100, odečti od 100
  scoreLabel:     "Doporučeno",
  b2bMarketLow:   420000,  // jen pokud chceš B2B blok
  b2bSaleTarget:  460000,
  b2bDaysSale:    20
},
detailPageUrl: "../nabidky_aut/20260523.../nabidka_..._KONVERZE.html"
```

### Napojení na existující Apps Script
Sheet URL je předvyplněna z konverzní stránky Passatu:
`https://script.google.com/macros/s/AKfycbwcFA8bRyHnBB.../exec`

Bidy jdou do stejného Sheetu jako ostatní leady. Rozliší se podle `formType`:
- `aukce_bid` = každý příhoz
- `aukce_winner` = vítěz (stav CEKA_NA_SCHVALENI)

---

_Verze 2.0 — 2026-05-29_
