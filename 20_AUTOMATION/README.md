# 20_AUTOMATION

Vrstva pro automatizace a workflow.

## Budoucí použití

- generování HTML z CSV,
- automatické posty,
- email parsing,
- exporty,
- GitHub Pages deploy,
- scoring aut,
- AI workflow.

## Doporučená struktura

- `/scripts`
- `/deploy`
- `/generators`
- `/email-parsers`
- `/scheduled-jobs`

## Bezpečnostní pravidlo

Automatizace nesmí přepisovat veřejnou produkci bez:
- zálohy,
- commitu,
- rollback možnosti.
