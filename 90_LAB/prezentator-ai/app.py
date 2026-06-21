import streamlit as st
import os

# ─── Konfigurace ───────────────────────────────────────────────────────────────
APP_TITLE    = "Prezentátor.ai"
APP_SUBTITLE = "Z vašich poznámek na profesionální prezentaci za 60 sekund"

DEFAULT_ACCESS_CODE         = ""
DEFAULT_PAYMENT_LINK        = "https://buy.stripe.com/your-payment-link"
DEFAULT_OPENAI_MODEL        = "gpt-4.1-mini"
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"
DEFAULT_PRICE_TEXT          = "990 Kč"


def get_config(name, default=None):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


# ─── Prompty ───────────────────────────────────────────────────────────────────
PROMPT_A = """
Jsi elitní stratég pro prezentace. Zákazník dodal toto téma a poznámky:

{USER_INPUT}

Tvým úkolem je ZDARMA navrhnout dokonalou, prodejně optimalizovanou osnovu (max 7 bodů),
která v zákazníkovi vyvolá 'Aha moment'.
Napiš také přesný, poutavý text pro úvodní Slide 1 (Hook/Háček) a Slide 2 (Hlavní problém).
Buď stručný, profesionální a piš striktně v češtině. Žádná omáčka.
Ukaž mu, že chápeš jeho byznys lépe než on sám.
""".strip()

PROMPT_B = """
Jsi elitní HTML PPT Studio Agent. Tvým úkolem je transformovat uživatelovy poznámky
do produkčně připravené, statické HTML prezentace s moderními GSAP animacemi.

Téma a poznámky zákazníka:
{USER_INPUT}

Typ prezentace: {PRESENTATION_TYPE}
Struktura pro pitch-deck: Cover → Problém → Řešení → Trakce → Trh → Byznys model → Tým → Výzva k akci

═══════════════════════════════════════════════════════════
PRAVIDLA VÝSTUPU — NESMÍŠ porušit ANI JEDNO:
═══════════════════════════════════════════════════════════

1. Jeden soubor HTML5 začínající <!DOCTYPE html>.
   Jen tyto CDN: GSAP 3.12.2 z cdnjs, Inter font z Google Fonts.

2. Každý slide: <section class="slide"> (BEZ inline style="display:none"!).
   Počet slidů: 10–15. První slide NESMÍ mít class "active" v HTML — JS to nastaví.

3. POVINNÁ CSS ARCHITEKTURA SLIDŮ (ZKOPÍRUJ PŘESNĚ):
   .slide-wrapper {{ position:relative; width:100vw; height:100vh; overflow:hidden; }}
   .slide {{
     position:absolute; top:0; left:0; width:100%; height:100%;
     display:flex; flex-direction:column; align-items:center; justify-content:center;
     opacity:0; pointer-events:none; padding:4rem 6rem;
     /* BEZ display:none — viditelnost řídí POUZE opacity! */
   }}
   .slide.active {{ opacity:1; pointer-events:auto; }}
   .notes {{ display:none; }}

4. POVINNÝ JAVASCRIPT SKELETON (ZKOPÍRUJ A DOPLŇ):
   let cur = 0;
   const slides = document.querySelectorAll('.slide');
   const prog = document.getElementById('progress');

   function show(n) {{
     if (slides[cur]) slides[cur].classList.remove('active');
     cur = Math.max(0, Math.min(n, slides.length - 1));
     slides[cur].classList.add('active');
     prog.style.width = ((cur + 1) / slides.length * 100) + '%';
     gsap.fromTo(slides[cur],
       {{ opacity: 0, y: 40 }},
       {{ opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }}
     );
   }}

   function togglePresenter() {{ /* ... */ }}

   document.addEventListener('keydown', e => {{
     if (e.key === 'ArrowRight') show(cur + 1);
     if (e.key === 'ArrowLeft')  show(cur - 1);
     if (e.key === 's' || e.key === 'S') togglePresenter();
     if (e.key === 'Escape') document.getElementById('presenter').style.display = 'none';
   }});

   window.onload = function() {{ show(0); }};  // NUTNO volat přes window.onload!

5. Design:
   - CSS :root proměnné pro barvy — žádné hardcoded hex mimo :root.
   - Téma: tmavé pozadí (#0f172a), akcenty fialová (#7c3aed) / modrá (#3b82f6).
   - Karty s glassmorphism (backdrop-filter:blur, border semi-transparentní).
   - Progress bar #progress: position:fixed; bottom:0; left:0; height:4px; background:var(--accent).

6. Presenter Mode overlay:
   - <div id="presenter"> s display:none v CSS, z-index:100.
   - Klávesa S → zobrazí poznámky aktuálního slidu.
   - Klávesa Escape nebo klik ✕ → zavře overlay.

7. Řečnické poznámky:
   - Na konci KAŽDÉHO <section class="slide"> vlož <div class="notes">.
   - 150–300 slov v češtině, konverzační styl.

8. Vrať VÝHRADNĚ platný HTML kód. Žádný text před <!DOCTYPE> ani za </html>.
   Vše v perfektní češtině.
""".strip()


