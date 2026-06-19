# Rozmluv mě s tím

Česká mikroaplikace, která rozebere rozhodnutí, jež uživatel chce slyšet potvrzené. Vede jej sedmi otázkami, oddělí fakta od výkladu a po odemčení vygeneruje přímý rozbor.

## Lokální spuštění

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Nejlevnější platební varianta

Použijte ve Stripe jednorázový **Payment Link** pro produkt „Rozmluv mě s tím“ za **199 Kč včetně DPH**. Po platbě nastavte děkovací stránku s přístupovým kódem a stejné hodnoty vložte do Streamlit Community Cloud → Settings → Secrets:

```toml
OPENAI_API_KEY = "sk-proj-..."
OPENAI_MODEL = "gpt-4.1-mini"
ACCESS_CODE = "tajny-kod-ze-stripe"
PAYMENT_LINK = "https://buy.stripe.com/..."
```

`secrets.toml` nikdy neukládejte do GitHubu. V této podobě nejsou potřeba databáze, webhooks ani Stripe API klíč: Stripe Payment Link je pro tento jednorázový produkt nejrychlejší a nejlevnější řešení.

## Nasazení

Vložte tuto složku do repozitáře a v Streamlit Community Cloud nastavte hlavní soubor `app.py`. Poté vložte Secrets uvedené výše.
