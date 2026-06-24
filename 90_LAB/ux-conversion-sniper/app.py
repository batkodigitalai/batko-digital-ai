import os
import tomllib
from textwrap import dedent
from pathlib import Path

import streamlit as st


APP_TITLE = "UX Conversion Sniper"
APP_LABEL = "ZDARMA: RYCHLÁ KONTROLA TEXTŮ PRO E-SHOPY A SAAS"
APP_SUBTITLE = "Zjistěte, kde váš text zákazníka mate nebo nutí váhat."
COMPANY_NAME = "BATKO.DIGITAL.AI"
COMPANY_PERSON = "Ing. Jaroslav Batko"
COMPANY_ICO = "14600153"
COMPANY_DIC = "CZ5912280418"
COMPANY_ADDRESS = "Lískovec 170, 273 51 Velké Přítočno"
COMPANY_PHONE = "+420 725 360 151"
COMPANY_EMAIL = "batko.digital.ai@gmail.com"

DEFAULT_ACCESS_CODE = "UX2490"
DEFAULT_PRICE_TEXT = "2 490 Kč včetně DPH"
DEFAULT_TEASER_MODEL = "gpt-4.1-mini"
DEFAULT_REPORT_MODEL = "gpt-4.1"
UPSELL_PRICE_SMALL = "14 990 Kč vč. DPH"
UPSELL_PRICE_LARGE = "29 990 Kč vč. DPH"

DEMO_FLOW = """1. Košík — tlačítko: Pokračovat
2. Doprava — text: Zvolte způsob doručení
3. Platba — tlačítko: Potvrdit objednávku
4. Chyba formuláře: Pole není vyplněno"""

PROMPT_TEASER = """Jsi přímý a zkušený UX výzkumník pro e-shopy a SaaS. Analyzuješ jeden nebo více krátkých UX textů v češtině.
Najdi největší problém z pohledu konverze: system-speak, nejasný následek akce, zbytečné tření nebo nepřiměřenou délku.
Nevymýšlej procenta ztrát, neodkazuj na neověřené studie a zatím nedávej konkrétní nové znění.
Odpověz česky, stručně, přesně v této struktuře:

**Skóre konverzního potenciálu: [0–100]/100**
**Největší tření:** [1–2 věty]
**Co uživatel v kritickém okamžiku neví nebo cítí:** [1 věta]
**Verdikt:** [1 úderná věta o prioritě opravy]
"""

PROMPT_REPORT = """Jsi špičkový UX copywriter. Přepisuješ microcopy pro e-shop nebo SaaS tak, aby člověk jasně věděl, co se stane, proč je to pro něj užitečné a jaký má udělat další krok.
Píšeš česky. Neuváděj smyšlené výsledky, procenta ani garance konverze. Nepřidávej funkce, ceny, termíny ani právní sliby, které nejsou ve vstupu.

Pro KAŽDÝ řádek/obrazovku ze vstupu vrať přesně tento blok:

### [Název obrazovky nebo původní text]
**Původní text:** [text]

| Varianta | Text připravený ke kopírování | Proč funguje |
|---|---|---|
| A – jasnost | ... | ... |
| B – užitek | ... | ... |
| C – klid / motivace | ... | ... |

**Doporučení k nasazení:** [zvol A/B/C a jednu konkrétní instrukci]

Na konci přidej:
## Priorita nasazení
1. [nejdůležitější změna]
2. [druhá změna]
3. [třetí změna]

## Checklist před publikací
- [ ] Text přesně říká, co se stane po kliknutí.
- [ ] Slova odpovídají jazyku zákazníka, ne internímu procesu.
- [ ] Tvrzení a podmínky jsou pravdivé a ověřené.
- [ ] Změnu lze měřit proti původní verzi.
"""

CSS = """<style>
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background:#f7f5f0!important; color:#13231b!important; }
[data-testid="stHeader"] { background:#f7f5f0!important; }
button[kind="primary"] { background:#13231b!important; color:#f7f5f0!important; border-radius:8px!important; font-weight:700!important; }
[data-testid="stMetricValue"] { color:#b6452c!important; font-weight:800!important; }
[data-testid="stExpander"] { background:#fff!important; border:1.5px solid #e8e0d0!important; border-radius:10px!important; }
.sniper-card { background:#fff; border:1.5px solid #e8e0d0; border-radius:12px; padding:1.25rem 1.4rem; margin:1rem 0; }
.eyebrow { color:#b6452c; font-size:.78rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }
.price { font-size:2rem; font-weight:800; color:#b6452c; margin:.5rem 0; }
.value-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.7rem; margin:1rem 0; }
.value-item { background:#fff;border:1.5px solid #e8e0d0;border-radius:10px;padding:.9rem; }
@media(max-width:640px) { .value-grid { grid-template-columns:1fr; } }
</style>"""


