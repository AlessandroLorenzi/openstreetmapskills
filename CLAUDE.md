# OSM Tag Updater

Strumenti per aggiornare tag OpenStreetMap a partire da immagini o testo.

## Script disponibili

| Script | Uso |
| -------- | ----- |
| `osm_search.py` | Cerca elementi per nome/città, restituisce type/id |
| `osm_get_element.py` | Legge i tag attuali di un elemento (no auth) |
| `osm_update_tags.py` | Applica modifiche di tag via OSM API |
| `osm_auth.py` | Ottieni un OAuth 2.0 token interattivamente |

## Autenticazione

Richiede `OSM_TOKEN` (Bearer token OAuth 2.0 con scope `write_api`).

```bash
export OSM_TOKEN="<token>"
```

Per ottenere il token: vedi `osm_auth.py`.

## Workflow standard

Quando l'utente fornisce un'immagine (locandina, menù, orari) e un elemento OSM:

### 0. Cerca l'elemento (se l'ID non è noto)

```bash
python osm_search.py "nome locale" --city "città"
python osm_search.py "Bar Centrale" --city Milano --type node
```

Restituisce `type/id` da usare nei passi successivi.

### 1. Leggi i tag attuali

```bash
python osm_get_element.py way/<id>
```

### 2. Estrai i dati dalla sorgente

Analizza l'immagine o il testo e mappa i valori ai tag OSM appropriati.
Non inventare valori: usa solo ciò che è esplicitamente visibile.

Tag comuni da estrarre:

- `name` — nome del locale
- `opening_hours` — orari (vedi formato sotto)
- `phone` — telefono in formato internazionale (`+39 02 1234567`)
- `website` — URL
- `cuisine` — tipo di cucina (`italian`, `pizza`, `seafood`, ...)
- `addr:street`, `addr:housenumber`, `addr:city`, `addr:postcode`
- `amenity` / `shop` / `tourism` — tipo di attività

### 3. Mostra il diff e chiedi conferma

Prima di modificare, mostra sempre cosa cambia e chiedi conferma esplicita.

### 4. Applica le modifiche

```bash
OSM_CHANGESET_COMMENT="descrizione breve" \
python osm_update_tags.py <type> <id> 'key=value' 'key2=value2'
```

Per rimuovere un tag: `-keyname` (senza `=`)

Per verificare senza caricare: `OSM_DRY_RUN=1`

## Formato opening_hours

```text
Mo-Fr 09:00-18:00
Mo 10:00-17:00; Tu off; We-Su 10:00-23:00
Mo-Su 00:00-24:00
```

- Giorni: `Mo Tu We Th Fr Sa Su`
- Giorno chiuso: `off` (non "closed" o "chiuso")
- Giorni consecutivi con stesso orario: `Th-Su 10:00-23:00`
- Più regole separate da `;`

## Regole di qualità OSM

- Non modificare `building`, geometrie o relazioni — solo tag descrittivi
- Usa tag standard del wiki OSM
- Non aggiungere `source=*` a meno che l'utente non lo chieda
- Per `opening_hours` complessi, valida su <https://openingh.openstreetmap.de>
