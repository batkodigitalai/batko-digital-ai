import os
from typing import Dict, List, Optional

import streamlit as st
from openai import OpenAI


APP_TITLE = "Strategický verdikt"
DEFAULT_ACCESS_CODE = ""
DEFAULT_PAYMENT_LINK = "https://buy.stripe.com/your-payment-link"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"

DEMO_ANSWERS = {
    "commitment": "Online kurz pro podnikatele, ve kterém jsem 18 měsíců.",
    "changed": "Poslední tři měsíce nepřicházejí nové prodeje a začíná mi být jasné, že mě to brzdí.",
    "sunk_costs": "Zhruba 220 hodin práce, 85 000 Kč za nástroje a reklamu, ego a strach přiznat si omyl.",
    "live_signals": "Mailing list občas odpovídá a pár lidí má zájem o konzultaci, ale kurz samotný se neprodává.",
    "continuing_cost": "Bere mi to večery, blokuje B2B službu a odkládá rozhodnutí, které už stejně tuším.",
    "make_it_yes": "Musel by se z toho stát malý B2B workshop s jasnou nabídkou, cenou a prodejem do 30 dnů.",
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
        "key": "commitment",
        "label": "Krok 1",
        "prompt": (
            "Pojmenujte jeden závazek, u kterého si nejste jistý. Může to být projekt, "
            "byznys, studium, vztah k práci nebo dlouhodobý plán. Jak dlouho v něm jste?"
        ),
        "placeholder": "Například: 18 měsíců rozjíždím online kurz, investoval jsem do něj...",
    },
    {
        "key": "changed",
        "label": "Krok 2",
        "prompt": "Co se změnilo? Proč to řešíte právě teď, a ne před půl rokem?",
        "placeholder": "Co vás donutilo se na to podívat znovu?",
    },
    {
        "key": "sunk_costs",
        "label": "Krok 3",
        "prompt": (
            "Vyčíslete utopené náklady: čas, peníze, ego, reputaci, energii. "
            "Neposuzujte je, jen je co nejkonkrétněji pojmenujte."
        ),
        "placeholder": "Například: 220 hodin, 85 000 Kč, strach přiznat si omyl...",
    },
    {
        "key": "live_signals",
        "label": "Krok 4",
        "prompt": (
            "Jaké reálné signály ukazují, že na projektu něco funguje právě teď? "
            "Ignorujte minulost, zajímá nás současnost."
        ),
        "placeholder": "Zákazníci, příjmy, tah, energie, data, konkrétní poptávka...",
    },
    {
        "key": "continuing_cost",
        "label": "Krok 5",
        "prompt": (
            "Jaká je budoucí cena za pokračování? Zahrňte energii, ušlé příležitosti "
            "a věci, které tento závazek blokuje."
        ),
        "placeholder": "Co vás to bude stát během dalších 3 až 6 měsíců?",
    },
    {
        "key": "make_it_yes",
        "label": "Krok 7",
        "prompt": (
            "Co by se muselo změnit ve struktuře, formátu, rozsahu, lidech nebo čase, "
            "aby odpověď byla jasné Ano?"
        ),
        "placeholder": "Jaké podmínky by z toho udělaly zdravé rozhodnutí?",
    },
]


