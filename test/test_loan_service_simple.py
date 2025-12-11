"""
Tests simples para verificar el funcionamiento de LoanService con BookShelf.
Evita complejidades de mocks y se enfoca en la lógica principal.
"""

import pytest
import sys
from io import StringIO


def test_loan_service_imports():
    """Verifica que los imports necesarios funcionan."""
    try:
        from app.domain.services.loan_service import LoanService
        from app.domain.models import BookCase
        from app.domain.models.enums import TypeOrdering
        from app.domain.algorithms.defientOrganicer import DeficientOrganizer
        from app.domain.algorithms.organizer_optimum import estanteria_optima
        print("[PASS] Todos los imports funcionan correctamente")
        return True
    except ImportError as e:
        print(f"[FAIL] Error en imports: {e}")
        return False


def test_bookcase_creation():
    """Verifica que se puede crear un BookCase."""
    try:
        from app.domain.models import BookCase, BookShelf
        from app.domain.models.enums import TypeOrdering
        
        # BookCase con DEFICIENT
        bc1 = BookCase(
            stands=BookShelf(books=[]),
            TypeOrdering=TypeOrdering.DEFICIENT,
            weighCapacity=10.0,
            capacityStands=5,
            store=[]
        )
        assert bc1.get_TypeOrdering() == TypeOrdering.DEFICIENT
        assert bc1.get_weighOrdering() == 10.0
        print("[PASS] BookCase DEFICIENT se crea correctamente")
        
        # BookCase con OPTIMOUM
        bc2 = BookCase(
            stands=BookShelf(books=[]),
            TypeOrdering=TypeOrdering.OPTIMOUM,
            weighCapacity=10.0,
            capacityStands=5,
            store=[]
        )
        assert bc2.get_TypeOrdering() == TypeOrdering.OPTIMOUM
        print("[PASS] BookCase OPTIMOUM se crea correctamente")
        return True
    except Exception as e:
        print(f"[FAIL] Error creando BookCase: {e}")
        return False


