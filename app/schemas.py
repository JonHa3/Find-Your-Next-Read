"""Pydantic request/response models for the API layer.

Kept separate from the SQLAlchemy models in database.py on purpose: these
describe the HTTP contract, not the storage schema, and the two are allowed
to drift. For example `subjects` is a list of strings here (what a client
sends/receives) but a single comma-joined string in the database row.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookCreate(BaseModel):
    """Request body for POST /books."""

    title: str
    author: str | None = None
    open_library_key: str | None = None
    subjects: list[str] | None = None


class BookOut(BaseModel):
    """Response shape for a saved book. from_attributes lets FastAPI build
    this directly from a SQLAlchemy Book instance instead of a dict."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    author: str | None
    open_library_key: str | None
    subjects: str | None
    added_at: datetime


class RecommendationOut(BaseModel):
    """One ranked Open Library result returned by GET /recommendations.
    Not a saved Book yet -- just a candidate the client can choose to
    POST to /books."""

    title: str | None
    author: str | None
    open_library_key: str | None
    subjects: list[str] | None
    score: float
