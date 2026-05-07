# OSM Tag Updater

Update OpenStreetMap tags from images or text, using Claude Code.

## Requirements

- Python 3.9+
- Account on [openstreetmap.org](https://www.openstreetmap.org)

## Getting an OSM token

### 1. Register an OAuth application

Go to **openstreetmap.org → Your account → OAuth 2 Applications →
Register new application** and fill in:

| Field | Value |
| ------- | -------- |
| Name | `claude-osm-cli` (or any name) |
| Redirect URIs | `urn:ietf:wg:oauth:2.0:oob` |
| Confidential application | leave **unchecked** |
| Permissions | check only **Modify the map** |

Click **Register** and copy the **Client ID** (the Client Secret is not needed).

### 2. Generate the token

```bash
python osm_auth.py <CLIENT-ID>
```

The script opens your browser on OSM. After clicking **Authorize**, OSM
displays a code — paste it in the terminal. The token will be printed on screen.

### 3. Export the token

```bash
export OSM_TOKEN="<token>"
```

To make it permanent:

```bash
echo 'export OSM_TOKEN="<token>"' >> ~/.zshrc
```

## Usage

```bash
# Search for an element by name
python osm_search.py "Osteria Irma" --city Varese
python osm_search.py "Bar Centrale" --city Milano --type node

# Read the current tags of an element
python osm_get_element.py way/154386826

# Update tags (shows diff and asks for confirmation)
OSM_CHANGESET_COMMENT="Update opening_hours" \
python osm_update_tags.py way 154386826 \
  'opening_hours=Mo 10:00-17:00; Tu off; We 10:00-17:00; Th-Su 10:00-23:00'

# Dry run without uploading
OSM_DRY_RUN=1 python osm_update_tags.py way 154386826 'name=New Name'

# Remove a tag
python osm_update_tags.py way 154386826 -old_tag
```

## Usage with Claude Code

Open Claude Code in this directory and describe what you want to update,
attaching an image or text with the relevant information. Claude reads the
current tags, extracts values from the source, and proposes changes before
applying them.
