import os
from typing import Dict, List, Optional

import streamlit as st
from openai import OpenAI


APP_TITLE = "AI Side Hustle Blueprint"
DEFAULT_ACCESS_CODE = ""
DEFAULT_PAYMENT_LINK = "https://buy.stripe.com/your-payment-link"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"
DEFAULT_PRICE_TEXT = "990 Kč včetně DPH"

DEMO_ANSWERS = {
    "skills": "Pracuji jako účetní, rozumím Excelu a daním, umím vysvětlovat složité věci jednoduše",
    "time_goal": "Mám 5-8 hodin týdně navíc a chci vydělat 5 000 - 10 000 Kč měsíčnę pasivnę",
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
        "key": "skills",
        "label": "Krok 1 ze 2",
        "prompt": "Co umíte nebo znáte lépe než většina lidí? Jaké jsou vaše pracovní zkušenosti, koníD�ky nebo oblasti, kde se lidé na vás obracejí o radu?",
        "placeholder": "Např.: Pracuji v IT, umím Python a řeším bezpečnost sítí. Nebo: Jsem trenér fitnessu a vím jak zhubnout po 40. Nebo: 10 let v marketingu, vím jak psát texty, které prodávají.",
    },
    {
        "key": "time_goal",
        "label": "Krok 2 ze 2",
        "prompt": "Kolik hodin týdně můžete věnovat vedlejšímu projektu a jaký měsíční příjem byste chtěli dosáhnout do 3 měsíců?",
        "placeholder": "Např.: Mám 3-5 hodin týdně a chci 3 000-5 000 Kč měsíčnĦ navíc. Nebo: 10+ hodin, cíl je 20 000 Kč za 3 měsíce.",
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
        "Jsi expert na monetizaci znalostí a AI-powered side hustles.\n"
        f"Dovednosti a zkušenosti uživatele: {answers.get('skills', '')}\n"
        f"Dostupný čas a cíl příjmu: {answers.get('time_goal', '')}\n\n"
        "Na základě tohoto profilu vygeneruj přesně 3 konkrétní nápady na digitální produkt nebo službu, "
        "které může tento člověk vytvořit s pomocí AI a začít prodávat do 30 dní. "
        "Pro každý nápad napiš:\n"
        "- Název produktu (stručný, marketingový)\n"
        "- Jedna věta: co to je a komu to pomůže\n"
        "- Odhadovaná cena prodeje\n"
        "- Čas potřebný k vytvoření (v hodinách)\n\n"
        "Formát: tři oddíly nadepsané **Nápad 1**, **Nápad 2**, **Nápad 3**. "
        "Buď konkrétní, žádné obecnosti. Pouze česky s diakritikou."
    )


def build_blueprint_prompt() -> str:
    answers = st.session_state.answers
    return (
        "Jsi špičkový kouč na budování AI-powered side hustles a digitálních produktů.\n"
        f"Dovednosti a zkušenosti uživatele: {answers.get('skills', '')}\n"
        f"Dostupný čas a cíl příjmu: {answers.get('time_goal', '')}\n\n"
        "Vygeneruj kompletní 90denní AI Side Hustle Blueprint v češtině s diakritikou. "
        "Žádná vata, jen konkrétní exekutivní plán:\n\n"
        "**🎯 Váš nejlepší digitální produkt**\n"
        "Pojmenuj jeden konkrétní produkt (mini-kurz PDF, šablona, checklist, mini-ebook nebo mini-nástroj), "
        "přesně popsaný: název, obsah (5-10 bodů), cílový zákazník, cena. "
        "Vysvětli, proč právě tento produkt sedí na jejich profil.\n\n"
        "**🛠️ Jak ho vytvořit (Týden 1-2)**\n"
        "Konkrétní postup krok za krokem s pomocí AI nástrojů (ChatGPT, Claude). "
        "Odhadovaný čas tvorby v hodinách. Co přesnę napsat do promptu pro AI.\n\n"
        "**💰 Kde a jak prodávat (Týden 3-4)**\n"
        "Konkrétní platforma pro prodej (Gumroad, Payhip, nebo jiná). "
        "3 konkrétní online komunity nebo subreddity/skupiny, kde je cílový zákazník. "
        "Přesná šablona prvního propagačního komentáře/přístěvku.\n\n"
        "**📈 Škálování (Měsíc 2-3)**\n"
        "Jak zvýšit cenu produktu (co přidat jako bonus). "
        "Jak z jednoho produktu udělat sérii nebo bundle. "
        "Realistický odhad měsíčního příjmu po 90 dnech při konzistentní práci.\n\n"
        "**⚡ První krok — dnes večer**\n"
        "Přesně jedna akce, kterou může uživatel udělat v příštích 2 hodinách, "
        "aby se posunul kupředu. Buďte brutálně konkrétní.\n\n"
        "Tón: přímý, motivující, bez prázdných frází. Striktně česky s diakritikou."
    )


def generate_teaser() -> str:
    client = get_openai_client()
    if client is None:
        return _local_teaser()
    try:
        resp = client.chat.completions.create(
            model=get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
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
        raise RuntimeError("Chybí OPENAI_API_KEY v Streamlit Secrets.")
    try:
        resp = client.chat.completions.create(
            model=get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            temperature=0.4,
            messages=[{"role": "user", "content": build_blueprint_prompt()}],
        )
        return resp.choices[0].message.content or _local_report()
    except Exception:
        if get_bool_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK):
            return _local_report()
        raise


