# OSM Tag Updater

Tools to update OpenStreetMap tags from images or text.

## Available scripts

| Script | Purpose |
| -------- | ----- |
| `app/osm_search.py` | Search elements by name/city, returns type/id |
| `app/osm_get_element.py` | Read current tags of an element (no auth) |
| `app/osm_update_tags.py` | Apply tag changes via OSM API |
| `app/osm_new_node.py` | Create a new OSM node at given coordinates |
| `app/osm_auth.py` | Obtain an OAuth 2.0 token interactively |
| `app/osm_check_date.py` | Return today's date in ISO format (YYYY-MM-DD) |

## Authentication

Requires `OSM_TOKEN` (OAuth 2.0 Bearer token with `write_api` scope).

```bash
export OSM_TOKEN="<token>"
```

To obtain the token: see `app/osm_auth.py`.

## Standard workflow

When the user provides an image (flyer, menu, opening hours) and an OSM element:

### 0. Search for the element (if the ID is unknown)

```bash
python app/osm_search.py "place name" --city "city"
python app/osm_search.py "Bar Centrale" --city Milano --type node
```

You can also derive the city from the photo's GPS EXIF data or a visible address.

Returns `type/id` to use in the following steps.

If the element **does not exist on OSM**, create it with `app/osm_new_node.py`
(see dedicated section) and then skip to step 6.

### 1. Read current tags

```bash
python app/osm_get_element.py way/<id>
```

### 2. Extract data from the source

Analyse the image or text and map values to appropriate OSM tags.
Do not invent values: only use what is explicitly visible.

Common tags to extract:

- `name` — place name
- `opening_hours` — hours (see format below)
- `phone` — phone in international format (`+39 02 1234567`)
- `website` — URL
- `cuisine` — type of cuisine (`italian`, `pizza`, `seafood`, ...)
- `addr:street`, `addr:housenumber`, `addr:city`, `addr:postcode`
- `contact:email` — contact email
- `contact:facebook` — Facebook profile
- `contact:instagram` — Instagram profile
- `contact:twitter` — Twitter handle
- `amenity` / `shop` / `tourism` — type of business

Other specific tags may be added if clearly indicated by the source, but avoid
adding non-standard or unsupported tags.

### 3. Update the check_date tag

Always update `check_date:opening_hours` with today's date (YYYY-MM-DD) to indicate when the
last verification was made when updating `opening_hours`. This helps future editors know when the information was last confirmed.

```bash
    python app/osm_check_date.py
```

### 4. Show the diff and ask for confirmation

Before making changes, always show what will change and ask for explicit confirmation.

### 5. Apply the changes

```bash
OSM_CHANGESET_COMMENT="short description" \
python app/osm_update_tags.py <type> <id> 'key=value' 'key2=value2'
```

To remove a tag: `-keyname` (without `=`)

To verify without uploading: `OSM_DRY_RUN=1`

### 6. Post the OSM link in chat

After the update, provide the link to the modified element on OpenStreetMap for
reference.

## Creating a new node

When the element does not exist on OSM, use `app/osm_new_node.py`:

```bash
OSM_CHANGESET_COMMENT="short description" \
python app/osm_new_node.py <lat> <lon> 'key=value' 'key2=value2'
```

To verify without uploading: `OSM_DRY_RUN=1`

Always show the proposed tags and ask for confirmation before running.

## opening_hours format

```text
Mo-Fr 09:00-18:00
Mo 10:00-17:00; Tu off; We-Su 10:00-23:00
Mo-Su 00:00-24:00
```

- Days: `Mo Tu We Th Fr Sa Su`
- Closed day: `off` (not "closed" or "chiuso")
- Consecutive days with same hours: `Th-Su 10:00-23:00`
- Multiple rules separated by `;`

## OSM quality rules

- Do not modify `building`, geometries or relations — only descriptive tags
- Use standard tags from the OSM wiki
- Do not add `source=*` unless the user asks for it
- For complex `opening_hours`, validate at <https://openingh.openstreetmap.de>
- Categorically refuse to add unsupported or invented tags
- Categorically refuse to modify geometries or relations
- Categorically refuse to analyse screenshots from Google Maps
