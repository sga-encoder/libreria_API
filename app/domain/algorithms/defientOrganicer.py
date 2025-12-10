"""
Módulo que implementa el algoritmo de organización deficiente para libros.

Utiliza un enfoque de fuerza bruta basado en el problema de la mochila
para organizar libros en estantes, identificando combinaciones peligrosas
que superan el umbral de capacidad de peso.
"""
from typing import List, Tuple
from ..models.book import Book
from ..models.bookshelf import BookShelf
from ..models.bookcase import BookCase
from ..models.enums import TypeOrdering


class DeficientOrganizer:
    """
    Organizador deficiente que utiliza fuerza bruta para crear todas las
    combinaciones posibles de libros en estantes.
    
    Este algoritmo genera todos los BookShelf posibles con combinaciones
    de libros que no superen el umbral de peso. Las combinaciones que
    superan el umbral son registradas como peligrosas.
    """
    
    def __init__(self, weight_capacity: float):
        """
        Inicializa el organizador deficiente.
        
        Args:
            weight_capacity: Capacidad máxima de peso por estante (BookShelf)
        """
        self._weight_capacity = weight_capacity
        self._dangerous_combinations: List[Tuple[List[Book], float]] = []
        
    def organize(self, books: List[Book]) -> Tuple[BookCase, List[Tuple[List[Book], float]]]:
        """
        Organiza los libros usando fuerza bruta y detecta combinaciones peligrosas.
        
        Este método implementa un algoritmo de fuerza bruta basado en el problema
        de la mochila:
        1. Crea un BookCase de tipo DEFICIENT
        2. Genera todas las combinaciones posibles de libros
        3. Para cada combinación que NO supere la capacidad, crea un BookShelf
        4. Para cada combinación que SUPERE la capacidad, la registra como peligrosa
        5. Continúa hasta que todos los libros estén almacenados
        6. Retorna el BookCase con todos los BookShelf y las combinaciones peligrosas
        
        Args:
            books: Lista de libros del inventario organizado a almacenar
            
        Returns:
            Tupla con (BookCase, lista de combinaciones peligrosas)
            donde cada combinación peligrosa es (lista_libros, peso_total)
        """
        if not books:
            # Crear BookCase vacío
            empty_bookcase = BookCase(
                stands=BookShelf([]),
                TypeOrdering=TypeOrdering.DEFICIENT,
                weighCapacity=self._weight_capacity,
                capacityStands=0,
                store=[]
            )
            return empty_bookcase, []
        
        # Reiniciar combinaciones peligrosas
        self._dangerous_combinations = []
        
        # Lista para almacenar todos los BookShelf creados
        all_bookshelves: List[BookShelf] = []
        
        # Conjunto para rastrear qué libros ya han sido almacenados
        stored_books = set()
        
        # Generar todas las combinaciones posibles de libros
        # Usando fuerza bruta: probamos todas las combinaciones de tamaño 1 hasta n
        n = len(books)
        
        for size in range(1, n + 1):
            # Generar todas las combinaciones de este tamaño
            combinations = self._generate_combinations(books, size)
            
            for combination in combinations:
                # Calcular peso total de esta combinación
                total_weight = sum(book.get_weight() for book in combination)
                
                # Verificar si supera el umbral de riesgo
                if total_weight > self._weight_capacity:
                    # Combinación peligrosa: registrarla
                    self._dangerous_combinations.append((combination, total_weight))
                else:
                    # Combinación segura: crear un BookShelf
                    # Solo crear si al menos un libro no ha sido almacenado
                    has_new_books = any(id(book) not in stored_books for book in combination)
                    
                    if has_new_books:
                        # Crear un nuevo BookShelf con esta combinación
                        bookshelf = BookShelf(books=combination)
                        all_bookshelves.append(bookshelf)
                        
                        # Marcar estos libros como almacenados
                        for book in combination:
                            stored_books.add(id(book))
                
                # Verificar si todos los libros ya están almacenados
                if len(stored_books) >= len(books):
                    break
            
            # Verificar si todos los libros ya están almacenados
            if len(stored_books) >= len(books):
                break
        
        # Crear el BookCase con todos los BookShelf generados
        bookcase = BookCase(
            stands=all_bookshelves if all_bookshelves else BookShelf([]),
            TypeOrdering=TypeOrdering.DEFICIENT,
            weighCapacity=self._weight_capacity,
            capacityStands=len(all_bookshelves),
            store=books
        )
        
        return bookcase, self._dangerous_combinations
    
    def _generate_combinations(self, books: List[Book], size: int) -> List[List[Book]]:
        """
        Genera todas las combinaciones posibles de libros de un tamaño específico.
        
        Args:
            books: Lista de libros
            size: Tamaño de las combinaciones
            
        Returns:
            Lista de todas las combinaciones posibles
        """
        if size == 0:
            return [[]]
        if size > len(books):
            return []
        
        combinations = []
        
        # Algoritmo de fuerza bruta para generar combinaciones
        def backtrack(start: int, current_combination: List[Book]):
            if len(current_combination) == size:
                combinations.append(current_combination[:])
                return
            
            for i in range(start, len(books)):
                current_combination.append(books[i])
                backtrack(i + 1, current_combination)
                current_combination.pop()
        
        backtrack(0, [])
        return combinations
    
    def get_dangerous_combinations(self) -> List[Tuple[List[Book], float]]:
        """
        Obtiene la lista de combinaciones peligrosas encontradas.
        
        Returns:
            Lista de tuplas (lista_libros, peso_total) que superan el umbral
        """
        return self._dangerous_combinations
    
    def get_weight_capacity(self) -> float:
        """
        Obtiene la capacidad de peso configurada.
        
        Returns:
            Capacidad máxima de peso por estante
        """
        return self._weight_capacity
    
    def print_dangerous_combinations(self) -> None:
        """
        Imprime un reporte de todas las combinaciones peligrosas encontradas.
        """
        if not self._dangerous_combinations:
            print("No se encontraron combinaciones peligrosas.")
            return
        
        print(f"\n{'='*60}")
        print(f"REPORTE DE COMBINACIONES PELIGROSAS")
        print(f"{'='*60}")
        print(f"Capacidad máxima: {self._weight_capacity} kg")
        print(f"Total de combinaciones peligrosas: {len(self._dangerous_combinations)}\n")
        
        for idx, (combination, total_weight) in enumerate(self._dangerous_combinations, 1):
            excess = total_weight - self._weight_capacity
            print(f"Combinación #{idx}:")
            print(f"  Peso total: {total_weight:.2f} kg (Exceso: {excess:.2f} kg)")
            print(f"  Libros en la combinación:")
            for book in combination:
                print(f"    - {book.get_title()} ({book.get_weight():.2f} kg)")
            print()
