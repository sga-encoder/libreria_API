"""Utilidad: gestión simple de archivos JSON y CSV.

Proporciona la clase FileManager para leer, escribir, anexar y eliminar
archivos JSON o CSV usando rutas manejadas por pathlib.Path.

Estrategia principal para append: leer con read(), combinar en memoria y
reescribir con write() (comportamiento sencillo y explícito).
"""
from enum import Enum
from pathlib import Path
import json
import csv

class FileType(Enum):
    """Tipos de archivo soportados por FileManager."""
    JSON = "json"
    CSV = "csv"
    
    
class FileManager:
    """Gestor de archivos JSON/CSV.

    Uso básico:
        fm = FileManager('data/books', FileType.JSON)
        fm.write({'a': 1})
        x = fm.read()
        fm.append({'b': 2})

    Atributos:
        __url: ruta al archivo (puede no incluir sufijo).
        __file_type: FileType indicando formato.
        __content: almacenamiento interno (no usado públicamente).

    Métodos principales:
        - read(): devuelve el contenido del archivo o None si no existe.
        - write(content): sobrescribe el archivo con 'content'.
        - append(content): lee, combina y reescribe (estrategia read+merge+write).
        - delete(): elimina el archivo.
    """
    __url: str
    __file_type: FileType
    __content: str | dict | list[dict]
    __csv_headers: list[str] | None
    
    def __init__(self, url: str, file_type: FileType, csv_headers: list[str] | None = None):
        """Inicializa FileManager con una ruta y tipo de archivo.

        Args:
            url: ruta al archivo (puede omitirse la extensión).
            file_type: miembro de FileType indicando formato (JSON o CSV).
            csv_headers: opcional; cuando `file_type` es `FileType.CSV`, una lista
                de nombres de cabecera que se escribirán en el CSV si el
                fichero no existe aún. Si se proporciona y el fichero ya
                existe, no se sobrescribe.

        Inicialmente la caché interna `__content` es None hasta la primera lectura
        o escritura. Si `csv_headers` se indica y el archivo CSV no existe,
        se crea con la línea de cabecera y la caché se inicializa como lista vacía.
        """
        self.__url = url
        self.__file_type = file_type
        self.__content = None
        # Guardar cabeceras opcionales para CSV
        self.__csv_headers = csv_headers

        # Si es CSV y se han provisto cabeceras, crear archivo con cabecera
        # si el fichero no existe aún.
        if self.__file_type == FileType.CSV and self.__csv_headers:
            p = Path(self.__get_path())
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                if not p.exists():
                    # Reusar la escritura CSV existente para crear la cabecera
                    self.__write_csv(p, list(self.__csv_headers))
            except Exception:
                # No detener la inicialización por errores en la creación de cabeceras;
                # la excepción se propagará en operaciones posteriores si es necesario.
                pass

    def __get_path(self) -> str:
        """Devuelve la Path resuelta para la URL configurada.

        Si la ruta no tiene sufijo, añade el sufijo correspondiente al tipo.
        """
        # Si el desarollador pasa una ruta que comienza por '/' o '\\' es probable
        # que pretendiera una ruta relativa dentro del proyecto (p. ej.
        # '/data/json/foo') en lugar de la raíz del disco en Windows
        # (C:\data\...). Para evitar intentos de escritura en ubicaciones
        # protegidas tratamos ese caso como relativo al root del proyecto.
        url_str = str(self.__url)
        if url_str.startswith('/') or url_str.startswith('\\'):
            # Proyecto raíz: subir dos niveles desde este fichero (app/utils)
            project_root = Path(__file__).resolve().parents[2]
            rel = url_str.lstrip('/\\')
            p = project_root / rel
        else:
            p = Path(self.__url)

        if not p.suffix:
            p = p.with_suffix('.' + self.__file_type.value)
        return p.resolve()
        
    def __read_json(self,file_path) -> str | dict | list[dict]:
        """Lee JSON desde `file_path`, actualiza la caché interna y devuelve el objeto Python.

        Comportamiento:
            - Carga el contenido con json.load y lo devuelve como dict o list.
            - Actualiza `self.__content` con el objeto Python leído (dict o list).
            - No realiza conversión adicional; las operaciones posteriores trabajan
              con objetos Python para facilitar append/merge.
        Args:
            file_path: pathlib.Path del fichero JSON.
        Returns:
            dict | list: representación Python del JSON leído.
        """
        with file_path.open('r', encoding='utf-8') as f:
                data = json.load(f)
                # actualizar caché interna
                self.__content = data
                return data
            
    def __read_csv(self,file_path) -> list[dict]:
        """Lee CSV desde `file_path`, actualiza la caché interna y devuelve una lista de filas.

        Comportamiento:
            - Usa csv.DictReader para devolver cada fila como dict.
            - Actualiza `self.__content` con la lista resultante.
        Args:
            file_path: pathlib.Path del fichero CSV.
        Returns:
            list[dict]: lista de filas, cada una como dict.
        """
        with file_path.open('r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                # actualizar caché interna
                self.__content = rows
                return rows
            
    def read(self) -> str | dict | list[dict]:
        """Lee y devuelve el contenido del archivo.

        Retorno:
            - Para JSON: dict o list según el contenido, o None si no existe pero
              `__content` contiene algo en memoria.
            - Para CSV: lista de dicts (cada fila como dict), o None si no existe
              y no hay caché en memoria.
        Notas:
            - Si el fichero no existe, se devuelve la caché interna (`__content`),
              de modo que es posible trabajar en memoria antes de la primera escritura.
        """
        file_path = Path(self.__get_path())
        # Si no existe el archivo, devolvemos la caché interna (puede ser None
        # si nunca se ha escrito nada). Esto permite usar FileManager en memoria
        # hasta que se escriba por primera vez.
        if not file_path.exists():
            return self.__content
        if self.__file_type == FileType.JSON:
            return self.__read_json(file_path)
        else:
            return self.__read_csv(file_path)
        
    def __write_json(self, file_path, content: dict | list[dict]) -> None:
        """Escribe `content` como JSON en `file_path` y actualiza la caché interna.

        A partir de la nueva política, siempre escribimos JSON como una lista
        de diccionarios. Reglas:
            - Si `content` es dict -> lo convertimos a [dict].
            - Si `content` es list -> validamos que cada elemento sea dict.
            - Si `content` no es dict ni list -> ValueError.
        Args:
            file_path: pathlib.Path del fichero destino.
            content: dict o list que será escrito como JSON.
        Raises:
            ValueError: si el contenido no puede representarse como lista de dicts.
        """
        new_content = None
        # Normalizar a lista de dicts
        if isinstance(content, dict):
            new_content = [content]
        elif isinstance(content, list):
            # validar elementos
            if not all(isinstance(item, dict) for item in content):
                raise ValueError("FileManager JSON write expects a dict or a list of dicts")
            new_content = content
        else:
            raise ValueError("FileManager JSON write expects a dict or a list of dicts")

        # Escribir el JSON (siempre una lista)
        with file_path.open('w', encoding='utf-8') as f:
            json.dump(new_content, f, ensure_ascii=False, indent=2)

        # actualizar caché interna con la lista escrita
        self.__content = new_content
        
    def __write_csv(self, file_path, content: list[dict]) -> None:
        """Escribe `content` como CSV en `file_path` y actualiza la caché interna.

        Acepta dos formatos para `content`:
            - `list[dict]`: escribe cabecera con las claves del primer dict y todas las filas.
            - `list[str]`: interpreta la lista como nombres de cabecera y escribe
              un fichero que solo contiene la línea de cabecera (sin filas de datos).

        Comportamiento:
            - Si `content` está vacío escribe un fichero vacío y guarda `[]` en la caché.
            - Si `content` es `list[str]` escribe solo la cabecera y deja la caché como `[]`.
            - Si `content` es `list[dict]` escribe cabecera + filas y guarda la lista en la caché.

        Args:
            file_path: pathlib.Path del fichero destino.
            content: lista de dicts (filas) o lista de strings (cabeceras).
        Raises:
            ValueError: si `content` no es una lista de dicts ni una lista de strings.
        """
        with file_path.open('w', newline='', encoding='utf-8') as f:
                # Caso: lista vacía -> fichero vacío
                if not content:
                    f.write('')
                    self.__content = []
                    return

                # Caso: lista de strings = cabeceras solamente
                if isinstance(content, list) and all(isinstance(h, str) for h in content):
                    writer = csv.writer(f)
                    writer.writerow(content)
                    # sin filas, caché vacía (lista de filas)
                    self.__content = []
                    return

                # Caso esperado: lista de dicts -> escribir con DictWriter
                if isinstance(content, list) and all(isinstance(row, dict) for row in content):
                    fieldnames = list(content[0].keys())
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(content)
                    # actualizar caché interna tras escribir
                    self.__content = content
                    return

                # Si llegamos aquí, el formato no es válido
                raise ValueError('CSV write expects a list of dicts (rows) or a list of header names (strings)')
    
    def write(self, content: dict | list[dict]) -> None:
        """Sobrescribe el archivo con 'content'.

        Comportamiento:
            - JSON: escribe el objeto pasado (dict o list) con indentación.
            - CSV: espera lista de dicts; crea cabecera con las claves de la primera fila.
        Args:
            content: dict (JSON) o list[dict] (JSON/CSV) a escribir.
        """
        p = Path(self.__get_path())

        # Intento seguro de crear los directorios padres con manejo de errores
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            print(f"FileManager: permiso denegado al crear directorio {p.parent}: {e}")
            raise
        except Exception as e:
            print(f"FileManager: error creando directorio {p.parent}: {e}")
            raise
        
        # Escribir el contenido según el tipo (se lanzarán excepciones si algo falla).
        try:
            if self.__file_type == FileType.JSON:
                self.__write_json(p, content)
            else:
                self.__write_csv(p, content)
        except Exception as e:
            # Mantener mensaje de error y volver a lanzar
            print(f"FileManager: error al escribir en {p}: {e}")
            raise
                
    def __apppend_json(self, existing: dict | list, content: dict | list[dict]) -> None:
        """Combina 'existing' y 'content' para JSON y reescribe con write().

        Modificado para garantizar que el fichero resultante sea siempre una
        lista de diccionarios. Reglas de normalización:
            - existing: None -> [], dict -> [dict], list -> list (siempre lista)
            - content: dict -> [dict], list -> list
            - si content no es dict ni list -> ValueError
        """
        # no logging: usamos prints para depuración

        # Normalizar existing a lista
        if existing is None:
            existing_list: list = []
        elif isinstance(existing, dict):
            existing_list = [existing]
        elif isinstance(existing, list):
            existing_list = existing
        else:
            # intentar preservar valor envolviéndolo en lista
            existing_list = [existing]

        # Normalizar content a lista
        if isinstance(content, dict):
            content_list = [content]
        elif isinstance(content, list):
            # validar elementos
            if not all(isinstance(item, dict) for item in content):
                raise ValueError('JSON append: content must be a dict or a list of dicts')
            content_list = content
        else:
            raise ValueError('JSON append: content must be a dict or a list of dicts')

        # Combinar listas (extend)
        new = existing_list + content_list

        # delegamos a write() que actualizará la caché interna (y validará el formato)
        self.write(new)
        
    def __append_csv(self, existing: list[dict] | None, content: dict | list[dict]) -> None:
        """Combina 'existing' y 'content' para CSV y reescribe con write().

        Reglas:
            - existing es lista de dicts o None.
            - content puede ser dict (una fila) o lista de dicts.
            - Se reconstruye la lista completa y se delega a write() para reescribir.
        """
        # Determinar tipo de content cuando es lista: lista de dicts (filas)
        # o lista de strings (cabeceras)
        def is_list_of_dicts(x):
            return isinstance(x, list) and all(isinstance(i, dict) for i in x)

        def is_list_of_str(x):
            return isinstance(x, list) and all(isinstance(i, str) for i in x)

        # Caso: no existe archivo previo
        if existing is None:
            if isinstance(content, dict):
                rows = [content]
            elif is_list_of_str(content):
                # content es solo cabeceras -> delegar a write para crear
                # archivo con cabecera y caché vacía
                self.write(content)
                return
            elif is_list_of_dicts(content):
                rows = content
            else:
                raise ValueError('CSV append expects a dict, a list of dicts, or a list of header strings')
        else:
            # existing ya es lista de filas (dict)
            rows = list(existing)
            if isinstance(content, dict):
                rows.append(content)
            elif is_list_of_dicts(content):
                rows.extend(content)
            elif is_list_of_str(content):
                # Si existing está vacío (lista vacía), permitir escribir solo cabecera
                if len(rows) == 0:
                    # delegar a write para crear cabecera
                    self.write(content)
                    return
                # No permitimos anexar una lista de cabeceras a un CSV ya existente con filas
                raise ValueError('CSV append: cannot append header list to existing CSV with rows')
            else:
                raise ValueError('CSV append expects a dict, a list of dicts, or a list of header strings')

        # reescribimos todo usando write (que espera lista). write()
        # actualizará la caché interna, por lo que no es necesario leer.
        self.write(rows)
    
    def append(self, content:  dict | list[dict]) -> None:
        """Aplica la estrategia read+merge+write para anexar datos.

        Llama a read(), combina en memoria según el tipo y llama a los
        helpers privados que finalmente usan write() para reescribir.
        """
        # Leemos el contenido actual; si el fichero no existe, read() devolverá
        # la caché interna (`__content`) — esto permite trabajar en memoria si
        # aún no se ha escrito nada.
        # Obtener la ruta utilizada y el contenido actual (sin prints de depuración).
        existing = self.read()

        if self.__file_type == FileType.JSON:
            self.__apppend_json(existing, content)
        else:
            self.__append_csv(existing, content)

        # Devolver la caché actualizada para mayor utilidad en pruebas/uso
        return self.__content
    
    def delete(self) -> None:
        """Elimina el archivo gestionado (silencioso si ya no existe)."""
        p = Path(self.__get_path())
        try:
            p.unlink(missing_ok=True)
        except TypeError:
            if p.exists():
                p.unlink()
        # limpiar la caché interna al eliminar el fichero
        self.__content = None
    
    def __str__(self):
        """Representación legible: ruta original."""
        return self.__url
    
    def __repr__(self):
        """Representación técnica con tipo de archivo."""
        return f"FileManager(url='{self.__url}', file_type='{self.__file_type.value}')"


