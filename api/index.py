import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Vercel ke liye relative imports (sath dot '.' lagana lazmi hai)
from parser import extract_content
from vector_data import add_to_mongodb 
from llm_service import generate_answer
from hybrid_search_engine import perform_hybrid_search

app = FastAPI(title="Tesla AI RAG System v5")

# CORS Add karein taake Streamlit is se baat kar sakay
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/ingest") # Streamlit mein /ingest/ update kar dena
async def ingest_file(file: UploadFile = File(...)):
    path = f"/tmp/temp_{file.filename}" # Vercel pe sirf /tmp folder allowed hai
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        chunks = extract_content(path)
        success = add_to_mongodb(chunks, file.filename)
        if os.path.exists(path):
            os.remove(path)
        
        if success:
            return {"status": "Success", "message": f"Ingested {len(chunks)} chunks"}
        else:
            raise HTTPException(status_code=500, detail="Database insertion failed.")
    except Exception as e:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ask")
async def ask_question(question: str):
    try:
        results = perform_hybrid_search(question, "vector_store", n_results=4)
        if not results:
            return {"answer": "Documents mein jawab nahi mila."}
        
        answer = generate_answer(question, results)
        sources = list(set([res['metadata']['source'] for res in results]))
        
        return {"answer": answer, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
