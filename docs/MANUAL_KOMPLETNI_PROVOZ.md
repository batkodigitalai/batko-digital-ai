# KOMPLETNÍ PROVOZNÍ MANUÁL — Forenzní rozhodovací audit vozu
_Batko Digital AI | Ing. Jaroslav Batko-Linet | IČ 14600153_
_Verze: 2026-05-29 — platný pro samostatný provoz bez zaměstnanců_

---

## JAK ČÍST TENTO MANUÁL

Manuál je rozdělený do 7 fází. Sleduj je v pořadí.
Každý krok říká: CO dělá zákazník / CO děláš ty / JAK DLOUHO / KOLIK Kč.
Na konci každé fáze je finanční rekapitulace.
Simulace vychází z reálného inzerátu na Sauto.cz (data z května 2026).

Aktualizace 2026-06-06: u konkretniho Sauto inzeratu nejdriv overit detail pres
`https://www.sauto.cz/api/v1/items/{sauto_id}`. Z detailu brat cenu, km, VIN, datumy,
prodejce a obrazky. Tvrzeni o stari inzeratu nebo DPH rezimu nepouzivat, pokud nejsou v detailu
overena. Fotky pro ukazku/aukci ukladat lokalne s refererem Sauto detailu, nehotlinkovat CDN.

---
---

# FÁZE 0 — JEDNOU NASTAVIT, NEŽ PŘIJDE PRVNÍ ZÁKAZNÍK

_Čas: 2–3 hodiny. Bez tohoto kroku nelze přijímat platby ani zakázky._

## 0-A — Co musíš mít připravené

| Co | Proč | Kde |
|---|---|---|
| Číslo účtu pro příjem plateb | zákazník musí mít kam poslat | Raiffeisenbank: 7236159001/5500 |
| WhatsApp na +420 725 360 151 | hlavní komunikační kanál | nainstalovaný v telefonu |
| E-mail batko.digital.ai@gmail.com | záloha komunikace, zasílání PDF | Gmail |
| Přístup na kontrolatachometru.cz | bezplatný tachometr a STK | prohlížeč, bez registrace |
| Přístup na isir.justice.cz | insolvenční rejstřík, zdarma | prohlížeč, bez registrace |
| Účet na Cebia.cz (cz.cebia.com) | placené VIN reporty pro Hloubkový audit | registrace zdarma, platba za report |
| Přístup na Sauto.cz a TipCars.cz | tržní srovnání, zdarma | prohlížeč |
| Přístup na dataovozidlech.cz | technická data VIN, zdarma | prohlížeč |
| Šablona zákaznické zprávy | rychlé odeslání odpovědi | viz Vzor 01 a 03 v složce vzory/ |

## 0-B — Inzerát na Bazoši (5 minut, zdarma)

1. Jdi na auto.bazos.cz → Přidat inzerát → kategorie Ostatní služby
2. Nadpis: `Prověření ojetého auta před koupí — 790 Kč, do 2 hodin`
3. Text: zkopíruj TEXT 1 ze souboru `vzory/VZOR_04_PRODEJNI_TEXTY.md`
4. Kontakt: +420 725 360 151
5. Uložit. Hotovo.

## 0-C — Příspěvek na Facebooku (10 minut, zdarma)

1. Přihlas se na Facebook → vyhledej skupiny: "Koupím auto ČR", "Ojeté auto ČR", "Autobazar ČR"
2. Vstup do skupiny → Přidat příspěvek
3. Text: zkopíruj TEXT 2 ze souboru `vzory/VZOR_04_PRODEJNI_TEXTY.md`
4. Opakovat max. 1× týdně ve stejných skupinách (spam filtr)

**Po dokončení Fáze 0:**
Náklady: 0 Kč
Čas: ~3 hodiny (nastavení) + 15 minut (inzeráty)
Výsledek: jsi připravený přijmout první zakázku

---
---

# FÁZE 1 — ZÁKAZNÍK PÍŠE (příchozí poptávka)

## Reálný inzerát, na základě kterého zákazník kontaktuje

