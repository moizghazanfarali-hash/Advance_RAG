import streamlit as st
import requests
import os
from datetime import datetime

# ── Configuration ──────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="DocMind AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #0f1117 !important;
    color: #e2e4ea !important;
    font-family: 'DM Sans', sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 2rem 2.5rem !important; max-width: 100% !important; }

[data-testid="stSidebar"] {
    background: #13151d !important;
    border-right: 1px solid #1e2130 !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div { padding: 1.8rem 1.4rem !important; }

.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 2rem;
}
.logo-icon {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #00e5a0, #0066ff);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}
.logo-text {
    font-family: 'DM Mono', monospace;
    font-size: 15px;
    font-weight: 500;
    color: #e2e4ea;
    letter-spacing: 0.3px;
}
.logo-sub {
    font-size: 10px;
    color: #4a5068;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 1px;
}

.section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a5068;
    margin-bottom: 10px;
    margin-top: 1.5rem;
}

[data-testid="stFileUploader"] {
    background: #1a1d27 !important;
    border: 1px dashed #2a2d3e !important;
    border-radius: 10px !important;
    padding: 8px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #00e5a0 !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploader"] small { color: #4a5068 !important; font-size: 11px !important; }

[data-testid="stFileUploader"] button {
    background: transparent !important;
    border: 1px solid #2a2d3e !important;
    color: #8b8fa8 !important;
    border-radius: 7px !important;
    font-size: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 6px 14px !important;
}
[data-testid="stFileUploader"] button:hover {
    border-color: #00e5a0 !important;
    color: #00e5a0 !important;
}

.file-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0,229,160,0.06);
    border: 1px solid rgba(0,229,160,0.15);
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 10px;
    font-size: 12px;
    color: #00e5a0;
}
.file-badge-name {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 140px;
    color: #c8cad6;
    font-size: 12px;
}

