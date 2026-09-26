#!/usr/bin/env python3
"""Extract the first page of public reviews from one Ctrip hotel detail page.

This reads only https://hotels.ctrip.com/hotels/ID.html and its embedded page
data. Supply the name and address from RollingGo to verify the hotel match.
It does not paginate, log in, or use undocumented review endpoints.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


URL_PATTERN = re.compile(r"https://hotels\.ctrip\.com/hotels/\d+\.html\Z")


def normalize(value):
    return re.sub(r"[\s()（）,，·\-]+", "", value or "").casefold()


def page_data(html):
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script"):
        text = script.get_text().strip()
        if "hotelCommentResponse" not in text or not text.startswith("self.__next_f.push("):
            continue
        try:
            chunk = json.loads(text[len("self.__next_f.push(") :].removesuffix(");").removesuffix(")"))
            flight_record = chunk[1]
            data = json.loads(flight_record.split(":", 1)[1])
        except (IndexError, ValueError, TypeError):
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict) and "hotelDetailResponse" in item and "hotelCommentResponse" in item:
                return item
    raise ValueError("Hotel review data was not found in the public page; the site layout may have changed")


def extract(data, url, expected_name, expected_address):
    hotel = data["hotelDetailResponse"]
    name = hotel["hotelBaseInfo"]["nameInfo"]["name"]
    address = hotel["hotelPositionInfo"]["address"]
    if normalize(expected_name) != normalize(name):
        raise ValueError(f"Hotel name mismatch: Ctrip returned {name!r}")
    if normalize(expected_address) not in normalize(address):
        raise ValueError(f"Hotel address mismatch: Ctrip returned {address!r}")
    review_data = data["hotelCommentResponse"]
    rating = review_data.get("commentRating", {})
    reviews = []
    for group in review_data.get("groupList", []):
        for item in group.get("commentList", []):
            reviews.append(
                {
                    "id": item.get("id"),
                    "published_at": item.get("createDate"),
                    "stay_date": item.get("checkinDate"),
                    "rating": item.get("rating"),
                    "content": item.get("content"),
                }
            )
    return {
        "source": "Ctrip public hotel page",
        "url": url,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "hotel_name": name,
        "hotel_address": address,
        "overall_rating": rating.get("ratingAll"),
        "rating_scale": rating.get("fullRating"),
        "review_count": review_data.get("totalCount"),
        "reviews_on_page": len(reviews),
        "reviews": reviews,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Ctrip hotel URL without query parameters")
    parser.add_argument("--expected-name", required=True, help="Hotel name returned by RollingGo")
    parser.add_argument("--expected-address", required=True, help="Hotel street address returned by RollingGo")
    parser.add_argument("--output", type=Path, help="Write JSON to this local file")
    args = parser.parse_args()
    if not URL_PATTERN.fullmatch(args.url):
        parser.error("URL must be https://hotels.ctrip.com/hotels/ID.html without query parameters")
    try:
        response = requests.get(
            args.url,
            headers={"User-Agent": "travel-agent-prototype/0.1"},
            timeout=25,
        )
        response.raise_for_status()
        result = extract(page_data(response.text), args.url, args.expected_name, args.expected_address)
    except (requests.RequestException, ValueError, KeyError) as exc:
        print(f"Ctrip page extraction failed: {exc}", file=sys.stderr)
        return 1
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Saved {len(result['reviews'])} public-page reviews to {args.output}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