def test_loan_service_initialization_without_bookcase():
    """Verifica que LoanService se inicializa sin bookcase."""
    try:
        from app.domain.services.loan_service import LoanService
        from app.domain.services.inventory_service import InventoryService
        from app.domain.structures import Queue
        
        # Los parámetros serán mocks simples para no dependencias del repositorio
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=[],
            inventory_service=None,  # Simplemente None para esta prueba
            bookcase=None
        )
        
        # Verificar que se creó
        assert service is not None
        print("[PASS] LoanService se inicializa correctamente sin bookcase")
        return True
    except Exception as e:
        print(f"[FAIL] Error inicializando LoanService: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_loan_service_initialization_with_bookcase():
    """Verifica que LoanService se inicializa con bookcase."""
    try:
        from app.domain.services.loan_service import LoanService
        from app.domain.models import BookCase, BookShelf
        from app.domain.models.enums import TypeOrdering
        from app.domain.structures import Queue
        
        # Crear un bookcase
        bookcase = BookCase(
            stands=BookShelf(books=[]),
            TypeOrdering=TypeOrdering.DEFICIENT,
            weighCapacity=10.0,
            capacityStands=5,
            store=[]
        )
        
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=[],
            inventory_service=None,
            bookcase=bookcase
        )
        
        # Verificar que se creó con bookcase
        assert service is not None
        print("[PASS] LoanService se inicializa correctamente con bookcase")
        return True
    except Exception as e:
        print(f"[FAIL] Error inicializando LoanService con bookcase: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_set_bookcase():
    """Verifica que se puede establecer bookcase después de inicializar."""
    try:
        from app.domain.services.loan_service import LoanService
        from app.domain.models import BookCase, BookShelf
        from app.domain.models.enums import TypeOrdering
        from app.domain.structures import Queue
        
        # Inicializar sin bookcase
        service = LoanService(
            url="test",
            reservations_queue=Queue(),
            users=[],
            inventory_service=None,
            bookcase=None
        )
        
        # Crear bookcase
        bookcase = BookCase(
            stands=BookShelf(books=[]),
            TypeOrdering=TypeOrdering.DEFICIENT,
            weighCapacity=10.0,
            capacityStands=5,
            store=[]
        )
        
        # Establecer bookcase
        service.set_bookcase(bookcase)
        
        print("[PASS] set_bookcase funciona correctamente")
        return True
    except Exception as e:
        print(f"[FAIL] Error en set_bookcase: {e}")
        return False


def test_deficient_organizer():
    """Verifica que DeficientOrganizer funciona."""
    try:
        from app.domain.algorithms.defientOrganicer import DeficientOrganizer
        from app.domain.models import Book
        
        organizer = DeficientOrganizer(weight_capacity=5.0)
        
        # Crear libros de prueba
        books = []
        for i in range(3):
            book = Book(
                id_IBSN=f"ISBN-{i}",
                title=f"Libro {i}",
                author=f"Autor {i}",
                gender=1,
                weight=0.5 + i * 0.1,
                price=10.0,
                is_borrowed=False
            )
            books.append(book)
        
        # Organizar
        bookcase, dangerous = organizer.organize(books)
        
        assert bookcase is not None
        print(f"[PASS] DeficientOrganizer funciona correctamente (generó {bookcase.get_capacityStands()} estantes)")
        return True
    except Exception as e:
        print(f"[FAIL] Error en DeficientOrganizer: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_organizer_optimum():
    """Verifica que estanteria_optima funciona."""
    try:
        from app.domain.algorithms.organizer_optimum import estanteria_optima
        
        # Preparar datos
        libros = [
            {"peso": 0.5, "valor": 1},
            {"peso": 0.6, "valor": 1},
            {"peso": 0.7, "valor": 1},
        ]
        
        # Ejecutar algoritmo
        mejor_valor, mejor_solucion = estanteria_optima(libros, 2.0)
        
        assert mejor_valor is not None
        print(f"[PASS] estanteria_optima funciona correctamente (valor óptimo: {mejor_valor})")
        return True
    except Exception as e:
        print(f"[FAIL] Error en estanteria_optima: {e}")
        return False


def test_queue_functionality():
    """Verifica que la cola de reservas funciona."""
    try:
        from app.domain.structures import Queue
        
        queue = Queue()
        
        # Agregar items
        queue.push(("usuario1", "libro1"))
        queue.push(("usuario2", "libro2"))
        
        # Verificar contenido
        items = queue.to_list()
        assert len(items) == 2
        assert items[0] == ("usuario1", "libro1")
        
        print("[PASS] Queue funciona correctamente")
        return True
    except Exception as e:
        print(f"[FAIL] Error en Queue: {e}")
        return False


def test_loan_methods_exist():
    """Verifica que LoanService tiene todos los métodos requeridos."""
    try:
        from app.domain.services.loan_service import LoanService
        import inspect
        
        # Obtener métodos
        methods = inspect.getmembers(LoanService, predicate=inspect.isfunction)
        method_names = [m[0] for m in methods]
        
        # Verificar métodos públicos
        required_public = ['create_loan', 'update_loan', 'delete_loan', 'set_bookcase', 
                          'get_loans_records', 'get_reservations_queue']
        
        for method in required_public:
            assert method in method_names, f"Método {method} no existe"
        
        print(f"[PASS] LoanService tiene todos los métodos requeridos")
        return True
    except Exception as e:
        print(f"[FAIL] Error verificando métodos: {e}")
        return False


def test_loan_methods_have_correct_signatures():
    """Verifica que los métodos tengan las firmas correctas."""
    try:
        from app.domain.services.loan_service import LoanService
        import inspect
        
        # Verificar create_loan
        sig = inspect.signature(LoanService.create_loan)
        params = list(sig.parameters.keys())
        assert 'user' in params and 'book' in params, "create_loan debe tener user y book"
        
        # Verificar update_loan
        sig = inspect.signature(LoanService.update_loan)
        params = list(sig.parameters.keys())
        assert 'id' in params and 'new_book' in params, "update_loan debe tener id y new_book"
        
        # Verificar delete_loan
        sig = inspect.signature(LoanService.delete_loan)
        params = list(sig.parameters.keys())
        assert 'id' in params, "delete_loan debe tener id"
        
        # Verificar set_bookcase
        sig = inspect.signature(LoanService.set_bookcase)
        params = list(sig.parameters.keys())
        assert 'bookcase' in params, "set_bookcase debe tener bookcase"
        
        print("[PASS] Todos los métodos tienen firmas correctas")
        return True
    except Exception as e:
        print(f"[FAIL] Error verificando firmas: {e}")
        return False


def main():
    """Ejecuta todos los tests."""
    print("\n" + "="*70)
    print("TESTS DE LOAN SERVICE CON BOOKSHELF")
    print("="*70 + "\n")
    
    tests = [
        test_loan_service_imports,
        test_bookcase_creation,
        test_loan_service_initialization_without_bookcase,
        test_loan_service_initialization_with_bookcase,
        test_set_bookcase,
        test_deficient_organizer,
        test_organizer_optimum,
        test_queue_functionality,
        test_loan_methods_exist,
        test_loan_methods_have_correct_signatures,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Excepción no manejada en {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
        print()
    
    # Resumen
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"RESUMEN: {passed}/{total} tests pasaron")
    print("="*70 + "\n")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