def cfg(key, default=None):
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass
    # Lokální vývoj: sdílí existující klíč mezi aplikacemi, aniž by se tajná
    # hodnota kopírovala do tohoto projektu nebo do repozitáře.
    if key == "OPENAI_API_KEY":
        shared_secret = Path(__file__).resolve().parent.parent / "ai-compliance-audit" / ".streamlit" / "secrets.toml"
        if shared_secret.exists():
            try:
                with shared_secret.open("rb") as handle:
                    shared_key = tomllib.load(handle).get("OPENAI_API_KEY", "")
                if shared_key:
                    return shared_key
            except Exception:
                pass
    return os.getenv(key, default)


def call_openai(system_prompt, user_input, model):
    api_key = cfg("OPENAI_API_KEY")
    if not api_key:
        return ""
    try:
        from openai import OpenAI

        response = OpenAI(api_key=api_key).chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
            temperature=0.55,
            max_tokens=2200,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        st.error(f"AI audit se nepodařilo vytvořit: {exc}")
        return ""


def demo_teaser():
    return dedent("""
    **Skóre konverzního potenciálu: 46/100**
    **Největší tření:** Texty popisují krok systému, ale ne výsledek pro zákazníka. „Potvrdit objednávku“ je v zásadě použitelné, ale neodstraňuje poslední nejistotu před odesláním.
    **Co uživatel v kritickém okamžiku neví nebo cítí:** Musí si sám domyslet, zda bude objednávka skutečně odeslána a co přesně následuje.
    **Verdikt:** Začněte posledním krokem nákupu — má nejvyšší potenciál odstranit zbytečné váhání.
    """).strip()


def demo_report():
    return dedent("""
    ### Košík — „Pokračovat"
    **Původní text:** Pokračovat

    | Varianta | Text připravený ke kopírování | Proč funguje |
    |---|---|---|
    | A – jasnost | Pokračovat k dopravě | Říká přesně, kam kliknutí vede. |
    | B – užitek | Vybrat dopravu | Popisuje další úkol jazykem zákazníka. |
    | C – klid / motivace | Doprava a platba → | Dává přehled o zbývajících krocích. |

    **Doporučení k nasazení:** A — použijte jej přímo na hlavní tlačítko košíku.

    ### Platba — „Potvrdit objednávku"
    **Původní text:** Potvrdit objednávku

    | Varianta | Text připravený ke kopírování | Proč funguje |
    |---|---|---|
    | A – jasnost | Objednat a zaplatit | Jasně pojmenovává dvě bezprostřední akce. |
    | B – užitek | Dokončit objednávku | Potvrzuje, že jde o finální krok. |
    | C – klid / motivace | Dokončit nákup → | Zkracuje formulaci a drží pozornost na cíli. |

    **Doporučení k nasazení:** A — ověřte, že skutečný platební krok odpovídá tomuto znění.

    ## Priorita nasazení
    1. Upřesněte tlačítko ve finálním kroku objednávky.
    2. Pojmenujte tlačítko v košíku podle následujícího kroku.
    3. Nahraďte obecné chybové hlášky konkrétní instrukcí.

    ## Checklist před publikací
    - [ ] Text přesně říká, co se stane po kliknutí.
    - [ ] Slova odpovídají jazyku zákazníka, ne internímu procesu.
    - [ ] Tvrzení a podmínky jsou pravdivé a ověřené.
    - [ ] Změnu lze měřit proti původní verzi.
    """).strip()


def reset_flow():
    for key in ("teaser", "report", "unlocked"):
        st.session_state.pop(key, None)


def load_demo():
    st.session_state.flow = DEMO_FLOW
    st.session_state.teaser = demo_teaser()
    st.session_state.report = ""
    st.session_state.unlocked = False


