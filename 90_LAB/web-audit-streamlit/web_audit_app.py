"""
web_audit_app.py – SEO Audit webu jako Streamlit SaaS

Vzor: stejná struktura jako diagnóza neprodaného auta.
Použití:
    streamlit run web_audit_app.py

Secrets (Streamlit Cloud nebo .streamlit/secrets.toml):
    OPENAI_API_KEY = "sk-..."
    PAYMENT_LINK   = "https://buy.stripe.com/..."
    ACCESS_CODE    = "tajnykod123"        # volitelné – manuální odemčení
    UNLOCK_VERIFY_URL = "https://..."     # volitelné – webhook ověření kódu
    LEAD_WEBHOOK_URL  = "https://..."     # volitelné – zápis leadu
    PRICE_TEXT     = "499 Kč včetně DPH"
"""

import json
import os
import re
import socket
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.error import URLError
from urllib.parse import urlsplit, unquote_plus, urlencode, parse_qsl, urlunsplit
from urllib.request import Request, urlopen
from html.parser import HTMLParser

import streamlit as st
from openai import OpenAI


# ── konfigurace ──────────────────────────────────────────────────────────────

APP_TITLE    = "SEO Audit webu"
APP_SUBTITLE = "Zjistěte za 2 minuty, proč váš web nenachází zákazníky na Googlu."

DEFAULT_PAYMENT_LINK          = "https://buy.stripe.com/your-payment-link"
DEFAULT_PRICE_TEXT            = "499 Kč včetně DPH"
DEFAULT_ACCESS_CODE           = ""
DEFAULT_OPENAI_MODEL          = "gpt-4.1-mini"
DEFAULT_ALLOW_LOCAL_FALLBACK  = "true"
DEFAULT_REQUIRE_LEAD_WEBHOOK  = "false"


# ── demo konstanty ────────────────────────────────────────────────────────────

DEMO_URL = "https://www.pizzeria-bella-vista.cz"  # fiktivní ukázkový web

DEMO_SITE_DATA: Dict = {
    "url": DEMO_URL,
    "https": True,
    "title": "Pizza Bella Vista",
    "title_len": 18,
    "description": "",
    "desc_len": 0,
    "h1s": ["Vítejte v Bella Vista", "Nejlepší pizza ve městě"],
    "h2s": ["Naše pizza", "Klasická pizza", "Speciální pizza", "Nápoje", "Kontakt"],
    "viewport": True,
    "canonical": "",
    "robots": "",
    "og_title": "",
    "og_description": "",
    "total_imgs": 12,
    "img_without_alt": 9,
    "word_count": 180,
    "error": None,
}

DEMO_SCORE_DATA: Dict = {
    "score": 42,
    "issues": [
        {"sev": "⚠️", "text": 'Title je příliš krátký (18 znaků). Doporučeno 50–60 znaků.'},
        {"sev": "❌", "text": "Chybí meta description – Google si vybere libovolný text ze stránky, obvykle nevhodný."},
        {"sev": "⚠️", "text": "Stránka má 2 nadpisy H1 – správně má být jen jeden."},
        {"sev": "⚠️", "text": "Málo textu na stránce (180 slov). Google preferuje stránky s alespoň 300 slovy."},
        {"sev": "⚠️", "text": "9 z 12 obrázků nemá alt text – Google je nemůže indexovat."},
        {"sev": "ℹ️", "text": "Chybí canonical tag – pomáhá Googlu určit preferovanou verzi stránky."},
    ],
}

