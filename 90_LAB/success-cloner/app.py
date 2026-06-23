import streamlit as st
import os

# ── CONFIG ─────────────────────────────────────────────────────────────────
APP_TITLE            = "Replikátor Úspěchu"
APP_SUBTITLE         = "Forenzní analýza vašeho úspěchu · SOP pro zopakování"
DEFAULT_ACCESS_CODE  = "CLONE990"
DEFAULT_PAYMENT_LINK = "https://buy.stripe.com/5kQ28sdYu1U3fRF1cf3VC0d"
DEFAULT_PRICE_TEXT   = "990 Kč včetně DPH"
DEFAULT_TEASER_MODEL = "gpt-4.1-mini"
DEFAULT_REPORT_MODEL = "gpt-4.1"
UPSELL_PRICE         = "9 900 Kč"
UPSELL_EMAIL         = "batko.digital.ai@gmail.com"

def get_cfg(key, default=None):
    try:
        val = st.secrets.get(key, None)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key, default)

PROMPT_TEASER = """Jsi elitní byznys analytik. Uživatel ti popíše svůj nedávný obchodní nebo marketingový úspěch.
Tvým úkolem NENÍ chválit ho. Tvým úkolem je poskytnout mu 'Reality Check'.

Z textu vytáhni a napiš POUZE DVA BODY v českém jazyce:

**1. Znalost:** Jedna konkrétní věc, kterou uživatel udělal strategicky správně (1-2 věty).
**2. Slepé místo:** Jeden skrytý faktor (štěstí nebo situační podmínka), který mu pomohl, ale uživatel si ho neuvědomuje. Pokud na něj bude spoléhat příště, může selhat (1-2 věty).

Buď velmi stručný, úderný a profesionální. Cílem je vytvořit okamžitý moment uvědomění.
Nezačínaj nadpisem ani welcome textem. Rovnou odpověz dvěma body."""

PROMPT_REPORT = """Jsi forenzní analytik výkonu, který provádí reverzní inženýrství úspěchů pro podnikatele.
Úspěch vnímáš jako řetězec příčin, nikoliv jako záblesk geniality.

Z uživatelova vstupu analyzuj jeho úspěch a aplikuj kontrafaktuální test na každou příčinu.

Vrať prémiový výstup PŘESNĚ v této struktuře (v českém jazyce):

---

## Skuteční hybatelé (The Real Drivers)

1. **[Faktor]** — [Proč na tom záleželo]
2. **[Faktor]** — [Proč na tom záleželo]

---

## Rozpad na složky

**Dovednost (Skill)** — co jsi ovládal:
- [bod]

**Situace (Condition)** — podmínky, které byly náhodou pravdivé:
- [bod]

**Štěstí (Luck)** — slepá náhoda:
- [bod]

---

## Checklist pro zopakování (The Replay Checklist)

1. [ ] [Krok]
2. [ ] [Krok]
3. [ ] [Krok]
4. [ ] [Krok]
5. [ ] [Krok]

---

## Spouštěč (Run It Again When)
[1-2 konkrétní věty kdy checklist použít]

---

Jazyk: tvrdý, konkrétní, bez korporátních frází."""

def call_openai(prompt, user_input, model):
    try:
        from openai import OpenAI
        api_key = get_cfg("OPENAI_API_KEY")
        if not api_key:
            return "API klic nenalezen."
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content":prompt},{"role":"user","content":user_input}],
            temperature=0.7,
            max_tokens=1800,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Chyba: {e}"

def generate_teaser(text):
    return call_openai(PROMPT_TEASER, text, get_cfg("TEASER_MODEL", DEFAULT_TEASER_MODEL))

