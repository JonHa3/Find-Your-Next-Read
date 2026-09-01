# Find Your Next Read

A book recommendation tool that takes a plain-language query ("something like
Dune but more political") and returns relevant books, using the Open Library
API as the data source and a custom keyword-scoring engine for relevance.

Started as a personal script; being extended into a full backend service
(REST API, auth, caching, Docker, CI/CD, cloud deployment) as a portfolio
project.

## Project structure

```
app/
  matcher.py       keyword extraction + relevance scoring
  open_library.py  Open Library API client
  database.py      SQLAlchemy models + storage (SQLite)
main.py             CLI entry point (temporary — Phase 1 replaces this with a FastAPI app)
```

## Setup

```
pip install -r requirements.txt
python main.py
```

## Status

Phase 0 (foundation rewrite) complete. See the project's phase plan for what's next:
FastAPI layer, tests, JWT auth, OpenAPI docs, Redis caching, Docker, CI/CD,
cloud deployment, and a frontend.