def render_value_proposition():
    st.markdown("""<div class='sniper-card'>
    <div class='eyebrow'>PROČ ZÁKAZNÍCI NEDOKONČÍ DALŠÍ KROK</div>
    <h3 style='margin:.35rem 0 .7rem'>Nejde o tlačítko. Jde o okamžik, kdy zákazník neví, co má udělat dál.</h3>
    <p>V košíku, registraci nebo formuláři už zákazník udělal většinu práce. Pak narazí na „Odeslat“, „Potvrdit“ nebo „Pole není vyplněno“. Systém ví, co se děje. Člověk ne — začne váhat, udělá chybu nebo odejde.</p>
    <p><strong>Vložte svůj text a zdarma uvidíte, kde vzniká problém.</strong> Ukážeme vám, co je pro zákazníka nejasné. Hotové přepisy celé flow si pak můžete odemknout, jen pokud je budete chtít.</p>
    <div class='value-grid'>
      <div class='value-item'><strong>🎯 Co zjistíte zdarma</strong><br><span>Jedno místo, kde text zákazníka mate nebo zbytečně brzdí.</span></div>
      <div class='value-item'><strong>🔬 Co je v plném auditu</strong><br><span>3 hotové varianty každého textu a vysvětlení, proč dávají větší smysl.</span></div>
      <div class='value-item'><strong>⚡ Kolik práce vás čeká</strong><br><span>Vyberete Variantu A a zkopírujete ji do CMS či kódu. Změna zabere přibližně 10 minut.</span></div>
      <div class='value-item'><strong>🛡️ Proč začít hned</strong><br><span>Nejdřív uvidíte problém na vlastním textu. Za kompletní řešení platíte až potom.</span></div>
    </div></div>""", unsafe_allow_html=True)


def render_paywall():
    payment_link = cfg("PAYMENT_LINK", "")
    st.markdown("---")
    st.markdown("<div class='eyebrow'>KROK 2 ZE 2</div>", unsafe_allow_html=True)
    st.subheader("⚡ Odemkněte Kompletní audit a UX přepis")
    st.write("Nekupujete generátor textu. Kupujete **rychlejší cestu k jasnému dalšímu kroku zákazníka** — bez redesignu, workshopů a týdnů čekání na UX agenturu.")
    st.markdown("""**Co přesně dostanete za jednu flow až o 5 obrazovkách:**

- původní text vedle 3 hotových variant připravených ke kopírování;
- u každé varianty krátké vysvětlení, jakou nejistotu nebo tření odstraňuje;
- doporučení, kterou variantu nasadit jako první;
- checklist a slovník, podle kterých odhalíte podobné chyby i příště.

**Co uděláte vy:** vyberete Variantu A a vložíte ji do CMS nebo kódu. Typicky do 10 minut.""")
    st.markdown(f"<div class='price'>{cfg('PRICE_TEXT', DEFAULT_PRICE_TEXT)}</div>", unsafe_allow_html=True)
    if payment_link:
        st.link_button("💳 Zaplatit a odemknout →", payment_link, type="primary", use_container_width=True)
        st.caption("Po platbě se vraťte sem a zadejte přístupový kód z potvrzení objednávky.")
    else:
        st.info("Stripe Payment Link zatím není nastaven. Pro test použijte přístupový kód v secrets.toml.")
    st.info("🛡️ **Garance 300milionového tlačítka:** Pokud vám nové texty nepřinesou použitelný a jasnější návrh, vrátíme 100 % částky a text vám manuálně přepracujeme.")
    with st.expander("🎁 Bonusy: Checklist + slovník zakázaných systémových slov"):
        st.markdown("- **Checklist 10 nejčastějších chyb v UX copy** — kontrola před publikací  \n- **Slovník zakázaných systémových slov** — formulace, které nutí zákazníka přemýšlet místo jednat  \n- **Priorita nasazení** — co přepsat jako první, aby se změna nezasekla v backlogu")
    with st.expander("Máte přístupový kód?"):
        code = st.text_input("Přístupový kód", type="password")
        if st.button("🔓 Odemknout audit", type="primary", use_container_width=True):
            if code.strip().upper() == cfg("ACCESS_CODE", DEFAULT_ACCESS_CODE).upper():
                st.session_state.unlocked = True
                st.rerun()
            else:
                st.error("Kód nesouhlasí. Zkontrolujte e-mail po platbě.")


def render_upsell():
    st.markdown(f"""<div style='background:linear-gradient(135deg,#0a2850,#1a4a8a);border-radius:12px;padding:1.8rem 2rem;margin:2rem 0;color:#f7f5f0'>
    <div style='font-size:1.15rem;font-weight:800;margin-bottom:.6rem'>🚀 Uděláme to za vás: Komplexní UX audit celého webu</div>
    <div style='color:#c9d8f0;margin-bottom:1rem'>Vidíte, jak jeden text dokáže vytvořit tření? Web má podobných tlačítek, formulářů a dialogů desítky. Provedeme audit člověk + AI, dodáme report s konkrétními přepisy a přidáme 60minutovou konzultaci.</div>
    <div style='color:#ffd700;font-size:1.5rem;font-weight:800'>{UPSELL_PRICE_SMALL} <span style='font-size:.95rem;color:#c9d8f0'>/ e-shop</span></div>
    <div style='color:#ffd700;font-size:1.5rem;font-weight:800'>{UPSELL_PRICE_LARGE} <span style='font-size:.95rem;color:#c9d8f0'>/ větší SaaS</span></div>
    <a href='mailto:{COMPANY_EMAIL}?subject=Komplexní%20UX%20audit' style='display:inline-block;margin-top:1rem;background:#ffd700;color:#0a2850;text-decoration:none;padding:.6rem 1.2rem;border-radius:8px;font-weight:800'>📧 Napsat a domluvit audit →</a></div>""", unsafe_allow_html=True)


