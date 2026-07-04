"""
AI Akvizicni Tovarna — BATKO.DIGITAL.AI
Kompletni prodejni SaaS (stejny funnel jako ostatni appky v projektu):
  2 otazky -> teaser zdarma -> Stripe paywall -> pristupovy kod -> plne placene plneni -> upsell.
Klice: st.secrets -> os.environ -> sdileny MASTER_CONFIG.toml.
  OPENAI_API_KEY sdileny (negeneruje se per-app), Stripe = PAYMENT_LINK per-app.
"""

import os
from typing import Dict, List, Optional

import streamlit as st

APP_TITLE = "AI Akviziční Továrna"
DEFAULT_ACCESS_CODE = ""
DEFAULT_PAYMENT_LINK = "https://buy.stripe.com/your-payment-link"
DEFAULT_TEASER_MODEL = "gpt-4.1-mini"
DEFAULT_REPORT_MODEL = "gpt-4.1"
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"
DEFAULT_PRICE_TEXT = "1 490 Kč včetně DPH"

APP_DIR = os.path.dirname(os.path.abspath(__file__))

DEMO_ANSWERS = {
    "offer": "Pořádám soutěž krásy Miss Princess of the World s velkým mediálním zásahem a hledám firemní partnery a sponzory.",
    "target": "Chci oslovit kosmetické značky, kliniky estetické medicíny a módní e-shopy střední a větší velikosti v ČR. Cíl: 5 schůzek se sponzory do měsíce.",
}


# ----------------------------- Konfigurace (domaci vzor) -----------------------------
def _load_master_config() -> Dict[str, str]:
    cfg: Dict[str, str] = {}
    for path in (os.path.join(APP_DIR, "MASTER_CONFIG.toml"),
                 os.path.join(APP_DIR, "..", "MASTER_CONFIG.toml")):
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    cfg.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except Exception:
            pass
    return cfg

_MASTER = _load_master_config()


