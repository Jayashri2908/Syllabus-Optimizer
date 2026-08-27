import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any
from pathlib import Path

class VectorStore:
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or str(Path(os.getcwd()) / "data" / "chroma_db")
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize Client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Use default Sentence Transformer embedding function (all-MiniLM-L6-v2)
        # This automatically downloads the model if not present.
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or Create Collection
        self.collection = self.client.get_or_create_collection(
            name="syllabus_knowledge_base",
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Add documents to the vector store"""
        if not documents:
            return
            
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 3) -> Dict[str, Any]:
        """Query the vector store"""
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
