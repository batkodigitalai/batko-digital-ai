import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.error import URLError
from urllib.parse import parse_qsl, urlencode, unquote_plus, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import streamlit as st
from openai import OpenAI


APP_TITLE = "Diagnóza neprodaného auta"
APP_SUBTITLE = "Rychlý verdikt pro auto, které visí v inzerci déle, než by mělo."
DEFAULT_ACCESS_CODE = ""
DEFAULT_PAYMENT_LINK = "https://buy.stripe.com/your-payment-link"
DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"
DEFAULT_ALLOW_LOCAL_FALLBACK = "true"
DEFAULT_PRICE_TEXT = "199 Kč včetně DPH"
DEFAULT_REQUIRE_LEAD_WEBHOOK = "false"


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


def format_int(value: str) -> str:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    if not digits:
        return str(value or "").strip()
    return f"{int(digits):,}".replace(",", " ")


def append_url_params(url: str, params: Dict[str, str]) -> str:
    if not url:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update({key: value for key, value in params.items() if value})
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def make_lead_id(car: Dict[str, str]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    sauto_id = car.get("sauto_id") or "bez-id"
    return f"sauto-{sauto_id}-{timestamp}"


def load_car_from_query() -> Dict[str, str]:
    return {
        "sauto_id": first_query_value("sauto_id"),
        "model": first_query_value("model") or first_query_value("car") or "vybrané auto",
        "year": first_query_value("year"),
        "price": first_query_value("price"),
        "km": first_query_value("km"),
        "days": first_query_value("days"),
        "listed_from": first_query_value("listed_from"),
        "sauto_url": first_query_value("sauto_url") or first_query_value("url"),
        "source": first_query_value("source", "sauto"),
    }


DEMO_CAR = {
    "sauto_id": "208932162",
    "model": "Volkswagen Passat",
    "year": "2019",
    "price": "488999",
    "km": "148000",
    "days": "313",
    "listed_from": "2025-08-07",
    "sauto_url": "https://www.sauto.cz/osobni/detail/volkswagen/passat/208932162",
    "source": "sauto_vlna_012",
}

DEMO_ANSWERS = {
    "interest": "Za poslední měsíc se ozvali dva lidé, ale oba chtěli výraznou slevu a nikdo nepřijel.",
    "flexibility": "Cenu bych upravil jen mírně, ale jsem ochotný změnit text, fotky a způsob komunikace.",
    "priority": "Chci auto prodat do 30 dní, nechci ho držet další měsíce.",
}

STEPS: List[Dict[str, str]] = [
    {
        "key": "interest",
        "label": "Doplnění 1",
        "prompt": "Kolik vážných zájemců se ozvalo za posledních 30 dní a co se s nimi stalo?",
        "placeholder": "Například: 3 lidé napsali, 1 přijel, všichni tlačili cenu dolů...",
    },
    {
        "key": "flexibility",
        "label": "Doplnění 2",
        "prompt": "Co jste ochotný změnit: cenu, fotky, text inzerátu, servisní doložení, nebo způsob jednání?",
        "placeholder": "Například: cenu jen trochu, ale text a fotky klidně hned...",
    },
    {
        "key": "priority",
        "label": "Doplnění 3",
        "prompt": "Je pro vás důležitější prodat rychle, nebo držet cenu co nejvýš?",
        "placeholder": "Například: chci prodat do 14 dní / klidně počkám, ale nechci jít pod...",
    },
]


def init_state() -> None:
    car = load_car_from_query()
    defaults = {
        "car": car,
        "lead_id": make_lead_id(car),
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
    for key in [
        "car",
        "lead_id",
        "contact",
        "contact_submitted",
        "lead_saved",
        "step_index",
        "answers",
        "unlocked",
        "final_report",
        "free_preview",
        "last_error",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


def load_demo_case() -> None:
    st.session_state.car = DEMO_CAR.copy()
    st.session_state.lead_id = make_lead_id(st.session_state.car)
    st.session_state.contact = {
        "name": "Demo prodávající",
        "email": "demo@example.com",
        "phone": "+420 700 000 000",
        "consent": True,
    }
    st.session_state.contact_submitted = True
    st.session_state.lead_saved = True
    st.session_state.answers = DEMO_ANSWERS.copy()
    st.session_state.step_index = len(STEPS)
    st.session_state.unlocked = False
    st.session_state.final_report = None
    st.session_state.free_preview = None
    st.session_state.last_error = None
    st.session_state.demo_loaded = True


def car_title(car: Dict[str, str]) -> str:
    parts = [car.get("model", "").strip(), car.get("year", "").strip()]
    return " ".join(part for part in parts if part).strip() or "vybrané auto"


def render_car_context() -> None:
    car = st.session_state.car
    price = format_int(car.get("price", ""))
    km = format_int(car.get("km", ""))
    days = format_int(car.get("days", ""))

    st.markdown("**Auto z inzerátu**")
    cols = st.columns(4)
    cols[0].metric("Model", car_title(car))
    cols[1].metric("Cena", f"{price} Kč" if price else "nezadáno")
    cols[2].metric("Nájezd", f"{km} km" if km else "nezadáno")
    cols[3].metric("Dní v inzerci", days if days else "nezadáno")

    if car.get("sauto_url"):
        st.markdown(f"[Otevřít původní inzerát]({car['sauto_url']})")

    if days and int(days.replace(" ", "")) >= 60:
        st.warning(
            "Toto auto je v inzerci dlouho. To obvykle znamená problém v ceně, důvěře, "
            "prezentaci, nebo ve výběru správného typu kupce."
        )


def render_history() -> None:
    answers = st.session_state.answers
    if not answers:
        return

    with st.expander("Doplněné odpovědi", expanded=False):
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
            height=140,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Pokračovat", type="primary")

    if submitted:
        if not answer.strip():
            st.warning("Napište prosím aspoň krátkou odpověď.")
            return
        save_answer(step["key"], answer)


def build_case_summary() -> str:
    car = st.session_state.car
    answers = st.session_state.answers
    contact = st.session_state.contact
    lines = [
        f"Lead ID: {st.session_state.lead_id}",
        f"Seller name: {contact.get('name', '')}",
        f"Seller email: {contact.get('email', '')}",
        f"Seller phone: {contact.get('phone', '')}",
        f"Model: {car_title(car)}",
        f"Sauto ID: {car.get('sauto_id', '')}",
        f"Current advertised price CZK: {car.get('price', '')}",
        f"Mileage km: {car.get('km', '')}",
        f"Days listed: {car.get('days', '')}",
        f"Listed from: {car.get('listed_from', '')}",
        f"Listing URL: {car.get('sauto_url', '')}",
        f"Source: {car.get('source', '')}",
        f"Recent buyer interest: {answers.get('interest', '')}",
        f"Seller flexibility: {answers.get('flexibility', '')}",
        f"Seller priority: {answers.get('priority', '')}",
    ]
    return "\n".join(lines)


def build_lead_payload() -> Dict[str, object]:
    contact = st.session_state.contact
    car = st.session_state.car
    answers = st.session_state.answers
    car_name = car_title(car)
    answer_summary = "\n".join(
        [
            f"Lead ID: {st.session_state.lead_id}",
            f"Zájem za 30 dní: {answers.get('interest', '')}",
            f"Ochota změn: {answers.get('flexibility', '')}",
            f"Priorita: {answers.get('priority', '')}",
        ]
    )
    return {
        "formType": "Diagnoza_Neprodaneho_Auta",
        "event_type": "lead_free_preview_requested",
        "lead_id": st.session_state.lead_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "name": contact.get("name", ""),
        "email": contact.get("email", ""),
        "phone": contact.get("phone", ""),
        "telefon": contact.get("phone", ""),
        "source": car.get("source", "sauto"),
        "channel": "Streamlit diagnóza neprodaného auta",
        "car_title": car_name,
        "car_meta": (
            f"Cena: {format_int(car.get('price', ''))} Kč | "
            f"Nájezd: {format_int(car.get('km', ''))} km | "
            f"Dní v inzerci: {format_int(car.get('days', ''))}"
        ),
        "sauto_id": car.get("sauto_id", ""),
        "sauto_url": car.get("sauto_url", ""),
        "url_aukce": car.get("sauto_url", ""),
        "conversation_key": f"diagnoza-{car.get('sauto_id', st.session_state.lead_id)}",
        "button_text": "Zobrazit bezplatný předverdikt",
        "lead_task": "Zpracovat lead z diagnózy neprodaného auta a nabídnout placenou službu",
        "zprava": answer_summary,
        "poznamka": (
            f"lead_id={st.session_state.lead_id} | "
            f"sauto_id={car.get('sauto_id', '')} | "
            f"source={car.get('source', '')}"
        ),
        "contact": contact,
        "car": car,
        "answers": answers,
        "processing_status": "LEAD_PREDVERDIKT",
        "approval_required": "CEKA_NA_NAVAZANI",
        "next_action": "Zobrazit predverdikt a nabidnout placenou plnou diagnozu",
    }


def post_lead_payload(payload: Dict[str, object]) -> None:
    webhook_url = get_config("LEAD_WEBHOOK_URL", "")
    if not webhook_url:
        if get_bool_config("REQUIRE_LEAD_WEBHOOK", DEFAULT_REQUIRE_LEAD_WEBHOOK):
            raise RuntimeError("Chybí LEAD_WEBHOOK_URL pro zápis leadu.")
        return

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=8) as response:
            if response.status >= 400:
                raise RuntimeError(f"Zápis leadu selhal se stavem {response.status}.")
    except URLError as exc:
        raise RuntimeError("Zápis leadu se nepodařil. Zkuste to prosím znovu.") from exc


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
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        verify_url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=8) as response:
            result = json.loads(response.read().decode("utf-8") or "{}")
            return bool(result.get("valid"))
    except (URLError, json.JSONDecodeError):
        return False


def get_openai_client() -> Optional[OpenAI]:
    api_key = get_config("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def diagnose_primary_blocker(car: Dict[str, str], answers: Dict[str, str]) -> str:
    days = int("".join(ch for ch in car.get("days", "") if ch.isdigit()) or "0")
    interest = answers.get("interest", "").lower()
    flexibility = answers.get("flexibility", "").lower()

    if days >= 180 and ("sleva" in interest or "cenu" in interest or "levn" in interest):
        return "Nejpravděpodobnější brzda je cena vůči důvěře kupujícího."
    if days >= 90 and ("nikdo" in interest or "málo" in interest or "neozval" in interest):
        return "Nejpravděpodobnější brzda je slabá poptávka na aktuální prezentaci a cenu."
    if "fot" in flexibility or "text" in flexibility:
        return "Rychlá páka je prezentace: fotky, text, důkazy a komunikace."
    return "Nejpravděpodobnější problém je kombinace ceny, prezentace a špatně zvoleného kupce."


def generate_local_preview() -> str:
    car = st.session_state.car
    days = format_int(car.get("days", ""))
    return f"""**Rychlý předverdikt**

U auta **{car_title(car)}** za **{format_int(car.get('price', ''))} Kč** a se stářím inzerátu **{days or 'nezadáno'} dní** už nejde jen o čekání na správného kupce.

Pravděpodobný problém: **{diagnose_primary_blocker(car, st.session_state.answers)}**

Plný výstup ukáže konkrétní 7denní taktiku, co změnit v inzerátu, jak komunikovat se zájemci a kdy už držení ceny nedává obchodní smysl.
"""


def generate_local_report() -> str:
    car = st.session_state.car
    answers = st.session_state.answers
    blocker = diagnose_primary_blocker(car, answers)

    return f"""**Auto (kontext z inzerátu):** {car_title(car)}, cena {format_int(car.get('price', ''))} Kč, nájezd {format_int(car.get('km', ''))} km, v inzerci {format_int(car.get('days', ''))} dní.

**Hlavní brzda prodeje:** {blocker}

**Co to pravděpodobně znamená:** Auto nemusí být špatné. Problém je, že kupující zatím nevidí dostatečný důvod jednat rychle za aktuální cenu. Dlouhá doba v inzerci navíc sama snižuje důvěru.

**Cenová taktika na 7 dní:** Nedělat slepou slevu. Nejdřív upravit prezentaci, doplnit důkazy a otestovat reakce. Pokud nepřijdou konkrétní zájemci, připravit jednu řízenou úpravu ceny s jasným důvodem.

**Co změnit v inzerátu do 24 hodin:**
- první fotka musí prodávat důvěru, ne jen ukázat auto,
- text má odpovědět na námitky kupujícího dřív, než se zeptá,
- zvýraznit servis, původ, stav a důvod prodeje,
- odstranit formulace, které vypadají jako bazarová mlha.

**Jak odpovídat zájemcům:** Neobhajovat cenu obecně. Vést rozhovor přes fakta: stav, servis, srovnání, rychlost předání a férový prostor pro kontrolu auta.

**První krok:** Přepsat inzerát tak, aby kupující pochopil, proč má řešit právě toto auto, a ne další levnější kus v seznamu.

**Nabídka pomoci:** Za 790 Kč včetně DPH lze připravit konkrétní úpravu textu inzerátu. Za 1 490 Kč včetně DPH lze doplnit cenové srovnání a prodejní taktiku.
"""


def generate_preview() -> str:
    return generate_local_preview()


def generate_final_report() -> str:
    client = get_openai_client()
    if client is None:
        if get_bool_config("ALLOW_LOCAL_FALLBACK", DEFAULT_ALLOW_LOCAL_FALLBACK):
            return generate_local_report()
        raise RuntimeError(
            "Chybí OPENAI_API_KEY. Přidejte ho do Streamlit Secrets nebo jako environment variable."
        )

    system_prompt = """
You are a Czech automotive sales diagnostician and conversion copywriter.
You analyze stale car listings for private sellers and small dealers.

Goal:
- diagnose why this specific listed car is not selling,
- turn the diagnosis into practical next actions,
- naturally offer paid help without sounding pushy.

Rules:
- Write in Czech with Czech diacritics.
- English is allowed only in parentheses if useful.
- Do not invent exact market prices if not provided.
- Use the listing data as known facts. Do not ask again for model, year, price, mileage, days listed, Sauto ID, or listing URL.
- Be direct, specific, and commercially useful.
- Do not shame the seller.
- If the car has been listed for a long time, name that as a trust and urgency signal.
- Do not promise guaranteed sale.
- Mention prices as Kč včetně DPH.

Output structure:
**Auto a situace:** One concise paragraph with the known listing data.

**Hlavní brzda prodeje:** State the likely blocker: price, trust, presentation, segment, buyer type, or combination.

**Co si pravděpodobně myslí kupující:** 3-5 bullets from the buyer's perspective.

**Cenová taktika na 7 dní:** Practical pricing strategy without fake precision.

**Úprava inzerátu do 24 hodin:** Concrete changes to photos, headline, text, proof, objections.

**Jak odpovídat zájemcům:** Practical response strategy.

**Kdy už čekání nedává smysl:** Clear condition for changing the plan.

**Doporučený další krok:** Offer these options naturally:
- přepis inzerátu za 790 Kč včetně DPH,
- cenové srovnání a taktika za 1 490 Kč včetně DPH,
- kompletní prodejní balíček za 2 490 Kč včetně DPH.
"""

    user_prompt = f"Analyze this stale car listing case:\n\n{build_case_summary()}"

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


def render_current_step() -> None:
    idx = st.session_state.step_index
    if idx < len(STEPS):
        render_text_step(STEPS[idx])
        return
    if not st.session_state.contact_submitted:
        render_contact_gate()
        return
    render_preview_and_paywall()


def valid_contact(name: str, email: str, phone: str, consent: bool) -> Optional[str]:
    if len(name.strip()) < 2:
        return "Doplňte prosím jméno."
    if "@" not in email or "." not in email.split("@")[-1]:
        return "Doplňte prosím platný e-mail."
    phone_digits = "".join(ch for ch in phone if ch.isdigit())
    if len(phone_digits) < 9:
        return "Doplňte prosím telefonní číslo."
    if not consent:
        return "Bez souhlasu nemůžeme bezplatný předverdikt zobrazit ani uložit kontakt."
    return None


def render_contact_gate() -> None:
    st.markdown("**Kam poslat bezplatný předverdikt**")
    st.write(
        "Auto už máme předvyplněné. Abychom mohli výsledek přiřadit ke konkrétnímu inzerátu "
        "a navázat na něj, zadejte prosím kontakt."
    )

    with st.form("contact_gate"):
        name = st.text_input("Jméno a příjmení", value=st.session_state.contact.get("name", ""))
        email = st.text_input("E-mail", value=st.session_state.contact.get("email", ""))
        phone = st.text_input("Telefon", value=st.session_state.contact.get("phone", ""))
        consent = st.checkbox(
            "Souhlasím se zpracováním kontaktu pro zaslání výsledku a navazující nabídku k prodeji auta.",
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
            "utm_source": st.session_state.car.get("source", "sauto"),
            "utm_content": st.session_state.lead_id,
        },
    )

    st.markdown("**Objednávka plné diagnózy**")
    if not access_code and not unlock_verify_url:
        st.error("Odemykání není nastavené. Přidejte ACCESS_CODE nebo UNLOCK_VERIFY_URL do Streamlit Secrets.")
        return

    st.write(
        "Krátký předverdikt je připravený. Plná diagnóza doplní konkrétní 7denní taktiku, "
        "úpravy inzerátu a doporučenou komunikaci se zájemci."
    )
    st.info(
        "Po zaplacení vám plnou diagnózu pošleme na e-mail uvedený v objednávce. "
        "Odemykací kód slouží jen k okamžitému zobrazení výsledku v aplikaci."
    )
    st.markdown(f"[Objednat plnou diagnózu za {price_text}]({payment_url})")

    code = st.text_input("Odemykací kód z potvrzení platby", type="password")
    if st.button("Odemknout plnou diagnózu", type="primary"):
        if not verify_unlock_token(code):
            st.error("Odemykací kód nesouhlasí nebo už vypršel.")
            return
        st.session_state.unlocked = True
        st.rerun()


def render_final_report() -> None:
    if st.session_state.final_report is None:
        with st.spinner("Připravuji plnou diagnózu..."):
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
        "Stáhnout diagnózu jako Markdown",
        data=st.session_state.final_report,
        file_name="diagnoza_neprodaneho_auta.md",
        mime="text/markdown",
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="centered")
    init_state()

    if st.query_params.get("demo") == "1" and not st.session_state.get("demo_loaded"):
        load_demo_case()

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)

    col_reset, col_demo = st.columns(2)
    with col_reset:
        if st.button("Začít znovu", use_container_width=True):
            reset_app()
    with col_demo:
        if st.button("Vyplnit demo", type="primary", use_container_width=True):
            load_demo_case()
            st.rerun()

    render_car_context()
    render_history()

    if st.session_state.unlocked:
        render_final_report()
    else:
        render_current_step()


if __name__ == "__main__":
    main()
