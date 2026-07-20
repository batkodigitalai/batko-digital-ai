# Decision Strategist

Streamlit micro-aplikace pro vyhodnoceni zavazku pres sunk-cost logiku s paywallem a finalnim verdiktem pres OpenAI API.

## Lokalni spusteni

```powershell
pip install -r requirements.txt
streamlit run app.py
```

Po spusteni otevri:

```text
http://localhost:8501
```

## Streamlit Community Cloud

1. Nahrajte tuto slozku do GitHub repozitare.
2. Ve Streamlit Cloud nastavte `app.py` jako hlavni soubor.
3. Do `Settings -> Secrets` vlozte:

```toml
OPENAI_API_KEY = "sk-proj-your-key-here"
ACCESS_CODE = "sem-vlozte-kod-ze-stripe-dekovaci-stranky"
PAYMENT_LINK = "https://buy.stripe.com/14A5kE6w2eGP5d108b3VC02"
OPENAI_MODEL = "gpt-4.1-mini"
ALLOW_LOCAL_FALLBACK = "false"
```

4. Ve Stripe Payment Link nastavte jednorazovou cenu `199 Kc vcetne DPH` a po zaplaceni dekovaci zpravu s pristupovym kodem.

Pro lokalni testovani je uz vytvoren soubor `.streamlit/secrets.toml`.
Tento soubor se nesmi nahrat na GitHub. Pokud neni nastaveny `OPENAI_API_KEY`,
aplikace muze pri lokalnim testu pouzit fallback verdikt. V produkci nastavte
`ALLOW_LOCAL_FALLBACK = "false"`.

## Overeni

Lokalne overeno:

- aplikace se spusti na `http://localhost:8501`
- kroky 1 az 7 postupne drzi stav v `st.session_state`
- potvrzeni utopenych nakladu se zobrazi po Kroku 3
- test od nuly zobrazuje tlacitka `ANO` a `NE`
- paywall odmita spatny kod a prijima kod nastaveny ve Streamlit Secrets
- bez `OPENAI_API_KEY` se vytvori lokalni fallback verdikt
