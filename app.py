import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Forensic Governance Agent", layout="wide")
st.title("🛡️ Forensic Governance Agent: Native Google Grounding")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- CORE AUDIT ENGINE ---
def run_native_search_audit(ticker):
    # Using gemini-2.0-flash or gemini-2.5-flash which perfectly support native web grounding
    # We pass tools="google_search" to give it direct, unblockable access to the live internet
    try:
        model = genai.GenerativeModel(
            model_name="models/gemini-2.0-flash",
            tools="google_search"
        )
        
        prompt = f"""
        Perform a professional forensic governance audit for the ticker/company: {ticker}.
        Use your live Google Search tool to find their official Board of Directors and Key Managerial Personnel (KMP) list.
        
        Look across high-quality financial platforms (Screener.in, Moneycontrol, Yahoo Finance, or the official Corporate website).
        
        TASK:
        Populate the exact table format below. If information for a cell cannot be found anywhere, use "N/A". 
        Do not output an empty table. Find at least the primary executive directors (CEO, MD, Chairman).
        
        REQUIRED FORMAT:
        | Name of Management | Designation | Relevant Info (Age/Tenure/Qual) | Political Connections | Involvement in Fraud/Litigation |
        | --- | --- | --- | --- | --- |
        
        After the table, provide a 'Forensic Risk Verdict' summarizing any corporate governance flags.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Execution Error: {str(e)}"

# --- UI ---
ticker_input = st.text_input("Enter Company Name or Ticker (e.g., Reliance Industries, INFOSYS, or RELIANCE.NS):")

if st.button("Run Forensic Audit"):
    if not ticker_input:
        st.error("Please enter a company name or ticker.")
    else:
        with st.spinner(f"Gemini is browsing Google natively to audit {ticker_input}..."):
            result = run_native_search_audit(ticker_input)
            st.markdown(result)