```
SAUTO.CZ — inzerát č. 19 284 731 (reálná data, květen 2026)

Škoda Octavia Combi 1.6 TDI, 2018, 165 800 km
Cena: 209 000 Kč
Prodávající: soukromá osoba (Pavel K., Brno-Jih)
Stav: ojetý, 2. majitel dle TP
Výbava: Ambition, manuální převodovka, navigace, adaptivní tempomat
STK: 04/2027
Servisní knížka: ano (dle inzerátu)
Popis: "Auto bez havárií, servisovaný v autorizovaném servisu, nekuřácké."
Fotky: 12 kusů (exteriér, interiér, motor, TP, STK)
```

---

## Průběh Fáze 1 — minutu po minutě

**PONDĚLÍ 08:14**
Zákazník (Radek Šimánek, Praha 9) vidí tvůj inzerát na Bazoši.
Píše WhatsApp:

> _"Dobrý den, mám zájem o prověření. Sauto inzerát Octavia 2018,
> link: sauto.cz/os/19284731. VIN mi prodávající zaslal: TMBEG7NE5J0165803.
> Chci vědět jestli to stojí za cestu do Brna, říkají tam že má servisní knížku.
> Co to stojí a jak funguje?"_

---

**PONDĚLÍ 08:20 — TVŮJ KROK**
Čteš zprávu. Spustíš:
→ `PROMPTY_FORENZNI_AUDIT_VOZU.md` → **PROMPT 4 — ZPRACOVÁNÍ POPTÁVKY**

Vložíš text zprávy jako vstup. AI za ~2 minuty připraví:
1. Vypsaná data zákazníka
2. Návrh odpovědi
3. Řádek pro evidenci

Zkontrololuješ, schválíš, odesíláš WhatsApp.

---

**PONDĚLÍ 08:23 — ZÁKAZNÍK DOSTANE:**

> _Dobrý den Radku,_
>
> _přijato. Prověřím VIN, tachometr, záznamy STK, právní stav prodávajícího_
> _a cenu vůči trhu — a řeknu: JET nebo NEJET + proč._
>
> _**Rychlý předfiltr: 790 Kč, dodám do 2 hodin od platby** (Po–Pá 8–18 hod.)._
> _Objednávky po 18:00 zpracovávám od 8:00 dalšího pracovního dne._
>
> _Platba:_
> _Číslo účtu: 7236159001/5500_
> _Variabilní symbol: TMBEG7NE5J0165803_
> _Poznámka: Šimánek Octavia_
>
> _Ing. Jaroslav Batko-Linet | Batko Digital AI | +420 725 360 151_

---

**PONDĚLÍ 08:31**
Zákazník odpoví:
> _"OK, platím hned."_

**PONDĚLÍ 08:44**
Platba 790 Kč připsána na účet.
_(Raiffeisenbank odesílá SMS notifikaci nebo zkontroluj výpis v internetovém bankovnictví.)_

---

**Fáze 1 — rekapitulace**
| | |
|---|---|
| Tvůj čas | 8 minut |
| Příchozí platba | +790 Kč |
| Náklady | 0 Kč |

---
---

# FÁZE 2 — ZPRACOVÁNÍ ZAKÁZKY (Rychlý předfiltr)

## Průběh Fáze 2 — krok po kroku

**PONDĚLÍ 08:45 — zahájení**
Platba připsána. Otevři si:
- Záložka 1: kontrolatachometru.cz
- Záložka 2: isir.justice.cz
- Záložka 3: sauto.cz (inzerát č. 19284731)
- Záložka 4: sauto.cz/vyhledávání (pro tržní srovnání)
- Záložka 5: dataovozidlech.cz

Spustíš:
→ `PROMPTY_FORENZNI_AUDIT_VOZU.md` → **PROMPT 1 — PROVEDENÍ AUDITU**

Vyplníš vstup:
```
VIN: TMBEG7NE5J0165803
Inzerát: Škoda Octavia Combi 1.6 TDI, 2018, 165 800 km, 209 000 Kč, soukromník, Brno
Balíček: Rychlý předfiltr
Účel: soukromý
Dokumenty: žádné (zákazník nedodal TP ani faktury)
```

---

**PONDĚLÍ 08:46 — TACHOMETR A STK (5 minut)**

Jdi na kontrolatachometru.cz → zadej VIN: TMBEG7NE5J0165803

_Výsledek (simulovaný reálně):_
| Datum | km | Zdroj |
|---|---|---|
| 06/2019 | 12 400 | registrace |
| 11/2020 | 54 200 | STK |
| 03/2022 | 98 700 | STK |
| 09/2023 | 134 900 | STK |
| 04/2025 | 165 800 | STK |

