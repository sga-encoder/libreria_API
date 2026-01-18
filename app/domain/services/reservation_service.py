"""Servicio de gestión de cola de reservas con HashMap por ISBN.

Este módulo proporciona la lógica para gestionar las reservas de libros
utilizando un HashMap (diccionario) organizado por ISBN para acceso
O(1) a las reservas de un libro específico.
"""

from typing import Optional, List, Tuple
from app.domain.models import User, Book
from app.domain.structures import Queue


class ReservationQueueService:
    """Servicio para gestionar la cola de reservas de libros.
    
    Utiliza un HashMap internamente donde la clave es el ISBN del libro
    y el valor es una cola FIFO de usuarios esperando ese libro.
    Esto permite acceso eficiente O(1) a las reservas de un libro específico.
    
    Attributes:
        __reservations_map: Diccionario {isbn: Queue[User]} para gestionar reservas.
        __all_reservations: Lista de todas las reservas para rastreo global.
    """
    
    __reservations_map: dict[str, Queue[User]]
    __all_reservations: list[Tuple[str, User, str]]  # (isbn, user, timestamp)
    
    def __init__(self) -> None:
        """Inicializa el servicio de cola de reservas."""
        self.__reservations_map = {}
        self.__all_reservations = []
    
    def add_reservation(self, book: Book, user: User) -> bool:
        """Agrega una reserva para un libro.
        
        Args:
            book: Libro para el que se crea la reserva.
            user: Usuario que realiza la reserva.
            
        Returns:
            True si la reserva se agregó exitosamente, False en caso contrario.
        """
        try:
            isbn = book.get_id_IBSN()
            
            # Crear cola para este ISBN si no existe
            if isbn not in self.__reservations_map:
                self.__reservations_map[isbn] = Queue[User]()
            
            # Agregar usuario a la cola
            self.__reservations_map[isbn].push(user)
            
            # Registrar en historial de todas las reservas
            from datetime import datetime
            self.__all_reservations.append((isbn, user, datetime.now().isoformat()))
            
            print(f"✅ Reserva agregada: {user.get_email()} para libro ISBN {isbn}")
            return True
        except Exception as e:
            print(f"❌ Error agregando reserva: {e}")
            return False
    
    def get_next_reservation(self, book: Book) -> Optional[User]:
        """Obtiene el próximo usuario en espera para un libro sin eliminar la reserva.
        
        Args:
            book: Libro para el que se consulta la reserva.
            
        Returns:
            El usuario que espera el libro o None si no hay reservas.
        """
        try:
            isbn = book.get_id_IBSN()
            if isbn not in self.__reservations_map:
                return None
            
            queue = self.__reservations_map[isbn]
            return queue.peek()
        except Exception as e:
            print(f"❌ Error obteniendo próxima reserva: {e}")
            return None
    
    def pop_reservation(self, book: Book) -> Optional[User]:
        """Extrae y devuelve el próximo usuario en espera para un libro.
        
        Args:
            book: Libro para el que se procesa la reserva.
            
        Returns:
            El usuario que espera el libro o None si no hay reservas.
        """
        try:
            isbn = book.get_id_IBSN()
            if isbn not in self.__reservations_map:
                return None
            
            queue = self.__reservations_map[isbn]
            user = queue.pop()
            
            # Limpiar cola vacía del mapa
            if queue.is_empty():
                del self.__reservations_map[isbn]
            
            if user:
                print(f"📚 Reserva procesada: {user.get_email()} para libro ISBN {isbn}")
            return user
        except Exception as e:
            print(f"❌ Error procesando reserva: {e}")
            return None
    
    def has_reservations_for_book(self, book: Book) -> bool:
        """Verifica si hay reservas pendientes para un libro.
        
        Args:
            book: Libro a verificar.
            
        Returns:
            True si hay al menos una reserva, False en caso contrario.
        """
        try:
            isbn = book.get_id_IBSN()
            if isbn not in self.__reservations_map:
                return False
            
            queue = self.__reservations_map[isbn]
            return not queue.is_empty()
        except Exception as e:
            print(f"❌ Error verificando reservas: {e}")
            return False
    
    def get_reservations_count_for_book(self, book: Book) -> int:
        """Obtiene el número de reservas pendientes para un libro.
        
        Args:
            book: Libro a consultar.
            
        Returns:
            Número de usuarios esperando por el libro.
        """
        try:
            isbn = book.get_id_IBSN()
            if isbn not in self.__reservations_map:
                return 0
            
            queue = self.__reservations_map[isbn]
            return len(queue)
        except Exception as e:
            print(f"❌ Error contando reservas: {e}")
            return 0
    
    def get_all_reservations_for_book(self, book: Book) -> List[User]:
        """Obtiene todos los usuarios en espera para un libro.
        
        Args:
            book: Libro a consultar.
            
        Returns:
            Lista de usuarios en orden de espera (FIFO).
        """
        try:
            isbn = book.get_id_IBSN()
            if isbn not in self.__reservations_map:
                return []
            
            queue = self.__reservations_map[isbn]
            return queue.to_list()
        except Exception as e:
            print(f"❌ Error obteniendo reservas del libro: {e}")
            return []
    
    def remove_user_from_all_reservations(self, user: User) -> bool:
        """Elimina un usuario de todas sus reservas pendientes.
        
        Args:
            user: Usuario a eliminar de las reservas.
            
        Returns:
            True si se encontró y eliminó al menos una reserva, False en caso contrario.
        """
        try:
            user_id = user.get_id()
            found = False
            
            # Revisar todas las colas
            isbns_to_remove = []
            for isbn, queue in self.__reservations_map.items():
                users_list = queue.to_list()
                # Crear nueva cola sin el usuario
                new_queue = Queue[User]()
                for u in users_list:
                    if u.get_id() != user_id:
                        new_queue.push(u)
                    else:
                        found = True
                
                # Actualizar o eliminar cola
                if new_queue.is_empty():
                    isbns_to_remove.append(isbn)
                else:
                    self.__reservations_map[isbn] = new_queue
            
            # Limpiar colas vacías
            for isbn in isbns_to_remove:
                del self.__reservations_map[isbn]
            
            if found:
                print(f"✅ Usuario {user.get_email()} eliminado de todas las reservas")
            return found
        except Exception as e:
            print(f"❌ Error eliminando usuario de reservas: {e}")
            return False
    
    def get_user_position_in_queue(self, user: User, book: Book) -> Optional[int]:
        """Obtiene la posición de un usuario en la cola de espera de un libro.
        
        Args:
            user: Usuario a buscar.
            book: Libro cuya cola se consulta.
            
        Returns:
            Posición en la cola (0-indexed) o None si no está reservado.
        """
        try:
            isbn = book.get_id_IBSN()
            if isbn not in self.__reservations_map:
                return None
            
            queue = self.__reservations_map[isbn]
            users_list = queue.to_list()
            
            for idx, u in enumerate(users_list):
                if u.get_id() == user.get_id():
                    return idx
            
            return None
        except Exception as e:
            print(f"❌ Error obteniendo posición en cola: {e}")
            return None
    
    def clear_reservations_for_book(self, book: Book) -> bool:
        """Limpia todas las reservas pendientes de un libro.
        
        Args:
            book: Libro cuyas reservas se limpiarán.
            
        Returns:
            True si se limpiaron reservas, False si no había ninguna.
        """
        try:
            isbn = book.get_id_IBSN()
            if isbn not in self.__reservations_map:
                return False
            
            del self.__reservations_map[isbn]
            print(f"✅ Reservas del libro ISBN {isbn} eliminadas")
            return True
        except Exception as e:
            print(f"❌ Error limpiando reservas: {e}")
            return False
    
    def get_total_reservations(self) -> int:
        """Obtiene el número total de reservas en el sistema.
        
        Returns:
            Total de usuarios en espera por algún libro.
        """
        try:
            total = 0
            for queue in self.__reservations_map.values():
                total += len(queue)
            return total
        except Exception as e:
            print(f"❌ Error contando total de reservas: {e}")
            return 0
    
    def get_all_pending_reservations(self) -> dict[str, List[User]]:
        """Obtiene todas las reservas pendientes organizadas por ISBN.
        
        Returns:
            Diccionario {isbn: [usuarios]} con las reservas pendientes.
        """
        try:
            result = {}
            for isbn, queue in self.__reservations_map.items():
                result[isbn] = queue.to_list()
            return result
        except Exception as e:
            print(f"❌ Error obteniendo todas las reservas: {e}")
            return {}
    
    def is_empty(self) -> bool:
        """Verifica si no hay reservas pendientes.
        
        Returns:
            True si no hay reservas, False si hay al menos una.
        """
        return len(self.__reservations_map) == 0
