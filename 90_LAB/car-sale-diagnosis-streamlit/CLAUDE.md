# CLAUDE.md - Diagnóza neprodaného auta

Toto je Streamlit kopie určená pro prodejní trychtýř ze starých Sauto inzerátů.

Není to obecný dotazník. Většina údajů o autě už existuje v HTML vlně a má přijít přes URL parametry.

## Neměnit princip

- Streamlit,
- URL parametry z oslovovací HTML vlny,
- 3 doplňující otázky,
- krátký předverdikt zdarma,
- paywall přes Stripe Payment Link,
- přístupový kód ze Streamlit Secrets,
- finální výstup přes OpenAI API,
- české UI s diakritikou.

## Povinná kontrola

Před tvrzením hotovo:

- anonymní otevření veřejné URL,
- předvyplnění auta z parametrů,
- Stripe cena v Kč včetně DPH,
- špatný kód,
- správný kód,
- český výstup,
- stažení Markdownu.

## Ostrý provozní postup 2026-06-17

Veřejná aplikace:
`https://batkodigitalai-bat-90-labcar-sale-diagnosis-streamlitapp-3hw8bj.streamlit.app/`

Stripe:
`https://buy.stripe.com/9B6cN61bIcyH7l95sv3VC03`

Denní workflow:
1. Z interní HTML vlny otevřít původní inzerát a zkontrolovat, že je pořád živý.
2. Kliknout `Diagnóza auta` a ověřit předvyplnění auta ve veřejném Streamlitu.
3. Prodávajícímu neposílat rovnou Stripe. Poslat krátké oslovení s cílem získat souhlas/reakci.
4. Po reakci poslat odkaz na diagnózu konkrétního auta.
5. Bezplatný předverdikt zobrazit až po jménu, e-mailu, telefonu a souhlasu.
6. Plná diagnóza stojí 199 Kč včetně DPH.
7. Jeden Stripe link stačí pro všechna auta; párování řeší `client_reference_id=[lead_id]`.
8. Po platbě dohledat zákazníka ve Stripe podle e-mailu a `client_reference_id`; výsledek poslat na e-mail nebo navázat ručně.
9. Navazující nabídka: přepis inzerátu 790 Kč, cenová taktika 1 490 Kč, kompletní balíček 2 490 Kč včetně DPH.

Nesmí se vrátit:
- `DIAGNOSIS_APP_URL = 'http://localhost:8501/'` v HTML vlně,
- ruční vytváření Stripe odkazu pro každé auto,
- zákaznické texty bez české diakritiky,
- tvrzení hotovo bez anonymního smoke testu.
