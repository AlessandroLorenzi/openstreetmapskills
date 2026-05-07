#!/usr/bin/env python3
"""Fetch and display tags for an OSM element. No authentication needed.

Usage:
  python osm_get_element.py <type>/<id>
  python osm_get_element.py way 154386826
"""

import sys
import json
from urllib.request import urlopen

API_URL = "https://api.openstreetmap.org"


def fetch_element(elem_type: str, elem_id: int) -> dict:
    url = f"{API_URL}/api/0.6/{elem_type}/{elem_id}.json"
    with urlopen(url) as r:
        return json.loads(r.read())["elements"][0]


def main():
    args = sys.argv[1:]
    if len(args) == 1 and "/" in args[0]:
        elem_type, elem_id = args[0].split("/", 1)
    elif len(args) == 2:
        elem_type, elem_id = args
    else:
        print(__doc__)
        sys.exit(1)

    element = fetch_element(elem_type.lower(), int(elem_id))
    print(f"{element['type']}/{element['id']} (v{element['version']}, changeset {element['changeset']})")
    print(f"Last edited by {element['user']} on {element['timestamp']}\n")
    print("Tags:")
    for k, v in sorted(element["tags"].items()):
        print(f"  {k} = {v}")


if __name__ == "__main__":
    main()
