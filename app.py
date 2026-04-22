import streamlit as st
import requests
import time

# --- Page Configuration ---
st.set_page_config(page_title="Amazon Virtual Assistant", page_icon="🤖", layout="centered")

# --- Custom Styling (Blue/White Theme) ---
st.markdown("""
    <style>
    /* Background and Main Container */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* User Message Bubble (Light Blue) */
    .user-bubble {
        background-color: #E3F2FD;
        color: #0D47A1;
        padding: 15px;
        border-radius: 20px 20px 0px 20px;
        margin-bottom: 10px;
        display: inline-block;
        float: right;
        max-width: 80%;
        border: 1px solid #BBDEFB;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Assistant Message Bubble (Dark Blue) */
    .assistant-bubble {
        background-color: #0D47A1;
        color: #FFFFFF;
        padding: 15px;
        border-radius: 20px 20px 20px 0px;
        margin-bottom: 10px;
        display: inline-block;
        float: left;
        max-width: 80%;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Sources Styling */
    .source-text {
        font-size: 0.8rem;
        color: #607D8B;
        margin-top: 5px;
        clear: both;
    }

    /* Input Field Styling */
    .stTextInput input {
        border-radius: 10px;
        border: 1px solid #0D47A1;
    }
    
    .clearfix { clear: both; }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🤖 Amazon AI Assistant")
st.markdown("---")

# --- Session State for Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-bubble">{message["content"]}</div><div class="clearfix"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-bubble">{message["content"]}</div><div class="clearfix"></div>', unsafe_allow_html=True)
        if "sources" in message:
            sources_html = f'<div class="source-text"><b>Sources:</b> {", ".join(message["sources"])}</div>'
            st.markdown(sources_html, unsafe_allow_html=True)

# --- Chat Input ---
if prompt := st.chat_input("Apna sawal yahan likhein..."):
    # User message display
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-bubble">{prompt}</div><div class="clearfix"></div>', unsafe_allow_html=True)

    # API Call to FastAPI Backend
    with st.spinner("Assistant soch raha hai..."):
        try:
            # Backend URL (Change if deployed on different host)
            backend_url = "http://localhost:8000/ask/"
            params = {"question": prompt}
            
            response = requests.get(backend_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "Maaf kijiyega, jawab nahi mil saka.")
                sources = data.get("sources", [])
                
                # Update Session State
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "sources": sources
                })
                
                # Display Assistant Response
                st.markdown(f'<div class="assistant-bubble">{answer}</div><div class="clearfix"></div>', unsafe_allow_html=True)
                if sources:
                    st.markdown(f'<div class="source-text"><b>Sources:</b> {", ".join(sources)}</div>', unsafe_allow_html=True)
            else:
                st.error("Backend se rabta nahi ho saka.")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

# --- Sidebar Info ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/144/amazon.png", width=100)
    st.header("About")
    st.info("Ye assistant Amazon sellers aur buyers ki madad ke liye banaya gaya hai. Ye MongoDB Atlas aur Groq LLM ka istemal karta hai.")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
