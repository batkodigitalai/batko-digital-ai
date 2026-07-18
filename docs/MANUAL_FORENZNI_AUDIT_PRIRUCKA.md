# PROVOZNÍ PŘÍRUČKA — Forenzní rozhodovací audit vozu
_Batko Digital AI | Ing. Jaroslav Batko-Linet | IČ 14600153_
_Verze: 2026-05-29_

---

## JAK ČÍST TUTO PŘÍRUČKU

Příručka sleduje jednu reálnou zakázku od začátku do konce.
Každá část říká: co dělá zákazník → co děláš ty → jak dlouho → kolik to stojí.
Na konci je shrnutí všech čísel.

Simulovaný inzerát: **Škoda Octavia Combi 1.6 TDI, 2018, 162 000 km, 209 000 Kč**
Prodávající: soukromá osoba, Brno
Odkaz: sauto.cz (simulovaný inzerát č. SA-2026-88821)
VIN: TMBEG7NE5J0123456 (simulovaný)

---

---

## ČÁST 1 — ČASOVÁ OSA CELÉ ZAKÁZKY

```
DEN 1 — PONDĚLÍ
────────────────────────────────────────────────────────
08:15  Zákazník (Petr N., Praha) posílá WhatsApp:
       "Zdravím, našel jsem Octavii na Sauto, VIN TMBEG7NE5J0123456,
        https://sauto.cz/... Chci vědět jestli to stojí za cestu.
        Kolik berete?"

08:20  Ty čteš zprávu → spustíš PROMPT 4 (ZPRACOVÁNÍ POPTÁVKY)
       → extrakce dat zákazníka (2 min)
       → připravíš návrh odpovědi a řádek pro evidenci poptávek

08:25  Předložíš návrh sobě ke schválení → schválíš → odesíláš

08:26  Zákazník dostane odpověď:
       "Dobrý den Petře, přijato. Rychlý předfiltr (ANO/NE + 3 rizika)
        za 790 Kč, dodám do 2 hod. od platby v pracovní době.
        Číslo účtu: 7236159001/5500, VS: TMBEG7NE5J0123456."

08:45  Zákazník posílá platbu 790 Kč
       (nebo: zákazník platí přes QR kód v potvrzovací zprávě)

09:00  Platba připsána → zahájení zpracování
       → spustíš PROMPT 1 (PROVEDENÍ AUDITU) — balíček Rychlý předfiltr
       → kontrola VIN, tachometr, právní registry, tržní srovnání

10:15  Audit dokončen → spustíš PROMPT 2 (SESTAVENÍ ZPRÁVY)
       → výstup: 1 strana textu pro zákazníka

10:20  Odesíláš výsledek zákazníkovi přes WhatsApp

10:22  Zákazník odpoví: "Díky! Jaký je plný audit kdyby..."
       → přirozeně nabídneš Hloubkový audit za 3 490 Kč

────────────────────────────────────────────────────────
DEN 1 — REKAPITULACE
Tvůj čas: ~45 minut
Tržba: 790 Kč
Variabilní náklady: ~100 Kč (tachometr zdarma, STK zdarma,
  insolvenční rejstřík zdarma, tržní srovnání zdarma — Cebia NEBYLA použita)
Příspěvek: ~570 Kč

────────────────────────────────────────────────────────
DEN 2 — ÚTERÝ (pokračování — zákazník objednal Hloubkový audit)

09:00  Zákazník posílá platbu 3 490 Kč
09:15  Platba připsána → zahájení zpracování
       → PROMPT 1 (PROVEDENÍ AUDITU) — balíček Hloubkový audit
       → Cebia report zakoupen (~669 Kč)
       → kontrola exekucí (60 Kč)
       → tachometr + STK (zdarma)
       → tržní srovnání 5 inzerátů (zdarma)
       → modelové vady 1.6 TDI (DPF, rozvodový řetěz)

12:30  Audit dokončen → PROMPT 2 (SESTAVENÍ ZPRÁVY)
       → PDF zpráva 7 stran

12:45  Odesíláš PDF zákazníkovi e-mailem

13:00  Zákazník potvrzuje přijetí

────────────────────────────────────────────────────────
DEN 2 — REKAPITULACE
Tvůj čas: ~90 minut
Tržba: 3 490 Kč
Variabilní náklady: ~729 Kč (Cebia 669 + exekuce 60)
Příspěvek: ~2 761 Kč

────────────────────────────────────────────────────────
CELKEM ZA ZÁKAZNÍKA PETRA (2 zakázky)
Tržba celkem: 4 280 Kč
Náklady celkem: ~812 Kč
Příspěvek celkem: ~3 468 Kč
Tvůj čas celkem: ~135 minut
```