✅ Průběh konzistentní, ~26 000 km/rok — odpovídá průměrnému řidiči.
✅ Poslední STK duben 2025, platná do 04/2027.
Bez zaznamenaných závad (závady by byly viditelné v záznamu STK).

---

**PONDĚLÍ 08:51 — INSOLVENČNÍ REJSTŘÍK (3 minuty)**

Jdi na isir.justice.cz → záložka "Dlužníci" → zadej jméno prodávajícího
_(jméno zjistíš z inzerátu nebo požádej zákazníka, aby si ho od prodávajícího ověřil)_

_Pokud jméno neznáš: zapiš do výstupu "NEZJIŠTĚNO — zákazník neposkytl jméno prodávajícího."_

Simulovaný výsledek: Pavel K., Brno → **žádný záznam** ✅

---

**PONDĚLÍ 08:54 — TRŽNÍ SROVNÁNÍ (15 minut)**

Jdi na sauto.cz → Škoda Octavia → filtry:
- Palivo: nafta
- Rok: 2017–2019
- Najeté km: do 200 000
- Cena: 150 000–250 000 Kč
- Karoserie: kombi
- Prodávající: soukromník

Zapiš 5 srovnatelných inzerátů:

| # | Rok | km | Cena | Prodávající | Kraj |
|---|---|---|---|---|---|
| 1 | 2018 | 152 822 | 185 000 Kč | soukromník | Praha |
| 2 | 2018 | 171 400 | 195 000 Kč | soukromník | Jihomoravský |
| 3 | 2018 | 144 900 | 210 000 Kč | soukromník | Středočeský |
| 4 | 2018 | 188 956 | 198 000 Kč | soukromník | Praha |
| 5 | 2019 | 131 200 | 229 000 Kč | soukromník | Olomoucký |

Medián: ~198 000 Kč
Inzerovaná cena: 209 000 Kč → **+11 000 Kč nad mediánem** ⚠️

---

**PONDĚLÍ 09:05 — TECHNICKÉ RIZIKO Z DAT (10 minut)**

Motor 1.6 TDI CAYC (typický pro Octavii 2018) — známé problémy:
- DPF (filtr pevných částic): zanáší se při krátkých jízdách ve městě → čištění 3 000–8 000 Kč, výměna 15 000–25 000 Kč
- Rozvodový řemen: doporučená výměna do 210 000 km nebo 5 let od poslední výměny → blíží se
- Klimatizace: bez záznamu, pozorovat při prohlídce
- Manuální převodovka: bez zvláštního rizika

Servisní evidence: NEZJIŠTĚNO — zákazník neposkytl faktury

---

**PONDĚLÍ 09:15 — SESTAVENÍ VÝSTUPU**

Spustíš:
→ `PROMPTY_FORENZNI_AUDIT_VOZU.md` → **PROMPT 2 — SESTAVENÍ ZPRÁVY**

Vložíš výsledky auditu jako vstup.
AI za ~3 minuty připraví čistý zákaznický text (viz Vzor 03).

---

**PONDĚLÍ 09:20 — ODESLÁNÍ ZÁKAZNÍKOVI**

Zkopíruješ výsledný text → odesíláš WhatsApp zákazníkovi Radkovi.

---

**Fáze 2 — rekapitulace**
| | |
|---|---|
| Celkový čas zpracování | ~35 minut |
| Použité nástroje | kontrolatachometru.cz (zdarma), isir.justice.cz (zdarma), sauto.cz (zdarma) |
| Variabilní náklady | 0 Kč |
| Příspěvek z této zakázky | +790 Kč |

---
---

# FÁZE 3 — ZÁKAZNÍK DOSTANE VÝSLEDEK

## Co zákazník obdrží (přesný text — WhatsApp)

---

