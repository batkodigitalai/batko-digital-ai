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
