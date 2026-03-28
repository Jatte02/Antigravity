"""
Módulo de conexión a la base de datos PostgreSQL (AWS RDS).

Expone:
  - engine:         motor SQLAlchemy (singleton)
  - SessionLocal:   fábrica de sesiones
  - get_db():       generador para inyección de dependencias (FastAPI)
"""

import os
import urllib.parse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── Cargar variables de entorno ───────────────────────────────────────────────
load_dotenv()

# ── Construir URL de conexión ─────────────────────────────────────────────────
# Se usa urllib.parse.quote_plus para escapar caracteres especiales en la
# contraseña (como $, @, #, etc.) que romperían el connection string.

_user = os.getenv("AWS_RDS_USER", "")
_password = urllib.parse.quote_plus(os.getenv("AWS_RDS_PASS", ""))
_host = os.getenv("AWS_RDS_HOST", "localhost")
_port = os.getenv("AWS_RDS_PORT", "5432")
_dbname = os.getenv("AWS_RDS_DBNAME", "postgres")

DATABASE_URL = f"postgresql://{_user}:{_password}@{_host}:{_port}/{_dbname}"

# ── Motor y Sesiones ─────────────────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    pool_size=5,              # Conexiones simultáneas en el pool
    max_overflow=10,          # Conexiones adicionales bajo carga
    pool_pre_ping=True,       # Verifica que la conexión siga viva antes de usarla
    connect_args={"connect_timeout": 10},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Generador de sesiones para FastAPI (Depends)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
