# 📘 Landing Page Playbook — batko.digital.ai

Postup pro vytvoření a publikování landing page pro **každý další vůz**. Cíl: **co nejméně tokenů, co nejvíce úspěšných výstupů, učení manuálních dovedností.**

Vytvořeno po prvním úspěšném dovozu: Mercedes-Benz GLC 300d (17. 5\. 2026).

---

## 🤖 1\. Doporučení modelu

| Model | Cena/M tokenů | Vhodný pro |
| :---- | :---- | :---- |
| **Sonnet** | \~$3 / $15 | **DEFAULT.** Generování souborů, úpravy textu, computer-use orchestrace, push na GitHub. **5× levnější než Opus** a u rutinního landing page workflow nepoznáš rozdíl. |
| Opus | \~$15 / $75 | Jen na **strategické momenty** — pivot v positioning, nový design system, řešení složitých chyb. Tady jsem byl Opus protože jsme stavěli template, teď už ho máš. |
| Haiku | \~$0.25 / $1.25 | **Nepoužívej** na tuhle práci. Je rychlý a levný, ale slabý na strategický push-back. Bude jen souhlasit a páchat „kompletní skriptování". |

**Praktické pravidlo:** spusť novou session v **Sonnet**. Pokud po 3–4 promptech cítíš, že to drhne (chybné interpretace, zacyklení), přepni do Opus na ten konkrétní problém, pak zpátky.

---

## 💰 2\. Token economy — principy

**Nepálíme tokeny na:**

- ❌ Opakované vysvětlování principů VIP Model 1 — máš to v tomto playbooku, pošli ho jako kontext.  
- ❌ Strategické debaty „jakou cestou" — rozhodnuto, viz `## 3. Pevná rozhodnutí`.  
- ❌ Recreate souborů od nuly — kopíruj `40_OUTPUT/mercedes-glc-landing/` jako template.  
- ❌ Vícenásobné iterace textů v chatu — udělej draft jednou, doladíš commit-em.  
- ❌ Opus pro generování HTML — to umí Sonnet.

**Pálíme tokeny smysluplně na:**

- ✅ Reálná data nového vozu (HTML/PDF/text z OPENLANE/DAT) — jednorázový vstup  
- ✅ Tvoje schválení/úpravy  
- ✅ Git push přes computer-use (máš `deploy-mercedes.bat` jako template)

---

## 🔒 3\. Pevná rozhodnutí (nepřehodnocovat)

Toto je tvůj brand a obchodní model. Příští Claude to **nesmí znovu řešit** — pošli mu tenhle playbook jako kontext.

| Co | Hodnota |
| :---- | :---- |
| **Repo** | `github.com/batkodigitalai/batko-digital-ai` |
| **Lokální clone** | `C:\Users\tomas\projekty\batko-digital-ai` |
| **Cesta pro landing pages** | `40_OUTPUT/[slug]/` |
| **URL pattern** | `https://batkodigitalai.github.io/batko-digital-ai/40_OUTPUT/[slug]/` |
| **Kurz EUR→CZK** | **24,5** (přepočet listové ceny pro orientaci) |
| **Prodejní model** | Single-channel direct sale, **VIP Model 1**, pevná konečná cena včetně 21% DPH |
| **Pillars** | (1) pevná cena · (2) přenos rizika · (3) all-inclusive · (4) radikální transparentnost |
| **Tech stack** | Vanilla HTML/CSS/JS, žádné frameworky |
| **CSS tokens** | `--primary: #00a3e0`, `--secondary: #1a1a1a`, `--accent: #ffd700` |
| **Responsive breakpoints** | 768 px, 480 px |
| **Transparentnost** | Všechny vady z DAT reportu **explicitně přiznat**. Cebia až po dovozu, ne sliby. `1. majitel` jen pokud neprůstřelně ověřeno. |
| **Origin data zdroj** | `autoDATAexperts (DAT databáze)` |
| **Kontakt** | Ing. Jaroslav Batko-Linet · \+420 725 360 151 · `batko.digital.ai@gmail.com` |
| **Firma** | IČ 14600153 · DIČ CZ5912280418 · Lískovec 170, 273 51 Velké Přítočno |
| **Social** | LinkedIn (`/in/jaroslav-batko-83a4aa62`, `/company/batko-digital-ai`), IG `batko.digital.ai`, FB (`jaroslav.batko`, `batkodigitalai`) |
| **Calendly** | `https://calendly.com/batko-digital-ai` |