# ─── Fallback (bez API klíče) ──────────────────────────────────────────────────
def _local_teaser(user_input: str) -> str:
    return f"""## Osnova prezentace: *{user_input[:80]}*

**Navržená struktura (7 bodů):**
1. 🎯 **Hook** — Poutavý úvod, který zastaví scrollování
2. 💡 **Problém** — Bolestivá realita, kterou vaše publikum zná
3. 🚀 **Řešení** — Váš unikátní přístup k problému
4. 📊 **Důkazy a trakce** — Čísla a výsledky, které mluví za vás
5. 🌍 **Trh a příležitost** — Jak velká je příležitost
6. 💰 **Byznys model** — Jak na tom vyděláte
7. 📣 **Výzva k akci** — Jasný a neodolatelný další krok

---
**Slide 1 — Hook:**
*„Každý rok přijdou tisíce podnikatelů o zakázky — ne proto, že mají špatný produkt,
ale proto, že neumí přesvědčivě prezentovat."*

**Slide 2 — Problém:**
*Vaši potenciální klienti a investoři vidí desítky prezentací týdně. Té vaší musí
porozumět za 30 sekund a musí si ji pamatovat za 30 dnů. Jinak ji zahodí.*

---
⚠️ *Toto je bezplatný náhled. Kompletní animovaná prezentace (10–15 slidů s GSAP efekty
a řečnickými poznámkami) čeká za paywallem.*"""


