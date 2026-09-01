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
  api.py           FastAPI app -- routes and request/DB wiring
  schemas.py       Pydantic request/response models
main.py             runs the API with uvicorn
cli.py              standalone CLI demo of matcher/database/open_library, no server needed
```

## Setup

```
pip install -r requirements.txt
python main.py
```

Then visit http://127.0.0.1:8000/docs for interactive Swagger docs, or:

```
GET  /recommendations?q=something+like+dune+but+more+political
POST /books          {"title": ..., "author": ..., "open_library_key": ..., "subjects": [...]}
GET  /books
GET  /books/{id}
```

`python cli.py` still runs the original terminal-prompt flow directly against
the same modules, without needing the server running.

## Status

Phase 1 (FastAPI layer) complete, on top of the Phase 0 foundation rewrite.
See the project's phase plan for what's next: automated tests, TF-IDF
re-ranking, JWT auth, OpenAPI docs polish, Redis caching, Docker, CI/CD,
cloud deployment, and a frontend.
