import os
from typing import Dict, List, Optional

import streamlit as st
from openai import OpenAI


APP_TITLE = "Autonomous Business Blueprint"
DEFAULT_ACCESS_CODE = ""
DEFAULT_PAYMENT_LINK = "https://buy.stripe.com/your-payment-link"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"
DEFAULT_PRICE_TEXT = "990 Kč včetně DPH"

DEMO_ANSWERS = {
    "industry": "E-shop s módou, 3 zaměstnanci, obrat 2 mil. Kč ročně",
    "time_drain": "Odpovídání na e-maily zákazníků ohledně reklamací a vrácení zboží",
}


def get_config(name: str, default: Optional[str] = None) -> Optional[str]:
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def get_bool_config(name: str, default: str = "false") -> bool:
    value = get_config(name, default)
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


STEPS: List[Dict[str, str]] = [
    {
        "key": "industry",
        "label": "Krok 1 ze 2",
        "prompt": "Popište svůj obor a velikost firmy (počet lidí, přibližný obrat nebo fáze).",
        "placeholder": "Např.: Účetní kancelář, 5 zaměstnanců, 150 klientů. Nebo: E-shop s elektronikou, solo podnikatel.",
    },
    {
        "key": "time_drain",
        "label": "Krok 2 ze 2",
        "prompt": "Co vám osobně žere nejvíce času každý týden? Napište jednu konkrétní rutinní činnost.",
        "placeholder": "Např.: Odpovídání na dotazy zákazníků. Nebo: Tvorba reportů pro klienty. Nebo: Schvalování faktur.",
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


def get_openai_client() -> Optional[OpenAI]:
    api_key = get_config("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def build_teaser_prompt() -> str:
    answers = st.session_state.answers
    return (
        "Jsi elitní byznys analytik zaměřený na automatizaci přes AI agenty.\n"
        f"Obor firmy: {answers.get('industry', '')}\n"
        f"Největší žrout času: {answers.get('time_drain', '')}\n\n"
        "Napiš brutálně úderný teaser přesně ve 3 větách v češtině s diakritikou:\n"
        "1. věta: Šokující uvědomění, jak tato ruční práce omezuje jeho růst.\n"
        "2. věta: Představení 1 konkrétního autonomního AI agenta (dej mu jméno, "
        "např. Support Sarah nebo Sales Sam), který tuto práci zvládá 24/7.\n"
        "3. věta: Krátký příklad, jak tento agent vyřeší žrout času rychleji a bez emocí.\n"
        "Pouze tyto 3 věty. Žádný nadpis, žádný další text."
    )


def build_blueprint_prompt() -> str:
    answers = st.session_state.answers
    return (
        "Jsi špičkový AI architekt. Uživatel chce postavit autonomní firmu, "
        "kde většinu exekutivy zastane 5 specializovaných AI agentů propojených "
        "přes nástroje jako n8n nebo Make.\n"
        f"Obor firmy: {answers.get('industry', '')}\n"
        f"Největší žrout času majitele: {answers.get('time_drain', '')}\n\n"
        "Aplikuj metodu z případové studie podnikatele, který snížil pracovní čas "
        "z 60 na 18 hodin týdně a zvýšil obrat o 40 %. "
        "Vygeneruj strukturovaný taktický plán v češtině s diakritikou. "
        "Pouze tvrdá architektura, nula omáčky:\n\n"
        "**1. Support Agent (Zákaznická podpora)**\n"
        "Jak přesně zkrátí dobu odpovědi pod 5 minut v tomto oboru. "
        "1 konkrétní kompetence a 1 tvrdý limit (co musí vždy řešit člověk).\n\n"
        "**2. Marketing Agent (Obsah a sítě)**\n"
        "Jakou analytiku sleduje a jaký obsah generuje pro maximální dosah.\n\n"
        "**3. Sales Agent (Prodej a leads)**\n"
        "Přesný spouštěč (trigger), po kterém agent automaticky osloví zákazníka "
        "a dovede ho k prodeji.\n\n"
        "**4. Data/Ops Agent (Analytika a operativa)**\n"
        "Jaké metriky reportuje majiteli každý den a v jakém formátu.\n\n"
        "**5. Zlaté pravidlo**\n"
        "Vypiš 3 konkrétní věci (strategie, vztahy, etika), které musí vždy "
        "zůstat v rukou lidského majitele, aby firma nezkrachovala.\n\n"
        "**Doporučený první krok (do 48 hodin)**\n"
        "Jeden konkrétní agent, kterého nasadit jako první, a proč právě on.\n\n"
        "Tón: direktivní, jasný, exekutivní. Striktně česky s diakritikou."
    )


def generate_teaser() -> str:
    client = get_openai_client()
    if client is None:
        return _local_teaser()
    try:
        resp = client.chat.completions.create(
            model=get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            temperature=0.4,
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
        raise RuntimeError("Chybí OPENAI_API_KEY v Streamlit Secrets.")
    try:
        resp = client.chat.completions.create(
            model=get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            temperature=0.3,
            messages=[{"role": "user", "content": build_blueprint_prompt()}],
        )
        return resp.choices[0].message.content or _local_report()
    except Exception:
        if get_bool_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK):
            return _local_report()
        raise


def _local_teaser() -> str:
    answers = st.session_state.answers
    drain = answers.get("time_drain", "rutinní práce")
    return (
        f"Každou hodinu strávenou nad '{drain}' vás stojí čas, "
        "který mohl jít do strategie a růstu firmy. "
        "Váš Support Agent dokáže tuto práci zvládat 24 hodin denně, "
        "7 dní v týdnu, s dobou odpovědi pod 5 minut. "
        "Zatímco vy spíte, agent třídí, odpovídá a eskaluje jen to, "
        "co skutečně vyžaduje váš zásah."
    )


def _local_report() -> str:
    answers = st.session_state.answers
    industry = answers.get("industry", "váš obor")
    drain = answers.get("time_drain", "rutinní práce")
    return f"""**1. Support Agent (Zákaznická podpora)**
Kompetence: Automatické odpovědi na běžné dotazy v oboru {industry} do 5 minut.
Limit: Reklamace nad 5 000 Kč a právní záležitosti vždy řeší člověk.

**2. Marketing Agent (Obsah a sítě)**
Sleduje engagement a denní analytics. Generuje 3 příspěvky týdně přizpůsobené oboru.

**3. Sales Agent (Prodej a leads)**
Spouštěč: Nová poptávka nebo přidání do košíku bez dokončení. Agent osloví do 15 minut.

**4. Data/Ops Agent (Analytika a operativa)**
Denní report v 7:00: tržby, nové leady, nevyřízené tickety, cash flow odhad.

**5. Zlaté pravidlo**
V rukou majitele vždy zůstává: firemní strategie a směřování, klíčové vztahy s partnery a klienty, etická rozhodnutí a krizové situace.

**Doporučený první krok (do 48 hodin)**
Nasaďte Support Agenta — řeší váš největší žrout času ({drain}) a efekt je viditelný okamžitě."""


def render_text_step(step: Dict[str, str]) -> None:
    st.markdown(f"**{step['label']}**")
    st.write(step["prompt"])

    with st.form(f"form_{step['key']}", clear_on_submit=True):
        answer = st.text_area(
            "Vaše odpověď",
            placeholder=step["placeholder"],
            height=130,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Pokračovat", type="primary")

    if submitted:
        if not answer.strip():
            st.warning("Napište prosím aspoň krátkou odpověď.")
            return
        save_answer(step["key"], answer)


def render_teaser_and_paywall() -> None:
    if st.session_state.teaser is None:
        with st.spinner("Analyzuji vaši situaci..."):
            st.session_state.teaser = generate_teaser()

    st.markdown("### Váš bezplatný přehled")
    st.info(st.session_state.teaser)

    st.divider()
    render_paywall()


def render_paywall() -> None:
    payment_link = get_config("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    access_code = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)
    price_text = get_config("PRICE_TEXT", DEFAULT_PRICE_TEXT)

    st.markdown("### Kompletní Autonomous Business Blueprint")
    st.write(
        "Kompletní plán obsahuje architekturu 5 AI agentů přesně pro váš obor, "
        "spouštěče, limity, doporučené nástroje a první krok nasazení do 48 hodin."
    )

    if payment_link == DEFAULT_PAYMENT_LINK:
        st.error("Platební odkaz není nastaven. Přidejte PAYMENT_LINK do Streamlit Secrets.")
    else:
        st.markdown(f"[Odemknout Blueprint za {price_text}]({payment_link})")

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
        st.error("ACCESS_CODE není nastaven v Streamlit Secrets.")


def render_final_report() -> None:
    if st.session_state.final_report is None:
        with st.spinner("Generuji váš Blueprint..."):
            try:
                st.session_state.final_report = generate_final_report()
                st.session_state.last_error = None
            except Exception as exc:
                st.session_state.last_error = str(exc)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        return

    st.markdown("### Váš Autonomous Business Blueprint")
    st.markdown(st.session_state.final_report)

    st.divider()
    st.markdown("**Chcete agenta nasadit na klíč?**")
    st.write(
        "Propojíme vašeho nejdůležitějšího agenta s e-mailem a CRM systémem — "
        "bez toho, abyste museli řešit technické nastavení."
    )
    st.markdown("**Cena: 9 900 Kč včetně DPH** — napište na batko.digital.ai@gmail.com")

    st.download_button(
        "Stáhnout Blueprint jako Markdown",
        data=st.session_state.final_report,
        file_name="autonomous_business_blueprint.md",
        mime="text/markdown",
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    init_state()

    if st.query_params.get("demo") == "1" and not st.session_state.demo_loaded:
        load_demo_case()

    st.title(APP_TITLE)
    st.caption("Plán na firmu řízenou 5 AI agenty — vygenerovaný za 3 minuty přesně pro váš obor.")

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
