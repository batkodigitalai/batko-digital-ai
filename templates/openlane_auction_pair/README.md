# OPENLANE Auction Pair Factory

Tento balíček drží opakovatelnou výrobu dvou výstupů pro jedno auto:

1. `AUK-XXX` - hlavní aukční stránka ve stylu AUK-018.
2. `AUK-XXXB` - investor brief / auditní přehled.

Jediný zdroj pravdy je JSON v `data/openlane_auction_pairs/`. Neopisovat ručně čísla do dvou HTML.

## Rychlý postup

```powershell
python scripts/create_openlane_auction_pair.py --data data/openlane_auction_pairs/AUK-019_golf.json
.\NAHRAT_AUK019_OBA_GITHUB.bat
```

## Povinné před generováním

- Ověřit přihlášený OPENLANE detail.
- Ověřit `bidpriceinfo` pro cílový bid.
- Ověřit `transportoptions`.
- Stáhnout skutečné fotky auta do složky v `img/`.
- Přiložit DEKRA/report PDF, pokud existuje.
- Nepoužívat DEKRA fotky jako hlavní galerii, pokud jsou dostupné skutečné zdrojové fotky.

## Výstupy

Generátor vytvoří:

- `aukce_system/YYYYMMDD_AUK-XXX_<slug>/index.html`
- `aukce_system/YYYYMMDD_AUK-XXX_<slug>/tracker.html`
- `aukce_system/YYYYMMDD_AUK-XXX_<slug>/urls.txt`
- `aukce_system/YYYYMMDD_AUK-XXX_<slug>/img/*`
- `aukce_system/YYYYMMDD_AUK-XXX_<slug>/docs/*`
- `aukce_system/YYYYMMDD_AUK-XXXB_<brief_slug>/index.html`
- `aukce_system/YYYYMMDD_AUK-XXXB_<brief_slug>/urls.txt`
- `NAHRAT_AUKXXX_OBA_GITHUB.bat`

## Bezpečnost

Generátor odmítne přepsat existující složku bez `--force`.
Po vytvoření automaticky kontroluje:

- počet fotek v `AUCTION_CONFIG.photos` proti souborům v `img/`,
- staré texty typu předchozího `AUK-018`, starý zdrojový ID nebo starý model,
- existenci lokálních obrázků a PDF,
- přítomnost upload batch souboru.
