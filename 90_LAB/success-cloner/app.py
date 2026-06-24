import streamlit as st
import os

# ── APP KONSTANTY ──────────────────────────────────────────
APP_TITLE    = "Replikátor Úspěchu"
APP_LABEL    = "BEZPLATNÝ AI NÁSTROJ PRO FREELANCERY"
APP_SUBTITLE = "Forenzní analýza vašeho úspěchu — SOP pro zopakování"

COMPANY_NAME    = "BATKO.DIGITAL.AI"
COMPANY_PERSON  = "Ing. Jaroslav Batko"
COMPANY_ICO     = "14600153"
COMPANY_DIC     = "CZ5912280418"
COMPANY_ADDRESS = "Lískovec 170, 273 51 Velké Přîtočno"
COMPANY_PHONE   = "+420 725 360 151"
COMPANY_EMAIL   = "batko.digital.ai@gmail.com"
UPSELL_EMAIL    = COMPANY_EMAIL

DEFAULT_ACCESS_CODE  = "CLONE990"
DEFAULT_PAYMENT_LINK = "https://buy.stripe.com/5kQ28sdYu1U3fRF1cf3VC0d"
DEFAULT_PRICE_TEXT   = "990 Kč včetně DPH"
DEFAULT_TEASER_MODEL = "gpt-4.1-mini"
DEFAULT_REPORT_MODEL = "gpt-4.1"
UPSELL_PRICE         = "9 900 Kč"

DEMO_DESCRIPTION = (
    "Minulý měsíc jsem získal prvního platícího klienta na copywriting za 15 000 Kč. "
    "Oslovil jsem ho přes LinkedIn s krátkým videem ukázkou mé práce. "
    "Rozhodující byl osobní přístup a to, že jsem přesně popsal jeho problém ještě před tím, než jsme se potkali. "
    "Kontrakt jsem podepsal do 3 dní od prvního kontaktu."
)
# ── SECRETS HELPER ─────────────────────────────────────────────────────────
def get_cfg(key, default=None):
    try:
        val = st.secrets.get(key, None)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key, default)

# ── PROMPTS ────────────────────────────────────────────────────────────────
PROMPT_TEASER = """Jsi elitní byznys analytik. Uživatel ti popíše svůj nedávný obchodní nebo marketingový úspěch.
Tvým úkolem NENÍ chválit ho. Tvým úkolem je poskytnout mu 'Reality Check'.

Z textu vytáhni a napiš POUZE DVA BODY v českém jazyce:

**1. ✅ Znalost:** Jedna konkrétní věc, kterou uživatel udělal strategicky správně (1-2 věty).
**2. ⚠️ Slepé místo:** Jeden skrytý faktor (štěstí nebo situační podmínka), který mu pomohl, ale uživatel si ho neuvědomuje. Pokud na něj bude spoléhat příště, může selhat (1-2 věty).

Buď velmi stručný, úderný a profesionální. Cílem je vytvořit okamžitý moment uvědomění.
Nezačínaj nadpisem ani welcome textem. Rovnou odpověz dvěma body."""

PROMPT_REPORT = """Jsi forenzní analytik výkonu, který provádí reverzní inženýrství úspěchů pro podnikatele.
Úspěch vnímáš jako řetězec příčin, nikoliv jako záblesk geniality.
Tvým úkolem je ponechat uživateli metodu, nikoliv jen vzpomínku.

Z uživatelova vstupu analyzuj jeho úspěch a aplikuj kontrafaktuální test na každou příčinu:
pokud by byl tento faktor odstraněn, platil by výsledek? Odstraň zbytečnosti.

Vrať prémiový výstup PŘESNĚ v této struktuře (v českém jazyce, striktně):

---

## 🎯 Skuteční hybatelé (The Real Drivers)
*Faktory, které přežily kontrafaktuální test a odvedly nejvíce práce:*

1. **[Faktor]** — [Jedna věta, proč na tom záleželo]
2. **[Faktor]** — [Jedna věta, proč na tom záleželo]

---

## 📊 Rozpad na složky

**🟢 Dovednost (Skill)** — co jsi ovládal:
- [bod 1]
- [bod 2]

**🟡 Situace (Condition)** — podmínky, které byly náhodou pravdivé:
- [bod 1]
- [bod 2]

**🔴 Štěstí (Luck)** — slepá náhoda:
- [bod 1]

---

## ✅ Checklist pro zopakování (The Replay Checklist)
*Seřazený SOP — max 7 kroků. Každý krok = konkrétní akce pro příští podobnou situaci:*

1. [ ] [Krok]
2. [ ] [Krok]
3. [ ] [Krok]
4. [ ] [Krok]
5. [ ] [Krok]
6. [ ] [Krok]
7. [ ] [Krok]

---

## 🔁 Spouštěč (Run It Again When)
**Přesně kdy tento checklist vytáhnout:**
[1-2 konkrétní věty — situace nebo signál, který říká: teď je čas použít tuto metodu znovu]

---

## 📋 Delegovací šablona
*Email/prompt pro asistenta nebo AI, který má za vás připravit příští příležitost:*

[2-3 věty — konkrétní zadání pro asistenta, co má připravit před příštím podobným kontaktem]

---

Jazyk: tvrdý, konkrétní, bez korporátních frází a bez zbytečné chvály.
Každý bod musí být okamžitě aplikovatelný."""
# ── AI VOLÁNÍ ──────────────────────────────────────────────────────────────
def call_openai(prompt: str, user_input: str, model: str) -> str:
    try:
        from openai import OpenAI
        api_key = get_cfg("OPENAI_API_KEY")
        if not api_key:
            return "⚠️ API klíč nenalezen. Zkontrolujte secrets."
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",   "content": user_input},
            ],
            temperature=0.7,
            max_tokens=1800,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Chyba při volání AI: {e}"

