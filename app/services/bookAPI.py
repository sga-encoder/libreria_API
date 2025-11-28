import os
import requests
import random
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo `.env` (si existe)
load_dotenv()

# Leer la clave de Google Books desde la variable de entorno
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

def search_book_by_BookAPI(query):
    if not GOOGLE_BOOKS_API_KEY:
        raise RuntimeError(
            "La variable de entorno `GOOGLE_BOOKS_API_KEY` no está configurada. "
            "Copia `.env.example` a `.env` y establece la clave."
        )
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={GOOGLE_BOOKS_API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    data_resp = resp.json().get("items", [])
    data = []
    for book in data_resp:
        ids = book.get("volumeInfo", {}).get("industryIdentifiers", [{}])
        id = ""
        for i in ids:
            if i.get("type") == "ISBN_13":
                id = i.get("identifier")
                break
            
        data.append({
            "id_IBSN": id,
            "title": book.get("volumeInfo", {}).get("title"),
            "author": book.get("volumeInfo", {}).get("authors", [])[0],
            "gender": book.get("volumeInfo", {}).get("categories", [])[0],
            "weight": round(random.uniform(0.4, 1.3), 2) ,  # promedio de peso en kg de un libro tapa dura
            "price":  int(id[-2:] + "000") if id and id[-2:].isdigit() else round(random.uniform(5.0, 100.0), 2),  # Precio simulado
            "description": book.get("volumeInfo", {}).get("description", ""),
            "frond_page_url": book.get("volumeInfo", {}).get("imageLinks", {}).get("thumbnail", ""),
            "is_borrowed": False  # Default value
        })
    return data
