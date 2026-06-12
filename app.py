import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Forensic Governance Agent", layout="wide")
st.title("🛡️ Forensic Governance Agent: Google Grounding")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- CORE AUDIT ENGINE ---
def run_native_search_audit(ticker):
    try:
        # Correctly passing google_search as a tool object to bypass the validation error
        model = genai.GenerativeModel(
            model_name="models/gemini-2.0-flash",
            tools=[{"google_search": {}}]
        )
        
        prompt = f"""
        Perform a professional forensic governance audit for the company/ticker: {ticker}.
        Use your live Google Search tool to look up their current Board of Directors and Key Managerial Personnel (KMP).
        
        Search high-quality financial websites like Screener.in, Moneycontrol, Yahoo Finance, or the official company Investor Relations page.
        
        TASK:
        Populate the exact 5-column Markdown table format below. If information for a cell cannot be found anywhere, use "N/A". Find at least the main executive directors (like CEO, MD, or Chairman).
        
        REQUIRED FORMAT:
        | Name of Management | Designation | Relevant Info (Age/Tenure/Qual) | Political Connections | Involvement in Fraud/Litigation |
        | --- | --- | --- | --- | --- |
        
        After the table, provide a 'Forensic Risk Verdict' summarizing any corporate governance flags or red flags found during the evaluation.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Execution Error: {str(e)}"

# --- UI ---
ticker_input = st.text_input("Enter Company Name or Ticker (e.g., Reliance Industries, Infosys, TATA Motors):")

if st.button("Run Forensic Audit"):
    if not ticker_input:
        st.error("Please enter a company name or ticker.")
    else:
        with st.spinner(f"Gemini is natively browsing Google to compile the audit for {ticker_input}..."):
            result = run_native_search_audit(ticker_input)
            st.markdown(result)
