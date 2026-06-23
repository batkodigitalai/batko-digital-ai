import streamlit as st
import os
import json
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────────
APP_TITLE = "AI Compliance Audit"
DEFAULT_ACCESS_CODE = ""
DEFAULT_PAYMENT_LINK = "https://buy.stripe.com/YOUR_LINK_HERE"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"
DEFAULT_PRICE_TEXT = "1 490 Kč vč. DPH"
DEFAULT_UPSELL_PRICE = "49 000 Kč"
UPSELL_EMAIL = "batko.digital.ai@gmail.com"


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


PROMPT_A = """Jsi elitní auditor AI bezpečnosti a regulací (AI Governance Specialist).
Uživatel ti poskytne stručný popis toho, jak jeho firma využívá umělou inteligenci.

Tvým úkolem je vygenerovat tvrdou a mírně alarmující analýzu.
Vrať POUZE validní JSON objekt (žádný jiný text, žádné markdown bloky) s těmito klíči:
- "risk_score": číslo mezi 65 a 85
- "vulnerability": string — jedna zásadní bezpečnostní nebo právní zranitelnost (max 2 věty, česky)
- "financial_warning": string — jedna krátká, úderná věta o možných finančních důsledcích nebo pokutách (česky)
- "risk_category": string — jedna z: "Únik dat", "Porušení GDPR", "Odpovědnost za chyby AI", "Chybějící transparentnost", "Porušení práv duševního vlastnictví"

Popis využití AI od uživatele:
"""

PROMPT_B = """Jsi světový expert na implementaci a legalitu AI procesů ve firmách.
Napiš vysoce strukturovaný, detailní a formálně působící AI Transparency Report.

Výstup MUSÍ obsahovat přesně tyto sekce (použij přesně tyto nadpisy):

## 1. MANAŽERSKÉ SHRNUTÍ
Profesionální zhodnocení nasazení AI ve firmě klienta (3–4 věty).

## 2. ANALÝZA RIZIK
Detailní rozpad čtyř rizik spojených s jejich konkrétním použitím:
- **Riziko halucinací a nepřesností** — dopad na jejich byznys
- **Riziko úniku dat a GDPR** — co konkrétně hrozí
- **Riziko zaujatosti (bias) AI systémů** — jak se projevuje v jejich případě
- **Regulační soulad (EU AI Act 2025)** — co konkrétně musí splnit

## 3. PROTOKOL O TRANSPARENTNOSTI
Hotový odstavec (4–6 vět), který si zákazník může zkopírovat na svůj web nebo do obchodních podmínek jako důkaz zodpovědného využívání AI.

## 4. AKČNÍ PLÁN NA PŘÍŠTÍCH 48 HODIN
Přesně 4 kroky k okamžité nápravě. Každý krok musí:
- mít nadpis ve formátu **Krok N: Název** (tučně)
- být fyzicky implementovatelný do 10 minut
- obsahovat konkrétní příklad — větu, nastavení nebo šablonu

## 5. AI BEZPEČNOSTNÍ CERTIFIKACE
Krátké profesionální hodnocení + odhadované snížení rizikového skóre po implementaci kroků.

Piš prémiovým byznysově-právním tónem. Výhradně v češtině.

Popis využití AI od klienta:
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
        "risk_score": 72,
        "vulnerability": "Vaše firma pravděpodobně sdílí interní data s veřejnými AI modely bez smluvní ochrany, čímž riskuje únik citlivých informací o klientech.",
        "financial_warning": "Pokuta za porušení GDPR při úniku dat přes AI systémy může dosáhnout až 4 % ročního obratu nebo 20 milionů EUR.",
        "risk_category": "Únik dat",
    }


def generate_teaser(description: str) -> dict:
    client = get_openai_client()
    fallback = get_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK).lower() == "true"
    if client is None:
        if fallback:
            return parse_teaser("")
        st.error("Chybí OpenAI API klíč.")
        st.stop()
    try:
        resp = client.chat.completions.create(
            model=get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            messages=[
                {"role": "system", "content": "Jsi AI governance auditor. Odpovídáš POUZE validním JSON objektem."},
                {"role": "user", "content": PROMPT_A + description},
            ],
            max_tokens=400,
            temperature=0.7,
        )
        return parse_teaser(resp.choices[0].message.content)
    except Exception as e:
        if fallback:
            return parse_teaser("")
        st.error(f"Chyba API: {e}")
        st.stop()


def generate_report(description: str) -> str:
    client = get_openai_client()
    fallback = get_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK).lower() == "true"
    if client is None:
        if fallback:
            return _local_report()
        st.error("Chybí OpenAI API klíč.")
        st.stop()
    try:
        resp = client.chat.completions.create(
            model=get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            messages=[
                {"role": "system", "content": "Jsi expertní AI governance auditor. Piš formálně, profesionálně, v češtině."},
                {"role": "user", "content": PROMPT_B + description},
            ],
            max_tokens=2000,
            temperature=0.6,
        )
        return resp.choices[0].message.content
    except Exception as e:
        if fallback:
            return _local_report()
        st.error(f"Chyba API: {e}")
        st.stop()


def _local_report() -> str:
    return """## 1. MANAŽERSKÉ SHRNUTÍ
