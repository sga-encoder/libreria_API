import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.v1 import book_router, loan_router, user_router, auth_router, admin_router
from app.core.logging_config import setup_logging
from app.domain.exceptions import LibraryException

logger = setup_logging(log_level="DEBUG")  # ← Cambiar a "INFO" en producción

logger.info("=" * 80)
logger.info("INICIANDO APLICACIÓN - Library Management API")
logger.info("=" * 80)

app = FastAPI(   
    title="Library Management API",
    description="API para gestión de biblioteca con préstamos y reservas",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "bienvenido a la API de la biblioteca"}

app.include_router(user_router)
app.include_router(book_router)
app.include_router(loan_router)
app.include_router(auth_router)
app.include_router(admin_router)



@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de todas las peticiones HTTP."""
    start_time = time.time()
    
    # Log de entrada
    logger.info(f"→ {request.method} {request.url.path}")
    
    # Procesar request
    response = await call_next(request)
    
    # Log de salida con duración
    duration = time.time() - start_time
    logger.info(
        f"← {request.method} {request.url.path} "
        f"[{response.status_code}] ({duration:.3f}s)"
    )
    
    return response

@app.exception_handler(LibraryException)
async def library_exception_handler(request: Request, exc: LibraryException):
    """Maneja todas las excepciones personalizadas de la biblioteca."""
    logger.error(f"LibraryException: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=400,
        content={
            "message": str(exc),
            "type": exc.__class__.__name__
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones no capturadas."""
    logger.critical(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"message": "Error interno del servidor"}
    )

logger.info("Aplicación FastAPI configurada exitosamente")







