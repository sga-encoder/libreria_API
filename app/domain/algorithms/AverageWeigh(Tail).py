"""
Módulo para calcular el peso promedio de libros por autor usando recursión de cola.

Este algoritmo implementa tail recursion (recursión de cola) para procesar
una lista de libros y calcular el peso promedio de aquellos que pertenecen
a un autor específico.

Características:
- Recursión de cola optimizable por el compilador/intérprete
- Acumuladores para suma de pesos y contador de libros
- Logging detallado de cada llamada recursiva para demostración educativa
"""

from typing import List, Dict, Any


def calculate_average_weight_tail(
    books: List[Any],
    author: str,
    index: int = 0,
    total_weight: float = 0.0,
    count: int = 0,
    depth: int = 0
) -> float:
    """
    Calcula el peso promedio de los libros de un autor usando recursión de cola.
    
    Esta función utiliza tail recursion con acumuladores para evitar el crecimiento
    de la pila de llamadas. Los acumuladores mantienen el estado entre llamadas:
    - total_weight: suma acumulada de pesos de libros del autor
    - count: número de libros del autor encontrados
    - index: posición actual en la lista de libros
    
    Args:
        books: Lista de objetos Book o diccionarios con información de libros.
        author: Nombre del autor cuyos libros se quieren procesar.
        index: Índice actual en la lista (inicia en 0).
        total_weight: Acumulador de la suma de pesos (inicia en 0.0).
        count: Acumulador del número de libros encontrados (inicia en 0).
        depth: Nivel de profundidad de la recursión (para logging).
    
    Returns:
        float: Peso promedio de los libros del autor.
               Retorna 0.0 si no se encuentran libros del autor.
    
    Nota:
        La función imprime en consola cada paso de la recursión para
        fines educativos, mostrando el estado de los acumuladores.
    
    Ejemplos:
        >>> books = [book1, book2, book3]
        >>> avg = calculate_average_weight_tail(books, "J.R.R. Tolkien")
        >>> print(f"Peso promedio: {avg} kg")
    """
    # Caso base: hemos procesado todos los libros
    if index >= len(books):
        # Logging del caso base
        print(f"{'  ' * depth}[RECURSIÓN COLA - Nivel {depth}] CASO BASE ALCANZADO")
        print(f"{'  ' * depth}├─ Total de libros procesados: {len(books)}")
        print(f"{'  ' * depth}├─ Libros del autor '{author}': {count}")
        print(f"{'  ' * depth}├─ Peso total acumulado: {total_weight:.2f} kg")
        
        if count == 0:
            print(f"{'  ' * depth}└─ RESULTADO: 0.0 kg (no se encontraron libros)")
            return 0.0
        
        average = total_weight / count
        print(f"{'  ' * depth}└─ RESULTADO: {average:.4f} kg (promedio = {total_weight:.2f} / {count})")
        return average
    
    # Obtener el libro actual
    current_book = books[index]
    
    # Extraer información del libro (puede ser objeto Book o diccionario)
    if hasattr(current_book, 'get_author'):
        book_author = current_book.get_author()
        book_weight = current_book.get_weight()
        book_title = current_book.get_title()
    else:
        book_author = current_book.get('author', '')
        book_weight = current_book.get('weight', 0.0)
        book_title = current_book.get('title', 'Sin título')
    
    # Logging del paso actual
    print(f"{'  ' * depth}[RECURSIÓN COLA - Nivel {depth}] Procesando libro {index + 1}/{len(books)}")
    print(f"{'  ' * depth}├─ Título: '{book_title}'")
    print(f"{'  ' * depth}├─ Autor: '{book_author}'")
    print(f"{'  ' * depth}├─ Peso: {book_weight} kg")
    
    # Verificar si el libro pertenece al autor buscado
    if book_author == author:
        new_total_weight = total_weight + book_weight
        new_count = count + 1
        
        print(f"{'  ' * depth}├─ ✓ COINCIDE con autor buscado '{author}'")
        print(f"{'  ' * depth}├─ Acumuladores actualizados:")
        print(f"{'  ' * depth}│  ├─ total_weight: {total_weight:.2f} + {book_weight} = {new_total_weight:.2f} kg")
        print(f"{'  ' * depth}│  └─ count: {count} + 1 = {new_count}")
        print(f"{'  ' * depth}└─ → Llamada recursiva con acumuladores actualizados\n")
        
        # Llamada recursiva de cola con acumuladores actualizados
        return calculate_average_weight_tail(
            books, 
            author, 
            index + 1, 
            new_total_weight, 
            new_count, 
            depth + 1
        )
    else:
        print(f"{'  ' * depth}├─ ✗ NO coincide (buscando '{author}')")
        print(f"{'  ' * depth}├─ Acumuladores sin cambios:")
        print(f"{'  ' * depth}│  ├─ total_weight: {total_weight:.2f} kg")
        print(f"{'  ' * depth}│  └─ count: {count}")
        print(f"{'  ' * depth}└─ → Llamada recursiva sin actualizar acumuladores\n")
        
        # Llamada recursiva de cola sin actualizar acumuladores
        return calculate_average_weight_tail(
            books, 
            author, 
            index + 1, 
            total_weight, 
            count, 
            depth + 1
        )


def get_average_weight_by_author(books: List[Any], author: str) -> Dict[str, Any]:
    """
    Función wrapper que calcula el peso promedio y retorna información detallada.
    
    Esta función inicia la recursión de cola y recolecta información adicional
    sobre los libros del autor para retornar un resultado completo.
    
    Args:
        books: Lista de objetos Book o diccionarios con información de libros.
        author: Nombre del autor cuyos libros se quieren analizar.
    
    Returns:
        dict: Diccionario con:
            - author: nombre del autor
            - average_weight: peso promedio de sus libros
            - total_books: cantidad de libros del autor
            - books: lista de libros con título, ISBN y peso
    
    Ejemplos:
        >>> result = get_average_weight_by_author(books, "Gabriel García Márquez")
        >>> print(f"Peso promedio: {result['average_weight']} kg")
    """
    print("=" * 80)
    print(f"INICIANDO CÁLCULO DE PESO PROMEDIO - RECURSIÓN DE COLA")
    print(f"Autor buscado: '{author}'")
    print(f"Total de libros en inventario: {len(books)}")
    print("=" * 80)
    print()
    
    # Ejecutar la recursión de cola
    average_weight = calculate_average_weight_tail(books, author)
    
    print()
    print("=" * 80)
    print("RECURSIÓN COMPLETADA")
    print("=" * 80)
    
    # Recolectar información de los libros del autor
    author_books = []
    for book in books:
        if hasattr(book, 'get_author'):
            if book.get_author() == author:
                author_books.append({
                    "title": book.get_title(),
                    "isbn": book.get_id_IBSN(),
                    "weight": book.get_weight()
                })
        else:
            if book.get('author', '') == author:
                author_books.append({
                    "title": book.get('title', 'Sin título'),
                    "isbn": book.get('id_IBSN', ''),
                    "weight": book.get('weight', 0.0)
                })
    
    return {
        "author": author,
        "average_weight": round(average_weight, 4),
        "total_books": len(author_books),
        "books": author_books
    }


__all__ = ['calculate_average_weight_tail', 'get_average_weight_by_author']
