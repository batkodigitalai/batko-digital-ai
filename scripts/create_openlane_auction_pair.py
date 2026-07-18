#!/usr/bin/env python3
"""
Create both outputs for one OPENLANE opportunity:
  - AUK-XXX main auction page, based on the proven AUK-018 style.
  - AUK-XXXB investor brief, rendered from the same data JSON.

Usage:
  python scripts/create_openlane_auction_pair.py --data data/openlane_auction_pairs/AUK-019_golf.json
  python scripts/create_openlane_auction_pair.py --data data/openlane_auction_pairs/AUK-019_golf.json --force
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import stat
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUCTION_TEMPLATE = ROOT / "aukce_system" / "20260717_AUK-018_Skoda_Kodiaq_2022_Tour_4x4_200hp"
MAIN_STALE_PATTERNS = ("AUK-018", "11261643", "Kodiaq", "TMBLN7NS", "461644", "740000", "749000")
COMPANY_PROFILE = {
    "brand": "BATKO.DIGITAL.AI",
    "legal_name": "Ing. Jaroslav Batko-Linet",
    "ico": "14600153",
    "dic": "CZ5912280418",
    "address": "Lískovec 170, 273 51 Velké Přítočno, Česká republika",
    "phone": "+420 725 360 151",
    "email": "batko.digital.ai@gmail.com",
}


def kc(value: float | int) -> str:
    return f"{round(value):,}".replace(",", " ") + " Kč"


def pct(value: float) -> str:
    return f"{value:.1f}".replace(".", ",") + " %"


def js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def js_object(mapping: dict[str, str], indent: str = "    ") -> str:
    lines = []
    items = list(mapping.items())
    for i, (key, value) in enumerate(items):
        comma = "," if i < len(items) - 1 else ""
        lines.append(f"{indent}{js_string(key)}: {js_string(value)}{comma}")
    return "{\n" + "\n".join(lines) + "\n  }"


def load_data(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    required = [
        "auction_id", "date", "slug", "source_id", "make", "model", "year",
        "engine", "transmission", "km", "color", "end_time", "start_price_czk",
        "market_price_czk", "market_price_net_czk", "european_cost_czk",
        "bidder_prep_cost_czk", "photo_dir", "photo_glob", "risks", "specs"
    ]
    missing = [k for k in required if k not in data]
    if missing:
        raise SystemExit(f"Missing required JSON fields: {', '.join(missing)}")
    return data


def reset_dir(path: Path, force: bool) -> None:
    if path.exists():
        if not force:
            raise SystemExit(f"Refusing to overwrite existing folder without --force: {path}")
        def clear_readonly(func, target, _exc):
            os.chmod(target, stat.S_IWRITE)
            func(target)
        shutil.rmtree(path, onexc=clear_readonly)
    path.mkdir(parents=True)


def copy_photos(data: dict, target_img: Path) -> list[str]:
    src_dir = (ROOT / data["photo_dir"]).resolve()
    photos = sorted(src_dir.glob(data.get("photo_glob", "foto_*.jpg")))
    if not photos:
        raise SystemExit(f"No photos found: {src_dir} / {data.get('photo_glob')}")
    target_img.mkdir(parents=True, exist_ok=True)
    result = []
    for i, src in enumerate(photos, 1):
        ext = src.suffix.lower()
        dest_name = f"foto_{i:02d}{ext}"
        shutil.copy2(src, target_img / dest_name)
        result.append(f"img/{dest_name}")
    return result


def copy_docs(data: dict, target_root: Path) -> list[dict]:
    docs = []
    for item in data.get("docs", []):
        src = (ROOT / item["source"]).resolve()
        target = target_root / item["target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        docs.append({
            "label": item["label"],
            "file": item["target"].replace("\\", "/"),
            "icon": item.get("icon", "📄")
        })
    return docs


def render_config(data: dict, photos: list[str], docs: list[dict]) -> str:
    risks = ",\n".join(f"    {js_string(r)}" for r in data["risks"])
    photo_lines = []
    for i in range(0, len(photos), 5):
        photo_lines.append("    " + ",".join(js_string(p) for p in photos[i:i + 5]))
    doc_lines = ",\n".join(
        "    { label: %s, file: %s, icon: %s }" % (
            js_string(d["label"]), js_string(d["file"]), js_string(d.get("icon", "📄"))
        )
        for d in docs
    )
    specs = js_object(data["specs"])
    return f'''var AUCTION_CONFIG = {{
  // -- Identifikace --
  auctionId:    {js_string(data["auction_id"])},
  carId:        {js_string(data["source_id"])},

  // -- Auto --
  make:         {js_string(data["make"])},
  model:        {js_string(data["model"])},
  year:         {int(data["year"])},
  engine:       {js_string(data["engine"])},
  transmission: {js_string(data["transmission"])},
  km:           {int(data["km"])},
  color:        {js_string(data["color"])},

  // -- Aukce -- (BROKER verze: vyvolavaci = porizovaci cena z evropske aukce vc. dovozu, marze drazitele viditelna)
  startPrice:   {int(data["start_price_czk"])},
  minIncrement: {int(data.get("min_increment_czk", 1000))},
  endTime:      {js_string(data["end_time"])},   // konec pred koncem evropske aukce - Firebase endTime ma VZDY prednost
  auctionRef:   {js_string("Evropský aukční zdroj " + str(data["source_id"]))},
  depositNote:  {js_string(data.get("deposit_note", "10 000 Kč"))},
  commissionNote: {js_string(data.get("commission_note", "8 000-12 000 Kč"))},

  // -- Odkaz na detailni _K.html stranku --
  detailPageUrl: "",

  // -- ROI & trzni data --
  roi: {{
    vatPayerMode:   true,
    vatRate:        {float(data.get("vat_rate", 0.21))},
    marketPriceCZ:  {int(data["market_price_czk"])},
    marketPriceNetCZ: {int(data["market_price_net_czk"])},
    extrasLabel:    "Doprava + přepis + příprava + servis bez DPH",
    extrasAmount:   {int(data.get("extras_amount_czk", 38500))},
    processingCostLabel: "Zpracování / provize bez DPH",
    processingCostAmount: {int(data.get("processing_cost_czk", 10000))},
    deliveryDaysMin: {int(data.get("delivery_days_min", 25))},
    deliveryDaysMax: {int(data.get("delivery_days_max", 38))},
    carScore:       {int(data.get("score", 80))},
    scoreLabel:     {js_string(data.get("score_label", "Solidní volba"))},
    commissionMin:  {int(data.get("commission_min", 8000))},
    commissionMax:  {int(data.get("commission_max", 12000))},
    b2bMarketLow:   {int(data.get("market_low_czk", data["market_price_czk"]))},
    b2bSaleTarget:  {int(data["market_price_czk"])},
    b2bDaysSale:    {int(data.get("b2b_days_sale", 30))},
    europeanCost:   {int(data["european_cost_czk"])},
    bidderPrepCost: {int(data["bidder_prep_cost_czk"])}
  }},

  // -- Fotky -- {len(photos)} realnych fotek konkretniho auta
  photos: [
{",\n".join(photo_lines)}
  ],

  // -- Rizika (max 4) --
  risks: [
{risks}
  ],

  // -- Specifikace --
  specs: {specs},

  // -- Firebase --
  firebase: {{
    apiKey:            "AIzaSyCzqE91qCN7CAHYNIlilzkyWLW3zYhlT8s",
    authDomain:        "batko-aukce.firebaseapp.com",
    databaseURL:       "https://batko-aukce-default-rtdb.europe-west1.firebasedatabase.app",
    projectId:         "batko-aukce",
    storageBucket:     "batko-aukce.firebasestorage.app",
    messagingSenderId: "567644084257",
    appId:             "1:567644084257:web:d4a8b172324b3d54092b60"
  }},

  // -- Google Sheet --
  sheetUrl: "https://script.google.com/macros/s/AKfycbwcFA8bRyHnBB_4XlgH5_IMR4IBqUfvTD8vScGZPiuCh0gR5f4Mp_9OjOAw1u3lNEjI/exec",

  // -- Dokumenty ke stazeni --
  documents: [
{doc_lines}
  ]
}};'''


def patch_main_html(target: Path, data: dict, photos: list[str], docs: list[dict]) -> None:
    html_path = target / "index.html"
    html = html_path.read_text(encoding="utf-8")
    new_config = render_config(data, photos, docs)
    html = re.sub(
        r"var AUCTION_CONFIG = \{.*?\n\};",
        new_config,
        html,
        flags=re.S,
        count=1,
    )
    html = html.replace("Ing. Jaroslav Batko – Linet", COMPANY_PROFILE["legal_name"])
    html = html.replace("Klimkovice, Česká republika", COMPANY_PROFILE["address"])
    html = html.replace("| Klimkovice, CZ", f"| DIČ {COMPANY_PROFILE['dic']} | Lískovec 170, 273 51 Velké Přítočno")
    html = html.replace(
        '<div class="cid-row"><span class="cid-label">IČO:</span><span class="cid-val">14600153</span></div>\n'
        f'    <div class="cid-row"><span class="cid-label">Sídlo:</span><span class="cid-val">{COMPANY_PROFILE["address"]}</span></div>',
        '<div class="cid-row"><span class="cid-label">IČO:</span><span class="cid-val">14600153</span></div>\n'
        f'    <div class="cid-row"><span class="cid-label">DIČ:</span><span class="cid-val">{COMPANY_PROFILE["dic"]}</span></div>\n'
        f'    <div class="cid-row"><span class="cid-label">Sídlo:</span><span class="cid-val">{COMPANY_PROFILE["address"]}</span></div>'
    )
    html = html.replace(
        '<div class="cid-row"><span class="cid-label">E-mail:</span><span class="cid-val">batko.digital.ai@gmail.com</span></div>',
        f'<div class="cid-row"><span class="cid-label">E-mail:</span><span class="cid-val">{COMPANY_PROFILE["email"]}</span></div>\n'
        f'    <div class="cid-row"><span class="cid-label">Telefon:</span><span class="cid-val">{COMPANY_PROFILE["phone"]}</span></div>'
    )
    html_path.write_text(html, encoding="utf-8")


def render_tracker(data: dict) -> str:
    profit = int(data["market_price_czk"]) - int(data["european_cost_czk"]) - int(data["bidder_prep_cost_czk"])
    roi_day = (profit / (int(data["european_cost_czk"]) + int(data["bidder_prep_cost_czk"])) * 100 / int(data.get("b2b_days_sale", 30)))
    return f"""<!DOCTYPE html>
