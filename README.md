# Robin Travel Agent (prototype)

This is a personal travel agent project in development. Its intended use is to help a traveler research a trip in mainland China, starting with hotel discovery and evaluation.

## Current scope

The first integration under evaluation is Tripadvisor Terra. The included Python command-line probe can:

- Search for hotels in mainland China by name, optionally narrowing by city.
- Retrieve original-language guest reviews for a selected Tripadvisor location ID.
- Print the API response as JSON so hotel identity, ratings, review counts, and review content can be inspected before any product design decisions.

The code is prepared, but **live hotel results have not yet been verified** because the project does not yet have a Terra API key. The project does not currently book hotels, make itinerary recommendations, or store guest reviews.

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
