from fastapi import FastAPI
from app.routers import book_router, loan_router, user_router, auth_router


app = FastAPI()

@app.get("/")
def root():
    return {"message": "bienvenido a la API de la biblioteca"}

app.include_router(user_router)
app.include_router(book_router)
app.include_router(loan_router)
app.include_router(auth_router)














