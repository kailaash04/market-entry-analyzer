import chromadb
from pypdf import PdfReader
import os

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest_pdf(pdf_path):
    print(f"Reading {pdf_path}...")
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + " "

    print(f"Chunking text...")
    chunks = chunk_text(full_text)
    print(f"Total chunks: {len(chunks)}")

    client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        client.delete_collection("msme_reports")
    except:
        pass
    
    collection = client.create_collection("msme_reports")

    ids = [f"chunk_{i}" for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids)
    print(f"Stored {len(chunks)} chunks in ChromaDB!")

if __name__ == "__main__":
    pdf_path = "./data/MSME-SAMPARK-2.0-REPORT.pdf"
    ingest_pdf(pdf_path)