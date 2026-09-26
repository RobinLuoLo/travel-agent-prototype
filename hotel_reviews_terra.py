#!/usr/bin/env python3
"""Minimal Tripadvisor Terra hotel search and review probe.

Set TRIPADVISOR_API_KEY or TRIPADVISOR_API_KEY_FILE in the shell.
The key is never printed or saved by this script.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE = "https://terra.tripadvisor.com/api"


def get(path, params, api_key):
    url = BASE + path
    if params:
        url += "?" + urlencode(params)
    req = Request(url, headers={"X-API-Key": api_key, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=15) as response:
            return json.load(response)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {body}", file=sys.stderr)
        raise SystemExit(1)
    except URLError as exc:
        print(f"Network error: {exc}", file=sys.stderr)
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    search = sub.add_parser("search", help="Search hotels in mainland China")
    search.add_argument("name", help="Hotel name or recognizable English name")
    search.add_argument("--city", help="City name to narrow the search")

    reviews = sub.add_parser("reviews", help="Get original-language reviews by Tripadvisor ID")
    reviews.add_argument("location_id", type=int)
    reviews.add_argument("--size", type=int, default=5)

    args = parser.parse_args()
    api_key = os.environ.get("TRIPADVISOR_API_KEY")
    key_file = os.environ.get("TRIPADVISOR_API_KEY_FILE")
    if not api_key and key_file:
        try:
            api_key = Path(key_file).read_text(encoding="utf-8").strip()
        except OSError as exc:
            parser.error(f"Cannot read key file: {exc}")
    if not api_key:
        parser.error("Set TRIPADVISOR_API_KEY or TRIPADVISOR_API_KEY_FILE first")

    if args.command == "search":
        params = {
            "version": 1,
            "query": args.name,
            "country_code": "CN",
            "category": "HOTEL",
            "size": 10,
        }
        if args.city:
            params["geo_name"] = args.city
        payload = get("/locations/search", params, api_key)
    else:
        payload = get(
            f"/locations/{args.location_id}/reviews",
            {"language": "primary", "page": 1, "size": args.size},
            api_key,
        )

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