.status-row {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 12px;
    color: #4a5068;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid #1e2130;
}
.dot-green { width: 6px; height: 6px; border-radius: 50%; background: #00e5a0; box-shadow: 0 0 6px #00e5a0; flex-shrink: 0; }
.dot-red   { width: 6px; height: 6px; border-radius: 50%; background: #ff4d6a; flex-shrink: 0; }

.page-header {
    margin-bottom: 1.8rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid #1e2130;
}
.page-title {
    font-size: 20px;
    font-weight: 600;
    color: #e2e4ea;
    letter-spacing: -0.3px;
    margin-bottom: 4px;
}
.page-sub {
    font-size: 13px;
    color: #4a5068;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    color: #4a5068;
    text-align: center;
}
.empty-icon { font-size: 36px; margin-bottom: 16px; opacity: 0.6; }
.empty-title { font-size: 15px; font-weight: 500; color: #6b6f85; margin-bottom: 6px; }
.empty-sub { font-size: 13px; line-height: 1.6; max-width: 320px; }

.user-msg {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 12px;
}
.user-bubble {
    background: #1a2a4a;
    border: 1px solid #1e3260;
    border-radius: 14px 14px 3px 14px;
    padding: 11px 16px;
    max-width: 65%;
    font-size: 14px;
    color: #c8d4f0;
    line-height: 1.6;
    word-wrap: break-word;
}

.bot-msg {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    align-items: flex-start;
}
.bot-avatar {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #00e5a0, #0066ff);
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
    flex-shrink: 0;
    margin-top: 2px;
}
.bot-bubble {
    background: #161820;
    border: 1px solid #1e2130;
    border-radius: 3px 14px 14px 14px;
    padding: 12px 16px;
    max-width: 72%;
    font-size: 14px;
    color: #c8cad6;
    line-height: 1.7;
    word-wrap: break-word;
}
.sources-row {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.source-chip {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    background: rgba(0,229,160,0.06);
    border: 1px solid rgba(0,229,160,0.18);
    color: #00e5a0;
    border-radius: 20px;
    padding: 3px 10px;
    letter-spacing: 0.3px;
}

.input-wrap {
    position: sticky;
    bottom: 0;
    background: #0f1117;
    padding: 1.2rem 0 0.5rem 0;
    border-top: 1px solid #1e2130;
    margin-top: 1rem;
}

.stTextInput > div > div > input {
    background: #161820 !important;
    border: 1px solid #1e2130 !important;
    color: #e2e4ea !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #00e5a0 !important;
    box-shadow: 0 0 0 3px rgba(0,229,160,0.08) !important;
}
.stTextInput > div > div > input::placeholder { color: #4a5068 !important; }

.stButton > button {
    background: linear-gradient(135deg, #00e5a0, #00b87a) !important;
    color: #0a0f0a !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    height: 46px !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

.clear-btn button {
    background: transparent !important;
    border: 1px solid #1e2130 !important;
    color: #6b6f85 !important;
    font-size: 12px !important;
    height: 34px !important;
    border-radius: 8px !important;
}
.clear-btn button:hover {
    border-color: #ff4d6a !important;
    color: #ff4d6a !important;
}

.stSpinner > div { border-top-color: #00e5a0 !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2d3e; border-radius: 4px; }

hr { border-color: #1e2130 !important; margin: 1rem 0 !important; }

.stSuccess { background: rgba(0,229,160,0.08) !important; border: 1px solid rgba(0,229,160,0.2) !important; color: #00e5a0 !important; border-radius: 8px !important; }
.stError   { background: rgba(255,77,106,0.08) !important; border: 1px solid rgba(255,77,106,0.2) !important; color: #ff4d6a !important; border-radius: 8px !important; }
.stWarning { background: rgba(255,160,0,0.08) !important; border: 1px solid rgba(255,160,0,0.2) !important; color: #ffa000 !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "doc_loaded" not in st.session_state:
    st.session_state.doc_loaded = False

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">◈</div>
        <div>
            <div class="logo-text">DocMind</div>
            <div class="logo-sub">RAG Engine</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">📄 Upload Document</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        if st.button("Process Document →", use_container_width=True):
            with st.spinner("Processing PDF..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    resp = requests.post(
                        f"{API_BASE}/ingest/",
                        files=files,
                        timeout=120
                    )
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.uploaded_file_name = uploaded_file.name
                        st.session_state.doc_loaded = True
                        st.success(f"✅ {data.get('message', 'Document processed!')}")
                    else:
                        error_msg = resp.json().get('detail', 'Unknown error')
                        st.error(f"❌ Failed: {error_msg}")
                        
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timeout. File might be too large.")
                except requests.exceptions.ConnectionError:
                    st.error(f"❌ Cannot connect to backend.\n\n**URL:** `{API_BASE}`\n\nMake sure FastAPI is running!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    if st.session_state.doc_loaded and st.session_state.uploaded_file_name:
        st.markdown(f"""
        <div class="file-badge">
            <span>📄</span>
            <span class="file-badge-name">{st.session_state.uploaded_file_name}</span>
        </div>
        """, unsafe_allow_html=True)

    # Backend Status
    try:
        r = requests.get(f"{API_BASE}/docs", timeout=2)
        connected = True
        status_msg = "✅ Backend connected"
        dot_class = "dot-green"
    except:
        connected = False
        status_msg = "❌ Backend offline"
        dot_class = "dot-red"

    st.markdown(f"""
    <div class="status-row">
        <div class="{dot_class}"></div>
        <span>{status_msg}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.doc_loaded = False
            st.session_state.uploaded_file_name = None
            st.rerun()
    with col2:
        if st.button("⟳ Refresh", use_container_width=True):
            st.rerun()

    st.markdown("---")
    st.caption(f"🔗 Backend: `{API_BASE}`")
    st.caption("💡 Upload a PDF, then ask questions about it.")

# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">💬 Document Chat</div>
    <div class="page-sub">Ask anything about your uploaded documents</div>
</div>
""", unsafe_allow_html=True)

# Chat History
if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">◈</div>
        <div class="empty-title">No conversation yet</div>
        <div class="empty-sub">Upload a PDF from the sidebar, then ask questions about its content.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-msg">
                <div class="user-bubble">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            sources_html = ""
            if msg.get("sources"):
                unique_sources = list(set(msg["sources"]))
                chips = "".join([f'<span class="source-chip">📄 {s}</span>' for s in unique_sources])
                sources_html = f'<div class="sources-row">{chips}</div>'
            
            answer = msg["content"].replace("\n", "<br>")
            st.markdown(f"""
            <div class="bot-msg">
                <div class="bot-avatar">◈</div>
                <div class="bot-bubble">{answer}{sources_html}</div>
            </div>
            """, unsafe_allow_html=True)

# Input Section
st.markdown('<div class="input-wrap">', unsafe_allow_html=True)
col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.text_input(
        "Question",
        placeholder="Ask a question about your document...",
        label_visibility="collapsed",
        key="user_input"
    )

with col2:
    send = st.button("Send", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle Send
if send and user_input.strip():
    if not st.session_state.doc_loaded:
        st.warning("⚠️ Please upload and process a document first.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        
        with st.spinner("Searching for answer..."):
            try:
                resp = requests.get(
                    f"{API_BASE}/ask/",
                    params={"question": user_input.strip()},
                    timeout=30
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data.get("answer", "No answer found in documents."),
                        "sources": data.get("sources", [])
                    })
                else:
                    error_detail = resp.json().get('detail', 'Unknown error')
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"❌ Error: {error_detail}",
                        "sources": []
                    })
            
            except requests.exceptions.Timeout:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⏱️ Request timeout. Please try again.",
                    "sources": []
                })
            
            except requests.exceptions.ConnectionError:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Cannot connect to backend.\n\n**URL:** `{API_BASE}`\n\nMake sure FastAPI server is running: `uvicorn main:app --reload`",
                    "sources": []
                })
            
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Error: {str(e)}",
                    "sources": []
                })
        
        st.rerun()