> **BATKO DIGITAL AI — Rychlý předfiltr vozu**
> Ing. Jaroslav Batko-Linet | IČ 14600153
>
> **Vůz:** Škoda Octavia Combi 1.6 TDI, 2018, 165 800 km, Brno
> **Prověřeno:** 29. 5. 2026
> **Skóre rizika:** 41 / 100 `[████░░░░░░]`
>
> ---
>
> ## ⚠️ VERDIKT: ZVÁŽIT
> **Jet pouze za splnění podmínky — viz níže.**
>
> ---
>
> **Co jsem zjistil:**
>
> ✅ **Tachometr je v pořádku**
> 5 záznamů v databázi MD, průběh konzistentní (~26 000 km/rok).
> STK platná do 04/2027, bez zaznamenaných závad.
>
> ⚠️ **Cena je 11 000 Kč nad středem trhu**
> Srovnal jsem 5 podobných vozidel — cenové pásmo 185 000–229 000 Kč,
> střed trhu ~198 000 Kč. Prostor pro vyjednávání: navrhujte 193 000–197 000 Kč.
>
> ⚠️ **Předvídatelné náklady po koupi — rezervujte 15 000–35 000 Kč**
> → Rozvodový řemen (blíží se výměna): 8 000–12 000 Kč práce + díly
> → DPF filtr: riziko zanášení — čištění 3 000–8 000 Kč, výměna až 25 000 Kč
>
> ⚠️ **Záznamy poškození a počet vlastníků nebyly prověřeny**
> (Cebia report není součástí Rychlého předfiltru — je součástí Hloubkového auditu)
>
> ---
>
> **Podmínka pro cestu:**
> Požádejte prodávajícího, aby před vaší návštěvou zaslal servisní faktury
> nebo výpis z digitální servisní knížky. Pokud odmítne → nedoporučuji jet.
>
> **Co se zeptat při prohlídce:**
> → "Kdy byl naposledy vyměněn rozvodový řemen a napínák?"
> → "Jezdíte převážně dálnice nebo město?" (DPF indikátor)
> → "Mohu vidět servisní faktury?"
>
> ---
>
> _Tato zpráva je analytickým podkladem. Nenahrazuje fyzickou prohlídku._
> _Batko Digital AI | IČ 14600153 | batko.digital.ai@gmail.com_

---

## Co se stane dál — 3 možné scénáře

### Scénář A — zákazník chce hloubkový audit (nejčastější)

**PONDĚLÍ 09:35**
Zákazník odpoví:
> _"Super, díky. Prodávající mi faktury zaslal — vypadá to OK.
> Ale chci ještě ten plný audit s Cebií, ať vím o historii škod. Co to stojí?"_

Ty odpovíš:
> _"Hloubkový audit s Cebia reportem, záznamy škod, počtem vlastníků
> a ekonomickou kalkulací je 3 490 Kč. Dodám do 24 pracovních hodin.
> Stejný účet, variabilní symbol: TMBEG7NE5J0165803-2."_

**PONDĚLÍ 10:02**
Zákazník posílá 3 490 Kč. → Přechod na FÁZI 4.

---

### Scénář B — zákazník říká "díky, jedu se podívat"

Odpovíš:
> _"Dobře. Pokud budete chtít ještě před podpisem smlouvy plný audit
> (záznamy poškození, ekonomiku, checklist smlouvy), dejte vědět — 3 490 Kč._
> _Přeji hodně štěstí při prohlídce!"_

_Zákazník může objednat Hloubkový audit i po prohlídce — před podpisem smlouvy._

---

### Scénář C — zákazník neodpoví nebo říká "děkuji, nepotřebuji"

Nic neděláš. Zakázka uzavřena. Příspěvek +790 Kč je tvůj.
Zákazníka nekontaktuješ znovu (spam).

---
---

# FÁZE 4 — HLOUBKOVÝ AUDIT (navazující zakázka)

_Tento krok nastane jen pokud zákazník objednal Hloubkový audit nebo Kompletní balíček._

## Průběh Fáze 4 — krok po kroku

**PONDĚLÍ 10:05 — zahájení po připsání platby 3 490 Kč**

Otevři si prohlížeč → záložky:
- Záložka 1: cz.cebia.com → přihlásit se → zakoupit report pro VIN TMBEG7NE5J0165803
- Záložka 2: exekutorskakamora.cz → CEE výpis pro jméno prodávajícího (60 Kč)
- Záložka 3: isir.justice.cz (již prověřeno — ze záznamu Fáze 2)
- Záložka 4: sauto.cz (tržní srovnání již připraveno)

---

**PONDĚLÍ 10:08 — CEBIA REPORT (10 minut + 5 minut čekání)**

