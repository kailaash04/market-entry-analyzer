import streamlit as st
import requests
import pandas as pd
import json
import os
import sys
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.report_export import generate_pdf_report

st.set_page_config(
    page_title="Market Entry Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { background-color: #000000 !important; color: #b8bcc8 !important; }
[data-testid="stAppViewContainer"] {
    background-color: #000000;
    background-image: linear-gradient(rgba(255,255,255,0.018) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(255,255,255,0.018) 1px, transparent 1px);
    background-size: 32px 32px;
}
[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 0.5px solid #1a1d24 !important; }
[data-testid="stSidebar"] * { color: #b8bcc8 !important; }
.stChatMessage { background: transparent !important; border: none !important; }
[data-testid="stChatMessageContent"] {
    background: #0d0d0d !important; border: 0.5px solid #1a1d24 !important;
    border-left: 2px solid #378ADD !important; border-radius: 0 10px 10px 10px !important;
    color: #b8bcc8 !important; font-size: 13px !important; line-height: 1.75 !important;
}
[data-testid="stChatInput"] { background: #0d0d0d !important; border: 0.5px solid #1e2230 !important; border-radius: 8px !important; color: #b8bcc8 !important; }
.stButton > button { background: #1a56db !important; color: #fff !important; border: none !important; border-radius: 8px !important; font-weight: 500 !important; }
.stMetric { background: #0d0d0d !important; border: 0.5px solid #1a1d24 !important; border-radius: 8px !important; padding: 10px !important; }
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; color: #dde2ee !important; }
[data-testid="stFileUploader"] { background: #0d0d0d !important; border: 0.5px dashed #1e2230 !important; border-radius: 8px !important; }
.stSuccess { background: #061a0e !important; border: 0.5px solid #14532d !important; color: #22c55e !important; border-radius: 8px !important; }
.stSpinner > div { border-top-color: #378ADD !important; }
div[data-testid="stExpander"] { background: #0d0d0d !important; border: 0.5px solid #1a1d24 !important; border-radius: 8px !important; }
.conf-bar { display: flex; align-items: center; gap: 8px; margin: 8px 0; }
.conf-track { width: 80px; height: 4px; background: #1a1d24; border-radius: 2px; overflow: hidden; }
.conf-fill { height: 100%; border-radius: 2px; }
.conf-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; }
.source-card { background: #050505; border-left: 2px solid #1e3a6e; padding: 6px 10px; border-radius: 0 4px 4px 0; font-size: 11px; color: #363c4a; margin: 4px 0; line-height: 1.5; }
.doc-card { background: #0d0d0d; border: 0.5px solid #1a1d24; border-left: 2px solid #22c55e; border-radius: 8px; padding: 8px 12px; margin: 4px 0; font-size: 12px; }
.doc-name { color: #b8bcc8; font-weight: 500; }
.doc-meta { color: #2e3340; font-size: 10px; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }
.topbar { background: #050505; border-bottom: 0.5px solid #1a1d24; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; margin: -1rem -1rem 1rem -1rem; }
.live-badge { background: #061a0e; border: 0.5px solid #14532d; color: #22c55e; font-size: 11px; padding: 3px 10px; border-radius: 20px; font-family: 'JetBrains Mono', monospace; }
.brand-name { font-size: 15px; font-weight: 500; color: #dde2ee; }
.brand-sub { font-size: 10px; color: #363c4a; letter-spacing: 0.05em; }
.score-bar { display: flex; align-items: center; gap: 8px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "total_chunks" not in st.session_state:
    st.session_state.total_chunks = 0
if "docs" not in st.session_state:
    st.session_state.docs = [{"name": "MSME-Sampark.pdf", "chunks": 33}]

def get_conf_color(score):
    if score >= 80: return "#22c55e"
    elif score >= 60: return "#eab308"
    else: return "#ef4444"

def get_opp_color(score):
    if score >= 7: return "#22c55e"
    elif score >= 5: return "#eab308"
    else: return "#ef4444"

def render_conf_bar(score):
    color = get_conf_color(score)
    return f"""<div class="conf-bar">
        <span class="conf-label" style="color:#2e3340">conf</span>
        <div class="conf-track"><div class="conf-fill" style="width:{score}%;background:{color}"></div></div>
        <span class="conf-label" style="color:{color}">{score}%</span>
    </div>"""

def render_opp_score(score, reasoning):
    color = get_opp_color(score)
    width = score * 10
    return f"""<div class="score-bar">
        <span class="conf-label" style="color:#2e3340">opp</span>
        <div class="conf-track" style="width:100px">
            <div class="conf-fill" style="width:{width}%;background:{color}"></div>
        </div>
        <span class="conf-label" style="color:{color};font-size:13px;font-weight:500">{score}/10</span>
        <span style="font-size:11px;color:#363c4a">— {reasoning}</span>
    </div>"""

def analyze_csv_inline(df, question):
    from groq import Groq
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    summary = f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\nColumns: {list(df.columns)}\nSample:\n{df.head(3).to_string()}\nStats:\n{df.describe().to_string()}"
    prompt = f"""You are a data analyst. Given this CSV summary, answer the question and suggest a chart.
Data: {summary}
Question: {question}
Respond ONLY in this JSON format:
{{"insight": "analysis here", "chart_type": "bar or line or pie or scatter", "x_column": "col name", "y_column": "col name", "title": "chart title"}}"""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except:
        return {"insight": raw, "chart_type": "bar", "x_column": df.columns[0], "y_column": df.columns[1] if len(df.columns) > 1 else df.columns[0], "title": question}

def create_chart_inline(df, config):
    import plotly.express as px
    chart_type = config.get("chart_type", "bar")
    x = config.get("x_column", df.columns[0])
    y = config.get("y_column", df.columns[1] if len(df.columns) > 1 else df.columns[0])
    title = config.get("title", "Chart")
    if x not in df.columns: x = df.columns[0]
    if y not in df.columns: y = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    fns = {"bar": px.bar, "line": px.line, "scatter": px.scatter}
    fig = fns.get(chart_type, px.bar)(df, x=x, y=y, title=title) if chart_type != "pie" else px.pie(df, names=x, values=y, title=title)
    fig.update_layout(paper_bgcolor="#0d0d0d", plot_bgcolor="#0d0d0d", font_color="#b8bcc8", title_font_color="#dde2ee")
    return fig

with st.sidebar:
    st.markdown('<div class="brand-name">Market Entry Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">RAG · GROQ · CHROMADB</div>', unsafe_allow_html=True)
    st.divider()

    st.markdown('<div style="font-size:10px;color:#2e3340;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px">Knowledge Base</div>', unsafe_allow_html=True)
    for doc in st.session_state.docs:
        st.markdown(f'<div class="doc-card"><div class="doc-name">{doc["name"]}</div><div class="doc-meta">{doc["chunks"]} chunks · ready</div></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div style="font-size:10px;color:#2e3340;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px">Add Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type="pdf", label_visibility="collapsed")
    if uploaded_file:
        with st.spinner("Ingesting..."):
            response = requests.post("http://127.0.0.1:8000/ingest", files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")})
            if response.status_code == 200:
                chunks = response.json().get("message", "").split()[1]
                st.session_state.docs.append({"name": uploaded_file.name, "chunks": int(chunks)})
                st.success(f"Ingested {chunks} chunks")

    st.divider()
    st.markdown('<div style="font-size:10px;color:#2e3340;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px">Analyze CSV</div>', unsafe_allow_html=True)
    csv_file = st.file_uploader("", type="csv", label_visibility="collapsed", key="csv")
    if csv_file:
        st.session_state.csv_df = pd.read_csv(csv_file)
        st.success(f"Loaded {len(st.session_state.csv_df)} rows")
    if "csv_df" in st.session_state:
        csv_question = st.text_input("Ask about your data:", placeholder="Which sector has highest revenue?")
        if st.button("Analyze CSV"):
            with st.spinner("Analyzing..."):
                config = analyze_csv_inline(st.session_state.csv_df, csv_question)
                st.session_state.csv_insight = config.get("insight", "")
                st.session_state.csv_fig = create_chart_inline(st.session_state.csv_df, config)

    st.divider()
    st.markdown('<div style="font-size:10px;color:#2e3340;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px">Session</div>', unsafe_allow_html=True)
    avg_conf = 0
    if st.session_state.chat_history:
        avg_conf = round(sum(c["confidence"] for c in st.session_state.chat_history) / len(st.session_state.chat_history))
    col1, col2 = st.columns(2)
    with col1: st.metric("Queries", len(st.session_state.chat_history))
    with col2: st.metric("Avg conf.", f"{avg_conf}%")
    st.metric("Chunks searched", st.session_state.total_chunks)

st.markdown(f"""<div class="topbar">
    <div><div class="brand-name">Market Entry Analyzer</div><div class="brand-sub">RAG · GROQ · CHROMADB</div></div>
    <div class="live-badge">● API live &nbsp;·&nbsp; {st.session_state.total_chunks} chunks searched</div>
</div>""", unsafe_allow_html=True)

for chat in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(f'<span style="color:#8ab4e8;font-size:13px">{chat["user"]}</span>', unsafe_allow_html=True)
    with st.chat_message("assistant"):
        st.markdown(chat["answer"])
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(render_conf_bar(chat["confidence"]), unsafe_allow_html=True)
        with col2:
            st.markdown(render_opp_score(chat.get("opportunity_score", 0), chat.get("score_reasoning", "")), unsafe_allow_html=True)
        with st.expander("Sources"):
            for src in chat["sources"]:
                st.markdown(f'<div class="source-card">{src}</div>', unsafe_allow_html=True)
        pdf_bytes = generate_pdf_report(
            chat["user"], chat["answer"], chat["confidence"],
            chat.get("opportunity_score", 0), chat.get("score_reasoning", ""), chat["sources"]
        )
        st.download_button(
            label="📄 Download Report",
            data=pdf_bytes,
            file_name="market_entry_report.pdf",
            mime="application/pdf",
            key=f"dl_{chat['user'][:20]}"
        )

if "csv_fig" in st.session_state:
    st.divider()
    st.markdown("### 📈 Data Analysis")
    st.markdown(st.session_state.csv_insight)
    st.plotly_chart(st.session_state.csv_fig, use_container_width=True)

question = st.chat_input("Ask a question about market entry...")
if question:
    with st.chat_message("user"):
        st.markdown(f'<span style="color:#8ab4e8;font-size:13px">{question}</span>', unsafe_allow_html=True)
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = requests.post(
                "http://127.0.0.1:8000/analyze",
                json={
                    "question": question,
                    "chat_history": [{"user": c["user"], "assistant": c["answer"]} for c in st.session_state.chat_history]
                }
            )
            if response.status_code == 200:
                data = response.json()
                answer = data["answer"]
                confidence = data["confidence"]
                sources = data["sources"]
                opp_score = data.get("opportunity_score", 0)
                score_reasoning = data.get("score_reasoning", "")

                st.markdown(answer)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(render_conf_bar(confidence), unsafe_allow_html=True)
                with col2:
                    st.markdown(render_opp_score(opp_score, score_reasoning), unsafe_allow_html=True)
                with st.expander("Sources"):
                    for src in sources:
                        st.markdown(f'<div class="source-card">{src}</div>', unsafe_allow_html=True)

                pdf_bytes = generate_pdf_report(
                    question, answer, confidence,
                    opp_score, score_reasoning, sources
                )
                st.download_button(
                    label="📄 Download Report",
                    data=pdf_bytes,
                    file_name="market_entry_report.pdf",
                    mime="application/pdf",
                    key=f"dl_new_{question[:20]}"
                )

                st.session_state.chat_history.append({
                    "user": question,
                    "answer": answer,
                    "confidence": confidence,
                    "sources": sources,
                    "opportunity_score": opp_score,
                    "score_reasoning": score_reasoning
                })
                st.session_state.total_chunks += 3
                st.rerun()
            else:
                st.error("Something went wrong. Make sure FastAPI is running.")

st.divider()
st.caption("Built with FastAPI + ChromaDB + Groq + LlamaIndex")