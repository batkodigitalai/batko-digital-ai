import streamlit as st
import os
import re
import json
import socket
import ipaddress
import urllib.request
import urllib.error
from urllib.parse import urlparse, urljoin
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────────
APP_TITLE    = "AI Visibility Auditor"
APP_LABEL    = "BEZPLATNÝ AI VISIBILITY AUDIT"
APP_SUBTITLE = "Zjistěte za 30 sekund, zda ChatGPT a Gemini doporučují vás — nebo vaši konkurenci."

DEFAULT_ACCESS_CODE          = ""
DEFAULT_PAYMENT_LINK         = "https://buy.stripe.com/YOUR_LINK_HERE"
# ─── MODELY ───────────────────────────────────────────────────────────────────
# Teaser je zdarma a hromadný → Luna (cost-sensitive, high-volume).
# Report je placený a generuje KÓD → Sol (complex reasoning and coding).
# Zdroj ID: developers.openai.com/api/docs/models (ověřeno 25.7.2026)
#
# ZÁMĚRNĚ se nečtou ze Secrets. Volba modelu je produktové rozhodnutí, které
# má být verzované gitem, ne schované v runtime konfiguraci. Překlep v názvu
# modelu v Secrets by jinak shodil volání do fallbacku a zákazník by dostal
# šablonový výstup, aniž by si toho kdokoli všiml. Případné staré klíče
# TEASER_MODEL / REPORT_MODEL v Secrets se prostě ignorují.
DEFAULT_TEASER_MODEL         = "gpt-5.6-luna"   # $1 / $6 za MTok
DEFAULT_REPORT_MODEL         = "gpt-5.6-sol"    # $5 / $30 za MTok, alias gpt-5.6
# Když zadaný model neexistuje nebo selže, zkusí se popořadě tyhle. Až pak fallback.
MODEL_SAFETY_NET             = ["gpt-5.6-terra", "gpt-4.1"]

# Fallback na lokální šablonu: rozdělený, protože teaser a report mají jiná rizika.
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"           # zpětná kompatibilita, výchozí pro teaser
DEFAULT_ALLOW_TEASER_FALLBACK = ""              # prázdné = zdědí ALLOW_LOCAL_FALLBACK
DEFAULT_ALLOW_REPORT_FALLBACK = "false"         # platící zákazník nesmí dostat šablonu mlčky
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

AI_BOTS = [
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot",
    "anthropic-ai", "PerplexityBot", "Perplexity-User", "Google-Extended",
    "Applebot-Extended", "CCBot", "Amazonbot", "meta-externalagent", "Bytespider",
]

FETCH_TIMEOUT = 7
FETCH_UA = "Mozilla/5.0 (compatible; BatkoVisibilityAuditor/1.0; +https://batko.digital)"
MAX_HTML_BYTES = 400_000

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

DEMO_URL = "https://www.mvcr.cz"
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


# ─── SKUTEČNÁ DIAGNOSTIKA WEBU ─────────────────────────────────────────────────
def _is_public_host(hostname: str) -> bool:
    """Zabrání dotazům na interní adresy (SSRF)."""
    if not hostname:
        return False
    if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
        return False
    try:
        infos = socket.getaddrinfo(hostname, None)
    except Exception:
        return False
    for info in infos:
        addr = info[4][0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            return False
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    return True


def _fetch(url: str, limit: int = MAX_HTML_BYTES):
    """Vrátí (text, error). Nikdy nevyhodí výjimku."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return None, "nepodporované schéma URL"
    if not _is_public_host(parsed.hostname):
        return None, "doménu nelze přeložit nebo není veřejná"
    req = urllib.request.Request(url, headers={"User-Agent": FETCH_UA, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            raw = resp.read(limit)
        return raw.decode("utf-8", errors="replace"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return None, f"nedostupné ({getattr(e, 'reason', 'chyba sítě')})"
    except socket.timeout:
        return None, f"timeout po {FETCH_TIMEOUT} s"
    except Exception as e:
        return None, f"chyba: {type(e).__name__}"


def _parse_robots(txt: str) -> dict:
    """Zjistí, jak robots.txt zachází s AI agenty."""
    allowed, blocked, mentioned = [], [], []
    blocks, current = [], None
    for line in txt.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip().lower(), val.strip()
        if key == "user-agent":
            if current is None or current["rules"]:
                current = {"agents": [], "rules": []}
                blocks.append(current)
            current["agents"].append(val)
        elif key in ("allow", "disallow") and current is not None:
            current["rules"].append((key, val))

    def verdict_for(agent: str):
        agent_l = agent.lower()
        for b in blocks:
            if any(a.lower() == agent_l for a in b["agents"]):
                if any(k == "disallow" and v == "/" for k, v in b["rules"]):
                    return "blocked"
                return "allowed"
        return None

    for bot in AI_BOTS:
        v = verdict_for(bot)
        if v == "blocked":
            blocked.append(bot)
            mentioned.append(bot)
        elif v == "allowed":
            allowed.append(bot)
            mentioned.append(bot)

    wildcard_blocked = False
    for b in blocks:
        if any(a == "*" for a in b["agents"]):
            if any(k == "disallow" and v == "/" for k, v in b["rules"]):
                wildcard_blocked = True
    return {
        "ai_allowed": allowed,
        "ai_blocked": blocked,
        "ai_mentioned": mentioned,
        "wildcard_blocked_all": wildcard_blocked,
        "has_sitemap": bool(re.search(r"(?im)^\s*sitemap\s*:", txt)),
    }


def _parse_html(html: str) -> dict:
    """Najde JSON-LD, og tagy, titulek, H2 otázky."""
    schema_types, jsonld_blocks, invalid = [], 0, 0
    for m in re.finditer(
        r'<script[^>]*type\s*=\s*["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.I | re.S,
    ):
        jsonld_blocks += 1
        body = m.group(1).strip()
        try:
            data = json.loads(body)
        except Exception:
            invalid += 1
            continue

        def collect(node):
            if isinstance(node, dict):
                t = node.get("@type")
                if isinstance(t, str):
                    schema_types.append(t)
                elif isinstance(t, list):
                    schema_types.extend([x for x in t if isinstance(x, str)])
                for v in node.values():
                    collect(v)
            elif isinstance(node, list):
                for v in node:
                    collect(v)

        collect(data)

    title_m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    h2s = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.I | re.S)
    h2_clean = [re.sub(r"<[^>]+>", "", h).strip() for h in h2s]
    return {
        "jsonld_blocks": jsonld_blocks,
        "jsonld_invalid": invalid,
        "schema_types": sorted(set(schema_types)),
        "has_org": any(t in ("Organization", "LocalBusiness", "Store", "Corporation")
                       for t in schema_types),
        "has_product_or_service": any(t in ("Product", "Service", "Offer", "OfferCatalog")
                                      for t in schema_types),
        "has_faq": any(t in ("FAQPage", "Question") for t in schema_types),
        "has_og": bool(re.search(r'<meta[^>]+property\s*=\s*["\']og:', html, re.I)),
        "title": (re.sub(r"\s+", " ", title_m.group(1)).strip()[:120] if title_m else ""),
        "h2_questions": [h for h in h2_clean if "?" in h][:5],
        "h2_count": len(h2_clean),
        "lang": (re.search(r'<html[^>]+lang\s*=\s*["\']([^"\']+)', html, re.I).group(1)
                 if re.search(r'<html[^>]+lang\s*=\s*["\']([^"\']+)', html, re.I) else ""),
    }


def probe_website(url: str) -> dict:
    """Skutečně stáhne robots.txt a homepage. Nic si nevymýšlí."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    out = {"url": url, "base": base, "robots": None, "robots_error": None,
           "html": None, "html_error": None}

    robots_txt, err = _fetch(urljoin(base + "/", "robots.txt"), limit=100_000)
    if robots_txt is None:
        out["robots_error"] = err
    else:
        out["robots"] = _parse_robots(robots_txt)

    html, err2 = _fetch(url)
    if html is None:
        html, err2b = _fetch(base + "/")
        if html is None:
            out["html_error"] = err2 or err2b
    if html is not None:
        out["html"] = _parse_html(html)
    return out


