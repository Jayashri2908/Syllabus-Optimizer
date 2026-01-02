from src.rag.retriever import RAGEngine

def test_rag():
    rag = RAGEngine()
    query = "What are the engineering program outcomes?"
    print(f"Querying: {query}")
    
    results = rag.query(query)
    
    if results['documents'][0]:
        print("\n--- Answer Found ---")
        print(results['documents'][0][0][:200] + "...")
        print("\nSource:", results['metadatas'][0][0]['source'])
    else:
        print("No results found yet.")

if __name__ == "__main__":
    test_rag()
