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
