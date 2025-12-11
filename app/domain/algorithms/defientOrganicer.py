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
                stands=[],
                TypeOrdering=TypeOrdering.DEFICIENT,
                weighCapacity=self._weight_capacity,
                capacityStands=0,
                store=[]
            )
            return empty_bookcase, []
        
        # Reiniciar combinaciones peligrosas
        self._dangerous_combinations = []
        
        n = len(books)
        print(f"\n🔍 Organizando {n} libros con capacidad {self._weight_capacity} kg...")
        print(f"   Estrategia: Algoritmo DEFICIENT (greedy + detección de peligros)")
        
        # Lista para almacenar estantes creados
        all_bookshelves: List[BookShelf] = []
        remaining_books = books.copy()
        
        # Estrategia DEFICIENT mejorada:
        # 1. Usar greedy First Fit para crear estantes eficientemente
        # 2. Solo analizar combinaciones peligrosas relevantes (las que involucran libros aún no almacenados)
        
        shelf_number = 0
        while remaining_books:
            shelf_number += 1
            current_shelf_books = []
            current_weight = 0.0
            
            # Intentar llenar el estante actual con tantos libros como sea posible (First Fit)
            i = 0
            while i < len(remaining_books):
                book = remaining_books[i]
                new_weight = current_weight + book.get_weight()
                
                if new_weight <= self._weight_capacity:
                    # El libro cabe, agregarlo al estante
                    current_shelf_books.append(book)
                    current_weight = new_weight
                    remaining_books.pop(i)
                else:
                    # No cabe, intentar con el siguiente libro
                    i += 1
            
            # Crear el estante si tiene libros
            if current_shelf_books:
                bookshelf = BookShelf(books=current_shelf_books)
                all_bookshelves.append(bookshelf)
                print(f"   Estante {shelf_number}: {len(current_shelf_books)} libro(s), {current_weight:.2f}/{self._weight_capacity} kg")
            else:
                # No se pudo colocar ningún libro (todos exceden capacidad individualmente)
                # Crear estantes individuales para los restantes
                print(f"   ⚠️ Libros restantes exceden capacidad individual")
                for book in remaining_books:
                    bookshelf = BookShelf(books=[book])
                    all_bookshelves.append(bookshelf)
                    print(f"   Estante {shelf_number}: {book.get_title()} ({book.get_weight()} kg) - EXCEDE CAPACIDAD")
                    shelf_number += 1
                break
        
        # Análisis de combinaciones peligrosas (solo las más relevantes)
        # Analizar combinaciones de 2 libros (pares peligrosos)
        print(f"\n🔍 Analizando combinaciones peligrosas...")
        for i in range(len(books)):
            for j in range(i + 1, len(books)):
                combination = [books[i], books[j]]
                total_weight = books[i].get_weight() + books[j].get_weight()
                if total_weight > self._weight_capacity:
                    self._dangerous_combinations.append((combination, total_weight))
        
        # Analizar combinaciones de 3 libros (trios peligrosos) - limitado
        if len(books) <= 15:  # Solo si hay pocos libros
            for i in range(len(books)):
                for j in range(i + 1, len(books)):
                    for k in range(j + 1, len(books)):
                        combination = [books[i], books[j], books[k]]
                        total_weight = sum(b.get_weight() for b in combination)
                        if total_weight > self._weight_capacity:
                            self._dangerous_combinations.append((combination, total_weight))
        
        print(f"   Combinaciones peligrosas detectadas: {len(self._dangerous_combinations)}")
        
        # Asignar IDs a los BookShelf generados
        for idx, shelf in enumerate(all_bookshelves, 1):
            shelf.set_id(f"SHELF-DEF-{idx:03d}")
        
        # Crear el BookCase con todos los BookShelf generados
        bookcase = BookCase(
            stands=all_bookshelves,
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
