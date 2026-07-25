import streamlit as st
import os
import json
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────────
APP_TITLE    = "AI Visibility Auditor"
APP_LABEL    = "BEZPLATNÝ AI VISIBILITY AUDIT"
APP_SUBTITLE = "Zjistěte za 30 sekund, zda ChatGPT a Gemini doporučují vás — nebo vaši konkurenci."

DEFAULT_ACCESS_CODE          = ""
DEFAULT_PAYMENT_LINK         = "https://buy.stripe.com/YOUR_LINK_HERE"
DEFAULT_TEASER_MODEL         = "gpt-4.1-mini"
DEFAULT_REPORT_MODEL         = "gpt-4.1"
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"
DEFAULT_PRICE_TEXT           = "1 490 Kč vč. DPH"
DEFAULT_UPSELL_PRICE         = "9 900 Kč"

COMPANY_NAME    = "BATKO.DIGITAL.AI"
COMPANY_PERSON  = "Ing. Jaroslav Batko"
COMPANY_ICO     = "14600153"
COMPANY_DIC     = "CZ5912280418"
COMPANY_ADDRESS = "Lískovec 170, 273 51 Velké Přítočno"
COMPANY_PHONE   = "+420 725 360 151"
COMPANY_EMAIL   = "batko.digital.ai@gmail.com"
UPSELL_EMAIL    = COMPANY_EMAIL

# ─── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
<style>
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #f7f5f0 !important;
    color: #13231b !important;
}
[data-testid="stHeader"]     { background: #f7f5f0 !important; border-bottom: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stSidebar"]    { display: none !important; }

button[kind="primary"],
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: #13231b !important;
    color: #f7f5f0 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    padding: .55rem 1.4rem !important;
}
button[kind="primary"]:hover { background: #1e3829 !important; }

.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #13231b !important;
    border: 1.5px solid #13231b !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: #B6452C !important;
    font-weight: 800 !important;
    font-size: 1.9rem !important;
}
[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: .87rem !important; }

.stTextArea textarea,
.stTextInput input {
    background: #faf8f4 !important;
    border: 1.5px solid #d6cfc0 !important;
    border-radius: 8px !important;
    color: #13231b !important;
}