def generate_teaser(success_text: str) -> str:
    return call_openai(PROMPT_TEASER, success_text, get_cfg("TEASER_MODEL", DEFAULT_TEASER_MODEL))

def generate_report(success_text: str, teaser_context: str) -> str:
    full_input = (
        f"POPIS ÚSPĚCHU OD UŽIVATELE:\n{success_text}\n\n"
        f"PŘEDBĚŽNÝ REALITY CHECK (pro kontext):\n{teaser_context}"
    )
    return call_openai(PROMPT_REPORT, full_input, get_cfg("REPORT_MODEL", DEFAULT_REPORT_MODEL))

# ── CSS (standardní šablona) ────────────────────────────────────────────────
CSS = """<style>
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #f7f5f0 !important; color: #13231b !important; }
[data-testid="stHeader"] { background: #f7f5f0 !important; border-bottom: none !important; }
[data-testid="stDecoration"] { display: none !important; }
button[kind="primary"] { background: #13231b !important; color: #f7f5f0 !important;
    border-radius: 8px !important; font-weight: 700 !important; }
[data-testid="stMetricValue"] { color: #B6452C !important; font-weight: 800 !important; font-size: 1.9rem !important; }
[data-testid="stExpander"] { background: #ffffff !important; border: 1.5px solid #e8e0d0 !important;
    border-radius: 10px !important; margin-bottom: .5rem !important; }
hr { border-color: #e8e0d0 !important; }
</style>"""

# ── HEADER ─────────────────────────────────────────────────────────────────
def render_header():
    st.markdown(
        f"<div style='font-size:.82rem;font-weight:700;color:#B6452C;"
        f"text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem'>"
        f"{APP_LABEL}</div>",
        unsafe_allow_html=True,
    )
    st.title("🔬 " + APP_TITLE)
    st.caption(APP_SUBTITLE)

# ── DEMO ───────────────────────────────────────────────────────────────────
def load_demo() -> None:
    st.session_state.success_input   = DEMO_DESCRIPTION
    st.session_state.teaser_text     = ""
    st.session_state.report_text     = ""
    st.session_state.unlocked        = False
    st.session_state.demo            = True
# ── VSTUPNÍ SEKCE ──────────────────────────────────────────────────────────
def render_input() -> str:
    st.subheader("Popište svůj nedávný úspěch")
    st.write(
        "Uzavřeli jste výjimečného klienta? Fungovalo vám volání za studena? "
        "Získali jste zakázku, která přišla jakoby sama? "
        "**Popište co se stalo — kdo, co, jak, výsledek.**"
    )

    success_text = st.text_area(
        "Váš úspěch (2–5 vět stačí):",
        placeholder=(
            "Např: Minulý týden jsem zavolal řediteli výroby v Brně. "
            "Znal jsem jejich problém z LinkedIn článku. "
            "Nabídl jsem konkrétní řešení hned v prvním hovoru — do 10 dní kontrakt za 180 000 Kč."
        ),
        height=160,
        key="success_input",
    )

    st.button(
        "🔍 Spustit Reality Check →",
        type="primary",
        use_container_width=True,
        key="generate_btn",
    )

    st.divider()

    c1, c2, c3 = st.columns(3)
    c1.metric("Čas do výsledku", "< 30 s")
    c2.metric("Kroků v checklistu", "5–7")
    c3.metric("Hodnota v koučinku", "3–8 tis. Kč")

    st.divider()

    st.markdown("**Nevíte, co čekat?**")
    st.caption("Vyzkoušejte demo — ukážeme analýzu na fiktivním příkladu.")
    st.button("▶ Načíst demo", key="demo_btn", on_click=load_demo)

    return success_text

