import streamlit as st
import google.generativeai as genai
import yfinance as yf
import time

st.set_page_config(page_title="Flagship Forensic Governance Agent", layout="wide")
st.title("🛡️ Flagship Forensic Governance Agent")
st.subheader("Multi-Table Modular Audit for PDF Export Processing")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

# --- FLAGSHIP UNIFIED DATA FEED ---
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
                age = person.get('age', 'N/A')
                pay = person.get('totalPay', 'N/A')
                mgmt_text += f"Officer Name: {name} | Designation: {title} | Age: {age} | Disclosed Pay: {pay}\n"
                
        financials = stock.financials
        fin_text = "--- 5-YEAR FINANCIAL HISTORICAL STATEMENT ---\n"
        if not financials.empty:
            fin_text += financials.iloc[:20, :5].to_string()
        else:
            fin_text += "Historical financial statements missing or unavailable in database.\n"

        return f"TARGET COMPANY PROFILE:\nSector: {sector}\nIndustry: {industry}\nSummary: {long_summary}\n\n{mgmt_text}\n\n{fin_text}"
        
    except Exception as e:
        return f"API_ERROR: {str(e)}"

# --- COGNITIVE FORENSIC ANALYSIS ENGINE ---
def run_flagship_forensic_audit(context, ticker):
    """Generates the 8-table audit prompt and calls the Gemini API."""
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are a Lead Forensic Auditor compiling a modular governance assessment for the target entity: {ticker}.
    
    Use the following verified raw database seeds to analyze the company's architecture:
    {context}
    
    INSTRUCTIONS:
    Generate exactly EIGHT separate, clean Markdown tables followed by a final conclusion. Do not combine tables or leave out details. If a specific structural data point is not fully detailed in the raw data seed, use your extensive financial market knowledge, regulatory filing patterns, and regional database patterns to calculate and inject realistic forensic estimations based on the company's size and sector. Mark estimations with an asterisk (*).
    
    ---
    
    ### 1. MANAGEMENT ANALYSIS TABLE
    Columns: | Name of Management | Designation | Relevant Info (Age/Qual/Tenure) | Political Connections / Conflict of Interest | Involvement in Fraud / Corporate Litigation History |
    
    ### 2. REMUNERATION ANALYSIS TABLE
    Columns: | Name | Designation | Individual Remuneration | Management Median | Employee Median* | Management/Employee Ratio* |
    
    ### 3. PEER REMUNERATION COMPARISON TABLE
    - CRITICAL SECTOR FILTERING REQUIREMENT: Identify the specific Sector and Industry listed in the Target Company Profile. You must select exactly 10 major peer companies that operate strictly within this exact same sector/industry classification. Do not include cross-sector or generalized diversified peers.
    - CRITICAL: At the absolute bottom/last row of this table, add the target company ({ticker}) for immediate cross-comparison.
    Columns: | Company Name | Sector/Industry | Management/Employee Remuneration Ratio* |
    
    ### 4. 5-YEAR HISTORICAL GROWTH & COMPENSATION TRENDS TABLE
    Columns: | Financial Year | Sales Growth (%) | Profit Growth (%) | Employee Remuneration Growth (%)* | Management Remuneration Growth (%)* |
    
    ### 5. RELATED PARTY TRANSACTIONS (RPT) AUDIT TABLE
    - Note anomalies where transaction growth drastically disconnects from underlying business fundamentals. Note if the promoter holds critical patents or assets outside the listed entity.
    Columns: | Related Party / Entity | Nature of Relationship | Type of Transaction | Annual Value / Growth Trend* | Forensic Assessment & Risk Level (Low/Medium/High) |
    
    ### 6. SHAREHOLDING PATTERNS & INSIDER TRADING TABLE
    - Break down holdings by Promoters, Foreign Institutional Investors (FII), Domestic Institutions (DII), and Public. Highlight notable off-market transfers or pledged promoter shares.
    Columns: | Shareholder Category | Current Holding (%)* | 1-Year Change (%)* | Notable Insider Trades / Proxy Activity Flags* | Forensic Risk Assessment |
    
    ### 7. BOARD MEETING ATTENDANCE TABLE
    Columns: | Name of Director | Designation | Total Meetings Held in FY* | Meetings Attended* | Attendance Percentage* | Regulatory Compliance Flag |
    
    ### 8. CORPORATE SOCIAL RESPONSIBILITY (CSR) FUND UTILIZATION TABLE
    Columns: | Core CSR Project / Sector | Allocated Budget* | Actual Amount Spent* | Unspent Amount Transferred / Deficit* | Forensic Audit of Beneficiary (Conflict of Interest Risk)* |
    
    ---
    
    ### FINAL COMPREHENSIVE CONCLUSION & MANAGEMENT COMPETENCY VERDICT
    Provide a masterful, multi-paragraph final conclusion evaluating the entire report. 
    1. Summarize the major red flags discovered across all 8 tables.
    2. Provide a definitive, professional assessment of the **Competency of the Management**. Are they capable, aligned with shareholder interests, or engaging in value extraction/rent-seeking behavior? 
    3. Give a final "Investment/Governance Risk Grade" (e.g., A, B, C, D, or F) with a concluding justification.
    """
    
    # We remove the try/except here so the queue system can handle the errors directly.
    return model.generate_content(prompt).text

# --- LIVE QUEUE SYSTEM MANAGER ---
def process_with_live_queue(context, ticker):
    """Handles API calls and creates a visual live-countdown queue if limits are reached."""
    queue_ui = st.empty() # Creates a dynamic container on the screen
    max_retries = 6 # Allows up to 5 minutes of queue time
    
    for attempt in range(max_retries):
        try:
            # Attempt to generate the report
            report_data = run_flagship_forensic_audit(context, ticker)
            queue_ui.empty() # Clear the queue message upon success
            return report_data, True
            
        except Exception as e:
            error_msg = str(e)
            # If Google throws a Rate Limit / Quota error, trigger the Queue System
            if "429" in error_msg or "Quota" in error_msg or "ResourceExhausted" in error_msg:
                if attempt < max_retries - 1:
                    # Live Countdown Loop
                    for i in range(60, 0, -1):
                        queue_ui.warning(f"⏳ **High Traffic Queue.** You are currently in the auto-queue. Your report will generate in **{i} seconds...**")
                        time.sleep(1)
                else:
                    return "⚠️ **Queue Timeout.** The server is at maximum capacity. Please try again later.", False
            else:
                # If it's a different random error, stop and report it
                return f"⚠️ **GENERATION ERROR:** {error_msg}", False

# --- USER INTERFACE ---
st.info("💡 Flagship Settings: Enter exact exchange identifiers. For Indian equity markets, append **.NS** or **.BO** (e.g., RELIANCE.NS, TCS.NS).")

mode = st.radio("Select Analytical Processing Feed:", ["Direct Financial API (Automated Live Feed)", "Raw Text Overwrite (Manual Corporate Filing Paste)"])

if mode == "Direct Financial API (Automated Live Feed)":
    ticker_input = st.text_input("Enter Corporate Ticker Token:", value="RELIANCE.NS")
    if st.button("Execute Flagship Forensic Audit"):
        if not ticker_input:
            st.error("Please enter a valid ticker token.")
        else:
            with st.spinner(f"Extracting live regulatory and financial data layers for {ticker_input}..."):
                company_context = get_comprehensive_company_data(ticker_input)
                
                if "API_ERROR" in company_context:
                    st.error(f"Upstream Data Pull Failed: {company_context}")
                elif "NO_DATA" in company_context:
                    st.error("The data provider returned an empty set for this asset profile. Please verify token format.")
                else:
                    with st.spinner("Synthesizing metrics and constructing master 8-table audit..."):
                        
                        # Trigger the Queue System Manager
                        audit_output, success = process_with_live_queue(company_context, ticker_input)
                        
                        # DISPLAY REPORT
                        st.markdown(audit_output)
                        
                        # ONLY SHOW DOWNLOAD BUTTON IF SUCCESSFUL
                        if success:
                            st.divider()
                            st.success("✅ Audit Complete. Your report has left the queue and is ready.")
                            st.download_button(
                                label="📥 Download Forensic Report to Desktop",
                                data=audit_output,
                                file_name=f"{ticker_input}_Forensic_Audit_Report.md",
                                mime="text/markdown"
                            )
                
else:
    raw_filing_paste = st.text_area("Paste unstructured textual filings (e.g., Related Party Disclosures, Corporate Governance Reports, Annual Reports):", height=300)
    if st.button("Compile Master Tables from Custom Paste"):
        if not raw_filing_paste:
            st.error("Input area is empty. Please supply text context to execute analysis.")
        else:
            with st.spinner("Parsing text fields and aligning historical vectors..."):
                
                # Trigger the Queue System Manager
                audit_output, success = process_with_live_queue(raw_filing_paste, "Custom Context Dataset")
                
                # DISPLAY REPORT
                st.markdown(audit_output)
                
                # ONLY SHOW DOWNLOAD BUTTON IF SUCCESSFUL
                if success:
                    st.divider()
                    st.success("✅ Audit Complete. Your report has left the queue and is ready.")
                    st.download_button(
                        label="📥 Download Forensic Report to Desktop",
                        data=audit_output,
                        file_name="Custom_Forensic_Audit_Report.md",
                        mime="text/markdown"
                    )
