import os
import json
import time
from groq import Groq
from dotenv import load_dotenv
import chromadb
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.news_fetch import fetch_news, fetch_web

load_dotenv()

def search_pdfs(question):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("msme_reports")
    results = collection.query(query_texts=[question], n_results=3)
    chunks = results["documents"][0]
    distances = results["distances"][0]
    raw_confidence = (1 - min(distances)) * 100
    confidence = round(max(0, min(100, raw_confidence)), 1)
    return "\n\n".join(chunks), confidence, [c[:200] + "..." for c in chunks]

def score_market(analysis_text):
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = f"""Based on this market analysis, give an Opportunity Score from 1-10.

Analysis:
{analysis_text}

Respond ONLY in this JSON format:
{{
    "score": 7.5,
    "reasoning": "one sentence explanation"
}}"""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except:
        return {"score": 5.0, "reasoning": "Could not calculate score"}

def orchestrate(question, chat_history=[]):
    # Step 1: Search PDFs
    print("Step 1: Searching PDFs...")
    pdf_context, confidence, sources = search_pdfs(question)

    # Step 2: Fetch live news
    print("Step 2: Fetching live news...")
    news = fetch_news(question, max_articles=3)
    news_context = "\n".join(news) if news else "No recent news found."
    print(f"NEWS FETCHED: {len(news)} articles")

    # Step 3: Web search with retry
    print("Step 3: Searching the web...")
    web_results = []
    for attempt in range(3):
        web_results = fetch_web(question, max_results=3)
        if web_results:
            break
        print(f"Web search attempt {attempt + 1} returned 0 results, retrying...")
        time.sleep(2)
    web_context = "\n".join(web_results) if web_results else "No web results found."
    print(f"WEB RESULTS: {len(web_results)} results")

    # Step 4: Build structured prompt
    print("Step 4: Generating structured analysis...")
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    messages = [
        {
            "role": "system",
            "content": f"""You are a senior market research analyst and business strategist.
Use the context below to answer. Prioritize document context, supplement with news and web data.
If context is insufficient on any point, say so clearly.

Context from uploaded documents:
{pdf_context}

Recent market news:
{news_context}

Web search results:
{web_context}

When answering, ALWAYS structure your response exactly like this:

**Market Overview**
[2-3 sentences on the market size, growth, and current state]

**Key Opportunities**
- [opportunity 1]
- [opportunity 2]
- [opportunity 3]

**Key Risks**
- [risk 1]
- [risk 2]
- [risk 3]

**Competitor Landscape**
[Key players, their positioning, market share if available]

**Regulatory Environment**
[Relevant regulations, policies, government initiatives]

**Recommendation**
[Clear YES / NO / CONDITIONAL with 2-3 sentence reasoning]"""
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

    answer = response.choices[0].message.content

    # Step 5: Score the market
    print("Step 5: Scoring market opportunity...")
    score_data = score_market(answer)

    return {
        "answer": answer,
        "confidence": confidence,
        "sources": sources,
        "opportunity_score": score_data.get("score", 5.0),
        "score_reasoning": score_data.get("reasoning", ""),
    }