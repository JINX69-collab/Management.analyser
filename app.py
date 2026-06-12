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
        
        # 1. Core Corporate Info (Sector, Industry, Summary)
        info_dict = stock.info
        sector = info_dict.get("sector", "N/A")
        industry = info_dict.get("industry", "N/A")
        long_summary = info_dict.get("longBusinessSummary", "No corporate summary available.")
        
        # 2. Executive Roster & Compensation
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
                
        # 3. 5-Year Financial Statements History
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
    """Processes all corporate and financial seeds to output five distinct, clean forensic tables."""
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are a Lead Forensic Auditor compiling a modular governance assessment for the target entity: {ticker}.
    
    Use the following verified raw database seeds to analyze the company's architecture:
    {context}
    
    INSTRUCTIONS:
    Generate exactly FIVE separate, clean Markdown tables. Do not combine tables or leave out details. If a specific structural data point (e.g., explicit political exposure, localized corporate fraud litigation, employee median baselines, specific competitor peer names/metrics, or precise transactional line items) is not fully detailed in the raw data seed, use your extensive financial market knowledge, regulatory filing patterns, and regional database patterns to calculate and inject realistic forensic estimations. Mark estimations with an asterisk (*).
    
    ---
    
    ### 1. MANAGEMENT ANALYSIS TABLE
    Purpose: Audit the baseline background, background qualifications, external exposure, and litigation history of all listed leadership.
    Columns: | Name of Management | Designation | Relevant Info (Age/Qual/Tenure) | Political Connections / Conflict of Interest | Involvement in Fraud / Corporate Litigation History |
    
    ### 2. REMUNERATION ANALYSIS TABLE
    Purpose: Map individual executive compensation and compute baseline internal spreads against standard workforce baselines. Do not include peer averages in this table.
    - Extract all leadership names and exact individual pay scales.
    - Compute the mathematical Median Remuneration of the Management cohort.
    - Derive the estimated Median Remuneration for standard Employees within this specific industry/tier.
    - Calculate the absolute Ratio of Management Median to Employee Median.
    Columns: | Name | Designation | Individual Remuneration | Management Median | Employee Median* | Management/Employee Ratio* |
    
    ### 3. PEER REMUNERATION COMPARISON TABLE
    Purpose: Provide a direct, name-by-name benchmarking breakdown of the top 10 closest sector peers in the market. 
    - CRITICAL SECTOR FILTERING REQUIREMENT: Identify the specific Sector and Industry listed in the Target Company Profile. You must select exactly 10 major peer companies that operate strictly within this exact same sector/industry classification. Do not include cross-sector or generalized diversified peers.
    - List these 10 distinct industry peers line-by-line by their actual corporate names.
    - Provide their corresponding estimated Management-to-Employee Remuneration Ratios.
    - CRITICAL: At the absolute bottom/last row of this table, add the target company ({ticker}) for immediate cross-comparison.
    Columns: | Company Name | Sector/Industry | Management/Employee Remuneration Ratio* |
    
    ### 4. 5-YEAR HISTORICAL GROWTH & COMPENSATION TRENDS TABLE
    Purpose: Cross-examine business performance trajectory directly against corporate wage expansion to track potential rent-seeking behaviors.
    - Extract year-over-year percentage shifts across Sales (Revenue) and Profit (Net Income) using the financial data.
    - Populate matching annual timeline percentage changes for broader Employee Remuneration Growth and top-tier Management Remuneration Growth.
    Columns: | Financial Year | Sales Growth (%) | Profit Growth (%) | Employee Remuneration Growth (%)* | Management Remuneration Growth (%)* |
    
    ### 5. RELATED PARTY TRANSACTIONS (RPT) AUDIT TABLE
    Purpose: Identify and analyze transactions between the company and its promoters, directors, or key relatives to catch asset siphoning or value diversion.
    - Analyze transaction types such as: Rent paid on promoter-owned properties, intellectual property/patent royalties paid to promoters, loans given to promoter entities, or key raw material purchases from related entities.
    - Flag anomalies where transaction growth drastically disconnects from underlying business fundamentals (e.g., *Sales growth is 10%, but rent paid on promoter properties spikes by 50%*).
    - Note if the promoter holds critical patents, brand rights, or land assets outside the listed entity that structurally affect or create dependence for the main operations of the company.
    Columns: | Related Party / Entity | Nature of Relationship | Type of Transaction | Annual Value / Growth Trend* | Forensic Assessment & Risk Level (Low/Medium/High) |
    
    ---
    
    ### FORENSIC RISK VERDICT
    Provide a concise summary evaluating discrepancies across these 5 standalone modules. Focus heavily on linking any remuneration asymmetries with critical anomalies highlighted in the Related Party Transactions matrix.
    """
    
    # AUTO-RETRY LOGIC TO PREVENT QUOTA CRASHES
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt).text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Quota" in error_msg:
                if attempt < max_retries - 1:
                    time.sleep(20)
                    continue
                else:
                    return "⚠️ **SPEED LIMIT REACHED:** Google's Free Tier limits usage to 5 requests per minute. Please wait 60 seconds and click 'Execute' again."
            else:
                return f"⚠️ **GENERATION ERROR:** {error_msg}"

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
                    with st.spinner("Synthesizing metrics and constructing master 5-table audit..."):
                        audit_output = run_flagship_forensic_audit(company_context, ticker_input)
                        st.markdown(audit_output)
                
else:
    raw_filing_paste = st.text_area("Paste unstructured textual filings (e.g., Related Party Disclosures, Corporate Governance Reports, Annual Reports):", height=300)
    if st.button("Compile Master Tables from Custom Paste"):
        if not raw_filing_paste:
            st.error("Input area is empty. Please supply text context to execute analysis.")
        else:
            with st.spinner("Parsing text fields and aligning historical vectors..."):
                audit_output = run_flagship_forensic_audit(raw_filing_paste, "Custom Context Dataset")
                st.markdown(audit_output)
