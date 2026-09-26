# Robin Travel Agent (prototype)

This is a personal travel agent project in development. Its intended use is to help a traveler research a trip in mainland China, starting with hotel discovery and evaluation.

## Current scope

The first live integration is RollingGo. Its Python command-line probe searches hotels and retrieves room prices through its MCP endpoint. A Tripadvisor Terra probe is also included for review research. The Terra probe can:

- Search for hotels in mainland China by name, optionally narrowing by city.
- Retrieve original-language guest reviews for a selected Tripadvisor location ID.
- Print the API response as JSON so hotel identity, ratings, review counts, and review content can be inspected before any product design decisions.

RollingGo hotel search has been verified with a live call. Its public tools do not expose guest review text or review counts, and a sample live search response did not include a guest score. **Tripadvisor Terra has not yet been verified** because the project does not yet have a Terra API key. The project does not currently book hotels, make itinerary recommendations, or store guest reviews.

## Run the RollingGo hotel probe

Install dependencies with `python3 -m pip install -r requirements.txt`. Set `ROLLINGGO_API_KEY` to a key beginning with `mcp_`, or set `ROLLINGGO_API_KEY_FILE` to a local file containing the key. The file may be a Markdown note; the script extracts only the RollingGo key. Never commit a key or key file.

```sh
export ROLLINGGO_API_KEY_FILE=/absolute/path/to/local/key-note.md
python3 rollinggo_hotels.py search '北京' --check-in 2026-10-10 --nights 1
python3 rollinggo_hotels.py detail HOTEL_ID --check-in 2026-10-10 --check-out 2026-10-11
```

## Intended use of Tripadvisor data

The travel agent would use hotel names, locations, ratings, review counts, and selected guest reviews to help a traveler compare hotels. The initial test will check coverage and review availability for hotels in mainland China. Any public display or derived summaries will be developed only after checking the applicable API access and attribution requirements.

## Run the API probe

Python 3 is required. Set the key in `TRIPADVISOR_API_KEY`, or set `TRIPADVISOR_API_KEY_FILE` to the path of a local file containing the key. Do not commit the key.

```sh
export TRIPADVISOR_API_KEY_FILE=/absolute/path/to/local/terra.key
python3 hotel_reviews_terra.py search 'Fairmont Peace Hotel' --city Shanghai
python3 hotel_reviews_terra.py reviews LOCATION_ID --size 5
```

The first command prints candidate hotels and their Tripadvisor IDs. Review the name and address before choosing an ID for the second command.