def _local_presentation() -> str:
    return """<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Ukázková prezentace — Prezentátor.ai</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<style>
:root {
  --bg: #0f172a; --surface: #1e293b; --accent: #7c3aed;
  --accent2: #3b82f6; --text: #f1f5f9; --muted: #94a3b8;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; overflow: hidden; }
/* Pozor: slides pouzivaji position:absolute + opacity, NIKOLI display:none! */
.slide-wrapper { position: relative; width: 100vw; height: 100vh; overflow: hidden; }
.slide {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 1.5rem; padding: 4rem 6rem;
  opacity: 0; pointer-events: none;
}
.slide.active { opacity: 1; pointer-events: auto; }
h1 { font-size: clamp(2rem, 5vw, 4rem); font-weight: 700; text-align: center; }
p  { font-size: clamp(1rem, 2vw, 1.4rem); color: var(--muted); max-width: 60ch; text-align: center; }
.notes { display: none; }
#progress { position: fixed; bottom: 0; left: 0; height: 4px;
  background: var(--accent); transition: width .3s; z-index: 50; }
#presenter { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.92);
  padding: 3rem; overflow-y: auto; z-index: 100; }
#presenter p { color: #e2e8f0; font-size: 1.2rem; line-height: 1.8; max-width: 70ch; margin: auto; }
#presenter .close { position: fixed; top: 1rem; right: 1.5rem; font-size: 1.5rem;
  cursor: pointer; color: var(--muted); }
</style>
</head>
<body>

<div class="slide-wrapper">
  <section class="slide">
    <h1>Vaše prezentace</h1>
    <p>Toto je ukázkový slide vygenerovaný bez OpenAI API klíče.<br>
       Skutečná verze bude mít 10–15 plně animovaných slidů s vašim obsahem.</p>
    <div class="notes">Ukázkové řečnické poznámky. Ve skutečné prezentaci zde budete mít
    150–300 slov konverzačního textu, který vám pomůže ovládnout místnost.</div>
  </section>

  <section class="slide">
    <h1>Jak to funguje</h1>
    <p>Po zadání OpenAI API klíče vygeneruje Prezentátor.ai kompletní interaktivní
    HTML prezentaci přímo z vašich poznámek.</p>
    <div class="notes">Druhý slide. Vysvětlete zákazníkovi, jak jednoduché to je.</div>
  </section>
</div>

<div id="progress"></div>
<div id="presenter"><span class="close" onclick="togglePresenter()">✕</span><p id="notesText"></p></div>

<script>
let cur = 0;
const slides = document.querySelectorAll('.slide');
const prog = document.getElementById('progress');
const presenter = document.getElementById('presenter');

function show(n) {
  if (slides[cur]) slides[cur].classList.remove('active');
  cur = Math.max(0, Math.min(n, slides.length - 1));
  slides[cur].classList.add('active');
  prog.style.width = ((cur + 1) / slides.length * 100) + '%';
  gsap.fromTo(slides[cur],
    { opacity: 0, y: 40 },
    { opacity: 1, y: 0, duration: 0.5, ease: 'power2.out' }
  );
}

function togglePresenter() {
  if (presenter.style.display === 'block') {
    presenter.style.display = 'none';
  } else {
    const notes = slides[cur].querySelector('.notes');
    document.getElementById('notesText').textContent =
      notes ? notes.textContent.trim() : 'Žádné poznámky.';
    presenter.style.display = 'block';
  }
}

document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') show(cur + 1);
  if (e.key === 'ArrowLeft')  show(cur - 1);
  if (e.key === 's' || e.key === 'S') togglePresenter();
  if (e.key === 'Escape') presenter.style.display = 'none';
});

window.onload = function() { show(0); };
</script>
</body>
</html>"""


# ─── OpenAI volání ─────────────────────────────────────────────────────────────
def generate_teaser(user_input: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=get_config("OPENAI_API_KEY"))
    model  = get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    resp   = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": PROMPT_A.format(USER_INPUT=user_input)}],
        max_tokens=900,
        temperature=0.7,
    )
    return resp.choices[0].message.content


def generate_presentation(user_input: str, presentation_type: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=get_config("OPENAI_API_KEY"))
    model  = get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    resp   = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": PROMPT_B.format(
            USER_INPUT=user_input,
            PRESENTATION_TYPE=presentation_type,
        )}],
        max_tokens=8000,
        temperature=0.7,
    )
    return resp.choices[0].message.content


def extract_html(text: str) -> str:
    """Vrátí čistý HTML kód — odstraní případný markdown wrapper."""
    if "```html" in text:
        text = text.split("```html", 1)[1]
        text = text.split("```", 1)[0]
    if "<!DOCTYPE" in text:
        text = text[text.index("<!DOCTYPE"):]
    return text.strip()