cz.cebia.com → Prověřit auto → VIN TMBEG7NE5J0165803 → Zakoupit report

Cena reportu: 669 Kč (platba kartou)
Dodání: okamžitě po platbě (online report)

_Výsledek Cebia reportu (simulovaný reálně):_
- Počet zápisů do registru: 3 (ČR)
- Počet vlastníků: 2 (shoduje se s TP)
- Záznamy poškození: **1 záznam — 04/2021, lehká nehoda, přední nárazník, pojišťovna Allianz, škoda 24 800 Kč** ⚠️
- Odcizení: nenalezeno ✅
- Financování / leasing: nenalezeno ✅
- Servisní záznamy: 4 záznamy (autorizovaný servis Škoda, poslední 03/2025) ✅
- Tržní cena dle Cebia: 192 000–208 000 Kč

---

**PONDĚLÍ 10:25 — EXEKUCE PRODÁVAJÍCÍHO (5 minut, 60 Kč)**

exekutorskakamora.cz → CEE → zadat jméno + datum narození prodávajícího
_(datum narození získáš od zákazníka nebo z TP — pokud nedostupné: NEZJIŠTĚNO)_

Simulovaný výsledek: Pavel K. — **žádný záznam** ✅
Poplatek: 60 Kč

---

**PONDĚLÍ 10:30 — AKTUALIZACE SKÓRE A ANALÝZA**

Nový poznatek: nehoda v 04/2021, škoda 24 800 Kč.
To zvyšuje skóre rizika — záznamy poškození mají váhu v historii a dokumentaci.
Prodávající v inzerátu tvrdil "bez havárií" — **NESOULAD** ❌

Aktualizované skóre: **54 / 100 → stále ZVÁŽIT, ale podmínky jsou přísnější.**

---

**PONDĚLÍ 10:40 — SESTAVENÍ PDF ZPRÁVY**

Spustíš:
→ **PROMPT 2 — SESTAVENÍ ZPRÁVY**

Vložíš veškerá data. AI připraví text PDF zprávy (6–8 stran).

Zkopíruješ text do Word / Google Docs → Export jako PDF.
Uložíš jako: `audit_TMBEG7NE5J0165803_20260529.pdf`

---

**PONDĚLÍ 11:15 — ODESLÁNÍ ZÁKAZNÍKOVI**

PDF odesíláš e-mailem (batko.digital.ai@gmail.com → radek.simanek@email.cz)
Zároveň WhatsApp notifikace:

> _"Dobrý den Radku, hloubkový audit je hotový — posílám na e-mail._
> _Důležité: Cebia odhalila nehodu z dubna 2021, škoda ~25 000 Kč._
> _V inzerátu prodávající uvádí 'bez havárií' — nesoulad. Detaily v PDF."_

---

**Fáze 4 — rekapitulace**
| | |
|---|---|
| Celkový čas zpracování | ~70 minut |
| Cebia report | -669 Kč |
| CEE exekuce | -60 Kč |
| Variabilní náklady celkem | -729 Kč |
| Tržba | +3 490 Kč |
| Příspěvek z této zakázky | **+261 Kč** |

---
---

# FÁZE 5 — REAKCE ZÁKAZNÍKA A UZAVŘENÍ ZAKÁZKY

## Možné reakce po dodání hloubkového auditu

### Reakce A — zákazník chce poradit s vyjednáváním

**PONDĚLÍ 11:30**
Zákazník odpoví:
> _"Jéžišmarjá. Prodávající lhal. Mám se vůbec ozvat? Co mu říct?"_

Odepíšeš (toto je součást Kompletního balíčku — zákazník má ale jen Hloubkový):

> _"Nesoulad v inzerátu je legitimní důvod pro přehodnocení ceny._
> _Doporučuji: ozvěte se prodávajícímu, řekněte, že jste si nechali auto prověřit_
> _a Cebia ukázala nehodu z roku 2021. Navrhněte 185 000 Kč._
> _Pokud odmítne nebo začne popírat, auto nedoporučuji kupovat._
> _Pokud chcete celý skript rozhovoru a checklist kupní smlouvy,_
> _mohu doplnit jako Kompletní balíček za 1 000 Kč (doplatek k Hloubkovému auditu)."_

---

### Reakce B — zákazník říká "děkuji, odvolávám zájem"

