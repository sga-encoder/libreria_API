import os
from dotenv import load_dotenv

load_dotenv()

# Leer la clave de Google Books desde la variable de entorno
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

class Settings:
    APP_NAME = "LibraryAPI"
    DATA_PATH = "./data"
    DATA_PATH_INVENTARY = f"{DATA_PATH}/json/books.json"
    DATA_PATH_USERS = f"{DATA_PATH}/json/users.json"
    DATA_PATH_LOANS_RECORDS = f"{DATA_PATH}/json/loans_records.json"
    GOOGLE_BOOKS_API_KEY = GOOGLE_BOOKS_API_KEY
    TOKEN_ALGORITHM = "HS256"

settings = Settings()