import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from parser import extract_content
from vector_data import add_to_mongodb 
# from search_engine import perform_hybrid_search 
from llm_service import generate_answer
from hybrid_search_engine import perform_hybrid_search
# FastAPI initialization
app = FastAPI(title="Tesla AI RAG System v5")

@app.post("/ingest/")
async def ingest_file(file: UploadFile = File(...)):
    """
    Step 1: PDF ko save kerna
    Step 2: Jina Reader se text nikalna (Markdown format)
    Step 3: Jina v5 se embed karke MongoDB Atlas me store kerna
    """
    path = f"temp_{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # PDF se content extract kerna
        chunks = extract_content(path)
        
        # Database me store kerna
        success = add_to_mongodb(chunks, file.filename)
        
        # Temp file delete kerna
        os.remove(path)
        
        if success:
            return {"status": "Success", "message": f"Ingested {len(chunks)} chunks from {file.filename}"}
        else:
            raise HTTPException(status_code=500, detail="Database insertion failed.")
            
    except Exception as e:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ask/")
async def ask_question(question: str):
    """
    Step 1: Atlas Vector Search se relevant chunks dhoondna
    Step 2: Jina Reranker v2 se accuracy filter kerna
    Step 3: Groq LLM se final answer generate kerna
    """
    try:
        # Search engine ko call kerna (Vector Search + Rerank)
        results = perform_hybrid_search(question, "vector_store", n_results=4)
        
        if not results:
            return {"question": question, "answer": "Mujhe is sawal ka jawab documents mein nahi mila."}
        
        # LLM se final answer lena
        answer = generate_answer(question, results)
        
        # Sources nikalna
        sources = list(set([res['metadata']['source'] for res in results]))
        
        return {
            "question": question, 
            "answer": answer,
            "sources": sources
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)