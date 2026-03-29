"""
Herramienta que permite buscar noticias financieras sobre una empresa.
"""


from langchain.tools import tool
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.conexion import SessionLocal
from backend.db.modelos import NoticiaSentimiento


class NewsSearchInput(BaseModel):
    """Input para consultar noticias por ticker symbol."""

    symbol: str


@tool("buscar_noticias", args_schema=NewsSearchInput)
def tool_buscar_noticias(symbol: str) -> list[dict[str, str | float]]:
    """
    Recupera las noticias históricas con puntaje de análisis de sentimiento (Loughran-McDonald) 
    disponibles en la base de datos de MarketSense para un símbolo financiero (ej: AAPL, TSLA).
    
    Es especialmente útil para entender el motivo detrás de un fuerte movimiento de precios o
    identificar si las notas recientes de prensa han sido predominantemente positivas o negativas.
    """
    db: Session = SessionLocal()
    try:
        # Últimas 15 noticias del símbolo específico, priorizando con sentimiento marcado si lo hay.
        noticias_query = (
            db.query(NoticiaSentimiento)
            .filter(NoticiaSentimiento.symbol == symbol.upper())
            .order_by(NoticiaSentimiento.pub_date.desc())
            .limit(15)
            .all()
        )

        resultados = []
        for n in noticias_query:
            resultados.append(
                {
                    "title": n.title,
                    "summary": n.summary,
                    "date": n.pub_date,
                    "sentiment": n.lm_sentiment or "neutral",
                    "score": n.lm_score1 or 0.0,
                    "provider": n.provider,
                }
            )

        if not resultados:
            return f"No se encontraron noticias para '{symbol}'."

        return resultados

    finally:
        db.close()
