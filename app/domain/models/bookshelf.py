from .book import Book
from typing import List

class BookShelf:

    _id: str
    _books: List[Book]
    _current_weight: float

    def __init__(self, books: List[Book], shelf_id: str = None):
            self.set_id(shelf_id if shelf_id else '000000')
            self.set_books(books if books else [])
            self._update_weight()
    
    @classmethod
    def from_dict(cls, data: dict):
          books = [Book.from_dict(book_data) for book_data in data.get("books", [])]
          return cls(
                books=books,
                shelf_id=data.get("id", "000000")
          )
    
    def get_id(self):
          return self._id
    
    def get_books(self):
          return self._books
    
    def get_current_weight(self):
          return self._current_weight
    
    def set_id(self, id: str):
          self._id = id
    
    def set_books(self, books: List[Book]):
          self._books = books
          self._update_weight()
    
    def add_book(self, book: Book):
          """Agrega un libro al estante."""
          self._books.append(book)
          self._update_weight()
    
    def remove_book(self, book: Book):
          """Remueve un libro del estante."""
          if book in self._books:
              self._books.remove(book)
              self._update_weight()
    
    def _update_weight(self):
          """Actualiza el peso total del estante."""
          self._current_weight = sum(book.get_weight() for book in self._books)
    
    def to_dict(self):
          return {
                "id": self._id,
                "books": [book.to_dict() for book in self._books],
                "current_weight": self._current_weight
          }
    
    def __str__(self):
          return f"Bookshelf {self._id}: {len(self._books)} books, {self._current_weight:.2f}kg"
    
    def __repr__(self):
          return f"Bookshelf(id={self._id}, books={len(self._books)}, weight={self._current_weight:.2f})"