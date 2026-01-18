import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Compliance Assistant", 
    page_icon="📋",
    layout="wide"
)

st.title("📋 Compliance Assistant")
st.markdown("""
**Your AI-powered guide to the EU Artificial Intelligence Act.** _Answers are grounded in the official legal text._
""")
st.divider()

# --- CHAT HISTORY (The Permanent View) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Render Sources from History
        if "sources" in message:
            with st.expander("📚 View Regulatory Sources"):
                for idx, source in enumerate(message["sources"]):
                    st.markdown(f"**Source {idx+1}**")
                    st.caption(f"Relevance: {source['score']:.2f}")
                    st.markdown(f"> *{source['text'][:400]}...*")
                    st.divider()


if prompt := st.chat_input("Ask questions about the EU AI Act (e.g., 'What are the rules for biometric data?')"):
    
    # 1. Add User Message to State
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Consulting regulation..."):
            try:
                payload = {"message": prompt}
                api_response = requests.post(f"{API_URL}/chat", json=payload)
                
                if api_response.status_code == 200:
                    data = api_response.json()
                    answer = data["response"]
                    sources = data.get("sources", [])
                    
                    # 3. Save directly to State
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                    
                    # 4. FORCE RERUN (The Fix)
                    # This makes the script restart immediately so the message 
                    # is rendered by the main history loop above.
                    st.rerun()
                    
                else:
                    st.error("System Error: Could not retrieve answer.")
            except Exception as e:
                st.error(f"Connection Error: {e}")