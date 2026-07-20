from __future__ import annotations

import json
from pathlib import Path


BASE = Path(r"C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1")
TEMPLATE = BASE / "aukce_system" / "aukce_TEMPLATE.html"
OUT_DIR = BASE / "aukce_system" / "20260710_AUK-015_Skoda_Kodiaq_2022_Tour_4x4_200hp"
OUT_HTML = OUT_DIR / "index.html"


config = {
    "auctionId": "AUK-015",
    "carId": "11226595",
    "make": "Skoda",
    "model": "Kodiaq 2.0 TDI Tour 4x4",
    "year": 2022,
    "engine": "2.0 TDI 147 kW / 200 hp",
    "transmission": "DSG automat 7st.",
    "km": 61306,
    "color": "\u0160ed\u00e1 metal\u00edza",
    "startPrice": 590000,
    "minIncrement": 1000,
    "endTime": "2026-07-12T20:30:00+02:00",
    "auctionRef": "OPENLANE-11226595",
    "depositNote": "10 000 K\u010d",
    "commissionNote": "10 000-15 000 K\u010d",
    "detailPageUrl": "https://www.openlane.eu/cs/car/info?auctionId=11226595",
    "roi": {
        "vatPayerMode": True,
        "vatRate": 0.21,
        "marketPriceCZ": 749000,
        "marketPriceNetCZ": 619008,
        "extrasLabel": "Doprava + p\u0159ihl\u00e1\u0161en\u00ed + p\u0159\u00edprava + brzdy + kosmetika bez DPH",
        "extrasAmount": 71125,
        "processingCostLabel": "Zpracov\u00e1n\u00ed / provize bez DPH",
        "processingCostAmount": 12000,
        "deliveryDaysMin": 26,
        "deliveryDaysMax": 39,
        "carScore": 78,
        "scoreLabel": "Siln\u00fd kandid\u00e1t p\u0159i n\u00edzk\u00e9m n\u00e1kupu",
        "commissionMin": 10000,
        "commissionMax": 15000,
        "b2bMarketLow": 602479,
        "b2bSaleTarget": 619008,
        "b2bDaysSale": 30,
    },
    "photos": [f"img/foto_{i:02d}.jpg" for i in range(1, 18)],
    "risks": [
        "Auto nen\u00ed je\u0161t\u011b koupen\u00e9; jde o \u010deskou p\u0159edaukci nav\u00e1zanou na dostupnost v OPENLANE. Pokud se v evropsk\u00e9 aukci cena zvedne nad limit, obchod se mus\u00ed zastavit nebo potvrdit znovu.",
        "OPENLANE profil ukazuje 1 kl\u00ed\u010d, DEKRA report zmi\u0148uje 2 hlavn\u00ed kl\u00ed\u010de. Pro kalkulaci po\u010d\u00edtat rad\u011bji s hor\u0161\u00ed variantou a rozpor ov\u011b\u0159it p\u0159i p\u0159evzet\u00ed.",
        "DEKRA uv\u00e1d\u00ed t\u0159i neakceptovan\u00e9 vady: \u0161kr\u00e1banec lev\u00e9ho zadn\u00edho boku, sjet\u00e9 zadn\u00ed brzdov\u00e9 desti\u010dky a d\u016flek na prav\u00fdch zadn\u00edch dve\u0159\u00edch.",
        "Servis je digit\u00e1ln\u00ed a posledn\u00ed servis prob\u011bhl 07.05.2026 p\u0159i 60 317 km, ale OPENLANE profil z\u00e1rove\u0148 uv\u00e1d\u00ed z\u00e1znam o \u00fadr\u017eb\u011b jako nedostupn\u00fd. Report m\u00e1 p\u0159ednost, rozpor je nutn\u00e9 dr\u017eet v pozn\u00e1mce.",
    ],
    "specs": {
        "Rok / prvn\u00ed registrace": "2022 / 01.06.2022",
        "Najeto": "61 306 km",
        "Motor": "2.0 TDI 147 kW (200 hp)",
        "Pohon": "4x4",
        "P\u0159evodovka": "DSG automat 7st.",
        "Palivo": "Diesel / Euro 6d",
        "Karoserie": "SUV, 5 m\u00edst",
        "Barva": "\u0160ed\u00e1",
        "VIN": "TMBLN7NS4N8045985",
        "STK / HU": "do 06/2027",
        "Pneumatiky": "Hankook Ventus S1 evo2 SUV, 235/50 R19, 6 mm v\u0161echny",
        "Servis": "digit\u00e1ln\u00ed, posledn\u00ed 07.05.2026 p\u0159i 60 317 km",
        "Zn\u00e1m\u00e9 vady": "zadn\u00ed brzdy, \u0161kr\u00e1banec lev\u00fd zadn\u00ed bok, d\u016flek prav\u00e9 zadn\u00ed dve\u0159e",
        "Dod\u00e1n\u00ed": "bude potvrzeno podle c\u00edlov\u00e9 adresy v OPENLANE; orienta\u010dn\u011b 10 968-13 625 K\u010d bez DPH",
        "Zdroj": "OPENLANE aukce 11226595, Moenchengladbach DE",
    },
    "firebase": {
        "apiKey": "AIzaSyCzqE91qCN7CAHYNIlilzkyWLW3zYhlT8s",
        "authDomain": "batko-aukce.firebaseapp.com",
        "databaseURL": "https://batko-aukce-default-rtdb.europe-west1.firebasedatabase.app",
        "projectId": "batko-aukce",
        "storageBucket": "batko-aukce.firebasestorage.app",
        "messagingSenderId": "567644084257",
        "appId": "1:567644084257:web:d4a8b172324b3d54092b60",
    },
    "sheetUrl": "https://script.google.com/macros/s/AKfycbwcFA8bRyHnBB_4XlgH5_IMR4IBqUfvTD8vScGZPiuCh0gR5f4Mp_9OjOAw1u3lNEjI/exec",
    "documents": [
        {
            "label": "DEKRA Zustandsbericht - ref 11226595",
            "file": "docs/dekra_zustandsbericht_11226595.pdf",
            "icon": "PDF",
        },
        {
            "label": "Fotoanlage DEKRA - ref 11226595",
            "file": "docs/fotoanlage_11226595.pdf",
            "icon": "PDF",
        },
        {
            "label": "COC / dokumenty - ref 11226595",
            "file": "docs/coc_11226595.pdf",
            "icon": "PDF",
        },
    ],
}


