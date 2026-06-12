import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

st.set_page_config(page_title="Forensic Governance Agent", layout="wide")
st.title("🛡️ Forensic Governance Agent: BSE Regulatory Mode")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Set GEMINI_API_KEY in Secrets.")
    st.stop()

# --- REGULATORY SEARCH ENGINE ---
def search_bse_filings(ticker):
    """
    Forces the agent to look ONLY at BSE India regulatory filings 
    where management disclosures are legally mandatory.
    """
    # This query targets the official 'Corporate Governance' reports on BSE
    query = f"site:bseindia.com {ticker} 'Corporate Governance Report' list of directors key managerial personnel"
    try:
        results = DDGS().text(query, max_results=3)
        # Combine the body text from the official announcements
        return "\n".join([r.get('body', '') for r in results])
    except Exception as e:
        return f"Regulatory Search Error: {str(e)}"

# --- FORENSIC AUDIT ENGINE ---
def run_forensic_analysis(context, ticker, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    
    prompt = f"""
    You are a Lead Forensic Auditor. Your task is to extract management data from OFFICIAL BSE REGULATORY FILINGS.
    
    CONTEXT DATA:
    {context[:150000]}
    
    TASK: Populate the table. 
    1. Extract Names, Designations, and Committee roles from the text.
    2. If information is missing (e.g. Political/Fraud), use 'N/A' (Do not write 'NOT DISCLOSED').
    3. If the data is not in the text, you MUST state "DATA NOT FOUND IN BSE FILINGS".
    
    TABLE FORMAT:
    | Name of Management | Designation | Committee/Role | Political/Conflict | Fraud/Litigation History |
    | --- | --- | --- | --- | --- |
    
    FORENSIC RISK VERDICT:
    Summarize any independence concerns or red flags (e.g., family dominance, frequent KMP turnover).
    """
    return model.generate_content(prompt).text

# --- UI ---
ticker = st.text_input("Enter Ticker (e.g., RELIANCE.NS or 500325):")
if st.button("Run Forensic Audit"):
    if not ticker:
        st.error("Please enter a ticker.")
    else:
        with st.spinner("Accessing BSE Regulatory Filings..."):
            context = search_bse_filings(ticker)
            
            if len(context) < 100:
                st.error("No governance filings found. The ticker might be incorrect, or the company hasn't filed recent disclosures on BSE.")
            else:
                result = run_forensic_analysis(context, ticker, API_KEY)
                st.markdown(result)
