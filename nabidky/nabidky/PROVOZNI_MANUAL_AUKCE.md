# PROVOZNÍ MANUÁL — Aukční systém BATKO.DIGITAL.AI

**Poslední aktualizace:** 2026-05-30  
**Firebase DB:** `https://batko-aukce-default-rtdb.europe-west1.firebasedatabase.app`  
**GitHub Pages:** `https://batkodigitalai.github.io/batko-digital-ai/nabidky/`

---

## PŘEHLED SOUBORŮ

| Soubor | Co to je | Kde otevřít |
|--------|----------|-------------|
| `aukce_system\aukce_admin.html` | Admin panel — vytváří aukce, sleduje bidy, ukončuje | Lokálně `file:///` — NIKDY na web |
| `aukce_system\aukce_TEMPLATE.html` | Šablona veřejné stránky | Kopírovat pro každou novou aukci |
| `aukce_system\YYYYMMDD_AUK-XXX_...\index.html` | Veřejná aukční stránka | GitHub Pages (po uploadu) |
| `upload_aukce.bat` | Nahraje opravenou stránku na GitHub Pages | Dvojklik v `auto1\` |

---

## FÁZE 1 — ROZHODNUTÍ VYTVOŘIT AUKCI

### Co musíš mít připraveno PŘED zahájením:
- ✅ **Přesný datum a čas konce aukce** — z aukční platformy nebo vlastní rozhodnutí; NIKDY hádat
- ✅ **Fotky auta** — uložené lokálně (pojmenované `foto_01.jpg`, `foto_02.jpg`, …)
- ✅ **Data auta** — značka, model, rok, km, barva, reference aukce
- ✅ **Vyvolávací cena** v Kč
- ✅ **Reserve price** (nepovinná) — skrytý floor; pod touto cenou se aukce automaticky zruší

---

## FÁZE 2 — VYTVOŘENÍ AUKCE

### Krok 2A — Unikátní ID aukce

Zvolit ID ve formátu `AUK-XXX` (např. `AUK-002`). Bez mezer, bez diakritiky. Toto ID se použije ve třech místech — admin panel, Firebase, složka.

### Krok 2B — Vytvořit v admin panelu

1. Otevřít `aukce_system\aukce_admin.html` dvojklikem
2. Heslo: **123**
3. Zkontrolovat zelený banner „Připojeno k Firebase" — pokud je žlutý DEMO režim, Firebase nedostupný, nepokračovat
4. V levém panelu vyplnit sekci **Nová aukce / upravit**:
   - ID aukce: `AUK-XXX`
   - Značka, Model, Rok, Km
   - Vyvolávací cena (Kč)
   - Min. příhoz (obvykle 1 000 Kč)
   - **Konec aukce — datum a čas** ← KRITICKÉ, musí být přesný
   - Reserve price (nepovinné)
   - Google Sheet URL (webhook Apps Script)
5. Kliknout **Vytvořit / Uložit aukci**
6. V seznamu aukcí vlevo se zobrazí nová aukce → kliknout na ni → zkontrolovat Detail

### Krok 2C — Vytvořit složku veřejné stránky

1. Zkopírovat složku poslední aukce (nebo `aukce_TEMPLATE.html`)
2. Přejmenovat na `YYYYMMDD_AUK-XXX_Znacka_Model` (např. `20260601_AUK-002_Skoda_Octavia`)
3. Do podsložky `img\` nakopírovat fotky jako `foto_01.jpg`, `foto_02.jpg`, …

### Krok 2D — Upravit AUCTION_CONFIG v index.html

Otevřít `index.html` v textovém editoru. Na začátku skriptu je blok `AUCTION_CONFIG` — upravit:

```javascript
const AUCTION_CONFIG = {
  auctionId:    'AUK-XXX',           // stejné ID jako v admin panelu
  make:         'Škoda',
  model:        'Octavia',
  year:         2022,
  km:           85000,
  color:        'Černá metalíza',
  startPrice:   250000,
  minIncrement: 1000,
  endTime:      '2026-06-10T18:00:00',  // PŘESNÝ čas — stejný jako v admin panelu
  auctionRef:   'SAUTO-XXXXXXX',
  photos: ['img/foto_01.jpg','img/foto_02.jpg'],  // přesný seznam fotek
  // ...
};
```

⚠️ **Pravidlo endTime:** hodnota v `AUCTION_CONFIG` je jen fallback. Firebase endTime má vždy přednost. Ale musí souhlasit — zadat stejný čas na obou místech.

### Krok 2E — Upload na GitHub Pages

1. V `auto1\` spustit `upload_aukce.bat` dvojklikem
2. Počkat na dokončení (výpis v CMD okně)
3. Ověřit živou URL: `https://batkodigitalai.github.io/batko-digital-ai/nabidky/SLOZKA/index.html`
4. Zkontrolovat: countdown běží (odpočítává sekundy), načítají se bidy z Firebase

---

## FÁZE 3 — PRŮBĚH AUKCE

### Sledování příhozů

