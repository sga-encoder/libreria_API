"""Repositorio de préstamos persistido en un archivo JSON.

Este módulo contiene la implementación de LoansRepository, una
implementación de RepositoriesInterface para objetos Loan. Usa FileManager
para lectura/escritura de datos en formato JSON y mantiene una caché
local de los registros leídos.
"""
from typing import Optional
from app.domain.models import Loan, Book, User
from .interface import RepositoriesInterface
from app.domain.structures import Queue
from app.domain.algorithms import linear_search
from app.utils import FileManager, FileType


class LoansRepository(RepositoriesInterface[Loan]):
    """Repositorio de Loan respaldado por un archivo JSON.

    Aporta operaciones CRUD básicas sobre préstamos: create, read, read_all,
    update y delete. Mantiene una caché interna (__loans) que se
    sincroniza con el archivo mediante FileManager.
    """
    __file: FileManager
    __loans: list[dict]

    def __init__(self, url: str) -> None:
        """Inicializa el repositorio.

        Args:
            url (str): Ruta o URL del archivo JSON donde se almacenan los préstamos.
        """
        self.__file = FileManager(url, FileType.JSON)
        self.__loans = self.__file.read()

    def __refresh_loans(self):
        """Recarga la caché interna desde el archivo.

        La caché se sobrescribe con el contenido actual del archivo para
        asegurar consistencia antes de operaciones de búsqueda o lectura.
        """
        self.__loans = self.__file.read()

    def __search_id(self, id: str) -> int:
        """Busca el índice de un préstamo por su ID.

        Args:
            id (str): ID del préstamo a buscar.

        Returns:
            int: Índice del préstamo en la lista de datos, o -1 si no se encuentra.
        """
        self.__refresh_loans()
        
        # Crear dummy para usar linear_search
        class LoanDummy:
            def __init__(self, loan_id):
                self._id = loan_id
            def get_id(self):
                return self._id
        
        dummy = LoanDummy(id)
        # Convertir diccionarios a objetos Loan temporalmente para la búsqueda
        loan_objects = [Loan.from_dict(loan_data) for loan_data in self.__loans]
        index = linear_search(
            loan_objects,
            key=lambda loan: loan.get_id(),
            item=dummy
        )
        return index

    def __search_loan(self, id: str) -> dict | int:
        """Obtiene el diccionario del préstamo correspondiente al ID dado.

        Args:
            id (str): ID del préstamo.

        Returns:
            dict | int: Diccionario con los datos del préstamo si se encuentra,
            o -1 si no existe.
        """
        index = self.__search_id(id)
        return self.__loans[index] if index != -1 else -1

    def create(self, json: dict) -> Loan:
        """Crea un nuevo Loan a partir de un dict y lo persiste.

        Args:
            json (dict): Datos del préstamo.

        Returns:
            Loan: Instancia creada.
        """
        instance = Loan.from_dict(json)
        self.__file.append(instance.to_dict())
        self.__refresh_loans()
        return instance

    def read(self, id: str) -> Loan | None:
        """Lee un préstamo por su ID.

        Args:
            id: ID del préstamo.

        Returns:
            Loan | None: Instancia Loan si se encuentra, None en caso contrario.
        """
        loan = self.__search_loan(id)
        if loan == -1:
            print(f"Loan with id {id} not found.")
            return None
        instance = Loan.from_dict(loan)
        return instance

    def read_all(self) -> list[Loan] | None:
        """Lee todos los préstamos y los devuelve en una lista.

        Returns:
            list[Loan] | None: Lista con todas las instancias Loan o None si la
            colección está vacía.
        """
        self.__refresh_loans()
        if not self.__loans:
            print("No loans found in the repository.")
            return None
        loans = []
        for data in self.__loans:
            loan = Loan.from_dict(data)
            loans.append(loan)
        return loans

    def update(self, id: str, json: dict) -> Loan | None:
        """Actualiza un préstamo existente con datos proporcionados.
        
        Args:
            id (str): ID del préstamo a actualizar.
            json (dict): Campos a actualizar.

        Returns:
            Loan | None: Instancia actualizada o None si no se encontró.
        """
        index = self.__search_id(id)
        if index == -1:
            print(f"Loan with id {id} not found for update.")
            return None
        instance = Loan.from_dict(self.__loans[index])
        instance.update_from_dict(json)
        self.__loans[index] = instance.to_dict()
        
        self.__file.write(self.__loans)
        return instance

    def delete(self, id: str) -> bool:
        """Elimina un préstamo por su ID y persiste el cambio en el archivo.

        Args:
            id (str): ID del préstamo a eliminar.

        Returns:
            bool: True si se eliminó con éxito, False si no se encontró.
        """
        index = self.__search_id(id)
        if index == -1:
            print(f"Loan with id {id} not found for deletion.")
            return False
        self.__loans.pop(index)
        self.__file.write(self.__loans)
        return True

    def __str__(self) -> str:
        """Representación legible del repositorio."""
        file_info = getattr(self.__file, "path", getattr(self.__file, "url", str(self.__file)))
        return f"LoansRepository(file={file_info!r}, cached_loans={len(self.__loans)})"

    def __repr__(self) -> str:
        """Representación no ambigua para debugging."""
        return f"LoansRepository(file={self.__file!r}, loans_count={len(self.__loans)})"
