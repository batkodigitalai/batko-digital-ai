# Podmínky aukce a způsob potvrzení
## BATKO.DIGITAL.AI | Ing. Jaroslav Batko-Linet | IČO 14600153 | DIČ CZ5912280418

---

## 1. CO JE TATO AUKCE

Aukce pořádaná prostřednictvím BATKO.DIGITAL.AI **není veřejná dražba** ve smyslu zákona č. 26/2000 Sb. Je to **nezávazný průzkum tržní ceny** formou časově omezené online nabídky.

- Výsledek aukce **nezakládá právní závazek** ani kupujícímu, ani prodávajícímu
- Slouží k zjištění reálné tržní ochoty koupit a prodat za konkrétní cenu
- Případný prodej se uskuteční **přímou dohodou** mezi prodávajícím a kupujícím na základě kontaktů předaných zprostředkovatelem

---

## 2. PODMÍNKY PRO PRODÁVAJÍCÍHO

### Práva prodávajícího:
- Stanovit minimální cenu pod kterou prodej neuskuteční
- Po skončení aukce svobodně rozhodnout zda prodá za vydraženou cenu
- Kdykoli před skončením aukce požádat o zrušení (bez nároku na vrácení paušálu)

### Povinnosti prodávajícího:
- Zaplatit paušál **2 490 Kč** před spuštěním aukce (zahrnuje zpracování + 7 dní propagace)
- Poskytnout pravdivé informace o vozidle (stav, km, rok, doklady, závady)
- Stanovit minimální cenu písemně před spuštěním aukce
- **Závazek férové hry:** Pokud vydražená cena dosáhne nebo překročí stanovenou minimální cenu, prodávající se zavazuje kontaktovat vítěze a vést prodejní jednání v dobré víře. Odmítnutí jednání bez věcného důvodu je porušením těchto podmínek — zprostředkovatel si vyhrazuje právo neuveřejnit další aukce tohoto prodávajícího.
- **Žádné další poplatky zprostředkovateli** — výsledek prodeje a jeho cena jsou věcí prodávajícího a kupujícího

### Volitelné příplatky:
- **+1 000 Kč** — prodloužení aukce o dalších 7 dní
- **+990 Kč** — boosted propagace (navýšení rozpočtu na reklamu)

### Cena pro prodávajícího — přehled:
| Co platí | Cena | Kdy |
|---|---|---|
| Zpracování + 7 dní propagace | 2 490 Kč | Předem, vždy |
| Prodloužení aukce (volitelné) | +1 000 Kč | Před prodloužením |
| Boosted reklama (volitelné) | +990 Kč | Předem |
| Procento z prodeje | 0 Kč | Nikdy |

---

## 3. PODMÍNKY PRO KUPUJÍCÍHO

### Práva kupujícího:
- Přihodit libovolnou částku nad minimální příhoz
- Po skončení aukce svobodně rozhodnout zda za vydraženou cenu skutečně koupí
- Získat přímý kontakt na prodávajícího při výhře v aukci

### Povinnosti kupujícího:
- Uvést pravdivé kontaktní údaje (jméno, e-mail, telefon)
- Při výhře v aukci reagovat na kontakt zprostředkovatele do **48 hodin**
- **Závazek férové hry:** Příhoz vyjadřuje skutečný zájem o koupi za danou cenu. Opakované přihazování bez zájmu o koupi (spekulativní příhozy) je porušením podmínek a může vést k zablokování přístupu.
- Registrace a přihazování je **zdarma**

---

## 4. ROLE ZPROSTŘEDKOVATELE (BATKO.DIGITAL.AI)

- Organizuje a technicky provozuje aukci
- Zajišťuje propagaci (Facebook, Instagram, LinkedIn, e-mail databáze)
- **Neručí** za to že prodávající prodá nebo že kupující koupí
- **Neúčastní se** finančního vypořádání mezi stranami
- Předá kontaktní údaje vítěze prodávajícímu po skončení aukce
- Zpracovává osobní údaje v souladu s GDPR (Nařízení EU 2016/679)

