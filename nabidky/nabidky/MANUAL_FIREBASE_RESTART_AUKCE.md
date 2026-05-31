# Manual: Firebase restart aukce

Tento manual resi situace, kdy je aukce uz vytvorena ve Firebase a potrebujes ji znovu pustit, prodlouzit, nebo spustit ciste od nove ceny.

Firebase DB:
`https://batko-aukce-default-rtdb.europe-west1.firebasedatabase.app`

Typicka cesta k aukci:
`auctions / AUK-TEST-001`

## Co ridi verejna stranka

Verejna HTML stranka si z Firebase bere hlavne:

- `status` - stav aukce
- `endTime` - konec aukce
- `startPrice` - vyvolavaci cena
- `minIncrement` - minimalni prihoz
- `bids` - existujici prihozy

Pokud je ve Firebase `endTime`, ma prednost pred casem napsanym v HTML.

## Varianta A: Jen prodlouzit aukci

Pouzij, kdyz aukce normalne bezi nebo skoncila, ale chces ji znovu otevrit se stejnymi prihozy.

Ve Firebase nastav:

```json
status: "active"
endTime: "2026-05-31T18:00:00.000+02:00"
```

Volitelne smaz:

```json
endedAt
winner
```

Vysledek:

- Stare prihozy zustanou.
- Minimalni dalsi prihoz bude posledni nejvyssi bid + `minIncrement`.
- Aukce navaze tam, kde skoncila.

## Varianta B: Restartovat aukci ciste od nove ceny

Pouzij, kdyz chces zacit znovu a nechces, aby se zobrazovaly stare testovaci nebo predchozi prihozy.

Ve Firebase u dane aukce nastav:

```json
status: "active"
endTime: "2026-05-31T18:00:00.000+02:00"
startPrice: 380000
minIncrement: 1000
```

Smaz tyto polozky:

```json
bids
winner
endedAt
cancelReason
```

Vysledek:

- Aukce zacne od `startPrice`.
- Na verejne strance nebudou stare bidy.
- Prvni zakaznik muze prihodit minimalne vyvolavaci cenu.

## Varianta C: Zrusit aukci

Pouzij, kdyz se auto neda koupit, neni dostupne, nebo nechces prijimat dalsi prihozy.

Ve Firebase nastav:

```json
status: "cancelled"
cancelReason: "Vozidlo jiz neni dostupne."
```

Vysledek:

- Formular pro prihoz se uzamkne.
- Stranka ukaze zrusenou aukci.

## Varianta D: Ukoncit aukci

Pouzij, kdyz aukce skoncila a chces ji uzavrit.

Ve Firebase nastav:

```json
status: "ended"
endedAt: 1780122415382
```

`endedAt` je timestamp v milisekundach. Pokud si nejsi jisty, muzes ho nechat vytvorit pres admin panel nebo ho pri rucnim ukonceni vynechat.

Vysledek:

- Prihozy se zastavi.
- Formular se uzamkne.
- Vitez se bere z nejvyssiho bidu, pripadne z polozky `winner`, pokud je ulozena.

## Jak rucne mazat ve Firebase

1. Otevri Firebase Console.
2. Jdi do projektu `batko-aukce`.
3. Otevri Realtime Database.
4. Najdi cestu `auctions`.
5. Otevri konkretni aukci, napr. `AUK-TEST-001`.
6. Klikni na polozku, kterou chces smazat, napr. `bids`.
7. Pouzij ikonu smazani / Delete.
8. Uloz zmeny.

Pozor: smazani `bids` je nevratne, pokud nemas export nebo zalozni kopii.

## Doporuceny postup pro cisty restart

1. Zkontroluj, ze mas spravne ID aukce.
2. Poznamenej si puvodni nejvyssi bid, pokud ho chces archivovat.
3. Smaz `bids`, `winner`, `endedAt`, pripadne `cancelReason`.
4. Nastav novou `startPrice`.
5. Nastav novy `endTime` v budoucnosti.
6. Nastav `status` na `"active"`.
7. Otevri verejnou stranku aukce a zkontroluj:
   - countdown bezi,
   - formular jde pouzit,
   - minimalni prihoz odpovida `startPrice`,
   - stare bidy se nezobrazuji.

## Format casu

Pro Cesko je nejprehlednejsi pouzit cas s posunem `+02:00` v letnim case:

```json
"2026-05-31T18:00:00.000+02:00"
```

Nebo UTC:

```json
"2026-05-31T16:00:00.000Z"
```

Oba priklady znamenaji stejny cas: 31. 5. 2026 v 18:00 v Praze.

## Co muze udelat Codex

Kdyz napises novy konec aukce a reknes, jestli chces:

- prodlouzit se starymi bidy,
- restartovat ciste,
- zrusit,
- ukoncit,

Codex muze Firebase upravit pres REST API a potom overit verejnou stranku.