def compute_score(probe: dict) -> int:
    """Deterministické skóre z reálných zjištění. Žádná fabulace."""
    if probe.get("html") is None and probe.get("robots") is None:
        return -1  # nelze měřit
    score = 100
    h = probe.get("html") or {}
    r = probe.get("robots")

    if probe.get("html") is None:
        score -= 20
    else:
        if h.get("jsonld_blocks", 0) == 0:
            score -= 45
        else:
            if not h.get("has_org"):
                score -= 12
            if not h.get("has_product_or_service"):
                score -= 10
            if not h.get("has_faq"):
                score -= 8
            if h.get("jsonld_invalid", 0) > 0:
                score -= 10
        if not h.get("has_og"):
            score -= 5
        if not h.get("title"):
            score -= 5
        if not h.get("h2_questions"):
            score -= 5

    if r is None:
        score -= 12
    else:
        if r.get("wildcard_blocked_all"):
            score -= 30
        if r.get("ai_blocked"):
            score -= 25
        elif not r.get("ai_mentioned"):
            score -= 15
        if not r.get("has_sitemap"):
            score -= 5

    score = max(5, min(98, score))

    # Strop: kdo blokuje AI crawlera, nemuze byt "dobre viditelny", i kdyby mel vse ostatni.
    if r is not None:
        if r.get("wildcard_blocked_all"):
            score = min(score, 15)
        elif r.get("ai_blocked"):
            score = min(score, 45)
    return score


def probe_facts_text(probe: dict) -> str:
    """Zjištění v čitelné podobě — vstup pro AI i pro report. Jen fakta."""
    lines = []
    h, r = probe.get("html"), probe.get("robots")
    lines.append("Auditovaná URL: " + probe.get("url", ""))
    if h is None:
        lines.append("HTML homepage: NEPODAŘILO SE NAČÍST (" + str(probe.get("html_error")) + ")")
    else:
        lines.append(f"JSON-LD bloků na homepage: {h['jsonld_blocks']}"
                     + (f" (z toho nevalidních: {h['jsonld_invalid']})" if h["jsonld_invalid"] else ""))
        lines.append("Nalezené schema.org typy: " + (", ".join(h["schema_types"]) if h["schema_types"] else "žádné"))
        lines.append(f"Schéma firmy (Organization/LocalBusiness): {'ANO' if h['has_org'] else 'NE'}")
        lines.append(f"Schéma produktu/služby: {'ANO' if h['has_product_or_service'] else 'NE'}")
        lines.append(f"FAQ schéma: {'ANO' if h['has_faq'] else 'NE'}")
        lines.append(f"Open Graph meta tagy: {'ANO' if h['has_og'] else 'NE'}")
        lines.append("Titulek stránky: " + (h["title"] or "chybí"))
        lines.append(f"Jazyk stránky (html lang): {h['lang'] or 'nenastaven'}")
        lines.append(f"H2 nadpisů celkem: {h['h2_count']}, z toho ve formě otázky: {len(h['h2_questions'])}")
        if h["h2_questions"]:
            lines.append("Otázkové nadpisy: " + " | ".join(h["h2_questions"]))
    if r is None:
        lines.append("robots.txt: NENALEZEN nebo nedostupný (" + str(probe.get("robots_error")) + ")")
    else:
        lines.append("robots.txt: nalezen")
        lines.append("AI agenti výslovně povolení: " + (", ".join(r["ai_allowed"]) if r["ai_allowed"] else "žádní"))
        lines.append("AI agenti výslovně blokovaní: " + (", ".join(r["ai_blocked"]) if r["ai_blocked"] else "žádní"))
        lines.append(f"Pravidlo 'User-agent: * / Disallow: /': {'ANO — web blokuje všechny roboty' if r['wildcard_blocked_all'] else 'ne'}")
        lines.append(f"Odkaz na sitemap v robots.txt: {'ANO' if r['has_sitemap'] else 'NE'}")
    return "\n".join(lines)


