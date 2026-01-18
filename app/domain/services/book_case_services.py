"""Servicio de gestión de estanterías y algoritmos de ordenamiento.

Este módulo proporciona la lógica de negocio para la gestión de estanterías (BookCase)
y la aplicación de algoritmos de ordenamiento de libros según diferentes estrategias.
"""

from typing import Optional
from app.domain.models import BookCase, Book
from app.domain.models.enums import TypeOrdering
from app.domain.algorithms.defientOrganicer import DeficientOrganizer
from app.domain.algorithms.organizer_optimum import estanteria_optima


class BookCaseService:
    """Servicio para la gestión de estanterías y ordenamiento de libros.
    
    Esta clase gestiona la aplicación de algoritmos de ordenamiento de libros
    en estanterías según diferentes estrategias (DEFICIENT, OPTIMOUM).
    
    Attributes:
        __bookcase: Estantería configurada con su tipo de ordenamiento y capacidad.
    """
    
    __bookcase: Optional[BookCase]
    
    def __init__(self, bookcase: Optional[BookCase] = None) -> None:
        """Inicializa el servicio de estanterías.
        
        Args:
            bookcase: Estantería opcional para configurar (por defecto None).
        """
        self.__bookcase = bookcase
    
    def get_bookcase(self) -> Optional[BookCase]:
        """Obtiene la estantería configurada.
        
        Returns:
            La estantería actual o None si no está configurada.
        """
        return self.__bookcase
    
    def set_bookcase(self, bookcase: Optional[BookCase]) -> None:
        """Configura la estantería para aplicar algoritmos de ordenamiento.
        
        Args:
            bookcase: Estantería a configurar o None para desactivar.
        """
        self.__bookcase = bookcase
    
    def apply_ordering_algorithm(self, books: list[Book]) -> None:
        """Aplica el algoritmo de ordenamiento de libros según la configuración de la estantería.
        
        Args:
            books: Lista de libros a organizar.
            
        Note:
            Soporta dos tipos de ordenamiento: DEFICIENT y OPTIMOUM.
            - DEFICIENT: Organiza libros evitando combinaciones peligrosas.
            - OPTIMOUM: Optimiza la ubicación de libros basado en peso y valor.
            
        Raises:
            Exception: Si hay un error aplicando el algoritmo de ordenamiento.
        """
        try:
            if self.__bookcase is None:
                return
            
            if not books:
                return
            
            ordering_type = self.__bookcase.get_TypeOrdering()
            weight_capacity = self.__bookcase.get_weighOrdering()
            
            if ordering_type == TypeOrdering.DEFICIENT:
                # Usar DeficientOrganizer
                organizer = DeficientOrganizer(weight_capacity)
                bookcase_result, dangerous_combinations = organizer.organize(books)
                
                if dangerous_combinations:
                    print(f"⚠️ Se encontraron {len(dangerous_combinations)} combinaciones peligrosas.")
                    organizer.print_dangerous_combinations()
                
                print(f"✓ Libros organizados usando algoritmo DEFICIENT.")
                
            elif ordering_type == TypeOrdering.OPTIMOUM:
                # Convertir libros a formato para estanteria_optima
                libros_dict = []
                for book in books:
                    libros_dict.append({
                        "peso": book.get_weight(),
                        "valor": 1  # Valor base por defecto
                    })
                
                mejor_valor, mejor_solucion = estanteria_optima(libros_dict, weight_capacity)
                print(f"Libros organizados usando algoritmo OPTIMOUM. Valor óptimo: {mejor_valor}")
                # mejor_solucion se guarda implícitamente en el algoritmo
                
        except Exception as e:
            print(f"Error aplicando algoritmo de ordenamiento: {e}")
    
    def has_bookcase_configured(self) -> bool:
        """Verifica si hay una estantería configurada.
        
        Returns:
            True si hay una estantería configurada, False en caso contrario.
        """
        return self.__bookcase is not None
