import streamlit as st
from PIL import Image
import io
import logging
import base64
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Docify | AI Health Assistant",
    page_icon="🩺",
    layout="wide",
)

# Custom CSS Integration
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css('style.css')

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Silent API Key Loading (Completely hidden from UI)
api_key = os.getenv("OPENAI_API_KEY")
client = None
if api_key:
    try:
        client = openai.OpenAI(api_key=api_key)
    except Exception as e:
        logging.error(f"Failed to initialize OpenAI client: {e}")

# Sidebar Navigation
with st.sidebar:
    st.markdown('<div style="text-align: center; padding: 1rem 0;"><h2 style="margin:0;">Dashboard</h2></div>', unsafe_allow_html=True)
    page = st.selectbox("Navigation", ["Home", "History", "About"], index=0)
    
    st.divider()
    st.caption("Docify v2.0 - Encrypted Session")

# Main Content Logic
if page == "Home":
    # Hero Section
    st.markdown('''
        <div class="docify-header">
            <h1 class="docify-logo">Docify</h1>
            <p class="docify-tagline">Advanced AI-Powered Healthcare Consultancy</p>
        </div>
    ''', unsafe_allow_html=True)
    
    if not client:
        st.error("🔑 API Key Missing: Please ensure OPENAI_API_KEY is set in your .env file.")
        st.stop()

    # Model Selection Area
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown("### Settings")
        select_model = st.radio("Mode", ["Consultancy", "Image Analysis"])
        st.info("💡 Image Analysis uses GPT-4o Vision.")

    with col2:
        # Chat Interface Container
        chat_container = st.container()
        
        # Image Upload (Conditional)
        image_bytes = None
        if select_model == "Image Analysis":
            st.markdown("### Upload Health Visuals")
            uploaded_file = st.file_uploader("Upload Medical Image/Report", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            if uploaded_file:
                image_bytes = uploaded_file.read()
                st.image(image_bytes, caption="Uploaded for analysis", use_column_width=True)
            
            cam_picture = st.camera_input("Quick Scan")
            if cam_picture:
                image_bytes = cam_picture.getvalue()

        # Render Chat History
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

    # Utilities
    def encode_image(data):
        return base64.b64encode(data).decode('utf-8')

    # Chat Input (Bottom)
    if chat_message := st.chat_input("Describe your symptoms or health query..."):
        with col2:
            st.chat_message("user").markdown(chat_message)
            st.session_state.messages.append({"role": "user", "content": chat_message})
            
            res_area = st.chat_message("assistant").empty()
            
            try:
                if select_model == "Image Analysis" and image_bytes:
                    b64_img = encode_image(image_bytes)
                    payload = [
                        {"role": "user", "content": [
                            {"type": "text", "text": chat_message},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                        ]}
                    ]
                    stream = client.chat.completions.create(model="gpt-4o", messages=payload, stream=True)
                else:
                    stream = client.chat.completions.create(model="gpt-4o", messages=st.session_state.messages, stream=True)

                full_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        res_area.markdown(full_response + "▌")
                res_area.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

elif page == "History":
    st.markdown('<div class="docify-header"><h1 class="docify-logo">Session History</h1></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        if not st.session_state.messages:
            st.info("No logs found for this session.")
        else:
            if st.button("Clear History"):
                st.session_state.messages = []
                st.rerun()
                
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(f"**{msg['role'].title()}**")
                    st.markdown(msg["content"])
                    st.caption("---")

elif page == "About":
    st.markdown('<div class="docify-header"><h1 class="docify-logo">About Docify</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### Intelligent Health Bridge
        Docify leverages OpenAI's GPT-4o engine to provide instant, clear, and actionable health insights. 
        Whether you're describing symptoms or uploading a medical visual, Docify analyzes the data to help you understand your situation better.
        
        #### Core Capabilities:
        - **Symptom Analysis**: Get clarity on common health issues.
        - **Vision AI**: Analysis of medical images and reports.
        - **Privacy First**: Secure session-based history and silent key loading.
        
        ---
        *⚠️ **Disclaimer**: This tool is for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.*
        """)
