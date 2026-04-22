import os
import requests
import streamlit as st
from pymongo import MongoClient
from groq import Groq
from dotenv import load_dotenv

# ─── Load Environment Variables ───────────────────────────────────────────────
load_dotenv()

MONGO_URI    = os.getenv("MONGO_URI")
JINA_API_KEY = os.getenv("JINA_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .stApp {
        background-color: #080b12;
        color: #dce3f0;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #1e2736;
    }
    /* Header */
    .app-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 26px;
        font-weight: 600;
        background: linear-gradient(90deg, #00e5a0, #00aaff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
    }
    .app-subtitle {
        font-size: 12px;
        color: #4a5568;
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    /* Chat bubbles */
    .user-msg {
        background: linear-gradient(135deg, #0d2a4a, #0a1f3a);
        border: 1px solid #1a3a5c;
        border-radius: 16px 16px 4px 16px;
        padding: 14px 18px;
        margin: 10px 0;
        margin-left: 20%;
        color: #dce3f0;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 2px 12px rgba(0,170,255,0.08);
    }
    .bot-msg {
        background: linear-gradient(135deg, #0e1a0e, #111a11);
        border: 1px solid #1e2e1e;
        border-radius: 16px 16px 16px 4px;
        padding: 14px 18px;
        margin: 10px 0;
        margin-right: 20%;
        color: #dce3f0;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 2px 12px rgba(0,229,160,0.06);
    }
    .source-tag {
        display: inline-block;
        background: rgba(0,229,160,0.08);
        border: 1px solid rgba(0,229,160,0.25);
        color: #00e5a0;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 11px;
        font-family: 'IBM Plex Mono', monospace;
        margin: 6px 3px 0 0;
    }
    .msg-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .user-label { color: #00aaff; }
    .bot-label  { color: #00e5a0; }

    /* Empty state */
    .empty-state {
        text-align: center;
        color: #2a3548;
        padding: 80px 0;
        font-size: 14px;
        font-family: 'IBM Plex Mono', monospace;
    }
    .empty-icon { font-size: 48px; margin-bottom: 16px; }

    /* Input */
    .stTextInput > div > div > input {
        background-color: #0d1117 !important;
        border: 1px solid #1e2736 !important;
        border-radius: 10px !important;
        color: #dce3f0 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00e5a0 !important;
        box-shadow: 0 0 0 2px rgba(0,229,160,0.1) !important;
    }
    .stTextInput > div > div > input::placeholder { color: #2a3548 !important; }

    /* Button */
    .stButton > button {
        background: linear-gradient(135deg, #00e5a0, #00aaff) !important;
        color: #080b12 !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 14px !important;
        transition: opacity 0.2s, transform 0.1s !important;
    }
    .stButton > button:hover {
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
    }
    /* Divider */
    hr { border-color: #1e2736 !important; }

    /* Sidebar caption */
    .stSidebar .stCaption { color: #4a5568 !important; }

    /* Spinner */
    .stSpinner > div { border-top-color: #00e5a0 !important; }

    /* Status badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0,229,160,0.08);
        border: 1px solid rgba(0,229,160,0.2);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 11px;
        font-family: 'IBM Plex Mono', monospace;
        color: #00e5a0;
        margin-top: 8px;
    }
    .status-dot {
        width: 6px; height: 6px;
        border-radius: 50%;
        background: #00e5a0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
</style>
""", unsafe_allow_html=True)


# ─── Core RAG Functions ────────────────────────────────────────────────────────

@st.cache_resource
def get_mongo_collection():
    """Initialize MongoDB connection (cached)."""
    client = MongoClient(MONGO_URI)
    return client["RAG_DB"]["vector_store"]

def get_query_embedding(query_text: str) -> list:
    """Generate query embedding using Jina AI."""
    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "jina-embeddings-v5-text-small",
        "task": "retrieval.query",
        "dimensions": 512,
        "input": [query_text]
    }
    response = requests.post("https://api.jina.ai/v1/embeddings", headers=headers, json=payload)
    return response.json()["data"][0]["embedding"]

def hybrid_search(query_text: str, n_results: int = 4) -> list:
    """
    Perform hybrid search: keyword + vector search, then rerank with Jina.
    """
    collection = get_mongo_collection()
    query_vector = get_query_embedding(query_text)

    # Keyword Search
    text_pipeline = {
        "$search": {
            "index": "vector_index",
            "text": {"query": query_text, "path": "content"}
        }
    }
    # Vector Search
    vector_pipeline = {
        "$search": {
            "index": "vector_index",
            "knnBeta": {"vector": query_vector, "path": "embedding", "k": 20}
        }
    }

    try:
        text_results   = list(collection.aggregate([text_pipeline,   {"$limit": 15}]))
        vector_results = list(collection.aggregate([vector_pipeline, {"$limit": 15}]))

        # Merge and deduplicate
        merged = {str(r["_id"]): r for r in (text_results + vector_results)}.values()
        results_list = list(merged)

        if not results_list:
            return []

        # Rerank with Jina
        docs = [r["content"] for r in results_list]
        headers = {"Authorization": f"Bearer {JINA_API_KEY}"}
        rerank_payload = {
            "model": "jina-reranker-v2-base-multilingual",
            "query": query_text,
            "documents": docs,
            "top_n": n_results
        }
        resp = requests.post("https://api.jina.ai/v1/rerank", headers=headers, json=rerank_payload)
        if resp.status_code == 200:
            indices = [item["index"] for item in resp.json()["results"]]
            return [results_list[i] for i in indices]

        return results_list[:n_results]

    except Exception as e:
        st.error(f"Search error: {e}")
        return []

def generate_answer(query: str, context_chunks: list) -> str:
    """Generate answer using Groq LLM based on retrieved context."""
    if not context_chunks:
        return "No relevant information was found in the documents."

    formatted_context = "\n\n".join([
        f"Source: {c['metadata']['source']}\n{c['content']}"
        for c in context_chunks
    ])

    system_prompt = """You are a professional AI Assistant. Answer the user's question strictly based on the provided context.

Guidelines:
1. Only use information from the provided context.
2. If the answer is not in the context, clearly state that the information is not available in the documents.
3. Be precise and preserve specific numbers, versions, or dates mentioned in the text.
4. Maintain a professional and helpful tone."""

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{formatted_context}\n\nQuestion: {query}"}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

def ask(question: str) -> dict:
    """Full RAG pipeline: search → rerank → generate."""
    results = hybrid_search(question, n_results=4)
    if not results:
        return {
            "answer": "No relevant information was found in the documents.",
            "sources": []
        }
    answer  = generate_answer(question, results)
    sources = list(set([r["metadata"]["source"] for r in results]))
    return {"answer": answer, "sources": sources}


# ─── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="app-title">RAG Chatbot</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Powered by Jina · Groq · MongoDB</p>', unsafe_allow_html=True)
    st.markdown(
        '<div class="status-badge"><div class="status-dot"></div>Connected to Cloud</div>',
        unsafe_allow_html=True
    )
    st.divider()

    st.markdown("**📦 Knowledge Base**")
    st.caption("Documents are pre-loaded in MongoDB Atlas. Ask any question to retrieve answers directly from the stored data.")
    st.divider()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("")
    st.caption("Model: llama-3.3-70b-versatile")
    st.caption("Embeddings: jina-embeddings-v5-text-small")
    st.caption("Reranker: jina-reranker-v2-base-multilingual")


# ─── Main Chat Area ────────────────────────────────────────────────────────────
st.markdown('<p class="app-title">💬 RAG Chat</p>', unsafe_allow_html=True)
st.caption("Ask questions — answers are retrieved from your cloud-stored documents.")
st.divider()

# Chat history display
with st.container():
    if not st.session_state.messages:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <div>Your knowledge base is ready.</div>
                <div style="margin-top:8px; font-size:12px; color:#1e2736;">
                    Ask any question to get started.
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                    <div class="user-msg">
                        <div class="msg-label user-label">You</div>
                        {msg["content"]}
                    </div>
                """, unsafe_allow_html=True)
            else:
                answer_html  = msg["content"].replace("\n", "<br>")
                sources_html = ""
                if msg.get("sources"):
                    sources_html = "<div style='margin-top:12px'>" + "".join(
                        [f'<span class="source-tag">📄 {s}</span>' for s in msg["sources"]]
                    ) + "</div>"
                st.markdown(f"""
                    <div class="bot-msg">
                        <div class="msg-label bot-label">Assistant</div>
                        {answer_html}
                        {sources_html}
                    </div>
                """, unsafe_allow_html=True)

st.divider()

# ─── Input Area ───────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        label="Question",
        placeholder="e.g. What is the main topic of the document?",
        label_visibility="collapsed",
        key="user_input"
    )
with col2:
    send = st.button("Send 🚀", use_container_width=True)

# ─── Handle Send ──────────────────────────────────────────────────────────────
if send and user_input.strip():
    st.session_state.messages.append({
        "role": "user",
        "content": user_input.strip()
    })

    with st.spinner("Searching knowledge base..."):
        try:
            result = ask(user_input.strip())
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"]
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ An error occurred: {str(e)}",
                "sources": []
            })

    st.rerun()
