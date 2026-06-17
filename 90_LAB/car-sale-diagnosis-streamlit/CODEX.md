# CODEX.md - Diagnóza neprodaného auta

Tato složka je pracovní kopie zlatého Streamlit vzoru pro trychtýř kolem starých Sauto inzerátů.

## Stav

- lokální app: `C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\car_sale_diagnosis_app`
- výchozí vzor: `C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\sunk_cost_decision_app`
- účel: převést oslovené prodávající na zájemce o placené služby kolem prodeje auta

## Produkt

Název: `Diagnóza neprodaného auta`

Logika:

- známá data auta se berou z URL parametrů z HTML oslovení,
- neptat se znovu na model, rok, cenu, km, stáří inzerátu ani Sauto ID,
- ptát se jen na to, co z inzerátu nevíme:
  - reálný zájem za posledních 30 dní,
  - ochota změnit cenu/fotky/text/jednání,
  - priorita rychlost vs. cena,
- krátký předverdikt zdarma až po zadání jména, e-mailu, telefonu a souhlasu,
- plná diagnóza za paywallem.

## Trychtýř

1. Sauto vlna najde staré inzeráty.
2. Interní HTML karta obsahuje tlačítko na Streamlit diagnózu s parametry auta.
3. Prodávající dostane personalizovanou diagnózu konkrétního auta.
4. Placený výstup nabídne:
   - přepis inzerátu za 790 Kč včetně DPH,
   - cenové srovnání a taktiku za 1 490 Kč včetně DPH,
   - kompletní prodejní balíček za 2 490 Kč včetně DPH.

## Bezpečnost

- `OPENAI_API_KEY`, skutečný `ACCESS_CODE` a ostrý `PAYMENT_LINK` jen v Secrets.
- `ACCESS_CODE` je jen MVP fallback; pro produkci preferovat `UNLOCK_VERIFY_URL` s hodinovým tokenem.
- `.streamlit/secrets.toml` nesmí do GitHubu.
- Před dokončením musí projít anonymní smoke test veřejné aplikace.
- Jeden Stripe Payment Link stačí pro všechny inzeráty; konkrétní auto se páruje přes `client_reference_id`.

## Ostrý stav 2026-06-17

Veřejná Streamlit URL:
`https://batkodigitalai-bat-90-labcar-sale-diagnosis-streamlitapp-3hw8bj.streamlit.app/`

Stripe Payment Link:
`https://buy.stripe.com/9B6cN61bIcyH7l95sv3VC03`

Aktuální HTML vlna s tlačítkem `Diagnóza auta`:
`C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1\docs\20260617 1048 osloveni vlna 012.html`

Aktuální funkční funnel:
1. Interní HTML seznam otevře konkrétní Sauto inzerát a veřejnou diagnózu.
2. Diagnóza dostane známá data z URL parametrů; neptá se znovu na model, cenu, km, dny ani Sauto ID.
3. První zpráva prodávajícímu má získat reakci, ne poslat platbu.
4. Po kladné reakci poslat odkaz na diagnózu konkrétního auta.
5. Zákazník vyplní 3 odpovědi + jméno, e-mail, telefon a souhlas.
6. Po kontaktu dostane bezplatný předverdikt.
7. Plná diagnóza je za 199 Kč včetně DPH přes jeden Stripe Payment Link.
8. Platba se páruje přes `client_reference_id=[lead_id]`, `prefilled_email`, `utm_source`, `utm_content`.
9. Po platbě výsledek poslat na e-mail / navázat ručně; navazující služby: 790 Kč, 1 490 Kč, 2 490 Kč včetně DPH.

Povinné předávací kontroly:
- Anonymní Chrome/inkognito otevře veřejnou URL bez přihlášení.
- URL s parametry auta zobrazí správný model, cenu, nájezd a dny.
- Stripe checkout ukáže `Plná diagnóza neprodaného auta` za 199 Kč.
- Stripe URL obsahuje `client_reference_id`.
- HTML nesmí obsahovat `localhost:8501`.