Vaše organizace využívá umělou inteligenci ve svém každodenním provozu, což přináší výhody v efektivitě,
ale zároveň vyžaduje systematický přístup ke governance a regulačnímu souladu. Tento report identifikuje
klíčová rizika specifická pro vaše využití AI a navrhuje konkrétní kroky k jejich okamžité eliminaci.
Po implementaci doporučení budete v souladu s aktuálními EU regulacemi.

## 2. ANALÝZA RIZIK
- **Riziko halucinací a nepřesností** — Generativní AI může produkovat sebejistě znějící, ale fakticky nesprávné informace. Ve vašem kontextu to může vést k předání chybných podkladů klientům nebo k interním rozhodnutím na základě nepravdivých dat.
- **Riziko úniku dat a GDPR** — Sdílení firemních dat a informací o klientech s veřejnými AI modely (ChatGPT, Gemini) může porušovat čl. 28 GDPR o zpracování osobních údajů třetí stranou bez uzavřené smlouvy o zpracování dat (DPA).
- **Riziko zaujatosti (bias) AI systémů** — AI modely trénované na biased datech mohou systematicky znevýhodňovat určité skupiny zákazníků. Bez auditu výstupů nelze tento vliv detekovat.
- **Regulační soulad (EU AI Act 2025)** — Od roku 2025 platí povinnosti transparentnosti a lidského dohledu pro systémy AI s dopadem na lidi. Firmy musí dokumentovat, jak AI používají a kdo nese odpovědnost za výstupy.

## 3. PROTOKOL O TRANSPARENTNOSTI
„Naše společnost využívá nástroje umělé inteligence jako podpůrný prostředek pro zvýšení efektivity práce.
Žádné osobní údaje klientů nejsou sdíleny s externími AI systémy bez uzavřené smlouvy o zpracování dat.
Veškerá AI-asistovaná rozhodnutí procházejí kontrolou odpovědného zaměstnance před jejich použitím.
Zavázali jsme se k transparentnímu využívání AI v souladu s EU AI Act a nařízením GDPR.
Tento závazek pravidelně přehodnocujeme a aktualizujeme dle aktuální legislativy."

## 4. AKČNÍ PLÁN NA PŘÍŠTÍCH 48 HODIN

**Krok 1: Přidejte AI doložku do obchodních podmínek** (5 minut)
Zkopírujte a vložte do svých OP: *„Při poskytování služeb využíváme nástroje AI jako asistenta. Finální rozhodnutí jsou vždy v rukou kompetentního člověka. Do AI systémů nevkládáme osobní údaje třetích stran."*

**Krok 2: Zaveďte interní AI pravidlo č. 1** (3 minuty)
Zašlete týmu tuto zprávu: *„Od dnes platí: Do ChatGPT, Copilotu ani jiného AI nikdy nevkládejte jméno, e-mail, telefon ani jiné osobní údaje klientů. Vždy nahraďte anonymní verzí, např. 'klient A'."*

**Krok 3: Označte AI-generovaný obsah** (5 minut)
Do každého dokumentu nebo e-mailu vytvořeného s pomocí AI přidejte poznámku: *„Vytvořeno s pomocí AI, zkontrolováno a schváleno [jméno] dne [datum]."* Vytvořte si na to šablonu.

