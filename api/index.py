from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# CORS allow karna zaroori hai taake Streamlit is se baat kar sakay
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
    # Yahan aapka parser_logic call hoga
    return {"message": f"{file.filename} processed successfully"}

@app.get("/api/ask")
async def ask_question(question: str):
    # Yahan aapka query_engine call hoga
    # response = get_answer_from_rag(question)
    return {
        "answer": f"Backend Response for: {question}",
        "sources": ["Page 1", "Table 2"]
    }
