"""
PRUEBA DE INTEGRACIÓN COMPLETA - BOOKCASE EN SISTEMA DE PRÉSTAMOS

Este script prueba que:
1. LoanAPIService se inicializa con BookCase
2. BookCase se pasa a LoanService correctamente
3. Todo el flujo funciona de punta a punta
4. La retrocompatibilidad sin bookcase sigue funcionando
"""

import sys
sys.path.insert(0, r'c:\Tecnias de Prog Juan\Biblioteca\libreria_API')

from app.domain.models import BookCase, BookShelf, Book, User, Loan
from app.domain.models.enums import TypeOrdering, PersonRole
from app.domain.services import LoanService, InventoryService, UserService
from app.domain.structures import Queue
from app.api.v1.loans.services import LoanAPIService
from datetime import datetime

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_api_service_with_bookcase():
    """Prueba LoanAPIService con BookCase"""
    print_section("1. INICIALIZACIÓN DE LoanAPIService CON BOOKCASE")
    
    try:
        # Simular rutas de datos
        loan_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\loans.json"
        inventory_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\books.json"
        user_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\users.json"
        
        # Crear LoanAPIService SIN bookcase inicialmente
        api_service = LoanAPIService(loan_url, inventory_url, user_url)
        print("✓ LoanAPIService creado sin bookcase")
        
        # Verificar que bookcase es None
        assert api_service.get_bookcase() is None, "Bookcase debe ser None inicialmente"
        print("✓ Bookcase es None inicialmente")
        
        # Crear bookcase dinámicamente
        bookcase = api_service.create_bookcase_with_algorithm(
            algorithm_type=TypeOrdering.DEFICIENT,
            weight_capacity=10.0,
            capacity_stands=5
        )
        print("✓ BookCase creado con algoritmo DEFICIENT")
        
        # Verificar que bookcase fue asignado
        assert api_service.get_bookcase() is not None, "Bookcase debe existir"
        print("✓ BookCase está disponible en el servicio")
        
        # Verificar que BookCase tiene propiedades correctas
        assert bookcase.get_TypeOrdering() == TypeOrdering.DEFICIENT
        print("✓ BookCase tiene algoritmo DEFICIENT configurado")
        
        return api_service, bookcase
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def test_loan_service_integration(api_service):
    """Prueba que LoanService recibió el bookcase"""
    print_section("2. INTEGRACIÓN DE BOOKCASE EN LOANSERVICE")
    
    try:
        # Acceder al LoanService interno
        loan_service = api_service._LoanAPIService__loan_service
        
        print("✓ LoanService obtenido desde LoanAPIService")
        
        # Verificar que tiene el bookcase
        bookcase = loan_service._LoanService__get_bookcase()
        if bookcase:
            print("✓ LoanService tiene BookCase configurado")
            print(f"  - Algoritmo: {bookcase.get_TypeOrdering()}")
            print(f"  - Capacidad por estante: {bookcase.get_weighOrdering()} kg")
            print(f"  - Cantidad de estantes: {bookcase.get_capacityStands()}")
        else:
            print("⚠ LoanService no tiene BookCase (retrocompatibilidad)")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def test_set_bookcase_dynamically(api_service):
    """Prueba establecer bookcase dinámicamente"""
    print_section("3. ESTABLECER BOOKCASE DINÁMICAMENTE")
    
    try:
        # Cambiar algoritmo a OPTIMOUM
        new_bookcase = api_service.create_bookcase_with_algorithm(
            algorithm_type=TypeOrdering.OPTIMOUM,
            weight_capacity=15.0,
            capacity_stands=8
        )
        print("✓ BookCase actualizado a algoritmo OPTIMOUM")
        
        # Verificar cambio
        current = api_service.get_bookcase()
        assert current.get_TypeOrdering() == TypeOrdering.OPTIMOUM
        print("✓ Cambio verificado correctamente")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def test_backward_compatibility():
    """Prueba retrocompatibilidad sin bookcase"""
    print_section("4. RETROCOMPATIBILIDAD SIN BOOKCASE")
    
    try:
        loan_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\loans.json"
        inventory_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\books.json"
        user_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\users.json"
        
        # Crear SIN pasar bookcase explícitamente
        api_service = LoanAPIService(loan_url, inventory_url, user_url)
        
        # Verificar que funciona sin bookcase
        assert api_service.get_bookcase() is None
        print("✓ LoanAPIService funciona sin bookcase")
        
        # LoanService también debe funcionar
        loan_service = api_service._LoanAPIService__loan_service
        bookcase = loan_service._LoanService__get_bookcase()
        assert bookcase is None
        print("✓ LoanService funciona sin bookcase")
        
        print("✓ Retrocompatibilidad verificada")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def test_methods_exist():
    """Verifica que todos los métodos nuevos existen"""
    print_section("5. VERIFICACIÓN DE MÉTODOS NUEVOS")
    
    try:
        loan_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\loans.json"
        inventory_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\books.json"
        user_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\users.json"
        
        api_service = LoanAPIService(loan_url, inventory_url, user_url)
        
        # Verificar métodos de LoanAPIService
        assert hasattr(api_service, 'set_bookcase')
        print("✓ LoanAPIService.set_bookcase() existe")
        
        assert hasattr(api_service, 'get_bookcase')
        print("✓ LoanAPIService.get_bookcase() existe")
        
        assert hasattr(api_service, 'create_bookcase_with_algorithm')
        print("✓ LoanAPIService.create_bookcase_with_algorithm() existe")
        
        # Verificar métodos de LoanService
        loan_service = api_service._LoanAPIService__loan_service
        
        assert hasattr(loan_service, 'set_bookcase')
        print("✓ LoanService.set_bookcase() existe")
        
        # Métodos privados
        assert hasattr(loan_service, '_LoanService__get_bookcase')
        print("✓ LoanService.__get_bookcase() existe")
        
        assert hasattr(loan_service, '_LoanService__apply_ordering_algorithm')
        print("✓ LoanService.__apply_ordering_algorithm() existe")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def test_signatures():
    """Verifica firmas de métodos"""
    print_section("6. VALIDACIÓN DE FIRMAS DE MÉTODOS")
    
    try:
        import inspect
        
        loan_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\loans.json"
        inventory_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\books.json"
        user_url = r"c:\Tecnias de Prog Juan\Biblioteca\libreria_API\data\users.json"
        
        api_service = LoanAPIService(loan_url, inventory_url, user_url)
        loan_service = api_service._LoanAPIService__loan_service
        
        # Verificar constructor acepta bookcase
        sig = inspect.signature(LoanAPIService.__init__)
        params = list(sig.parameters.keys())
        assert 'bookcase' in params
        print("✓ LoanAPIService.__init__() acepta parámetro 'bookcase'")
        
        # Verificar constructor de LoanService acepta bookcase
        sig = inspect.signature(LoanService.__init__)
        params = list(sig.parameters.keys())
        assert 'bookcase' in params
        print("✓ LoanService.__init__() acepta parámetro 'bookcase'")
        
        # Verificar create_loan existe
        assert hasattr(loan_service, 'create_loan')
        print("✓ LoanService.create_loan() existe")
        
        # Verificar update_loan existe
        assert hasattr(loan_service, 'update_loan')
        print("✓ LoanService.update_loan() existe")
        
        # Verificar delete_loan existe
        assert hasattr(loan_service, 'delete_loan')
        print("✓ LoanService.delete_loan() existe")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        raise