- Otevřít `aukce_admin.html` lokálně
- Kliknout na aukci vlevo → Detail
- Bidy se aktualizují každých 5 sekund automaticky
- Tabulka zobrazuje: pořadí, jméno, e-mail, telefon, nabídka, čas

### Smazání neplatného příhozu

Nastane pokud někdo zadá text místo čísla (označeno ⚠ červeně):
1. Admin panel → Detail aukce
2. V tabulce příhozů posunout doprava (scroll) → poslední sloupec je 🗑
3. Kliknout 🗑 u neplatného řádku → potvrdit dialog
4. Příhoz se smaže přímo z Firebase

### Prodloužení aukce

1. Admin panel → Detail → sekce **Nová aukce / upravit** (vlevo)
2. Změnit pole **Konec aukce** na nový čas
3. Kliknout **Vytvořit / Uložit** → Firebase se aktualizuje
4. Veřejná stránka načte nový endTime do 5 sekund (polling)
5. **Není třeba nový upload** — endTime se čte z Firebase

### Zrušení aukce

1. Admin panel → Detail → tlačítko 🚫 **Zrušit aukci**
2. Zadat důvod (zobrazí se zákazníkům)
3. Veřejná stránka zobrazí zrušení do 4 sekund

---

## FÁZE 4 — UKONČENÍ AUKCE

### Krok 4A — Ukončit v admin panelu

1. Admin panel → Detail → tlačítko 🏁 **Ukončit a vybrat vítěze**
2. Systém zkontroluje reserve price:
   - Pokud nejvyšší bid < reserve → aukce se automaticky zruší
   - Pokud OK → zobrazí se vítěz s kontakty
3. Kontakty vítěze se zapíší do Google Sheet (stav: ČEKÁ NA SCHVÁLENÍ)
4. Zobrazí se panel oznámení s předvyplněnou zprávou vítězi

### Krok 4B — Kontaktovat vítěze (PŘED odesláním zprávy)

⚠️ Zprávu vítězi NEODESÍLAT bez schválení. Postup:
1. Zavolat vítězi na telefon (číslo vidíš v admin panelu)
2. Potvrdit zájem a zálohu (10 000 Kč)
3. Teprve po telefonním potvrzení odeslat zprávu přes panel

### Krok 4C — Export pro archiv

Admin panel → Detail → 📥 **Export bidů (CSV)**  
Uložit CSV do složky aukce jako `bidy_export_AUK-XXX.csv`

---

## FÁZE 5 — PO AUKCI

### Co NEZAHAJOVAT v evropské aukci bez:
- [ ] Telefonního potvrzení vítěze
- [ ] Přijaté zálohy 10 000 Kč
- [ ] Zkontrolování reserve price splnění

### Archivace

Složku aukce nechat na místě — GitHub Pages URL zůstane funkční jako archiv.

---

## ZNÁT NAZPAMĚŤ — Časté chyby

| Chyba | Příčina | Řešení |
|-------|---------|--------|
| Countdown ukazuje 31 dní místo správného času | `endTime` v `index.html` je špatný (hardcoded) | Firebase endTime má přednost — zkontrolovat admin panel, správný čas tam uložit |
| Countdown se zobrazí ale nezmenšuje | JS chyba v `initExtras` zastavila skript před `setInterval` | Otevřít F12 konzoli, najít chybu, opravit null-check |
| Admin panel DEMO režim (žlutý) | Firebase nedostupný nebo blokovaný | Zkontrolovat internet, otevřít jako `file:///` (ne přes server) |
| Tlačítko 🗑 není vidět | Tabulka je příliš široká, sloupec je mimo obrazovku | Scrollovat tabulku doprava |
| Příhoz neprojde — „neplatná částka" | Uživatel zadal text nebo neplatné číslo | Smazat příhoz přes 🗑 v admin panelu |

---

## TECHNICKÉ DETAILY (pro debugování)

### Proč REST API, ne Firebase SDK?
Firebase JS SDK selhává z `file:///` (blokuje WebSocket). Admin panel proto používá výhradně `fetch()` na Firebase REST endpoints.

### Firebase struktura
```
/auctions/AUK-XXX/
  make, model, year, km, color
  startPrice, minIncrement, endTime
  reservePrice, sheetUrl
  status: active | ended | cancelled
  cancelReason
  winner: { name, email, phone, amount }
  /bids/PUSH_ID: { name, email, phone, amount, timestamp }
```

### Upload skript
`upload_aukce.bat` — volá `scripts\upload_single_folder_to_github.js`  
Nahraje složku `aukce_system\20260529_AUK-TEST-001_VW_Passat_2023\` na GitHub Pages.  
Pro novou aukci: upravit cestu ke složce ve skriptu nebo vytvořit nový .bat.

---

## AKTUÁLNÍ STAV SYSTÉMU (2026-05-30)

| Aukce | Auto | Stav | Nejvyšší bid | Konec |
|-------|------|------|-------------|-------|
| AUK-TEST-001 | VW Passat Variant 2023 | active | 423 500 Kč | 30.5.2026 08:25 |

**Živá URL:** https://batkodigitalai.github.io/batko-digital-ai/nabidky/20260529_AUK-TEST-001_VW_Passat_2023/index.html
