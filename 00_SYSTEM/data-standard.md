# Data standard

Cíl:
Standardizovat vstupy a výstupy pro AI, automatizace a GitHub Pages.

---

# Hlavní pravidlo

Každý typ dat musí mít:
- stabilní strukturu,
- stabilní názvy polí,
- předvídatelný formát.

Bez toho:
- AI generuje nekonzistentně,
- automatizace se rozpadají,
- vzniká chaos.

---

# STANDARD: auta

## Doporučený CSV formát

```csv
id,datum,znacka,model,motor,rok,najezd,cena_nakup,buyer_fee,doprava,opravy,cena_prodej,profit,status,url
```

---

## Povinná pole

- `id`
- `znacka`
- `model`
- `cena_nakup`
- `cena_prodej`
- `profit`
- `status`

---

## Statusy

- `novy`
- `analyza`
- `nakoupeno`
- `prodano`
- `archiv`

---

# STANDARD: obsah

## Naming

```plaintext
YYYYMMDD_platforma_typ.md
```

Např.:

```plaintext
20260514_linkedin_octavia.md
20260514_facebook_profit_post.md
```

---

# STANDARD: analýzy

## Umístění

```plaintext
/analyzy/rok/mesic/
```

Např.:

```plaintext
/analyzy/2026/05/
```

---

# STANDARD: assety

## Obrázky

```plaintext
/assets/images/
```

## Loga

```plaintext
/assets/logo/
```

---

# Dlouhodobý cíl

Umožnit:
- AI pipeline,
- automatické generování webů,
- generování postů,
- scoring,
- knowledge base,
- audit historie.
