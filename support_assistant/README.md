# Zepto Support Assistant

A generative AI support assistant designed to handle customer inquiries for Zepto. This module implements a fully functional RAG (Retrieval-Augmented Generation) pipeline using LangGraph and FastAPI, with a robust Mock mode that deterministically processes requests without requiring network LLM API calls.

## Project Overview

The Zepto Support Assistant uses LangGraph to orchestrate a StateGraph that classifies incoming intents and retrieves policy information using vector search (ChromaDB + Sentence Transformers). It then returns the generated response.

The default graded configuration uses a strict deterministic Mock Mode (`MOCK_LLM=1`), meaning no API keys or cloud services are required. An optional Real LLM Mode (`MOCK_LLM=0`) is also implemented.

## Architecture & ASCII RAG Pipeline

The application follows a structured RAG pipeline:

```text
       [Ingestion]                            [Query]
            |                                    |
            v                                    v
     (app/embeddings.py)                 (app/graph.py)
            |                            classify_intent
            v                                    |
      Chunking (per-file)                   (Keyword routing)
            |                                    |
            v                             -------+-------
       [Embedding]                       |               |
   (Sentence-Transformers)        policy_question  general_question
            |                            |               |
            v                            v               |
        ChromaDB               [Retrieval] (app/retriever.py)
      (Vector Store)               Similarity Search     |
                                         |               |
                                         v               v
                                  [Generation]    [Generation]
                             (retrieve_and_answer) (direct_answer)
```

### Pipeline Explanation

1. **Ingestion**: Documents from `docs/` are loaded, where each document serves as a single chunk given their concise length. Handled by `app/embeddings.py`.
2. **Embedding**: The loaded documents are encoded into dense vectors using the open-source `sentence-transformers/all-MiniLM-L6-v2` model. This is executed fully locally.
3. **Retrieval**: When a query is classified as a policy question, `app/retriever.py` embeds the query and retrieves the Top-3 closest chunks from the local `ChromaDB` via cosine similarity. This step always runs genuinely regardless of MOCK mode.
4. **Generation (Branching)**: 
   - **MOCK_LLM=1 (Default/Graded)**: The `retrieve_and_answer` node deterministically returns a templated response (`Based on the retrieved context: <top_chunk>...`). The `direct_answer` node returns a fixed string (`I can only answer questions about Zepto policies right now.`).
   - **MOCK_LLM=0 (Optional/Real)**: A call to an LLM provider (e.g., Groq) is made using a structured prompt template from `app/prompts.py` which enforces negative constraints and few-shot examples. It also implements a retry-on-failure structure.

## Installation & Running Locally

1. Create a virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 7860
```
On startup, ChromaDB will automatically ingest the files from `/docs` if it hasn't already.

## Docker Deployment

This repository includes a production-ready `Dockerfile`.

1. Build the image:
```bash
docker build -t zepto-support-assistant .
```
2. Run the container:
```bash
docker run -p 7860:7860 zepto-support-assistant
```
The FastAPI endpoint will be available at `http://localhost:7860/ask`.

## Example API Calls

The following calls were made with `MOCK_LLM=1` (the default mode).

### 1. Policy Question (Triggers Retrieval)
**Request:**
```json
{
  "query": "What is the return policy for damaged items?"
}
```

**Response:**
```json
{
  "answer": "Based on the retrieved context: If an order arrives with damaged, spoiled, or missing items, customers must report it within 24 hours of delivery through the 'Report an Issue' button on the order page. Zepto ships a free replacement",
  "sources": [
    "doc_06.txt",
    "doc_02.txt",
    "doc_05.txt"
  ],
  "confidence": 1.0
}
```

### 2. General Question (Bypasses Retrieval)
**Request:**
```json
{
  "query": "What is the capital of France?"
}
```

**Response:**
```json
{
  "answer": "I can only answer questions about Zepto policies right now.",
  "sources": [],
  "confidence": 1.0
}
```
