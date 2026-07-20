# SOP: OPENLANE aukce + investor brief vždy ve dvojici

Používat pro každé auto, kde má vzniknout investor výstup i veřejně sdílitelná aukce.

## Princip

Nikdy nevyrábět jen jeden HTML soubor ručně. Vždy vzniká pár:

- `AUK-XXX` hlavní aukční stránka ve stylu AUK-018,
- `AUK-XXXB` investor brief.

Jediný zdroj pravdy je JSON:

`data/openlane_auction_pairs/AUK-XXX_*.json`

## Povinný postup pro Codex / Cowork

1. Ověřit auto v přihlášeném evropském zdroji.
2. Ověřit `bidpriceinfo`, `transportoptions`, report/poškození a fotky.
3. Stáhnout skutečné fotky auta do lokální složky `img/`.
4. Vyplnit nebo zkopírovat JSON v `data/openlane_auction_pairs/`.
5. Spustit generátor:

```powershell
python scripts/create_openlane_auction_pair.py --data data/openlane_auction_pairs/AUK-019_golf.json
```

Pokud se opravuje existující výstup:

```powershell
python scripts/create_openlane_auction_pair.py --data data/openlane_auction_pairs/AUK-019_golf.json --force
```

6. Lokálně otevřít oba `index.html`.
7. Nahrát obě verze jedním batch souborem:

```powershell
.\NAHRAT_AUK019_OBA_GITHUB.bat
```

8. Ověřit veřejné URL přes HTTP `200`.

## Co se nesmí

- Nepřepisovat jen hlavní aukci bez briefu.
- Nepoužívat DEKRA fotky jako hlavní galerii, když existují skutečné zdrojové fotky.
- Nenechat ve složce staré texty předchozí aukce (`AUK-018`, staré ID, starý model).
- Nenahrávat zbytečné nepoužité obrázky na GitHub.
- Nepublikovat výstup, pokud nesedí počet fotek v `AUCTION_CONFIG.photos` proti disku.

## Kontrolní příkazy

```powershell
rg -n "AUK-018|Kodiaq|11261643|Ã|�|Â" aukce_system\YYYYMMDD_AUK-XXX_*\*.html
Get-ChildItem aukce_system\YYYYMMDD_AUK-XXX_*\img -Filter foto_*.jpg | Measure-Object
```

## Výsledek

Pro každé auto musí existovat:

- lokální složka hlavní aukce,
- lokální složka investor briefu,
- upload `.bat` pro obě složky,
- veřejný odkaz na hlavní aukci,
- veřejný odkaz na investor brief.
