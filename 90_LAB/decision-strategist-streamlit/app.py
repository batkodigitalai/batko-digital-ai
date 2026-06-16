import os
from typing import Dict, List, Optional

import streamlit as st
from openai import OpenAI


APP_TITLE = "Decision Strategist"
DEFAULT_ACCESS_CODE = ""
DEFAULT_PAYMENT_LINK = "https://buy.stripe.com/your-payment-link"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"

DEMO_ANSWERS = {
    "commitment": "Online kurz pro podnikatele, ve kterem jsem 18 mesicu.",
    "changed": "Posledni tri mesice neprichazeji nove prodeje a zacina mi byt jasne, ze me to brzdi.",
    "sunk_costs": "Zhruba 220 hodin prace, 3 500 EUR za nastroje a reklamu, ego a strach priznat si omyl.",
    "live_signals": "Mailing list obcas odpovida a par lidi ma zajem o konzultaci, ale kurz samotny se neprodava.",
    "continuing_cost": "Bere mi to vecery, blokuje B2B sluzbu a odklada rozhodnuti, ktere uz stejne tusim.",
    "make_it_yes": "Musel by se z toho stat maly B2B workshop s jasnou nabidkou, cenou a prodejem do 30 dni.",
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
            "Pojmenujte jeden zavazek, u ktereho si nejste jisty. Muze to byt projekt, "
            "byznys, studium, vztah k praci nebo dlouhodoby plan. Jak dlouho v nem jste?"
        ),
        "placeholder": "Napriklad: 18 mesicu rozjizdim online kurz, investoval jsem do nej...",
    },
    {
        "key": "changed",
        "label": "Krok 2",
        "prompt": "Co se zmenilo? Proc to resite prave ted, a ne pred pul rokem?",
        "placeholder": "Co vas donutilo se na to podivat znovu?",
    },
    {
        "key": "sunk_costs",
        "label": "Krok 3",
        "prompt": (
            "Vycislete utopene naklady: cas, penize, ego, reputaci, energii. "
            "Neposuzujte je, jen je co nejkonkretneji pojmenujte."
        ),
        "placeholder": "Napriklad: 220 hodin, 3 500 EUR, strach priznat si omyl...",
    },
    {
        "key": "live_signals",
        "label": "Krok 4",
        "prompt": (
            "Jake realne signaly ukazuji, ze na projektu neco funguje prave ted? "
            "Ignorujte minulost, zajima nas soucasnost."
        ),
        "placeholder": "Zakaznici, prijmy, tah, energie, data, konkretni poptavka...",
    },
    {
        "key": "continuing_cost",
        "label": "Krok 5",
        "prompt": (
            "Jaka je budouci cena za pokracovani? Zahrnte energii, usle prilezitosti "
            "a veci, ktere tento zavazek blokuje."
        ),
        "placeholder": "Co vas to bude stat behem dalsich 3 az 6 mesicu?",
    },
    {
        "key": "make_it_yes",
        "label": "Krok 7",
        "prompt": (
            "Co by se muselo zmenit ve strukture, formatu, rozsahu, lidech nebo case, "
            "aby odpoved byla jasne Ano?"
        ),
        "placeholder": "Jake podminky by z toho udelaly zdrave rozhodnuti?",
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

    with st.expander("Dosavadni odpovedi", expanded=False):
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
    commitment = answers.get("commitment", "Zavazek nebyl pojmenovan.")
    sunk_costs = answers.get("sunk_costs", "Utopene naklady nebyly vycisleny.")
    live_signals = answers.get("live_signals", "Nejsou uvedene jasne zive signaly.")
    continuing_cost = answers.get("continuing_cost", "Budouci cena nebyla popsana.")
    make_it_yes = answers.get("make_it_yes", "Neni popsano, co by z toho udelalo jasne Ano.")

    if from_scratch == "ANO":
        verdict = "Recommit"
        verdict_text = (
            "Znovu se zavazat, ale jen s tvrdym deadlinem 30 dni a jednim meritelnym "
            "dukazem, ze projekt ma tah."
        )
        first_move = "Do 48 hodin si nastavte 30denni checkpoint a jednu metriku, podle ktere rozhodnete."
    elif len(live_signals.strip()) > 40 and len(make_it_yes.strip()) > 40:
        verdict = "Restructure"
        verdict_text = (
            "Restrukturalizovat presne podle podminky, kterou jste popsali. Pokracovani "
            "ve stare podobe neni schvalene."
        )
        first_move = "Do 48 hodin prepisete projekt do nove mensi varianty a zrusite vse, co do ni nepatri."
    else:
        verdict = "Cut"
        verdict_text = (
            "Ukoncit. Soucasna podoba neprosla testem od nuly a minulost neni argument "
            "pro dalsi investici."
        )
        first_move = "Do 48 hodin napiste jednu zpravu nebo rozhodnuti, ktere projekt formalne ukonci."

    return f"""**Závazek (The Commitment):** {commitment}

**Utopené náklady stranou (Sunk Cost, Set Aside):** {sunk_costs}. Tyto naklady jsou pryc a nejsou relevantni pro dalsi rozhodovani.

**Co je živé vs. co jen dobíhá (What's Live vs. Fading):**
Živé:
- {live_signals}

Dobíhá:
- Setrvacnost, ego a potreba ospravedlnit minule investice nejsou dukaz, ze ma projekt pokracovat.

**Cena pokračování (The Cost of Continuing):** {continuing_cost}

**Test od nuly (The From-Scratch Test):** Odpoved: {from_scratch}. To je hlavni signal, jestli byste projekt zvolili i bez historie.

**Verdikt (The Verdict):** {verdict}. {verdict_text}

**Emoční kontrola (The Emotional Check):** Pravdepodobne je pritomna vina, strach z omylu nebo neochota zavrit neco, co uz stalo cas a penize. Verdikt temto emocim odolava, protoze se opira o budoucnost, ne o minulost.

**První tah v dalších 48 hodinách (First Move, Next 48 Hours):** {first_move}
"""


def generate_final_report() -> str:
    client = get_openai_client()
    if client is None:
        if get_bool_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK):
            return generate_local_report()
        raise RuntimeError(
            "Chybi OPENAI_API_KEY. Pridejte ho do Streamlit secrets nebo jako environment variable."
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
        st.info("Tyto naklady jsou pryc a nebudou se pocitat do dalsiho rozhodovani.")
        if st.button("Potvrzuji, nebudu je pocitat do dalsiho rozhodovani", type="primary"):
            st.session_state.sunk_cost_acknowledged = True
            st.rerun()
        return

    if idx < 5:
        render_text_step(STEPS[idx])
        return

    if idx == 5 and st.session_state.from_scratch_answer is None:
        st.markdown("**Krok 6**")
        st.write(
            "Kdybyste dnes nemel zadnou historii v tomto projektu a zadne utracene penize, "
            "zacal byste s nim dnes znovu v jeho soucasne podobe?"
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
            "Vase odpoved",
            placeholder=step["placeholder"],
            height=150,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Pokracovat", type="primary")

    if submitted:
        if not answer.strip():
            st.warning("Napiste prosim aspon kratkou odpoved.")
            return
        save_answer(step["key"], answer)


def render_paywall() -> None:
    payment_link = get_config("PAYMENT_LINK", DEFAULT_PAYMENT_LINK)
    access_code = get_config("ACCESS_CODE", DEFAULT_ACCESS_CODE)

    st.markdown("**Strategicka analyza**")
    if not access_code:
        st.error("Pristupovy kod neni nastaveny. Pridejte ACCESS_CODE do Streamlit Secrets.")
        return

    st.write(
        "Vase data jsou pripravena k finalni strategicke analyze. Pro zobrazeni tvrdeho "
        "verdiktu a akcniho planu zadejte pristupovy kod."
    )
    st.markdown(f"[Koupit přístupový kód za 199 Kč včetně DPH]({payment_link})")

    code = st.text_input("Pristupovy kod", type="password")
    if st.button("Odemknout verdikt", type="primary"):
        if code.strip() != access_code:
            st.error("Pristupovy kod nesouhlasi.")
            return
        st.session_state.unlocked = True
        st.rerun()


def render_final_report() -> None:
    if st.session_state.final_report is None:
        with st.spinner("Pripravuji tvrdy verdikt..."):
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
    st.caption("Klidny test zavazku, ve kterych muze byt schovana past utopenych nakladu.")

    col_reset, col_demo = st.columns(2)
    with col_reset:
        if st.button("Zacit znovu", use_container_width=True):
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