DEMO_REPORT = """\
**Web:** https://www.pizzeria-bella-vista.cz
**SEO skóre:** 42/100 – Slabý

---

**Web a situace:**
Pizzeria Bella Vista má web se základní prezentací menu a kontaktu. Web běží na HTTPS \
a je mobilní – to je dobrý základ. Technické základy SEO jsou ale v takovém stavu, že Google \
web zobrazuje výrazně níže, než odpovídá jeho skutečné kvalitě. Místní zákazníci hledající \
„pizza [město]" nebo „pizzeria rozvoz" ho pravděpodobně vůbec nenajdou.

**Hlavní brzda viditelnosti:**
Chybí meta description a title je příliš krátký. Google neví, jak stránku prezentovat \
ve výsledcích vyhledávání – buď si vybere náhodný text, nebo web přeskočí ve prospěch \
konkurence, která to má správně nastavené.

**Co vidí Google:**
- ⚠️ **Title „Pizza Bella Vista" má jen 18 znaků** – měl by obsahovat klíčová slova \
jako „rozvoz pizzy", „pizza [město]" a mít 50–60 znaků
- ❌ **Chybí meta description** – popis zobrazovaný pod názvem webu v Googlu; zákazníci \
vidí náhodný text a neklikají
- ⚠️ **Dva nadpisy H1** – Google preferuje jediný hlavní nadpis, který jasně říká, \
o čem stránka je
- ⚠️ **Málo textu (180 slov)** – Google nemá dostatek obsahu k pochopení, čím se \
pizzeria odlišuje
- ⚠️ **9 z 12 obrázků nemá alt text** – fotky pizzy, které pomáhají prodávat, \
Google vůbec nevidí

**Akční plán na 7 dní:**
1. **Den 1–2:** Napište nový title – např. *„Pizza Bella Vista | Rozvoz pizzy v Brně | \
Čerstvé ingredience"*
2. **Den 2–3:** Doplňte meta description – 140–160 znaků s popisem pizzerie a výzvou \
k akci
3. **Den 3–4:** Sjednoťte H1 na jeden výstižný nadpis, ostatní převeďte na H2
4. **Den 4–5:** Doplňte alt texty ke všem obrázkům – popište, co je na fotce \
(„margherita pizza s čerstvou bazalkou")
5. **Den 5–7:** Rozšiřte text hlavní stránky na min. 300 slov – přidejte příběh \
podniku, speciality a oblast rozvozu

**Co se stane, když to neopravíte:**
Konkurenční pizzerie, která má tyto základy v pořádku, bude ve výsledcích Googlu výše. \
Při 50–100 vyhledáváních za měsíc v lokalitě to znamená desítky ztracených zákazníků \
měsíčně. Situace se nezlepší sama od sebe.

**Doporučený další krok:**
- 🔧 **Technická oprava kritických chyb** (title, description, H1, alt texty): \
**990 Kč včetně DPH** – hotovo do 48 hodin
- 📋 **Kompletní SEO audit s přepisem textů**: **2 490 Kč včetně DPH** – nové texty \
pro celý web optimalizované pro Google
- 📅 **Měsíční SEO péče**: **1 990 Kč/měsíc včetně DPH** – průběžné sledování, obsah, \
reporty

---
*Toto je ukázková analýza fiktivního webu. Pro audit vašeho webu klikněte na \
„Začít znovu" a zadejte svou adresu.*
"""


