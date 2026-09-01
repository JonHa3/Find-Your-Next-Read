"""SQLAlchemy models and storage helpers for saved books.

Rewritten from the original raw-sqlite3 create_table()/save_book() version.
User/Favorite models (and the relationship between them) land in Phase 3
once JWT auth needs them — kept out for now to avoid scope creep.
"""
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "sqlite:///books.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    open_library_key = Column(String, unique=True, nullable=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    subjects = Column(Text, nullable=True)  # comma-separated, kept simple pre-Phase-1
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db() -> None:
    """Create tables if they don't exist yet. Safe to call on every startup."""
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return SessionLocal()


def save_book(
    session: Session,
    title: str,
    author: str | None = None,
    open_library_key: str | None = None,
    subjects: list[str] | None = None,
) -> Book:
    """Save a book, or return the existing row if it's already saved.

    De-dupes on open_library_key when one is provided, so re-saving the same
    search result doesn't create duplicate rows.
    """
    if open_library_key:
        existing = (
            session.query(Book)
            .filter(Book.open_library_key == open_library_key)
            .first()
        )
        if existing:
            return existing

    book = Book(
        title=title,
        author=author,
        open_library_key=open_library_key,
        subjects=", ".join(subjects) if subjects else None,
    )
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


def get_book(session: Session, book_id: int) -> Book | None:
    return session.get(Book, book_id)


def list_books(session: Session) -> list[Book]:
    return session.query(Book).order_by(Book.added_at.desc()).all()