[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1.5px solid #e8e0d0 !important;
    border-radius: 10px !important;
    margin-bottom: .5rem !important;
}
[data-testid="stExpander"] summary { color: #13231b !important; font-weight: 600 !important; }

hr { border-color: #e8e0d0 !important; }

@media (max-width: 640px) {
    [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
}
</style>
"""

DEMO_URL = "https://www.zahradni-nabytek-novak.cz"
DEMO_DESCRIPTION = (
    "Prodáváme ručně vyráběný teakový zahradní nábytek — lavice, jídelní sety a lehátka. "
    "Působíme na Kladensku a rozvážíme po celé ČR. Máme vlastní truhlářskou dílnu, "
    "nábytek děláme na míru a dáváme 7 let záruky na konstrukci. "
    "Web je na WordPressu, ceny od 12 000 do 90 000 Kč."
)


def get_config(name, default=None):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


# ─── OPENAI ────────────────────────────────────────────────────────────────────
def get_openai_client():
    from openai import OpenAI
    key = get_config("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)


PROMPT_A = """Jsi elitní auditor sémantické čitelnosti webu pro AI vyhledávače
(GEO / AEO specialist — Generative Engine Optimization).

Uživatel ti dá URL svého webu a stručný popis toho, co nabízí.
Tvým úkolem je vygenerovat tvrdou, konkrétní a mírně alarmující analýzu toho,
proč ho ChatGPT, Gemini a Perplexity nedoporučují.

Vrať POUZE validní JSON objekt (žádný jiný text, žádné markdown bloky) s těmito klíči:
- "visibility_score": číslo mezi 12 a 34 (nízké = web je pro AI téměř neviditelný)
- "main_barrier": string — jedna zásadní technická/sémantická bariéra, KONKRÉTNĚ pro jeho oboru (max 2 věty, česky)
- "competitor_warning": string — jedna úderná věta o tom, co se děje, když se zákazník zeptá AI na jeho službu (česky)
- "barrier_category": string — jedna z: "Chybějící JSON-LD", "Blokované AI roboty", "Nečitelná struktura obsahu", "Chybějící entita firmy", "Žádný FAQ markup"

Vstup od uživatele:
"""

PROMPT_B = """Jsi světový expert na Generative Engine Optimization (GEO) — optimalizaci webů
pro AI vyhledávače ChatGPT Search, Google AI Overviews, Gemini, Perplexity a Claude.

Napiš vysoce konkrétní, prakticky použitelný AI Visibility Fix Report.
Klíčové pravidlo: zákazník musí dostat HOTOVÝ KÓD, který jen zkopíruje. Žádná teorie.

Výstup MUSÍ obsahovat přesně tyto sekce (použij přesně tyto nadpisy):

## 1. MANAŽERSKÉ SHRNUTÍ
Proč tento konkrétní web AI vyhledávače ignorují a co se změní po opravě (3–4 věty).

## 2. DIAGNÓZA — 4 DŮVODY, PROČ VÁS AI NEVIDÍ
Čtyři konkrétní body vázané na jeho obor a typ webu:
- **Chybějící entita firmy** — AI neví, kdo jste
- **Chybějící produktová/službová data** — AI neví, co a za kolik prodáváte
- **Blokované nebo neinstruované AI roboty** — AI se k vám nedostane
- **Obsah nepřipravený na citaci** — AI z vás nemá co citovat

## 3. HOTOVÝ ROBOTS.TXT
Vygeneruj kompletní, funkční obsah souboru robots.txt v markdown code bloku.
Musí explicitně povolovat: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot,
PerplexityBot, Google-Extended, Googlebot, Bingbot, Applebot-Extended, CCBot.
Přidej odkaz na sitemap odpovídající jeho domény.

## 4. HOTOVÝ JSON-LD KÓD
Vygeneruj kompletní, validní JSON-LD v markdown code bloku (typ application/ld+json).
Musí obsahovat propojené schémata: Organization (nebo LocalBusiness, pokud má provozovnu),
WebSite, a Product nebo Service podle jeho nabídky, plus FAQPage se 3 otázkami,
které jeho zákazníci reálně pokládají AI. Použij JEHO skutečné údaje z popisu
(název, obor, region, ceny, záruky). Vše česky, kde to jde.

## 5. NÁVOD NA NAHRÁNÍ — 10 MINUT
Přesné kroky pro platformu, kterou zákazník používá (pokud ji uvedl),
a krátce i pro ostatní: WordPress, Shopify, Shoptet, Wix.
Kam přesně soubory nahrát, na jaké tlačítko kliknout.

## 6. KONTROLA ZA 7 DNÍ
Tři konkrétní testy, jak si zákazník sám ověří, že to zabralo
(např. jaký přesný dotaz napsat do ChatGPT, kde zkontrolovat validitu schématu).
Uveď realistický časový horizont, kdy se změna projeví.

Piš prakticky, technicky přesně, bez marketingové vaty. Výhradně v češtině.

Vstup od klienta:
"""


def parse_teaser(text: str) -> dict:
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception:
        pass
    return {
        "visibility_score": 21,
        "main_barrier": "Váš web nemá žádná strukturovaná data (JSON-LD schema.org). Pro ChatGPT a Gemini jste nerozlišitelná hromada textu — nechápou, co prodáváte, za kolik ani komu.",
        "competitor_warning": "Když se zákazník zeptá AI na vaši službu ve vašem regionu, dostane jméno konkurence, která strukturovaná data má.",
        "barrier_category": "Chybějící JSON-LD",
    }


def generate_teaser(url: str, description: str) -> dict:
    client = get_openai_client()
    fallback = get_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK).lower() == "true"
    payload = "URL webu: " + url + "\nCo firma nabízí: " + description
    if client is None:
        if fallback:
            return parse_teaser("")
        st.error("Chybí OpenAI API klíč.")
        st.stop()
    try:
        resp = client.chat.completions.create(
            model=get_config("TEASER_MODEL", DEFAULT_TEASER_MODEL),
            messages=[
                {"role": "system", "content": "Jsi GEO auditor sémantické čitelnosti webu. Odpovídáš POUZE validním JSON objektem."},
                {"role": "user", "content": PROMPT_A + payload},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return parse_teaser(resp.choices[0].message.content)
    except Exception as e:
        if fallback:
            return parse_teaser("")
        st.error("Chyba API: " + str(e))
        st.stop()


def generate_report(url: str, description: str) -> str:
    client = get_openai_client()
    fallback = get_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK).lower() == "true"
    payload = "URL webu: " + url + "\nCo firma nabízí: " + description
    if client is None:
        if fallback:
            return _local_report()
        st.error("Chybí OpenAI API klíč.")
        st.stop()
    try:
        resp = client.chat.completions.create(
            model=get_config("REPORT_MODEL", DEFAULT_REPORT_MODEL),
            messages=[
                {"role": "system", "content": "Jsi expertní GEO/AEO konzultant. Generuješ hotový, validní kód k okamžitému nasazení. Česky."},
                {"role": "user", "content": PROMPT_B + payload},
            ],
            max_tokens=3500,
            temperature=0.5,
        )
        return resp.choices[0].message.content
    except Exception as e:
        if fallback:
            return _local_report()
        st.error("Chyba API: " + str(e))
        st.stop()


def _local_report() -> str:
    return """## 1. MANAŽERSKÉ SHRNUTÍ
Váš web je pro klasický Google čitelný, ale pro generativní AI vyhledávače prakticky neexistuje.
Chybí mu strukturovaná data, která AI potřebuje k tomu, aby vás mohla s jistotou doporučit —
tedy strojově čitelné informace o tom, kdo jste, co nabízíte, za kolik a v jakém regionu.
Po nasazení dvou souborů z tohoto reportu (robots.txt a JSON-LD) začnou AI vyhledávače
vaši firmu chápat jako konkrétní entitu s konkrétní nabídkou, a mohou vás začít citovat
v přímých odpovědích zákazníkům.

## 2. DIAGNÓZA — 4 DŮVODY, PROČ VÁS AI NEVIDÍ

- **Chybějící entita firmy** — Bez schématu Organization / LocalBusiness AI neví, že jste firma, kde sídlíte a jak vás kontaktovat. Nemá k čemu vás přiřadit, takže vás v odpovědi radši vynechá, než aby riskovala nepřesnost.
- **Chybějící produktová a službová data** — Bez Product / Service schématu AI nezná váš sortiment, cenové rozpětí ani rozsah služeb. Na dotaz „kdo mi v okolí udělá X do Y Kč" vás nemůže nabídnout, protože o vašich cenách nic neví.
- **Blokované nebo neinstruované AI roboty** — Většina českých webů má robots.txt, který o moderních agentech (GPTBot, ClaudeBot, PerplexityBot) vůbec nemluví, případně je restriktivním pravidlem blokuje. Bez explicitního povolení se řada z nich obsah radši nenačte.
- **Obsah nepřipravený na citaci** — AI cituje odstavce, které přímo odpovídají na konkrétní otázku. Prodejní texty ve stylu „jsme lídr na trhu" citovat nelze. Bez FAQ struktury AI z vašeho webu nemá co vytáhnout.

## 3. HOTOVÝ ROBOTS.TXT

Vytvořte (nebo přepište) soubor `robots.txt` v korenovém adresáři webu tímto obsahem:

```
# ── Klasické vyhledávače ──────────────────────────────
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Seznam-Zbozi-robot
Allow: /

# ── AI vyhledávače a asistenti (KLÍČOVÉ) ──────────────
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: CCBot
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: meta-externalagent
Allow: /

# ── Ostatní ───────────────────────────────────────────
User-agent: *
Allow: /
Disallow: /wp-admin/
Disallow: /kosik
Disallow: /objednavka
Disallow: /?s=

Sitemap: https://www.vasedomena.cz/sitemap.xml
```

**Pozor:** řádek `Sitemap:` upravte na svou skutečnou domenu.

## 4. HOTOVÝ JSON-LD KÓD

Vložte celý tento blok do sekce `<head>` na hlavní stránku webu:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "LocalBusiness",
      "@id": "https://www.vasedomena.cz/#organizace",
      "name": "Název vaší firmy",
      "description": "Jednou vetou konkrétně to, co děláte, pro koho a v jakém regionu.",
      "url": "https://www.vasedomena.cz/",
      "telephone": "+420 000 000 000",
      "email": "info@vasedomena.cz",
      "priceRange": "12000-90000 CZK",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "Ulice a číslo",
        "addressLocality": "Město",
        "postalCode": "000 00",
        "addressCountry": "CZ"
      },
      "areaServed": {
        "@type": "Country",
        "name": "Česká republika"
      },
      "openingHours": "Mo-Fr 08:00-17:00"
    },
    {
      "@type": "WebSite",
      "@id": "https://www.vasedomena.cz/#web",
      "url": "https://www.vasedomena.cz/",
      "name": "Název vaší firmy",
      "inLanguage": "cs-CZ",
      "publisher": { "@id": "https://www.vasedomena.cz/#organizace" }
    },
    {
      "@type": "Service",
      "name": "Hlavní služba nebo produktová kategorie",
      "provider": { "@id": "https://www.vasedomena.cz/#organizace" },
      "areaServed": "Česká republika",
      "offers": {
        "@type": "Offer",
        "priceCurrency": "CZK",
        "price": "12000",
        "availability": "https://schema.org/InStock"
      }
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Kolik to stojí?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Konkrétní odpověď s číslem a rozsahem. AI cituje přesná čísla, ne fráze typu 'individuální kalkulace'."
          }
        },
        {
          "@type": "Question",
          "name": "Jak dlouho to trvá?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Konkrétní termín ve dnech nebo týdnech."
          }
        },
        {
          "@type": "Question",
          "name": "Jakou dáváte záruku?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Konkrétní délka záruky a co přesně krtyje."
          }
        }
      ]
    }
  ]
}
</script>
```

## 5. NÁVOD NA NAHRÁNÍ — 10 MINUT

**WordPress**
1. robots.txt: plugin *Yoast SEO* nebo *Rank Math* → Nástroje → Editor souborů → robots.txt → vložit → Uložit.
2. JSON-LD: Vzhled → Editor motivu → `header.php`, vložit před `</head>`. Bezpečnější varianta: plugin *WPCode* → Add Snippet → typ „HTML Snippet" → Location „Site Wide Header".

**Shopify**
1. robots.txt: Online Store → Themes → Edit code → Add a new template → `robots.txt.liquid`.
2. JSON-LD: Edit code → `layout/theme.liquid`, vložit před `</head>`.

**Shoptet**
1. robots.txt: Nastavení → Roboti a SEO → pole robots.txt.
2. JSON-LD: Nastavení → HTML kódy a měřicí skripty → sekce „Kód v head".

**Wix**
1. robots.txt: Nastavení → SEO → Upravit robots.txt.
2. JSON-LD: Nastavení → Vlastní kód → Přidat kód → umístění „Head", na všech stránkách.

## 6. KONTROLA ZA 7 DNÍ

1. **Validita schématu** — otevřete `validator.schema.org`, vložte URL své hlavní stránky. Musí projít bez chyb (varování typu „recommended field missing" jsou v pořádku).
2. **Dostupnost pro roboty** — otevřete `https://vasedomena.cz/robots.txt` v prohlížeči. Musíte tam vidět řádky GPTBot a ClaudeBot.
3. **Reálný test v AI** — napište do ChatGPT (v režimu s vyhledáváním) přesně: *„Kdo v [vaše město] nabízí [vaše hlavní služba] a jaké má ceny?"* Test opakujte po 7, 21 a 45 dnech.

