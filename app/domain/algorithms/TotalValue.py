"""
Módulo que implementa el cálculo del valor total de libros de un autor.

Utiliza recursión y una estructura de pila (Stack) para procesar todos los libros
y calcular el valor total de aquellos que pertenecen a un autor específico.
"""
from app.domain.structures import Stack as StackStructure
from app.domain.models import Book
from typing import List, Optional


def TotalValue(books: List[Book], author: str, stack: Optional[StackStructure] = None, accumulated: float = 0.0) -> float:
    """
    Calcula recursivamente el valor total de todos los libros de un autor específico.
    
    Esta función utiliza una pila (Stack) para procesar los libros de forma recursiva.
    En la primera llamada, crea la pila y añade todos los libros. Luego, va sacando
    libros uno por uno y sumando el precio de aquellos que pertenecen al autor.
    
    Args:
        books (List[Book]): Lista de libros a procesar.
        author (str): Nombre del autor cuyos libros se quieren valorar.
        stack (Optional[StackStructure]): Pila interna para el procesamiento recursivo.
            Se crea automáticamente en la primera llamada.
        accumulated (float): Valor acumulado en las llamadas recursivas.
    
    Returns:
        float: Valor total de todos los libros del autor especificado.
    
    Ejemplos:
        >>> books = [book1, book2, book3]
        >>> total = TotalValue(books, "Gabriel García Márquez")
        >>> print(f"Valor total: ${total:.2f}")
    """
    # CASO BASE 1: Primera llamada - crear pila e introducir todos los libros
    if stack is None:
        stack = StackStructure()
        for book in books:
            stack.push(book)
    
    # CASO BASE 2: Pila vacía - retornar el valor acumulado
    if stack.is_empty():
        return accumulated
    
    # PASO RECURSIVO: Sacar libro del tope de la pila
    current_book = stack.pop()
    
    # Si el libro pertenece al autor, sumar su precio
    new_accumulated = accumulated
    if current_book.get_author() == author:
        new_accumulated += current_book.get_price()
    
    # LLAMADA RECURSIVA: Procesar los libros restantes en la pila
    return TotalValue(books, author, stack, new_accumulated)
