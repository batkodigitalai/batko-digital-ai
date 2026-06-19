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
    PRICE_TEXT     = "299 Kč včetně DPH"
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
APP_SUBTITLE = "Zjistěte za 2 minuty, proč váš web nenachází zákazníci na Googlu."

DEFAULT_PAYMENT_LINK          = "https://buy.stripe.com/your-payment-link"
DEFAULT_PRICE_TEXT            = "299 Kč včetně DPH"
DEFAULT_ACCESS_CODE           = ""
DEFAULT_OPENAI_MODEL          = "gpt-4.1-mini"
DEFAULT_ALLOW_LOCAL_FALLBACK  = "true"
DEFAULT_REQUIRE_LEAD_WEBHOOK  = "false"


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
            content_type = resp.headers.get("Content-Type", "")
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
        issues.append({"sev": "❌", "text": "Chybí <title> tag – Google neví, jak stránku pojmenovat ve výsledcích."})
        score -= 20
    elif title_len < 30:
        issues.append({"sev": "⚠️", "text": f"Title je příliš krátký ({title_len} znaků). Doporučeno 50–60 znaků."})
        score -= 10
    elif title_len > 65:
        issues.append({"sev": "⚠️", "text": f"Title je příliš dlouhý ({title_len} znaků) – Google ho ořízne. Max 60 znaků."})
        score -= 5

    # Meta description
    desc_len = data.get("desc_len", 0)
    if desc_len == 0:
        issues.append({"sev": "❌", "text": "Chybí meta description – Google si vybere libovolný text ze stránky, obvykle nevhodný."})
        score -= 15
    elif desc_len < 70:
        issues.append({"sev": "⚠️", "text": f"Meta description je příliš krátký ({desc_len} znaků). Ideál 140–160 znaků."})
        score -= 7
    elif desc_len > 165:
        issues.append({"sev": "⚠️", "text": f"Meta description je příliš dlouhý ({desc_len} znaků) – Google ho ořízne."})
        score -= 3

    # H1
    h1s = data.get("h1s", [])
    if len(h1s) == 0:
        issues.append({"sev": "❌", "text": "Chybí nadpis H1 – hlavní signal pro Google, o čem stráka je."})
        score -= 15
    elif len(h1s) > 1:
        issues.append({"sev": "⚠️", "text": f"Stráka má {len(h1s)} nadpisů H1 – správně má být jen jeden."})
        score -= 8

    # Viewport
    if not data.get("viewport"):
        issues.append({"sev": "❌", "text": "Chybí viewport meta tag – web pravděpodobnę není mobilní. Google upřednostňuje mobilní weby."})
        score -= 15

    # Obsah
    word_count = data.get("word_count", 0)
    if word_count < 200:
        issues.append({"sev": "⚠️", "text": f"Málo textu na stránce ({word_count} slov). Google preferuje stránky s obsahem 300+ slov."})
        score -= 10
    elif word_count > 3000:
        issues.append({"sev": "ℹ️", "text": f"Hodnę textu ({word_count} slov). Ujistěte se, že je strukturovaný a čitelný."})

    # Obrázky bez alt textu
    img_no_alt = data.get("img_without_alt", 0)
    total_imgs = data.get("total_imgs", 0)
    if img_no_alt > 0:
        issues.append({"sev": "⚠️", "text": f"{img_no_alt} z {total_imgs} obrázků nemá alt text – Google je nemůže indexovat."})
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


# ── kroky (otázl�) ───────────────────────────────────────────────────────────