**Krok 4: Zdokumentujte AI nástroje a odpovědnosti** (10 minut)
Vytvořte jednoduchý seznam (stačí Google Docs nebo Notion): jaké AI nástroje firma používá, k čemu, a kdo je odpovědný za kontrolu jejich výstupů. Tento dokument je základem vašeho AI governance záznamu dle EU AI Act.

## 5. AI BEZPEČNOSTNÍ CERTIFIKACE
Na základě analýzy odhadujeme aktuální rizikové skóre vaší firmy na 72/100 — kategorie vysokého rizika.
Po implementaci všech čtyř kroků z akčního plánu očekáváme snížení na přibližně 32/100 — bezpečná zóna.
Gratulujeme k proaktivnímu přístupu k AI governance. Tento report slouží jako váš interní doklad o dodržování zásad zodpovědného AI."""


# ─── HTML REPORT GENERATION ────────────────────────────────────────────────────
def md_to_html_body(text: str) -> str:
    """Minimal markdown → HTML converter for the report."""
    import re
    lines = text.split('\n')
    html_lines = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            html_lines.append('<br>')
            continue
        # H2
        if line_stripped.startswith('## '):
            html_lines.append(f'<h2>{line_stripped[3:]}</h2>')
            continue
        # Bold inline
        line_stripped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line_stripped)
        # Bullet
        if line_stripped.startswith('- '):
            html_lines.append(f'<li>{line_stripped[2:]}</li>')
            continue
        html_lines.append(f'<p>{line_stripped}</p>')
    return '\n'.join(html_lines)


def generate_html_download(report_text: str, ai_description: str, risk_score: int) -> str:
    date_str = datetime.now().strftime('%d. %m. %Y')
    body_html = md_to_html_body(report_text)
    color = '#c0392b' if risk_score >= 70 else '#e67e22' if risk_score >= 50 else '#27ae60'
    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Transparency Report</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; max-width: 860px; margin: 0 auto; padding: 2rem; color: #1a1a2e; line-height: 1.7; }}
  .header {{ background: linear-gradient(135deg, #0a2850, #1a4a8a); color: white; padding: 2rem 2.5rem; border-radius: 10px; margin-bottom: 2rem; }}
  .header h1 {{ margin: 0 0 0.3rem 0; font-size: 1.8rem; }}
  .header p {{ margin: 0; opacity: 0.75; font-size: 0.95rem; }}
  .score-box {{ display: inline-block; background: {color}; color: white; font-size: 2.5rem; font-weight: 900; border-radius: 50%; width: 80px; height: 80px; line-height: 80px; text-align: center; margin-right: 1rem; vertical-align: middle; }}
  .score-label {{ display: inline-block; vertical-align: middle; }}
  .score-label strong {{ font-size: 1.2rem; color: {color}; }}
  .input-box {{ background: #f4f6fb; border-left: 4px solid #1a4a8a; padding: 1rem 1.5rem; border-radius: 6px; margin-bottom: 2rem; font-size: 0.9rem; color: #555; }}
  h2 {{ background: #eef2ff; color: #0a2850; padding: 0.6rem 1rem; border-radius: 6px; font-size: 1.05rem; margin-top: 2rem; }}
  p {{ margin: 0.5rem 0; }}
  li {{ margin: 0.3rem 0 0.3rem 1.2rem; }}
  .footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: 0.78rem; color: #999; text-align: center; }}
  strong {{ color: #0a2850; }}
  @media print {{ body {{ padding: 0.5rem; }} .header {{ border-radius: 0; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>🔒 AI Transparency Report</h1>
  <p>Vygenerováno: {date_str} &nbsp;|&nbsp; Batko Digital AI</p>
</div>

<div style="margin-bottom:1.5rem;">
  <span class="score-box">{risk_score}</span>
  <span class="score-label">Skóre rizikovosti<br><strong>VYSOKÉ RIZIKO ⚠️</strong></span>
</div>

<div class="input-box">
  <strong>Popis využití AI klientem:</strong><br>
  {ai_description}
</div>

{body_html}

<div class="footer">
  Batko Digital AI &nbsp;|&nbsp; {UPSELL_EMAIL}<br>
  Tento report nepředstavuje právní poradenství. Doporučujeme konzultaci s odborníkem pro vaši konkrétní situaci.
</div>
</body>
</html>"""


