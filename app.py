import streamlit as st
import google.generativeai as genai
import yfinance as yf
import pdfplumber
import pandas as pd

# 1. Page Configuration & UI Layout
st.set_page_config(page_title="AI Governance & Valuation Agent", layout="wide")
st.title("🛡️ Institutional Corporate Governance & Valuation AI Agent")
st.write("Deep-dive forensic analysis on management, integrity, remuneration, RPTs, and structural cash flows.")

# Sidebar for Setup & Configurations
st.sidebar.header("🔑 Configuration Panel")
api_key = st.secrets["GEMINI_API_KEY"]
ticker_input = st.sidebar.text_input("Enter Indian Stock Ticker (e.g., INFY.NS, BAJAJHFL.NS):", value="")

# Document Uploader
uploaded_file = st.sidebar.file_uploader("Upload Annual Report or AGM Notice (PDF)", type=["pdf"])

# 2. Financial Data Fetching Engine (yfinance)
def fetch_financial_metrics(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Pull multi-year financial data
        financials = ticker.financials
        
        # Extract Sales (Revenue) and Profit Before Tax (PBT) if available
        sales_growth_str = "Data missing in public feed"
        pbt_growth_str = "Data missing in public feed"
        
        if financials is not None and not financials.empty:
            # Safely navigate rows across varying yfinance formats
            row_labels = [str(idx).lower() for idx in financials.index]
            
            # Find Revenue row
            rev_idx = [i for i, label in enumerate(row_labels) if 'revenue' in label or 'sales' in label]
            if rev_idx:
                rev_series = financials.iloc[rev_idx[0]]
                if len(rev_series) >= 2:
                    # Calculate simple YoY growth from latest two periods
                    growth = ((rev_series.iloc[0] - rev_series.iloc[1]) / rev_series.iloc[1]) * 100
                    sales_growth_str = f"{growth:.2f}% YoY"
            
            # Find PBT row
            pbt_idx = [i for i, label in enumerate(row_labels) if 'pretax' in label or 'before tax' in label]
            if pbt_idx:
                pbt_series = financials.iloc[pbt_idx[0]]
                if len(pbt_series) >= 2:
                    growth = ((pbt_series.iloc[0] - pbt_series.iloc[1]) / pbt_series.iloc[1]) * 100
                    pbt_growth_str = f"{growth:.2f}% YoY"

        meta_data = {
            "Company Name": info.get("longName", ticker_symbol),
            "Sector": info.get("sector", "Unknown"),
            "Industry": info.get("industry", "Unknown"),
            "Market Cap (INR)": f"{info.get('marketCap', 0):,}",
            "Sales Growth (Latest YoY)": sales_growth_str,
            "Profit Before Tax Growth (Latest YoY)": pbt_growth_str
        }
        return meta_data
    except Exception as e:
        return {"Error": f"Could not automatically fetch market data: {str(e)}"}

# 3. PDF Parsing Engine
def extract_text_from_pdf(pdf_file):
    text_content = ""
    with pdfplumber.open(pdf_file) as pdf:
        # Scan up to 45 pages to capture major governance/remuneration/RPT disclosures
        max_pages = min(len(pdf.pages), 45)
        for i in range(max_pages):
            page_text = pdf.pages[i].extract_text()
            if page_text:
                text_content += f"\n--- PAGE {i+1} ---\n" + page_text
    return text_content

# 4. Main Execution Button Trigger
if st.sidebar.button("Run Comprehensive Forensic Analysis"):
    if not api_key:
        st.error("Please enter your Gemini API Key to continue.")
    elif not ticker_input:
        st.error("Please provide a valid stock ticker symbol.")
    else:
        with st.spinner("Analyzing data streams and corporate documents... Please wait..."):
            # Execute yfinance layer
            market_context = fetch_financial_metrics(ticker_input)
            
            # Execute PDF parser layer
            document_context = ""
            if uploaded_file is not None:
                document_context = extract_text_from_pdf(uploaded_file)
            else:
                document_context = "No standalone PDF uploaded. Relying purely on internal knowledge and financial data parameters."
            
            # Configure Gemini Brain
            genai.configure(api_key=api_key)
            # --- MODEL IS HARDCODED TO FLASH HERE ---
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Formulate the Strict System Core Prompt
            # Formulate the Strict System Core Prompt
      # Formulate the Strict System Core Prompt
          # Formulate the Strict System Core Prompt
            system_prompt = f"""
            You are an elite Forensic Equity Research Analyst and Corporate Governance Auditor. 
            Analyze the following target company using the provided real-time financial context and the uploaded annual report text extract.

            ### INPUT STRUCTURAL DATA CONTEXT:
            {market_context}

            ### DOCUMENT TEXT EXTRACT:
            {document_context[:60000]}
            
            ### 🛑 CONTENT DIRECTIVE (CRITICAL):
            DO NOT SUMMARIZE OR CUT DETAILS. You must provide a comprehensive, deep-dive forensic analysis. Include all nuances, context, and detailed explanations of your findings. Provide the full institutional depth expected by a professional fund manager.

            ### 🎨 FORMATTING DIRECTIVE: "INVESTOR DECK" AESTHETIC
            While the content must be exhaustive and detailed, the presentation must be pristine, spaced out, and highly readable.
            1. **Structured Depth:** Do NOT write massive block paragraphs. Instead, use detailed bullet points. A bullet point should contain full, thorough explanations (3-5 sentences is fine), but breaking it into bullets creates necessary whitespace.
            2. **Visual Hierarchy:** Use clear headings (##, ###) and horizontal rules (---) to separate sections.
            3. **Bold for Scannability:** Heavily **bold** key numbers, names, percentages, and critical financial terms within your detailed text so the reader's eye can easily scan the heavy data.
            4. **Data Tables:** You MUST use Markdown tables whenever comparing numbers, showing board attendance, or listing peer comparisons.
            5. **Blockquotes:** Use blockquotes (>) to highlight executive verdicts or severe red-flag alerts.

            ### MANDATORY REPORT STRUCTURE:

            # 🏢 Corporate Governance & Forensic Audit: [Company Name]
            > **Executive Verdict:** [Provide a detailed, highly professional, multi-sentence bottom-line assessment on the company's management quality, integrity, and structural stability.]
            
            ---

            ## 🕵️ 1. Management Profile & Integrity Check
            * **Relevant Management Information:** [Provide a detailed assessment of qualifications, tenure, historical track record, and "skin in the game" of KMPs. Do not cut details.]
            * **Political Connections:** [Provide a detailed mapping of any potential political exposure, affiliations, or government policy alignments.]
            * **Involvement in Frauds:** [Provide a thorough check on past or present regulatory litigations, defaults, or corporate enforcement actions.]

            ---

            ## ⚖️ 2. Board Efficiency & Remuneration Analysis
            * **Board Meetings & Attendance:** [Detail the board structure, number of meetings, and specific attendance nuances. Flag any structural absenteeism.]
            * **Remuneration vs. Performance Link:** [Provide a deep-dive comparison of Management Remuneration Growth directly against Sales Growth and Profit Before Tax (PBT) Growth. Explain the alignment or decoupling.]
            * **Internal Pay Equity Ratios:** [Document and thoroughly explain the ratio of highest-paid director to median employee salary, and the median management remuneration vs median employee.]
            
            ### 📊 Top 10 Peer Capitalization Comparison
            [Insert detailed Markdown Table showcasing the top 10 listed peer companies sorted by market capitalization. Include columns for Peer Name, Market Cap, and a brief Governance/Remuneration Benchmark note.]

            ---

            ## 🚩 3. Shareholding Patterns & Concerning RPTs
            * **Promoter Holding Trends:** [Provide a deep analysis of structural dilution, pledge percentages, and equity ownership patterns over time.]
            * **Related Party Transactions (RPTs):** [Thoroughly screen and detail any potential wealth extraction channels. Explicitly explain the nature of brand royalties, asset leases, or un-commercialized loans to sister entities.]

            ---

            ## 💸 4. CSR Deployments & Structural Quantitative Stability
            * **Use of CSR Funds:** [Audit and explain in detail where corporate social responsibility funds are deployed. Are they routing transparently?]
            * **Cash Flow Trend Stability (Steadystick Ratio Framework):** [Provide a detailed evaluation of the fundamental trend stability of cash generation. Explain how securely accounting earnings translate to operating cash flows to guarantee underlying trend line health.]
            
            ---
            """
            
            try:
                # Run the AI Inference
                response = model.generate_content(system_prompt)
                report_markdown = response.text
                
                # Render the final report to the website screen
                st.success("Analysis Complete!")
                st.markdown(report_markdown)
                
                # Automatic Markdown Downloader Feature
                st.sidebar.markdown("---")
                st.sidebar.download_button(
                    label="📥 Download Forensic Report (.md)",
                    data=report_markdown,
                    file_name=f"{ticker_input}_Forensic_Governance_Report.md",
                    mime="text/markdown"
                )
            except Exception as ai_err:
                st.error(f"AI Generation Failed: {str(ai_err)}")
