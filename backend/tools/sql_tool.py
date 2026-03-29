"""
Herramienta que permite al agente ejecutar consultas SQL (solo lectura)
contra la base de datos de MarketSense.
"""

from typing import Any

from langchain.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.db.conexion import SessionLocal
from backend.db.modelos import Base


class SQLInput(BaseModel):
    """Input para la herramienta de ejecución SQL."""

    query: str = Field(description="Consulta SQL a ejecutar en PostgreSQL")


def _obtener_esquema() -> str:
    """Genera la definición simplificada del esquema para el agente."""
    tablas = []

    # Extraemos nombres de tablas y columnas directamente desde SQLAlchemy Base
    for nombre_tabla, mapeador in Base.metadata.tables.items():
        columnas = [
            f"{col.name} ({col.type})"
            for col in mapeador.columns
        ]
        tablas.append(f"Tabla: {nombre_tabla}\nColumnas: {', '.join(columnas)}\n")

    return "\n".join(tablas)


@tool("ejecutar_sql", args_schema=SQLInput)
def tool_ejecutar_sql(query: str) -> str | list[dict[str, Any]]:
    """
    Ejecuta una consulta SQL SELECT en la base de datos de MarketSense y devuelve 
    los resultados en formato lista de diccionarios. 
    ¡IMPORTANTE!: 
    - Nunca usar DELETE, UPDATE o DROP.
    - Se debe usar PostgreSQL syntax.
    - Las tablas disponibles son: empresas, noticias_sentimiento, balance_general, 
      datos_financieros, presentaciones_sec, ejecutivos, precios_historicos.
    """
    keywords = ["delete", "update", "drop", "insert", "truncate"]
    if any(keyword in query.lower() for keyword in keywords):
        return "Error: Solo se permiten consultas SELECT (solo lectura)."

    db: Session = SessionLocal()
    try:
        resultado = db.execute(text(query))

        # En SQLAlchemy 2.0+ las consultas traen objetos o listas de tuplas
        # Mapeamos los resultados a nombres de las columnas reales.
        if resultado.returns_rows:
            columnas = resultado.keys()
            filas = resultado.fetchall()
            return [dict(zip(columnas, fila, strict=False)) for fila in filas]
        else:
            return "Comando ejecutado sin resultados de retorno."

    except Exception as e:
        return f"Error SQL: {str(e)}"

    finally:
        db.close()


@tool("ver_esquema_db")
def tool_ver_esquema_db() -> str:
    """
    Retorna el esquema completo de la base de datos de MarketSense. 
    Úsalo antes de escribir consultas SQL para saber qué tablas y columnas exactas existen.
    """
    return _obtener_esquema()