# ─── OPENAI ────────────────────────────────────────────────────────────────────
def get_openai_client():
    from openai import OpenAI
    key = get_config("OPENAI_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key)


def _model_chain(configured: str) -> list:
    """Zadaný model první, pak záchranná síť. Bez duplikátů, bez prázdných."""
    chain = [configured] + MODEL_SAFETY_NET
    seen, out = set(), []
    for m in chain:
        m = (m or "").strip()
        if m and m not in seen:
            seen.add(m)
            out.append(m)
    return out


def _call_model(client, model: str, messages: list, max_out: int,
                temperature=None, effort=None) -> str:
    """Jedno volání, které přežije rozdíly mezi generacemi modelů.

    Modely řady gpt-5.6 neberou `max_tokens` ani `temperature` a naopak
    umí `reasoning_effort`. Starší modely je to naopak. Zkoušíme od
    nejmodernějšího tvaru volání k nejstaršímu.
    """
    base = {"model": model, "messages": messages}
    attempts = []
    if effort:
        attempts.append({**base, "max_completion_tokens": max_out, "reasoning_effort": effort})
    attempts.append({**base, "max_completion_tokens": max_out})
    legacy = {**base, "max_tokens": max_out}
    if temperature is not None:
        legacy["temperature"] = temperature
    attempts.append(legacy)

    last_err = None
    for kwargs in attempts:
        try:
            resp = client.chat.completions.create(**kwargs)
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text
            last_err = RuntimeError("model vrátil prázdnou odpověď")
        except Exception as e:
            last_err = e
    raise last_err if last_err else RuntimeError("volání modelu selhalo")


def call_llm(client, configured_model: str, messages: list, max_out: int,
             temperature=None, effort=None):
    """Projde model chain. Vrací (text, jméno modelu, který uspěl)."""
    last_err = None
    for model in _model_chain(configured_model):
        try:
            return _call_model(client, model, messages, max_out, temperature, effort), model
        except Exception as e:
            last_err = e
    raise last_err if last_err else RuntimeError("žádný model neodpověděl")


# ─── VALIDACE VLASTNÍHO VÝSTUPU ────────────────────────────────────────────────
def extract_jsonld_blocks(md: str) -> list:
    """Vytáhne z markdown reportu bloky, které mají být JSON-LD."""
    out = []
    for block in re.findall(r"```[a-zA-Z-]*\s*(.*?)```", md, re.S):
        s = block.strip()
        m = re.search(r"<script[^>]*ld\+json[^>]*>(.*?)</script>", s, re.S | re.I)
        if m:
            s = m.group(1).strip()
        if s[:1] in ("{", "["):
            out.append(s)
    return out


def report_jsonld_valid(md: str) -> bool:
    """Report musí obsahovat aspoň jeden JSON-LD blok a všechny musí být validní.

    Prodáváme hotový kód k nasazení. Rozbitý JSON-LD je vrácení peněz,
    takže si vlastní výstup kontrolujeme stejně, jako měříme cizí weby.
    """
    blocks = extract_jsonld_blocks(md)
    if not blocks:
        return False
    for b in blocks:
        try:
            json.loads(b)
        except Exception:
            return False
    return True


PROMPT_A = """Jsi auditor sémantické čitelnosti webu pro AI vyhledávače (GEO / AEO specialist).

Níže dostaneš SKUTEČNĚ ZMĚŘENÁ ZJIŠTĚNÍ z webu klienta (stáhli jsme jeho robots.txt a homepage).

ABSOLUTNÍ PRAVIDLO: Smíš mluvit POUZE o tom, co je v zjištěních. Nikdy netvrď, že něco chybí,
pokud to zjištění neuvádějí. Pokud zjištění říkají, že něco ANO má, uznej to a najdi skutečnou
slabinu jinde. Žádné vymýšlení. Žádné strašení nepodloženými čísly.

Vrať POUZE validní JSON objekt (žádný jiný text, žádné markdown bloky) s klíči:
- "main_barrier": string — největší SKUTEČNĚ ZMĚŘENÁ bariéra, konkrétně pojmenovaná (max 2 věty, česky)
- "consequence": string — jedna věcná věta o tom, co ta konkrétní bariéra znamená pro dohledatelnost v AI (česky, bez hyperbol)
- "barrier_category": string — jedna z: "Chybějící JSON-LD", "Nekompletní JSON-LD", "Blokované AI roboty",
  "Neinstruované AI roboty", "Chybějící entita firmy", "Chybějící FAQ markup", "Chybějící sitemap", "Obsah bez otázek"

ZMĚŘENÁ ZJIŠTĚNÍ:
"""

PROMPT_B = """Jsi expert na Generative Engine Optimization (GEO) — optimalizaci webů pro
ChatGPT Search, Google AI Overviews, Gemini, Perplexity a Claude.

Napiš konkrétní AI Visibility Fix Report. Klíčové pravidlo: klient musí dostat HOTOVÝ KÓD,
který jen zkopíruje. Žádná teorie.

ABSOLUTNÍ PRAVIDLO O PRAVDĚ: Níže máš SKUTEČNĚ ZMĚŘENÁ ZJIŠTĚNÍ z jeho webu.
Diagnostická část musí vycházet výhradně z nich. Co už na webu má, to výslovně uznej
a nenavrhuj to znovu — místo toho to rozšiř. Nikdy netvrď nic, co zjištění nepotvrzují.

Výstup MUSÍ obsahovat přesně tyto sekce:

## 1. MANAŽERSKÉ SHRNUTÍ
Co jsme na webu skutečně našli, co chybí a co se změní po opravě (3–4 věty).

## 2. DIAGNÓZA — CO JSME NA VAŠEM WEBU NAŠLI
Odrážky vázané na změřená zjištění. U každé uveď, zda jde o stav ANO/NE a co to znamená.
Pokud se homepage nebo robots.txt nepodařilo načíst, napiš to otevřeně jako omezení auditu.

## 3. HOTOVÝ ROBOTS.TXT
Kompletní funkční obsah souboru robots.txt v markdown code bloku.
Musí povolovat: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-SearchBot,
PerplexityBot, Google-Extended, Googlebot, Bingbot, Applebot-Extended, CCBot.
Zachovej smysluplné Disallow (košík, administrace). Sitemap řádek na jeho skutečné doméně.

## 4. HOTOVÝ JSON-LD KÓD
Kompletní validní JSON-LD v markdown code bloku (application/ld+json).
Propojená schémata: Organization nebo LocalBusiness, WebSite, Product nebo Service podle
jeho nabídky, plus FAQPage se 3 otázkami, které jeho zákazníci reálně pokládají AI.
Použij JEHO skutečné údaje z popisu (název, obor, region, ceny, záruky).
Pokud už nějaká schémata má, vyjdi z nich a doplň, co chybí.

## 5. NÁVOD NA NAHRÁNÍ — 10 MINUT
Přesné kroky pro platformu, kterou uvedl, a krátce i pro WordPress, Shopify, Shoptet, Wix.

## 6. KONTROLA ZA 7 DNÍ
Tři konkrétní testy, jak si klient sám ověří, že to zabralo (přesný dotaz do ChatGPT,
validator.schema.org, kontrola robots.txt). Uveď realistický časový horizont.

Piš prakticky, technicky přesně, bez marketingové vaty. Výhradně v češtině.

ZMĚŘENÁ ZJIŠTĚNÍ Z WEBU:
{facts}

CO KLIENT NABÍZÍ (jeho vlastní popis):
{description}
"""


def _fallback_teaser(probe: dict) -> dict:
    """Teaser bez AI — poskládaný ze skutečných zjištění, nic si nevymýšlí."""
    h, r = probe.get("html"), probe.get("robots")
    if h is None and r is None:
        return {
            "main_barrier": "Web se nepodařilo načíst, takže jsme nemohli změřit nic. "
                            "Pokud je nedostupný i pro nás, je nedostupný i pro AI crawlery.",
            "consequence": "Dokud web neodpovídá robotům, nemůže se dostat do žádného indexu.",
            "barrier_category": "Chybějící JSON-LD",
        }
    if r is not None and r["wildcard_blocked_all"]:
        return {
            "main_barrier": "Váš robots.txt obsahuje pravidlo `User-agent: *` a `Disallow: /` — "
                            "web tím zakazuje přístup všem robotům bez rozdílu.",
            "consequence": "Dokud tohle pravidlo platí, nezáleží na ničem dalším — crawler obsah nenačte.",
            "barrier_category": "Blokované AI roboty",
        }
    if r is not None and r["ai_blocked"]:
        return {
            "main_barrier": "Váš robots.txt výslovně blokuje tyto AI agenty: "
                            + ", ".join(r["ai_blocked"]) + ".",
            "consequence": "Zablokovaný agent obsah nenačte, takže vás jeho model nemůže citovat.",
            "barrier_category": "Blokované AI roboty",
        }
    if r is not None and not r["ai_mentioned"]:
        return {
            "main_barrier": "Váš robots.txt o moderních AI agentech (GPTBot, ClaudeBot, PerplexityBot) "
                            "vůbec nemluví — nemají explicitní povolení.",
            "consequence": "Část agentů bez explicitního Allow obsah radši nenačte.",
            "barrier_category": "Neinstruované AI roboty",
        }
    if h is not None and h["jsonld_blocks"] == 0:
        return {
            "main_barrier": "Na homepage jsme nenašli žádný blok strukturovaných dat "
                            "(application/ld+json). AI tak nemá strojově čitelnou informaci o tom, "
                            "kdo jste a co nabízíte.",
            "consequence": "Bez schématu firmy a nabídky vás AI v přímé odpovědi nemá podle čeho nabídnout.",
            "barrier_category": "Chybějící JSON-LD",
        }
    if h is not None and not h["has_faq"]:
        return {
            "main_barrier": "Strukturovaná data máte, ale chybí FAQ schéma. "
                            "Nalezené typy: " + (", ".join(h["schema_types"]) or "žádné") + ".",
            "consequence": "FAQPage je nejrychlejší cesta k citaci v přímé odpovědi AI.",
            "barrier_category": "Chybějící FAQ markup",
        }
    if r is not None and not r["has_sitemap"]:
        return {
            "main_barrier": "Základ máte v pořádku, ale robots.txt neodkazuje na sitemap.xml.",
            "consequence": "Crawler pak najde jen to, na co vede odkaz z homepage.",
            "barrier_category": "Chybějící sitemap",
        }
    return {
        "main_barrier": "Základní technické signály máte v pořádku. Prostor je v rozšíření schémat "
                        "na podstránky a v obsahu formulovaném jako odpovědi na konkrétní otázky.",
        "consequence": "Bez citovatelných odstavců AI nemá co vytáhnout, i když web přečte.",
        "barrier_category": "Obsah bez otázek",
    }


def parse_teaser(text: str, probe: dict) -> dict:
    try:
        start, end = text.find("{"), text.rfind("}") + 1
        if start >= 0 and end > start:
            d = json.loads(text[start:end])
            if d.get("main_barrier"):
                return d
    except Exception:
        pass
    return _fallback_teaser(probe)


def _teaser_fallback_allowed() -> bool:
    v = get_config("ALLOW_TEASER_FALLBACK", DEFAULT_ALLOW_TEASER_FALLBACK).strip()
    if not v:  # nenastaveno → zdědí starý společný přepínač
        v = get_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK)
    return v.strip().lower() == "true"


