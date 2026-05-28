import requests
from matcher import extract_keywords

def search_books(query):
    url = f"https://openlibrary.org/search.json?q={query}&limit=10"
    response = requests.get(url)
    books = response.json()["docs"]
    for index, book in enumerate(books, start=1):
        print(f"{index}. {book.get('title')} - {book.get('author_name', ['unknown']) [0]}")

search_books(extract_keywords(input("What are you looking for?: ")))
