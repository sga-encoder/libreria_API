from sqlalchemy.orm import Session
from typing import Optional, List
from app.domain.models import Book
from app.persistence.models import BookORM
from .base_repository import BaseRepository

class BooksRepositorySQL(BaseRepository[BookORM]):
    """Repositorio SQL para gestionar libros."""
    
    def __init__(self, db: Session):
        super().__init__(db, BookORM)
    
    def read_all(self) -> List[BookORM]:
        """Lee todos los libros activos (no prestados obligatoriamente)."""
        return self.db.query(BookORM).all()

    def read(self, isbn: str) -> Optional[BookORM]:
        """Obtiene un libro por ISBN (sobrescribe BaseRepository)."""
        return self.read_by_isbn(isbn)
    
    def read_by_isbn(self, isbn: str) -> Optional[BookORM]:
        """Obtiene un libro por ISBN."""
        return self.db.query(BookORM).filter(BookORM.id_IBSN == isbn).first()
    
    def read_by_title(self, title: str) -> List[BookORM]:
        """Obtiene libros que coincidan con el título (búsqueda parcial)."""
        return self.db.query(BookORM).filter(BookORM.title.ilike(f"%{title}%")).all()
    
    def read_by_author(self, author: str) -> List[BookORM]:
        """Obtiene libros por autor (búsqueda parcial)."""
        return self.db.query(BookORM).filter(BookORM.author.ilike(f"%{author}%")).all()
    
    def read_by_genre(self, genre: str) -> List[BookORM]:
        """Obtiene libros por género/categoría (búsqueda parcial)."""
        return self.db.query(BookORM).filter(BookORM.gender.ilike(f"%{genre}%")).all()
    
    def read_available(self) -> List[BookORM]:
        """Obtiene solo los libros disponibles (no prestados)."""
        return self.db.query(BookORM).filter(BookORM.is_borrowed == False).all()
    
    def read_borrowed(self) -> List[BookORM]:
        """Obtiene solo los libros prestados."""
        return self.db.query(BookORM).filter(BookORM.is_borrowed == True).all()

    def update(self, isbn: str, **kwargs) -> Optional[BookORM]:
        """Actualiza un libro por ISBN (sobrescribe BaseRepository)."""
        book = self.read_by_isbn(isbn)
        if book:
            for key, value in kwargs.items():
                if hasattr(book, key):
                    setattr(book, key, value)
            self.db.commit()
            self.db.refresh(book)
        return book

    def delete(self, isbn: str) -> bool:
        """Elimina un libro por ISBN (sobrescribe BaseRepository)."""
        book = self.read_by_isbn(isbn)
        if book:
            self.db.delete(book)
            self.db.commit()
            return True
        return False
    
    def mark_as_borrowed(self, isbn: str) -> bool:
        """Marca un libro como prestado."""
        book = self.read(isbn)
        if book:
            book.is_borrowed = True
            self.db.commit()
            return True
        return False
    
    def mark_as_available(self, isbn: str) -> bool:
        """Marca un libro como disponible (devuelto)."""
        book = self.read(isbn)
        if book:
            book.is_borrowed = False
            self.db.commit()
            return True
        return False
    
    def orm_to_domain(self, orm_book: BookORM) -> Book:
        """Convierte un BookORM a un Book del dominio."""
        if not orm_book:
            return None
        
        return Book(
            id_IBSN=orm_book.id_IBSN,
            title=orm_book.title,
            author=orm_book.author,
            gender=orm_book.gender,
            weight=orm_book.weight,
            price=orm_book.price,
            description=orm_book.description or "",
            frond_page_url=orm_book.frond_page_url or "",
            is_borrowed=orm_book.is_borrowed
        )
    
    def domain_to_orm(self, book: Book) -> BookORM:
        """Convierte un Book del dominio a un BookORM."""
        if not book:
            return None
        
        return BookORM(
            id_IBSN=book.get_id_IBSN(),
            title=book.get_title(),
            author=book.get_author(),
            gender=book.get_gender(),
            weight=book.get_weight(),
            price=book.get_price(),
            description=book.get_description(),
            frond_page_url=book.get_frond_page_url(),
            is_borrowed=book.get_is_borrowed()
        )
