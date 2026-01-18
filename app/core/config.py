import os
from dotenv import load_dotenv
# from datetime import timedelta

load_dotenv()

# Leer la clave de Google Books desde la variable de entorno
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

class Settings:
    APP_NAME = "LibraryAPI"
    DATA_PATH = "./data"
    DATA_PATH_INVENTARY = f"{DATA_PATH}/json/books.json"
    DATA_PATH_USERS = f"{DATA_PATH}/json/users.json"
    DATA_PATH_ADMINS = f"{DATA_PATH}/json/admins.json"
    DATA_PATH_LOANS_RECORDS = f"{DATA_PATH}/json/loans.json"
    DATA_PATH_CURRENT_LOANS = f"{DATA_PATH}/csv/active_loans.csv"
    GOOGLE_BOOKS_API_KEY = GOOGLE_BOOKS_API_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 100000000
    SECRET_KEY = SECRET_KEY

settings = Settings()