---

---

## ČÁST 2 — VZOROVÝ VÝSTUP: PROMPT 4 — ZPRACOVÁNÍ POPTÁVKY

### Vstup (zpráva od zákazníka):
> "Zdravím, našel jsem Octavii na Sauto, VIN TMBEG7NE5J0123456,
> https://sauto.cz/inzerce/osobni/skoda/octavia/SA-2026-88821
> Chci vědět jestli to stojí za cestu do Brna. Kolik berete?"
> _— Petr Novák, tel. +420 603 XXX XXX_

---

### Výstup promptu (co ti AI připraví):

**KROK 1 — VYPSANÁ DATA ZÁKAZNÍKA**

| Položka | Hodnota |
|---|---|
| Jméno | Petr Novák |
| Telefon | +420 603 XXX XXX |
| E-mail | nezjištěno (doplnit) |
| VIN | TMBEG7NE5J0123456 |
| Odkaz na inzerát | sauto.cz/...SA-2026-88821 |
| Zájem o balíček | nespecifikováno |
| Účel koupě | soukromý (pravděpodobně) |
| Naléhavost | standardní |

**KROK 2 — DUPLICITA:** Zákazník není v evidenci. Nová poptávka.

**KROK 3 — NAVRŽENÁ ODPOVĚĎ ZÁKAZNÍKOVI**

> Dobrý den Petře,
>
> přijato. Prověřím vám VIN, tachometr, právní stav a cenu vůči trhu
> a řeknu: ANO — má cenu jet, nebo NE — neplýtvejte časem a benzínem.
>
> **Rychlý předfiltr: 790 Kč, dodám do 2 hodin od platby** (Po–Pá 8–18 hod.).
>
> Platba:
> Číslo účtu: 7236159001/5500
> Variabilní symbol: TMBEG7NE5J0123456
> Poznámka: Novák Octavia
>
> Po připsání platby zahájím zpracování.
> Případné dotazy: +420 725 360 151
>
> Ing. Jaroslav Batko-Linet | Batko Digital AI

**KROK 4 — ŘÁDEK PRO EVIDENCI POPTÁVEK (Google Sheet)**

| tlacitko | sekce | ukol | stav | schvaleni | kontakt | VIN | balicek | poznamka |
|---|---|---|---|---|---|---|---|---|
| WhatsApp | rychly_predfiltr | pripravit_audit | podklady_pripraveny | CEKA | +420603XXX | TMBEG7NE5J0123456 | predfiltr_790 | Octavia 2018 Brno |

**KROK 5 — ČEKÁM NA SCHVÁLENÍ**
⚠️ Zpráva nebyla odeslána. Schvalujete odeslání? **ANO / upravit**

---

---

## ČÁST 3 — VZOROVÝ VÝSTUP: PROMPT 1 — PROVEDENÍ AUDITU (Rychlý předfiltr)

### Vstup:
- VIN: TMBEG7NE5J0123456
- Inzerát: Škoda Octavia Combi 1.6 TDI, 2018, 162 000 km, 209 000 Kč, soukromník, Brno
- Balíček: Rychlý předfiltr

