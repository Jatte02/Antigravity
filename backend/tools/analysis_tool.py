"""
Herramienta de análisis numéricos y cálculos sobre los datos de Mercado.
"""


import numpy as np
from langchain.tools import tool
from pydantic import BaseModel, Field


class CAGRInput(BaseModel):
    """Input para calcular la Tasa de Crecimiento Anual Compuesto (CAGR)."""

    start_value: float = Field(description="Valor inicial en el periodo histórico")
    end_value: float = Field(description="Valor final al término del periodo")
    years: float = Field(description="Años transcurridos entre inicio y fin.")


class CorrelationInput(BaseModel):
    """Correlación entre dos activos"""
    x_returns: list[float] = Field(description="Rendimientos diarios (en porcentaje) del ACTIVO X")
    y_returns: list[float] = Field(description="Rendimientos diarios (en porcentaje) del ACTIVO Y")


@tool("calcular_cagr", args_schema=CAGRInput)
def tool_calcular_cagr(start_value: float, end_value: float, years: float) -> str:
    """
    Calcula la Tasa de Crecimiento Anual Compuesta (CAGR) para evaluar rendimientos 
    de inversiones eliminando el efecto de fluctuaciones intermedias. 
    Ideal si conoces el precio del activo (o ganancias netas) en el año N y en el año N+5.
    """
    if years <= 0:
        return "El valor en 'años' debe ser mayor a 0."
    if start_value <= 0:
        return "El valor inicial debe ser superior a 0."

    cagr = (end_value / start_value) ** (1 / years) - 1
    return f"El CAGR compuesto para {years} años con estos valores es {cagr * 100:.2f}%"


@tool("calcular_correlacion", args_schema=CorrelationInput)
def tool_calcular_correlacion(x_returns: list[float], y_returns: list[float]) -> str:
    """
    Determina la correlación de Pearson r (-1 a +1) entre dos series de datos idénticas (por ejm dos 
    distintos retornos de precios diarios históricos para AAPL y MSFT).
    Al agente: provee un listado de puntos en orden idéntico para dos entidades y obtendrás 
    qué tan correlacionados están (comúnmente usado en finanzas como 'Pearsons correlation'). 
    """
    if len(x_returns) != len(y_returns):
        return "Las series para X e Y deben tener el mismo número de puntos."
    if len(x_returns) < 2:
         return "Se requiere mínimo de 2 puntos para un cálculo de correlación."

    correlacion = np.corrcoef(x_returns, y_returns)[0, 1]
    return f"Coeficiente de correlación de Pearson: {correlacion:.4f}"
