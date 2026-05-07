#!/usr/bin/env python3
"""Search OSM elements by name using the Nominatim API.

Usage:
  python osm_search.py <query> [--city <city>] [--type node|way|relation]
  python osm_search.py "Osteria Irma"
  python osm_search.py "Osteria Irma" --city Varese
  python osm_search.py "bar centrale" --city Milano --type node

Output:
  List of matching elements with type/id and current tags.
  Use the type/id with osm_update_tags.py to edit.
"""

import sys
import json
import argparse
from urllib.request import urlopen, Request
from urllib.parse import urlencode

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
ELEMENTS_URL = "https://api.openstreetmap.org/api/0.6"


def search_nominatim(query: str, city: str | None, elem_type: str | None) -> list[dict]:
    params = {
        "q": f"{query}, {city}" if city else query,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 10,
    }
    if elem_type:
        params["osm_type"] = elem_type[0].upper()

    url = f"{NOMINATIM_URL}?{urlencode(params)}"
    req = Request(url, headers={"User-Agent": "osm_search.py/1.0"})
    with urlopen(req) as r:
        return json.loads(r.read())


def fetch_tags(osm_type: str, osm_id: int) -> dict:
    type_map = {"N": "node", "W": "way", "R": "relation"}
    elem_type = type_map.get(osm_type, osm_type.lower())
    url = f"{ELEMENTS_URL}/{elem_type}/{osm_id}.json"
    try:
        with urlopen(url) as r:
            return json.loads(r.read())["elements"][0].get("tags", {})
    except Exception:
        return {}


def main():
    parser = argparse.ArgumentParser(description="Search OSM elements by name")
    parser.add_argument("query", help="Search query (e.g. 'Osteria Irma')")
    parser.add_argument("--city", help="Restrict search to a city")
    parser.add_argument("--type", dest="elem_type", choices=["node", "way", "relation"],
                        help="Restrict to element type")
    args = parser.parse_args()

    print(f"Searching for: {args.query}" + (f" in {args.city}" if args.city else "") + " ...")
    results = search_nominatim(args.query, args.city, args.elem_type)

    if not results:
        print("No results found.")
        sys.exit(0)

    type_map = {"node": "N", "way": "W", "relation": "R"}
    reverse_map = {"N": "node", "W": "way", "R": "relation"}

    for i, r in enumerate(results, 1):
        osm_type = r.get("osm_type", "?")[0].upper()
        osm_id = r.get("osm_id")
        display = r.get("display_name", "")
        elem_type_full = reverse_map.get(osm_type, osm_type)

        print(f"\n[{i}] {elem_type_full}/{osm_id}")
        print(f"    {display}")

        tags = fetch_tags(osm_type, osm_id)
        if tags:
            for k in ("name", "amenity", "shop", "tourism", "opening_hours", "phone", "website"):
                if k in tags:
                    print(f"    {k} = {tags[k]}")

    print(f"\nUso: python osm_update_tags.py <type> <id> 'key=value'")


if __name__ == "__main__":
    main()
