from .book import Book

class BookShelf:

    _id: str
    _books:Book

    def __init__(self, books:Book):
            self.set_id('000000')
            self.set_books(books)
    
    @classmethod
    def from_dict(cls, data:dict):
          return cls(
                id=data["id"],
                books=Book[data["books"]]
          )
    def get_id(self):
          return self._id
    def get_books(self):
          return self._books
    
    def set_id(self, id:str):
          self._id = id
    def set_books(self, books: Book):
          self._books = books
    def to_dict(self):
          return{
                "id": self._id,
                "books": self._books
          }
    
    def __str__(self):
          return f"Bookshelf: {self._id} - Book {self._books}"
    def __repr__(self):
          return f"Bookshelf(id={self._id}, books={self._books})"