def generate_report(text, teaser):
    model = get_cfg("REPORT_MODEL", DEFAULT_REPORT_MODEL)
    full = f"POPIS USPECHU:\n{text}\n\nREALITY CHECK:\n{teaser}"
    return call_openai(PROMPT_REPORT, full, model)

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.hero{background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:16px;padding:2.5rem 2rem;margin-bottom:1.5rem;border:1px solid #334155;text-align:center;}
.hero h1{color:#f8fafc;font-size:2.2rem;font-weight:800;margin:0 0 .5rem 0;}
.hero p{color:#94a3b8;font-size:1rem;margin:0;}
.step-badge{display:inline-block;background:#6366f1;color:white;font-size:.75rem;font-weight:700;padding:.2rem .7rem;border-radius:999px;margin-bottom:.75rem;}
.teaser-box{background:#0f172a;border:1px solid #1e40af;border-radius:12px;padding:1.5rem;margin:1.5rem 0;}
.teaser-title{color:#93c5fd;font-size:.8rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:1rem;}
.paywall-box{background:linear-gradient(135deg,#1e1b4b,#0f172a);border:1px solid #4f46e5;border-radius:16px;padding:2rem;margin:1.5rem 0;text-align:center;}
.paywall-box h3{color:#e2e8f0;font-size:1.3rem;font-weight:700;}
.paywall-box .price{color:#818cf8;font-size:2rem;font-weight:800;margin:.5rem 0;}
.paywall-box .guarantee{color:#64748b;font-size:.8rem;font-style:italic;margin-top:1rem;}
.bonus-box{background:#0f2d1a;border:1px solid #166534;border-radius:10px;padding:1rem 1.2rem;margin:1rem 0;font-size:.88rem;color:#86efac;}
.upsell-box{background:linear-gradient(135deg,#1c0533,#0f172a);border:2px solid #7c3aed;border-radius:16px;padding:2rem;margin:2rem 0;}
.upsell-box h3{color:#c4b5fd;font-size:1.2rem;font-weight:700;}
.upsell-price{color:#a78bfa;font-size:1.6rem;font-weight:800;}
.report-container{background:#0f172a;border:1px solid #334155;border-radius:12px;padding:1.5rem;color:#e2e8f0;}
div.stButton>button{background:linear-gradient(135deg,#4f46e5,#6366f1);color:white;border:none;border-radius:10px;padding:.65rem 2rem;font-weight:700;font-size:1rem;width:100%;}
.stripe-btn{display:inline-block;background:linear-gradient(135deg,#4f46e5,#7c3aed);color:white!important;text-decoration:none!important;padding:.8rem 2.5rem;border-radius:12px;font-weight:700;font-size:1.1rem;margin:1rem 0;}
</style>
""", unsafe_allow_html=True)

def render_hero():
    st.markdown(f'<div class="hero"><h1>🔬 {APP_TITLE}</h1><p>{APP_SUBTITLE}</p></div>', unsafe_allow_html=True)

def render_paywall():
    link = get_cfg("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    price = get_cfg("PRICE_TEXT", DEFAULT_PRICE_TEXT)
    st.markdown(f"""
<div class="paywall-box">
<h3>Odemkněte plnou forenzní analýzu</h3>
<p style="color:#94a3b8;">Replay Checklist (SOP) + Delegovací šablona + Systém spouštěčů</p>
<div class="price">{price}</div>
<a href="{link}" target="_blank" class="stripe-btn">💳 Zaplatit a odemknout →</a>
<p class="guarantee">Garance — min. 3 okamžitě aplikovatelné kroky, nebo vracíme peníze.</p>
</div>""", unsafe_allow_html=True)
    st.markdown('<div class="bonus-box">Bonusy: Delegovací šablona + Systém spouštěčů</div>', unsafe_allow_html=True)
    with st.expander("Máte přístupový kód?"):
        code = st.text_input("Kód:", type="password", key="code_input")
        if st.button("Odemknout", key="unlock_btn"):
            if code.strip().upper() == get_cfg("ACCESS_CODE", DEFAULT_ACCESS_CODE).upper():
                st.session_state["unlocked"] = True
                st.rerun()
            else:
                st.error("Nesprávný kód.")

def render_upsell():
    st.markdown(f"""
<div class="upsell-box">
<h3>Chcete to zadrátovat do firmy na klíč?</h3>
<div class="upsell-price">{UPSELL_PRICE} <span style="font-size:1rem;color:#a78bfa;">vč. DPH</span></div>
<p style="color:#c4b5fd;font-size:.9rem;">45min hovor · převod checklistu do promptů pro CRM/tým · zero time delay.</p>
<p style="color:#94a3b8;font-size:.85rem;">Email: <strong style="color:#c4b5fd;">{UPSELL_EMAIL}</strong> · předmět: "Chci zadrátovat"</p>
</div>""", unsafe_allow_html=True)

def render_report(report_text):
    st.success("Analýza odemčena!")
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown(report_text)
    st.markdown('</div>', unsafe_allow_html=True)
    st.download_button("Stáhnout Replay Checklist", data=report_text, file_name="replay-checklist.md", mime="text/markdown", use_container_width=True)
    render_upsell()

def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🔬", layout="centered")
    inject_css()
    render_hero()
    for k in ("teaser_text","report_text","success_input_saved","unlocked"):
        if k not in st.session_state:
            st.session_state[k] = "" if k != "unlocked" else False
    st.markdown('<span class="step-badge">KROK 1 ze 2</span>', unsafe_allow_html=True)
    st.markdown("### Popište svůj nedávný úspěch")
    success_text = st.text_area("Váš úspěch (2–5 vět):", placeholder="Např: Zavolal jsem řediteli výroby v Brně, znal jsem jejich problém a do 10 dní jsme podepsali kontrakt za 180 000 Kč.", height=160, key="success_input")
    col1, _ = st.columns([1,2])
    with col1:
        go = st.button("Spustit Reality Check", use_container_width=True)
    if go:
        if not success_text.strip():
            st.warning("Popište prosím svůj úspěch.")
        else:
            with st.spinner("Analyzuji..."):
                teaser = generate_teaser(success_text)
            st.session_state.update({"teaser_text":teaser,"success_input_saved":success_text,"unlocked":False,"report_text":""})
            st.rerun()
    if st.session_state["teaser_text"]:
        st.markdown(f'<div class="teaser-box"><div class="teaser-title">Váš Reality Check</div>{st.session_state["teaser_text"]}</div>', unsafe_allow_html=True)
        if not st.session_state["unlocked"]:
            st.markdown("---")
            st.markdown('<span class="step-badge">KROK 2 ze 2</span>', unsafe_allow_html=True)
            render_paywall()
        else:
            if not st.session_state["report_text"]:
                with st.spinner("Generuji Replay Checklist — 20–30 sekund..."):
                    report = generate_report(st.session_state["success_input_saved"], st.session_state["teaser_text"])
                st.session_state["report_text"] = report
                st.rerun()
            render_report(st.session_state["report_text"])

if __name__ == "__main__":
    main()
