import logging
from app.persistence.repositories import BooksRepositorySQL
from app.domain.models import Book
from app.domain.exceptions import ValidationException, ResourceNotFoundException, RepositoryException
from app.domain.algorithms import insertion_sort

class BookService:
    """Servicio para gestionar libros con lógica de negocio."""
    
    def __init__(self, repo: BooksRepositorySQL):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        if repo is None:
            raise ValidationException("Repositorio no puede ser None")
        
        self._repository = repo
        self._books = []
        self.__load()
        self.logger.info("BookService inicializado")
    
    def __load(self) -> None:
        """Carga y ordena libros desde el repositorio."""
        try:
            self.logger.debug("Iniciando carga de libros...")
            books_orm = self._repository.read_all()
            
            if books_orm is None:
                self.logger.warning("No hay libros en la BD")
                self._books = []
            else:
                self._books = [
                    self._repository.orm_to_domain(orm_book) 
                    for orm_book in books_orm
                ]
                self._books = insertion_sort(self._books, key=lambda b: b.get_id_IBSN())
                self.logger.info(f"{len(self._books)} libros cargados y ordenados")
                
        except Exception as e:
            self.logger.error(f"Error cargando libros: {e}", exc_info=True)
            raise RepositoryException(f"Error crítico al cargar libros: {e}")
    
    def add(self, json: dict) -> Book:
        """Crea un nuevo libro."""
        try:
            # Crear libro del dominio
            book = Book.from_dict(json)
            
            # Persistir en BD
            book_orm = self._repository.create(
                id_IBSN=book.get_id_IBSN(),
                title=book.get_title(),
                author=book.get_author(),
                gender=book.get_gender(),
                weight=book.get_weight(),
                price=book.get_price(),
                description=book.get_description(),
                frond_page_url=book.get_frond_page_url(),
                is_borrowed=book.get_is_borrowed(),
            )
            
            # Convertir a dominio
            book_domain = self._repository.orm_to_domain(book_orm)
            self._books.append(book_domain)
            self._books = insertion_sort(self._books, key=lambda b: b.get_id_IBSN())
            
            self.logger.info(f"Libro {book_domain.get_id_IBSN()} creado: {book_domain.get_title()}")
            return book_domain
            
        except ValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error creando libro: {e}", exc_info=True)
            raise RepositoryException(f"Error creando libro: {e}")
    
    def get_all(self) -> list[Book]:
        """Obtiene todos los libros."""
        try:
            books_orm = self._repository.read_all()
            if books_orm is None:
                return []
            return [self._repository.orm_to_domain(orm_b) for orm_b in books_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo libros: {e}")
            raise RepositoryException(f"Error obteniendo libros: {e}")
    
    def get_by_isbn(self, isbn: str) -> Book | None:
        """Obtiene un libro por ISBN."""
        try:
            book_orm = self._repository.read_by_isbn(isbn)
            if not book_orm:
                return None
            return self._repository.orm_to_domain(book_orm)
        except Exception as e:
            self.logger.error(f"Error obteniendo libro: {e}")
            raise RepositoryException(f"Error obteniendo libro: {e}")
    
    def get_by_title(self, title: str) -> list[Book]:
        """Obtiene libros por título."""
        try:
            books_orm = self._repository.read_by_title(title)
            if not books_orm:
                return []
            return [self._repository.orm_to_domain(orm_b) for orm_b in books_orm]
        except Exception as e:
            self.logger.error(f"Error buscando libros por título: {e}")
            raise RepositoryException(f"Error buscando libros: {e}")
    
    def get_by_author(self, author: str) -> list[Book]:
        """Obtiene libros por autor."""
        try:
            books_orm = self._repository.read_by_author(author)
            if not books_orm:
                return []
            return [self._repository.orm_to_domain(orm_b) for orm_b in books_orm]
        except Exception as e:
            self.logger.error(f"Error buscando libros por autor: {e}")
            raise RepositoryException(f"Error buscando libros: {e}")
    
    def get_by_genre(self, genre: str) -> list[Book]:
        """Obtiene libros por género."""
        try:
            books_orm = self._repository.read_by_genre(genre)
            if not books_orm:
                return []
            return [self._repository.orm_to_domain(orm_b) for orm_b in books_orm]
        except Exception as e:
            self.logger.error(f"Error buscando libros por género: {e}")
            raise RepositoryException(f"Error buscando libros: {e}")
    
    def get_available(self) -> list[Book]:
        """Obtiene libros disponibles (no prestados)."""
        try:
            books_orm = self._repository.read_available()
            if not books_orm:
                return []
            return [self._repository.orm_to_domain(orm_b) for orm_b in books_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo libros disponibles: {e}")
            raise RepositoryException(f"Error obteniendo libros disponibles: {e}")
    
    def get_borrowed(self) -> list[Book]:
        """Obtiene libros prestados."""
        try:
            books_orm = self._repository.read_borrowed()
            if not books_orm:
                return []
            return [self._repository.orm_to_domain(orm_b) for orm_b in books_orm]
        except Exception as e:
            self.logger.error(f"Error obteniendo libros prestados: {e}")
            raise RepositoryException(f"Error obteniendo libros prestados: {e}")
    
    def update(self, isbn: str, book_data: dict) -> Book | None:
        """Actualiza un libro."""
        try:
            updated_orm = self._repository.update(isbn, **book_data)
            if updated_orm is None:
                return None
            self.__load()
            self.logger.info(f"Libro {isbn} actualizado")
            return self._repository.orm_to_domain(updated_orm)
        except Exception as e:
            self.logger.error(f"Error actualizando libro: {e}")
            raise RepositoryException(f"Error actualizando libro: {e}")
    
    def delete(self, isbn: str) -> dict:
        """Elimina un libro."""
        try:
            result = self._repository.delete(isbn)
            if result:
                self.__load()
                return {"success": True}
            raise RepositoryException(f"Libro {isbn} no encontrado")
        except Exception as e:
            raise RepositoryException(f"Error eliminando libro: {e}")
    
    def mark_borrowed(self, isbn: str) -> dict:
        """Marca un libro como prestado."""
        try:
            result = self._repository.mark_as_borrowed(isbn)
            if result:
                return {"success": True}
            raise RepositoryException(f"Libro {isbn} no encontrado")
        except Exception as e:
            raise RepositoryException(f"Error marcando libro como prestado: {e}")
    
    def mark_available(self, isbn: str) -> dict:
        """Marca un libro como disponible (devuelto)."""
        try:
            result = self._repository.mark_as_available(isbn)
            if result:
                return {"success": True}
            raise RepositoryException(f"Libro {isbn} no encontrado")
        except Exception as e:
            raise RepositoryException(f"Error marcando libro como disponible: {e}")