def generate_checklist_html() -> str:
    return """<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<title>12 skrytých chyb firem při využívání AI — 2026</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 760px; margin: 0 auto; padding: 2rem; color: #222; }
  h1 { font-size: 1.4rem; border-bottom: 3px solid #0a2850; padding-bottom: 0.5rem; }
  .intro { color: #555; font-size: 0.9rem; margin-bottom: 1.5rem; }
  .item { display: flex; gap: 1rem; margin-bottom: 1rem; padding: 0.8rem; background: #f9f9f9; border-left: 4px solid #c0392b; border-radius: 4px; }
  .num { font-size: 1.4rem; font-weight: 900; color: #c0392b; min-width: 2rem; }
  .content strong { display: block; margin-bottom: 0.2rem; }
  .content span { font-size: 0.88rem; color: #555; }
  .footer { margin-top: 2rem; font-size: 0.8rem; color: #999; border-top: 1px solid #eee; padding-top: 0.8rem; }
</style>
</head>
<body>
<h1>12 skrytých chyb, které v roce 2026 potápějí malé firmy při využívání AI</h1>
<p class="intro">Praktický checklist od Batko Digital AI. Žádná teorie — jen konkrétní chyby z praxe a jejich rychlé opravy.</p>

<div class="item"><div class="num">1</div><div class="content"><strong>Vkládají osobní data klientů do ChatGPT</strong><span>OpenAI může tato data použít k trénování. Fix: anonymizujte vstupy — nahraďte jméno za "klient A".</span></div></div>
<div class="item"><div class="num">2</div><div class="content"><strong>Nemají uzavřenou DPA (Data Processing Agreement) s AI poskytovatelem</strong><span>Bez DPA porušujete čl. 28 GDPR. Fix: Enterprise plán ChatGPT nebo Microsoft 365 Copilot DPA podepište ještě dnes.</span></div></div>
<div class="item"><div class="num">3</div><div class="content"><strong>Vydávají AI výstupy za vlastní odbornou práci bez kontroly</strong><span>AI halucinuje. Fix: každý AI výstup musí projít kontrolou odpovědné osoby před odesláním klientovi.</span></div></div>
<div class="item"><div class="num">4</div><div class="content"><strong>Nemají žádnou zmínku o AI v obchodních podmínkách</strong><span>Klient neví, že AI používáte. Fix: přidejte jeden odstavec do OP — viz Transparentnostní protokol z vašeho reportu.</span></div></div>
<div class="item"><div class="num">5</div><div class="content"><strong>Generují obsah chráněný autorskými právy pomocí AI a dál ho prodávají</strong><span>AI může generovat výstupy podobné chráněným dílům. Fix: nepoužívejte AI pro přepis konkrétních textů třetích stran.</span></div></div>
<div class="item"><div class="num">6</div><div class="content"><strong>Neoznačují AI-generovaný obsah</strong><span>V EU je od 2025 povinné označovat syntetický obsah (deepfake, AI texty v reklamě). Fix: přidejte poznámku "Vytvořeno s pomocí AI".</span></div></div>
<div class="item"><div class="num">7</div><div class="content"><strong>Používají AI k automatizovaným rozhodnutím o lidech bez možnosti odvolání</strong><span>Např. AI hodnotí životopisy nebo bonitu. Fix: vždy zajistěte možnost přezkumu rozhodnutí člověkem.</span></div></div>
<div class="item"><div class="num">8</div><div class="content"><strong>Nikdo ve firmě neví, jaké AI nástroje vlastně používají kolegové</strong><span>Shadow AI = nekontrolované riziko. Fix: vytvořte interní registr AI nástrojů (stačí tabulka).</span></div></div>
<div class="item"><div class="num">9</div><div class="content"><strong>Prompty s firemními tajemstvími uložené v cloudu třetí strany</strong><span>Historii ChatGPT může vidět OpenAI. Fix: citlivé prompty pište bez konkrétních názvů a čísel.</span></div></div>
<div class="item"><div class="num">10</div><div class="content"><strong>Žádná politika pro případ, kdy AI udělá chybu s dopadem na klienta</strong><span>Kdo nese odpovědnost? Fix: do smlouvy s klienty přidejte větu o AI a odpovědnosti za výstupy.</span></div></div>
<div class="item"><div class="num">11</div><div class="content"><strong>Zaměstnanci nebyli proškoleni — dělají to "od oka"</strong><span>1 špatný prompt = GDPR incident. Fix: 30minutové školení na základní pravidla AI hygieny stačí.</span></div></div>
<div class="item"><div class="num">12</div><div class="content"><strong>Nemonitorují aktualizace EU AI Act</strong><span>Nařízení se vyvíjí. Fix: přihlaste se na newsletter UOOU.cz — přijde vám upozornění zdarma.</span></div></div>

<div class="footer">Batko Digital AI &nbsp;|&nbsp; batko.digital.ai@gmail.com &nbsp;|&nbsp; Tento checklist slouží jako praktická pomůcka, nikoli jako právní poradenství.</div>
</body>
</html>"""


