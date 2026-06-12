import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

st.set_page_config(page_title="Forensic Governance Audit", layout="wide")
st.title("🛡️ Forensic Governance Agent: Site-Specific Audit")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- TARGETED SEARCH ENGINE ---
def search_management_info(ticker):
    """Targets ONLY Screener.in and Yahoo Finance for board data."""
    # We use OR to search both sites simultaneously
    query = f"(site:screener.in OR site:finance.yahoo.com) {ticker} board of directors management team"
    try:
        results = DDGS().text(query, max_results=5)
        # Combine the body text from the search results
        context = "\n".join([r.get('body', '') for r in results])
        return context if context else "NO_DATA_FOUND"
    except Exception as e:
        return f"Search Error: {str(e)}"

# --- AUDIT ENGINE ---
def run_management_audit(context, ticker, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    
    prompt = f"""
    You are a forensic auditor. Your goal is to extract the Board of Directors/Management team from the provided financial search data.
    
    SEARCH DATA:
    {context[:150000]}
    
    TASK: Populate the table below. 
    INSTRUCTIONS:
    1. Extract Names and Designations.
    2. If info (Age/Political/Fraud) is missing, write "N/A".
    3. If you find NO management names, explicitly write "NO MANAGEMENT DATA FOUND IN SEARCH".
    
    TABLE:
    | Name | Designation | Relevant Info | Political | Fraud/Litigation |
    | --- | --- | --- | --- | --- |
    
    Forensic Risk Verdict:
    Summarize any governance concerns in 2 sentences.
    """
    return model.generate_content(prompt).text

# --- UI ---
ticker = st.text_input("Enter Ticker (e.g., RELIANCE.NS):")
debug_mode = st.toggle("Show Raw Search Results")

if st.button("Run Audit"):
    if not ticker:
        st.error("Please enter a ticker.")
    else:
        with st.spinner("Searching targeted financial databases..."):
            context = search_management_info(ticker)
            
            if debug_mode:
                st.subheader("🔍 Raw Search Data:")
                st.write(context)
            
            if "NO_DATA_FOUND" in context or len(context) < 50:
                st.error("No management data found on Screener or Yahoo Finance. Try a different Ticker format (e.g., RELIANCE.NS).")
            else:
                result = run_management_audit(context, ticker, API_KEY)
                st.markdown(result)