# ── TEASER BOX ─────────────────────────────────────────────────────────────
def render_teaser(teaser_text: str):
    st.markdown(
        "<div style='background:#ffffff;border:1.5px solid #e8e0d0;border-radius:10px;"
        "padding:1.2rem 1.5rem;margin:1rem 0'>"
        "<div style='font-size:.78rem;font-weight:700;color:#B6452C;"
        "text-transform:uppercase;letter-spacing:.08em;margin-bottom:.6rem'>"
        "🔍 VÁŠ TEST REALITY</div>",
        unsafe_allow_html=True,
    )
    st.markdown(teaser_text)
    st.markdown("</div>", unsafe_allow_html=True)
# ── PAYWALL ────────────────────────────────────────────────────────────────
def render_paywall():
    payment_link = get_cfg("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    price_text   = get_cfg("PRICE_TEXT",   DEFAULT_PRICE_TEXT)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:.82rem;font-weight:700;color:#B6452C;"
        "text-transform:uppercase;letter-spacing:.08em;margin-bottom:.4rem'>"
        "KROK 2 ze 2</div>",
        unsafe_allow_html=True,
    )
    st.subheader("⚡ Odemkněte plnou forenzní analýzu")
    st.write(
        "Dostanete přesný **Replay Checklist (SOP)** — krok za krokem jak tento úspěch zopakovat. "
        "Plus Delegovací šablona + Systém spouštěčů. Připraveno do 60 sekund."
    )

    st.markdown(
        f"<div style='font-size:2rem;font-weight:800;color:#B6452C;margin:.5rem 0'>"
        f"{price_text}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<a href='{payment_link}' target='_blank' style='"
        f"display:inline-block;background:#13231b;color:#f7f5f0;"
        f"text-decoration:none;padding:.75rem 2rem;border-radius:8px;"
        f"font-weight:700;font-size:1rem;margin:.5rem 0'>"
        f"💳 Zaplatit a odemknout →</a>",
        unsafe_allow_html=True,
    )

    st.caption(
        "🛡️ Garance — pokud checklist nebude obsahovat alespoň 3 okamžitě aplikovatelné kroky, "
        "vrátíme peníze a analýzu si nechte."
    )

    with st.expander("🎁 Bonusy: Delegovací šablona + Systém spouštěčů"):
        st.write(
            "- **Delegovační šablona** — email/prompt pro asistenta nebo AI, "
            "který připraví příštímu klientovi personalizované podklady  \n"
            "- **Systém spouštěčů** — přesně definované situace/signály, "
            "kdy vytáhnout checklist a znovu ho použít"
        )

    with st.expander("Máte přístupový kód?"):
        code_input = st.text_input("Přístupový kód:", type="password", key="access_code_input")
        if st.button("🔓 Odemknout", key="unlock_btn", type="primary"):
            expected = get_cfg("ACCESS_CODE", DEFAULT_ACCESS_CODE)
            if code_input.strip().upper() == expected.upper():
                st.session_state["unlocked"] = True
                st.rerun()
            else:
                st.error("Nesprávný kód. Po platbě obdržíte kód na email.")

# ── REPORT ─────────────────────────────────────────────────────────────────
def render_report(report_text: str):
    st.success("✅ Analýza odemčena! Váš Replay Checklist je připraven.")
    st.markdown(report_text)
    st.download_button(
        label="⬇️ Stáhnout Replay Checklist (.md)",
        data=report_text,
        file_name="replay-checklist.md",
        mime="text/markdown",
        use_container_width=True,
    )
    render_upsell()