---

### Výstup promptu:

**SKÓRE RIZIKA: 41 / 100 → VERDIKT: ZVÁŽIT**

**PRÁVNÍ VRSTVA (váha 25 %)**
| Oblast | Výsledek | Hodnocení |
|---|---|---|
| Rejstřík zástav | Neprověřeno — není v ceně Rychlého předfiltru | — |
| Exekuce prodávajícího | Neprověřeno — není v ceně Rychlého předfiltru | — |
| Insolvenční rejstřík | Čistý (veřejný rejstřík, zdarma) | ✅ |
| Odcizení / financování | NEZJIŠTĚNO — Cebia nebyla zakoupena | ⚠️ |
| Shoda VIN s TP | Nelze ověřit bez fyzického průkazu | — |

_Skóre právní vrstvy: 35 / 100 (nejistota kvůli neprovedené zástavě a Cebii)_

**HISTORIE A DATA (váha 20 %)**
| Oblast | Výsledek | Hodnocení |
|---|---|---|
| Tachometr (kontrolatachometru.cz) | 3 záznamy: 87 000 km (2020), 124 000 km (2022), 162 000 km (2025) — konzistentní průběh | ✅ |
| STK záznamy | Poslední STK 03/2025, bez závad | ✅ |
| Počet majitelů | NEZJIŠTĚNO bez Cebia reportu | ⚠️ |
| Záznamy poškození | NEZJIŠTĚNO bez Cebia reportu | ⚠️ |

_Skóre historie: 30 / 100 (tachometr čistý, ale vlastníci a poškození neznámé)_

**TECHNICKÉ RIZIKO Z DAT (váha 25 %)**
| Oblast | Výsledek | Hodnocení |
|---|---|---|
| Typické závady 1.6 TDI (CAYC) | Znám problém: DPF zanášení při krátkých trasách, náhrada 15–25 tis. Kč | ⚠️ |
| Rozvodový řetěz | Motor CAYC má rozvodový řemen — výměna doporučena do 210 000 km nebo 5 let | ⚠️ |
| DSG / převodovka | Manuální 6-st. (dle inzerátu) — bez zvláštního rizika | ✅ |
| STK závady | Žádné zaznamenané | ✅ |
| Servisní evidence | NEZJIŠTĚNO — prodávající nepřiložil faktury | ⚠️ |

_Skóre technika: 50 / 100 (DPF + řemen = predikované náklady po koupi)_

**TRŽNÍ A CENOVÉ RIZIKO (váha 20 %)**
| Oblast | Výsledek | Hodnocení |
|---|---|---|
| Srovnatelné inzeráty (Sauto, TipCars) | 5 srovnatelných vozidel: 185 000–229 000 Kč | ✅ |
| Pozice inzerované ceny | 209 000 Kč = střed trhu, mírně nad mediánem (195 000 Kč) | ⚠️ |
| DPH režim | Soukromník → bez DPH, bez fakturace | ✅ |

_Skóre trh: 35 / 100 (cena mírně nad trhem, prostor pro slevu ~10–15 tis. Kč)_

**DOKUMENTACE (váha 10 %)**
| Oblast | Výsledek | Hodnocení |
|---|---|---|
| Servisní faktury | Nepřiloženy, prodávající zmiňuje "servisní knížku" | ⚠️ |
| Shoda výbavy | Dle inzerátu odpovídá základní výbavě Ambition | ✅ |

_Skóre dokumentace: 40 / 100_

---

**CELKOVÉ SKÓRE:**
```
RIZIKO = 0,25×35 + 0,20×30 + 0,25×50 + 0,20×35 + 0,10×40
       = 8,75 + 6,0 + 12,5 + 7,0 + 4,0
       = 38,25 → zaokrouhleno 38 / 100
```