---

## 🚀 4\. Workflow AUTOMATIZOVANÝ — pro budoucí Claude session

### Co dodáš do nového chatu

1. **Tento playbook** (zkopíruj ho jako první message).  
2. **Data o vozu** — kopíruj z OPENLANE/autoDATAexperts (HTML export nebo PDF report), GPT/Perplexity output. Hlavně:  
   - VIN, model, motor, výkon, registrace, najeto, HU  
   - Vady z reportu  
   - Gross list price (€)  
3. **Tvoje sale price** v Kč včetně 21 % DPH.  
4. **Slug pro URL** — krátký, latinka, pomlčky. Např. `bmw-x5-m50d-2024` nebo `audi-q7-50tdi-2023`.

### Pak řekneš Claude:

*„Mám nové auto pro landing page. Postupuj podle Landing Page Playbooku (přiložen výše). Data o vozu: \[…\]. Sale price: X Kč. Slug: \[slug\]. Vytvoř soubory, pushni do `40_OUTPUT/[slug]/` a publikuj přes Pages."*

### Co Claude udělá (a co od tebe potřebuje)

| Krok | Kdo | Tvoje akce |
| :---- | :---- | :---- |
| Zkopíruje mercedes-glc-landing jako template | Claude | — |
| Nahradí data (titulek, specs, cena, transparentnost, slug) | Claude | — |
| Vytvoří `deploy-[slug].bat` přizpůsobený pro nový slug | Claude | — |
| Pushne přes computer-use | Claude | **Dvojklik na .bat \+ Enter v cmd** (\~10 s) |
| Otevře finální URL v prohlížeči | Claude | — |
| Verifikuje že stránka loaduje | Claude | — |

**Tvůj reálný čas: 5–10 minut** (data input \+ 1× Enter \+ vizuální kontrola).

---

## 🎓 5\. Workflow MANUÁLNÍ — pro tvoje učení

Zkus to **jednou ručně bez Claude** pro každé 3\. auto. Naučíš se to.

### A. Připrav data (5 min)

Zkopíruj data z OPENLANE/DAT reportu. Spočítej cenu.

### B. Zkopíruj template (1 min)

