import streamlit as st
import requests
import os
import time

API_URL = os.getenv("API_URL", "http://localhost:8001")

# 1. Page Configuration
st.set_page_config(
    page_title="Apex Financial Intelligence | Autonomous Agent",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Modern Enterprise Custom CSS
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Background & Main Container */
.stApp {
    background: radial-gradient(circle at 10% 20%, rgba(14, 20, 40, 0.95) 0%, rgba(7, 10, 20, 1) 90%);
    color: #F1F5F9;
}

/* Top Hero Card */
.hero-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
}

.hero-title {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(90deg, #60A5FA 0%, #A78BFA 50%, #34D399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.5;
}

/* Status Pill Badges */
.pill-container {
    display: flex;
    gap: 10px;
    margin-top: 14px;
    flex-wrap: wrap;
}

.pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}

.pill-green {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.pill-gold {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.pill-blue {
    background: rgba(59, 130, 246, 0.15);
    color: #60A5FA;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

.pill-purple {
    background: rgba(168, 85, 247, 0.15);
    color: #C084FC;
    border: 1px solid rgba(168, 85, 247, 0.3);
}

/* Sidebar Beautification */
section[data-testid="stSidebar"] {
    background-color: rgba(15, 23, 42, 0.95);
    border-right: 1px solid rgba(148, 163, 184, 0.1);
}

.sidebar-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(148, 163, 184, 0.12);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}

.sidebar-card-title {
    font-size: 13px;
    font-weight: 700;
    color: #E2E8F0;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Route Badge in Chat */
.route-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 10px;
}

.route-sql {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.route-market {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.route-vector {
    background: rgba(99, 102, 241, 0.15);
    color: #818CF8;
    border: 1px solid rgba(99, 102, 241, 0.3);
}

.telemetry-meta {
    display: inline-flex;
    gap: 12px;
    font-size: 11px;
    color: #94A3B8;
    margin-left: 8px;
}

/* Quick Question Chip Buttons */
div.stButton > button {
    border-radius: 10px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    background: rgba(30, 41, 59, 0.6);
    color: #E2E8F0;
    font-size: 12px;
    font-weight: 500;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    border-color: #60A5FA;
    background: rgba(59, 130, 246, 0.15);
    color: #FFFFFF;
    box-shadow: 0 0 12px rgba(59, 130, 246, 0.3);
}

/* Primary Action Buttons */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
    border: none;
    font-weight: 600;
    color: white;
}

div.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.5);
    transform: translateY(-1px);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. Sidebar: Control Center
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <span style="font-size: 26px;">💎</span>
        <div>
            <div style="font-size: 16px; font-weight: 800; color: #F8FAFC; letter-spacing: -0.3px;">APEX FINANCIAL</div>
            <div style="font-size: 11px; font-weight: 600; color: #60A5FA;">AUTONOMOUS MARKET INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Ingestion Card
    st.markdown('<div class="sidebar-card"><div class="sidebar-card-title">📁 Ingestion Pipeline</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload 10-K / Financial PDF", type=["pdf"], label_visibility="collapsed")
    
    col_proc, col_demo = st.columns(2)
    with col_proc:
        process_btn = st.button("⚡ Process PDF", type="primary", use_container_width=True)
    with col_demo:
        demo_btn = st.button("📄 Load Demo", use_container_width=True)

    if process_btn and uploaded_file is not None:
        with st.spinner("Embedding & indexing into Hybrid Retriever..."):
            try:
                res = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                    timeout=300
                )
                if res.status_code == 200:
                    st.success("✅ Hybrid Retriever Built!")
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    if demo_btn:
        with st.spinner("Loading pre-indexed Apple FY24 10-K..."):
            demo_pdf_path = "data/sample_docs/Apple_FY2024_Financial_Report.pdf"
            if os.path.exists(demo_pdf_path):
                with open(demo_pdf_path, "rb") as f:
                    try:
                        res = requests.post(
                            f"{API_URL}/upload",
                            files={"file": ("Apple_FY2024_Financial_Report.pdf", f.read(), "application/pdf")},
                            timeout=300
                        )
                        if res.status_code == 200:
                            st.success("✅ Demo Loaded (Apple FY24)")
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
            else:
                st.warning("Demo file not found locally.")
                
    st.markdown('</div>', unsafe_allow_html=True)

    # Agent Architecture & Pipeline Card
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">⚙️ Agent Infrastructure</div>
        <div style="font-size: 12px; color: #CBD5E1; line-height: 1.8;">
            <div>🧠 <b>Router:</b> 3-Way LangGraph Agent</div>
            <div>📡 <b>Live Tool:</b> yfinance Market Telemetry</div>
            <div>⚡ <b>SQL Engine:</b> SQLite Text-to-SQL</div>
            <div>🔍 <b>Vector Store:</b> ChromaDB (MiniLM-L6)</div>
            <div>📊 <b>Sparse Search:</b> BM25 Okapi</div>
            <div>🎯 <b>Re-ranker:</b> Cross-Encoder (bge)</div>
            <div>🔭 <b>Observability:</b> Langfuse Cloud OTel</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # System Status Card
    backend_status = "Online (200 OK)"
    try:
        health_res = requests.get(f"{API_URL}/health", timeout=2)
        if health_res.status_code == 200:
            status_color = "#34D399"
            status_dot = "🟢"
        else:
            status_color = "#F87171"
            status_dot = "🔴"
            backend_status = "Degraded"
    except Exception:
        status_color = "#F87171"
        status_dot = "🔴"
        backend_status = "Offline"

    st.markdown(f"""
    <div class="sidebar-card" style="padding: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px;">
            <span style="color: #94A3B8;">FastAPI Backend:</span>
            <span style="color: {status_color}; font-weight: 700;">{status_dot} {backend_status}</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; margin-top: 6px;">
            <span style="color: #94A3B8;">Agent Engine:</span>
            <span style="color: #60A5FA; font-weight: 700;">LangGraph + Gemini</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; margin-top: 6px;">
            <span style="color: #94A3B8;">Tracing:</span>
            <span style="color: #C084FC; font-weight: 700;">Langfuse Active</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 4. Main View: Hero Header
st.markdown("""
<div class="hero-card">
    <div class="hero-title">Apex Financial Analyst AI</div>
    <div class="hero-subtitle">
        Autonomous Financial Intelligence combining <b>3-Way LangGraph Routing</b>, real-time <b>yfinance Market Telemetry</b>, deterministic <b>SQLite Text-to-SQL</b>, and <b>Two-Stage Hybrid RAG</b>.
    </div>
    <div class="pill-container">
        <div class="pill pill-gold">📈 Real-Time yfinance Live</div>
        <div class="pill pill-green">🟢 SQLite Text-to-SQL Live</div>
        <div class="pill pill-blue">🔍 Hybrid BM25 + Vector Search</div>
        <div class="pill pill-purple">🔭 Langfuse Observability Instrument</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. Quick Suggestion Chips (Prompt Starters)
st.markdown("<div style='font-size: 13px; font-weight: 600; color: #94A3B8; margin-bottom: 8px;'>⚡ TRY A SAMPLE QUESTION:</div>", unsafe_allow_html=True)
q_col1, q_col2, q_col3, q_col4 = st.columns(4)

prompt_to_send = None
with q_col1:
    if st.button("📈 Live Quote: Apple ($AAPL)", use_container_width=True):
        prompt_to_send = "What is Apple current stock price, market cap, and P/E ratio today?"
with q_col2:
    if st.button("⚡ Live Quote: Tesla ($TSLA)", use_container_width=True):
        prompt_to_send = "What is Tesla stock price and market valuation today?"
with q_col3:
    if st.button("📊 Audited 2024 Net Sales", use_container_width=True):
        prompt_to_send = "What was Apple's total net sales and iPhone revenue in 2024?"
with q_col4:
    if st.button("⚠️ Supply Chain Risk Disclosures", use_container_width=True):
        prompt_to_send = "What are the primary geopolitical and supply chain risks mentioned in the report?"

# 6. Chat History Management
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "metadata" in message:
            meta = message["metadata"]
            route = meta.get("route", "unknown")
            latency = meta.get("latency", 0)
            
            if route == "sql_database":
                badge_html = f'<div class="route-badge route-sql">⚡ Structured Route: Text-to-SQL Engine <span class="telemetry-meta">⏱️ {latency}ms | 📊 Langfuse Traced</span></div>'
            elif route == "live_market_data":
                badge_html = f'<div class="route-badge route-market">📈 Real-Time Route: Live yfinance API Telemetry <span class="telemetry-meta">⏱️ {latency}ms | 📊 Langfuse Traced</span></div>'
            else:
                badge_html = f'<div class="route-badge route-vector">🔍 Unstructured Route: Hybrid RAG + Re-ranker <span class="telemetry-meta">⏱️ {latency}ms | 📊 Langfuse Traced</span></div>'
            st.markdown(badge_html, unsafe_allow_html=True)
            
        st.markdown(message["content"])

# 7. User Input Handling
user_input = st.chat_input("Ask a real-time quote, quantitative statement, or qualitative question...")
active_prompt = prompt_to_send or user_input

if active_prompt:
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    with st.chat_message("user"):
        st.markdown(active_prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent routing through LangGraph & executing pipeline..."):
            try:
                start_req = time.time()
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"question": active_prompt, "user_id": "portfolio_evaluator"},
                    timeout=90
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer found.")
                    route = data.get("route_taken", "unknown")
                    latency_ms = data.get("latency_ms", round((time.time() - start_req) * 1000))

                    if route == "sql_database":
                        badge_html = f'<div class="route-badge route-sql">⚡ Structured Route: Text-to-SQL Engine <span class="telemetry-meta">⏱️ {latency_ms}ms | 📊 Langfuse Traced</span></div>'
                    elif route == "live_market_data":
                        badge_html = f'<div class="route-badge route-market">📈 Real-Time Route: Live yfinance API Telemetry <span class="telemetry-meta">⏱️ {latency_ms}ms | 📊 Langfuse Traced</span></div>'
                    else:
                        badge_html = f'<div class="route-badge route-vector">🔍 Unstructured Route: Hybrid RAG + Re-ranker <span class="telemetry-meta">⏱️ {latency_ms}ms | 📊 Langfuse Traced</span></div>'
                    
                    st.markdown(badge_html, unsafe_allow_html=True)
                    st.markdown(answer)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "metadata": {"route": route, "latency": latency_ms}
                    })
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")
