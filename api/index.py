from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

# Aapki existing logic files ka import
# Vercel par relative imports (.) zaroori hain agar files same folder mein hon
from .parser import extract_content
from .vector_data import save_to_mongodb
from .hybrid_search_engine import hybrid_search
from .llm_service import get_llm_answer

app = FastAPI()

# CORS settings taake Streamlit cloud se connect ho sakay
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Vercel Backend is Live!"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 1. Temporary file save karein
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Content extract karein (Aapka parser.py)
        chunks = extract_content(temp_path)
        
        # 3. MongoDB Atlas mein save karein (Aapka vector_data.py)
        save_to_mongodb(chunks)
        
        # 4. Temp file delete karein
        os.remove(temp_path)
        
        return {"message": f"{file.filename} processed and synced to Atlas!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ask")
async def ask_question(question: str):
    try:
        # 1. Hybrid Search se context nikalain (Aapka hybrid_search_engine.py)
        context_chunks = hybrid_search(question)
        
        # 2. Gemini se final answer mangwayein (Aapka llm_service.py)
        answer = get_llm_answer(question, context_chunks)
        
        # 3. Sources ki list banayein (Metadata se)
        sources = list(set([chunk.get("metadata", {}).get("source", "Unknown") for chunk in context_chunks]))
        
        return {
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Vercel ko handler chahiye hota hai (Optional but good practice)
handler = app