---

## 5. JAK PODMÍNKY POTVRDIT — PRAKTICKÝ POSTUP

### A) PRODÁVAJÍCÍ — potvrzení před spuštěním aukce

**Krok 1 — E-mail s přihláškou**
Prodávající pošle e-mail na batko.digital.ai@gmail.com s předmětem:
`AUKCE PŘIHLÁŠKA — [značka auta] — [rok] — [SPZ nebo VIN]`

E-mail musí obsahovat:
- Jméno, telefon, e-mail
- Popis vozidla (značka, model, rok, km, stav, hlavní závady)
- **Minimální cena** (číselně)
- Větu: *"Souhlasím s podmínkami aukce BATKO.DIGITAL.AI a zavazuji se k férovému jednání při dosažení minimální ceny."*

**Krok 2 — Potvrzení zpětným e-mailem**
Zprostředkovatel odpoví e-mailem s:
- Potvrzením přijetí přihlášky
- Rekapitulací podmínek a minimální ceny
- Platebními údaji pro paušál 2 490 Kč

**Krok 3 — Platba paušálu**
Po přijetí platby se aukce spustí.

---

### B) KUPUJÍCÍ — potvrzení při registraci a přihazování

**Při registraci (buyer_registration.html):**
- Checkbox: *"Beru na vědomí, že registrace je nezávazná a slouží k zasílání upozornění na aukce."*

**Při přihazování (aukční stránka):**
- Checkbox: *"Rozumím, že příhoz vyjadřuje můj zájem o koupi za tuto cenu. Aukce není závazná smlouva — k prodeji dojde na základě přímé dohody s prodávajícím. Zavazuji se jednat v dobré víře."*
- Toto potvrzení je již implementováno v aukčních stránkách.

---

## 6. ARCHIVACE POTVRZENÍ

| Dokument | Kde se ukládá |
|---|---|
| E-mail přihláška prodávajícího | Gmail vlákno, štítek AUKCE-PRODAVAJICI |
| Potvrzovací e-mail zprostředkovatele | Gmail, stejné vlákno |
| Doklad o platbě paušálu | Gmail / Google Drive složka AUTO_LEADS_PODKLADY |
| Záznamy příhozů kupujících | Firebase databáze + Google Sheet |
| Předání kontaktu vítězi | E-mail, archivovat do Gmailu |

---

## 7. AKTUALIZACE SOCIAL MEDIA TEXTŮ — klíčové věty k přidání

### Do postů pro PRODÁVAJÍCÍ přidat:
```
Pokud vydražená cena dosáhne vašeho minima, zavazujete se jednat 
s kupujícím v dobré víře. Ne prodat za každou cenu — 
ale vést skutečné jednání.
```

### Do postů pro KUPUJÍCÍ přidat:
```
Příhoz = zájem, ne závazek. Pokud vyhrajete a prodávající souhlasí,
dostanete jeho kontakt přímo. Žádný prostředník při samotném prodeji.
```

### Do podmínek na aukční stránce přidat (checkbox kupujícího):
```
Rozumím, že aukce slouží ke zjištění tržní ceny. Příhoz není 
závazná objednávka. K prodeji dojde přímou dohodou stran.
Zavazuji se jednat v dobré víře.
```

---

## 8. SHRNUTÍ — CO KDO PODEPISUJE / POTVRZUJE

| Strana | Způsob potvrzení | Závaznost |
|---|---|---|
| Prodávající | E-mail s větou souhlasu + platba paušálu | Morální + férovost, ne právní |
| Kupující | Checkbox při registraci + checkbox při příhozu | Morální + férovost, ne právní |
| Zprostředkovatel | Potvrzovací e-mail prodávajícímu | Závazek organizace a propagace |

**Právní závaznost prodeje vzniká až přímou dohodou prodávajícího a kupujícího — mimo platformu.**
