# Mercedes-Benz GLC 300d AMG Line 4MATIC — landing page

Statická landing page pro prodej **konkrétního zánovního vozu** Mercedes-Benz GLC 300d AMG Line 4MATIC
přes obchodní model **„VIP dovoz s pevnou konečnou cenou"** (Master SOP, Model 1).

> **Konečná cena: 1 307 233 Kč včetně 21 % DPH** — absolutně fixní, all-inclusive, bez skrytých poplatků.

## Co stránka komunikuje

1. **Hero** — headline + klíčové parametry + cenová karta s fixní cenou + 2× CTA (formulář + Calendly)
2. **VIP dovoz — co dostáváte v ceně** — 4 pilíře (pevná cena · přenos rizika · all-inclusive · transparentnost)
3. **Specifikace vozu** — 4 karty (motor, identita/VIN, výbava, pořizovací kontext)
4. **Stav vozu — radikální transparentnost** — explicitní přiznání drobné vady (škrábanec pravých dveří), původ z NL / autoDATAexperts, Cebia po dovozu
5. **Fotogalerie** — aktuálně placeholdery, fotky doplnit po finálním detailingu
6. **Kontakt** — telefon, e-mail, Calendly + nezávazný formulář s validací
7. **Footer** — IČ/DIČ, sídlo, sociální sítě

## Klíčová data vozu (single source of truth)

| Atribut | Hodnota |
|---|---|
| Značka / model | Mercedes-Benz GLC 300d Edition AMG Line 4MATIC |
| VIN | W1NKM0HB3TF430120 |
| 1. registrace | 25. 09. 2025 |
| Najeto | 17 160 km |
| Motor | 2.0 diesel, 1 993 ccm, 198 kW / 270 k |
| Převodovka | 9G-TRONIC automat |
| Pohon | 4MATIC (4×4) |
| HU (TÜV) platná do | 09/2027 |
| Země poslední registrace | Nizozemsko |
| Gross list price | 74 125,10 € |
| DPH | lze odpočíst (VAT can be shown) |
| Drobná vada | 1× škrábanec pravých předních dveří |
| **Prodejní cena** | **1 307 233 Kč včetně 21 % DPH** (kurz 24,5 Kč/€) |

## Technologie

| Vrstva | Stack |
|---|---|
| Struktura | HTML5 (semantické tagy, ARIA tam, kde dává smysl) |
| Styly | Vanilla CSS, CSS custom properties, CSS Grid + Flexbox |
| Logika | Vanilla JavaScript (žádné frameworky, žádné externí knihovny) |
| Build | Žádný build step — soubory se nasazují tak, jak jsou |

### Barevné tokeny

| Token | Hex | Použití |
|---|---|---|
| `--primary` | `#00a3e0` | Akční prvky, odkazy, primární tlačítka |
| `--secondary` | `#1a1a1a` | Hero, footer, nadpisy |
| `--accent` | `#ffd700` | Highlight (badge, cenová karta border-top) |

## Jak spustit lokálně

```bash
# 1) Nejjednodušší — otevřít v prohlížeči přímo
start index.html      # Windows

# 2) Lokální HTTP server (Python 3)
python -m http.server 8000
#    a otevřít http://localhost:8000

# 3) Live-server (Node.js)
npx live-server
```

## Struktura souborů

```
mercedes-glc-landing/
├── index.html      # HTML struktura + obsah
├── style.css       # Veškeré styly (v2)
├── script.js       # Smooth scroll, header shadow, form validace
├── README.md       # Tento soubor
└── .gitignore
```

## TODO před spuštěním (live)

> Tyto věci jsou **blokující pro publikování** — neřešit „někdy".

- [ ] **Calendly URL ověřit.** V index.html i ve footeru je použit `https://calendly.com/batko-digital-ai` (odhad). Pokud máš jinou cestu (např. `/d/xxx/30min`), opravit na 3 místech (hero CTA, kontakt sekce, footer).
- [ ] **Fotky.** Aktuálně 6 šedých placeholderů v `gallery-grid`. Doplnit po finálním detailingu — ideálně `img/01.jpg`–`img/06.jpg` (cca 1600×1200 px, JPG ~80 % kvalita). Pak v `index.html` přepsat `<div class="gallery-item">` na `<img>`.
- [ ] **Formulář backend.** Aktuálně `script.js` jen předstírá odeslání. Napojit na **Formspree**, **Web3Forms**, nebo vlastní endpoint. Cílový e-mail: `batko.digital.ai@gmail.com`.
- [ ] **Cebia report.** Po fyzickém dovozu doplnit do sekce „Stav vozu" — buď samostatnou kartu, nebo PDF k stažení.
- [ ] **GDPR / Zásady zpracování OÚ.** Footer dnes obsahuje jen základní legal info. Pro plnou GDPR compliance doplnit link na samostatnou stránku „Zásady zpracování osobních údajů".
- [ ] **Open Graph image.** Pro pěkné náhledy na sociálních sítích přidat `<meta property="og:image" content="...">`.
- [ ] **Favicon.** Aktuálně chybí.

## Back-end strategie (mimo landing page)

Tato landing page je **front-end**. Obchodní procesy okolo (D+7 / D+14 / D+21 pricing model, lead nurturing, CRM napojení) řešíme jinde — tato stránka jen zachytává leady a posílá je dál.

## Deployment

Publikováno přes **GitHub Pages** v rámci monorepa
[`batkodigitalai/batko-digital-ai`](https://github.com/batkodigitalai/batko-digital-ai)
v cestě `40_OUTPUT/mercedes-glc-landing/`.

Po push-i na `main` bude stránka dostupná na:
`https://batkodigitalai.github.io/batko-digital-ai/40_OUTPUT/mercedes-glc-landing/`

## Licence a odpovědnost

Mercedes-Benz a GLC jsou registrované ochranné známky Mercedes-Benz Group AG.
Tato stránka **není oficiální stránkou výrobce** — slouží pouze k prodeji jednoho konkrétního vozu.

Data o stavu vozu pochází z externí databáze **autoDATAexperts (DAT)** — nikoli z vlastní inspekce.
Cebia report bude doplněn po fyzickém dovozu vozu do ČR.
