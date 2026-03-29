"""
Orquestador LangGraph que integra LLM AWS Bedrock (Claude 3.5 Sonnet) 
con herramientas de bases de datos, noticias y análisis financiero.
"""

import os
from datetime import datetime
from typing import Annotated, Sequence, TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Herramientas armadas en fases previas
from backend.tools import (
    tool_buscar_noticias,
    tool_calcular_cagr,
    tool_calcular_correlacion,
    tool_ejecutar_sql,
    tool_ver_esquema_db,
)


class AgentState(TypedDict):
    """Estado compartido a través de las iteraciones del LLM en LangGraph."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


def _crear_mensajes_sistema() -> SystemMessage:
    fecha = datetime.today().strftime('%Y-%m-%d')
    return SystemMessage(
        content=(
            "Eres un experto Analista Financiero de Wall Street con acceso total a MarketSense. "
            "Tienes a tu disposición información histórica de más de 500 empresas del S&P 500. "
            f"La fecha de hoy es {fecha}. "
            "Usa tus herramientas para satisfacer los requerimientos del usuario. "
            "1. Si necesitas datos numéricos exactos de precios asocia PostgreSQL usando SQL. "
            "2. Usa ver_esquema_db primero para conocer las tablas. "
            "3. Oculta todo tu proceso matemático o rastro lógico (raciocinio). "
            "4. En tus entregas al usuario limítate ÚNICAMENTE a darle la respuesta final de forma directa y conversacional breve."
        )
    )


class FinancialAnalystAgent:
    """Clase del Agente ReAct construida sobre LangGraph."""

    def __init__(self):
        # Para que el backend no colapse si la variable está vacía en .env
        api_key = os.getenv("GEMINI_API_KEY") or "mock_key_solo_para_arrancar"
        
        # 1. Escogemos el modelo Gemini 2.5 Flash
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=api_key,
            temperature=0,
            max_retries=2,
        )
        
        # 2. Asignamos las herramientas
        self.tools = [
            tool_ver_esquema_db,
            tool_ejecutar_sql,
            tool_buscar_noticias,
            tool_calcular_cagr,
            tool_calcular_correlacion,
        ]
        
        # El LLM "sabe" usar estas herramientas
        self.llm_with_tools = llm.bind_tools(self.tools)
        
        # 3. Ensamblamos el Grafo
        self.graph = self._build_graph()

    def _call_model(self, state: AgentState):
        """Nodo principal: El LLM evalúa qué hacer dados los mensajes."""
        mensajes = state["messages"]
        system_msg = _crear_mensajes_sistema()
        respuesta = self.llm_with_tools.invoke([system_msg] + list(mensajes))
        return {"messages": [respuesta]}

    def _should_continue(self, state: AgentState) -> str:
        """Nodo condicional: Si el LLM requiere usar una herramienta, continua al ToolNode."""
        last_message = state["messages"][-1]
        # Si el modelo decidió llamar a alguna herramienta, irá temporalmente allí
        if last_message.tool_calls:
            return "tools"
        # Si no, ha resuelto el problema y termina su turno
        return END

    def _build_graph(self):
        """Compila los diferentes nodos en un sistema iterativo."""
        workflow = StateGraph(AgentState)
        
        # Nodo de razonamiento LLM
        workflow.add_node("agent", self._call_model)
        
        # Nodo de ejecución de Herramientas
        tool_node = ToolNode(self.tools)
        workflow.add_node("tools", tool_node)

        # Configurar los lazos (Edges)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                END: END,
            },
        )
        # Después de usar herramientas, el agente recibe el feedback para seguir analizando
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def agendar_consulta(self, mensaje_usuario: str) -> list[BaseMessage]:
        """Interfaz principal: Recibe la inquietud y activa la cadena de pensamiento."""
        estado_inicial = {"messages": [HumanMessage(content=mensaje_usuario)]}
        resultados = self.graph.invoke(estado_inicial)
        return resultados["messages"]

# Singleton opcional
analyst_agent = FinancialAnalystAgent()
