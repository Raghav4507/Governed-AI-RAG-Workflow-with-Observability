from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from .ingest_pdfs import ingest_pdf
from .rag_pipeline import rag_answer

app = FastAPI(title="Governed RAG with Observability")

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
os.makedirs(PDF_DIR, exist_ok=True)

@app.post("/ingest")
async def ingest_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    dest_path = os.path.join(PDF_DIR, file.filename)
    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    ingest_pdf(dest_path, title=file.filename)
    return {"status": "ok", "file": file.filename}

@app.post("/ask")
async def ask_endpoint(payload: dict):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query'")

    try:
        result = rag_answer(query=query)
        return JSONResponse(
            {
                "answer": result["answer"],
                "model": result["model"],
                "usage": result["usage"],
                "num_chunks": len(result["chunks"]),
                "chunks": result["chunks"],
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))