**Realistický horizont:** robots.txt se propaguje za 1–7 dní. Strukturovaná data se v AI odpovědích začínají projevovat typicky za 3–8 týdnů — indexy generativních vyhledávačů se neaktualizují v reálném čase. Kdo tvrdí, že vás dostane do ChatGPT „do 48 hodin", není poctivý."""


# ─── HTML REPORT GENERATION ────────────────────────────────────────────────────
def md_to_html_body(text: str) -> str:
    """Minimal markdown → HTML converter for the report (incl. code fences)."""
    import re
    import html as html_mod
    lines = text.split('\n')
    out = []
    in_code = False
    for line in lines:
        if line.strip().startswith('```'):
            if in_code:
                out.append('</code></pre>')
                in_code = False
            else:
                out.append('<pre><code>')
                in_code = True
            continue
        if in_code:
            out.append(html_mod.escape(line))
            continue
        s = line.strip()
        if not s:
            out.append('<br>')
            continue
        if s.startswith('## '):
            out.append('<h2>' + s[3:] + '</h2>')
            continue
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'`(.+?)`', r'<code class="inline">\1</code>', s)
        if s.startswith('- '):
            out.append('<li>' + s[2:] + '</li>')
            continue
        out.append('<p>' + s + '</p>')
    if in_code:
        out.append('</code></pre>')
    return '\n'.join(out)