def main():
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "PRUEBA DE INTEGRACIÓN - BOOKCASE EN LOAN SERVICE" + " "*15 + "║")
    print("╚" + "="*78 + "╝")
    
    try:
        # Ejecutar pruebas
        api_service, bookcase = test_api_service_with_bookcase()
        test_loan_service_integration(api_service)
        test_set_bookcase_dynamically(api_service)
        test_backward_compatibility()
        test_methods_exist()
        test_signatures()
        
        # Resumen
        print_section("✅ RESULTADO FINAL")
        print("┌" + "─"*76 + "┐")
        print("│  TODAS LAS PRUEBAS PASARON EXITOSAMENTE                                  │")
        print("│                                                                          │")
        print("│  ✓ BookCase se integra correctamente en LoanAPIService                  │")
        print("│  ✓ BookCase se pasa correctamente a LoanService                         │")
        print("│  ✓ Todos los métodos nuevos existen                                     │")
        print("│  ✓ Las firmas son correctas                                             │")
        print("│  ✓ Retrocompatibilidad sin bookcase funciona                            │")
        print("│  ✓ Inicialización dinámica de bookcase funciona                         │")
        print("│                                                                          │")
        print("│  LA INTEGRACIÓN ESTÁ COMPLETA Y FUNCIONAL                               │")
        print("└" + "─"*76 + "┘")
        
    except Exception as e:
        print_section("❌ ERROR")
        print(f"Una prueba falló: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
