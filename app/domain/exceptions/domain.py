from .base import LibraryException

class ResourceNotFoundException(LibraryException):
    """Recurso no encontrado (libro, usuario, préstamo)"""
    pass

class ResourceAlreadyExistsException(LibraryException):
    """Recurso ya existe"""
    pass

class BookAlreadyBorrowedException(LibraryException):  # Ya existe
    """Libro ya prestado"""
    pass

class InvalidOperationException(LibraryException):
    """Operación no válida en el estado actual"""
    pass