**VERDIKT: ZVÁŽIT**
Tachometr je čistý, STK bez závad, insolvence čistá. Hlavní nejistoty:
záznamy poškození a vlastníci neznámé (chybí Cebia), DPF a rozvodový řemen
jsou předvídatelné náklady. Cena je 10–15 tis. Kč nad mediánem trhu.

**DOPORUČENÍ PRO ZÁKAZNÍKA:**
Na cestu jeď pouze pokud prodávající předloží servisní faktury nebo digitální
servisní knížku. Bez nich NEJET. Při prohlídce: otestovat studeným startem,
zeptat se na poslední výměnu řemene a historii DPF.

---

---

## ČÁST 4 — VZOROVÝ VÝSTUP: PROMPT 2 — SESTAVENÍ ZPRÁVY (Rychlý předfiltr)

_Toto je text, který zákazník dostane přes WhatsApp nebo e-mail._

---

> **BATKO DIGITAL AI — Rychlý předfiltr vozu**
> Ing. Jaroslav Batko-Linet | IČ 14600153 | +420 725 360 151
>
> ---
>
> **Vůz:** Škoda Octavia Combi 1.6 TDI, 2018, 162 000 km
> **Datum prověření:** 29. 5. 2026
> **Skóre rizika:** 38 / 100 `[███░░░░░░░]`
>
> ---
>
> ## ⚠️ VERDIKT: ZVÁŽIT
> **Jet pouze za podmínky — viz níže.**
>
> ---
>
> **Co jsem zjistil (3 klíčové body):**
>
> 1. ✅ **Tachometr je čistý** — 3 záznamy v databázi MD, průběh odpovídá, žádné stočení.
>
> 2. ⚠️ **Cena je ~12 000 Kč nad středem trhu** — srovnatelná auta jsou v pásmu 185 000–229 000 Kč,
>    medián ~197 000 Kč. Prostor pro slevu existuje.
>
> 3. ⚠️ **Předvídatelné náklady po koupi:**
>    - Rozvodový řemen: doporučená výměna do 210 000 km nebo 5 let (blíží se) → ~8 000–12 000 Kč
>    - DPF filtr: riziko zanášení u krátkých tras → čištění 3 000–8 000 Kč, výměna až 25 000 Kč
>
> ---
>
> **Podmínka pro cestu:**
> Požádejte prodávajícího o servisní faktury nebo výpis z digitální servisní knížky.
> Pokud odmítne nebo nemá → nedoporučuji jet.
>
> **Co se zeptat při prohlídce:**
> - "Kdy byl naposledy vyměněn rozvodový řemen?"
> - "Jezdíte převážně po dálnici nebo ve městě?" (DPF riziko)
> - "Mohu vidět servisní faktury?"
>
> ---
>
> _Tato zpráva je analytickým podkladem pro vaše rozhodnutí.
> Nenahrazuje fyzickou prohlídku vozidla._
> _Batko Digital AI | IČ 14600153 | batko.digital.ai@gmail.com_

---

---

## ČÁST 5 — VZOROVÝ VÝSTUP: PROMPT 3 — PRODEJNÍ TEXTY

### Příklad: Inzerát na Bazoši (bezplatná sekce Služby)

---

