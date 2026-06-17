# Seznam trychtýře - staré Sauto inzeráty

## Hlavní cesta

1. Interní HTML vlna obsahuje karty starých inzerátů.
2. U každé karty bude tlačítko `Diagnóza auta`.
3. Tlačítko otevře Streamlit s parametry konkrétního auta.
4. Prodávající doplní jen tři odpovědi.
5. Zadá jméno, e-mail, telefon a souhlas.
6. Zdarma uvidí krátký předverdikt.
7. Plný výstup se odemkne přístupovým kódem nebo později hodinovým tokenem.
8. Výstup nabídne navazující placené služby.

## Parametry do odkazu

```text
?sauto_id=...&model=...&year=...&price=...&km=...&days=...&listed_from=...&sauto_url=...&source=sauto_vlna_012
```

## Nabídky po výstupu

- Přepis inzerátu: 790 Kč včetně DPH.
- Cenové srovnání a 7denní taktika: 1 490 Kč včetně DPH.
- Kompletní prodejní balíček: 2 490 Kč včetně DPH.

## Otevřené rozhodnutí

- Cena plné diagnózy: zatím 199 Kč včetně DPH.
- Stripe Payment Link: `https://buy.stripe.com/9B6cN61bIcyH7l95sv3VC03`.
- Přístupový kód: nastavit jen v Secrets.
- Veřejná Streamlit URL: doplnit po deployi.
- Lead webhook: `https://script.google.com/macros/s/AKfycbwcFA8bRyHnBB_4XlgH5_IMR4IBqUfvTD8vScGZPiuCh0gR5f4Mp_9OjOAw1u3lNEjI/exec`.
- V produkci zapnout `REQUIRE_LEAD_WEBHOOK = "true"`.

## Aktuální napojení

- Soubor `C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1\docs\20260617 1048 osloveni vlna 012.html` má doplněné tlačítko `Diagnóza auta`.
- Odkaz se skládá automaticky z karty auta.
- Konstanta `DIAGNOSIS_APP_URL` je zatím `http://localhost:8501/`.
- Po produkčním deployi změnit `DIAGNOSIS_APP_URL` na veřejnou Streamlit URL.
- Apps Script webhook byl nahrán přes `clasp push --force` a redeploynut na `@20`.
- Testovací POST `Diagnoza_Neprodaneho_Auta` vrátil `{"ok":true}`.

## Stripe a odemykání pro 100+ inzerátů

Nepřipravovat nový Stripe produkt pro každý inzerát.

Použít jeden Stripe Payment Link pro `Plná diagnóza neprodaného auta - 199 Kč včetně DPH`.

Aplikace přidá k platební URL:

```text
client_reference_id=[lead_id]
prefilled_email=[email]
utm_source=[source]
utm_content=[lead_id]
```

Tím jde platba dohledat podle konkrétního auta a kontaktu.

## Zákaznická logika platby

Neprodává se heslo. Prodává se výsledek.

Zákazník má chápat:

1. Bezplatný předverdikt ukáže základní směr.
2. Plná diagnóza za 199 Kč včetně DPH je objednávka výsledku.
3. Po zaplacení dostane plnou diagnózu na e-mail.
4. Odemykací kód/token slouží jen k okamžitému zobrazení výsledku v aplikaci.

### Text pro Stripe děkovací stránku MVP

```text
Děkujeme za objednávku.

Plnou diagnózu k vašemu autu vám pošleme na e-mail uvedený v objednávce.
Obvykle do 15 minut, nejpozději do 24 hodin.

Pokud chcete výsledek zobrazit hned v aplikaci, použijte tento odemykací kód:
[KÓD]
```

U automatické verze místo pevného kódu poslat jednorázový token navázaný na `lead_id`.

### Další automatizační krok

Google Apps Script webhook pro Stripe:

1. Přijme událost zaplacení.
2. Najde `lead_id` z `client_reference_id`.
3. Vygeneruje plnou diagnózu přes OpenAI nebo označí objednávku ke zpracování.
4. Vygeneruje `unlock_token`.
5. Nastaví `expires_at = now + 60 min`.
6. Zapíše token a výsledek / stav do Sheetu.
7. Pošle e-mail zákazníkovi.
8. Streamlit ověří token přes Apps Script a odemkne výstup jen pro daný `lead_id`.

Streamlit už počítá s `UNLOCK_VERIFY_URL`. Pokud je nastavené, nepoužije statický `ACCESS_CODE`,
ale pošle `lead_id + token` do Apps Scriptu a čeká odpověď `{ "valid": true }`.