def _local_teaser() -> str:
    answers = st.session_state.answers
    skills = answers.get("skills", "vaše zkušenosti")
    return (
        f"**Nápad 1 — Mini-průvodce PDF**\n"
        f"Shrňte svou odbornost v 10-15 stránkovém PDF, které řeší jeden konkrétní problém. "
        f"Cena: 200-500 Kč. Čas tvorby: 3-5 hodin s pomocí AI.\n\n"
        f"**Nápad 2 — Šablona nebo checklist**\n"
        f"Z oblasti '{skills}' vytvořte hotový pracovní nástroj, "
        f"který lidem ušetří hodiny práce. Cena: 150-300 Kč. Čas tvorby: 1-2 hodiny.\n\n"
        f"**Nápad 3 — Poradenský mini-balíček**\n"
        f"Nabídněte 60minutovou konzultaci přes Zoom + follow-up dokument. "
        f"Cena: 990-1 990 Kč za session. Žoádný čas na tvorbu — jen váš čas."
    )


def _local_report() -> str:
    answers = st.session_state.answers
    skills = answers.get("skills", "vaše odbornost")
    time_goal = answers.get("time_goal", "vāš cíl")
    return f"""**🎯 Váš nejlepší digitální produkt**
Na základě profilu '{skills}' doporučuji: **Mini-průvodce PDF** — 12-15 stránkový dokument řešící jeden konkrétní bolestivý problém ve vašem oboru.
Cílový zákazník: začátečníci nebo kolegové, kteří potřebují zkráceninu vaši zkušenosti.
Cena: 390-590 Kč. Prodejní platforma: Gumroad (bezplatná).

**🛠️ Jak ho vytvořit (Týden 1-2)**
1. Otevřete Claude nebo ChatGPT a napište: "Pomoz mi vytvořit strukturu PDF průvodce na téma [vaše téma] pro [cílový zákazník]. Obsah: 10 klíčových bodů."
2. Každý bod rozepište do 1-2 odstavců vlastními slovy — AI je jen startovní bod.
3. Export z Google Docs do PDF. Žoádný design nutnî.
Odhadovaný čas: 4-6 hodin celkem.

**💰 Kde a jak prodávat (Týden 3-4)**
Platforma: Gumroad.com — hastavení za 20 minut, bez měsíčního poplatku.
Komunity: Hledejte Facebook skupiny nebo LinkedIn skupiny s '{skills}'.
Šablona přístěvku: "Bojuji s [problém] roky. Napsal jsem krátkù prõvodce, jak jsem to vyqeil. Kdo chce, dám link."

**📈 Škálování (Měsíc 2-3)**
Po prvních 10 prodeji přidejte bonus (checklist nebo šablonu) a zvyšte cenu o 200 Kč.
Bundle: 3 PDF za cenu 2. Realistický odhad po 90 dnech: {time_goal} — při 3-5 prodeji denně.

**⚑ První krok — dnes večer**
Otevřete nový Google Doc, napište nadpis "10 věcí, které jsem se naučil za [X let] v  [oboru]" a vyplňte alespoň 3 body. Tím spustíte proces. Zbytek udělá AI."""


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
            st.warning("Napište prosím aspoň krátkou odpovēď.")
            return
        save_answer(step["key"], answer)


def render_teaser_and_paywall() -> None:
    if st.session_state.teaser is None:
        with st.spinner("Analyzuji vás profil a hledám nejlepší příležitosti..."):
            st.session_state.teaser = generate_teaser()

    st.markdown("### Vaše 3 AI side hustle příležitosti (zdarma)")
    st.info(st.session_state.teaser)

    st.divider()
    render_paywall()


def render_paywall() -> None:
    payment_link = get_config("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    access_code = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)
    price_text = get_config("PRICE_TEXT", DEFAULT_PRICE_TEXT)

    st.markdown("### Kompletní AI Side Hustle Blueprint")
    st.write(
        "Kompletní plán obsahuje: konkrétní digitální produkt přesnę pro vaše profil, "
        "postup tvorby krok za krokem s AI, kde a jak prodávat, šablony obsahu "
        "a realistický plán na 90 dní k prvnímu pasivnímu příjmu."
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
        with st.spinner("Generuji vás osobní Blueprint..."):
            try:
                st.session_state.final_report = generate_final_report()
                st.session_state.last_error = None
            except Exception as exc:
                st.session_state.last_error = str(exc)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        return

    st.markdown("### Vás AI Side Hustle Blueprint")
    st.markdown(st.session_state.final_report)

    st.divider()
    st.markdown("**Chcete to celé nastavil za vás?**")
    st.write(
        "Pomůžeme vám vytvořit první digitální produkt od A do Z — "
        "od nápadu přes tvorbu s AI až po spuštění prodeje. Bez technickùch znalostí."
    )
    st.markdown("**Cena: 4 900 Kč včetnę DPH** — napište na batko.digital.ai@gmail.com")

    st.download_button(
        "Stáhnout Blueprint jako Markdown",
        data=st.session_state.final_report,
        file_name="ai_side_hustle_blueprint.md",
        mime="text/markdown",
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    init_state()

    if st.query_params.get("demo") == "1" and not st.session_state.demo_loaded:
        load_demo_case()

    st.title(APP_TITLE)
    st.caption("Personalizovaný plán vedlejšího příjmu přes AI — vygenerovaný za 2 minuty přesně pro vaše dovednosti.")

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