STEPS: List[Dict[str, str]] = [
    {
        "key": "goal",
        "label": "Doplnění 1",
        "prompt": "Co je hlavní cíl vašeho webu? (získat zákazníky, prodat produkt, prezentovat služby, jiné)",
        "placeholder": "Např.: chceme získávat poptávky od místních zákazníků na rekonstrukce koupelen...",
    },
    {
        "key": "traffic",
        "label": "Doplnění 2",
        "prompt": "Jak jste spokojeni s návštěvností z Googlu? Kolik lidí web navštíví měsíčně (odhadem)?",
        "placeholder": "Např.: z Googlu chodí skoro nikdo, Google Analytics ukazuje 50 lidí za měsíc...",
    },
    {
        "key": "history",
        "label": "Doplnění 3",
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
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_app() -> None:
    keys = [
           "input_url", "url_submitted", "site_data", "site_score",
        "lead_id", "contact", "contact_submitted", "lead_saved",
        "step_index", "answers", "unlocked", "final_report",
        "free_preview", "last_error",
    ]
    for k in keys:
        st.session_state.pop(k, None)
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
        raise RuntimeError("Zápis leadu se nepodařil.") from exc


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
        f"Obrázky bez alt: {data.get('img_without_alt', 0)} z {data.get('total_imgs', 0)}",
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
        "Plná zpráva ukáže konkrétní 7denní akční plán, úpravy textů, "
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

**Co to znamená pro vaše zákazníky:** Google pravděpodobně váš web neindexuje optimálně nebo ho zobrazuje níže, než by mohl. Kaſdý nenalezený problém znamená zákazníky, kteří tás nenajdou.

**Akční plán na 7 dní:**
1. Opravte kritické technické chyby (HTTPS, title, H1, meta description)
2. Doplňte nebo přepište texty klíčových stránek – minimálně 300 slov na stránku
3. Doplňte alt texty ke všem obrázkům
4. Zkontrolujte, zda Google web vidí: přejděte na search.google.com/search-console

**Co Říkáte o svém webu:** Cíl: {answers.get('goal', 'nezadáno')} | Návštěvnost: {answers.get('traffic', 'nezadáno')}

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
        st.error(f"Web nelze načíst: {data['error']}\n\nZkontrolujte, zda je adresa správná a web funguje.")
        return

    score_data = compute_score(data)
    st.session_state.input_url = url
    st.session_state.site_data = data
    st.session_state.site_score = score_data
    st.session_state.lead_id = make_lead_id(url)
    st.session_state.url_submitted = True
    st.rerun()


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
            "Web má závažné SEO problémy, které pravděpodobně brání zobrazení ve výsledcích Googlu."
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
    st.markdown(f"**{step['label']}**")
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
            st.warning("Napište prosím aspoň krátkou odpověď.")
            return
        save_answer(step["key"], answer)


def valid_contact(name: str, email: str, phone: str, consent: bool) -> Optional[str]:
    if len(name.strip()) < 2:
        return "Doplňte prosím jméno."
    if "@" not in email or "." not in email.split("@")[-1]:
        return "Doplňte prosím platný e-mail."
    phone_digits = "".join(ch for ch in phone if ch.isdigit())
    if len(phone_digits) < 9:
        return "Doplňte prosím telefonní číslo."
    if not consent:
        return "Bez souhlasu nemůžeme bezplatný předverdikt zobrazit."
    return None


def render_contact_gate() -> None:
    st.markdown("**Kam poslat bezplatný přehled chyb**")
    st.write(
        "Web jsme prověřili. Abychom mohli výsledek přiřadit k vašemu auditu "
        "a navázat na něj, zadejte prosím kontakt."
    )
    with st.form("contact_gate"):
        name = st.text_input("Jméno a příjmení", value=st.session_state.contact.get("name", ""))
        email = st.text_input("E-mail", value=st.session_state.contact.get("email", ""))
        phone = st.text_input("Telefon", value=st.session_state.contact.get("phone", ""))
        consent = st.checkbox(
            "Souhlasím se zpracováním kontaktu pro zaslání výsledku.",
            value=bool(st.session_state.contact.get("consent", False)),
        )
        submitted = st.form_submit_button("Zobrazit bezplatný předverdikt", type="primary")
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
    st.success("Kontakt je uložený. Připravuji předverdikt.")
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
        st.error("Platební odkaz není nastavený. Přidejte PAYMENT_LINK do Streamlit Secrets.")
        return
    st.write(
        "Rychlý předverdikt je připravený. Plná zpráva doplní konkrétní 7denní akční plán, "
        "úpravy textů, doporučení pro místní SEO a srovnání s konkurencí."
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
                    st.error("Odemykací kód nesouhlasí nebo už vypršel.")
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
    st.download_button(
        "Stáhnout analýzu jako Markdown",
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

    if st.button("Začít znovu", use_container_width=True):
        reset_app()

    if not st.session_state.url_submitted:
        render_url_input()
        return

    render_site_overview()
    render_history_answers()

    if st.session_state.unlocked:
        render_final_report()
    else:
        render_current_step()


if __name__ == "__main__":
    main()
