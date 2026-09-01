"""Thin client around the Open Library search API.

Kept separate from matcher.py so the "talk to an external API" concern is
isolated from the "score these results" concern, and so Phase 5 (Redis
caching) has a single, obvious place to slot a cache in front of later.
"""
import requests

SEARCH_URL = "https://openlibrary.org/search.json"

# Ask Open Library for exactly the fields matcher.py scores against, plus a
# few useful display fields. Keeps the payload small.
FIELDS = "title,author_name,subject,first_sentence,ratings_average,first_publish_year,key"


class OpenLibraryError(RuntimeError):
    """Raised when the Open Library API can't be reached or returns bad data."""


def search_open_library(keywords: set[str], limit: int = 20) -> list[dict]:
    """Search Open Library using the extracted keywords and return raw docs.

    Ranking here is intentionally naive (whatever order Open Library returns)
    — matcher.rank_candidates() is what actually decides relevance.
    """
    query = " ".join(sorted(keywords))
    if not query:
        return []

    params = {"q": query, "limit": limit, "fields": FIELDS}
    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise OpenLibraryError(f"Open Library search failed: {exc}") from exc

    try:
        return response.json()["docs"]
    except (ValueError, KeyError) as exc:
        raise OpenLibraryError("Open Library returned an unexpected response") from exc
