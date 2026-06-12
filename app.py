import streamlit as st
import google.generativeai as genai
import pdfplumber
from duckduckgo_search import DDGS
import logging

# --- CONFIGURATION ---
st.set_page_config(page_title="Forensic Governance Agent", layout="wide")
st.title("🛡️ Phase 1: Management Profile & Integrity")

# --- AUTOMATIC API AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Streamlit Cloud 'Secrets'.")
    st.stop()

# --- DATA GATHERING (PDF or WEB) ---
def extract_pdf_content(pdf_file):
    if pdf_file is None: return None
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

def search_management_info(ticker):
    """Searches the web for management data and regulatory news."""
    try:
        query = f"{ticker} company board of directors management team SEBI MCA fraud litigation news"
        results = DDGS().text(query, max_results=5)
        return str(results)
    except Exception as e:
        return f"Web search failed: {e}"

# --- ANALYSIS ENGINE ---
def run_management_audit(context_data, api_key):
    genai.configure(api_key=api_key)
    # Using the confirmed working model
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    
    prompt = f"""
    You are a professional Forensic Auditor. Analyze the provided context (either PDF or Web Search Results).
    
    CONTEXT DATA: 
    {context_data}
    
    Your task:
    1. Identify all KMPs, CEO, MD, and Directors.
    2. Populate a Markdown table based strictly on the provided context.
    
    REQUIRED TABLE COLUMNS:
    | Name of Management | Designation | Relevant Info (Age/Qual/Tenure) | Political Connections | Involvement in Fraud/Litigation |
    
    INSTRUCTIONS:
    - If any data is missing for a specific person or column, write "DATA NOT DISCLOSED".
    - After the table, write a 'Forensic Risk Verdict' summarizing any red flags found in the data.
    """
    response = model.generate_content(prompt)
    return response.text

# --- UI & LOGIC ---
ticker = st.sidebar.text_input("Enter Ticker (e.g., RELIANCE.NS):")
uploaded_file = st.sidebar.file_uploader("Upload Annual Report (Optional)", type=["pdf"])

if st.sidebar.button("Run Phase 1 Audit"):
    if not ticker:
        st.error("Please provide a Ticker symbol.")
    else:
        with st.spinner("Gathering data..."):
            # Logic: PDF first, then Web
            if uploaded_file:
                context = extract_pdf_content(uploaded_file)
                st.info("Using PDF document as source...")
            else:
                context = search_management_info(ticker)
                st.info("No PDF detected. Searching live web for management data...")
            
            # This line now aligns correctly with the indentation rules
            result = run_management_audit(context, API_KEY)
            st.markdown(result)
