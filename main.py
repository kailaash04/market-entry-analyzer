from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from agent.orchestrator import orchestrate
from typing import List, Optional
import chromadb
from pypdf import PdfReader
import io

app = FastAPI(title="Market Entry Analyzer")

class Message(BaseModel):
    user: str
    assistant: str

class Query(BaseModel):
    question: str
    chat_history: Optional[List[Message]] = []

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

@app.get("/")
def home():
    return {"message": "Market Entry Analyzer is running"}

@app.post("/analyze")
def analyze(query: Query):
    history = [{"user": m.user, "assistant": m.assistant} for m in query.chat_history]
    result = orchestrate(query.question, history)
    return {
        "question": query.question,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "sources": result["sources"],
        "opportunity_score": result["opportunity_score"],
        "score_reasoning": result["score_reasoning"]
    }

@app.post("/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    reader = PdfReader(io.BytesIO(contents))
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + " "
    chunks = chunk_text(full_text)
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        collection = client.get_collection("msme_reports")
    except:
        collection = client.create_collection("msme_reports")
    existing = collection.count()
    ids = [f"chunk_{existing + i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)
    return {"message": f"Ingested {len(chunks)} chunks from {file.filename}"}