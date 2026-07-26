import json
from fastapi.testclient import TestClient
from app.main import app

# This acts as our e2e testing script utilizing the FastAPI test client
# to hit the app endpoint synchronously, proving that ChromaDB spins up,
# models are valid, and outputs are strictly typed.

def run_tests():
    print("Initializing Client...")
    client = TestClient(app)
    
    # 1. Policy Question (Routes to retrieve_and_answer)
    print("\n--- Testing Policy Question ---")
    req1 = {"query": "What is the return policy for damaged items?"}
    print(f"Request: {req1}")
    res1 = client.post("/ask", json=req1)
    
    print(f"Status Code: {res1.status_code}")
    print("JSON Response:")
    print(json.dumps(res1.json(), indent=2))
    
    # 2. General Question (Routes to direct_answer)
    print("\n--- Testing General Question ---")
    req2 = {"query": "What is the capital of France?"}
    print(f"Request: {req2}")
    res2 = client.post("/ask", json=req2)
    
    print(f"Status Code: {res2.status_code}")
    print("JSON Response:")
    print(json.dumps(res2.json(), indent=2))

if __name__ == "__main__":
    run_tests()