> _"Díky moc za audit! Prodávajícímu se neozvu. Ušetřil jste mi cestu."_

Zakázka uzavřena. Zákazník spokojený. Příspěvek +261 Kč z Hloubkového auditu.
Celkový příspěvek za zákazníka Radka (předfiltr + hloubkový): **+551 Kč**

---

### Reakce C — zákazník chce vrátit peníze

> _"Nechci report, chci peníze zpět."_

Zkontroluj: Byla služba splněna (byl dodán výsledek)?
→ ANO → vrácení peněz není povinné (digitální služba byla poskytnuta)
→ NE (audit nebyl dodán) → vrátit peníze bez diskuze

Odpověď v případě splněné služby:
> _"Dobrý den, chápu vaše zklamání. Audit byl dokončen a doručen v souladu_
> _s objednávkou. Vrácení ceny za provedenou práci bohužel není možné._
> _Jsem k dispozici pro případné dotazy k obsahu zprávy."_

---
---

# FÁZE 6 — FINANČNÍ PŘEHLED CELÉ ZAKÁZKY

## Zákazník Radek — kompletní tok peněz

| Čas | Událost | Příjem | Výdaj | Zůstatek |
|---|---|---:|---:|---:|
| Po 08:44 | Platba za Rychlý předfiltr | +790 Kč | | +790 Kč |
| Po 10:02 | Platba za Hloubkový audit | +3 490 Kč | | +1 380 Kč |
| Po 10:08 | Cebia report | | -669 Kč | +711 Kč |
| Po 10:25 | CEE exekuce | | -60 Kč | +651 Kč |
| | **CELKEM** | **+1 380 Kč** | **-729 Kč** | **+651 Kč** |

Tvůj čas celkem: ~2 hodiny (35 min předfiltr + 70 min hloubkový + 15 min komunikace)
Hodinová sazba: ~325 Kč/hod.

---

## Přehled všech balíčků — co kdy platíš

| Balíček | Tržba | Cebia | CEE | Zástavy | Ostatní | Příspěvek | Tvůj čas |
|---|---:|---:|---:|---:|---:|---:|---|
| Rychlý předfiltr | 790 Kč | 0 | 0 | 0 | ~100 Kč | ~570 Kč | ~35–45 min |
| Hloubkový audit | 3 490 Kč | 669 Kč | 60 Kč | 0 | 0 | ~2 761 Kč | ~70–90 min |
| Kompletní balíček | 4 490 Kč | 669 Kč | 60 Kč | 363 Kč | 0 | ~3 398 Kč | ~120–150 min |

**Kdy koupit Cebia report:** POUZE pro Hloubkový audit a Kompletní balíček.
Pro Rychlý předfiltr NE — zákazník to ví z objednávky, je to v podmínkách.

---

## Měsíční bod zvratu

| Fixní náklady/měsíc | Potřebné zakázky |
|---|---|
| 0 Kč (jen vlastní čas) | **1 zakázka = zisk** |
| 5 000 Kč (čas + nástroje) | **~11 Rychlých předfiltrů** |
| 10 000 Kč (při rozšíření) | **~22 Rychlých předfiltrů nebo 10 Hloubkových auditů** |

---
---

# FÁZE 7 — CO SE MŮŽE POKAZIT A JAK REAGOVAT

## Problém 1 — zákazník nezaplatí po dohodě

**Situace:** Domluvili jste se, zákazník neplatí 2+ hodiny.

**Reakce:**
> _"Dobrý den, jen připomínám, že zahájím zpracování po připsání platby._
> _Pokud jste se rozhodli jinak, žádný problém — jen dejte vědět."_

Pokud neodpoví do 24 hodin → zakázku uzavři, neřeš.

---

## Problém 2 — zákazník chce výsledek "okamžitě" mimo pracovní dobu

**Situace:** zákazník platí v 22:00 a chce výsledek "dnes večer".

**Reakce:**
> _"Dobrý den, platbu jsem přijal. Zpracování probíhá v pracovní době Po–Pá 8–18 hod._
> _Výsledek odešlu zítra ráno do 10:00. Díky za pochopení."_

**Nikdy neslib výsledek mimo pracovní dobu** — budeš to pak dělat vždy.

---

## Problém 3 — VIN neexistuje nebo je nesprávný

