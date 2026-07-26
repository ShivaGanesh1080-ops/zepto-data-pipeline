from fastapi import FastAPI, HTTPException
from app.models import AskRequest, AskResponse
from app.graph import app_graph
from app.embeddings import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Zepto Support Assistant")

@app.on_event("startup")
def startup_event():
    logger.info("Initializing ChromaDB and embeddings on startup...")
    init_db()

@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    try:
        initial_state = {
            "query": request.query,
            "intent": "",
            "answer": "",
            "sources": [],
            "confidence": 0.0
        }
        
        result = app_graph.invoke(initial_state)
        
        return AskResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=7860, reload=True)
