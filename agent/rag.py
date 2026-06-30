import chromadb
from groq import Groq
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.news_fetch import fetch_news

load_dotenv()

def ask(question, chat_history=[]):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("msme_reports")
    
    results = collection.query(query_texts=[question], n_results=3)
    chunks = results["documents"][0]
    distances = results["distances"][0]
    context = "\n\n".join(chunks)
    
    confidence = round((1 - min(distances)) * 100, 1)
    
    news_articles = fetch_news(question, max_articles=3)
    news_context = "\n".join(news_articles) if news_articles else "No recent news found."
    
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    messages = [
        {
            "role": "system",
            "content": f"""You are a market research analyst. Use the context below to answer questions.
If the context does not contain enough information, say:
"I don't have data on this topic in my knowledge base. Please upload a relevant PDF."
Never answer from your own knowledge — only use the provided context.
Always remember previous conversation for follow-up questions.

Context from documents:
{context}

Recent news:
{news_context}"""
        }
    ]
    
    for chat in chat_history:
        messages.append({"role": "user", "content": chat["user"]})
        messages.append({"role": "assistant", "content": chat["assistant"]})
    
    messages.append({"role": "user", "content": question})
    
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    
    return {
        "answer": response.choices[0].message.content,
        "confidence": confidence,
        "sources": [chunk[:200] + "..." for chunk in chunks]
    }