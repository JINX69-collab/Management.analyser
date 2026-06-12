import streamlit as st
import google.generativeai as genai
import pdfplumber
from duckduckgo_search import DDGS

st.set_page_config(page_title="Forensic Governance Audit", layout="wide")
st.title("🛡️ Forensic Governance Agent")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Secrets not found.")
    st.stop()

def get_context(ticker, uploaded_file):
    """Detects if PDF is image-based and switches to Web Search if necessary."""
    text = ""
    if uploaded_file:
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages[:5] if page.extract_text()])
        
        # If less than 100 characters, it's almost certainly an image-scan
        if len(text) < 100:
            st.warning("⚠️ PDF is an image-scan (No text found). Switching to Web Search automatically...")
            return None
        return text
    return None

def run_audit(context, ticker, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    
    # If context is empty (No PDF or Scanned PDF), Search the Web
    if not context:
        st.info(f"Searching web for {ticker} management details...")
        context = str(DDGS().text(f"{ticker} company annual report board of directors management details management team", max_results=8))

    prompt = f"""
    You are a Lead Forensic Auditor.
    
    DATA SOURCE: {context[:150000]}
    
    TASK: Populate this table regarding the company's management:
    | Name of Management | Designation | Relevant Info (Age/Qual/Tenure) | Political Connections | Involvement in Fraud |
    
    If the source does not mention a specific field, write "NOT DISCLOSED". 
    Do not skip names.
    
    FORENSIC VERDICT: 
    After the table, provide a short summary of any governance concerns found in the data (e.g. lack of independence, family-run structure, litigation history).
    """
    return model.generate_content(prompt).text

# --- UI ---
ticker = st.sidebar.text_input("Enter Ticker (e.g., RELIANCE.NS):")
uploaded_file = st.sidebar.file_uploader("Upload Annual Report", type=["pdf"])

if st.sidebar.button("Run Audit"):
    if not ticker: st.error("Need Ticker.")
    else:
        context = get_context(ticker, uploaded_file)
        result = run_audit(context, ticker, API_KEY)
        st.markdown(result)
