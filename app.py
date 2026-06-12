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
        # Initialize the model without the tool first
        model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
        
        prompt = f"""
        Perform a professional forensic governance audit for the company: {ticker}.
        Use your Google Search tool to find their official Board of Directors and Key Managerial Personnel (KMP) list.
        
        TASK:
        Populate the exact 5-column Markdown table format below. If information for a cell cannot be found, use "N/A".
        Find at least the main executive directors (like CEO, MD, or Chairman).
        
        REQUIRED FORMAT:
        | Name of Management | Designation | Relevant Info (Age/Tenure/Qual) | Political Connections | Involvement in Fraud/Litigation |
        | --- | --- | --- | --- | --- |
        
        After the table, provide a 'Forensic Risk Verdict' summarizing any corporate governance flags.
        """
        
        # We pass the exact string required by the updated SDK directly into generate_content
        response = model.generate_content(
            prompt,
            tools="google_search_retrieval"
        )
        return response.text
    except Exception as e:
        return f"Execution Error: {str(e)}\n\n(Did you update requirements.txt to google-generativeai>=0.8.4?)"

# --- UI ---
ticker_input = st.text_input("Enter Company Name (e.g., Reliance Industries, Infosys):")

if st.button("Run Forensic Audit"):
    if not ticker_input:
        st.error("Please enter a company name.")
    else:
        with st.spinner(f"Gemini is natively browsing Google to compile the audit for {ticker_input}..."):
            result = run_native_search_audit(ticker_input)
            st.markdown(result)
