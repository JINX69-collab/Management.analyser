import streamlit as st
import google.generativeai as genai
import yfinance as yf

st.set_page_config(page_title="Forensic Governance Audit", layout="wide")
st.title("🛡️ Forensic Governance Agent: Remuneration & Growth")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- OFFICIAL YAHOO FINANCE DATA FEED ---
def get_company_data(ticker):
    """Pulls management and 5-year financial data from Yahoo's backend."""
    try:
        stock = yf.Ticker(ticker)
        
        # 1. Management Data Extraction
        officers = stock.info.get("companyOfficers", [])
        mgmt_text = "MANAGEMENT LIST FOUND IN DATABASE:\n"
        if not officers:
            mgmt_text += "No management data found.\n"
        else:
            for person in officers:
                name = person.get('name', 'N/A')
                title = person.get('title', 'N/A')
                pay = person.get('totalPay', 'N/A')
                mgmt_text += f"- Name: {name} | Designation: {title} | Pay: {pay}\n"
                
        # 2. Historical Financials Extraction (Past 5 Years)
        financials = stock.financials
        fin_text = "FINANCIAL STATEMENT DATA (Revenue & Income):\n"
        if not financials.empty:
            # Grabs the top rows (Total Revenue, Net Income) for the available years
            fin_text += financials.iloc[:15, :5].to_string()
        else:
            fin_text += "No financial statements available in DB."

        return f"{mgmt_text}\n\n{fin_text}"
        
    except Exception as e:
        return f"ERROR: {str(e)}"

# --- FORENSIC AI ANALYZER ---
def run_advanced_audit(context, ticker):
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are a forensic auditor. Analyze the following official raw data for {ticker}.
    
    RAW DATA:
    {context}
    
    INSTRUCTIONS:
    Provide exactly TWO Markdown tables. Do not output empty tables. If exact data (like median employee pay or peer ratios) is missing from the raw text, use your industry knowledge to provide highly realistic estimates marked with an asterisk (*).
    
    TABLE 1: Remuneration Analysis
    - Extract all management names and individual remunerations.
    - Calculate the Median Remuneration of the Management team.
    - Provide the estimated Median Remuneration for the company's Employees.
    - Calculate the Ratio of Management Median to Employee Median.
    - Provide the estimated Average Ratio for the Top 10 Industry Peers of this company.
    
    Columns: | Name | Designation | Individual Remuneration | Mgmt Median | Employee Median | Mgmt/Employee Ratio | Top 10 Peers Ratio |
    
    TABLE 2: Historical Growth Trends (Past 5 Years)
    - Using the Raw Financial Data, calculate the Sales (Revenue) Growth and Profit (Net Income) Growth year-over-year.
    - Provide the estimated Employee Remuneration Growth and Management Remuneration Growth for those same years.
    
    Columns: | Year | Sales Growth (%) | Profit Growth (%) | Employee Remuneration Growth (%) | Mgmt Remuneration Growth (%) |
    
    FORENSIC VERDICT:
    After the tables, write a brief verdict summarizing whether management compensation aligns fairly with the company's 5-year profit and sales growth, or if it represents a red flag.
    """
    
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"⚠️ **GENERATION ERROR:** {str(e)}"

# --- UI ---
st.info("💡 Ticker Rules: Use exact Yahoo Finance symbols. Add **.NS** for Indian stocks (e.g., RELIANCE.NS, INFY.NS)")

ticker_input = st.text_input("Enter Ticker:", value="RELIANCE.NS")

if st.button("Run Advanced Remuneration Audit"):
    if not ticker_input:
        st.error("Please enter a ticker.")
    else:
        with st.spinner(f"Pulling Management & Financial APIs for {ticker_input}..."):
            data = get_company_data(ticker_input)
            
            if "ERROR" in data:
                st.error(f"API Error: {data}")
            else:
                with st.spinner("Calculating ratios and structuring tables..."):
                    result = run_advanced_audit(data, ticker_input)
                    st.markdown(result)
