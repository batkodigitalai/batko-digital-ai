# Diagnóza neprodaného auta

Streamlit mikroaplikace pro prodávající aut, jejichž inzerát visí dlouho bez výsledku.

Ostrá veřejná URL:

```text
https://batkodigitalai-bat-90-labcar-sale-diagnosis-streamlitapp-3hw8bj.streamlit.app/
```

Vychází ze zlatého vzoru `sunk_cost_decision_app`, ale je přepsaná pro Sauto oslovení:

- auto se předvyplní z URL parametrů,
- uživatel doplní jen 3 věci, které z inzerátu neznáme,
- krátký předverdikt je zdarma až po zadání kontaktu,
- plná diagnóza je za přístupovým kódem,
- výstup generuje OpenAI API,
- UI je česky s diakritikou.

## URL parametry

Příklad odkazu z HTML vlny:

```text
https://[streamlit-url]/?sauto_id=208932162&model=Volkswagen%20Passat&year=2019&price=488999&km=148000&days=313&listed_from=2025-08-07&source=sauto_vlna_012
```

Podporované parametry:

- `sauto_id`
- `model`
- `year`
- `price`
- `km`
- `days`
- `listed_from`
- `sauto_url`
- `source`

## Secrets

Skutečné hodnoty patří jen do `.streamlit/secrets.toml` lokálně a do Streamlit Secrets v produkci.

```toml
OPENAI_API_KEY = "placeholder-openai-key"
ACCESS_CODE = "placeholder"
PAYMENT_LINK = "https://buy.stripe.com/9B6cN61bIcyH7l95sv3VC03"
OPENAI_MODEL = "gpt-4.1-mini"
ALLOW_LOCAL_FALLBACK = "false"
PRICE_TEXT = "199 Kč včetně DPH"
LEAD_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwcFA8bRyHnBB_4XlgH5_IMR4IBqUfvTD8vScGZPiuCh0gR5f4Mp_9OjOAw1u3lNEjI/exec"
UNLOCK_VERIFY_URL = "https://script.google.com/macros/s/..."
REQUIRE_LEAD_WEBHOOK = "false"
```

`.streamlit/secrets.toml` se nesmí nahrát do GitHubu.

`LEAD_WEBHOOK_URL` je volitelný pro lokální test. V produkci nastavit `REQUIRE_LEAD_WEBHOOK = "true"`,
aby se bezplatný předverdikt nezobrazil bez zápisu kontaktu.

`ACCESS_CODE` je jen MVP fallback. Pro škálování použít `UNLOCK_VERIFY_URL`, kde Apps Script ověří jednorázový token proti `lead_id` a expiraci.

## Lead a Stripe

Po třech doplňujících otázkách aplikace vyžádá jméno, e-mail, telefon a souhlas se zpracováním kontaktu.

Potom vytvoří `lead_id` ve tvaru:

```text
sauto-[sauto_id]-[timestamp]
```

Stripe Payment Link se používá jeden pro všechny inzeráty. Aplikace k němu automaticky přidá:

```text
client_reference_id=[lead_id]
prefilled_email=[email]
utm_source=[source]
utm_content=[lead_id]
```

Tím se platba dá spárovat s konkrétním autem a leadem bez vytváření nového Stripe produktu pro každý inzerát.

Zákaznicky se neprodává kód, ale plná diagnóza. Kód nebo token je pouze technický způsob,
jak po platbě zobrazit výsledek ihned v aplikaci. Hlavní slib je dodání výsledku na e-mail.

## Lokální spuštění

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Demo:

```text
http://localhost:8501/?demo=1
```

## Produkční kontrola

Před slovem hotovo ověřit:

- veřejná URL jde otevřít anonymně,
- předvyplněné auto se správně zobrazí z parametrů,
- interní HTML vlna neobsahuje `localhost:8501`,
- tlačítko `Diagnóza auta` míří na veřejnou Streamlit URL,
- doplňující 3 otázky fungují,
- paywall ukazuje cenu v Kč včetně DPH,
- Stripe checkout ukazuje `Plná diagnóza neprodaného auta` za 199 Kč,
- Stripe URL obsahuje `client_reference_id`,
- špatný / expirovaný kód je odmítnut,
- správný kód nebo token odemkne plnou diagnózu,
- výstup je česky,
- stažení Markdownu funguje.

## Provozní funnel

1. Oslovit prodávajícího krátce a lidsky; neposílat rovnou platební odkaz.
2. Po reakci poslat diagnostiku konkrétního auta.
3. Získat kontakt přes Streamlit.
4. Zobrazit bezplatný předverdikt.
5. Prodat plnou diagnózu za 199 Kč včetně DPH.
6. Spárovat platbu přes e-mail a `client_reference_id`.
7. Navázat vyšší službou: 790 Kč, 1 490 Kč nebo 2 490 Kč včetně DPH.
