from typing import Optional
from datetime import datetime
from app.domain.models import Loan, Book, User
from .interface import RepositoriesInterface
from app.domain.structures import Queue
from app.domain.algorithms import linear_search, insertion_sort
from app.utils import FileManager, FileType


class LoansRepository(RepositoriesInterface[Loan]):
    """Repositorio para gestionar préstamos (historial y activos).

    Encapsula operaciones de creación, lectura, actualización y eliminación
    de préstamos, manteniendo una caché sincronizada con los archivos
    de persistencia: JSON para el historial de préstamos y CSV para los préstamos
    activos. Provee búsquedas por `id`, listado y desactivación de préstamos.
    """
    __file_history_loans: FileManager
    __file_active_loans: FileManager
    __history_loans: list[dict]
    __active_loans: list[dict]

    def __init__(self, url_loans: str, url_active_loans: str) -> None:
        """Inicializa el repositorio con las rutas de persistencia.

        - `url_loans`: ruta del archivo JSON con el historial de préstamos.
        - `url_active_loans`: ruta del archivo CSV con los IDs de préstamos activos.
        """
        self.__file_history_loans = FileManager(url_loans, FileType.JSON)
        self.__file_active_loans = FileManager(url_active_loans, FileType.CSV, ["ids_actives_loans"])
        self.__history_loans = self.__file_history_loans.read()
        self.__active_loans = self.__file_active_loans.read()

    def __refresh_history_loans(self):
        """Recarga la caché interna desde el archivo.

        La caché se sobrescribe con el contenido actual del archivo para
        asegurar consistencia antes de operaciones de búsqueda o lectura.
        """
        self.__history_loans = self.__file_history_loans.read()
        
    def __refresh_active_loans(self):
        """Recarga la caché interna del historial desde el archivo.

        La caché se sobrescribe con el contenido actual del archivo para
        asegurar consistencia antes de operaciones de búsqueda o lectura.
        """
        self.__active_loans = self.__file_active_loans.read()
        

    def __search_id_in_history_loans(self, id: str) -> int:
        """Busca el índice del préstamo por `id` dentro del historial.

        Refresca previamente la caché del historial para garantizar consistencia.

        Retorna el índice si existe; `-1` en caso contrario.
        """
        self.__refresh_history_loans()
        index = linear_search(
            self.__history_loans,
            key=lambda loan: loan["id"],
            item=id
        )
        return index
    
    def __search_id_loan_in_active_loans(self, id: str) -> int:
        """Busca el índice del `id` de préstamo dentro de la lista de activos.

        Refresca previamente la caché de activos para garantizar consistencia.

        Retorna el índice si existe; `-1` en caso contrario.
        """
        self.__refresh_active_loans()
        index = linear_search(
            self.__active_loans,
            key=lambda loan: loan["ids_actives_loans"],
            item=id
        )
        return index

    def __search_loan_in_history_loans(self, id: str) -> dict | int:
        """Obtiene el registro del préstamo en el historial por `id`.

        Retorna:
        - `dict` con la información del préstamo si existe.
        - `-1` si no se encontró.
        """
        index = self.__search_id_in_history_loans(id)
        return self.__history_loans[index] if index != -1 else -1
    
    def __active_loan(self, id: str) -> None:
        """Marca un préstamo como activo.

        Agrega el `id` del préstamo al archivo de activos (CSV) y
        refresca la caché interna de activos.
        """
        self.__file_active_loans.append({"ids_actives_loans": id})
        self.__refresh_active_loans()

    def create(self, json: dict) -> Loan:
        """Crea un préstamo, lo persiste en historial y lo activa.

        Parámetros:
        - `json`: datos del préstamo en forma de diccionario.

        Retorna:
        - Instancia de `Loan` creada y marcada como activa.
        """
        # Agregar fecha del préstamo si no existe
        if "loan_date" not in json:
                json["loan_date"] = datetime.now().isoformat()
        instance = Loan.from_dict(json)
        self.__file_history_loans.append(instance.to_dict())
        self.__refresh_history_loans()
        self.__active_loan(instance.get_id())
        return instance
    
    def read_in_history_loan(self, id_loan: str) -> Loan | None:
        """Lee un préstamo del historial por su `id`.

        Si no existe, imprime un mensaje informativo y retorna `None`.

        Retorna:
        - `Loan` si el registro se encuentra en el historial.
        - `None` si no existe.
        """
        loan = self.__search_loan_in_history_loans(id_loan)
        if loan == -1:
            print(f"Loan with id {id_loan} not found.")
            return None
        instance = Loan.from_dict(loan)
        return instance
    
    def read(self, id: str) -> Loan | None:
        """Lee un préstamo activo por su `id`.

        Si no existe en activos, imprime un mensaje informativo y retorna `None`.

        Retorna:
        - `Loan` si el préstamo está activo.
        - `None` si no está activo.
        """
        index = self.__search_id_loan_in_active_loans(id)
        if index == -1:
            print(f"Loan with id {id} not found in active loans.")
            return None
        loan_dict = self.__search_loan_in_history_loans(id)
        instance = Loan.from_dict(loan_dict)
        return instance

    def read_all_history_loans(self) -> list[Loan] | None:
        """Retorna todos los préstamos registrados en el historial.

        Refresca la caché del historial y construye objetos `Loan`.

        Retorna:
        - Lista de `Loan` si hay registros.
        - `None` si el historial está vacío.
        """
        self.__refresh_history_loans()
        if not self.__history_loans:
            print("No loans found in the repository.")
            return None
        loans = []
        for data in self.__history_loans:
            loan = Loan.from_dict(data)
            loans.append(loan)
        return loans
    
    def read_all(self) -> list[Loan] | None:
        """Retorna los préstamos activos como instancias de `Loan`.

        Carga la lista de préstamos activos (IDs), resuelve cada uno contra
        el historial y los convierte a instancias de `Loan`. Si un préstamo
        no se encuentra en el historial, se omite con un aviso. Finalmente
        ordena los resultados por `id`.

        Retorna:
        - Lista de `Loan` activos ordenados por `id`.
        - `None` si no hay préstamos activos.
        """
        self.__refresh_active_loans()
        if not self.__active_loans:
            print("No history records found in the repository.")
            return None
        loans = []
        for active_loan_entry in self.__active_loans:
            # Extraer el ID del préstamo del diccionario CSV
            id_loan = active_loan_entry.get("ids_actives_loans") if isinstance(active_loan_entry, dict) else active_loan_entry
            loan_dict = self.__search_loan_in_history_loans(id_loan)
            if loan_dict == -1:
                print(f"Warning: Active loan {id_loan} not found in history. Skipping.")
                continue
            loan_instance = Loan.from_dict(loan_dict)
            loans.append(loan_instance)
        # Ordenar todos los préstamos al final (más eficiente que dentro del loop)
        if loans:
            loans = insertion_sort(
                loans, 
                key=lambda loan: loan.get_id(),
            )
        return loans

    def update(self, id: str, json: dict) -> Loan | None:
        """Actualiza los campos de un préstamo del historial.

        Parámetros:
        - `id`: identificador del préstamo a actualizar.
        - `json`: diccionario con los campos a modificar.

        Retorna:
        - `Loan` actualizado si existe.
        - `None` si no se encontró el préstamo.
        """
        index = self.__search_id_in_history_loans(id)
        if index == -1:
            print(f"Loan with id {id} not found for update.")
            return None
        instance = Loan.from_dict(self.__history_loans[index])
        instance.update_from_dict(json)
        self.__history_loans[index] = instance.to_dict()
        
        self.__file_history_loans.write(self.__history_loans)
        return instance
    
    def __disable_loan(self, id: str) -> None:
        """Desactiva un préstamo eliminándolo del archivo de activos.

        Si el `id` no está en activos, imprime un mensaje y no realiza cambios.
        """
        index = self.__search_id_loan_in_active_loans(id)
        if index == -1:
            print(f"Loan with id {id} not found in active loans for disabling.")
            return
        self.__active_loans.pop(index)
        self.__file_active_loans.write(self.__active_loans)

    def delete(self, id: str) -> bool:
        """Marca un préstamo como inactivo y lo quita de activos.

        Realiza una actualización en el historial (`active = False`) y elimina
        su `id` del archivo de préstamos activos.

        Retorna:
        - `True` si la operación se realizó.
        - `False` si el préstamo no estaba en activos.
        """
        index = self.__search_id_in_history_loans(id)
        if index == -1:
            print(f"Loan with id {id} not found for deletion.")
            return False
        self.__history_loans[index]["status"] = False
        self.__file_history_loans.write(self.__history_loans)
        self.__disable_loan(id)
        return True

    def __str__(self) -> str:
        """Representación legible del repositorio."""
        file_info = getattr(self.__file_history_loans, "path", getattr(self.__file_history_loans, "url", str(self.__file_history_loans)))
        return f"LoansRepository(file={file_info!r}, cached_loans={len(self.__history_loans)})"

    def __repr__(self) -> str:
        """Representación no ambigua para debugging."""
        return f"LoansRepository(file={self.__file_history_loans!r}, loans_count={len(self.__history_loans)})"