def score_color(score: int) -> str:
    return "#c0392b" if score < 40 else "#e67e22" if score < 65 else "#27ae60"


def score_label(score: int) -> str:
    return "NEVIDITELNÝ ⚠️" if score < 40 else "ČÁSTEČNĚ VIDITELNÝ" if score < 65 else "DOBŘE VIDITELNÝ ✓"


def generate_html_download(report_text: str, url: str, description: str, score: int) -> str:
    date_str = datetime.now().strftime('%d. %m. %Y')
    body_html = md_to_html_body(report_text)
    color = score_color(score)
    label = score_label(score)
    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Visibility Fix Report</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 880px; margin: 0 auto; padding: 2rem; color: #1a1a2e; line-height: 1.7; }}
  .header {{ background: linear-gradient(135deg, #0a2850, #1a4a8a); color: white; padding: 2rem 2.5rem; border-radius: 10px; margin-bottom: 2rem; }}
  .header h1 {{ margin: 0 0 0.3rem 0; font-size: 1.8rem; }}
  .header p {{ margin: 0; opacity: 0.75; font-size: 0.95rem; }}
  .score-box {{ display: inline-block; background: {color}; color: white; font-size: 2.2rem; font-weight: 900; border-radius: 50%; width: 84px; height: 84px; line-height: 84px; text-align: center; margin-right: 1rem; vertical-align: middle; }}
  .score-label {{ display: inline-block; vertical-align: middle; }}
  .score-label strong {{ font-size: 1.15rem; color: {color}; }}
  .input-box {{ background: #f4f6fb; border-left: 4px solid #1a4a8a; padding: 1rem 1.5rem; border-radius: 6px; margin-bottom: 2rem; font-size: 0.9rem; color: #555; }}
  h2 {{ background: #eef2ff; color: #0a2850; padding: 0.6rem 1rem; border-radius: 6px; font-size: 1.05rem; margin-top: 2rem; }}
  p {{ margin: 0.5rem 0; }}
  li {{ margin: 0.3rem 0 0.3rem 1.2rem; }}
  pre {{ background: #10141c; color: #d6e2f0; padding: 1.1rem 1.3rem; border-radius: 8px; overflow-x: auto; font-size: 0.82rem; line-height: 1.5; }}
  pre code {{ font-family: 'Consolas', 'Courier New', monospace; white-space: pre; }}
  code.inline {{ background: #eef2ff; color: #0a2850; padding: 0.1rem 0.35rem; border-radius: 4px; font-size: 0.9em; }}
  .footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: 0.78rem; color: #999; text-align: center; }}
  strong {{ color: #0a2850; }}
  @media print {{ body {{ padding: 0.5rem; }} .header {{ border-radius: 0; }} pre {{ background: #f4f4f4; color: #222; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>🤖 AI Visibility Fix Report</h1>
  <p>Vygenerováno: {date_str} &nbsp;|&nbsp; Batko Digital AI</p>
</div>

<div style="margin-bottom:1.5rem;">
  <span class="score-box">{score}</span>
  <span class="score-label">AI Visibility Score (0–100)<br><strong>{label}</strong></span>
</div>

<div class="input-box">
  <strong>Auditovaný web:</strong> {url}<br>
  <strong>Popis nabídky:</strong> {description}
</div>

{body_html}

<div class="footer">
  Batko Digital AI &nbsp;|&nbsp; {UPSELL_EMAIL}<br>
  Report má konzultační charakter. Rychlost indexace generativními vyhledávači nelze garantovat — závisí na jejich vlastních cyklech.
</div>
</body>
</html>"""


def generate_checklist_html() -> str:
    return """<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<title>12 signálů, podle kterých si vás AI vyhledávače vyberou — 2026</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 780px; margin: 0 auto; padding: 2rem; color: #222; }
  h1 { font-size: 1.4rem; border-bottom: 3px solid #0a2850; padding-bottom: 0.5rem; }
  .intro { color: #555; font-size: 0.9rem; margin-bottom: 1.5rem; }
  .item { display: flex; gap: 1rem; margin-bottom: 1rem; padding: 0.8rem; background: #f9f9f9; border-left: 4px solid #1a4a8a; border-radius: 4px; }
  .num { font-size: 1.4rem; font-weight: 900; color: #1a4a8a; min-width: 2rem; }
  .content strong { display: block; margin-bottom: 0.2rem; }
  .content span { font-size: 0.88rem; color: #555; }
  .footer { margin-top: 2rem; font-size: 0.8rem; color: #999; border-top: 1px solid #eee; padding-top: 0.8rem; }
</style>
</head>
<body>
<h1>12 signálů, podle kterých si vás AI vyhledávače vyberou (nebo přeskočí)</h1>
<p class="intro">Praktický checklist od Batko Digital AI. Projděte bod po bodu — každý zaberte pod 15 minut.</p>

<div class="item"><div class="num">1</div><div class="content"><strong>Máte na webu konkrétní čísla, ne fráze</strong><span>AI cituje "od 12 000 Kč, dodání 14 dní". Necituje "individuální kalkulace" ani "špičková kvalita".</span></div></div>
<div class="item"><div class="num">2</div><div class="content"><strong>Vaše firma je strojově identifikovatelná entita</strong><span>Organization / LocalBusiness schéma s IČO, adresou, telefonem. Bez toho jste pro AI jen text.</span></div></div>
<div class="item"><div class="num">3</div><div class="content"><strong>robots.txt explicitně jmenuje GPTBot a ClaudeBot</strong><span>Mlčení není souhlas. Část agentů bez explicitního Allow raději obsah nenačte.</span></div></div>
<div class="item"><div class="num">4</div><div class="content"><strong>Odpovídáte na otázky, které lidé reálně píší do AI</strong><span>Ne "Naše služby", ale "Kolik stojí X v Praze?" — přesně tou formulací jako nadpis H2.</span></div></div>
<div class="item"><div class="num">5</div><div class="content"><strong>Klíčový obsah není schovaný v JavaScriptu</strong><span>Většina AI crawlerů nespouští JS. Co se načte až po kliknutí, pro ně neexistuje.</span></div></div>
<div class="item"><div class="num">6</div><div class="content"><strong>Máte FAQPage schéma se 3–8 reálnými otázkami</strong><span>Nejrychlejší cesta k citaci v přímé odpovědi. Otázky berte z e-mailů od zákazníků.</span></div></div>
<div class="item"><div class="num">7</div><div class="content"><strong>Uvádíte region, kde působíte, doslova</strong><span>"Kladno a okolí do 40 km" AI zpracuje. "Působíme po celé republice" ji nikam nenavede.</span></div></div>
<div class="item"><div class="num">8</div><div class="content"><strong>Zmiňují vás jiné weby jmenovitě</strong><span>AI váží konsenzus napříč zdroji. Katalogy, oborové portály, recenze — na tom staví důvěru.</span></div></div>
<div class="item"><div class="num">9</div><div class="content"><strong>Máte funkční a aktuální sitemap.xml</strong><span>Odkázaný z robots.txt. Bez něj crawler najde jen to, na co vede odkaz z homepage.</span></div></div>
<div class="item"><div class="num">10</div><div class="content"><strong>Autorství a datum aktualizace jsou vidět</strong><span>AI preferuje obsah s jasným autorem a datem. Nedatovaný text vypadá jako riziko.</span></div></div>
<div class="item"><div class="num">11</div><div class="content"><strong>Nemáte duplicitní nebo kanibalizující stránky</strong><span>Tři stránky o téže službě si navzájem berou váhu. Sloučit do jedné silné.</span></div></div>
<div class="item"><div class="num">12</div><div class="content"><strong>Kontrolujete to opakovaně, ne jednou</strong><span>Indexy AI vyhledávačů se mění. Test stejným dotazem po 7, 21 a 45 dnech.</span></div></div>

<div class="footer">Batko Digital AI &nbsp;|&nbsp; batko.digital.ai@gmail.com &nbsp;|&nbsp; Checklist slouží jako praktická pomůcka. Pozice v AI odpovědích nelze garantovat.</div>
</body>
</html>"""


# ─── UI ────────────────────────────────────────────────────────────────────────
def render_header():
    st.markdown(
        f"<div style='font-size:.82rem;font-weight:700;color:#B6452C;"
        f"text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem'>"
        f"{APP_LABEL}</div>",
        unsafe_allow_html=True,
    )
    st.title("🤖 " + APP_TITLE)
    st.caption(APP_SUBTITLE)


def load_demo() -> None:
    st.session_state.url = DEMO_URL
    st.session_state.description = DEMO_DESCRIPTION
    st.session_state.step = "generating_teaser"
    st.session_state.demo = True


def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return raw
    if not (raw.startswith("http://") or raw.startswith("https://")):
        raw = "https://" + raw
    return raw


def render_input():
    url = st.text_input(
        "URL vašeho webu nebo e-shopu:",
        placeholder="www.mujweb.cz",
        key="url_input",
    )
    desc = st.text_area(
        "Co nabízíte a komu? (čím konkrétněji, tím přesnější kód dostanete)",
        placeholder="Např. 'Prodáváme ručně vyráběný teakový zahradní nábytek na Kladensku, "
                    "rozvoz po ČR, ceny 12–90 tis. Kč, 7 let záruka, web na WordPressu.'",
        height=130,
        key="desc_input",
    )
    if st.button("🔍 Zkontrolovat mou viditelnost v AI", type="primary", use_container_width=True):
        if not url.strip():
            st.warning("Zadejte prosím adresu svého webu.")
        elif not desc or len(desc.strip()) < 20:
            st.warning("Popište prosím v 1–2 větách, co nabízíte — bez toho nelze vygenerovat funkční kód.")
        else:
            st.session_state.url = normalize_url(url)
            st.session_state.description = desc.strip()
            st.session_state.step = "generating_teaser"
            st.rerun()

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Čas do výsledku", "< 30 s")
    c2.metric("Hotové soubory", "2 ks")
    c3.metric("Cena v agentuře", "15–40 tis. Kč")

    st.divider()
    st.markdown("### Nevíte, co od auditu čekat?")
    st.caption("Prohlédněte si ukázku na fiktivním e-shopu — zdarma, bez registrace.")
    if st.button("Zobrazit demo zdarma", use_container_width=True, key="btn_demo"):
        load_demo()
        st.rerun()


def render_teaser(t: dict):
    score = int(t.get("visibility_score", 21))
    barrier = t.get("main_barrier", "")
    warn = t.get("competitor_warning", "")
    cat = t.get("barrier_category", "Chybějící JSON-LD")
    color = score_color(score)
    label = score_label(score)

    st.markdown(f"""
    <div style="background:#fff8f8;border:2px solid {color};border-radius:12px;padding:1.5rem;margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:1.2rem;">
        <div style="background:{color};color:white;font-size:2.1rem;font-weight:900;border-radius:50%;
                    width:88px;height:88px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
          {score}
        </div>
        <div>
          <div style="font-size:0.8rem;color:#888;text-transform:uppercase;font-weight:600;letter-spacing:.05em;">AI Visibility Score (0–100)</div>
          <div style="font-size:1.35rem;font-weight:700;color:{color};">{label}</div>
          <div style="font-size:0.88rem;color:#999;">Hlavní bariéra: {cat}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#fff3cd;border-left:4px solid #f39c12;padding:1rem 1.2rem;border-radius:8px;margin-bottom:0.8rem;">
      <div style="font-weight:700;color:#856404;margin-bottom:0.3rem;">🔴 Kritická bariéra odhalena:</div>
      <div style="color:#533f03;line-height:1.6;">{barrier}</div>
    </div>
    <div style="background:#fce8e8;border-left:4px solid #c0392b;padding:1rem 1.2rem;border-radius:8px;margin-bottom:1.5rem;">
      <div style="font-weight:700;color:#c0392b;margin-bottom:0.3rem;">💸 Co se děje právě teď:</div>
      <div style="color:#7b241c;">{warn}</div>
    </div>
    """, unsafe_allow_html=True)


def render_paywall():
    payment_link = get_config("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    price_text = get_config("PRICE_TEXT", DEFAULT_PRICE_TEXT)

    st.markdown("---")
    st.markdown("### 🔓 Získejte hotové opravné soubory na míru")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
**Co dostanete za {price_text}:**
- ✅ **Hotový robots.txt** — povolení pro GPTBot, ClaudeBot, PerplexityBot
- ✅ **Hotový JSON-LD kód** — vaše firma, ceny, služby, FAQ
- ✅ Diagnóza 4 důvodů, proč vás AI přeskakuje
- ✅ Návod na nahrání pro WordPress / Shopify / Shoptet / Wix
- ✅ 3 testy, jak si sami ověříte, že to zabralo
- 🎁 **BONUS:** Checklist „12 signálů, podle kterých si vás AI vybere"
        """)
        st.markdown("""
<div style="background:#e8f5e9;border:1px solid #4caf50;border-radius:8px;padding:0.8rem;font-size:0.85rem;margin-top:0.5rem;">
  <strong>💚 Garance vrácení:</strong><br>
  Pokud kód nebude použitelný na vašem webu, stačí jeden e-mail
  a do 24 h vrátíme 100 % v Kč. Soubory si navíc můžete nechat.
</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
<div style="text-align:center;background:linear-gradient(135deg,#0a2850,#1a4a8a);border-radius:12px;padding:1.5rem;color:white;">
  <div style="font-size:2rem;margin-bottom:0.5rem;">🤖</div>
  <div style="font-size:1.05rem;font-weight:700;margin-bottom:0.3rem;">AI Visibility Fix Report</div>
  <div style="font-size:1.8rem;font-weight:900;color:#ffd700;margin-bottom:1rem;">{price_text}</div>
  <a href="{payment_link}" target="_blank"
     style="background:#ffd700;color:#0a2850;text-decoration:none;padding:0.75rem 1.8rem;
            border-radius:8px;font-weight:700;font-size:1rem;display:inline-block;">
    🔐 Zaplatit a získat kód
  </a>
  <div style="font-size:0.75rem;color:#a0c4ff;margin-top:0.8rem;">Platba kartou přes bezpečný Stripe</div>
</div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("✅ Mám přístupový kód"):
        code_input = st.text_input("Přístupový kód:", type="password", key="code_input")
        if st.button("Odemknout report", type="primary"):
            expected = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)
            if expected and code_input.strip() == expected:
                st.session_state.step = "generating_report"
                st.rerun()
            else:
                st.error("Nesprávný kód. Po platbě obdržíte kód e-mailem.")


def render_report(report_text: str, url: str, description: str, score: int):
    st.success("✅ Vaše opravné soubory jsou připravené!")
    st.markdown("---")
    st.markdown(report_text)
    st.markdown("---")

    html_report = generate_html_download(report_text, url, description, score)
    html_checklist = generate_checklist_html()

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Stáhnout AI Visibility Fix Report (HTML)",
            data=html_report.encode("utf-8"),
            file_name=f"AI_Visibility_Fix_Report_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True,
            type="primary",
        )
    with col2:
        st.download_button(
            label="🎁 Stáhnout Bonus Checklist",
            data=html_checklist.encode("utf-8"),
            file_name="12_signalu_AI_visibility_2026.html",
            mime="text/html",
            use_container_width=True,
        )

    st.caption("💡 Tip: Soubory otevřete v prohlížeči a vytiskněte jako PDF (Ctrl+P → Uložit jako PDF).")

    upsell_price = get_config("UPSELL_PRICE", DEFAULT_UPSELL_PRICE)
    st.markdown("---")
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0a2850,#1a4a8a);border-radius:12px;padding:1.8rem;color:white;text-align:center;margin-top:1rem;">
  <div style="font-size:1.5rem;font-weight:700;margin-bottom:0.5rem;">🚀 Nechcete se hrabat v kódu?</div>
  <div style="color:#a0c4ff;margin-bottom:1.2rem;max-width:520px;margin-left:auto;margin-right:auto;">
    Máte přesně vědět co nahrát. Nahrát to ale musíte. Pokud na to není čas ani chuť, uděláme to za vás.
  </div>
  <div style="background:rgba(255,255,255,.1);border-radius:8px;padding:1rem 1.5rem;margin-bottom:1.2rem;text-align:left;max-width:480px;margin-left:auto;margin-right:auto;">
    <strong>Balíček „AI Visibility na klíč":</strong><br>
    ✅ Nahrajeme robots.txt i JSON-LD přímo na váš web<br>
    ✅ Rozšíříme schémata na všechny podstatné podstránky<br>
    ✅ Přepíšeme 5 klíčových odstavců do citovatelné podoby<br>
    ✅ Kontrolní report po 30 dnech s reálnými testy v AI
  </div>
  <div style="font-size:2rem;font-weight:900;color:#ffd700;margin-bottom:1rem;">{upsell_price}</div>
  <a href="mailto:{UPSELL_EMAIL}?subject=Z%C3%A1jem%20o%20AI%20Visibility%20na%20kl%C3%AD%C4%8D&body=Dobr%C3%BD%20den%2C%20m%C3%A1m%20z%C3%A1jem%20o%20bal%C3%AD%C4%8Dek%20AI%20Visibility%20na%20kl%C3%AD%C4%8D.%20URL%20m%C3%A9ho%20webu%3A%20"
     style="background:#ffd700;color:#0a2850;text-decoration:none;padding:0.8rem 2rem;border-radius:8px;font-weight:700;font-size:1rem;display:inline-block;">
    📩 Chci to nechat na vás
  </a>
</div>
    """, unsafe_allow_html=True)


# ─── FOOTER ────────────────────────────────────────────────────────────────────
def render_footer():
    st.markdown("---")
    with st.expander("Kontakt"):
        st.markdown(
            f"**{COMPANY_NAME}**  \n"
            f"{COMPANY_PERSON}  \n"
            f"IČO: {COMPANY_ICO} &nbsp;|&nbsp; DIČ: {COMPANY_DIC}  \n"
            f"Sídlo: {COMPANY_ADDRESS}  \n"
            f"Tel: {COMPANY_PHONE}  \n"
            f"E-mail: [{COMPANY_EMAIL}](mailto:{COMPANY_EMAIL})"
        )
    with st.expander("Obchodní podmínky"):
        st.markdown(
            f"**Prodávající:** {COMPANY_NAME}, {COMPANY_PERSON}, "
            f"IČO {COMPANY_ICO}, DIČ {COMPANY_DIC}, sídlo {COMPANY_ADDRESS}.  \n\n"
            "Předmětem plnění je digitální produkt (AI Visibility Fix Report ve formátu HTML "
            "včetně vygenerovaného kódu robots.txt a JSON-LD) dodaný k okamžitému zobrazení "
            "a stažení v aplikaci po ověření platby.  \n\n"
            "Report má konzultační a technicko-informační charakter. Prodávající negarantuje "
            "konkrétní pozici, zmínku ani citaci ve výstupech vyhledávačů či AI asistentů — "
            "ty závisí na algoritmech a indexačních cyklech třetích stran.  \n\n"
            "Na digitální obsah zpřístupněný na žádost kupujícího se zákonné právo na odstoupení "
            "bez udání důvodu nevztahuje (§ 1837 písm. l) OZ).  \n\n"
            f"Dotazy: [{COMPANY_EMAIL}](mailto:{COMPANY_EMAIL})"
        )
    with st.expander("Ochrana soukromí (GDPR)"):
        st.markdown(
            f"Správce: {COMPANY_NAME}, IČO {COMPANY_ICO}.  \n\n"
            "Tato aplikace nezpracovává ani neukládá žádné osobní údaje uživatelů. "
            "Zadaná URL a popis nabídky jsou použity výhradně pro jednorázové vygenerování "
            "reportu a nejsou trvale ukládány ani sdíleny s třetími stranami.  \n\n"
            "Zpracování probíhá přes OpenAI API v souladu s GDPR a EU AI Act.  \n\n"
            f"Dotazy: [{COMPANY_EMAIL}](mailto:{COMPANY_EMAIL})"
        )
    with st.expander("Vrácení peněz"):
        st.markdown(
            "Report je vygenerován a zpřístupněn ihned po potvrzení platby.  \n\n"
            "Pokud vygenerovaný kód není použitelný na vašem webu, napište nám do 14 dnů "
            f"od nákupu na [{COMPANY_EMAIL}](mailto:{COMPANY_EMAIL}) "
            "s číslem objednávky.  \n\n"
            "Vrácení provedeme do 14 dnů přes Stripe."
        )
    st.markdown(
        f"<div style='font-size:.73rem;color:#9ca3af;text-align:center;padding:.7rem 0 .3rem'>"
        f"{COMPANY_NAME} &nbsp;·&nbsp; IČO {COMPANY_ICO} &nbsp;·&nbsp; {COMPANY_ADDRESS}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🤖", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)
    render_header()

    if "step" not in st.session_state:
        st.session_state.step = "input"

    step = st.session_state.step

    if step == "input":
        render_input()

    elif step == "generating_teaser":
        with st.spinner("Kontrolujeme, jak váš web vidí AI vyhledávače..."):
            t = generate_teaser(st.session_state.url, st.session_state.description)
        st.session_state.teaser = t
        st.session_state.step = "teaser"
        st.rerun()

    elif step == "teaser":
        render_teaser(st.session_state.teaser)
        render_paywall()
        if st.button("← Začít znovu", key="restart_teaser"):
            for k in ["step", "teaser", "url", "description", "report"]:
                st.session_state.pop(k, None)
            st.rerun()

    elif step == "generating_report":
        with st.spinner("Generujeme robots.txt a JSON-LD kód na míru (30–50 sekund)..."):
            r = generate_report(st.session_state.url, st.session_state.description)
        st.session_state.report = r
        st.session_state.step = "report"
        st.rerun()

    elif step == "report":
        render_report(
            st.session_state.report,
            st.session_state.get("url", ""),
            st.session_state.get("description", ""),
            int(st.session_state.get("teaser", {}).get("visibility_score", 21)),
        )
        if st.button("← Nový audit", key="restart_report"):
            for k in ["step", "teaser", "url", "description", "report"]:
                st.session_state.pop(k, None)
            st.rerun()

    render_footer()


if __name__ == "__main__":
    main()
