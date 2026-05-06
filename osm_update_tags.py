#!/usr/bin/env python3
"""Update tags on an OSM element (node/way/relation) via the OSM API v0.6.

Usage:
  python osm_update_tags.py <type> <id> <tag_key>=<tag_value> [<tag_key>=<tag_value> ...]

  To remove a tag, prefix the key with '-':
  python osm_update_tags.py way 154386826 -old_tag opening_hours="Mo 10:00-17:00; Tu off"

Auth (one of):
  OSM_TOKEN   OAuth 2.0 bearer token  (preferred)
  OSM_USER + OSM_PASS  basic auth (deprecated by OSM but still works on dev server)

Environment:
  OSM_API_URL  defaults to https://api.openstreetmap.org
  OSM_CHANGESET_COMMENT  optional comment for the changeset
  OSM_DRY_RUN  if set to "1", prints the XML diff without uploading
"""

import os
import sys
import json
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import urllib.parse

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


def fetch_element(elem_type: str, elem_id: int) -> dict:
    url = f"{API_URL}/api/0.6/{elem_type}/{elem_id}.json"
    with urlopen(url) as r:
        return json.loads(r.read())["elements"][0]


def create_changeset(comment: str, headers: dict) -> int:
    comment = comment or "Tag update via osm_update_tags.py"
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<osm><changeset>'
        f'<tag k="created_by" v="osm_update_tags.py"/>'
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


def build_element_xml(element: dict, new_tags: dict, changeset_id: int) -> str:
    elem_type = element["type"]
    root = ET.Element("osm")
    el = ET.SubElement(root, elem_type)
    el.set("id", str(element["id"]))
    el.set("version", str(element["version"]))
    el.set("changeset", str(changeset_id))

    if elem_type == "node":
        el.set("lat", str(element["lat"]))
        el.set("lon", str(element["lon"]))

    if elem_type in ("way",):
        for ref in element.get("nodes", []):
            nd = ET.SubElement(el, "nd")
            nd.set("ref", str(ref))
    elif elem_type == "relation":
        for member in element.get("members", []):
            m = ET.SubElement(el, "member")
            m.set("type", member["type"])
            m.set("ref", str(member["ref"]))
            m.set("role", member.get("role", ""))

    for k, v in new_tags.items():
        tag = ET.SubElement(el, "tag")
        tag.set("k", k)
        tag.set("v", v)

    return '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(root, encoding="unicode")


def upload_element(elem_type: str, elem_id: int, xml_body: str, headers: dict) -> int:
    req = Request(
        f"{API_URL}/api/0.6/{elem_type}/{elem_id}",
        data=xml_body.encode(),
        headers={**headers, "Content-Type": "text/xml"},
        method="PUT",
    )
    with urlopen(req) as r:
        return int(r.read().strip())


def parse_tag_args(args: list[str]) -> tuple[dict, list[str]]:
    """Returns (tags_to_set, keys_to_remove)."""
    to_set = {}
    to_remove = []
    for arg in args:
        if arg.startswith("-") and "=" not in arg:
            to_remove.append(arg[1:])
        elif "=" in arg:
            k, _, v = arg.partition("=")
            to_set[k.strip()] = v.strip()
        else:
            print(f"WARNING: ignoring malformed argument: {arg}", file=sys.stderr)
    return to_set, to_remove


def print_diff(old_tags: dict, new_tags: dict):
    all_keys = sorted(set(old_tags) | set(new_tags))
    print("\n--- current tags")
    print("+++ proposed tags\n")
    changed = False
    for k in all_keys:
        old_v = old_tags.get(k)
        new_v = new_tags.get(k)
        if old_v == new_v:
            print(f"    {k}={old_v}")
        elif old_v is None:
            print(f"+   {k}={new_v}")
            changed = True
        elif new_v is None:
            print(f"-   {k}={old_v}")
            changed = True
        else:
            print(f"-   {k}={old_v}")
            print(f"+   {k}={new_v}")
            changed = True
    if not changed:
        print("(no changes)")
    print()
    return changed


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    elem_type = sys.argv[1].lower()
    elem_id = int(sys.argv[2])
    tag_args = sys.argv[3:]

    if elem_type not in ("node", "way", "relation"):
        print(f"ERROR: element type must be node, way, or relation (got {elem_type!r})")
        sys.exit(1)

    tags_to_set, keys_to_remove = parse_tag_args(tag_args)

    print(f"Fetching {elem_type}/{elem_id} from OSM...")
    element = fetch_element(elem_type, elem_id)
    old_tags = dict(element["tags"])

    new_tags = {**old_tags}
    new_tags.update(tags_to_set)
    for k in keys_to_remove:
        new_tags.pop(k, None)

    has_changes = print_diff(old_tags, new_tags)

    if not has_changes:
        print("Nothing to update.")
        sys.exit(0)

    if DRY_RUN:
        print("DRY RUN — not uploading.")
        sys.exit(0)

    answer = input("Apply these changes to OSM? [y/N] ").strip().lower()
    if answer != "y":
        print("Aborted.")
        sys.exit(0)

    headers = auth_headers()
    comment = os.environ.get("OSM_CHANGESET_COMMENT", "")
    changeset_id = create_changeset(comment, headers)
    print(f"Created changeset #{changeset_id}")

    try:
        xml_body = build_element_xml(element, new_tags, changeset_id)
        new_version = upload_element(elem_type, elem_id, xml_body, headers)
        print(f"Updated {elem_type}/{elem_id} to version {new_version}")
    finally:
        close_changeset(changeset_id, headers)
        print(f"Closed changeset #{changeset_id}")


if __name__ == "__main__":
    main()