def render_footer():
    st.divider()
    with st.expander("📞 Kontakt"):
        st.markdown(f"**{COMPANY_NAME}**  \n{COMPANY_PERSON}  \nIČO: {COMPANY_ICO} · DIČ: {COMPANY_DIC}  \n{COMPANY_ADDRESS}  \n{COMPANY_PHONE} · {COMPANY_EMAIL}")
    with st.expander("📄 Obchodní podmínky"):
        st.write(f"Digitální produkt ve smyslu § 1837 písm. l) občanského zákoníku. Zakoupením souhlasíte se zahájením plnění před uplynutím lhůty pro odstoupení. Provozovatel: {COMPANY_NAME}, IČO {COMPANY_ICO}, {COMPANY_ADDRESS}.")
    with st.expander("🔒 Ochrana soukromí"):
        st.write("Zadané texty používáme výhradně k vytvoření auditu. Neukládáme je do vlastního úložiště. Pro generování je využíváno OpenAI API; nevkládejte do aplikace citlivé osobní údaje, platební údaje ani hesla.")
    with st.expander("💸 Vrácení peněz"):
        st.write(f"Pokud audit nebude obsahovat alespoň 3 okamžitě použitelné návrhy, napište do 14 dnů na {COMPANY_EMAIL} s předmětem „Vrácení peněz“. Situaci vyřešíme individuálně.")
    st.caption(f"{COMPANY_NAME} · IČO {COMPANY_ICO} · {COMPANY_ADDRESS}")


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🎯", layout="centered")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(f"<div class='eyebrow'>{APP_LABEL}</div>", unsafe_allow_html=True)
    st.title("🎯 UX Conversion Sniper")
    st.caption(APP_SUBTITLE)
    render_value_proposition()

    st.subheader("Zjistěte zdarma, kde váš text vytváří problém")
    st.write("Vložte text tlačítka, formuláře, chybové hlášky nebo dialogu. Za půl minuty uvidíte, kde zákazník neví, co se stane dál — ještě před tím, než se rozhodnete pro kompletní audit.")
    if "flow" not in st.session_state:
        st.session_state.flow = ""
    with st.form("audit_form", border=False):
        flow = st.text_area("Texty k auditu", height=190, placeholder="Košík — tlačítko: Pokračovat\nPlatba — tlačítko: Potvrdit objednávku\nChyba adresy: Pole není vyplněno", key="flow")
        left, right = st.columns(2)
        generate_clicked = left.form_submit_button("🔍 Najít problém v textu zdarma →", type="primary", use_container_width=True)
        right.form_submit_button("▶ Načíst demo", use_container_width=True, on_click=load_demo)
    if generate_clicked:
        reset_flow()
        if not flow.strip():
            st.warning("Vložte alespoň jeden text k analýze.")
        else:
            with st.spinner("Hledám největší tření v microcopy…"):
                st.session_state.teaser = call_openai(PROMPT_TEASER, flow, cfg("TEASER_MODEL", DEFAULT_TEASER_MODEL)) or demo_teaser()

    a, b, c = st.columns(3)
    a.metric("Čas do výsledku", "< 30 s")
    b.metric("Rozsah auditu", "až 5 obrazovek")
    c.metric("Čas nasazení", "~ 10 min")

    if st.session_state.get("teaser"):
        st.markdown("<div class='sniper-card'><div class='eyebrow'>Váš test reality</div>", unsafe_allow_html=True)
        st.markdown(st.session_state.teaser)
        st.markdown("</div>", unsafe_allow_html=True)
        if not st.session_state.get("unlocked"):
            render_paywall()
        else:
            if not st.session_state.get("report"):
                with st.spinner("Připravuji kompletní UX přepis…"):
                    st.session_state.report = call_openai(PROMPT_REPORT, flow, cfg("REPORT_MODEL", DEFAULT_REPORT_MODEL)) or demo_report()
            st.success("Audit je odemčený. Vyberte jednu variantu a před publikací ji ověřte v kontextu obrazovky.")
            st.markdown(st.session_state.report)
            st.download_button("⬇️ Stáhnout audit (.md)", st.session_state.report, "ux-conversion-audit.md", "text/markdown", use_container_width=True)
            render_upsell()
    render_footer()


if __name__ == "__main__":
    main()
