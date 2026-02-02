import os
from dotenv import load_dotenv
# from datetime import timedelta

load_dotenv()

# Leer la clave de Google Books desde la variable de entorno
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")


class Settings:
    APP_NAME = "LibraryAPI"
    GOOGLE_BOOKS_API_KEY = GOOGLE_BOOKS_API_KEY
    SECRET_KEY = SECRET_KEY
    ALGORITHM = ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    DATABASE_URL = DATABASE_URL

settings = Settings()