import os
import chromadb
from sentence_transformers import SentenceTransformer

# Constants
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
DOCS_PATH = os.path.join(os.path.dirname(__file__), "..", "docs")
COLLECTION_NAME = "zepto_policies"

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

def init_db():
    client = get_chroma_client()
    # Check if collection exists
    try:
        client.get_collection(name=COLLECTION_NAME)
        # Collection exists, skip ingestion
        return
    except Exception:
        pass # Collection doesn't exist

    collection = client.create_collection(name=COLLECTION_NAME)
    
    # Load model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    docs = []
    ids = []
    
    # Load and chunk documents (treating each file as one chunk given their short length)
    if os.path.exists(DOCS_PATH):
        for filename in os.listdir(DOCS_PATH):
            if filename.endswith(".txt"):
                file_path = os.path.join(DOCS_PATH, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    docs.append(content)
                    ids.append(filename)
    
    if not docs:
        print("No documents found in docs/ directory.")
        return

    # Generate embeddings
    embeddings = model.encode(docs).tolist()
    
    # Store in ChromaDB
    collection.add(
        documents=docs,
        embeddings=embeddings,
        ids=ids
    )
    print(f"Ingested {len(docs)} documents into ChromaDB.")

if __name__ == "__main__":
    init_db()
