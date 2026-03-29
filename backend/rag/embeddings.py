"""
Configuración de modelos de Embedding usando Google Gemini.
"""

import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def get_embeddings():
    """Retorna la instancia de Embeddings de Google Gemini Text."""
    api_key = os.getenv("GEMINI_API_KEY") or "mock_key_solo_para_arrancar"
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key,
    )
