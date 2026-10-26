# 20261026_1139_po_prenos_monetizace_siti

## KONTEXT PROJEKTU
Výzkum, na čem tvůrci na IG/TikTok/FB/LinkedIn/Pinterest vydělávají, zúžený na to, co Ing. Jaroslav Batko umí prodat hned (obě větve: AUTO = rozbor a předvýběr aut na zakázku; FIRMA = AI audit, Shadow-AI-Check + směrnice, správa automatizací, workshopy, avatar školení, diagnostika před předáním firmy). Na to postavená automatizace publikace: tabulka → Claude generuje texty z předplatného → schválení → Apps Script exportuje konzoli PUBLIKOVAT.html + PDF → obrázky na GitHub Pages. Hlavní měřítko: počet lidí, kteří napíšou, jaké auto hledají / co je ve firmě pálí.

## ROZHODNUTÁ FAKTA
- Varianta B: texty negeneruje API, ale Claude v chatu na pokyn „generuj z VSTUPY“ (nebo naplánovaná úloha). Apps Script v tabulce je bez klíče, vložený a autorizovaný 26. 10. 09:50.
- Obrázky: `publikace/RRRRMMDD/` v repozitáři batkodigitalai/batko-digital-ai, přehled `publikace/PREHLED.md`, generátor `scripts/publikace_karta.js`. Soubory se nikdy nepřepisují. Nahrává Claude (git push ze sandboxu funguje).
- Nikdy neuvádět název aukční platformy (jen „evropská aukce“); u aut částky v Kč i €; nic nepublikovat bez schválení.
- Vzor ověřený v ČR: Autobezobalu (Ing. Landgráf, IG 9 864) prodává „pomoc s výběrem vozu“ za 2 500 Kč.
- Naplánované úlohy mi systém odmítl založit — zakládá je uživatel ze souborů se zadáním. Doporučené modely: sken Haiku 5.5, generování Sonnet 5.5.

## ROZPRACOVÁNO
- Ve VYSTUPY jsou 2 DEMO řádky (A1, B4) se Schváleno=ano, obrázky nahrané, export proběhl (20261026_1004_po_PUBLIKOVAT.html na Disku). Nic nebylo publikováno.
- Naplánované úlohy (týdenní sken, denní generování) zatím nezaložené.

## DALŠÍ KROK
Uživatel pošle odkaz na jeden skutečný inzerát → „generuj z VSTUPY“ naostro: zapsat řádek do VSTUPY, vyrobit 5 textů do VYSTUPY, kartu přes `node scripts/publikace_karta.js`, push do `publikace/20261026/`, řádek do PREHLED.md, URL do sloupce I, vypsat texty ke schválení. Pak uživatel: Schváleno=ano → menu Monetizace → Export.

## KLÍČOVÉ SOUBORY / LINKY
- Tabulka: https://docs.google.com/spreadsheets/d/17FhLa6hf9RzYJAXrgQkCQjnmJsAsMZ_dz0K3JK_oQFY/edit (listy NAVOD, VSTUPY, VYSTUPY, VZORY, CENIK, SKEN, OBJEDNAVKY)
- Výzkum (dokument): https://claude.ai/artifact/WZujCqqwtfh5Y1Rs24Uf1B
- Formulář auta: https://docs.google.com/forms/d/1Q0xvgYswaCp2X2_akyBPeOkwpUf-OgCIDQpxzs0eSY8/viewform
- Formulář firmy: https://docs.google.com/forms/d/1_wwh9oHAVepDXIzKWMAhOqx8jJFKMgzlvCthoYcNE_k/viewform
- Apps Script projekt: https://script.google.com/u/0/home/projects/1l2_BcFZRJar6Aq4RHeEvzYvZynnKwKHu12HmelhGIZYzQj1lkVAmPmnJ/edit
- GitHub Pages obrázky: https://batkodigitalai.github.io/batko-digital-ai/publikace/
- Zadání úloh: 20261026_0733_po_tydenni_sken_zadani.txt, 20261026_0940_po_denni_generovani_zadani.txt (v chatu)
