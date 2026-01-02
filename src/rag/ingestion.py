import os
import pdfplumber
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .vector_store import VectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIngestion:
    def __init__(self, docs_dir: str = "d:/Syllabus Optimizer/docs"):
        self.docs_dir = docs_dir
        self.vector_store = VectorStore()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def ingest_all(self):
        """Ingest all supported files from the docs directory."""
        if not os.path.exists(self.docs_dir):
            logger.warning(f"Docs directory not found: {self.docs_dir}")
            return

        files = [f for f in os.listdir(self.docs_dir) if f.lower().endswith(('.pdf', '.txt'))]
        
        for file in files:
            file_path = os.path.join(self.docs_dir, file)
            self._process_file(file_path, file)

    def _process_file(self, file_path: str, filename: str):
        logger.info(f"Processing {filename}...")
        text = ""
        
        try:
            if file_path.endswith('.pdf'):
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

            if not text:
                logger.warning(f"No text extracted from {filename}")
                return

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Prepare for Vector Store
            ids = [f"{filename}_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename, "chunk_index": i} for i in range(len(chunks))]
            
            # Add to DB
            self.vector_store.add_documents(documents=chunks, metadatas=metadatas, ids=ids)
            logger.info(f"Successfully ingested {len(chunks)} chunks from {filename}")

        except Exception as e:
            logger.error(f"Failed to ingest {filename}: {e}")

if __name__ == "__main__":
    # For manual testing
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    docs_dir = os.path.join(base_dir, "docs")
    ingestion = DocumentIngestion(docs_dir)
    ingestion.ingest_all()