def _report_fallback_allowed() -> bool:
    return get_config("ALLOW_REPORT_FALLBACK",
                      DEFAULT_ALLOW_REPORT_FALLBACK).strip().lower() == "true"


def generate_teaser(probe: dict) -> dict:
    """Teaser je zdarma. Šablona je tu lepší než chybová stránka."""
    client = get_openai_client()
    if client is None:
        if _teaser_fallback_allowed():
            return _fallback_teaser(probe)
        st.error("Chybí OpenAI API klíč.")
        st.stop()
    try:
        text, _used = call_llm(
            client,
            DEFAULT_TEASER_MODEL,
            [
                {"role": "system", "content": "Jsi GEO auditor. Mluvíš pouze o změřených faktech. Odpovídáš POUZE validním JSON objektem."},
                {"role": "user", "content": PROMPT_A + probe_facts_text(probe)},
            ],
            max_out=2000,      # rezerva na reasoning tokeny; platí se jen za skutečně použité
            temperature=0.5,
            effort="low",      # teaser slibuje výsledek do 30 s
        )
        return parse_teaser(text, probe)
    except Exception:
        if _teaser_fallback_allowed():
            return _fallback_teaser(probe)
        st.error("Analýzu se nepodařilo dokončit. Zkuste to prosím znovu.")
        st.stop()


def generate_report(probe: dict, description: str) -> str:
    """Report je placený a obsahuje kód k nasazení.

    Politika selhání je záměrně jiná než u teaseru:
      • API vůbec nejede  → spadne nahlas, ať si toho provozovatel všimne
      • model vrátí nevalidní JSON-LD → jeden opravný pokus, pak deterministická
        šablona, protože fungující šablona je pro zákazníka lepší než rozbitý kód
    """
    client = get_openai_client()
    if client is None:
        if _report_fallback_allowed():
            return _local_report(probe)
        st.error("Report nelze vygenerovat — chybí OpenAI API klíč. "
                 "Napište nám a pošleme ho ručně: " + COMPANY_EMAIL)
        st.stop()

    sys_msg = ("Jsi GEO/AEO konzultant. Generuješ hotový validní kód k nasazení. "
               "Tvrdíš jen to, co potvrzují změřená zjištění. Česky.")
    user_msg = PROMPT_B.format(facts=probe_facts_text(probe), description=description)

    text = None
    try:
        text, _used = call_llm(
            client,
            DEFAULT_REPORT_MODEL,
            [{"role": "system", "content": sys_msg},
             {"role": "user", "content": user_msg}],
            max_out=16000,     # report má 5–8 stran a dva kódové bloky
            temperature=0.4,
            effort="high",     # generuje se kód, tady se nespěchá
        )
    except Exception:
        if _report_fallback_allowed():
            return _local_report(probe)
        st.error("Report se nepodařilo vygenerovat. Napište nám a pošleme ho ručně: "
                 + COMPANY_EMAIL)
        st.stop()

    if report_jsonld_valid(text):
        return text

    # Jeden opravný pokus — nevalidní JSON-LD je pro zákazníka nepoužitelný.
    try:
        fixed, _used = call_llm(
            client,
            DEFAULT_REPORT_MODEL,
            [{"role": "system", "content": sys_msg},
             {"role": "user", "content": user_msg},
             {"role": "assistant", "content": text},
             {"role": "user", "content":
              "JSON-LD blok v sekci 4 není validní JSON, takže by ho zákazník "
              "nemohl nasadit. Vrať CELÝ report znovu ve stejné struktuře, ale "
              "s JSON-LD, který projde `json.loads()` — jeden kódový blok, "
              "bez komentářů, bez koncových čárek, správně uzavřené uvozovky."}],
            max_out=16000,
            temperature=0.2,
            effort="high",
        )
        if report_jsonld_valid(fixed):
            return fixed
    except Exception:
        pass

    # Dvakrát nevalidní → radši ověřená šablona než rozbitý kód.
    return _local_report(probe)