> **Kupujete ojeté auto? Zjistím předem, jestli stojí za cestu.**
>
> Než vyrazíte přes půl republiky za autem, které může být předraženou chybou —
> nechte si ho prověřit na dálku.
>
> **Co udělám:**
> Zkontroluju VIN, tachometr a záznamy STK, právní stav prodávajícího,
> cenu vůči aktuálnímu trhu a typické závady dané motorizace.
> Dostanete jasnou odpověď: **JET / NEJET + 3 hlavní důvody**.
>
> **Proč to dává smysl:**
> Fyzická prohlídka u nezávislého technika stojí 2 000–5 000 Kč.
> Špatně koupené auto může stát 30 000–150 000 Kč na opravách.
> Rychlý předfiltr za **790 Kč vám ušetří cestu za špatným autem**
> — a peníze na fyzickou prohlídku nechte na to auto, které projde prověřením.
>
> **Jak to funguje:**
> Pošlete VIN + odkaz na inzerát → dostanete výsledek do 2 hodin
> (pracovní dny 8–18 hod., objednávky mimo tuto dobu zpracovávám od 8:00 dalšího dne).
>
> **Ceník:**
> 790 Kč — Rychlý předfiltr (ANO/NE + rizika, do 2 hod.)
> 3 490 Kč — Hloubkový audit (úplná zpráva PDF + ekonomika, do 24 hod.)
> 4 490 Kč — Kompletní balíček (+ konzultace 15 min + 2 alternativy)
>
> Prověřím jedno auto nebo celý váš seznam kandidátů.
>
> **Kontakt:**
> WhatsApp / tel.: +420 725 360 151
> E-mail: batko.digital.ai@gmail.com
>
> _Nejsem bazar. Nejsem motivován auto prodat. Jsem na vaší straně._

---

---

## ČÁST 6 — FINANČNÍ PŘEHLED CELÉ ZAKÁZKY

| Položka | Rychlý předfiltr | Hloubkový audit | Kompletní balíček |
|---|---:|---:|---:|
| Cena pro zákazníka | 790 Kč | 3 490 Kč | 4 490 Kč |
| Cebia report | 0 Kč | 669 Kč | 669 Kč |
| Exekuce CEE | 0 Kč | 60 Kč | 120 Kč |
| Rejstřík zástav | 0 Kč | 0 Kč | 363 Kč |
| Ostatní (čas, data) | 100 Kč | 0 Kč | 0 Kč |
| **Variabilní náklady celkem** | **~100 Kč** | **~729 Kč** | **~1 152 Kč** |
| **Příspěvek** | **~490 Kč** | **~2 761 Kč** | **~3 338 Kč** |
| Tvůj čas (odhad) | 45 min | 90 min | 150 min |
| Hodinová sazba | ~387 Kč/hod. | ~174 Kč/hod. | ~335 Kč/hod. |

> **Poznámka k Rychlému předfiltru:** záměrně se neprovádí Cebia report
> (šetří ~669 Kč). Zákazník dostane odpověď z bezplatných zdrojů.
> Cebia se zakoupí až pro Hloubkový audit.

**Bod zvratu:**
- Při fixních nákladech 0 Kč → zisk od první zakázky
- Při fixních nákladech 5 000 Kč/měsíc → stačí 11 Rychlých předfiltrů

**Logika navazujícího prodeje:**
Zákazník Petr prošel celou cestou: Rychlý předfiltr (790 Kč) → Hloubkový audit (3 490 Kč).
Celková tržba: 1 380 Kč. Přitom zaplatil méně než jedna fyzická prohlídka u Automato (3 970 Kč).

---

## ČÁST 7 — KONTROLNÍ SEZNAM PŘED ODESLÁNÍM VÝSLEDKU

Před každým odesláním zákazníkovi zkontroluj:

- [ ] Zpráva neobsahuje lokální cesty souborů (C:\Users...)
- [ ] Zpráva neobsahuje zmínky o Google Sheet nebo Google Drive
- [ ] Zpráva neobsahuje interní kódy nebo marže
- [ ] Verdikt je jasně uveden na začátku (KOUPIT / ZVÁŽIT / ODMÍTNOUT)
- [ ] NEZJIŠTĚNO je uvedeno kurzívou u každé neprověřené položky
- [ ] Zápatí s prohlášením o rozsahu je přítomné
- [ ] Platební údaje ve zprávě souhlasí s objednávkou (správný variabilní symbol)

---

_Batko Digital AI | batko.digital.ai@gmail.com | +420 725 360 151_
_IČ 14600153 | DIČ CZ5912280418 | Lískovec 170, 273 51 Velké Přítočno_