def to_js(value, indent: int = 0) -> str:
    space = " " * indent
    child = " " * (indent + 2)
    if isinstance(value, dict):
        lines = ["{"]
        for key, item in value.items():
            lines.append(f"{child}{json.dumps(key, ensure_ascii=False)}: {to_js(item, indent + 2)},")
        lines.append(f"{space}}}")
        return "\n".join(lines)
    if isinstance(value, list):
        lines = ["["]
        for item in value:
            lines.append(f"{child}{to_js(item, indent + 2)},")
        lines.append(f"{space}]")
        return "\n".join(lines)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


html = TEMPLATE.read_text(encoding="utf-8")
replacement = (
    "<!-- =============================================================\n"
    "     KONFIGURACE AUK-015 - Skoda Kodiaq 2.0 TDI Tour 4x4 200 hp 2022\n"
    "     ============================================================= -->\n"
    "<script>\n"
    f"var AUCTION_CONFIG = {to_js(config)};\n"
    "</script>"
)

var_start = html.find("var AUCTION_CONFIG")
if var_start == -1:
    raise RuntimeError("AUCTION_CONFIG block not found")
comment_start = html.rfind("<!--", 0, var_start)
script_end = html.find("</script>", var_start)
if comment_start == -1 or script_end == -1:
    raise RuntimeError("AUCTION_CONFIG block boundaries not found")
script_end += len("</script>")
html = html[:comment_start] + replacement + html[script_end:]

html = html.replace(
    "Internetov\u00e1 aukce vozidla",
    "Internetov\u00e1 aukce vozidla - dostupnost podle OPENLANE",
    1,
)
html = html.replace(
    '<div class="cid-row"><span class="cid-label">S\u00eddlo:</span><span class="cid-val">Klimkovice, \u010cesk\u00e1 republika</span></div>',
    '<div class="cid-row"><span class="cid-label">S\u00eddlo:</span><span class="cid-val">L\u00edskovec 170, 273 51 Velk\u00e9 P\u0159\u00edto\u010dno, \u010cesk\u00e1 republika</span></div>',
)
html = html.replace("| Klimkovice, CZ", "| DI\u010c CZ5912280418 | L\u00edskovec 170, 273 51 Velk\u00e9 P\u0159\u00edto\u010dno")

OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_HTML.write_text(html, encoding="utf-8")
print(OUT_HTML)
