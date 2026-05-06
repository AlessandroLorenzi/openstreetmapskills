# OSM Tag Updater

Aggiorna tag OpenStreetMap a partire da immagini o testo, usando Claude Code.

## Requisiti

- Python 3.9+
- Account su [openstreetmap.org](https://www.openstreetmap.org)

## Ottenere un token OSM

### 1. Registra un'applicazione OAuth

Vai su **openstreetmap.org → Il tuo account → OAuth 2 Applications →
Register new application** e compila:

| Campo | Valore |
| ------- | -------- |
| Name | `claude-osm-cli` (o qualsiasi nome) |
| Redirect URIs | `urn:ietf:wg:oauth:2.0:oob` |
| Confidential application | lascia **deselezionato** |
| Permissions | spunta solo **Modify the map** |

Clicca **Register** e copia il **Client ID** (il Client Secret non è necessario).

### 2. Genera il token

```bash
python osm_auth.py <CLIENT-ID>
```

Lo script apre il browser su OSM. Dopo aver cliccato **Authorize**, OSM
mostra un codice — incollalo nel terminale. Il token viene stampato a schermo.

### 3. Esporta il token

```bash
export OSM_TOKEN="<token>"
```

Per renderlo permanente:

```bash
echo 'export OSM_TOKEN="<token>"' >> ~/.zshrc
```

## Uso

```bash
# Cerca un elemento per nome
python osm_search.py "Osteria Irma" --city Varese
python osm_search.py "Bar Centrale" --city Milano --type node

# Leggi i tag attuali di un elemento
python osm_get_element.py way/154386826

# Aggiorna tag (mostra diff e chiede conferma)
OSM_CHANGESET_COMMENT="Update opening_hours" \
python osm_update_tags.py way 154386826 \
  'opening_hours=Mo 10:00-17:00; Tu off; We 10:00-17:00; Th-Su 10:00-23:00'

# Verifica senza caricare
OSM_DRY_RUN=1 python osm_update_tags.py way 154386826 'name=Nuovo Nome'

# Rimuovi un tag
python osm_update_tags.py way 154386826 -old_tag
```

## Uso con Claude Code

Apri Claude Code in questa directory e descrivi cosa vuoi aggiornare,
allegando un'immagine o testo con le informazioni. Claude legge i tag
attuali, estrae i valori dalla sorgente e propone le modifiche prima
di applicarle.
