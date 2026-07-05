import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8001")

st.set_page_config(page_title="Advanced Financial AI", page_icon="📈", layout="centered")

st.title("📈 Advanced Financial Analyst AI")
st.markdown("""
**Powered by LangGraph & Hybrid Search (BM25 + ChromaDB + Cross-Encoder Re-ranking)**
Upload a 10-K or financial report, and ask quantitative or qualitative questions.
""")

# --- Sidebar: File Upload ---
with st.sidebar:
    st.header("📂 1. Upload Financial Report")
    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Process Document (Hybrid Search)"):
            with st.spinner("Chunking, Embedding, and generating BM25 indexes..."):
                try:
                    response = requests.post(
                        f"{API_URL}/upload",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                        timeout=300
                    )
                    if response.status_code == 200:
                        st.success("✅ Document processed and Hybrid Retriever built!")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")
                    
    st.markdown("---")
    st.markdown("### 🛠️ Architecture")
    st.markdown("- **Router**: LangGraph (Gemini 2.5 Flash)")
    st.markdown("- **Vector**: ChromaDB (Semantic)")
    st.markdown("- **Keyword**: BM25 (Sparse)")
    st.markdown("- **Re-ranker**: HuggingFace Cross-Encoder")

# --- Main Chat Interface ---
st.header("💬 2. Ask the Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the document..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call FastAPI Agent
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking & routing..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"question": prompt},
                    timeout=60
                )
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer found.")
                    route = data.get("route_taken", "unknown")
                    
                    # Display the route taken (very impressive for a portfolio)
                    st.caption(f"🧭 *Agent routed question to: {route}*")
                    st.markdown(answer)
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