def get_config(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def get_bool_config(name: str, default: str = "false") -> bool:
    value = get_config(name, default)
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def first_query_value(name: str, default: str = "") -> str:
    value = st.query_params.get(name, default)
    if isinstance(value, list):
        value = value[0] if value else default
    return unquote_plus(str(value or default)).strip()


def append_url_params(url: str, params: Dict[str, str]) -> str:
    if not url:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update({k: v for k, v in params.items() if v})
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def make_lead_id(url: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    domain = urlsplit(url).netloc.replace("www.", "") or "web"
    safe = re.sub(r"[^a-zA-Z0-9]", "-", domain)[:30]
    return f"audit-{safe}-{ts}"


# ── česká pluralizace ─────────────────────────────────────────────────────────

def pluralize_cs(n: int, singular: str, few: str, many: str) -> str:
    """Vrátí správný tvar: 1 → singular, 2–4 → few, 5+ → many."""
    if n == 1:
        return f"{n} {singular}"
    if 2 <= n <= 4:
        return f"{n} {few}"
    return f"{n} {many}"


# ── HTML parser pro základní SEO kontrolu ────────────────────────────────────

class _SEOParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.description = ""
        self.h1s: List[str] = []
        self.h2s: List[str] = []
        self.viewport = False
        self.canonical = ""
        self.robots = ""
        self.og_title = ""
        self.og_description = ""
        self._in_title = False
        self._current_h1 = ""
        self._in_h1 = False
        self._current_h2 = ""
        self._in_h2 = False
        self.word_count = 0
        self.img_without_alt = 0
        self.total_imgs = 0
        self._body_text = []
        self._in_body = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description":
                self.description = content
            elif name == "viewport":
                self.viewport = True
            elif name == "robots":
                self.robots = content
            elif prop == "og:title":
                self.og_title = content
            elif prop == "og:description":
                self.og_description = content
        elif tag == "link":
            if attrs_dict.get("rel", "").lower() == "canonical":
                self.canonical = attrs_dict.get("href", "")
        elif tag == "h1":
            self._in_h1 = True
            self._current_h1 = ""
        elif tag == "h2":
            self._in_h2 = True
            self._current_h2 = ""
        elif tag == "img":
            self.total_imgs += 1
            if not attrs_dict.get("alt", "").strip():
                self.img_without_alt += 1
        elif tag == "body":
            self._in_body = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "h1":
            if self._current_h1.strip():
                self.h1s.append(self._current_h1.strip())
            self._in_h1 = False
        elif tag == "h2":
            if self._current_h2.strip():
                self.h2s.append(self._current_h2.strip())
            self._in_h2 = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_h1:
            self._current_h1 += data
        if self._in_h2:
            self._current_h2 += data
        if self._in_body:
            self._body_text.append(data)

    def get_word_count(self) -> int:
        text = " ".join(self._body_text)
        return len(text.split())


def fetch_and_parse(url: str, timeout: int = 10) -> Optional[Dict]:
    """Stáhne URL a vrátí základní SEO data. Bez externích závislostí."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        req = Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; SEOAuditBot/1.0; "
                    "+https://batkodigitalai.com)"
                ),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "cs,en;q=0.9",
            },
        )
        with urlopen(req, timeout=timeout) as resp:
            final_url = resp.geturl()
            html = resp.read().decode(
                resp.headers.get_content_charset("utf-8"), errors="replace"
            )
    except Exception as exc:
        return {"error": str(exc), "url": url}

    parser = _SEOParser()
    try:
        parser.feed(html)
    except Exception:
        pass

    https_ok = final_url.startswith("https://")
    word_count = parser.get_word_count()

    return {
        "url": final_url,
        "https": https_ok,
        "title": parser.title.strip(),
        "title_len": len(parser.title.strip()),
        "description": parser.description.strip(),
        "desc_len": len(parser.description.strip()),
        "h1s": parser.h1s,
        "h2s": parser.h2s[:10],
        "viewport": parser.viewport,
        "canonical": parser.canonical,
        "robots": parser.robots,
        "og_title": parser.og_title,
        "og_description": parser.og_description,
        "total_imgs": parser.total_imgs,
        "img_without_alt": parser.img_without_alt,
        "word_count": word_count,
        "error": None,
    }


def compute_score(data: Dict) -> Dict:
    """Vypočítá skóre a vrátí dict s body a problémy."""
    issues = []
    score = 100

    # HTTPS
    if not data.get("https"):
        issues.append({"sev": "❌", "text": "Web nepoužívá HTTPS – Google ho penalizuje a prohlížeče zobrazují varování."})
        score -= 20

    # Title
    title_len = data.get("title_len", 0)
    if title_len == 0:
        issues.append({"sev": "❌", "text": "Chybí tag <title> – Google neví, jak stránku pojmenovat ve výsledcích vyhledávání."})
        score -= 20
    elif title_len < 30:
        issues.append({"sev": "⚠️", "text": f"Title je příliš krátký ({title_len} znaků). Doporučená délka je 50–60 znaků."})
        score -= 10
    elif title_len > 65:
        issues.append({"sev": "⚠️", "text": f"Title je příliš dlouhý ({title_len} znaků) – Google ho ořízne. Maximum je 60 znaků."})
        score -= 5

    # Meta description
    desc_len = data.get("desc_len", 0)
    if desc_len == 0:
        issues.append({"sev": "❌", "text": "Chybí meta description – Google si vybere libovolný text ze stránky, obvykle nevhodný."})
        score -= 15
    elif desc_len < 70:
        issues.append({"sev": "⚠️", "text": f"Meta description je příliš krátký ({desc_len} znaků). Ideální délka je 140–160 znaků."})
        score -= 7
    elif desc_len > 165:
        issues.append({"sev": "⚠️", "text": f"Meta description je příliš dlouhý ({desc_len} znaků) – Google ho ořízne ve výsledcích."})
        score -= 3

    # H1
    h1s = data.get("h1s", [])
    if len(h1s) == 0:
        issues.append({"sev": "❌", "text": "Chybí nadpis H1 – hlavní signál pro Google, o čem stránka je."})
        score -= 15
    elif len(h1s) > 1:
        issues.append({
            "sev": "⚠️",
            "text": f"Stránka má {pluralize_cs(len(h1s), 'nadpis H1', 'nadpisy H1', 'nadpisů H1')} – správně má být jen jeden.",
        })
        score -= 8

    # Viewport
    if not data.get("viewport"):
        issues.append({"sev": "❌", "text": "Chybí viewport meta tag – web pravděpodobně není mobilní. Google upřednostňuje weby přizpůsobené mobilu."})
        score -= 15

    # Obsah
    word_count = data.get("word_count", 0)
    if word_count < 200:
        issues.append({"sev": "⚠️", "text": f"Na stránce je málo textu ({word_count} slov). Google preferuje stránky s alespoň 300 slovy."})
        score -= 10
    elif word_count > 3000:
        issues.append({"sev": "ℹ️", "text": f"Na stránce je hodně textu ({word_count} slov). Ujistěte se, že je dobře strukturovaný a čitelný."})

    # Obrázky bez alt textu
    img_no_alt = data.get("img_without_alt", 0)
    total_imgs = data.get("total_imgs", 0)
    if img_no_alt > 0:
        issues.append({
            "sev": "⚠️",
            "text": (
                f"{pluralize_cs(img_no_alt, 'obrázek', 'obrázky', 'obrázků')} "
                f"z {total_imgs} nemá alt text – Google tyto obrázky nemůže indexovat."
            ),
        })
        score -= min(img_no_alt * 2, 8)

    # Canonical
    if not data.get("canonical"):
        issues.append({"sev": "ℹ️", "text": "Chybí canonical tag – pomáhá Googlu určit preferovanou verzi stránky."})
        score -= 3

    score = max(0, min(100, score))
    return {"score": score, "issues": issues}


def score_label(score: int) -> str:
    if score >= 80:
        return "Dobrý"
    if score >= 55:
        return "Průměrný"
    if score >= 30:
        return "Slabý"
    return "Kritický"


def score_color(score: int) -> str:
    if score >= 80:
        return "#16a34a"
    if score >= 55:
        return "#d97706"
    if score >= 30:
        return "#ea580c"
    return "#dc2626"


# ── kroky (doplňující otázky) ─────────────────────────────────────────────────

STEPS: List[Dict[str, str]] = [
    {
        "key": "goal",
        "label": "Váš cíl",
        "prompt": "Co je hlavní cíl vašeho webu? (získat zákazníky, prodat produkt, prezentovat služby, jiné)",
        "placeholder": "Např.: chceme získávat poptávky od místních zákazníků na rekonstrukce koupelen...",
    },
    {
        "key": "traffic",
        "label": "Návštěvnost",
        "prompt": "Jak jste spokojeni s návštěvností z Googlu? Kolik lidí web navštíví měsíčně (odhadem)?",
        "placeholder": "Např.: z Googlu chodí skoro nikdo, Google Analytics ukazuje 50 lidí za měsíc...",
    },
    {
        "key": "history",
        "label": "Historie webu",
        "prompt": "Jak starý je web a dělali jste někdy úpravy pro Google (SEO, texty, technické změny)?",
        "placeholder": "Např.: web máme 3 roky, nikdy jsme SEO nedělali, texty psal kolega od oka...",
    },
]


# ── state ─────────────────────────────────────────────────────────────────────

def init_state() -> None:
    url_from_query = first_query_value("url")
    defaults = {
        "input_url": url_from_query,
        "url_submitted": bool(url_from_query),
        "site_data": None,
        "site_score": None,
        "lead_id": make_lead_id(url_from_query) if url_from_query else "",
        "contact": {},
        "contact_submitted": False,
        "lead_saved": False,
        "step_index": 0,
        "answers": {},
        "unlocked": False,
        "final_report": None,
        "free_preview": None,
        "last_error": None,
        "demo_mode": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_app() -> None:
    keys = [
        "input_url", "url_submitted", "site_data", "site_score",
        "lead_id", "contact", "contact_submitted", "lead_saved",
        "step_index", "answers", "unlocked", "final_report",
        "free_preview", "last_error", "demo_mode",
    ]
    for k in keys:
        st.session_state.pop(k, None)
    st.rerun()


def activate_demo() -> None:
    """Okamžitě zobrazí ukázkový výsledek bez zadávání URL nebo kontaktu."""
    keys = [
        "input_url", "url_submitted", "site_data", "site_score",
        "lead_id", "contact", "contact_submitted", "lead_saved",
        "step_index", "answers", "unlocked", "final_report",
        "free_preview", "last_error", "demo_mode",
    ]
    for k in keys:
        st.session_state.pop(k, None)

    st.session_state.demo_mode = True
    st.session_state.input_url = DEMO_URL
    st.session_state.url_submitted = True
    st.session_state.site_data = {**DEMO_SITE_DATA}
    st.session_state.site_score = {
        "score": DEMO_SCORE_DATA["score"],
        "issues": list(DEMO_SCORE_DATA["issues"]),
    }
    st.session_state.lead_id = "demo-pizzeria-bella-vista"
    st.session_state.answers = {
        "goal": "Získávat zákazníky přes internet a zvýšit rozvoz v okolí.",
        "traffic": "Z Googlu chodí skoro nikdo – odhadem 80 návštěv za měsíc.",
        "history": "Web máme 2 roky, SEO jsme nikdy nedělali, texty psal majitel.",
    }
    st.session_state.contact = {
        "name": "Jan Novák",
        "email": "jan.novak@example.cz",
        "phone": "777 123 456",
        "consent": True,
    }
    st.session_state.contact_submitted = True
    st.session_state.lead_saved = True
    st.session_state.step_index = len(STEPS)
    st.session_state.unlocked = True
    st.session_state.final_report = DEMO_REPORT
    st.session_state.free_preview = None
    st.session_state.last_error = None
    st.rerun()


# ── lead / webhook ────────────────────────────────────────────────────────────

def build_lead_payload() -> Dict:
    contact = st.session_state.contact
    answers = st.session_state.answers
    data = st.session_state.site_data or {}
    score_data = st.session_state.site_score or {}
    ts = datetime.now(timezone.utc).isoformat()
    return {
        "formType": "SEO_Audit_Webu",
        "event_type": "lead_free_preview_requested",
        "lead_id": st.session_state.lead_id,
        "created_at": ts,
        "name": contact.get("name", ""),
        "email": contact.get("email", ""),
        "phone": contact.get("phone", ""),
        "source": "streamlit_web_audit",
        "url": data.get("url", st.session_state.input_url),
        "seo_score": score_data.get("score", ""),
        "issues_count": len(score_data.get("issues", [])),
        "goal": answers.get("goal", ""),
        "traffic": answers.get("traffic", ""),
        "history": answers.get("history", ""),
        "contact": contact,
        "answers": answers,
        "site_data": {k: v for k, v in data.items() if k != "error"},
    }


def post_lead_payload(payload: Dict) -> None:
    webhook_url = get_config("LEAD_WEBHOOK_URL", "")
    if not webhook_url:
        if get_bool_config("REQUIRE_LEAD_WEBHOOK", DEFAULT_REQUIRE_LEAD_WEBHOOK):
            raise RuntimeError("Chybí LEAD_WEBHOOK_URL.")
        return
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=8) as resp:
            if resp.status >= 400:
                raise RuntimeError(f"Webhook selhal se stavem {resp.status}.")
    except URLError as exc:
        raise RuntimeError("Zápis kontaktu se nepodařil.") from exc


def verify_unlock_token(token: str) -> bool:
    verify_url = get_config("UNLOCK_VERIFY_URL", "")
    if not verify_url:
        access_code = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)
        return bool(access_code) and token.strip() == access_code
    payload = {
        "action": "verify_unlock_token",
        "lead_id": st.session_state.lead_id,
        "token": token.strip(),
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = Request(
        verify_url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=8) as resp:
            result = json.loads(resp.read().decode("utf-8") or "{}")
            return bool(result.get("valid"))
    except Exception:
        return False


# ── AI generování ─────────────────────────────────────────────────────────────

def get_openai_client() -> Optional[OpenAI]:
    api_key = get_config("OPENAI_API_KEY")
    if not api_key:
        return None
    base_url = get_config("OPENAI_BASE_URL", "")
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def build_audit_summary() -> str:
    data = st.session_state.site_data or {}
    score_data = st.session_state.site_score or {}
    answers = st.session_state.answers
    contact = st.session_state.contact
    issues = score_data.get("issues", [])
    issues_text = "\n".join(f"- [{i['sev']}] {i['text']}" for i in issues)

    lines = [
        f"Lead ID: {st.session_state.lead_id}",
        f"Jméno: {contact.get('name', '')}",
        f"E-mail: {contact.get('email', '')}",
        f"Telefon: {contact.get('phone', '')}",
        f"URL: {data.get('url', '')}",
        f"HTTPS: {'ano' if data.get('https') else 'NE'}",
        f"Title ({data.get('title_len', 0)} znaků): {data.get('title', '')}",
        f"Meta description ({data.get('desc_len', 0)} znaků): {data.get('description', '')}",
        f"H1 tagy: {', '.join(data.get('h1s', [])) or 'žádný'}",
        f"H2 tagy (prvních 5): {', '.join(data.get('h2s', [])[:5]) or 'žádný'}",
        f"Viewport: {'ano' if data.get('viewport') else 'NE'}",
        f"Canonical: {data.get('canonical', 'chybí')}",
        f"Počet slov: {data.get('word_count', 0)}",
        f"Obrázky bez alt textu: {data.get('img_without_alt', 0)} z {data.get('total_imgs', 0)}",
        f"SEO skóre: {score_data.get('score', 0)}/100",
        f"\nNalezené problémy:\n{issues_text}",
        f"\nCíl webu: {answers.get('goal', '')}",
        f"Návštěvnost: {answers.get('traffic', '')}",
        f"Historie webu: {answers.get('history', '')}",
    ]
    return "\n".join(lines)


def generate_local_preview() -> str:
    data = st.session_state.site_data or {}
    score_data = st.session_state.site_score or {}
    score = score_data.get("score", 0)
    issues = score_data.get("issues", [])
    critical = [i for i in issues if i["sev"] == "❌"]
    url = data.get("url", st.session_state.input_url)

    preview = f"""**Rychlý předverdikt pro: {url}**

SEO skóre: **{score}/100 – {score_label(score)}**

"""
    if critical:
        preview += f"Nejzávažnější problém: **{critical[0]['text']}**\n\n"
    elif issues:
        preview += f"Hlavní problém: **{issues[0]['text']}**\n\n"
    else:
        preview += "Web nemá zjevné kritické chyby v základní SEO analýze.\n\n"

    preview += (
        "Plná zpráva ukáže konkrétní 7denní akční plán, doporučené úpravy textů, "
        "technické chyby a doporučení pro místní vyhledávání."
    )
    return preview


def generate_local_report() -> str:
    data = st.session_state.site_data or {}
    score_data = st.session_state.site_score or {}
    answers = st.session_state.answers
    issues = score_data.get("issues", [])
    score = score_data.get("score", 0)

    issues_md = "\n".join(f"- {i['sev']} {i['text']}" for i in issues) or "- Žádné kritické problémy nenalezeny."

    return f"""**Web:** {data.get('url', '')}
**SEO skóre:** {score}/100 – {score_label(score)}

**Nalezené technické problémy:**
{issues_md}

**Co to znamená pro vaše zákazníky:** Google pravděpodobně váš web neindexuje optimálně \
nebo ho zobrazuje níže, než by mohl. Každý neopravený problém znamená zákazníky, \
kteří vás nenajdou.

**Akční plán na 7 dní:**
1. Opravte kritické technické chyby (HTTPS, title, H1, meta description)
2. Doplňte nebo přepište texty klíčových stránek – minimálně 300 slov na stránku
3. Doplňte alt texty ke všem obrázkům
4. Zkontrolujte, zda Google web vidí: přejděte na search.google.com/search-console

**Co říkáte o svém webu:** Cíl: {answers.get('goal', 'nezadáno')} | Návštěvnost: {answers.get('traffic', 'nezadáno')}

**Nabídka pomoci:**
- Technická oprava kritických chyb + nový title a description: **990 Kč včetně DPH**
- Kompletní SEO audit s akčním plánem a přepisem textů: **2 490 Kč včetně DPH**
"""


def generate_preview() -> str:
    return generate_local_preview()


def generate_final_report() -> str:
    client = get_openai_client()
    if client is None:
        if get_bool_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK):
            return generate_local_report()
        raise RuntimeError("Chybí OPENAI_API_KEY.")

    system_prompt = """
You are a Czech SEO specialist and digital marketing consultant.
You analyze websites for small local businesses in Czech Republic and Slovakia.

Goal:
- diagnose why this specific website is not getting traffic from Google,
- give concrete next actions,
- naturally offer paid help.

Rules:
- Write in Czech with Czech diacritics.
- Do not invent metrics you don't have.
- Use the provided technical data as facts.
- Be direct and commercially useful.
- Focus on actionable steps, not theory.
- Mention prices as Kč včetně DPH.

Output structure:
**Web a situace:** One concise paragraph with the URL and key context.

**Hlavní brzda viditelnosti:** The most likely reason why Google isn't showing the site.

**Co vidí Google:** 4-6 bullets of the technical findings interpreted for a non-technical owner.

**Akční plán na 7 dní:** Day-by-day or priority-ordered concrete steps.

**Co se stane, když to neopravíte:** Brief consequence section – not fearmongering, just honest.

**Doporučený další krok:** Naturally offer:
- Technická oprava kritických chyb za 990 Kč včetně DPH,
- Kompletní SEO audit s přepisem textů za 2 490 Kč včetně DPH,
- Měsíční SEO péče za 1 990 Kč/měsíc včetně DPH.
"""

    user_prompt = f"Analyze this website audit:\n\n{build_audit_summary()}"

    try:
        response = client.chat.completions.create(
            model=get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            temperature=0.25,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
    except Exception:
        if get_bool_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK):
            return generate_local_report()
        raise


# ── renderování ───────────────────────────────────────────────────────────────

def render_url_input() -> None:
    st.markdown("**Adresa webu ke kontrole**")
    with st.form("url_form"):
        url = st.text_input(
            "URL webu",
            placeholder="https://www.vas-web.cz",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Analyzovat web", type="primary")

    if not submitted:
        return

    url = url.strip()
    if not url:
        st.warning("Zadejte prosím adresu webu.")
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    with st.spinner("Načítám web a kontroluji základní SEO..."):
        data = fetch_and_parse(url)

    if data.get("error"):
        st.error(
            f"Web nelze načíst: {data['error']}\n\n"
            "Zkontrolujte, zda je adresa správná a web funguje."
        )
        return

    score_data = compute_score(data)
    st.session_state.input_url = url
    st.session_state.site_data = data
    st.session_state.site_score = score_data
    st.session_state.lead_id = make_lead_id(url)
    st.session_state.url_submitted = True
    st.rerun()


def render_demo_cta() -> None:
    """Tlačítko pro spuštění demo ukázky pod vstupním formulářem."""
    st.markdown("---")
    st.markdown("**Nevíte, co od analýzy čekat?**")
    st.caption("Prohlédněte si ukázku výsledků na fiktivním webu – žádná registrace není potřeba.")
    if st.button("Zobrazit ukázkový výsledek", use_container_width=True):
        activate_demo()


def render_demo_banner() -> None:
    """Banner zobrazený v demo režimu."""
    st.info(
        "**Ukázka výsledků** – takhle vypadá kompletní analýza pro reálný web. "
        "Pro audit vašeho webu klikněte na „Začít znovu" a zadejte svou adresu."
    )


def render_site_overview() -> None:
    data = st.session_state.site_data or {}
    score_data = st.session_state.site_score or {}
    score = score_data.get("score", 0)
    color = score_color(score)
    label = score_label(score)
    url = data.get("url", st.session_state.input_url)

    st.markdown("**Analyzovaný web**")
    st.markdown(
        f"""
        <div style="padding:16px 18px;border:1px solid #e6e8ee;border-radius:10px;background:#fff;margin:8px 0 14px;">
          <div style="font-size:.88rem;color:#6b7280;margin-bottom:4px;">URL</div>
          <div style="font-size:1rem;font-weight:600;color:#2f2f3d;margin-bottom:14px;overflow-wrap:anywhere;">{url}</div>
          <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;">
            <div>
              <div style="font-size:.88rem;color:#6b7280;">SEO skóre</div>
              <div style="font-size:1.55rem;font-weight:750;color:{color};">{score}/100</div>
              <div style="font-size:.85rem;color:{color};font-weight:600;">{label}</div>
            </div>
            <div>
              <div style="font-size:.88rem;color:#6b7280;">Počet chyb</div>
              <div style="font-size:1.55rem;font-weight:750;color:#2f2f3d;">{len(score_data.get('issues', []))}</div>
            </div>
            <div>
              <div style="font-size:.88rem;color:#6b7280;">HTTPS</div>
              <div style="font-size:1.55rem;font-weight:750;color:{'#16a34a' if data.get('https') else '#dc2626'};">{'✓' if data.get('https') else '✗'}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if score < 50:
        st.warning(
            "Web má závažné SEO problémy, které pravděpodobně brání jeho zobrazení ve výsledcích Googlu."
        )


def render_history_answers() -> None:
    answers = st.session_state.answers
    if not answers:
        return
    with st.expander("Vaše odpovědi", expanded=False):
        for step in STEPS:
            answer = answers.get(step["key"])
            if answer:
                st.markdown(f"**{step['label']}**")
                st.write(answer)


def save_answer(step_key: str, answer: str) -> None:
    st.session_state.answers[step_key] = answer.strip()
    st.session_state.step_index += 1
    st.rerun()


def render_text_step(step: Dict[str, str]) -> None:
    idx = st.session_state.step_index
    total = len(STEPS)
    st.markdown(f"**Otázka {idx + 1} z {total}: {step['label']}**")
    st.write(step["prompt"])
    with st.form(f"form_{step['key']}", clear_on_submit=True):
        answer = st.text_area(
            "Vaše odpověď",
            placeholder=step["placeholder"],
            height=120,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Pokračovat", type="primary")
    if submitted:
        if not answer.strip():
            st.warning("Napište prosím alespoň krátkou odpověď.")
            return
        save_answer(step["key"], answer)


def valid_contact(name: str, email: str, phone: str, consent: bool) -> Optional[str]:
    if len(name.strip()) < 2:
        return "Doplňte prosím jméno a příjmení."
    if "@" not in email or "." not in email.split("@")[-1]:
        return "Doplňte prosím platný e-mail."
    phone_digits = "".join(ch for ch in phone if ch.isdigit())
    if len(phone_digits) < 9:
        return "Doplňte prosím telefonní číslo (alespoň 9 číslic)."
    if not consent:
        return "Bez souhlasu se zpracováním kontaktu nelze bezplatný přehled zobrazit."
    return None


def render_contact_gate() -> None:
    st.markdown("**Kam poslat bezplatný přehled chyb**")
    st.write(
        "Web jsme prověřili. Abychom mohli výsledek přiřadit k vašemu auditu "
        "a navázat na něj, zadejte prosím kontaktní údaje."
    )
    with st.form("contact_gate"):
        name = st.text_input("Jméno a příjmení", value=st.session_state.contact.get("name", ""))
        email = st.text_input("E-mail", value=st.session_state.contact.get("email", ""))
        phone = st.text_input("Telefon", value=st.session_state.contact.get("phone", ""))
        consent = st.checkbox(
            "Souhlasím se zpracováním kontaktních údajů za účelem zaslání výsledku auditu.",
            value=bool(st.session_state.contact.get("consent", False)),
        )
        submitted = st.form_submit_button("Zobrazit bezplatný přehled chyb", type="primary")
    if not submitted:
        return
    error = valid_contact(name, email, phone, consent)
    if error:
        st.warning(error)
        return
    st.session_state.contact = {
        "name": name.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
        "consent": True,
    }
    try:
        post_lead_payload(build_lead_payload())
    except RuntimeError as exc:
        st.error(str(exc))
        return
    st.session_state.contact_submitted = True
    st.session_state.lead_saved = True
    st.success("Kontakt byl uložen. Připravuji přehled...")
    st.rerun()


def render_preview_and_paywall() -> None:
    if st.session_state.free_preview is None:
        st.session_state.free_preview = generate_preview()
    st.markdown(st.session_state.free_preview)
    render_paywall()


def render_paywall() -> None:
    payment_link = get_config("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    access_code = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)
    unlock_verify_url = get_config("UNLOCK_VERIFY_URL", "")
    price_text = get_config("PRICE_TEXT", DEFAULT_PRICE_TEXT)
    contact = st.session_state.contact
    payment_url = append_url_params(
        payment_link,
        {
            "client_reference_id": st.session_state.lead_id,
            "prefilled_email": contact.get("email", ""),
            "utm_source": "streamlit_web_audit",
            "utm_content": st.session_state.lead_id,
        },
    )
    st.markdown("**Plná analýza s akčním plánem**")
    if payment_link == DEFAULT_PAYMENT_LINK:
        st.error("Platební odkaz není nastaven. Přidejte PAYMENT_LINK do Streamlit Secrets.")
        return
    st.write(
        "Rychlý předverdikt je připraven. Plná zpráva doplní konkrétní 7denní akční plán, "
        "doporučené úpravy textů, doporučení pro místní SEO a srovnání s konkurencí."
    )
    st.info(
        "Po zaplacení vám plnou zprávu pošleme na e-mail z objednávky. "
        "Odemykací kód slouží k okamžitému zobrazení v aplikaci."
    )
    st.markdown(f"[Objednat plnou analýzu za {price_text}]({payment_url})")
    if access_code or unlock_verify_url:
        with st.expander("Už máte odemykací kód?"):
            code = st.text_input("Odemykací kód z potvrzení platby", type="password")
            if st.button("Odemknout plnou analýzu", type="primary"):
                if not verify_unlock_token(code):
                    st.error("Odemykací kód nesouhlasí nebo vypršela jeho platnost.")
                    return
                st.session_state.unlocked = True
                st.rerun()


def render_final_report() -> None:
    if st.session_state.final_report is None:
        with st.spinner("Připravuji plnou analýzu..."):
            try:
                st.session_state.final_report = generate_final_report()
                st.session_state.last_error = None
            except Exception as exc:
                st.session_state.last_error = str(exc)
    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        return
    st.markdown(st.session_state.final_report)
    if not st.session_state.get("demo_mode"):
        st.download_button(
            "Stáhnout analýzu (Markdown)",
            data=st.session_state.final_report,
            file_name="seo_audit_webu.md",
            mime="text/markdown",
        )


def render_current_step() -> None:
    idx = st.session_state.step_index
    if idx < len(STEPS):
        render_text_step(STEPS[idx])
        return
    if not st.session_state.contact_submitted:
        render_contact_gate()
        return
    render_preview_and_paywall()


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    init_state()

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    # Demo banner
    if st.session_state.get("demo_mode"):
        render_demo_banner()

    if st.button("Začít znovu", use_container_width=True):
        reset_app()

    if not st.session_state.url_submitted:
        render_url_input()
        render_demo_cta()
        return

    render_site_overview()
    render_history_answers()

    if st.session_state.unlocked:
        render_final_report()
    else:
        render_current_step()


if __name__ == "__main__":
    main()
