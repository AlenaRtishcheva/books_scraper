import pytest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__)) 
parent_dir = os.path.dirname(current_dir)                 
sys.path.insert(0, parent_dir)

from scraper import get_book_data, scrape_books

def test_get_book_structure() -> None:
    """Проверяет структуру данных, возвращаемых get_book_data()."""
    book = get_book_data(
        'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
    )
    assert isinstance(book, dict)
    assert 'title' in book
    assert 'price' in book
    assert 'rating' in book
    assert 'availability' in book
    assert 'description' in book

def test_get_book_key_value() -> None:
    """Проверяет соответствие ключ-значение в данных, возвращаемых get_book_data()."""
    book = get_book_data(
        'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
    )
    assert book['title'] == 'A Light in the Attic'
    assert book['availability'] == 'In stock (22 available)'
    assert book['product_type'] == 'Books'
    assert book['rating'] in ['One', 'Two', 'Three', 'Four', 'Five']
    assert '£' in book['price'] 

def test_scrape_books__number_of_books() -> None:
    """Проверяет количество возвращаемых книг."""
    books = scrape_books(is_save=False)
    assert len(books) > 0
    assert len(books) <= 1000