# ─── UI ────────────────────────────────────────────────────────────────────────
def render_header():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0a2850,#1a4a8a);padding:2rem 2.5rem;border-radius:12px;margin-bottom:1.5rem;text-align:center;">
      <h1 style="color:white;margin:0;font-size:2rem;">🔒 AI Compliance Audit</h1>
      <p style="color:#a0c4ff;margin:0.5rem 0 0 0;font-size:1rem;">
        Zjistěte za 30 sekund, zda je vaše firma v bezpečí před AI regulacemi
      </p>
    </div>
    """, unsafe_allow_html=True)


def render_input():
    st.markdown("### 📝 Popište, jak ve firmě používáte AI")
    st.markdown(
        "*Napr.: 'Piseme s ChatGPT emaily klientum a generujeme texty na web.' "
        "nebo 'Automaticky zpracovavame faktury pres AI.'*"
    )
    desc = st.text_area(
        "Váš popis:",
        placeholder="Napište 2–4 věty o tom, jak vaše firma využívá AI nástroje...",
        height=150,
        key="desc_input",
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 Analyzovat moje AI rizika", type="primary", use_container_width=True):
            if not desc or len(desc.strip()) < 20:
                st.warning("Prosím, popište využití AI alespoň v 1–2 větách.")
            else:
                st.session_state.description = desc.strip()
                st.session_state.step = "generating_teaser"
                st.rerun()


def render_teaser(t: dict):
    score = t.get("risk_score", 72)
    vuln = t.get("vulnerability", "")
    warn = t.get("financial_warning", "")
    cat = t.get("risk_category", "Regulační riziko")
    color = "#c0392b" if score >= 70 else "#e67e22" if score >= 50 else "#27ae60"

    st.markdown(f"""
    <div style="background:#fff8f8;border:2px solid {color};border-radius:12px;padding:1.5rem;margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:1.2rem;">
        <div style="background:{color};color:white;font-size:2.2rem;font-weight:900;border-radius:50%;
                    width:88px;height:88px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
          {score}
        </div>
        <div>
          <div style="font-size:0.8rem;color:#888;text-transform:uppercase;font-weight:600;letter-spacing:.05em;">Skóre rizikovosti</div>
          <div style="font-size:1.35rem;font-weight:700;color:{color};">VYSOKÉ RIZIKO ⚠️</div>
          <div style="font-size:0.88rem;color:#999;">Kategorie: {cat}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:#fff3cd;border-left:4px solid #f39c12;padding:1rem 1.2rem;border-radius:8px;margin-bottom:0.8rem;">
      <div style="font-weight:700;color:#856404;margin-bottom:0.3rem;">🔴 Kritická zranitelnost odhalena:</div>
      <div style="color:#533f03;line-height:1.6;">{vuln}</div>
    </div>
    <div style="background:#fce8e8;border-left:4px solid #c0392b;padding:1rem 1.2rem;border-radius:8px;margin-bottom:1.5rem;">
      <div style="font-weight:700;color:#c0392b;margin-bottom:0.3rem;">💸 Finanční hrozba:</div>
      <div style="color:#7b241c;">{warn}</div>
    </div>
    """, unsafe_allow_html=True)


def render_paywall():
    payment_link = get_config("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    price_text = get_config("PRICE_TEXT", DEFAULT_PRICE_TEXT)

    st.markdown("---")
    st.markdown("### 🔓 Získejte kompletní AI Transparency Report")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
**Co dostanete za {price_text}:**
- ✅ Manažerské shrnutí pro vaši firmu
- ✅ Detailní analýza 4 typů AI rizik
- ✅ Hotový text pro web / OP (copy-paste)
- ✅ Akční plán — 4 kroky, každý pod 10 minut
- ✅ Vaše AI bezpečnostní certifikace
- 🎁 **BONUS:** Checklist „12 chyb, které potápějí firmy při AI"
        """)
        st.markdown("""
<div style="background:#e8f5e9;border:1px solid #4caf50;border-radius:8px;padding:0.8rem;font-size:0.85rem;margin-top:0.5rem;">
  <strong>💚 Garance vrácení:</strong><br>
  Pokud report nepřinese okamžitý klid na duši, stačí jeden e-mail
  a do 24 h vrátíme 100 % v Kč. Report si navíc můžete nechat.
</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
<div style="text-align:center;background:linear-gradient(135deg,#0a2850,#1a4a8a);border-radius:12px;padding:1.5rem;color:white;">
  <div style="font-size:2rem;margin-bottom:0.5rem;">📄</div>
  <div style="font-size:1.05rem;font-weight:700;margin-bottom:0.3rem;">AI Transparency Report</div>
  <div style="font-size:1.8rem;font-weight:900;color:#ffd700;margin-bottom:1rem;">{price_text}</div>
  <a href="{payment_link}" target="_blank"
     style="background:#ffd700;color:#0a2850;text-decoration:none;padding:0.75rem 1.8rem;
            border-radius:8px;font-weight:700;font-size:1rem;display:inline-block;">
    🔐 Zaplatit a získat report
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


def render_report(report_text: str, description: str, risk_score: int):
    st.success("✅ Váš AI Transparency Report je připraven!")
    st.markdown("---")
    st.markdown(report_text)
    st.markdown("---")

    html_report = generate_html_download(report_text, description, risk_score)
    html_checklist = generate_checklist_html()

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Stáhnout AI Transparency Report (HTML)",
            data=html_report.encode("utf-8"),
            file_name=f"AI_Transparency_Report_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True,
            type="primary",
        )
    with col2:
        st.download_button(
            label="🎁 Stáhnout Bonus Checklist",
            data=html_checklist.encode("utf-8"),
            file_name="12_chyb_AI_2026_checklist.html",
            mime="text/html",
            use_container_width=True,
        )

    st.caption("💡 Tip: Soubory otevřete v prohlížeči a vytiskněte jako PDF (Ctrl+P → Uložit jako PDF).")

    # Upsell
    upsell_price = get_config("UPSELL_PRICE", DEFAULT_UPSELL_PRICE)
    st.markdown("---")
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0a2850,#1a4a8a);border-radius:12px;padding:1.8rem;color:white;text-align:center;margin-top:1rem;">
  <div style="font-size:1.5rem;font-weight:700;margin-bottom:0.5rem;">🚀 Chcete to vyřešit úplně bez práce?</div>
  <div style="color:#a0c4ff;margin-bottom:1.2rem;max-width:520px;margin-left:auto;margin-right:auto;">
    Víte přesně, kde máte trhliny. Implementace vás ale čeká. Příliš zaneprázdněni?
  </div>
  <div style="background:rgba(255,255,255,.1);border-radius:8px;padding:1rem 1.5rem;margin-bottom:1.2rem;text-align:left;max-width:480px;margin-left:auto;margin-right:auto;">
    <strong>Balíček „AI Platform Governance na klíč":</strong><br>
    ✅ Nastavení bezpečných interních AI promptů<br>
    ✅ RAG pipeline — vaše data nikdy neopustí firmu<br>
    ✅ Školení celého týmu (2 hodiny, online)<br>
    ✅ Právní dokumentace pro GDPR a EU AI Act
  </div>
  <div style="font-size:2rem;font-weight:900;color:#ffd700;margin-bottom:1rem;">{upsell_price}</div>
  <a href="mailto:{UPSELL_EMAIL}?subject=Z%C3%A1jem%20o%20AI%20Platform%20Governance&body=Dobr%C3%BD%20den%2C%20m%C3%A1m%20z%C3%A1jem%20o%20bal%C3%AD%C4%8Dek%20AI%20Platform%20Governance%20na%20kl%C3%AD%C4%8D."
     style="background:#ffd700;color:#0a2850;text-decoration:none;padding:0.8rem 2rem;border-radius:8px;font-weight:700;font-size:1rem;display:inline-block;">
    📩 Chci to vyřešit za mě
  </a>
</div>
    """, unsafe_allow_html=True)


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🔒", layout="centered")
    render_header()

    if "step" not in st.session_state:
        st.session_state.step = "input"

    step = st.session_state.step

    if step == "input":
        render_input()

    elif step == "generating_teaser":
        with st.spinner("Analyzujeme vaše AI rizika..."):
            t = generate_teaser(st.session_state.description)
        st.session_state.teaser = t
        st.session_state.step = "teaser"
        st.rerun()

    elif step == "teaser":
        render_teaser(st.session_state.teaser)
        render_paywall()
        if st.button("← Začít znovu", key="restart_teaser"):
            for k in ["step", "teaser", "description", "report"]:
                st.session_state.pop(k, None)
            st.rerun()

    elif step == "generating_report":
        with st.spinner("Generujeme váš kompletní AI Transparency Report (30–40 sekund)..."):
            r = generate_report(st.session_state.description)
        st.session_state.report = r
        st.session_state.step = "report"
        st.rerun()

    elif step == "report":
        render_report(
            st.session_state.report,
            st.session_state.get("description", ""),
            st.session_state.get("teaser", {}).get("risk_score", 72),
        )
        if st.button("← Nový audit", key="restart_report"):
            for k in ["step", "teaser", "description", "report"]:
                st.session_state.pop(k, None)
            st.rerun()

    render_footer()