**Situace:** zadáš VIN do kontrolatachometru.cz → žádný výsledek.

**Reakce zákazníkovi:**
> _"Dobrý den, VIN, který jste zaslal, nenachází záznam v databázi MD._
> _Požádejte prodávajícího o přepis VIN přímo z technického průkazu (VIN je vytlačen_
> _na vozidle + v TP). Jakmile mi správný VIN zašlete, zahájím zpracování."_

Cebia report nekupovat dokud VIN není ověřen.

---

## Problém 4 — Cebia report nedodá výsledek (technická chyba)

**Situace:** Cebia vrátí "nedostatečná data" nebo report je prázdný.

**Postup:** Zkus carVertical jako druhý zdroj (cena nezjištěna — prověř aktuálně na carvertical.com).
Do zprávy zákazníkovi: _"Databáze historií vozidel pro tento VIN neobsahuje záznamy._
_To může znamenat čisté auto nebo auto bez záznamu — obě možnosti jsou uvedeny v reportu."_

---

## Problém 5 — zákazník tvrdí, že výsledek je špatný

**Situace:** zákazník říká "vaše data jsou nepravdivá, tachometr nebyl stočen".

**Reakce:**
> _"Rozumím vašim obavám. Data vychází z databáze Ministerstva dopravy, nikoli z mého odhadu._
> _Pokud máte doklad, který je v rozporu se záznamy MD, doporučuji situaci prověřit přímo_
> _s prodávajícím a případně na STK stanici před koupí._
> _Výstup auditu je podklad pro rozhodnutí, ne závazný posudek."_

---
---

# PŘEHLED — CELÝ PROVOZ NA JEDNÉ STRÁNCE

```
ZÁKAZNÍK PÍŠE
  ↓
Ty: PROMPT 4 (Zpracování poptávky) → schválit → odeslat odpověď s platebními údaji
  ↓ (~8 min)
ZÁKAZNÍK PLATÍ
  ↓
Ověř platbu v internetovém bankovnictví
  ↓
SPUSŤ AUDIT:
  Rychlý předfiltr (790 Kč):
    → tachometr (kontrolatachometru.cz) + insolvenční rejstřík + tržní srovnání
    → PROMPT 1 → PROMPT 2 → WhatsApp zákazníkovi
    → čas: ~35–45 minut
    → příspěvek: ~490 Kč

  Hloubkový audit (3 490 Kč):
    → Cebia report (669 Kč) + CEE exekuce (60 Kč) + vše z předfiltru
    → PROMPT 1 → PROMPT 2 → PDF → e-mail zákazníkovi
    → čas: ~70–90 minut
    → příspěvek: ~2 761 Kč

  Kompletní balíček (4 490 Kč):
    → vše z hloubkového + Rejstřík zástav (363 Kč) + telefonická konzultace
    → PROMPT 1 → PROMPT 2 → PDF + telefonát
    → čas: ~120–150 minut
    → příspěvek: ~898 Kč
  ↓
ZÁKAZNÍK DOSTANE VÝSLEDEK
  ↓ (možné scénáře)
  A: objedná hloubkový audit → přejdi na Hloubkový audit výše
  B: jde se podívat na auto → nabídni Hloubkový audit před podpisem
  C: vzdal zájem → zakázka uzavřena
  D: chce vrácení peněz → viz Fáze 7, Problém 3
```

---

## KONTROLNÍ SEZNAM PŘED KAŽDÝM ODESLÁNÍM

- [ ] Zpráva neobsahuje C:\Users ani žádné lokální cesty
- [ ] Zpráva neobsahuje zmínku o Google Sheet, Google Drive, interních kódech
- [ ] Verdikt je jasně viditelný (KOUPIT / ZVÁŽIT / ODMÍTNOUT)
- [ ] NEZJIŠTĚNO je uvedeno u každé neprověřené položky
- [ ] Prohlášení o rozsahu je přítomné (nenahrazuje fyzickou prohlídku)
- [ ] Variabilní symbol platby odpovídá VIN zákazníka
- [ ] Platba byla skutečně připsána (zkontrolovat výpis, ne jen příslib)

---

_Batko Digital AI | IČ 14600153 | DIČ CZ5912280418 | Lískovec 170, 273 51 Velké Přítočno_
_batko.digital.ai@gmail.com | +420 725 360
