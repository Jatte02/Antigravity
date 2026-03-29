"""
Retriever basado en FAISS y Embeddings para MarketSense.
(Recuperación indexada para búsqueda de similitud). 
"""

import os

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from backend.rag.embeddings import get_embeddings


class DocumentRetriever:
    """Clase simplificada para indexación local en FAISS de textos extensos."""
    
    def __init__(self, index_path: str = "./faiss_index"):
        self.index_path = index_path
        self.embeddings = get_embeddings()
        self.vector_store = None
        self._load_or_create()

    def _load_or_create(self):
        """Carga el índice FAISS si existe, de lo contrario lo prepara vacío."""
        if os.path.exists(self.index_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.index_path, 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
            except Exception:
                self.vector_store = None
                
    def ingest_documents(self, documents: list[Document]):
        """Añade documentos y los indexa."""
        if not documents:
            return
            
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store.add_documents(documents)
            
        self.vector_store.save_local(self.index_path)

    def retrieve(self, query: str, k: int = 3) -> list[Document]:
        """Recupera los K documentos más similares a la consulta de búsqueda."""
        if self.vector_store is None:
            return []
        
        return self.vector_store.similarity_search(query, k=k)
