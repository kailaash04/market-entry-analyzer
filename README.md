 📊 Market Entry Analyzer

An agentic RAG-powered market intelligence platform that helps businesses decide whether entering a new market is worth it.

Ask a single question — the system automatically searches internal documents, fetches live news, scans the web, scores the opportunity, and generates a structured business report.



 🎯 What it does

> "Should a fintech startup enter the MSME lending market in India?"

Instead of a simple text answer, the system runs a 5-step orchestration pipeline:

1. Searches uploaded PDFs (industry reports, regulatory documents) via semantic search
2. Fetches live news relevant to the query
3. Searches the web for current market data
4. Generates a structured analysis — Market Overview, Opportunities, Risks, Competitor Landscape, Regulatory Environment, Recommendation
5. Scores the opportunity 1-10 with reasoning

The user gets a confidence-scored, source-cited, boardroom-ready answer — and can export it as a PDF report.



 ✨ Features

- 🔍 RAG Pipeline — ChromaDB vector search over uploaded PDF documents
- 🌐 Live Web Intelligence — real-time news and web search via DuckDuckGo
- 🤖 Agentic Orchestration — multi-step pipeline that combines document, news, and web context
- 📈 Opportunity Scoring — AI-generated 1-10 market attractiveness score with reasoning
- 💬 Conversational Memory — follow-up questions retain full context
- 📊 CSV Analysis — upload structured data and get AI-generated Plotly visualizations
- 📄 PDF Report Export — download a professional, boardroom-ready analysis report
- 🎨 Premium Dark UI — custom-styled Streamlit interface with confidence/opportunity indicators
- ⚡ REST API — FastAPI backend with auto-generated Swagger documentation



 🏗️ Architecture

Streamlit (UI) leads to FastAPI (REST API) leads to the Orchestrator (Agentic Pipeline), which fans out to three parallel sources: PDF Search via ChromaDB, Live News via DuckDuckGo, and Web Search via DuckDuckGo. All three feed into the Groq LLM (Llama 3.3 70B), which produces the final Structured Analysis and Opportunity Score.



 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq (Llama 3.3 70B Versatile) |
| Vector Database | ChromaDB |
| Backend | FastAPI |
| Frontend | Streamlit |
| Web/News Search | DuckDuckGo Search API |
| Data Analysis | Pandas + Plotly |
| PDF Processing | PyPDF |
| Report Generation | ReportLab |



 🚀 Getting Started

 Prerequisites
- Python 3.10+
- A free Groq API key from console.groq.com

 Installation

Clone the repo, then run:

    git clone https://github.com/kailaash04/market-entry-analyzer.git
    cd market-entry-analyzer
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt

Create a `.env` file with:

    GROQ_API_KEY=your_key_here

 Running the app

Terminal 1 — Start the API:

    uvicorn main:app --reload --reload-exclude venv

Terminal 2 — Start the UI:

    python -m streamlit run ui/app.py

Visit `http://localhost:8501` to use the app.
API docs available at `http://localhost:8000/docs`

---

 📁 Project Structure

    market-entry-analyzer/
    ├── agent/
    │   └── orchestrator.py      Multi-step agentic pipeline
    ├── tools/
    │   ├── news_fetch.py        Live news + web search
    │   └── report_export.py     PDF report generation
    ├── ui/
    │   └── app.py                Streamlit frontend
    ├── main.py                   FastAPI backend
    └── requirements.txt

---

📌 Roadmap

This project is under active development, evolving from a document Q&A tool into a full agentic market intelligence platform.

Completed
- PDF ingestion + ChromaDB vector search
- Agentic orchestrator combining PDF, live news, and web search
- Opportunity scoring with reasoning
- Structured business analysis output (Market Overview, Risks, Opportunities, Competitors, Regulatory Environment, Recommendation)
- CSV analysis with AI-generated Plotly visualizations
- PDF report export
- Conversation memory across follow-up questions
- Premium custom UI

In Progress / Planned
- Multi-document comparison (compare two markets side by side)
- Persistent conversation memory across sessions (database-backed)
- Dedicated Competitor Analysis agent
- Boardroom-grade PDF report design (cover page, executive summary, branded layout)
- Deployment to a public cloud endpoint



 👤 Author

B.Kailaash 
Computer Science Engineering Graduate | Data & AI Enthusiast

GitHub: https://github.com/kailaash04