def init_state() -> None:
    defaults = {
        "step_index": 0,
        "answers": {},
        "sunk_cost_acknowledged": False,
        "from_scratch_answer": None,
        "unlocked": False,
        "final_report": None,
        "last_error": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def render_history() -> None:
    answers = st.session_state.answers
    if not answers and st.session_state.from_scratch_answer is None:
        return

    with st.expander("Dosavadní odpovědi", expanded=False):
        for step in STEPS[:5]:
            answer = answers.get(step["key"])
            if answer:
                st.markdown(f"**{step['label']}**")
                st.write(answer)

        if st.session_state.from_scratch_answer:
            st.markdown("**Krok 6 - Test od nuly**")
            st.write(st.session_state.from_scratch_answer)

        final_answer = answers.get("make_it_yes")
        if final_answer:
            st.markdown("**Krok 7**")
            st.write(final_answer)


def save_answer(step_key: str, answer: str) -> None:
    st.session_state.answers[step_key] = answer.strip()
    st.session_state.step_index += 1
    st.rerun()


def reset_app() -> None:
    for key in [
        "step_index",
        "answers",
        "sunk_cost_acknowledged",
        "from_scratch_answer",
        "unlocked",
        "final_report",
        "last_error",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


def load_demo_case() -> None:
    st.session_state.answers = DEMO_ANSWERS.copy()
    st.session_state.step_index = 7
    st.session_state.sunk_cost_acknowledged = True
    st.session_state.from_scratch_answer = "NE"
    st.session_state.unlocked = True
    st.session_state.final_report = None
    st.session_state.last_error = None
    st.session_state.demo_loaded = True


def build_case_summary() -> str:
    answers = st.session_state.answers
    lines = [
        f"Commitment and duration: {answers.get('commitment', '')}",
        f"What changed: {answers.get('changed', '')}",
        f"Sunk costs: {answers.get('sunk_costs', '')}",
        f"Live signals: {answers.get('live_signals', '')}",
        f"Cost of continuing: {answers.get('continuing_cost', '')}",
        f"From-scratch test answer: {st.session_state.from_scratch_answer or ''}",
        f"What would make it a clear yes: {answers.get('make_it_yes', '')}",
    ]
    return "\n".join(lines)


def get_openai_client() -> Optional[OpenAI]:
    api_key = get_config("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def generate_local_report() -> str:
    answers = st.session_state.answers
    from_scratch = st.session_state.from_scratch_answer or "NEZODPOVEZENO"
    commitment = answers.get("commitment", "Závazek nebyl pojmenován.")
    sunk_costs = answers.get("sunk_costs", "Utopené náklady nebyly vyčísleny.")
    live_signals = answers.get("live_signals", "Nejsou uvedené jasné živé signály.")
    continuing_cost = answers.get("continuing_cost", "Budoucí cena nebyla popsána.")
    make_it_yes = answers.get("make_it_yes", "Není popsáno, co by z toho udělalo jasné Ano.")

    if from_scratch == "ANO":
        verdict = "Znovu se zavázat (Recommit)"
        verdict_text = (
            "Znovu se zavázat, ale jen s tvrdým deadlinem 30 dní a jedním měřitelným "
            "důkazem, že projekt má tah."
        )
        first_move = "Do 48 hodin si nastavte 30denní kontrolní bod a jednu metriku, podle které rozhodnete."
    elif len(live_signals.strip()) > 40 and len(make_it_yes.strip()) > 40:
        verdict = "Restrukturalizovat (Restructure)"
        verdict_text = (
            "Restrukturalizovat přesně podle podmínky, kterou jste popsali. Pokračování "
            "ve staré podobě není schválené."
        )
        first_move = "Do 48 hodin přepište projekt do nové menší varianty a zrušte vše, co do ní nepatří."
    else:
        verdict = "Ukončit (Cut)"
        verdict_text = (
            "Ukončit. Současná podoba neprošla testem od nuly a minulost není argument "
            "pro další investici."
        )
        first_move = "Do 48 hodin napište jednu zprávu nebo rozhodnutí, které projekt formálně ukončí."

    return f"""**Závazek (The Commitment):** {commitment}

**Utopené náklady stranou (Sunk Cost, Set Aside):** {sunk_costs}. Tyto náklady jsou pryč a nejsou relevantní pro další rozhodování.

**Co je živé vs. co jen dobíhá (What's Live vs. Fading):**
Živé:
- {live_signals}

Dobíhá:
- Setrvačnost, ego a potřeba ospravedlnit minulé investice nejsou důkaz, že má projekt pokračovat.

**Cena pokračování (The Cost of Continuing):** {continuing_cost}

**Test od nuly (The From-Scratch Test):** Odpověď: {from_scratch}. To je hlavní signál, jestli byste projekt zvolili i bez historie.

**Verdikt (The Verdict):** {verdict}. {verdict_text}

**Emoční kontrola (The Emotional Check):** Pravděpodobně je přítomná vina, strach z omylu nebo neochota zavřít něco, co už stálo čas a peníze. Verdikt těmto emocím odolává, protože se opírá o budoucnost, ne o minulost.

**První tah v dalších 48 hodinách (First Move, Next 48 Hours):** {first_move}
"""


def generate_final_report() -> str:
    client = get_openai_client()
    if client is None:
        if get_bool_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK):
            return generate_local_report()
        raise RuntimeError(
            "Chybí OPENAI_API_KEY. Přidejte ho do Streamlit secrets nebo jako environment variable."
        )

    system_prompt = """
You are a calm, intellectually honest Decision Strategist.
Your job is to help a person escape sunk-cost bias. Be direct, humane, and practical.

Rules:
- Do not count past money, time, ego, or reputation as reasons to continue.
- Do not allow vague compromise, corporate jargon, motivational fluff, or both-sides padding.
- The final verdict must be exactly one of these three labels: Cut, Restructure, Recommit.
- If the case is weak and the from-scratch answer is No, prefer Cut unless there is a precise viable restructuring.
- If choosing Restructure, state exactly what must change.
- If choosing Recommit, include a hard deadline and measurable proof that continuation is justified.
- Write in Czech unless the user's answers are clearly in another language.
- Section headings must be Czech first. If an English label is useful, put it only after the Czech heading in parentheses.
- Use the exact section headings below and keep the report concise.

Output structure:
**Závazek (The Commitment):** One line defining the commitment and duration.

**Utopené náklady stranou (Sunk Cost, Set Aside):** Clearly quantify spent money, time, ego/reputation where provided, and mark them irrelevant for the future decision.

**Co je živé vs. co jen dobíhá (What's Live vs. Fading):**
Živé:
- short bullet list
Dobíhá:
- short bullet list

**Cena pokračování (The Cost of Continuing):** The real future cost in energy, opportunities, and blocked alternatives.

**Test od nuly (The From-Scratch Test):** The user's Yes/No answer and what it means.

**Verdikt (The Verdict):** Exactly one of: Ukončit (Cut), Restrukturalizovat (Restructure), Znovu se zavázat (Recommit). Then give the precise meaning in one short paragraph.

**Emoční kontrola (The Emotional Check):** Name the guilt or fear present, and judge whether the verdict survives those emotions.

**První tah v dalších 48 hodinách (First Move, Next 48 Hours):** One concrete action the user must take within 48 hours.
"""

    user_prompt = f"Analyze this sunk-cost decision case:\n\n{build_case_summary()}"

    try:
        response = client.chat.completions.create(
            model=get_config("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
            temperature=0.3,
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


def render_current_step() -> None:
    idx = st.session_state.step_index

    if idx < 3:
        render_text_step(STEPS[idx])
        return

    if idx == 3 and not st.session_state.sunk_cost_acknowledged:
        st.info("Tyto náklady jsou pryč a nebudou se počítat do dalšího rozhodování.")
        if st.button("Potvrzuji, nebudu je počítat do dalšího rozhodování", type="primary"):
            st.session_state.sunk_cost_acknowledged = True
            st.rerun()
        return

    if idx < 5:
        render_text_step(STEPS[idx])
        return

    if idx == 5 and st.session_state.from_scratch_answer is None:
        st.markdown("**Krok 6**")
        st.write(
            "Kdybyste dnes neměl žádnou historii v tomto projektu a žádné utracené peníze, "
            "začal byste s ním dnes znovu v jeho současné podobě?"
        )
        col_yes, col_no = st.columns(2)
        with col_yes:
            if st.button("ANO", use_container_width=True):
                st.session_state.from_scratch_answer = "ANO"
                st.session_state.step_index += 1
                st.rerun()
        with col_no:
            if st.button("NE", use_container_width=True, type="primary"):
                st.session_state.from_scratch_answer = "NE"
                st.session_state.step_index += 1
                st.rerun()
        return

    if idx == 6:
        render_text_step(STEPS[5])
        return

    render_paywall()


def render_text_step(step: Dict[str, str]) -> None:
    st.markdown(f"**{step['label']}**")
    st.write(step["prompt"])

    with st.form(f"form_{step['key']}", clear_on_submit=True):
        answer = st.text_area(
            "Vaše odpověď",
            placeholder=step["placeholder"],
            height=150,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Pokračovat", type="primary")

    if submitted:
        if not answer.strip():
            st.warning("Napište prosím aspoň krátkou odpověď.")
            return
        save_answer(step["key"], answer)


def render_paywall() -> None:
    payment_link = get_config("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    access_code = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)

    st.markdown("**Strategická analýza**")
    if not access_code:
        st.error("Přístupový kód není nastavený. Přidejte ACCESS_CODE do Streamlit Secrets.")
        return

    st.write(
        "Vaše data jsou připravena k finální strategické analýze. Pro zobrazení tvrdého "
        "verdiktu a akčního plánu zadejte přístupový kód."
    )
    st.markdown(f"[Koupit přístupový kód za 199 Kč včetně DPH]({payment_link})")

    code = st.text_input("Přístupový kód", type="password")
    if st.button("Odemknout verdikt", type="primary"):
        if code.strip() != access_code:
            st.error("Přístupový kód nesouhlasí.")
            return
        st.session_state.unlocked = True
        st.rerun()


def render_final_report() -> None:
    if st.session_state.final_report is None:
        with st.spinner("Připravuji tvrdý verdikt..."):
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
        "Stáhnout výsledek jako Markdown",
        data=st.session_state.final_report,
        file_name="decision_strategist_verdict.md",
        mime="text/markdown",
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    init_state()

    if st.query_params.get("demo") == "1" and not st.session_state.get("demo_loaded"):
        load_demo_case()

    st.title(APP_TITLE)
    st.caption("Klidný test závazků, ve kterých může být schovaná past utopených nákladů.")

    col_reset, col_demo = st.columns(2)
    with col_reset:
        if st.button("Začít znovu", use_container_width=True):
            reset_app()
    with col_demo:
        if st.button("Vyplnit demo a ukázat verdikt", type="primary", use_container_width=True):
            load_demo_case()
            st.rerun()

    render_history()

    if st.session_state.unlocked:
        render_final_report()
    else:
        render_current_step()


if __name__ == "__main__":
    main()
