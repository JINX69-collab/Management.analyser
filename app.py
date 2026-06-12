import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

st.set_page_config(page_title="Forensic Governance Agent", layout="wide")
st.title("🛡️ Forensic Governance Agent: Management Audit")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- SEARCH ENGINE ---
def search_management_info(ticker):
    """Targets specific, high-quality financial websites."""
    query = f"site:moneycontrol.com OR site:screener.in {ticker} Board of Directors management team"
    try:
        results = DDGS().text(query, max_results=5)
        return "\n".join([r['body'] for r in results])
    except:
        return ""

# --- AUDIT ENGINE ---
def run_management_audit(context, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    
    prompt = f"""
    You are a professional Forensic Auditor. Extract the management team from the provided search data.
    
    SEARCH DATA:
    {context[:100000]}
    
    INSTRUCTIONS:
    1. Create a table of the Board of Directors/Key Management.
    2. If a value is missing, use "N/A" (DO NOT write 'NOT DISCLOSED').
    3. If the search data is insufficient to find names, write "NO DATA FOUND IN SEARCH".
    
    REQUIRED FORMAT:
    | Name | Designation | Info | Political | Fraud/Litigation |
    | --- | --- | --- | --- | --- |
    | [Name] | [Role] | [Age/Tenure] | [None/Details] | [None/Details] |
    
    Provide the table, then a 3-sentence Forensic Risk Verdict.
    """
    return model.generate_content(prompt).text

# --- UI ---
ticker = st.text_input("Enter Ticker (e.g., RELIANCE.NS):")
debug_mode = st.toggle("Enable Debug Mode (See Search Results)")

if st.button("Run Audit"):
    if not ticker:
        st.error("Please enter a ticker.")
    else:
        with st.spinner("Fetching data..."):
            context = search_management_info(ticker)
            
            if debug_mode:
                st.subheader("🔍 Raw Search Data Received:")
                st.write(context)
            
            result = run_management_audit(context, API_KEY)
            st.markdown(result)
