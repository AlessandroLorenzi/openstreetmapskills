#!/usr/bin/env python3
"""Create a new OSM node at given coordinates with the specified tags.

Usage:
  python osm_new_node.py <lat> <lon> <tag_key>=<tag_value> [<tag_key>=<tag_value> ...]

Example:
  python osm_new_node.py 45.606719 8.822751 shop=hairdresser name="Raf Style"

Auth (one of):
  OSM_TOKEN   OAuth 2.0 bearer token  (preferred)
  OSM_USER + OSM_PASS  basic auth (deprecated by OSM but still works on dev server)

Environment:
  OSM_API_URL           defaults to https://api.openstreetmap.org
  OSM_CHANGESET_COMMENT optional comment for the changeset
  OSM_DRY_RUN           if set to "1", prints the XML without uploading
"""

import os
import sys
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request

API_URL = os.environ.get("OSM_API_URL", "https://api.openstreetmap.org")
DRY_RUN = os.environ.get("OSM_DRY_RUN", "") == "1"


def auth_headers() -> dict:
    token = os.environ.get("OSM_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    user = os.environ.get("OSM_USER")
    pwd = os.environ.get("OSM_PASS")
    if user and pwd:
        import base64
        creds = base64.b64encode(f"{user}:{pwd}".encode()).decode()
        return {"Authorization": f"Basic {creds}"}
    print("ERROR: set OSM_TOKEN or OSM_USER+OSM_PASS", file=sys.stderr)
    sys.exit(1)


def create_changeset(comment: str, headers: dict) -> int:
    comment = comment or "Add node via https://github.com/AlessandroLorenzi/openstreetmapskills"
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<osm><changeset>'
        '<tag k="created_by" v="https://github.com/AlessandroLorenzi/openstreetmapskills"/>'
        f'<tag k="comment" v="{comment}"/>'
        '</changeset></osm>'
    )
    req = Request(
        f"{API_URL}/api/0.6/changeset/create",
        data=xml.encode(),
        headers={**headers, "Content-Type": "text/xml"},
        method="PUT",
    )
    with urlopen(req) as r:
        return int(r.read().strip())


def close_changeset(changeset_id: int, headers: dict):
    req = Request(
        f"{API_URL}/api/0.6/changeset/{changeset_id}/close",
        data=b"",
        headers=headers,
        method="PUT",
    )
    with urlopen(req) as r:
        r.read()


def build_node_xml(lat: str, lon: str, tags: dict, changeset_id: int) -> str:
    root = ET.Element("osm")
    node = ET.SubElement(root, "node")
    node.set("changeset", str(changeset_id))
    node.set("lat", lat)
    node.set("lon", lon)
    for k, v in tags.items():
        tag = ET.SubElement(node, "tag")
        tag.set("k", k)
        tag.set("v", v)
    return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(root, encoding="unicode")


def create_node(xml_body: str, headers: dict) -> int:
    req = Request(
        f"{API_URL}/api/0.6/node/create",
        data=xml_body.encode(),
        headers={**headers, "Content-Type": "text/xml"},
        method="PUT",
    )
    with urlopen(req) as r:
        return int(r.read().strip())


def parse_tag_args(args: list[str]) -> dict:
    tags = {}
    for arg in args:
        if "=" not in arg:
            print(f"WARNING: ignoring malformed argument: {arg}", file=sys.stderr)
            continue
        k, _, v = arg.partition("=")
        tags[k.strip()] = v.strip()
    return tags


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    lat = sys.argv[1]
    lon = sys.argv[2]
    tags = parse_tag_args(sys.argv[3:])

    print(f"New node at lat={lat}, lon={lon}")
    print("Tags:")
    for k, v in tags.items():
        print(f"  {k}={v}")
    print()

    if DRY_RUN:
        xml_body = build_node_xml(lat, lon, tags, changeset_id=0)
        print("DRY RUN — XML:")
        print(xml_body)
        sys.exit(0)

    headers = auth_headers()
    comment = os.environ.get("OSM_CHANGESET_COMMENT", "")
    changeset_id = create_changeset(comment, headers)
    print(f"Created changeset #{changeset_id}")

    try:
        xml_body = build_node_xml(lat, lon, tags, changeset_id)
        node_id = create_node(xml_body, headers)
        print(f"Created node/{node_id}")
        print(f"\nhttps://www.openstreetmap.org/node/{node_id}")
    finally:
        close_changeset(changeset_id, headers)
        print(f"Closed changeset #{changeset_id}")


if __name__ == "__main__":
    main()
