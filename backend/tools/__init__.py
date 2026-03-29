"""
Paquete backend.tools 

Contiene las funciones (tools) que puede invocar el Agente LangGraph.
"""

from backend.tools.analysis_tool import tool_calcular_cagr, tool_calcular_correlacion
from backend.tools.news_tool import tool_buscar_noticias
from backend.tools.sql_tool import tool_ejecutar_sql, tool_ver_esquema_db

__all__ = [
    "tool_ejecutar_sql",
    "tool_ver_esquema_db",
    "tool_buscar_noticias",
    "tool_calcular_cagr",
    "tool_calcular_correlacion",
]