def get_config(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        val = st.secrets.get(name)
    except Exception:
        val = None
    if val is None:
        val = os.getenv(name)
    if val is None:
        val = _MASTER.get(name, default)
    return val


def get_bool_config(name: str, default: str = "false") -> bool:
    return str(get_config(name, default)).strip().lower() in {"1", "true", "yes", "on"}


STEPS: List[Dict[str, str]] = [
    {
        "key": "offer",
        "label": "Krok 1 ze 2",
        "prompt": "Co nabízíte a pro jakou akci, projekt nebo firmu hledáte partnery či sponzory?",
        "placeholder": "Např.: Pořádám hudební festival pro 5 000 lidí a hledám generálního partnera. Nebo: Mám B2B SaaS a hledám firmy, kterým ušetří náklady.",
    },
    {
        "key": "target",
        "label": "Krok 2 ze 2",
        "prompt": "Koho chcete oslovit (obor, velikost firem, region) a jaký je váš cíl?",
        "placeholder": "Např.: Chci oslovit stavební firmy do 50 zaměstnanců v Praze, cíl 5 schůzek za měsíc. Nebo: Kosmetické značky s obratem 50M+, cíl 3 sponzoři.",
    },
]


def init_state() -> None:
    defaults = {
        "step_index": 0,
        "answers": {},
        "unlocked": False,
        "teaser": None,
        "final_report": None,
        "last_error": None,
        "demo_loaded": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_history() -> None:
    answers = st.session_state.answers
    if not answers:
        return
    with st.expander("Vaše odpovědi", expanded=False):
        for step in STEPS:
            val = answers.get(step["key"])
            if val:
                st.markdown(f"**{step['label']}**")
                st.write(val)


def save_answer(step_key: str, answer: str) -> None:
    st.session_state.answers[step_key] = answer.strip()
    st.session_state.step_index += 1
    st.rerun()


def reset_app() -> None:
    for key in ["step_index", "answers", "unlocked", "teaser",
                "final_report", "last_error", "demo_loaded"]:
        st.session_state.pop(key, None)
    st.rerun()


def load_demo_case() -> None:
    st.session_state.answers = DEMO_ANSWERS.copy()
    st.session_state.step_index = len(STEPS)
    st.session_state.unlocked = False
    st.session_state.teaser = None
    st.session_state.final_report = None
    st.session_state.last_error = None
    st.session_state.demo_loaded = True


def get_openai_client():
    api_key = get_config("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception:
        return None


def build_teaser_prompt() -> str:
    a = st.session_state.answers
    return (
        "Jsi špičkový B2B akviziční stratég pro sponzoring a partnerství.\n"
        f"Nabídka / projekt uživatele: {a.get('offer', '')}\n"
        f"Cílová skupina a cíl: {a.get('target', '')}\n\n"
        "Vygeneruj přesně 3 konkrétní typy firem/segmentů, které by měly reálný důvod tohoto partnera/sponzora podpořit. "
        "Pro každý napiš:\n"
        "- Název segmentu (konkrétní, ne obecný)\n"
        "- Jedna věta: proč právě je to dává smysl (jejich motivace)\n"
        "- Jeden úderný oslovovací háček (1 věta), na který by reagovali\n\n"
        "Formát: **Segment 1/2/3**. Bez vaty, česky s diakritikou, lidsky."
    )


def build_kit_prompt() -> str:
    a = st.session_state.answers
    return (
        "Jsi elitní B2B akviziční stratég a copywriter (styl Alex Hormozi: prodej výsledku, ne procesu).\n"
        f"Nabídka / projekt uživatele: {a.get('offer', '')}\n"
        f"Cílová skupina a cíl: {a.get('target', '')}\n\n"
        "Vytvoř KOMPLETNÍ akviziční kit v češtině s diakritikou. Bez vaty, jen použitelný obsah:\n\n"
        "**🎯 Cílové segmenty (4–5)**\n"
        "Konkrétní typy firem + u každého 1 věta proč a jeden personalizační bod, který si má uživatel zjistit.\n\n"
        "**✉️ E-mailová sekvence (3 kroky)**\n"
        "Krok 1 – první oslovení, Krok 2 – follow-up po 3 dnech, Krok 3 – poslední po 7 dnech. "
        "U každého: PŘEDMĚT + tělo max 120 slov, lidský tón, žádné AI fráze, jasná nízkoprahová výzva (krátký hovor).\n\n"
        "**💬 LinkedIn varianta**\n"
        "Krátká úvodní zpráva (max 60 slov) na LinkedIn pro stejný segment.\n\n"
        "**📋 Checklist doručitelnosti**\n"
        "Konkrétně: samostatná doména, warm-up schránky, kolik e-mailů denně max, jak nezapadnout do spamu, kdy přestat.\n\n"
        "**📊 Realistická čísla**\n"
        "Poctivě: konverze cold e-mailu na schůzku bývá pod 1–2 %. Spočítej, kolik firem musí uživatel oslovit, "
        "aby při 1 % dostal počet schůzek ze svého cíle. Žádné přehnané sliby.\n\n"
        "**⚡ První krok — dnes**\n"
        "Přesně jedna akce na příští 2 hodiny. Brutálně konkrétní.\n\n"
        "Tón: přímý, profesionální, lidský. Striktně česky s diakritikou."
    )


def generate_teaser() -> str:
    client = get_openai_client()
    if client is None:
        return _local_teaser()
    try:
        resp = client.chat.completions.create(
            model=get_config("TEASER_MODEL", DEFAULT_TEASER_MODEL),
            temperature=0.5,
            messages=[{"role": "user", "content": build_teaser_prompt()}],
        )
        return resp.choices[0].message.content or _local_teaser()
    except Exception:
        return _local_teaser()


def generate_final_report() -> str:
    client = get_openai_client()
    if client is None:
        if get_bool_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK):
            return _local_report()
        raise RuntimeError("Chybí OPENAI_API_KEY v Secrets / MASTER_CONFIG.toml.")
    try:
        resp = client.chat.completions.create(
            model=get_config("REPORT_MODEL", DEFAULT_REPORT_MODEL),
            temperature=0.4,
            messages=[{"role": "user", "content": build_kit_prompt()}],
        )
        return resp.choices[0].message.content or _local_report()
    except Exception:
        if get_bool_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK):
            return _local_report()
        raise


def _local_teaser() -> str:
    a = st.session_state.answers
    target = a.get("target", "vaší cílové skupiny")
    return (
        f"**Segment 1 — Firmy s produktem pro stejné publikum**\n"
        f"Značky, které cílí na totéž publikum jako vy z '{target}'. Motivace: přístup k vaší cílovce. "
        f"Háček: „Vaše cílovka je přesně naše publikum — ukážu vám, jak se před ní objevíte.\"\n\n"
        f"**Segment 2 — Lokální firmy hledající viditelnost**\n"
        f"Regionální hráči, kteří chtějí posílit značku. Motivace: PR a známost. "
        f"Háček: „Hledáme 1 lokálního partnera — ne masu log, ale jednu firmu, která vynikne.\"\n\n"
        f"**Segment 3 — Firmy, které nedávno podobně sponzorovaly**\n"
        f"Kdo už do podobné akce dal peníze, dá je znovu. Motivace: prokázaný zájem. "
        f"Háček: „Viděl jsem, že jste podpořili [akce] — tohle na to navazuje.\""
    )


def _local_report() -> str:
    a = st.session_state.answers
    offer = a.get("offer", "vaše nabídka")
    target = a.get("target", "vaše cílová skupina")
    return f"""**🎯 Cílové segmenty**
Na základě '{offer}' a cílovky '{target}' miřte na: (1) značky se stejným publikem, (2) lokální firmy hledající PR, (3) firmy s nedávným sponzoringem, (4) dodavatele vašeho oboru, (5) firmy s novým produktem k uvedení.
U každé si zjisti 1 konkrétní věc (nedávná kampaň, nový produkt, výročí).

**✉️ E-mailová sekvence**
Krok 1 (den 0) — Předmět: „Krátký návrh partnerství pro [firma]"
Dobrý den, sleduji [konkrétní věc o firmě]. Připravuji {offer} a vidím konkrétní překryv s vaším publikem. Nechci dlouhý e-mail — mám 10 minut tento týden ukázat, jak by to fungovalo. Dává smysl se spojit?

Krok 2 (den 3) — Předmět: „Ještě k tomu partnerství"
Dobrý den, jen krátce navazuji. Připravil jsem konkrétní čísla dosahu pro [firma]. Stačí říct a pošlu je, nebo si je projdeme na 10minutovém hovoru.

Krok 3 (den 7) — Předmět: „Poslední zpráva k [akce]"
Dobrý den, nechci obtěžovat. Pokud teď není vhodná chvíle, dám vědět příště. Kdyby vás to zajímalo, jsem k dispozici tento i příští týden.

**💬 LinkedIn varianta**
Dobrý den, pracuji na {offer} a vidím u vás konkrétní překryv s naší cílovkou. Nechci sem psát pitch — dáte 10 minut tento týden?

**📋 Checklist doručitelnosti**
Samostatná doména (ne hlavní firemní). Warm-up schránky 2–3 týdny. Max 30–50 e-mailů/den/schránka. Personalizuj první větu. Sleduj odpovědi denně. Když 3× po sobě spam/odmítnutí, zpomal.

**📊 Realistická čísla**
Konverze cold e-mailu na schůzku bývá pod 1–2 %. Při 1 % potřebuješ oslovit cca 300–500 firem na 3–5 schůzek. Nejde o počet e-mailů, ale o relevanci a follow-up.

**⚡ První krok — dnes**
Sestav seznam 20 konkrétních firem ze segmentu 1 a u každé zapiš 1 personalizační bod. Nic víc. Zítra napíšeš prvních 5."""


def render_text_step(step: Dict[str, str]) -> None:
    st.markdown(f"**{step['label']}**")
    st.write(step["prompt"])
    with st.form(f"form_{step['key']}", clear_on_submit=True):
        answer = st.text_area("Vaše odpověď", placeholder=step["placeholder"],
                              height=130, label_visibility="collapsed")
        submitted = st.form_submit_button("Pokračovat", type="primary")
    if submitted:
        if not answer.strip():
            st.warning("Napište prosím aspoň krátkou odpověď.")
            return
        save_answer(step["key"], answer)


def render_teaser_and_paywall() -> None:
    if st.session_state.teaser is None:
        with st.spinner("Analyzuji nabídku a hledám nejlepší cílové segmenty..."):
            st.session_state.teaser = generate_teaser()
    st.markdown("### Vaše 3 nejlepší cílové segmenty (zdarma)")
    st.info(st.session_state.teaser)
    st.divider()
    render_paywall()


def render_paywall() -> None:
    payment_link = get_config("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    access_code = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)
    price_text = get_config("PRICE_TEXT", DEFAULT_PRICE_TEXT)

    st.markdown("### Kompletní akviziční kit")
    st.write(
        "Kit obsahuje: 4–5 cílových segmentů přesně pro vaši nabídku, hotovou 3krokovou e-mailovou "
        "sekvenci (předměty + texty), LinkedIn variantu, checklist doručitelnosti a poctivá čísla, "
        "kolik firem oslovit pro váš cíl schůzek."
    )
    if payment_link == DEFAULT_PAYMENT_LINK:
        st.error("Platební odkaz není nastaven. Přidejte PAYMENT_LINK do Secrets.")
    else:
        st.markdown(f"[Odemknout kompletní kit za {price_text}]({payment_link})")

    if access_code:
        with st.expander("Máte přístupový kód?"):
            code = st.text_input("Přístupový kód", type="password")
            if st.button("Odemknout", type="primary"):
                if code.strip() != access_code:
                    st.error("Kód nesouhlasí.")
                    return
                st.session_state.unlocked = True
                st.rerun()
    else:
        st.info("Tip: nastavte ACCESS_CODE v Secrets pro odemykání po platbě.")


def render_final_report() -> None:
    if st.session_state.final_report is None:
        with st.spinner("Generuji váš kompletní akviziční kit..."):
            try:
                st.session_state.final_report = generate_final_report()
                st.session_state.last_error = None
            except Exception as exc:
                st.session_state.last_error = str(exc)
    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        return

    st.markdown("### Váš akviziční kit")
    st.markdown(st.session_state.final_report)

    st.divider()
    st.markdown("**Chcete akvizici na klíč?**")
    st.write(
        "Nastavíme a rozjedeme celou kampaň za vás — domény, schránky, odesílání, třídění odpovědí. "
        "Vy dostáváte jen teplé schůzky do kalendáře."
    )
    st.markdown("**Cena: 14 900 Kč včetně DPH** — napište na batko.digital.ai@gmail.com")

    st.download_button(
        "Stáhnout kit jako Markdown",
        data=st.session_state.final_report,
        file_name="akvizicni_kit.md",
        mime="text/markdown",
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    init_state()

    if st.query_params.get("demo") == "1" and not st.session_state.demo_loaded:
        load_demo_case()

    st.title(APP_TITLE)
    st.caption("Kompletní B2B akviziční kit na míru vaší nabídce — segmenty, e-mailová sekvence a poctivá čísla za 2 minuty.")

    col_reset, col_demo = st.columns(2)
    with col_reset:
        if st.button("Začít znovu", use_container_width=True):
            reset_app()
    with col_demo:
        if st.button("Zobrazit demo", type="primary", use_container_width=True):
            load_demo_case()
            st.rerun()

    render_history()

    if st.session_state.unlocked:
        render_final_report()
    elif st.session_state.step_index >= len(STEPS):
        render_teaser_and_paywall()
    else:
        render_text_step(STEPS[st.session_state.step_index])


if __name__ == "__main__":
    main()
