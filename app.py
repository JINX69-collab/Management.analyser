import streamlit as st
import google.generativeai as genai
import pdfplumber
from duckduckgo_search import DDGS
import logging

# --- CONFIGURATION ---
st.set_page_config(page_title="Forensic Governance Agent", layout="wide")
st.title("🛡️ Forensic Governance & Valuation Agent")

# --- AUTOMATIC API AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("API Key missing! Please set GEMINI_API_KEY in Streamlit Cloud 'Secrets'.")
    st.stop()

# --- DATA GATHERING (PDF or WEB) ---
def extract_pdf_content(pdf_file):
    if pdf_file is None: return None
    try:
        with pdfplumber.open(pdf_file) as pdf:
            # Extract text from all pages
            return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    except Exception as e:
        return f"Error reading PDF: {e}"

def search_management_info(ticker):
    """Searches the web for management data."""
    try:
        query = f"{ticker} company board of directors management team SEBI MCA fraud litigation news"
        results = DDGS().text(query, max_results=5)
        return str(results)
    except Exception as e:
        return f"Web search failed: {e}"

# --- ANALYSIS ENGINE ---
def run_management_audit(context_data, api_key):
    genai.configure(api_key=api_key)
    # Using the verified model
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    
    # We now instruct the AI to be a "Section Auditor" to fix the "NOT DISCLOSED" issue
    prompt = f"""
    You are a Lead Forensic Auditor. Your goal is to extract Management data from the following Annual Report content.
    
    CRITICAL INSTRUCTION: 
    1. Search specifically for sections titled: 'Corporate Governance Report', 'Directors' Report', 'Board of Directors', or 'Key Managerial Personnel'.
    2. Extract management details ONLY from those sections. 
    3. If you do not see these sections, state "SECTION NOT FOUND, CHECKING GENERAL TEXT" and proceed to scan the rest.
    
    CONTEXT DATA: 
    {context_data[:300000]} 
    
    TASK: Populate this table:
    | Name of Management | Designation | Relevant Info (Age/Qual/Tenure) | Political Connections | Involvement in Fraud/Litigation |
    
    If any cell remains empty because the report does not mention it, explicitly write "NOT DISCLOSED". 
    Do not skip people. If a name is mentioned in the Board list, it must be in the table.
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
        with st.spinner("Gathering and analyzing data..."):
            if uploaded_file:
                context = extract_pdf_content(uploaded_file)
                st.info("Reading PDF document...")
            else:
                context = search_management_info(ticker)
                st.info("Searching live web for management data...")
            
            # This is the line that caused the indentation error previously
            # It is now correctly indented inside the 'with' block
            result = run_management_audit(context, API_KEY)
            st.markdown(result)