# ── UPSELL (standardní dark gradient) ─────────────────────────────────────
def render_upsell():
    st.markdown(
        f"<div style='background:linear-gradient(135deg,#0a2850,#1a4a8a);"
        f"border-radius:12px;padding:1.8rem 2rem;margin:2rem 0'>"
        f"<div style='color:#f7f5f0;font-size:1.15rem;font-weight:700;margin-bottom:.6rem'>"
        f"🚀 Chcete to zadrátovat do firmy na klíč?</div>"
        f"<div style='color:#c9d8f0;font-size:.9rem;margin-bottom:1rem'>"
        f"Máte v ruce strategii. Teď máte dvě možnosti:<br>"
        f"<strong style='color:#f7f5f0'>Možnost A:</strong> Strávit dny převodem checklistu do interních procesů.<br>"
        f"<strong style='color:#f7f5f0'>Možnost B:</strong> Nám dovolte, abychom to udělali za vás.</div>"
        f"<div style='color:#ffd700;font-size:1.8rem;font-weight:800'>"
        f"{UPSELL_PRICE} <span style='font-size:1rem;color:#c9d8f0'>vč. DPH</span></div>"
        f"<div style='color:#c9d8f0;font-size:.88rem;margin:.5rem 0 1rem'>"
        f"45minutový hovor · Převod checklistu do promptů pro váš CRM/tým · Žádná ztráta času.</div>"
        f"<a href='mailto:{UPSELL_EMAIL}?subject=Chci zadrátovat' "
        f"style='background:#ffd700;color:#0a2850;text-decoration:none;"
        f"padding:.6rem 1.6rem;border-radius:8px;font-weight:700;font-size:.95rem'>"
        f"📧 Napsat a domluvit se →</a>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ── FOOTER ─────────────────────────────────────────────────────────────────
def render_footer():
    st.divider()

    with st.expander("📞 Kontakt"):
        st.write(
            f"**{COMPANY_NAME}**  \n"
            f"{COMPANY_PERSON}  \n"
            f"IČO: {COMPANY_ICO} · DIČ: {COMPANY_DIC}  \n"
            f"{COMPANY_ADDRESS}  \n"
            f"📞 {COMPANY_PHONE}  \n"
            f"📧 {COMPANY_EMAIL}"
        )

    with st.expander("📄 Obchodní podmínky"):
        st.write(
            "Digitální produkt ve smyslu § 1837 písm. l) NOZ. "
            "Zakoupením souhlasíte se zahájením plnění před uplynutím lhůty pro odstoupení od smlouvy. "
            "Právo na odstoupení od smlouvy zaniká dodáním digitálního obsahu. "
            f"Provozovatel: {COMPANY_NAME}, IČO {COMPANY_ICO}, {COMPANY_ADDRESS}."
        )

    with st.expander("🔒 Ochrana soukromí"):
        st.write(
            "Váš popis úspěchu je zpracováván výhradně pro generování analýzy. "
            "Neukládáme žádná data na naše servery. "
            "Analýza je generována přes OpenAI API (EU region). "
            "V souladu s GDPR — žádné osobní údaje nejsou sdíleny s třetími stranami."
        )

    with st.expander("💸 Vrácení peněz"):
        st.write(
            "Garance ostrého startu: pokud checklist nebude obsahovat alespoň 3 okamžitě aplikovatelné kroky, "
            "vrátíme vám celou částku do 14 dnů bez otázek přes Stripe. "
            f"Stačí napsat na {COMPANY_EMAIL} s předmětem 'Vrácení peněz'."
        )

    st.markdown(
        f"<div style='font-size:.73rem;color:#9ca3af;text-align:center;padding:.7rem 0 .3rem'>"
        f"{COMPANY_NAME} &nbsp;·&nbsp; IČO {COMPANY_ICO} &nbsp;·&nbsp; {COMPANY_ADDRESS}"
        f"</div>",
        unsafe_allow_html=True,
    )

# ── HLAVNÍ FLOW ────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🔬",
        layout="centered",
    )
    st.markdown(CSS, unsafe_allow_html=True)
    render_header()

    # State init
    for key, default in [
        ("teaser_text", ""),
        ("report_text", ""),
        ("success_input", ""),
        ("unlocked", False),
        ("demo", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── KROK 1 ──
    success_text = render_input()

    if st.session_state.get("generate_btn"):
        if not success_text.strip():
            st.warning("Popište prosím svůj úspěch.")
        else:
            with st.spinner("Analyzuji váš úspěch..."):
                teaser = generate_teaser(success_text)
            st.session_state.teaser_text    = teaser
            st.session_state.success_input  = success_text
            st.session_state.unlocked       = False
            st.session_state.report_text    = ""
            st.rerun()

    # ── KROK 2 ──
    if st.session_state.teaser_text:
        render_teaser(st.session_state.teaser_text)

        if not st.session_state.unlocked:
            render_paywall()
        else:
            if not st.session_state.report_text:
                with st.spinner("Generuji Replay Checklist — 20–30 sekund..."):
                    report = generate_report(
                        st.session_state.success_input,
                        st.session_state.teaser_text,
                    )
                st.session_state.report_text = report
                st.rerun()
            render_report(st.session_state.report_text)

    render_footer()

if __name__ == "__main__":
    main()
