"""
MarketSense — API REST principal.

Servidor de desarrollo:
    uvicorn backend.api.main:app --reload --port 8000

Documentación automática:
    http://localhost:8000/docs   (Swagger UI)
    http://localhost:8000/redoc  (ReDoc)
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes_empresas import router as empresas_router
from backend.api.routes_mercado import router as mercado_router
from backend.api.routes_chat import router as chat_router
from backend.db.conexion import engine
from backend.db.modelos import Base

load_dotenv()


# ── Lifespan: crear tablas al iniciar ────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Evento de inicio/cierre de la aplicación."""
    # Startup: asegurar que las tablas existan
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: limpiar recursos
    engine.dispose()


# ── Crear aplicación ─────────────────────────────────────────────────────────

app = FastAPI(
    title="MarketSense API",
    description=(
        "API de análisis financiero del S&P 500. "
        "Consulta empresas, precios históricos, noticias con sentimiento, "
        "datos financieros, y más."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS (permitir frontend Next.js) ─────────────────────────────────────────

frontend_url = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registrar routers ────────────────────────────────────────────────────────

app.include_router(empresas_router, prefix="/api")
app.include_router(mercado_router, prefix="/api")
app.include_router(chat_router, prefix="/api")


# ── Health check ─────────────────────────────────────────────────────────────


@app.get("/", tags=["Health"])
def health_check():
    """Endpoint de salud — confirma que la API está online."""
    return {
        "status": "healthy",
        "service": "MarketSense API",
        "version": "0.1.0",
    }


@app.get("/api/health", tags=["Health"])
def api_health():
    """Health check con verificación de conexión a DB."""
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "healthy",
        "database": db_status,
    }
