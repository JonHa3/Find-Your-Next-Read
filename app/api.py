"""FastAPI application -- wraps matcher/open_library/database behind HTTP
endpoints. This is Phase 1: the CLI (now cli.py) is no longer the primary
interface. Phase 4 adds richer OpenAPI metadata on top of what FastAPI
already generates for free just from this file's type hints and docstrings.
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_book, init_db, list_books, save_book
from app.matcher import extract_keywords, rank_candidates, score_candidate
from app.open_library import OpenLibraryError, search_open_library
from app.schemas import BookCreate, BookOut, RecommendationOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup, before any request is served -- the modern
    # replacement for the deprecated @app.on_event("startup") decorator.
    init_db()
    yield


app = FastAPI(
    title="Find Your Next Read",
    description="Book recommendations from plain-language queries, backed by the Open Library API.",
    lifespan=lifespan,
)


def get_db():
    """Per-request DB session. FastAPI calls this before the route runs and
    resumes it after the response is built, so the session always closes --
    even if the route raises."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/recommendations", response_model=list[RecommendationOut])
def get_recommendations(
    q: str = Query(..., min_length=1, description="Plain-language description of what you're looking for"),
    limit: int = Query(10, ge=1, le=50),
):
    keywords = extract_keywords(q)
    if not keywords:
        raise HTTPException(
            status_code=400,
            detail="Couldn't extract any meaningful keywords from that query.",
        )

    # Over-fetch from Open Library so ranking has more than `limit` candidates
    # to choose from before trimming down.
    try:
        docs = search_open_library(keywords, limit=max(limit * 2, 20))
    except OpenLibraryError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    ranked = rank_candidates(keywords, docs, limit=limit)
    return [
        RecommendationOut(
            title=doc.get("title"),
            author=(doc.get("author_name") or [None])[0],
            open_library_key=doc.get("key"),
            subjects=doc.get("subject"),
            score=score_candidate(keywords, doc),
        )
        for doc in ranked
    ]


@app.post("/books", response_model=BookOut, status_code=201)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return save_book(
        db,
        title=book.title,
        author=book.author,
        open_library_key=book.open_library_key,
        subjects=book.subjects,
    )


@app.get("/books", response_model=list[BookOut])
def get_books(db: Session = Depends(get_db)):
    return list_books(db)


@app.get("/books/{book_id}", response_model=BookOut)
def get_book_by_id(book_id: int, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
