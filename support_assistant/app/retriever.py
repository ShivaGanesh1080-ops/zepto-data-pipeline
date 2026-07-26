from app.embeddings import get_chroma_client, COLLECTION_NAME
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_chunks(query: str, top_k: int = 3):
    client = get_chroma_client()
    try:
        collection = client.get_collection(name=COLLECTION_NAME)
    except ValueError:
        return [], []
    
    query_embedding = model.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    if not results['documents'] or not results['documents'][0]:
        return [], []
        
    documents = results['documents'][0]
    ids = results['ids'][0]
    
    return documents, ids
