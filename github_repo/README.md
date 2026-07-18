# auto — lead pages pro dovoz aut z evropských aukcí

Sada landing pages pro generování poptávek na analýzu a dovoz aut z evropských aukcí (DAT-Auction, Bca, Manheim, ADAC, autobid.de, auto1, OpenLane, eCarsTrade a další).

**Provozovatel:** Ing. Jaroslav Batko-Linet, Lískovec 170, 273 51 Velké Přítočno
**Kontakt:** batko.digital.ai@gmail.com
**Web:** nemanahi.cz

## Co tento repozitář obsahuje

```
pages/
├── landing_B2B.html          # Pro malé autobazary (1–5 aut/měs)
├── landing_B2C.html          # Pro koncové zájemce o auto
└── mercedes_GLC300d.html     # Konkrétní vůz — Mercedes-Benz GLC 300d

apps_script/
└── lead_webhook.gs           # Sdílený backend (Google Apps Script)

docs/
├── HOW_TO_ADD_NEW_LANDING.md # Návod: nová stránka za 5 minut
└── GOOGLE_SHEET_SETUP.md     # Setup Google Sheet + Apps Script

assets/
├── config.example.js         # Šablona konfigurace (URL backendu)
└── shared.css                # Společné styly (volitelné)
```

## Architektura (jak to funguje)

```
[Návštěvník] → [HTML stránka] → [vyplní formulář]
                                       ↓
                                       fetch POST
                                       ↓
                        [Google Apps Script webhook]
                                       ↓
                            ┌──────────┴──────────┐
                            ↓                     ↓
                    [Google Sheet]       [Email notifikace tobě]
                    všechny leady           +
                    sloupec `source`     [Auto-responder klientovi]
                    je segmentuje
```

**Jedno backend řešení obsluhuje VŠECHNY stránky.** Každá stránka posílá `source=...` (např. `mercedes_glc300d`, `B2B_autobazary`, `B2C_koncovi`). V sheetu pak filtruješ podle zdroje.

## Lokální spuštění

Otevři libovolnou HTML stránku v `pages/` dvojklikem. To je vše — žádný build, žádný server.

**Před spuštěním:** Zkopíruj `assets/config.example.js` → `assets/config.js` a vlož svou Apps Script URL (viz `docs/GOOGLE_SHEET_SETUP.md`).

## Bezpečnost

- ❌ `assets/config.js` (skutečná Apps Script URL) **NIKDY** necommituj do PUBLIC repa — je v `.gitignore`
- ✅ V repu zůstává `config.example.js` s placeholderem
- ✅ Pokud klonuje někdo jiný, formulář prostě nefunguje (URL chybí), ale stránka se zobrazí

## Licence

MIT — viz `LICENSE`. Můžeš použít a upravit.

## Pomohlo? Podělte se

Pokud používáš tento template pro vlastní lead pages, dej hvězdičku ⭐ na GitHubu nebo se ozvi.
