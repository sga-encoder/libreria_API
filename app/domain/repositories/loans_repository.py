from typing import Optional
from app.domain.models import Loan, Book, User
from .interface import RepositoriesInterface
from app.domain.structures import Queue
from app.domain.algorithms import linear_search
from .library import Library
from app.utils import FileManager, FileType

class LoansRepository(RepositoriesInterface[Loan]):

    def __init__(self, loansRecords: list[Loan], resevacionQueue, users) -> None:
        self.__loans = loansRecords
        self.__resevacionQueue = resevacionQueue
        
    def create(self, json: dict, user: User = None, book: Book = None) -> Loan:
        # Permitir llamarse con un único argumento (pydantic LoanCreate)
        # o con los parámetros (json, user, book).
        if user is None and book is None:
            # Extraer datos del objeto json/model
            if hasattr(json, "model_dump"):
                data = json.model_dump()
            elif hasattr(json, "dict"):
                data = json.dict()
            else:
                data = json
            # Buscar usuario por email y libro por id_IBSN en Library
            user_email = data.get("user")
            book_id = data.get("book")
            # localizar usuario
            user = None
            for u in Library.get_user():
                try:
                    if u.get_email() == user_email:
                        user = u
                        break
                except Exception:
                    # fallback: user may be dict
                    try:
                        if u.get("email") == user_email:
                            user = u
                            break
                    except Exception:
                        pass
            # localizar libro en inventario
            book = None
            for b in Library.get_inventary():
                try:
                    if b.get_id_IBSN() == book_id:
                        book = b
                        break
                except Exception:
                    try:
                        if b.get("id_IBSN") == book_id:
                            book = b
                            break
                    except Exception:
                        pass
                    
        if user is None or book is None:
            print("Error: user or book not found in Library.")
            return None
        

        # Si el libro ya está prestado, encolar al usuario en la cola de reservas
        if book.get_is_borrowed():
            print("Loan has been attempted for a borrowed book. Adding user to reservation queue.")
            reservationQueue = Library.get_reservationsQueue()
            # Queue en utils expone `push` / `pop`; usar push para encolar
            try:
                reservationQueue.push((user, book))
            except Exception:
                # Fallback a método genérico si existiera
                try:
                    reservationQueue.append((user, book))
                except Exception:
                    pass
            Library.set_reservationsQueue(reservationQueue)
            # No se crea préstamo ahora: devolvemos None para indicar reserva
            return None

        # Si no está prestado: crear préstamo y actualizar estados/colecciones
        loan = Loan(user, book)

        # Añadir el préstamo a la lista de loans del usuario (usar API pública)
        try:
            user.add_loan(loan)
        except Exception:
            # Fallback: manipular directamente la lista de loans si es necesario
            try:
                user_loans = user.get_loans()
                user_loans.append(loan)
                try:
                    # intentar actualizar con el setter privado si existe
                    user.__set_loans(user_loans)
                except Exception:
                    pass
            except Exception:
                pass

        # Añadir a la lista de préstamos activos de esta instancia si existe
        try:
            self.__loans.append(loan)
        except Exception:
            pass

        # Marcar el libro correspondiente dentro del inventario de la Library
        for inv_book in Library.get_inventary():
            if inv_book.get_id_IBSN() == book.get_id_IBSN():
                inv_book.set_is_borrowed(True)
                break

        # También marcar la instancia `book` pasada (por si es otra referencia)
        try:
            book.set_is_borrowed(True)
        except Exception:
            pass

        # Añadir al registro global de préstamos
        loanRecord = Library.get_loanRecords()
        loanRecord.append(loan)
        Library.set_loanRecords(loanRecord)

        return loan
    
    def read(self, id: str):
        if not self.__loans:
            return None
        
        # Crear un objeto dummy con el id buscado para usar con linear_search
        class LoanDummy:
            def __init__(self, id):
                self._id = id
            def get_id(self):
                return self._id
        
        dummy = LoanDummy(id)
        index = linear_search(self.__loans, lambda loan: loan.get_id(), dummy)
        
        if index != -1:
            return self.__loans[index]
        return None
    
    def read_all(self):
        """Leer todos los préstamos activos desde persistencia.

        Estrategia:
        1. Intentar leer desde FileManager('data/loanRecords.json').
        2. Si existe y contiene datos, parsear cada dict como Loan usando Loan.from_dict.
        3. Sincronizar Library.loanRecords con los Loan parseados.
        4. Devolver la lista de objetos Loan.
        5. Si no hay archivo o está vacío, devolver self.__loans.
        """
        # Intentar leer desde el fichero JSON gestionado por FileManager
        try:
            fm = FileManager("data/loanRecords", FileType.JSON)
            stored = fm.read()
        except Exception:
            stored = None

        # Si obtuvimos datos del archivo, parsearlos como objetos Loan
        if stored and isinstance(stored, list) and len(stored) > 0:
            loans_list = []
            for item in stored:
                try:
                    # Cada item debería ser un dict con estructura de Loan.to_dict()
                    loan = Loan.from_dict(item)
                    loans_list.append(loan)
                except Exception as e:
                    # Si un item falla al parsear, loguear pero continuar
                    print(f"Warning: failed to parse loan from dict: {e}")
                    continue
            
            # Sincronizar Library con los loans leídos
            if loans_list:
                Library.set_loanRecords(loans_list)
                self.__loans = loans_list
            return loans_list

        # Fallback: si no hay archivo o está vacío, devolver objetos Loan en memoria
        return self.__loans
    
    def update(self, id: str, json: dict, new_book_id: Optional[str] = None) -> Loan:
        # Buscar el préstamo usando linear_search
        class LoanDummy:
            def __init__(self, id):
                self._id = id
            def get_id(self):
                return self._id
        
        dummy = LoanDummy(id)
        index = linear_search(self.__loans, lambda loan: loan.get_id(), dummy)
        
        if index != -1:
            loan = self.__loans[index]
            user = loan.get_user()
            book = loan.get_book()

            # Liberar el libro en inventario e instancia
            try:
                # marcar en inventario
                for inv_book in Library.get_inventary():
                    if inv_book.get_id_IBSN() == book.get_id_IBSN():
                        inv_book.set_is_borrowed(False)
                        break
            except Exception:
                pass
            try:
                book.set_is_borrowed(False)
            except Exception:
                pass

            # Buscar si hay reservas para este ISBN y asignar al siguiente usuario
            try:
                rq = Library.get_reservationsQueue().to_list()
                for idx, reservation in enumerate(rq):
                    reserved_user, reserved_book = reservation
                    if reserved_book.get_id_IBSN() == book.get_id_IBSN():
                        print("There is a reservation for this book. Assigning to the next user in the queue.")
                        created = LoansRepository.create(self, json, reserved_user, reserved_book)
                        if created is not None:
                            # eliminar la reserva encontrada
                            rq.pop(idx)
                        break
                # reconstruir la cola sin la reserva consumida
                new_q = Queue()
                for item in rq:
                    new_q.push(item)
                Library.set_reservationsQueue(new_q)
            except Exception:
                pass

            # Eliminar el loan antiguo de las listas (global y local)
            try:
                lr = Library.get_loanRecords()
                if loan in lr:
                    lr.remove(loan)
                    Library.set_loanRecords(lr)
            except Exception:
                pass
            try:
                if loan in self.__loans:
                    self.__loans.remove(loan)
            except Exception:
                pass

            # Usar new_book_id si fue pasado
            if new_book_id is None:
                print("No new_book_id provided for update; aborting.")
                return None

            book_found = None
            for book1 in Library.get_inventary():
                if book1.get_id_IBSN() == new_book_id:
                    book_found = book1
                    break

            if book_found is None:
                print("Book not found")
                return None

            if book_found.get_is_borrowed():
                print("Loan has been attempted for a borrowed book. Adding user to reservation queue.")
                reservationQueue = Library.get_reservationsQueue()
                try:
                    reservationQueue.push((user, book_found))
                except Exception:
                    try:
                        reservationQueue.append((user, book_found))
                    except Exception:
                        pass
                Library.set_reservationsQueue(reservationQueue)
                return None

            # Crear el nuevo préstamo y devolverlo (create ya sincroniza Library y self.__loans)
            created = LoansRepository.create(self, json, user, book_found)
            if created is not None:
                return created
            return None
        
        print("Loan not found")
    
    def delete(self, id: str) -> bool:
        # Buscar el loan en el registro global usando linear_search
        lr = Library.get_loanRecords()
        
        class LoanDummy:
            def __init__(self, id):
                self._id = id
            def get_id(self):
                return self._id
        
        dummy = LoanDummy(id)
        index = linear_search(lr, lambda loan: loan.get_id(), dummy)
        
        if index != -1:
            loan = lr[index]
            book = loan.get_book()
            # Liberar libro en inventario e instancia
            try:
                for inv_book in Library.get_inventary():
                    if inv_book.get_id_IBSN() == book.get_id_IBSN():
                        inv_book.set_is_borrowed(False)
                        break
            except Exception:
                pass
            try:
                book.set_is_borrowed(False)
            except Exception:
                pass

            # Asignar a la siguiente reserva si existe
            try:
                rq = Library.get_reservationsQueue().to_list()
                for idx, reservation in enumerate(rq):
                    reserved_user, reserved_book = reservation
                    if reserved_book.get_id_IBSN() == book.get_id_IBSN():
                        print("There is a reservation for this book. Assigning to the next user in the queue.")
                        created = LoansRepository.create(self, {}, reserved_user, reserved_book)
                        if created is not None:
                            rq.pop(idx)
                        break
                new_q = Queue()
                for item in rq:
                    new_q.push(item)
                Library.set_reservationsQueue(new_q)
            except Exception:
                pass

            # Eliminar loan de registros global y lista local
            try:
                if loan in lr:
                    lr.remove(loan)
                    Library.set_loanRecords(lr)
            except Exception:
                pass
            try:
                if loan in self.__loans:
                    self.__loans.remove(loan)
            except Exception:
                pass
            return True
        return False