def _local_report(probe: dict) -> str:
    """Report bez AI. Diagnóza vychází ze skutečných zjištění."""
    h, r = probe.get("html"), probe.get("robots")
    base = probe.get("base", "https://www.vasedomena.cz")

    diag = []
    if h is None:
        diag.append("- **Homepage se nepodařilo načíst** (" + str(probe.get("html_error"))
                    + "). Tuto část auditu proto nelze považovat za úplnou. "
                      "Pokud je web nedostupný i pro AI crawlery, nemůže se dostat do žádného indexu.")
    else:
        if h["jsonld_blocks"] == 0:
            diag.append("- **Strukturovaná data: NE.** Na homepage není žádný blok "
                        "`application/ld+json`. AI nemá strojově čitelnou informaci o tom, kdo jste "
                        "a co nabízíte, takže vás v přímé odpovědi nemá podle čeho nabídnout.")
        else:
            diag.append(f"- **Strukturovaná data: ANO** — nalezeno {h['jsonld_blocks']} bloků, typy: "
                        + ", ".join(h["schema_types"]) + ". To je dobrý základ, na kterém se dá stavět.")
            if h["jsonld_invalid"]:
                diag.append(f"- **Pozor: {h['jsonld_invalid']} blok(y) JSON-LD jsou nevalidní** a parser "
                            "je zahodí. Nevalidní schéma je pro AI stejné jako žádné.")
            if not h["has_org"]:
                diag.append("- **Schéma firmy (Organization / LocalBusiness): NE.** AI neví, "
                            "že jste firma, kde sídlíte a jak vás kontaktovat.")
            if not h["has_product_or_service"]:
                diag.append("- **Schéma produktu nebo služby: NE.** AI nezná váš sortiment ani "
                            "cenové rozpětí, takže na dotaz „kdo mi udělá X do Y Kč\" vás nenabídne.")
            if not h["has_faq"]:
                diag.append("- **FAQ schéma: NE.** FAQPage je nejrychlejší cesta k citaci "
                            "v přímé odpovědi — AI cituje odstavce, které odpovídají na konkrétní otázku.")
        if not h["has_og"]:
            diag.append("- **Open Graph meta tagy: NE.** Chybí základní popisná vrstva, "
                        "kterou používají náhledy i některé crawlery.")
        if not h["title"]:
            diag.append("- **Titulek stránky: chybí.** To je nejzákladnější signál vůbec.")
        if not h["h2_questions"]:
            diag.append(f"- **Obsah formulovaný jako otázky: NE.** Z {h['h2_count']} nadpisů H2 "
                        "není žádný ve formě otázky. AI cituje odpovědi na otázky, ne nadpisy "
                        "typu „Naše služby\".")
        else:
            diag.append("- **Obsah formulovaný jako otázky: ANO** — např. „"
                        + h["h2_questions"][0] + "\". Přesně tohle AI cituje, v tom pokračujte.")

    if r is None:
        diag.append("- **robots.txt: nenalezen nebo nedostupný** (" + str(probe.get("robots_error"))
                    + "). Bez něj nemají crawlery žádné instrukce.")
    else:
        if r["wildcard_blocked_all"]:
            diag.append("- **KRITICKÉ: robots.txt obsahuje `User-agent: *` + `Disallow: /`** — "
                        "web blokuje všechny roboty. Tohle je nejzávažnější zjištění tohoto auditu.")
        if r["ai_blocked"]:
            diag.append("- **Blokovaní AI agenti: " + ", ".join(r["ai_blocked"])
                        + ".** Zablokovaný agent obsah nenačte, takže vás jeho model nemůže citovat.")
        if r["ai_allowed"]:
            diag.append("- **Výslovně povolení AI agenti: " + ", ".join(r["ai_allowed"])
                        + ".** To máte správně.")
        if not r["ai_mentioned"]:
            diag.append("- **AI agenti v robots.txt: neuvedeni.** Soubor o GPTBot, ClaudeBot ani "
                        "PerplexityBot vůbec nemluví. Mlčení není souhlas — část agentů bez "
                        "explicitního `Allow` obsah radši nenačte.")
        if not r["has_sitemap"]:
            diag.append("- **Odkaz na sitemap v robots.txt: NE.** Crawler pak najde jen to, "
                        "na co vede odkaz z homepage.")

    diag_text = "\n".join(diag) if diag else "- Zásadní technické bariéry jsme nenašli."

    return """## 1. MANAŽERSKÉ SHRNUTÍ
Stáhli jsme váš robots.txt a homepage a vyhodnotili signály, podle kterých se generativní
vyhledávače rozhodují, zda vás mohou citovat. Níže je diagnóza vycházející výhradně
z toho, co jsme skutečně našli — plus dva hotové soubory, které opraví to, co chybí.
Po jejich nasazení budou AI vyhledávače vaši firmu chápat jako konkrétní entitu s konkrétní
nabídkou, místo nerozlišeného textu.

## 2. DIAGNÓZA — CO JSME NA VAŠEM WEBU NAŠLI

""" + diag_text + """

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

Sitemap: """ + base + """/sitemap.xml
```

## 4. HOTOVÝ JSON-LD KÓD

Vložte celý tento blok do sekce `<head>` na hlavní stránku webu.
Nahraďte hodnoty v uvozovkách svými skutečnými údaji:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "LocalBusiness",
      "@id": \"""" + base + """/#organizace",
      "name": "Název vaší firmy",
      "description": "Jednou vetou konkrétně to, co děláte, pro koho a v jakém regionu.",
      "url": \"""" + base + """/",
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
      "areaServed": { "@type": "Country", "name": "Česká republika" },
      "openingHours": "Mo-Fr 08:00-17:00"
    },
    {
      "@type": "WebSite",
      "@id": \"""" + base + """/#web",
      "url": \"""" + base + """/",
      "name": "Název vaší firmy",
      "inLanguage": "cs-CZ",
      "publisher": { "@id": \"""" + base + """/#organizace" }
    },
    {
      "@type": "Service",
      "name": "Hlavní služba nebo produktová kategorie",
      "provider": { "@id": \"""" + base + """/#organizace" },
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
            "text": "Konkrétní délka záruky a co přesně kryje."
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
2. JSON-LD: plugin *WPCode* → Add Snippet → typ „HTML Snippet" → Location „Site Wide Header".

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

1. **Validita schématu** — otevřete `validator.schema.org`, vložte URL hlavní stránky.
   Musí projít bez chyb (varování „recommended field missing" jsou v pořádku).
2. **Dostupnost pro roboty** — otevřete `""" + base + """/robots.txt` v prohlížeči.
   Musíte tam vidět řádky GPTBot a ClaudeBot.
3. **Reálný test v AI** — napište do ChatGPT (v režimu s vyhledáváním):
   *„Kdo v [vaše město] nabízí [vaše hlavní služba] a jaké má ceny?"*
   Test opakujte po 7, 21 a 45 dnech.

**Realistický horizont:** robots.txt se propaguje za 1–7 dní. Strukturovaná data se v AI
odpovědích začínají projevovat typicky za 3–8 týdnů — indexy generativních vyhledávačů
se neaktualizují v reálném čase. Kdo tvrdí, že vás dostane do ChatGPT „do 48 hodin",
není poctivý. Konkrétní pozici ani zmínku vám nemůže garantovat nikdo, protože o ní
rozhodují algoritmy třetích stran."""


