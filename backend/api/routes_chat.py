"""
Rutas de la API para el Chat Inteligente con el Agente LangGraph. 
"""

import uuid

from fastapi import APIRouter, HTTPException
from typing import Optional

from backend.api.schemas import ChatRequest, ChatResponse
from backend.agents.financial_analyst import analyst_agent

router = APIRouter(prefix="/chat", tags=["Agent Chat"])

@router.post("/", response_model=ChatResponse)
async def chat_con_agente(request: ChatRequest):
    """
    Toma un mensaje del usuario, lo pasa al grafo del agente LangGraph para
    que este tome decisiones y devuelva el análisis resultante.
    """
    # Si no nos pasan un ID de conversación, generamos uno nuevo.
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    try:
        # Petición principal que detona la cadena del Pensamiento (ReAct loop)
        mensajes = analyst_agent.agendar_consulta(request.message)
        
        # Obtenemos el último mensaje (que es donde reside el output final de AI)
        ultimo_ai_mensaje = mensajes[-1].content
        
        # Corrección exclusiva para Gemini 2.x: Extraer el texto de la lista de metadatos
        texto_final = ""
        if isinstance(ultimo_ai_mensaje, list):
            for bloque in ultimo_ai_mensaje:
                if isinstance(bloque, dict) and 'text' in bloque:
                    texto_final += bloque['text']
            if not texto_final:
                texto_final = str(ultimo_ai_mensaje)
        else:
            texto_final = str(ultimo_ai_mensaje)
            
        return ChatResponse(
            response=texto_final,
            conversation_id=conversation_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error en la interacción con el Agente: {e}"
        )
