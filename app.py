import streamlit as st
import requests

# ─── Config ───────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0a0c10; color: #e8eaf0; }

    [data-testid="stSidebar"] {
        background-color: #111318;
        border-right: 1px solid #2a2d36;
    }

    .user-msg {
        background: #0d2a4a;
        border-radius: 12px 12px 2px 12px;
        padding: 12px 16px;
        margin: 8px 0;
        margin-left: 15%;
        color: #e8eaf0;
        font-size: 14px;
    }
    .bot-msg {
        background: #131a12;
        border: 1px solid #2a2d36;
        border-radius: 12px 12px 12px 2px;
        padding: 12px 16px;
        margin: 8px 0;
        margin-right: 15%;
        color: #e8eaf0;
        font-size: 14px;
    }
    .source-tag {
        display: inline-block;
        background: rgba(0,229,160,0.1);
        border: 1px solid rgba(0,229,160,0.3);
        color: #00e5a0;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 11px;
        margin: 4px 2px 0 0;
    }
    .chat-header {
        font-family: monospace;
        font-size: 22px;
        font-weight: 700;
        color: #00e5a0;
        letter-spacing: -0.5px;
    }
    .stTextInput > div > div > input {
        background-color: #1a1d24 !important;
        border: 1px solid #2a2d36 !important;
        color: #e8eaf0 !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00e5a0, #0066ff);
        color: #0a0c10;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🤖 RAG Chatbot")
    st.caption("Powered by Jina + Groq + MongoDB")
    st.divider()

    st.markdown("📦 **Data is already loaded in the cloud**")
    st.caption("You can start asking questions right away.")
    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("")
    st.caption(f"🔗 Backend: `{API_BASE}`")

# ─── Main: Chat ───────────────────────────────────────────────────────────────
st.markdown('<p class="chat-header">💬 RAG Chat</p>', unsafe_allow_html=True)
st.caption("Get instant answers from documents stored in the cloud.")
st.divider()

# ─── Chat History ─────────────────────────────────────────────────────────────
with st.container():
    if not st.session_state.messages:
        st.markdown(
            "<div style='text-align:center; color:#6b7280; padding: 60px 0; font-size:14px;'>"
            "💬 Ask any question — your data is already available in the cloud."
            "</div>",
            unsafe_allow_html=True
        )
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-msg">🧑 {msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                answer_html = msg["content"].replace("\n", "<br>")
                sources_html = ""
                if msg.get("sources"):
                    sources_html = "<div style='margin-top:10px'>" + "".join(
                        [f'<span class="source-tag">📄 {s}</span>' for s in msg["sources"]]
                    ) + "</div>"
                st.markdown(
                    f'<div class="bot-msg">🤖 {answer_html}{sources_html}</div>',
                    unsafe_allow_html=True
                )

st.divider()

# ─── Input ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        "Ask a question...",
        placeholder="e.g. What is the main topic of the document?",
        label_visibility="collapsed",
        key="user_input"
    )
with col2:
    send = st.button("Send 🚀", use_container_width=True)

# ─── Handle Send ──────────────────────────────────────────────────────────────
if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input.strip()})

    with st.spinner("Searching for an answer..."):
        try:
            resp = requests.get(
                f"{API_BASE}/ask/",
                params={"question": user_input.strip()}
            )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data.get("answer", "No answer found in the documents."),
                    "sources": data.get("sources", [])
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Error: {resp.json().get('detail', 'Unknown error occurred.')}",
                    "sources": []
                })
        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "❌ Unable to connect to the backend. Please make sure `uvicorn main:app --reload` is running.",
                "sources": []
            })

    st.rerun()