1. Otevři Průzkumník souborů.  
2. Jdi do `C:\Users\tomas\projekty\batko-digital-ai\40_OUTPUT\`.  
3. Pravým klikem na `mercedes-glc-landing` → **Kopírovat** (Ctrl+C).  
4. Pravým klikem na prázdné místo ve `40_OUTPUT` → **Vložit** (Ctrl+V).  
5. Vznikne `mercedes-glc-landing - Kopie` — přejmenuj na nový slug (např. `bmw-x5-m50d-2024`).

### C. Uprav soubory (15–30 min)

Otevři `index.html` v **Poznámkovém bloku** nebo **VS Code** (lepší). Najdi a nahraď:

- `Mercedes-Benz GLC 300d` → název nového vozu  
- `17 160 km` → nový km stav  
- `09/2025` → nová registrace  
- `270 k` → nový výkon  
- `W1NKM0HB3TF430120` → nový VIN  
- `1 307 233` → nová cena  
- `Pravé přední dveře — povrchový škrábanec` → reálné vady nového vozu (nebo smazat celou trans-warn kartu pokud bez vad)

Stejně tak `README.md` (klíčová data \+ URL slug v deploymentu).

### D. Commit a push (5 min) — postup v Příkazovém řádku

Otevři `Příkazový řádek` (cmd) a postupně napiš:

cd /d "C:\\Users\\tomas\\projekty\\batko-digital-ai"

git pull

git add 40\_OUTPUT/\[slug\]/

git commit \-m "feat: \[Vozidlo\] landing page"

git push

**Co každý řádek dělá:**

- `cd /d "..."` → přepnutí do složky repo  
- `git pull` → stáhnout poslední změny z GitHubu (důležité\!)  
- `git add ...` → zařadit nové soubory ke commitu  
- `git commit -m "..."` → zaznamenat změnu s popisem  
- `git push` → poslat na GitHub (může vyskočit prohlížeč na auth — klikni „Sign in with browser")

### E. Otevři finální URL

https://batkodigitalai.github.io/batko-digital-ai/40\_OUTPUT/\[slug\]/

Pages už je zapnuté — stačí čekat 1–2 min po push a stránka jede.

---

## 🔁 6\. Šablona promptu pro novou session (zkopíruj do nového chatu)

KONTEXT: Posílám Landing Page Playbook. Postupuj přesně podle něj.

\[zkopíruj sem celý LANDING-PAGE-PLAYBOOK.md\]

NOVÝ ÚKOL:

\- Auto: \[název modelu\]

\- Data: \[paste z OPENLANE / DAT / Perplexity / GPT output\]

\- Sale price: \[X\] Kč včetně 21 % DPH

\- Slug: \[latinka-s-pomlckami\]

\- Vady: \[seznam nebo "bez vad podle reportu"\]

\- Fotky: \[yes / no — pokud yes, kde\]

CÍL: vytvoř soubory v 40\_OUTPUT/\[slug\]/, pushni na GitHub, ověř Pages URL.

POZNÁMKA: jsem absolutní laik na Git, vysvětluj kroky, vytvoř .bat soubor 

pro deployment, dvojklikem to provedu sám.

MODEL: Sonnet (Opus jen pokud něco zásadního drhne).

---

## ⚠️ 7\. Známé limity / TODO pro všechny landing pages

1. **Formulář neodesílá data.** Pro produkci napojit Formspree:  
     
   - Free tier: 50 odeslání/měsíc zdarma  
   - Setup: [https://formspree.io](https://formspree.io) → nový formulář → cílový e-mail `batko.digital.ai@gmail.com` → dostaneš endpoint URL → vložit do `script.js` jako `fetch(URL, ...)`  
   - Pak je to **jednou nastavené pro všechny budoucí landing pages**.

   

2. **Calendly URL** — ověř jednou provždy přesnou URL a aktualizuj v `mercedes-glc-landing` template. Pak ji budou všechny další stránky dědit.  
     
3. **Cebia report** — proces: po dovozu auta do ČR uděláš Cebia kontrolu, PDF nahraješ do `50_ASSETS/cebia/[VIN].pdf` a v `index.html` daného auta přidáš `<a href="/50_ASSETS/cebia/...pdf">Cebia report PDF</a>`.  
     
4. **Fotky** — proces: po detailingu si nafotíš/vyrenderuješ. Pojmenuj `01.jpg` až `06.jpg`. Vlož do složky `40_OUTPUT/[slug]/img/`. V `index.html` přepíšeš `<div class="gallery-item">Foto N — ...</div>` na `<img src="img/01.jpg" alt="...">`.  
     
5. **OG image** — pro hezké náhledy na sociálních sítích. 1200×630 px JPG.

---

## 📊 8\. Co tohle všechno stojí v praxi

**První landing page (Mercedes GLC — 17\. 5\. 2026):**

- \~3 hodiny session, Opus model  
- \~$15–25 v tokenech (odhad)  
- Vytvořeno: template, deploy.bat, Pages workflow, brand pravidla

**Druhá landing page (s tímto playbookem):**

- \~30 minut session, Sonnet model  
- \~$1–3 v tokenech  
- Hotový postup, jen substituce dat

**Desátá landing page:**

- \~10 minut session  
- \< $1 v tokenech  
- Skoro mechanika.

---

*Konec playbooku. Ulož si tenhle soubor, je tvoje SOP.*  