<html lang="cs">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sledování ceny - {data['model']} ({data['auction_id']})</title>
<style>body{{font:15px/1.5 Arial,sans-serif;background:#0f1626;color:#eef2f9;padding:20px}}.card{{background:#182238;border-radius:12px;padding:16px;margin:12px 0}}b{{color:#f5a623}}</style></head>
<body>
<h1>Sledování ceny - {data['make']} {data['model']} ({data['auction_id']})</h1>
<div class="card">Zdroj {data['source_id']} · vyvolávací cena {kc(data['start_price_czk'])} · cílový retail {kc(data['market_price_czk'])}</div>
<div class="card">Modelová marže při startu: <b>{kc(profit)}</b> · ROI/den při {data.get('b2b_days_sale', 30)} dnech: <b>{roi_day:.2f} %</b></div>
</body></html>
"""


def render_urls(data: dict, photos: list[str], docs: list[dict]) -> str:
    lines = [
        f"{data['auction_id']} {data['make']} {data['model']}",
        "",
        "Lokální stránka:",
        "index.html",
        "",
        "Dokumenty:",
    ]
    lines += [d["file"] for d in docs] or ["(žádné)"]
    lines += ["", "Market comparison links:"]
    lines += data.get("market_links", [])
    lines += [
        "",
        "Internal source reference:",
        f"Evropský aukční zdroj {data['source_id']}",
        f"Car ID {data.get('car_id', '')}",
        f"VIN {data.get('vin', data['specs'].get('VIN', ''))}",
        "",
        "Ověřené náklady pro default:",
        f"Zdroj + poplatky: {kc(data.get('source_total_czk', data['european_cost_czk']))}",
        f"Doprava: {kc(data.get('delivery_czk', 0))}",
        f"Evropské pořízení včetně dopravy: {kc(data['european_cost_czk'])}",
        f"Vyvolávací cena aukce: {kc(data['start_price_czk'])}",
        f"Náklady dražitele: {kc(data['bidder_prep_cost_czk'])}",
        f"Orientační cílový retail: {kc(data['market_price_czk'])}",
        "",
        f"Počet fotek v galerii: {len(photos)}",
    ]
    return "\n".join(lines) + "\n"


def render_brief(data: dict, brief_photos: list[str], docs: list[dict]) -> str:
    all_in = int(data["european_cost_czk"]) + int(data["bidder_prep_cost_czk"])
    scenarios = [
        ("Rychlý prodej", int(data.get("quick_sale_gross_czk", data["market_low_czk"]))),
        ("Konzervativní trh", int(data.get("market_low_czk", data["market_price_czk"]))),
        ("Standardní retail", int(data["market_price_czk"])),
        ("Horní trh", int(data.get("market_high_czk", data["market_price_czk"]))),
    ]
    rows = []
    for label, gross in scenarios:
        net = gross / (1 + float(data.get("vat_rate", 0.21)))
        profit = net - all_in
        roi = profit / all_in * 100
        rows.append(f"<tr><td>{label}</td><td>{kc(gross)}</td><td>{kc(net)}</td><td>{kc(profit)}</td><td>{pct(roi)}</td></tr>")
    gallery = "".join(
        f'<figure><img src="img/{Path(p).name}" alt="{data["model"]}"><figcaption>Report / stav vozidla</figcaption></figure>'
        for p in brief_photos[:6]
    )
    risks = "".join(f"<li>{r}</li>" for r in data["risks"])
    source_notes = "".join(f"<li>{n}</li>" for n in data.get("source_notes", []))
    doc_links = "".join(f'<a href="{d["file"]}" target="_blank">{d["label"]}</a>' for d in docs)
    market_links = "".join(f'<a href="{u}" target="_blank">Market link</a>' for u in data.get("market_links", []))
    return f"""<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{data['auction_id']}B | {data['make']} {data['model']} | Investor brief</title>
<style>
body{{margin:0;font-family:Arial,sans-serif;background:#f6f8fb;color:#18212f;line-height:1.5}}.wrap{{max-width:1120px;margin:auto;padding:24px}}.hero{{display:grid;grid-template-columns:1.2fr .8fr;gap:20px}}.panel,.card{{background:#fff;border:1px solid #d8dee8;border-radius:8px;padding:20px;box-shadow:0 10px 28px rgba(24,33,47,.08)}}img{{max-width:100%;display:block;border-radius:8px}}h1{{font-size:34px;line-height:1.1;margin:0 0 10px}}h2{{margin:0 0 12px}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:20px 0}}.metric{{background:#fff;border:1px solid #d8dee8;border-radius:8px;padding:14px}}.v{{font-size:22px;font-weight:800}}table{{width:100%;border-collapse:collapse}}td,th{{border-bottom:1px solid #edf1f6;padding:9px;text-align:left}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}}.gallery{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}figcaption{{font-size:12px;color:#657082;padding-top:4px}}.links a{{display:inline-block;margin:4px 8px 4px 0;padding:6px 10px;border:1px solid #d8dee8;border-radius:999px;text-decoration:none;color:#0b5c56;background:white}}@media(max-width:850px){{.hero,.grid,.metrics,.gallery{{grid-template-columns:1fr}}h1{{font-size:28px}}}}
</style>
</head>
<body><main class="wrap">
<section class="hero"><div><img src="img/{Path(brief_photos[0]).name if brief_photos else ''}" alt="{data['model']}"></div><div class="panel"><p><b>{data['auction_id']}B · Investor brief</b></p><h1>{data['make']} {data['model']}</h1><p>{data['year']} · {data['km']:,} km · {data['engine']} · {data['transmission']}</p><p><b>Verdikt:</b> vhodné pouze při disciplíně na bidu a po kontrole nákladů.</p></div></section>
<section class="metrics"><div class="metric"><div>Vyvolávací cena</div><div class="v">{kc(data['start_price_czk'])}</div></div><div class="metric"><div>Evropské pořízení</div><div class="v">{kc(data['european_cost_czk'])}</div></div><div class="metric"><div>All-in kapitál</div><div class="v">{kc(all_in)}</div></div><div class="metric"><div>Cílový retail</div><div class="v">{kc(data['market_price_czk'])}</div></div></section>
<section class="card"><h2>Investor ekonomika</h2><table><thead><tr><th>Scénář</th><th>Hrubá cena</th><th>Bez DPH</th><th>Zisk</th><th>ROI</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>
<section class="grid"><article class="card"><h2>Rizika</h2><ul>{risks}</ul></article><article class="card"><h2>Ověření</h2><ul>{source_notes}</ul></article></section>
<section class="card" style="margin-top:18px"><h2>Fotky z reportu / stavu</h2><div class="gallery">{gallery}</div></section>
<section class="card links" style="margin-top:18px"><h2>Zdroje</h2>{doc_links}{market_links}</section>
<footer style="margin-top:18px;color:#657082;font-size:12px">Vytvořeno generátorem OPENLANE Auction Pair Factory. Nejde o garanci zisku ani právní nebo daňové doporučení.</footer>
</main></body></html>
"""


def create_upload_bat(data: dict, main_folder: str, brief_folder: str) -> None:
    aid = data["auction_id"]
    path = ROOT / f"NAHRAT_{aid.replace('-', '')}_OBA_GITHUB.bat"
    text = f"""@echo off
chcp 65001 >nul
title auto1 :: Nahrat obe verze {aid} na GitHub Pages
cd /d "%~dp0"

echo [1/2] Nahravam hlavni aukci {aid}...
python scripts\\upload_github_folder.py --folder "aukce_system\\{main_folder}" --remote-path "aukce_system/{main_folder}"
if errorlevel 1 goto error

echo [2/2] Nahravam investor brief {aid}B...
python scripts\\upload_github_folder.py --folder "aukce_system\\{brief_folder}" --remote-path "aukce_system/{brief_folder}"
if errorlevel 1 goto error

echo Hotovo.
echo Hlavni aukce:
echo https://batkodigitalai.github.io/batko-digital-ai/aukce_system/{main_folder}/index.html
echo Investor brief:
echo https://batkodigitalai.github.io/batko-digital-ai/aukce_system/{brief_folder}/index.html
pause
exit /b 0

:error
echo CHYBA: Upload se nepovedl.
pause
exit /b 1
"""
    path.write_text(text, encoding="utf-8")


def validate(main: Path, brief: Path, photos: list[str], data: dict) -> None:
    html = (main / "index.html").read_text(encoding="utf-8")
    photo_refs = re.findall(r'"img/foto_\d+\.[a-z]+"', html)
    disk_photos = sorted((main / "img").glob("foto_*.*"))
    if len(photo_refs) != len(disk_photos) or len(disk_photos) != len(photos):
        raise SystemExit(f"Photo mismatch: config={len(photo_refs)} disk={len(disk_photos)} expected={len(photos)}")
    stale = [p for p in MAIN_STALE_PATTERNS if p in html]
    if stale:
        raise SystemExit(f"Stale template strings in main HTML: {stale}")
    for rel in photos:
        if not (main / rel).exists():
            raise SystemExit(f"Missing photo: {rel}")
    if not (brief / "index.html").exists():
        raise SystemExit("Missing brief index.html")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    data = load_data((ROOT / args.data).resolve() if not args.data.is_absolute() else args.data)

    main_folder = f"{data['date']}_{data['auction_id']}_{data['slug']}"
    brief_folder = f"{data['date']}_{data['auction_id']}B_{data.get('brief_slug', data['slug'] + '_Investor_Brief')}"
    main_dir = ROOT / "aukce_system" / main_folder
    brief_dir = ROOT / "aukce_system" / brief_folder

    reset_dir(main_dir, args.force)
    shutil.copytree(AUCTION_TEMPLATE, main_dir, dirs_exist_ok=True)
    for item in main_dir.iterdir():
        if item.is_file() and item.name.startswith("STAHNI_FOTKY_AUK"):
            item.unlink()
    shutil.rmtree(main_dir / "img", ignore_errors=True)
    photos = copy_photos(data, main_dir / "img")
    docs = copy_docs(data, main_dir)
    patch_main_html(main_dir, data, photos, docs)
    (main_dir / "tracker.html").write_text(render_tracker(data), encoding="utf-8")
    (main_dir / "urls.txt").write_text(render_urls(data, photos, docs), encoding="utf-8")

    reset_dir(brief_dir, args.force)
    (brief_dir / "img").mkdir(parents=True)
    brief_photos = []
    for src_text in data.get("brief_gallery", []):
        src = (ROOT / src_text).resolve()
        dest = brief_dir / "img" / src.name
        shutil.copy2(src, dest)
        brief_photos.append(f"img/{src.name}")
    docs_brief = copy_docs(data, brief_dir)
    (brief_dir / "index.html").write_text(render_brief(data, brief_photos, docs_brief), encoding="utf-8")
    (brief_dir / "urls.txt").write_text(render_urls(data, brief_photos, docs_brief), encoding="utf-8")

    create_upload_bat(data, main_folder, brief_folder)
    validate(main_dir, brief_dir, photos, data)

    print("OK created:")
    print(f"  {main_dir}")
    print(f"  {brief_dir}")
    print(f"  {ROOT / ('NAHRAT_' + data['auction_id'].replace('-', '') + '_OBA_GITHUB.bat')}")


if __name__ == "__main__":
    main()
