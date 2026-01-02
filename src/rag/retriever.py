from typing import List, Dict, Any
from .vector_store import VectorStore

class RAGEngine:
    def __init__(self):
        self.vector_store = VectorStore()

    def query(self, question: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Query the knowledge base.
        Returns detailed results including documents and metadata.
        """
        results = self.vector_store.query(query_text=question, n_results=n_results)
        return results

    def get_context(self, question: str) -> str:
        """
        Get a simplified string context for LLM prompting.
        """
        results = self.query(question)
        documents = results.get('documents', [[]])[0]
        
        context = "\n\n".join(documents)
        return context
