#!/usr/bin/env python3
"""Search mainland China hotels through the RollingGo MCP endpoint.

Set ROLLINGGO_API_KEY or ROLLINGGO_API_KEY_FILE. The latter may point to a
plain key file or a Markdown note containing a key beginning with ``mcp_``.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests


ENDPOINT = "https://mcp.rollinggo.cn/mcp"


def load_key(parser):
    key = os.environ.get("ROLLINGGO_API_KEY", "").strip()
    key_file = os.environ.get("ROLLINGGO_API_KEY_FILE")
    if not key and key_file:
        try:
            content = Path(key_file).read_text(encoding="utf-8")
        except OSError as exc:
            parser.error(f"Cannot read key file: {exc}")
        match = re.search(r"\bmcp_[A-Za-z0-9_-]+", content)
        key = match.group(0) if match else ""
    if not key.startswith("mcp_"):
        parser.error("Set ROLLINGGO_API_KEY or ROLLINGGO_API_KEY_FILE with a RollingGo mcp_ key")
    return key


def call_tool(name, arguments, key):
    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "MCP-Protocol-Version": "2025-03-26",
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    }
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        envelope = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise RuntimeError(f"RollingGo request failed: {exc}") from exc
    if envelope.get("error"):
        raise RuntimeError(f"RollingGo RPC error: {envelope['error']}")
    result = envelope.get("result", {})
    if result.get("isError"):
        raise RuntimeError(f"RollingGo tool error: {result.get('content')}")
    for item in result.get("content", []):
        if item.get("type") == "text":
            return json.loads(item["text"])
    raise RuntimeError("RollingGo returned no text payload")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search", help="Search hotels by city or point of interest")
    search.add_argument("place")
    search.add_argument("--place-type", choices=["城市", "景点", "机场", "火车站", "地铁站", "酒店", "区/县", "详细地址"], default="城市")
    search.add_argument("--check-in", required=True, help="YYYY-MM-DD")
    search.add_argument("--nights", type=int, default=1)
    search.add_argument("--adults", type=int, default=2)
    search.add_argument("--size", type=int, default=5)
    detail = sub.add_parser("detail", help="Get rooms and prices by RollingGo hotel ID")
    detail.add_argument("hotel_id", type=int)
    detail.add_argument("--check-in", required=True, help="YYYY-MM-DD")
    detail.add_argument("--check-out", required=True, help="YYYY-MM-DD")
    detail.add_argument("--adults", type=int, default=2)
    args = parser.parse_args()
    key = load_key(parser)
    if args.command == "search":
        if not 1 <= args.size <= 20 or args.nights < 1 or args.adults < 1:
            parser.error("size must be 1-20; nights and adults must be positive")
        name = "searchHotels"
        arguments = {
            "originQuery": f"查询{args.place}酒店，{args.check_in}入住{args.nights}晚，{args.adults}名成人",
            "place": args.place,
            "placeType": args.place_type,
            "size": args.size,
            "checkInParam": {"checkInDate": args.check_in, "stayNights": args.nights, "adultCount": args.adults},
        }
    else:
        name = "getHotelDetail"
        arguments = {
            "hotelId": args.hotel_id,
            "dateParam": {"checkInDate": args.check_in, "checkOutDate": args.check_out},
            "occupancyParam": {"adultCount": args.adults, "roomCount": 1},
        }
    try:
        result = call_tool(name, arguments, key)
    except (RuntimeError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