# ─── HTML EXPORT ───────────────────────────────────────────────────────────────
def md_to_html_body(text: str) -> str:
    import html as html_mod
    lines = text.split("\n")
    out, in_code = [], False
    for line in lines:
        if line.strip().startswith("```"):
            out.append("</code></pre>" if in_code else "<pre><code>")
            in_code = not in_code
            continue
        if in_code:
            out.append(html_mod.escape(line))
            continue
        s = line.strip()
        if not s:
            out.append("<br>")
            continue
        if s.startswith("## "):
            out.append("<h2>" + s[3:] + "</h2>")
            continue
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`(.+?)`", r'<code class="inline">\1</code>', s)
        if s.startswith("- "):
            out.append("<li>" + s[2:] + "</li>")
            continue
        out.append("<p>" + s + "</p>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


def score_color(score: int) -> str:
    if score < 0:
        return "#6b7280"
    return "#c0392b" if score < 40 else "#e67e22" if score < 65 else "#27ae60"


def score_label(score: int) -> str:
    if score < 0:
        return "NELZE ZMĚŘIT"
    return "NEVIDITELNÝ ⚠️" if score < 40 else "ČÁSTEČNĚ VIDITELNÝ" if score < 65 else "DOBŘE VIDITELNÝ ✓"


def generate_html_download(report_text: str, probe: dict, description: str, score: int) -> str:
    date_str = datetime.now().strftime("%d. %m. %Y")
    body_html = md_to_html_body(report_text)
    facts_html = md_to_html_body("\n".join("- " + l for l in probe_facts_text(probe).split("\n")))
    color, label = score_color(score), score_label(score)
    score_txt = str(score) if score >= 0 else "?"
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
  .input-box {{ background: #f4f6fb; border-left: 4px solid #1a4a8a; padding: 1rem 1.5rem; border-radius: 6px; margin-bottom: 1.5rem; font-size: 0.9rem; color: #555; }}
  .facts-box {{ background: #fbfbfd; border: 1px solid #dfe4ee; padding: 1rem 1.5rem; border-radius: 6px; margin-bottom: 2rem; font-size: 0.84rem; color: #444; }}
  .facts-box h3 {{ margin: 0 0 .5rem 0; font-size: .95rem; color: #0a2850; }}
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
  <span class="score-box">{score_txt}</span>
  <span class="score-label">AI Visibility Score (0–100)<br><strong>{label}</strong></span>
</div>

<div class="input-box">
  <strong>Auditovaný web:</strong> {probe.get('url','')}<br>
  <strong>Popis nabídky (vaše slova):</strong> {description}
</div>

<div class="facts-box">
  <h3>Co jsme na webu skutečně naměřili</h3>
  {facts_html}
</div>

{body_html}

<div class="footer">
  Batko Digital AI &nbsp;|&nbsp; {UPSELL_EMAIL}<br>
  Report vychází ze stavu webu v okamžiku měření. Konkrétní pozici, zmínku ani citaci
  ve výstupech vyhledávačů a AI asistentů nelze garantovat — rozhodují o ní algoritmy třetích stran.
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


def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return raw
    if not (raw.startswith("http://") or raw.startswith("https://")):
        raw = "https://" + raw
    return raw


def load_demo() -> None:
    st.session_state.url = DEMO_URL
    st.session_state.description = DEMO_DESCRIPTION
    st.session_state.step = "probing"
    st.session_state.demo = True


def render_input(unlocked: bool = False):
    if unlocked:
        st.success("✅ Platba ověřena — přístup odemčen. Zadejte web a nabídku, "
                   "report vygenerujeme rovnou bez dalšího kroku.")
    url = st.text_input("URL vašeho webu nebo e-shopu:", placeholder="www.mujweb.cz", key="url_input")
    desc = st.text_area(
        "Co nabízíte a komu? (čím konkrétněji, tím přesnější kód dostanete)",
        placeholder="Např. 'Prodáváme ručně vyráběný teakový zahradní nábytek na Kladensku, "
                    "rozvoz po ČR, ceny 12–90 tis. Kč, 7 let záruka, web na WordPressu.'",
        height=130,
        key="desc_input",
    )
    st.caption("🔒 Nezadávejte prosím osobní údaje třetích stran. Zadaný text odesíláme "
               "do OpenAI API a nikde jej neukládáme.")
    label = "📄 Vygenerovat můj Fix Report" if unlocked else "🔍 Zkontrolovat mou viditelnost v AI"
    if st.button(label, type="primary", use_container_width=True):
        if not url.strip():
            st.warning("Zadejte prosím adresu svého webu.")
        elif not desc or len(desc.strip()) < 20:
            st.warning("Popište prosím v 1–2 větách, co nabízíte — bez toho nelze vygenerovat funkční kód.")
        else:
            st.session_state.url = normalize_url(url)
            st.session_state.description = desc.strip()
            st.session_state.step = "probing"
            st.rerun()

    if unlocked:
        return

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Čas do výsledku", "< 30 s")
    c2.metric("Hotové soubory", "2 ks")
    c3.metric("Cena v agentuře", "15–40 tis. Kč")

    st.divider()
    st.markdown("### Nevíte, co od auditu čekat?")
    st.caption("Prohlédněte si ukázku na skutečném veřejném webu — zdarma, bez registrace.")
    if st.button("Zobrazit demo zdarma", use_container_width=True, key="btn_demo"):
        load_demo()
        st.rerun()


def render_teaser(t: dict, probe: dict, score: int):
    barrier = t.get("main_barrier", "")
    cons = t.get("consequence", "")
    cat = t.get("barrier_category", "Chybějící JSON-LD")
    color, label = score_color(score), score_label(score)
    score_txt = str(score) if score >= 0 else "?"

    st.markdown(f"""
    <div style="background:#fff8f8;border:2px solid {color};border-radius:12px;padding:1.5rem;margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:1.2rem;">
        <div style="background:{color};color:white;font-size:2.1rem;font-weight:900;border-radius:50%;
                    width:88px;height:88px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
          {score_txt}
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
      <div style="font-weight:700;color:#856404;margin-bottom:0.3rem;">🔴 Co jsme na vašem webu naměřili:</div>
      <div style="color:#533f03;line-height:1.6;">{barrier}</div>
    </div>
    <div style="background:#fce8e8;border-left:4px solid #c0392b;padding:1rem 1.2rem;border-radius:8px;margin-bottom:1rem;">
      <div style="font-weight:700;color:#c0392b;margin-bottom:0.3rem;">💸 Co to znamená:</div>
      <div style="color:#7b241c;">{cons}</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔎 Přesná měřená data (můžete si je ověřit sami)"):
        st.code(probe_facts_text(probe), language="text")
        st.caption("Stáhli jsme váš robots.txt a HTML homepage a vyhodnotili je. "
                   "Nic z výše uvedeného není odhad — vše si můžete zkontrolovat "
                   "ve zdrojovém kódu svého webu.")


def render_paywall():
    payment_link = get_config("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    price_text = get_config("PRICE_TEXT", DEFAULT_PRICE_TEXT)
    link_ready = "YOUR_LINK_HERE" not in (payment_link or "")

    st.markdown("---")
    st.markdown("### 🔓 Získejte hotové opravné soubory na míru")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
**Co dostanete za {price_text}:**
- ✅ **Hotový robots.txt** — povolení pro GPTBot, ClaudeBot, PerplexityBot
- ✅ **Hotový JSON-LD kód** — vaše firma, ceny, služby, FAQ
- ✅ Diagnóza vycházející z reálného měření vašeho webu
- ✅ Návod na nahrání pro WordPress / Shopify / Shoptet / Wix
- ✅ 3 testy, jak si sami ověříte, že to zabralo
- 🎁 **BONUS:** Checklist „12 signálů, podle kterých si vás AI vybere"
        """)
        st.markdown("""
<div style="background:#e8f5e9;border:1px solid #4caf50;border-radius:8px;padding:0.8rem;font-size:0.85rem;margin-top:0.5rem;">
  <strong>💚 Garance nad rámec zákona:</strong><br>
  Pokud vygenerovaný kód nebude použitelný na vašem webu, napište nám do 14 dnů
  od nákupu a vrátíme 100 % ceny — vyřídíme do 24 h. Soubory si přitom můžete nechat.
  Tuto garanci dáváme dobrovolně, nad rámec zákonných práv.
</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
<div style="text-align:center;background:linear-gradient(135deg,#0a2850,#1a4a8a);border-radius:12px;padding:1.5rem;color:white;">
  <div style="font-size:2rem;margin-bottom:0.5rem;">🤖</div>
  <div style="font-size:1.05rem;font-weight:700;margin-bottom:0.3rem;">AI Visibility Fix Report</div>
  <div style="font-size:1.8rem;font-weight:900;color:#ffd700;margin-bottom:.6rem;">{price_text}</div>
  <div style="font-size:.78rem;color:#a0c4ff;">Platba kartou přes bezpečný Stripe</div>
</div>
        """, unsafe_allow_html=True)

    st.markdown("")
    consent = st.checkbox(
        "Souhlasím s tím, aby mi byl digitální obsah zpřístupněn ihned po zaplacení, "
        "a beru na vědomí, že tímto souhlasem mi zaniká právo odstoupit od smlouvy "
        "do 14 dnů (§ 1837 písm. l) občanského zákoníku). Dobrovolná garance vrácení "
        "peněz uvedená výše tím není dotčena.",
        key="consent_1837",
    )

    if not consent:
        st.info("Pro pokračování prosím potvrďte souhlas výše. Bez něj vám nemůžeme "
                "obsah zpřístupnit okamžitě — zákon to neumožňuje.")
    else:
        st.session_state.consent_at = st.session_state.get(
            "consent_at", datetime.now().strftime("%d. %m. %Y %H:%M")
        )
        if link_ready:
            st.link_button("🔐 Zaplatit a získat report", payment_link,
                           type="primary", use_container_width=True)
        else:
            st.warning("Platební odkaz zatím není nastavený. Napište nám na "
                       f"{COMPANY_EMAIL} a pošleme vám ho.")

    st.markdown("---")
    with st.expander("✅ Mám přístupový kód"):
        code_input = st.text_input("Přístupový kód:", type="password", key="code_input")
        if st.button("Odemknout report", type="primary"):
            expected = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)
            if not st.session_state.get("consent_1837"):
                st.error("Nejprve prosím potvrďte souhlas se zpřístupněním obsahu výše.")
            elif expected and code_input.strip() == expected:
                st.session_state.unlocked = True
                st.session_state.step = "generating_report"
                st.rerun()
            else:
                st.error("Nesprávný kód. Po platbě obdržíte kód na potvrzovací stránce.")


def render_report(report_text: str, probe: dict, description: str, score: int):
    st.success("✅ Vaše opravné soubory jsou připravené!")
    consent_at = st.session_state.get("consent_at")
    if consent_at:
        st.caption(f"Potvrzení: dne {consent_at} jste vyjádřil souhlas se zpřístupněním "
                   "digitálního obsahu ihned a s tím, že vám zaniká právo na odstoupení "
                   "od smlouvy do 14 dnů. Dobrovolná garance vrácení peněz do 14 dnů platí dál.")
    st.markdown("---")
    st.markdown(report_text)
    st.markdown("---")

    html_report = generate_html_download(report_text, probe, description, score)
    html_checklist = generate_checklist_html()

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Stáhnout AI Visibility Fix Report (HTML)",
            data=html_report.encode("utf-8"),
            file_name=f"AI_Visibility_Fix_Report_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html", use_container_width=True, type="primary",
        )
    with col2:
        st.download_button(
            label="🎁 Stáhnout Bonus Checklist",
            data=html_checklist.encode("utf-8"),
            file_name="12_signalu_AI_visibility_2026.html",
            mime="text/html", use_container_width=True,
        )

    st.caption("💡 Tip: Soubory otevřete v prohlížeči a vytiskněte jako PDF (Ctrl+P → Uložit jako PDF).")

    # Přístupový kód pro pozdější návrat — aby zákazník o přístup nepřišel zavřením okna.
    code = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)
    if code and st.session_state.get("unlocked"):
        st.markdown("---")
        st.markdown(
            f"""
<div style="background:#fffbea;border:1.5px solid #f0c000;border-radius:10px;padding:1rem 1.3rem;">
  <div style="font-weight:700;color:#7a5c00;margin-bottom:.4rem;">🔑 Uschovejte si přístupový kód</div>
  <div style="color:#5c4600;font-size:.92rem;line-height:1.6;">
    Kdybyste okno zavřel a chtěl se k reportu vrátit, otevřete aplikaci znovu,
    rozbalte „Mám přístupový kód" a zadejte:
  </div>
  <div style="font-family:Consolas,'Courier New',monospace;font-size:1.5rem;font-weight:800;
              color:#13231b;background:#fff;border:1.5px dashed #f0c000;border-radius:8px;
              padding:.6rem 1rem;margin:.7rem 0 .4rem;text-align:center;letter-spacing:.06em;">
    {code}
  </div>
  <div style="color:#8a7300;font-size:.8rem;">
    Doporučujeme rovnou stáhnout oba soubory výše — máte je pak natrvalo u sebe.
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    upsell_price = get_config("UPSELL_PRICE", DEFAULT_UPSELL_PRICE)
    st.markdown("---")
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0a2850,#1a4a8a);border-radius:12px;padding:1.8rem;color:white;text-align:center;margin-top:1rem;">
  <div style="font-size:1.5rem;font-weight:700;margin-bottom:0.5rem;">🚀 Nechcete se hrabat v kódu?</div>
  <div style="color:#a0c4ff;margin-bottom:1.2rem;max-width:520px;margin-left:auto;margin-right:auto;">
    Víte přesně, co nahrát. Nahrát to ale musíte. Pokud na to není čas ani chuť, uděláme to za vás.
  </div>
  <div style="background:rgba(255,255,255,.1);border-radius:8px;padding:1rem 1.5rem;margin-bottom:1.2rem;text-align:left;max-width:480px;margin-left:auto;margin-right:auto;">
    <strong>Balíček „AI Visibility na klíč":</strong><br>
    ✅ Nahrajeme robots.txt i JSON-LD přímo na váš web<br>
    ✅ Rozšíříme schémata na všechny podstatné podstránky<br>
    ✅ Přepíšeme 5 klíčových odstavců do citovatelné podoby<br>
    ✅ Kontrolní měření po 30 dnech se stejnou metodikou
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

            "**1. Předmět plnění.** Digitální produkt „AI Visibility Fix Report\" — HTML report "
            "obsahující diagnostiku webu kupujícího, vygenerovaný obsah souboru robots.txt, "
            "vygenerovaný kód JSON-LD, návod na nasazení a bonusový checklist. Obsah se zobrazí "
            "a je ke stažení v aplikaci ihned po zadání přístupového kódu, který kupující obdrží "
            "na potvrzovací stránce po zaplacení.  \n\n"

            "**2. Charakter plnění.** Report má konzultační a technicko-informační charakter. "
            "Diagnostická část vychází ze stavu webu v okamžiku měření (stažení souboru robots.txt "
            "a HTML úvodní stránky). Prodávající **negarantuje** konkrétní pozici, zmínku ani citaci "
            "ve výstupech vyhledávačů či AI asistentů — o těch rozhodují algoritmy a indexační cykly "
            "třetích stran, které prodávající neovlivňuje. Report není právním ani daňovým poradenstvím.  \n\n"

            "**3. Odstoupení od smlouvy.** Kupující má jako spotřebitel právo odstoupit od smlouvy "
            "do 14 dnů. Toto právo mu **zaniká**, pokud před zpřístupněním obsahu udělí výslovný souhlas "
            "se započetím plnění před uplynutím lhůty a potvrdí, že tím právo na odstoupení pozbývá "
            "(§ 1837 písm. l) občanského zákoníku). Souhlas se udílí zaškrtnutím políčka v aplikaci "
            "před zpřístupněním obsahu; jeho potvrzení se kupujícímu zobrazí u vygenerovaného reportu. "
            "Bez tohoto souhlasu nelze obsah zpřístupnit okamžitě a kupujícímu 14denní lhůta zůstává.  \n\n"

            "**4. Dobrovolná garance vrácení peněz.** Nad rámec zákonných práv prodávající "
            "poskytuje záruku spokojenosti: pokud vygenerovaný kód není použitelný na webu kupujícího, "
            "kupující o vrácení požádá e-mailem do 14 dnů od nákupu a prodávající vrátí 100 % ceny — "
            "vyřízení do 24 hodin od žádosti, výplata přes Stripe. Stažené soubory si kupující může "
            "ponechat. Tato garance platí i tehdy, když kupující udělil souhlas podle bodu 3.  \n\n"

            "**5. Mimosoudní řešení sporů.** Česká obchodní inspekce, www.coi.cz.  \n\n"

            f"Dotazy: [{COMPANY_EMAIL}](mailto:{COMPANY_EMAIL})"
        )

    with st.expander("Ochrana soukromí (GDPR)"):
        st.markdown(
            f"**Správce:** {COMPANY_NAME}, {COMPANY_PERSON}, IČO {COMPANY_ICO}, {COMPANY_ADDRESS}, "
            f"[{COMPANY_EMAIL}](mailto:{COMPANY_EMAIL}).  \n\n"

            "**Co zpracováváme a proč**  \n"
            "1. *Údaje, které zadáte do formuláře* (URL webu a popis nabídky). Odesíláme je do "
            "OpenAI API za jediným účelem — vygenerovat váš report. Právní základ: plnění smlouvy, "
            "resp. oprávněný zájem u bezplatného auditu.  \n"
            "2. *Obsah vašeho webu* — stahujeme veřejně dostupný soubor robots.txt a HTML úvodní "
            "stránky zadané adresy. Jde o veřejně publikovaná data.  \n"
            "3. *Technické provozní údaje* — aplikace je hostována na Streamlit Community Cloud "
            "(Snowflake Inc., USA). Poskytovatel hostingu zpracovává provozní logy, které mohou "
            "obsahovat IP adresu a informace o prohlížeči.  \n\n"

            "**Co neděláme**  \n"
            "Zadaný text ani vygenerovaný report nikde neukládáme — po ukončení práce v aplikaci "
            "zmizí. Nevytváříme databázi zákazníků z auditů, neprofilujeme a nepředáváme data "
            "pro marketingové účely.  \n\n"

            "**Zpracovatelé a přenos mimo EU**  \n"
            "Generování obsahu zajišťuje OpenAI jako zpracovatel; podmínky se řídí zpracovatelskou "
            "smlouvou OpenAI (openai.com/policies/data-processing-addendum). Hosting zajišťuje "
            "Snowflake Inc. Zpracování může probíhat mimo EU/EHP, a to na základě standardních "
            "smluvních klauzulí Evropské komise.  \n\n"

            "**Prosba**  \n"
            "Do formuláře nezadávejte osobní údaje třetích stran ani citlivé firemní informace. "
            "K vygenerování reportu je potřeba jen adresa webu a věcný popis toho, co nabízíte. "
            "Uvědomte si, že adresa webu může sama být osobním údajem (např. u živnostníka "
            "s vlastním jménem v domeně) — zadáváte ji vy a na základě svého rozhodnutí.  \n\n"

            "**Vaše práva**  \n"
            "Máte právo na přístup, opravu, výmaz, omezení zpracování, přenositelnost a vznesení "
            "námitky. Protože data neukládáme, u většiny žádostí není co vydat ani mazat. "
            f"Žádosti a dotazy: [{COMPANY_EMAIL}](mailto:{COMPANY_EMAIL}). "
            "Stížnost lze podat u Úřadu pro ochranu osobních údajů (uoou.gov.cz)."
        )

    with st.expander("Vrácení peněz"):
        st.markdown(
            "**Dobrovolná garance spokojenosti.** Pokud vygenerovaný kód není použitelný "
            "na vašem webu, napište nám do 14 dnů od nákupu na "
            f"[{COMPANY_EMAIL}](mailto:{COMPANY_EMAIL}) — uveďte e-mail použitý při platbě "
            "nebo číslo objednávky ze Stripe. Vrátíme 100 % ceny, žádost vyřídíme do 24 hodin, "
            "výplata jde přes Stripe zpět na kartu. Stažené soubory si můžete ponechat.  \n\n"

            "**Zákonné odstoupení od smlouvy.** Před zpřístupněním reportu potvrzujete souhlas "
            "s okamžitým dodáním, čímž vám zákonné 14denní právo na odstoupení zaniká "
            "(§ 1837 písm. l) OZ) — viz bod 3 obchodních podmínek. Dobrovolná garance výše "
            "tím dotčena není a platí nezávisle na tom.  \n\n"

            "Jinými slovy: i když se zákonného práva vzdáte, my vám peníze vrátíme."
        )

    st.markdown(
        f"<div style='font-size:.73rem;color:#9ca3af;text-align:center;padding:.7rem 0 .3rem'>"
        f"{COMPANY_NAME} &nbsp;·&nbsp; IČO {COMPANY_ICO} &nbsp;·&nbsp; {COMPANY_ADDRESS}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def _check_url_unlock():
    """Umožní Stripe potvrzovací stránce doručit přístup přes ?unlock=<kód>."""
    if st.session_state.get("url_unlock_checked"):
        return
    st.session_state.url_unlock_checked = True
    expected = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)
    if not expected:
        return
    try:
        params = st.query_params
        supplied = params.get("unlock")
    except Exception:
        return
    if isinstance(supplied, list):
        supplied = supplied[0] if supplied else None
    if supplied and str(supplied).strip() == expected:
        st.session_state.unlocked = True
        st.session_state.consent_at = st.session_state.get(
            "consent_at", datetime.now().strftime("%d. %m. %Y %H:%M")
        )


def _reset():
    for k in ["step", "teaser", "url", "description", "report", "probe", "score",
              "consent_1837", "consent_at", "unlocked", "demo"]:
        st.session_state.pop(k, None)


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🤖", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)
    render_header()

    _check_url_unlock()

    if "step" not in st.session_state:
        st.session_state.step = "input"

    step = st.session_state.step
    unlocked = bool(st.session_state.get("unlocked"))

    # Ochrana proti nekonzistentnimu session_state (napr. kdyz se appka
    # znovu nasadi, zatimco ma nekdo rozdelanou praci ve starsi verzi).
    _potreba = {
        "probing": ["url"],
        "teaser": ["teaser", "probe", "score"],
        "generating_report": ["probe"],
        "report": ["report", "probe"],
    }
    if step in _potreba and any(k not in st.session_state for k in _potreba[step]):
        _reset()
        st.session_state.step = "input"
        step = "input"
        st.warning("Aplikace byla mezitím aktualizována, takže jsme museli začít znovu. "
                   "Zadejte prosím adresu webu ještě jednou — zabere to 10 sekund.")

    if step == "input":
        render_input(unlocked=unlocked)

    elif step == "probing":
        with st.spinner("Stahujeme váš robots.txt a homepage a vyhodnocujeme signály..."):
            probe = probe_website(st.session_state.url)
            score = compute_score(probe)
        st.session_state.probe = probe
        st.session_state.score = score
        if unlocked:
            st.session_state.step = "generating_report"
        else:
            with st.spinner("Formulujeme závěr..."):
                st.session_state.teaser = generate_teaser(probe)
            st.session_state.step = "teaser"
        st.rerun()

    elif step == "teaser":
        render_teaser(st.session_state.teaser, st.session_state.probe, st.session_state.score)
        render_paywall()
        if st.button("← Začít znovu", key="restart_teaser"):
            _reset()
            st.rerun()

    elif step == "generating_report":
        with st.spinner("Generujeme robots.txt a JSON-LD kód na míru (30–50 sekund)..."):
            st.session_state.report = generate_report(
                st.session_state.probe, st.session_state.get("description", "")
            )
        st.session_state.step = "report"
        st.rerun()

    elif step == "report":
        render_report(
            st.session_state.report,
            st.session_state.probe,
            st.session_state.get("description", ""),
            st.session_state.get("score", -1),
        )
        if st.button("← Nový audit", key="restart_report"):
            _reset()
            st.rerun()

    render_footer()


if __name__ == "__main__":
    main()
