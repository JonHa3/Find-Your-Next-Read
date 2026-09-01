"""Keyword extraction and relevance scoring for book recommendations.

This is the "recommendation engine" part of the project: it doesn't just
forward the user's query to Open Library's own search ranking. It pulls out
meaningful keywords, then scores each candidate book against those keywords
using weighted overlap across a few fields (subjects matter more than an
incidental word in the title, which matters more than a word buried in the
first sentence).
"""
import re

STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she",
    "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that",
    "these", "those", "am", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the",
    "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by",
    "for", "with", "about", "against", "between", "into", "through", "during",
    "before", "after", "above", "below", "to", "from", "up", "down", "in", "out",
    "on", "off", "over", "under", "again", "further", "then", "once", "here", "there",
    "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "book", "books",
    "looking", "similar", "like", "want", "read", "find", "im",
}

# Field weights: how much a keyword match in each field counts toward score.
_WEIGHTS = {
    "subject": 3,
    "title": 2,
    "first_sentence": 1,
}


def extract_keywords(query: str) -> set[str]:
    """Pull meaningful search terms out of a plain-language query.

    Strips punctuation (regex tokenization instead of a naive .split()) and
    drops stopwords, so "I'm looking for something like Dune!" becomes
    {"dune", "something"}.
    """
    words = re.findall(r"[a-z0-9]+", query.lower().replace("'", ""))
    return {w for w in words if w not in STOPWORDS}


def _field_words(value) -> set[str]:
    """Normalize an Open Library field (string, list of strings, or None)
    into a lowercase word set for overlap scoring."""
    if not value:
        return set()
    if isinstance(value, list):
        text = " ".join(str(v) for v in value)
    else:
        text = str(value)
    return set(re.findall(r"[a-z0-9]+", text.lower().replace("'", "")))


def score_candidate(keywords: set[str], doc: dict) -> float:
    """Score one Open Library search result against the extracted keywords.

    Returns a weighted count of keyword overlaps across subject, title, and
    first_sentence. Higher is more relevant. 0 means no overlap at all.
    """
    if not keywords:
        return 0.0

    score = 0.0
    for field, weight in _WEIGHTS.items():
        field_words = _field_words(doc.get(field))
        overlap = keywords & field_words
        score += weight * len(overlap)

    return score


def rank_candidates(keywords: set[str], docs: list[dict], limit: int = 10) -> list[dict]:
    """Score and sort candidate books, dropping anything with zero relevance.

    Ties are broken by Open Library's average rating (when present), so
    among equally-relevant matches, better-reviewed books surface first.
    """
    scored = []
    for doc in docs:
        score = score_candidate(keywords, doc)
        if score > 0:
            scored.append((score, doc.get("ratings_average") or 0, doc))

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [doc for _score, _rating, doc in scored[:limit]]
