import streamlit as st
import google.generativeai as genai
import yfinance as yf
import time
import os
from markdown_pdf import MarkdownPdf, Section

st.set_page_config(page_title="Flagship Forensic Governance Agent", layout="wide")
st.title("🛡️ Flagship Forensic Governance Agent")
st.subheader("Automated PDF Report Generator")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- FLAGSHIP UNIFIED DATA FEED ---
@st.cache_data(ttl=86400, show_spinner=False)
def get_comprehensive_company_data(ticker):
    """Extracts raw management profiles, operational data, and 5-year financials."""
    try:
        stock = yf.Ticker(ticker)
        info_dict = stock.info
        sector = info_dict.get("sector", "N/A")
        industry = info_dict.get("industry", "N/A")
        long_summary = info_dict.get("longBusinessSummary", "No corporate summary available.")
        
        officers = info_dict.get("companyOfficers", [])
        mgmt_text = "--- OFFICIAL MANAGEMENT DATA SEED ---\n"
        if not officers:
            mgmt_text += "No structured officer database found.\n"
        else:
            for person in officers:
                name = person.get('name', 'N/A')
                title = person.get('title', 'N/A')
                pay = person.get('totalPay', 'N/A')
                mgmt_text += f"Name: {name} | Designation: {title} | Pay: {pay}\n"
                
        financials = stock.financials
        fin_text = "--- 5-YEAR FINANCIAL HISTORICAL STATEMENT ---\n"
        if not financials.empty:
            fin_text += financials.iloc[:20, :5].to_string()
        else:
            fin_text += "Historical financial statements missing or unavailable.\n"

        return f"TARGET PROFILE:\nSector: {sector}\nIndustry: {industry}\nSummary: {long_summary}\n\n{mgmt_text}\n\n{fin_text}"
        
    except Exception as e:
        return f"API_ERROR: {str(e)}"

# --- COGNITIVE FORENSIC ANALYSIS ENGINE ---
@st.cache_data(ttl=86400, show_spinner=False)
def run_flagship_forensic_audit(context, ticker):
    """Generates the comprehensive forensic audit via Gemini API."""
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are a Lead Forensic Auditor compiling a governance assessment for the entity: {ticker}.
    
    Use these raw database seeds:
    {context}
    
    INSTRUCTIONS:
    Generate exactly SIX comprehensive Markdown tables followed by a final conclusion. Use forensic estimations marked with an asterisk (*) if specific data is unavailable.
    
    ### 1. MANAGEMENT ANALYSIS TABLE
    Columns: | Name of Management | Designation | Relevant Info | Political Connections / Conflict of Interest | Fraud / Litigation History |
    
    ### 2. REMUNERATION ANALYSIS TABLE
    Columns: | Name | Designation | Individual Remuneration | Management Median | Employee Median* | Management/Employee Ratio* |
    
    ### 3. PEER RATIO COMPARISON TABLE
    - Select exactly 10 major peer companies in the EXACT same sector/industry. Place {ticker} at the very bottom.
    Columns: | Company Name | Sector/Industry | Management/Employee Remuneration Ratio* |
    
    ### 4. RELATED PARTY TRANSACTIONS (RPT) AUDIT TABLE
    - Detail transactions with promoters/directors and flag anomalies or concerning queries.
    Columns: | Related Party Entity | Nature of Relationship | Type of Transaction | Annual Value Trend* | Forensic Assessment & Risk Concern |
    
    ### 5. SHAREHOLDING PATTERNS & INSIDER TRADING TABLE
    - Map ownership (Promoters, FII, DII, Public) and flag proxy activity.
    Columns: | Shareholder Category | Current Holding (%)* | 1-Year Change (%)* | Notable Insider Trades / Proxy Flags* | Forensic Risk Assessment |
    
    ### 6. 5-YEAR HISTORICAL GROWTH TRENDS
    Columns: | Financial Year | Sales Growth (%) | Profit Growth (%) | Employee Remuneration Growth (%)* | Mgmt Remuneration Growth (%)* |
    
    ---
    ### 7. FINAL ANALYSIS OF THE MANAGEMENT (VERDICT)
    Provide your definitive, professional analysis of the management's competency, ethical alignment, and assign a final Investment/Governance Risk Grade.
    """
    
    return model.generate_content(prompt).text

# --- PDF GENERATOR ---
def create_pdf_document(markdown_text, filename):
    """Converts the AI markdown text directly into a binary PDF file."""
    pdf = MarkdownPdf()
    pdf.add_section(Section(markdown_text))
    
    # Save temporarily to system
    temp_path = f"temp_{filename}.pdf"
    pdf.save(temp_path)
    
    # Read as binary bytes
    with open(temp_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        
    # Clean up the temp file so the server doesn't get cluttered
    os.remove(temp_path)
    
    return pdf_bytes

# --- LIVE QUEUE SYSTEM MANAGER ---
def process_with_live_queue(context, ticker):
    """Handles API calls and creates a visual live-countdown queue if limits are reached."""
    queue_ui = st.empty() 
    max_retries = 6 
    
    for attempt in range(max_retries):
        try:
            report_data = run_flagship_forensic_audit(context, ticker)
            queue_ui.empty() 
            return report_data, True
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Quota" in error_msg or "ResourceExhausted" in error_msg:
                if attempt < max_retries - 1:
                    for i in range(60, 0, -1):
                        queue_ui.warning(f"⏳ **Google API Limit Reached.** Retrying automatically in **{i} seconds...**")
                        time.sleep(1)
                else:
                    return "⚠️ Queue Timeout. Please try again later.", False
            else:
                return f"⚠️ GENERATION ERROR: {error_msg}", False

# --- USER INTERFACE ---
st.info("💡 Enter an exact exchange identifier. The system will process the data and generate a downloadable PDF report.")

ticker_input = st.text_input("Enter Corporate Ticker Token:", value="RELIANCE.NS")

if st.button("Generate Forensic PDF Report"):
    if not ticker_input:
        st.error("Please enter a valid ticker token.")
    else:
        with st.spinner(f"Extracting live regulatory and financial data layers for {ticker_input}..."):
            company_context = get_comprehensive_company_data(ticker_input)
            
            if "API_ERROR" in company_context:
                st.error(f"Upstream Data Pull Failed: {company_context}")
            else:
                with st.spinner("Synthesizing metrics and formatting PDF document..."):
                    
                    # 1. Generate the text
                    audit_output, success = process_with_live_queue(company_context, ticker_input)
                    
                    # 2. ONLY if successful, convert to PDF and show download button
                    if success:
                        try:
                            pdf_file_bytes = create_pdf_document(audit_output, ticker_input)
                            
                            st.success("✅ Audit Complete. Your PDF is ready for download.")
                            
                            # The user ONLY sees this button, not the text
                            st.download_button(
                                label="📄 Download Forensic PDF Report",
                                data=pdf_file_bytes,
                                file_name=f"{ticker_input}_Forensic_Report.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                        except Exception as e:
                            st.error(f"An error occurred while compiling the PDF: {str(e)}")
                    else:
                        st.error(audit_output) # Show the error if it failed