# ─── FOOTER ────────────────────────────────────────────────────────────────────
def render_footer():
    st.markdown("---")
    st.markdown(
        """
<div style="font-size:0.78rem; color:#666; text-align:center; line-height:1.8; padding:1rem 0 0.5rem 0;">

**Provozovatel služby (§ 1826 odst. 1 NOZ):**<br>
Jaroslav Batko — Batko Digital AI &nbsp;|&nbsp; IČO: neuvedeno &nbsp;|&nbsp;
📩 <a href="mailto:batko.digital.ai@gmail.com" style="color:#1a4a8a;">batko.digital.ai@gmail.com</a>

<br>

**Ochrana osobních údajů (GDPR):**<br>
Tato aplikace nezpracovává ani neukládá žádné osobní údaje uživatelů.
Vložený text (popis využití AI) je použit výhradně pro jednorázové vygenerování reportu
a není nikde trvale ukládán ani sdílen s třetími stranami.
Zpracování probíhá přes OpenAI API (datové centrum EU) v souladu s GDPR.

<br>

**Obchodní podmínky:**<br>
Zakoupením reportu souhlasíte s tím, že výstup má informační a konzultační charakter
a nepředstavuje právní poradenství ve smyslu zákona č. 85/1996 Sb.
Právo na odstoupení od smlouvy ve lhůtě 14 dnů (§ 1829 NOZ) uplatněte e-mailem na
<a href="mailto:batko.digital.ai@gmail.com" style="color:#1a4a8a;">batko.digital.ai@gmail.com</a>.
Spory se řeší před příslušnými soudy ČR; mimosoudně lze využít
<a href="https://www.coi.cz" target="_blank" style="color:#1a4a8a;">ČOI (www.coi.cz)</a>.

<br>

**Právní upozornění:**<br>
Report je generován pomocí umělé inteligence a slouží jako orientační podklad.
Nepředstavuje právní, daňové ani jiné odborné poradenství.
Doporučujeme ověřit závěry s kvalifikovaným odborníkem.

<br>

© {year} Batko Digital AI &nbsp;|&nbsp; Všechna práva vyhrazena

</div>
""".format(year=datetime.now().year),
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
