import streamlit as st
import google.generativeai as genai
import yfinance as yf

st.set_page_config(page_title="Forensic Governance Audit", layout="wide")
st.title("🛡️ Forensic Governance Agent: Financial API")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- OFFICIAL YAHOO FINANCE DATA FEED ---
def get_management_data(ticker):
    """Pulls exact management data directly from Yahoo's backend database."""
    try:
        stock = yf.Ticker(ticker)
        officers = stock.info.get("companyOfficers", [])
        
        if not officers:
            return "NO_DATA"
            
        raw_text = "MANAGEMENT LIST FOUND IN DATABASE:\n"
        for person in officers:
            name = person.get('name', 'N/A')
            title = person.get('title', 'N/A')
            age = person.get('age', 'N/A')
            pay = person.get('totalPay', 'N/A')
            raw_text += f"- Name: {name} | Designation: {title} | Age: {age} | Pay: {pay}\n"
        return raw_text
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- OFFLINE GEMINI ANALYZER ---
def run_audit(context, ticker):
    # USING THE CORRECT, ACTIVE FREE TIER MODEL FOR 2026
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are a forensic auditor. Convert the following official raw data into our governance table.
    
    RAW DATA:
    {context}
    
    INSTRUCTIONS:
    1. Extract all names into the table.
    2. Because this is a financial database pull, Political/Fraud data will not be explicitly listed. Fill those columns with "No adverse flags in DB".
    
    REQUIRED FORMAT:
    | Name of Management | Designation | Relevant Info (Age/Pay) | Political Connections | Involvement in Fraud/Litigation |
    | --- | --- | --- | --- | --- |
    
    After the table, write a brief 'Forensic Risk Verdict' summarizing the team structure based on the extracted data.
    """
    
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"⚠️ **GENERATION ERROR:** {str(e)}"

# --- UI ---
st.info("💡 Ticker Rules: Use exact Yahoo Finance symbols. Add **.NS** for Indian stocks (e.g., RELIANCE.NS, INFY.NS)")

mode = st.radio("Select Input Mode:", ["Automatic API (Yahoo Finance)", "Manual Paste (For Obscure Stocks)"])

if mode == "Automatic API (Yahoo Finance)":
    ticker_input = st.text_input("Enter Ticker:", value="RELIANCE.NS")
    if st.button("Run Forensic Audit"):
        with st.spinner(f"Pulling API data for {ticker_input}..."):
            data = get_management_data(ticker_input)
            
            if data == "NO_DATA":
                st.error("Yahoo Finance returned no management data for this ticker. Check the symbol or use the Manual Paste tab.")
            elif "ERROR" in data:
                st.error(f"API Error: {data}")
            else:
                with st.spinner("Structuring Governance Table..."):
                    result = run_audit(data, ticker_input)
                    st.markdown(result)
                
else:
    raw_paste = st.text_area("Paste raw text from BSE / Annual Report here:")
    if st.button("Generate Table from Paste"):
        if not raw_paste:
            st.error("Please paste some text.")
        else:
            with st.spinner("Analyzing text..."):
                result = run_audit(raw_paste, "Custom Data")
                st.markdown(result)
