import os
from typing import Dict, Optional

import streamlit as st
from openai import OpenAI


NÁZEV_APLIKACE = "Rozmluv mě s tím"
VÝCHOZÍ_ODKAZ_PLATBY = "https://buy.stripe.com/vas-odkaz"
VÝCHOZÍ_MODEL = "gpt-4.1-mini"

KROKY = [
    ("tvrzení", "Krok 1", "Co přesně chcete udělat nebo čemu chcete věřit? Napište to jednou větou.", "Například: Chci dát výpověď a začít podnikat na plný úvazek."),
    ("přání", "Krok 2", "K jaké odpovědi tajně doufáte, že vás dovedu?", "Například: Že výpověď je správná a jen se zbytečně bojím."),
    ("záznam", "Krok 3", "Jaká ověřitelná fakta máte? Uveďte konkrétní slova, činy, data, peníze nebo termíny.", "Například: Mám příjem 40 000 Kč měsíčně z klientů po dobu posledních tří měsíců."),
    ("příběh", "Krok 4", "Jaký význam jste na tato fakta navěsil(a)? Co z nich podle vás plyne?", "Například: Znamená to, že podnikání už je bezpečné."),
    ("sázky", "Krok 5", "Co byste musel(a) přiznat, ztratit nebo cítit, kdyby odpověď, kterou si přejete, byla chybná?", "Například: Že jsem si spletl(a) nadšení s jistotou a budu muset počkat."),
    ("protikaz", "Krok 6", "Jaké jsou nejsilnější důkazy nebo okolnosti proti vašemu oblíbenému závěru?", "Napište i to, co se vám nechce uznat."),
    ("obrat", "Krok 7", "Jaký konkrétní důkaz by vám změnil názor? Musí být pozorovatelný a časově ohraničený.", "Například: Pokud příjem z klientů nepřesáhne 60 000 Kč po šest měsíců, výpověď nedám."),
]

DEMO_ODPOVĚDI = {
    "tvrzení": "Chci dát výpověď a do tří měsíců přejít na podnikání na plný úvazek.",
    "přání": "Chci slyšet, že už nemusím čekat a že opatrnost je jen strach.",
    "záznam": "Poslední tři měsíce mám od klientů 35 000, 42 000 a 38 000 Kč. Mám úspory na čtyři měsíce. Dva klienti řekli, že možná navýší spolupráci.",
    "příběh": "Znamená to, že poptávka je stabilní a za chvíli budu vydělávat víc než v zaměstnání.",
    "sázky": "Musel bych přiznat, že jsem si z přání udělal předpověď. Zůstat v práci mě frustruje a nechci působit nerozhodně.",
    "protikaz": "Tři měsíce jsou krátké období. Příjem není stabilní ani vyšší než moje výdaje. Navýšení od klientů není závazek.",
    "obrat": "Názor změním, pokud budu mít šest měsíců po sobě alespoň 70 000 Kč měsíčního zisku, úspory na devět měsíců a dva podepsané kontrakty na další čtvrtletí.",
}


def nastavení(název: str, výchozí: Optional[str] = None) -> Optional[str]:
    try:
        return st.secrets.get(název, os.getenv(název, výchozí))
    except Exception:
        return os.getenv(název, výchozí)


def připrav_stav() -> None:
    for klíč, hodnota in {"krok": 0, "odpovědi": {}, "odemčeno": False, "výsledek": None}.items():
        st.session_state.setdefault(klíč, hodnota)


def začít_znovu() -> None:
    for klíč in ("krok", "odpovědi", "odemčeno", "výsledek", "demo"):
        st.session_state.pop(klíč, None)
    st.rerun()


def načíst_demo() -> None:
    st.session_state.odpovědi = DEMO_ODPOVĚDI.copy()
    st.session_state.krok = len(KROKY)
    st.session_state.odemčeno = True
    st.session_state.výsledek = None
    st.session_state.demo = True
    st.rerun()


def souhrn_případu() -> str:
    return "\n".join(f"{popis}: {st.session_state.odpovědi.get(klíč, '')}" for klíč, popis, _, _ in KROKY)


def místní_výsledek() -> str:
    o = st.session_state.odpovědi
    return f"""## Odpověď, kterou si přejete
{o.get('přání', 'Neuvedeno.')}

## Záznam vs. příběh
| Ověřitelný záznam | Příběh, který na něm stojí |
| --- | --- |
| {o.get('záznam', 'Neuvedeno.')} | {o.get('příběh', 'Neuvedeno.')} |

## Kde se příběh vydává za fakt
{o.get('příběh', 'Neuvedeno.')} není důkaz sám o sobě. Je to výklad; jeho platnost musí nést konkrétní data.

## Co ztratíte, když nemáte pravdu
{o.get('sázky', 'Neuvedeno.')}

## Nejsilnější případ proti vám
{o.get('protikaz', 'Neuvedeno.')}

## Důkaz, který by vás obrátil
{o.get('obrat', 'Neuvedeno.')}

## Přímé čtení
Nemáte dost podkladů k tomu, aby pouhé přání fungovalo jako důkaz. Rozhodnutí držte jen tak silně, jak silný je ověřitelný záznam.

## Jeden další krok
Nastavte si konkrétní test podle uvedené podmínky obratu a do jeho splnění neudělejte nevratný krok.
"""


