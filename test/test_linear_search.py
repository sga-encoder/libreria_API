"""
Test para validar el comportamiento de linear_search con diferentes tipos de datos.
Cubre:
- Búsqueda en listas simples (números, strings)
- Búsqueda en listas de diccionarios
- Búsqueda en listas de objetos
- Casos edge: lista vacía, elemento no encontrado
"""
import pytest
from app.domain.algorithms import linear_search


class SimpleObject:
    """Objeto simple para pruebas."""
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
    
    def __repr__(self):
        return f"SimpleObject(id={self.id}, name={self.name})"


class TestLinearSearchWithSimpleLists:
    """Pruebas con listas simples de números y strings."""
    
    def test_search_in_number_list(self):
        """Buscar un número en una lista de números."""
        numbers = [10, 20, 30, 40, 50]
        index = linear_search(
            numbers,
            key=lambda x: x,
            item=30
        )
        assert index == 2
    
    def test_search_in_string_list(self):
        """Buscar un string en una lista de strings."""
        names = ["Ana", "Luis", "Carlos", "María"]
        index = linear_search(
            names,
            key=lambda x: x,
            item="Carlos"
        )
        assert index == 2
    
    def test_not_found_in_simple_list(self):
        """Elemento no encontrado debe retornar -1."""
        numbers = [1, 2, 3, 4, 5]
        index = linear_search(
            numbers,
            key=lambda x: x,
            item=99
        )
        assert index == -1


class TestLinearSearchWithDictionaries:
    """Pruebas con listas de diccionarios (como en loans_repository)."""
    
    def test_search_by_id_in_dict_list(self):
        """Buscar un diccionario por su clave 'id'."""
        loans = [
            {"id": "17681468977650001", "user": "user1", "book": "book1"},
            {"id": "17681488224680002", "user": "user2", "book": "book2"},
            {"id": "17681488224680003", "user": "user3", "book": "book3"}
        ]
        
        index = linear_search(
            loans,
            key=lambda loan: loan["id"],
            item="17681488224680002"
        )
        assert index == 1
        assert loans[index]["user"] == "user2"
    
    def test_search_by_ids_actives_loans_key(self):
        """Buscar usando la clave 'ids_actives_loans' (como en CSV)."""
        active_loans = [
            {"ids_actives_loans": "17681468977650001"},
            {"ids_actives_loans": "17681488224680002"},
            {"ids_actives_loans": "17681488224680003"}
        ]
        
        index = linear_search(
            active_loans,
            key=lambda loan: loan["ids_actives_loans"],
            item="17681488224680002"
        )
        assert index == 1
    
    def test_search_not_found_in_dict_list(self):
        """ID no encontrado en lista de diccionarios."""
        loans = [
            {"id": "001", "name": "Loan1"},
            {"id": "002", "name": "Loan2"}
        ]
        
        index = linear_search(
            loans,
            key=lambda loan: loan["id"],
            item="999"
        )
        assert index == -1
    
    def test_search_with_duplicate_values(self):
        """Cuando hay duplicados, retorna el primer índice."""
        loans = [
            {"id": "001", "status": "active"},
            {"id": "002", "status": "active"},
            {"id": "001", "status": "inactive"}  # Duplicado
        ]
        
        index = linear_search(
            loans,
            key=lambda loan: loan["id"],
            item="001"
        )
        assert index == 0  # Debe retornar el primero


class TestLinearSearchWithObjects:
    """Pruebas con listas de objetos."""
    
    def test_search_object_by_id(self):
        """Buscar un objeto por su atributo id."""
        objects = [
            SimpleObject("001", "Object1"),
            SimpleObject("002", "Object2"),
            SimpleObject("003", "Object3")
        ]
        
        index = linear_search(
            objects,
            key=lambda obj: obj.id,
            item=SimpleObject("002", "")  # Solo importa el id
        )
        assert index == 1
        assert objects[index].name == "Object2"
    
    def test_search_object_by_name(self):
        """Buscar un objeto por su atributo name."""
        objects = [
            SimpleObject("001", "Alpha"),
            SimpleObject("002", "Beta"),
            SimpleObject("003", "Gamma")
        ]
        
        index = linear_search(
            objects,
            key=lambda obj: obj.name,
            item=SimpleObject("", "Beta")
        )
        assert index == 1
    
    def test_search_object_not_found(self):
        """Objeto no encontrado."""
        objects = [
            SimpleObject("001", "Object1"),
            SimpleObject("002", "Object2")
        ]
        
        index = linear_search(
            objects,
            key=lambda obj: obj.id,
            item=SimpleObject("999", "NotFound")
        )
        assert index == -1


class TestLinearSearchEdgeCases:
    """Casos edge y excepciones."""
    
    def test_empty_list_raises_index_error(self):
        """Lista vacía debe lanzar IndexError."""
        with pytest.raises(IndexError, match="La lista proporcionada está vacía"):
            linear_search(
                [],
                key=lambda x: x,
                item=10
            )
    
    def test_none_list_raises_index_error(self):
        """Lista None debe lanzar IndexError."""
        with pytest.raises(IndexError, match="La lista proporcionada está vacía"):
            linear_search(
                None,
                key=lambda x: x,
                item=10
            )
    
    def test_single_element_found(self):
        """Lista de un solo elemento - encontrado."""
        index = linear_search(
            [42],
            key=lambda x: x,
            item=42
        )
        assert index == 0
    
    def test_single_element_not_found(self):
        """Lista de un solo elemento - no encontrado."""
        index = linear_search(
            [42],
            key=lambda x: x,
            item=99
        )
        assert index == -1


class TestLinearSearchRealWorldScenario:
    """Pruebas que simulan el caso real del loans_repository."""
    
    def test_search_in_history_loans_structure(self):
        """Simula búsqueda en __history_loans."""
        history_loans = [
            {
                "id": "17681468977650001",
                "id_user": "17653218466160001",
                "id_ISBN_book": "9780062316097",
                "loan_date": "2026-01-11T10:54:57.765744",
                "status": True
            },
            {
                "id": "17681488224680002",
                "id_user": "17653218466160001",
                "id_ISBN_book": "9780345539434",
                "loan_date": "2026-01-11T11:27:02.468352",
                "status": True
            }
        ]
        
        # Buscar el segundo préstamo
        index = linear_search(
            history_loans,
            key=lambda loan: loan["id"],
            item="17681488224680002"
        )
        
        assert index == 1
        assert history_loans[index]["id_ISBN_book"] == "9780345539434"
    
    def test_search_in_active_loans_structure(self):
        """Simula búsqueda en __active_loans (CSV format)."""
        active_loans = [
            {"ids_actives_loans": "17681468977650001"},
            {"ids_actives_loans": "17681488224680002"}
        ]
        
        # Buscar el segundo préstamo activo
        index = linear_search(
            active_loans,
            key=lambda loan: loan["ids_actives_loans"],
            item="17681488224680002"
        )
        
        assert index == 1
    
    def test_mismatch_key_returns_not_found(self):
        """
        Si usamos la clave incorrecta, no encontramos el elemento.
        Este era el bug original: buscar por 'id' en active_loans.
        """
        active_loans = [
            {"ids_actives_loans": "17681468977650001"},
            {"ids_actives_loans": "17681488224680002"}
        ]
        
        # Intentar buscar con la clave INCORRECTA 'id' (no existe)
        # Esto causaría KeyError en el lambda
        with pytest.raises(KeyError):
            linear_search(
                active_loans,
                key=lambda loan: loan["id"],  # ❌ Clave incorrecta
                item="17681488224680002"
            )
