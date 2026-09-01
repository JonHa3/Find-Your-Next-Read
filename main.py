"""CLI entry point — exercises the rewritten matcher/database/open_library
modules end to end. This is a stepping stone: Phase 1 wraps these same
modules in FastAPI endpoints instead of a terminal prompt.
"""
from app.database import init_db, get_session, save_book, list_books
from app.matcher import extract_keywords, rank_candidates
from app.open_library import search_open_library, OpenLibraryError


def run() -> None:
    init_db()
    query = input("What are you looking for?: ")

    keywords = extract_keywords(query)
    if not keywords:
        print("Couldn't pull any meaningful keywords out of that — try adding more detail.")
        return

    try:
        docs = search_open_library(keywords)
    except OpenLibraryError as exc:
        print(f"Search failed: {exc}")
        return

    results = rank_candidates(keywords, docs)
    if not results:
        print("No relevant matches found.")
        return

    for index, doc in enumerate(results, start=1):
        author = doc.get("author_name", ["Unknown"])[0]
        print(f"{index}. {doc.get('title')} - {author}")

    choice = input("\nSave one to your list? Enter a number, or press Enter to skip: ").strip()
    if not choice:
        return

    try:
        selected = results[int(choice) - 1]
    except (ValueError, IndexError):
        print("Not a valid choice.")
        return

    session = get_session()
    try:
        book = save_book(
            session,
            title=selected.get("title"),
            author=(selected.get("author_name") or [None])[0],
            open_library_key=selected.get("key"),
            subjects=selected.get("subject"),
        )
        print(f"Saved: {book.title}")
    finally:
        session.close()


def show_saved() -> None:
    session = get_session()
    try:
        for book in list_books(session):
            print(f"- {book.title} ({book.author or 'unknown author'})")
    finally:
        session.close()


if __name__ == "__main__":
    run()
