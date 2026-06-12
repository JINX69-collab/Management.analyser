import streamlit as st
import google.generativeai as genai
import logging

# --- CONFIGURATION ---
st.set_page_config(page_title="Forensic Governance Agent", layout="wide")
st.title("🛡️ Forensic Governance & Valuation Agent: Setup Phase")

# --- API CONNECTION TEST ---
def verify_api_connection(api_key):
    try:
        genai.configure(api_key=api_key)
        # Check available models to solve 404 errors
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return True, models
    except Exception as e:
        return False, str(e)

# --- UI ---
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

if st.sidebar.button("Test Connection"):
    if not api_key:
        st.error("Please enter your API Key.")
    else:
        success, result = verify_api_connection(api_key)
        if success:
            st.success("Connection Successful!")
            st.write("Available Models:", result)
        else:
            st.error(f"Connection Failed: {result}")
