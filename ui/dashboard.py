import streamlit as st
import requests
import json

# --- Configuration ---
# In production, you would load this from an environment variable
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Compliance Assistant - EU AI Act", 
    page_icon="",
    layout="wide"
)

# --- App Header ---
st.title("Compliance Assistant")
st.markdown("""
**Your AI-powered guide to the new European Artificial Intelligence Act.** _Assess risk, identify obligations, and chat with the regulation._
""")
st.markdown("---")

# --- SIDEBAR: The Dynamic Auditor ---
with st.sidebar:
    st.header("🛡️ Compliance Auditor")
    
    # 1. Fetch the Questionnaire dynamically from the Backend
    questions = []
    try:
        response = requests.get(f"{API_URL}/questionnaire")
        if response.status_code == 200:
            questions = response.json()
            st.success("✅ Module Loaded: EU AI Act")
        else:
            st.error("⚠️ Could not load regulation module.")
    except Exception as e:
        st.error(f"🔴 Backend Offline: {e}")

    # 2. Build the Form dynamically
    with st.form("audit_form"):
        st.info("Describe your AI system to get a risk assessment.")
        
        user_inputs = {}
        
        # A. Static Fields (Always needed)
        user_inputs["description"] = st.text_area(
            "System Description", 
            "E.g., An AI system that evaluates loan applications..."
        )

        # B. Dynamic Fields (From the Module)
        for q in questions:
            if q["type"] == "select":
                user_inputs[q["id"]] = st.selectbox(q["text"], q["options"])
            elif q["type"] == "boolean":
                user_inputs[q["id"]] = st.checkbox(q["text"])
            elif q["type"] == "text":
                user_inputs[q["id"]] = st.text_input(q["text"])
        
        submitted = st.form_submit_button("Run Compliance Scan")
        
        # 3. Handle Submission
        if submitted:
            with st.spinner("Consulting the EU AI Act..."):
                try:
                    # Send generic inputs to the generic scan endpoint
                    payload = {"inputs": user_inputs}
                    scan_response = requests.post(f"{API_URL}/scan", json=payload)
                    
                    if scan_response.status_code == 200:
                        report = scan_response.json()
                        
                        # --- Display Results ---
                        st.divider()
                        st.subheader(f"Risk Level: {report['risk_level']}")
                        
                        # Visual Indicator
                        if report['risk_level'] == "High":
                            st.error("🚨 HIGH RISK SYSTEM")
                        elif report['risk_level'] == "Limited":
                            st.warning("⚠️ LIMITED RISK")
                        else:
                            st.success("✅ MINIMAL RISK")

                        st.metric("Compliance Confidence", f"{report['compliance_score']}%")
                        
                        # Key Obligations
                        st.markdown("### 📋 Key Obligations")
                        if report['key_obligations']:
                            for ob in report['key_obligations']:
                                st.info(ob)
                        else:
                            st.write("No specific obligations found for this category.")

                        # Detailed Checks (Expandable)
                        with st.expander("🔍 View Detailed Analysis"):
                            for check in report['checks']:
                                icon = "✅" if check['status'] == "PASS" else "❌" if check['status'] == "FAIL" else "⚠️"
                                st.markdown(f"**{icon} {check['name']}**")
                                st.caption(check['reason'])
                                st.caption(f"Ref: {', '.join(check['reference_articles'])}")
                                st.divider()
                                
                    else:
                        st.error(f"Scan Failed: {scan_response.text}")
                        
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# --- MAIN AREA: The Chatbot ---
st.header("💬 Regulatory Chat")
st.caption("Ask questions about the EU AI Act (e.g., 'What are the rules for biometric data?')")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Type your question here..."):
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get AI Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("Analyzing regulation..."):
                api_response = requests.post(f"{API_URL}/chat", json={"message": prompt})
                
                if api_response.status_code == 200:
                    data = api_response.json()
                    answer = data["response"]
                    sources = data["sources"]
                    
                    # A. Show the Answer
                    message_placeholder.markdown(answer)
                    
                    # B. Show the Sources (The "Click to View" feature)
                    if sources:
                        with st.expander("📚 View Regulatory Sources"):
                            for idx, source in enumerate(sources):
                                st.markdown(f"**Source {idx+1} (Page {source['page']})**")
                                st.caption(f"Relevance Score: {source['score']:.2f}")
                                # Use blockquote for the actual legal text
                                st.markdown(f"> {source['text'][:500]}...") # Truncate long text
                                st.divider()
                    
                    # Add to history 
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                else:
                    message_placeholder.error("System Error: Could not retrieve answer.")
        except Exception as e:
            message_placeholder.error(f"Connection Error: {e}")