# ─── UI ────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown("""
    <style>
    #MainMenu {visibility:hidden;} footer {visibility:hidden;}
    .block-container {padding-top: 2rem;}
    .main-header {text-align:center; padding: 1.5rem 0 1rem;}
    .step-box {background:#f8faff; border-radius:14px; padding:1.5rem 2rem;
               margin:1rem 0; border-left:5px solid #7c3aed;}
    .paywall-box {background:linear-gradient(135deg,#7c3aed 0%,#3b82f6 100%);
                  color:white; border-radius:18px; padding:2.5rem 2rem;
                  text-align:center; margin:2rem 0;}
    .upsell-box {background:#fffbeb; border-radius:14px; padding:1.5rem 2rem;
                 border:2px solid #f59e0b; margin:1.5rem 0;}
    .success-box {background:#f0fdf4; border-radius:14px; padding:1.5rem 2rem;
                  border-left:5px solid #22c55e; margin:1rem 0;}
    kbd {background:#e2e8f0; border-radius:4px; padding:2px 6px; font-family:monospace;}
    /* ── Zelené tlačítko pro stažení ── */
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: linear-gradient(135deg, #15803d 0%, #16a34a 100%) !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Načtení konfigurace
    price_text    = get_config("PRICE_TEXT",    DEFAULT_PRICE_TEXT)
    payment_link  = get_config("PAYMENT_LINK",  DEFAULT_PAYMENT_LINK)
    access_code   = get_config("ACCESS_CODE",   DEFAULT_ACCESS_CODE)
    allow_fallback = get_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK).lower() == "true"

    # Session state
    for key, val in {
        "stage": "input",       # input | teaser | unlocked
        "user_input": "",
        "pres_type": "pitch-deck",
        "teaser": "",
        "html": "",
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # ── HEADER ──
    st.markdown(f"""
    <div class="main-header">
        <h1>🎯 {APP_TITLE}</h1>
        <p style="font-size:1.15em; color:#64748b;">{APP_SUBTITLE}</p>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # KROK 1 — vstup
    # ══════════════════════════════════════════════════════════
    if st.session_state.stage == "input":

        st.markdown('<div class="step-box">', unsafe_allow_html=True)
        st.markdown("### 📝 Vložte vaše téma a poznámky")
        st.caption("Stačí pár vět nebo odrážek. AI pochopí záměr a navrhne strukturu.")

        user_input = st.text_area(
            "Vaše téma / poznámky:",
            placeholder=(
                "Např: Chci prezentovat realitní projekt v Dubaji investorům. "
                "Máme 50 bytů, cena od 5M CZK, výnos 8 % p.a., vstup od 1M CZK..."
            ),
            height=160,
            key="ta_input",
        )

        pres_type_label = st.selectbox(
            "Typ prezentace:",
            [
                "pitch-deck — pro investory a fundraising",
                "product-launch — pro klienty a obchodní prezentace",
                "case-study — referenční případ / úspěšný projekt",
            ],
        )
        pres_type = pres_type_label.split("—")[0].strip()

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Vygenerovat náhled zdarma", type="primary", use_container_width=True):
                if not user_input.strip():
                    st.warning("Prosím vložte téma nebo poznámky.")
                else:
                    st.session_state.user_input = user_input.strip()
                    st.session_state.pres_type  = pres_type
                    with st.spinner("🧠 AI analyzuje váš byznys a navrhuje strukturu..."):
                        try:
                            api_key = get_config("OPENAI_API_KEY")
                            if api_key:
                                st.session_state.teaser = generate_teaser(user_input)
                            else:
                                st.session_state.teaser = _local_teaser(user_input)
                        except Exception as e:
                            if allow_fallback:
                                st.session_state.teaser = _local_teaser(user_input)
                            else:
                                st.error(f"Chyba generování: {e}")
                                st.stop()
                    st.session_state.stage = "teaser"
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Social proof
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("⚡ Čas do výsledku", "< 60 s")
        c2.metric("🎨 Animovaných slidů", "10–15")
        c3.metric("💰 Hodnota u agentury", "5–10 000 Kč")

    # ══════════════════════════════════════════════════════════
    # KROK 2 — teaser + paywall
    # ══════════════════════════════════════════════════════════
    elif st.session_state.stage == "teaser":

        st.success("✅ Osnova vaší prezentace je připravena!")

        with st.container():
            st.markdown("### 👁️ Bezplatný náhled — Osnova + první 2 slidy")
            st.markdown(st.session_state.teaser)

        st.markdown("---")

        # Paywall box
        st.markdown(f"""
        <div class="paywall-box">
          <h2 style="margin-bottom:.5rem;">🔒 Kompletní prezentace čeká</h2>
          <p style="font-size:1.1em; opacity:.95;">
            10–15 animovaných slidů · GSAP efekty · Řečnické poznámky v češtině<br>
            Jeden HTML soubor → otevřete v Chrome → prezentujete.
          </p>
          <h3 style="font-size:2.2em; margin:1.2rem 0;">
            {price_text}
            <span style="text-decoration:line-through; opacity:.55; font-size:.55em; margin-left:.5rem;">
              bývá 5 000 Kč u agentury
            </span>
          </h3>
          <p style="font-size:.9em; opacity:.88;">
            🛡️ Garance: Pokud vaši klienti nebudou nadšení, vracíme 100 % do 24 hodin.
            Soubor si můžete ponechat.
          </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.link_button(
                "💳 Zaplatit a odemknout prezentaci",
                payment_link,
                use_container_width=True,
                type="primary",
            )

        st.markdown("**🎁 Bonus zdarma ke každé prezentaci:**")
        st.markdown(
            "PDF Tahák: *Jak ovládnout místnost* — pravidla řeči těla a hlasu pro sebejisté vystupování"
        )

        st.markdown("---")

        with st.expander("💬 Máte přístupový kód? (Obdržíte ho e-mailem po platbě)"):
            code_input = st.text_input(
                "Přístupový kód:", type="password", key="pw_input"
            )
            if st.button("🔓 Odemknout", key="btn_unlock"):
                if code_input.strip() == access_code:
                    with st.spinner("🎨 Generuji vaši prezentaci… (30–60 sekund)"):
                        try:
                            api_key = get_config("OPENAI_API_KEY")
                            if api_key:
                                raw  = generate_presentation(
                                    st.session_state.user_input,
                                    st.session_state.pres_type,
                                )
                                html = extract_html(raw)
                            else:
                                html = _local_presentation()
                        except Exception as e:
                            if allow_fallback:
                                html = _local_presentation()
                            else:
                                st.error(f"Chyba: {e}")
                                st.stop()
                    st.session_state.html  = html
                    st.session_state.stage = "unlocked"
                    st.rerun()
                else:
                    st.error("❌ Nesprávný kód. Zkontrolujte e-mail nebo kontaktujte podporu.")

        if st.button("← Upravit téma"):
            st.session_state.stage = "input"
            st.rerun()

    # ══════════════════════════════════════════════════════════
    # KROK 3 — doručení
    # ══════════════════════════════════════════════════════════
    elif st.session_state.stage == "unlocked":

        st.balloons()

        st.markdown("""
        <div class="success-box">
          <h2>🎉 Vaše prezentace je hotová!</h2>
          <p>
            <strong>3 jednoduché kroky:</strong><br>
            1. Klikněte na zelené tlačítko níže a stáhněte soubor <code>prezentace.html</code><br>
            2. Dvojklikem otevřete soubor v <strong>Google Chrome</strong><br>
            3. <kbd>→</kbd> pohyb mezi slidy &nbsp;·&nbsp; <kbd>S</kbd> zobrazí řečnické poznámky
               &nbsp;·&nbsp; <kbd>Esc</kbd> zavře Presenter Mode
          </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="⬇️ Stáhnout prezentaci (HTML)",
                data=st.session_state.html.encode("utf-8"),
                file_name="prezentace.html",
                mime="text/html",
                type="primary",
                use_container_width=True,
            )

        st.markdown("---")

        # Upsell
        st.markdown("""
        <div class="upsell-box">
          <h3>🏆 Hrajete o zakázky za statisíce?</h3>
          <p><strong>VIP Pitch Deck & Trénink — Done For You</strong></p>
          <ul style="margin: .8rem 0 .8rem 1.2rem; line-height:2;">
            <li>✅ 45min Zoom hovor — osobně projdeme strukturu pro vaši nejdůležitější schůzku</li>
            <li>✅ Expert manuálně posílí prodejní copy celé prezentace</li>
            <li>✅ Převod do vašeho firemního designu (logo, barvy, fonty)</li>
            <li>✅ Trénink prezentace: jak odprezentovat tak, aby klient nemohl říct ne</li>
          </ul>
          <p><strong>Cena: 9 900 Kč</strong>
             <span style="color:#78716c;"> (vs. agentura: 25 000–50 000 Kč)</span></p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.link_button(
                "📧 Mám zájem o VIP servis",
                "mailto:batko.digital.ai@gmail.com"
                "?subject=VIP%20Pitch%20Deck%20%E2%80%94%20z%C3%A1jem"
                "&body=Dobr%C3%BD%20den%2C%20m%C3%A1m%20z%C3%A1jem%20o%20VIP%20Pitch%20Deck%20servis%20za%209%20900%20K%C4%8D.",
                use_container_width=True,
            )

        st.markdown("---")
        if st.button("🔄 Vytvořit další prezentaci"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


if __name__ == "__main__":
    main()
