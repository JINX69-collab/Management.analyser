import streamlit as st
import google.generativeai as genai
from duckduckgo_search import DDGS

st.set_page_config(page_title="Forensic Governance Audit", layout="wide")
st.title("🛡️ Forensic Governance Agent")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Set GEMINI_API_KEY in Secrets.")
    st.stop()

# --- ENGINE ---
def run_forensic_audit(text, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    
    prompt = f"""
    You are a forensic auditor. Your goal is to convert the provided text into a formal governance table.
    
    DATA PROVIDED:
    {text}
    
    INSTRUCTIONS:
    1. Extract all names and roles found in the text.
    2. Format as a table. Use "N/A" if info is missing.
    3. If the text does not contain people, say "No management data found in text."
    
    | Name | Designation | Relevant Info | Political | Fraud/Litigation |
    | --- | --- | --- | --- | --- |
    
    Forensic Verdict:
    Summarize any red flags found.
    """
    return model.generate_content(prompt).text

# --- UI ---
ticker = st.text_input("Ticker (e.g., RELIANCE.NS):")
use_manual = st.checkbox("Manual Mode: I will paste text from my phone")

if use_manual:
    raw_text = st.text_area("Paste the text you see on your phone here:")
    if st.button("Generate Table from Paste"):
        st.markdown(run_forensic_audit(raw_text, API_KEY))
else:
    if st.button("Run Auto-Search"):
        with st.spinner("Searching..."):
            results = DDGS().text(f"{ticker} board of directors management team", max_results=5)
            full_context = "\n".join([r['body'] for r in results])
            st.markdown(run_forensic_audit(full_context, API_KEY))
            st.info("If the table is empty, check 'Manual Mode' and paste the text from your phone.")
