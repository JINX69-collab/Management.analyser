import streamlit as st
import google.generativeai as genai
import pdfplumber
from duckduckgo_search import DDGS

st.set_page_config(page_title="Forensic Governance Audit", layout="wide")
st.title("🛡️ Forensic Governance: Debug Mode")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secrets not found.")
    st.stop()

def extract_pdf_content(pdf_file):
    if not pdf_file: return ""
    with pdfplumber.open(pdf_file) as pdf:
        # Extract only the first 10 pages for the debug test
        text = "\n".join([page.extract_text() for page in pdf.pages[:10] if page.extract_text()])
        return text

def run_audit(context_data, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    
    prompt = f"""
    You are a forensic auditor. Your goal is to extract management data into a table.
    
    DATA PROVIDED:
    {context_data[:100000]}
    
    INSTRUCTIONS:
    1. Scan the text for names, roles, and governance disclosures.
    2. Populate the table below.
    3. If you do not find info, write "NOT DISCLOSED" for that specific cell. Do not say "NOT DISCLOSED" for the whole table if you found at least one name.
    
    EXAMPLE FORMAT:
    | Name of Management | Designation | Relevant Info | Political Connections | Involvement in Fraud |
    | --- | --- | --- | --- | --- |
    | John Doe | CEO | 55, MBA, 10yrs tenure | None disclosed | None |
    
    YOUR OUTPUT:
    """
    response = model.generate_content(prompt)
    return response.text

# --- UI ---
ticker = st.sidebar.text_input("Ticker:")
uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if st.sidebar.button("Run Audit"):
    if not ticker: st.error("Need Ticker.")
    else:
        context = extract_pdf_content(uploaded_file) if uploaded_file else ""
        
        # DEBUG: Show us what the AI sees
        st.subheader("🔍 Debug: Raw Text Extracted from PDF")
        st.text_area("Extracted Preview:", value=context[:2000], height=200)
        
        if not context:
            st.info("No text extracted. Using Web Search instead.")
            context = str(DDGS().text(f"{ticker} management board of directors", max_results=3))
            
        result = run_audit(context, API_KEY)
        st.markdown(result)
