# OSM Tag Updater

Update OpenStreetMap tags from images or text using an MCP server and Claude.

## Requirements

- Python 3.11+
- [fastmcp](https://github.com/jlowin/fastmcp) (`pip install fastmcp`)
- Account on [openstreetmap.org](https://www.openstreetmap.org)

## Setup

### 1. Install dependencies

```bash
pip install fastmcp
```

### 2. Get an OSM token

Register an OAuth application on **openstreetmap.org → Your account →
OAuth 2 Applications → Register new application**:

| Field | Value |
| ----- | ----- |
| Name | `claude-osm-mcp` (or any name) |
| Redirect URIs | `urn:ietf:wg:oauth:2.0:oob` |
| Confidential application | leave **unchecked** |
| Permissions | check only **Modify the map** |

Then generate the token:

```bash
python app/osm_auth.py <CLIENT-ID>
```

The script opens your browser, asks you to authorize, then prints the token.

```bash
export OSM_TOKEN="<token>"
```

### 3. Register the MCP server in Claude Code

Add to `~/.claude/mcp.json`:

```json
{
  "mcpServers": {
    "osm": {
      "command": "python",
      "args": ["/path/to/openstreetmapskills/server.py"],
      "env": {
        "OSM_TOKEN": "<your-token>"
      }
    }
  }
}
```

## Available tools

| Tool | Description |
| ---- | ----------- |
| `search_osm` | Search elements by name and city |
| `get_osm_element` | Read current tags (no auth needed) |
| `update_osm_tags` | Apply tag changes |
| `create_osm_node` | Create a new node at given coordinates |
| `get_today_date` | Return today's date in ISO format |

## Usage

Once the MCP server is registered, open Claude and describe what you want to
update, attaching an image or text (flyer, menu, opening hours sign). Claude
will search for the element, read its current tags, propose changes, and ask
for confirmation before applying them.
