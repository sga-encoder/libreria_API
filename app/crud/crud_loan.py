from app.crud.interface import ICrud
from app.models import Loan
from app.services.library import Library
from app.models.user import User
from app.models.book import Book
from typing import Optional
from app.utils.queue import Queue
from app.utils import FileManager, FileType

class CRUDLoan(ICrud[Loan]):

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
        for loan in self.__loans:
            if loan.get_id() == id:
                return loan
    
    def read_all(self):
        """Leer todos los préstamos activos.

        Estrategia:
        - Intentar leer desde un JSON persistente usando FileManager en
          'data/loanRecords.json'. Si existe y contiene datos, devolver esa lista.
        - Si no existe fichero o está vacío, devolver la representación actual
          en memoria (`self.__loans`) transformada a dicts si es posible.
        """
        # Intentar leer desde el fichero JSON gestionado por FileManager
        try:
            fm = FileManager("data/loanRecords", FileType.JSON)
            stored = fm.read()
        except Exception:
            stored = None

        if stored:
            # Si FileManager devolvió datos (lista de dicts), devolverlos tal cual
            return stored

        # Fallback: construir lista desde la memoria (objetos Loan)
        result = []
        for loan in self.__loans:
            try:
                result.append(loan.to_dict())
            except Exception:
                # Si no es un objeto Loan serializable, intentar usarlo tal cual
                result.append(loan)
        return result
    
    def update(self, id: str, json: dict, new_book_id: Optional[str] = None) -> Loan:
        for loan in list(self.__loans):
            if loan.get_id() == id:
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
                            created = CRUDLoan.create(self, json, reserved_user, reserved_book)
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

                # Usar new_book_id si fue pasado; evitar input en tests
                if new_book_id is None:
                    try:
                        new_book_id = input("Enter id of the new book for the loan: ")
                    except Exception:
                        # No estamos en modo interactivo; devolver None
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
                else:
                    CRUDLoan.create(self, json, user, book_found)

                # Aceptar tanto dicts como modelos Pydantic (BookCreate)
                if hasattr(json, "model_dump"):
                    data = json.model_dump()
                elif hasattr(json, "dict"):
                    data = json.dict()
                else:
                    data = json
                data["id"] = id
                return Loan.from_dict(data)
        
        print("Loan not found")
    
    def delete(self, id: str) -> bool:
        # Buscar el loan en el registro global
        lr = Library.get_loanRecords()
        for loan in list(lr):
            if loan.get_id() == id:
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
                            created = CRUDLoan.create(self, {}, reserved_user, reserved_book)
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