def vytvořit_výsledek() -> str:
    klíč = nastavení("OPENAI_API_KEY")
    if not klíč:
        return místní_výsledek()
    systém = """Jsi Rozmluv mě s tím, přímý český partner pro testování úsudku.
Uživatel často chce potvrdit výsledek, kterému už fandí. Odděl ověřitelný záznam od příběhu,
vytvoř nejsilnější argument proti jeho preferované odpovědi a netvař se jako konečná autorita
v lásce, zdraví, penězích, právu ani bezpečnosti. Piš česky, věcně a bez lichotek.
Použij přesně tyto nadpisy: Odpověď, kterou si přejete; Záznam vs. příběh; Kde se příběh vydává za fakt;
Co ztratíte, když nemáte pravdu; Nejsilnější případ proti vám; Důkaz, který by vás obrátil;
Přímé čtení; Jeden další krok. U části Záznam vs. příběh použij tabulku. Poslední část obsahuje jediný krok."""
    try:
        odpověď = OpenAI(api_key=klíč).chat.completions.create(
            model=nastavení("OPENAI_MODEL", VÝCHOZÍ_MODEL), temperature=0.25,
            messages=[{"role": "system", "content": systém}, {"role": "user", "content": souhrn_případu()}],
        )
        return odpověď.choices[0].message.content or místní_výsledek()
    except Exception:
        return místní_výsledek()


def zobrazit_krok() -> None:
    číslo = st.session_state.krok
    if číslo >= len(KROKY):
        zobrazit_placení()
        return
    klíč, označení, otázka, nápověda = KROKY[číslo]
    st.markdown(f"**{označení} z {len(KROKY)}**")
    st.write(otázka)
    with st.form(f"formulář_{klíč}", clear_on_submit=True):
        text = st.text_area("Vaše odpověď", placeholder=nápověda, height=150, label_visibility="collapsed")
        odeslat = st.form_submit_button("Pokračovat", type="primary")
    if odeslat:
        if not text.strip():
            st.warning("Napište alespoň krátkou odpověď.")
            return
        st.session_state.odpovědi[klíč] = text.strip()
        st.session_state.krok += 1
        st.rerun()


def zobrazit_placení() -> None:
    odkaz = nastavení("PAYMENT_LINK", VÝCHOZÍ_ODKAZ_PLATBY)
    kód = nastavení("ACCESS_CODE", "")
    st.subheader("Tvrdý rozbor je připraven")
    st.write("Vaše odpovědi jsou připravené. Pro odemčení finálního rozboru zadejte přístupový kód.")
    st.markdown(f"[Koupit přístupový kód za 199 Kč včetně DPH]({odkaz})")
    if not kód:
        st.info("Platba ještě není nastavená. Doplňte `PAYMENT_LINK` a `ACCESS_CODE` do Streamlit Secrets.")
        return
    zadaný_kód = st.text_input("Přístupový kód", type="password")
    if st.button("Odemknout rozbor", type="primary"):
        if zadaný_kód.strip() != kód:
            st.error("Přístupový kód nesouhlasí.")
        else:
            st.session_state.odemčeno = True
            st.rerun()


def hlavní() -> None:
    st.set_page_config(page_title=NÁZEV_APLIKACE, page_icon="🧭", layout="centered")
    připrav_stav()
    st.title(NÁZEV_APLIKACE)
    st.caption("Neberu stranu odpovědi, kterou chcete slyšet. Nejdřív ji zkusíme rozebrat.")
    první, druhý = st.columns(2)
    with první:
        if st.button("Začít znovu", use_container_width=True):
            začít_znovu()
    with druhý:
        if st.button("Ukázat demo", type="primary", use_container_width=True):
            načíst_demo()
    if st.session_state.odemčeno:
        if st.session_state.výsledek is None:
            with st.spinner("Připravuji přímý rozbor…"):
                st.session_state.výsledek = vytvořit_výsledek()
        st.markdown(st.session_state.výsledek)
        st.download_button("Stáhnout výsledek jako Markdown", st.session_state.výsledek, "rozmluv-me-s-tim.md", "text/markdown")
    else:
        zobrazit_krok()


if __name__ == "__main__":
    hlavní()
