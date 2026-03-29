"""
Configuración de modelos de Embedding usando Google Gemini.
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def get_embeddings():
    """Retorna la instancia de Embeddings de Google Gemini Text."""
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
    )
