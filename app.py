import streamlit as st
import google.generativeai as genai
import yfinance as yf
import pdfplumber
import markdown
from xhtml2pdf import pisa
from io import BytesIO

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
        
        financials = ticker.financials
        sales_growth_str = "Data missing in public feed"
        pbt_growth_str = "Data missing in public feed"
        
        if financials is not None and not financials.empty:
            row_labels = [str(idx).lower() for idx in financials.index]
            
            rev_idx = [i for i, label in enumerate(row_labels) if 'revenue' in label or 'sales' in label]
            if rev_idx:
                rev_series = financials.iloc[rev_idx[0]]
                if len(rev_series) >= 2:
                    growth = ((rev_series.iloc[0] - rev_series.iloc[1]) / rev_series.iloc[1]) * 100
                    sales_growth_str = f"{growth:.2f}% YoY"
            
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
        max_pages = min(len(pdf.pages), 45)
        for i in range(max_pages):
            page_text = pdf.pages[i].extract_text()
            if page_text:
                text_content += f"\n--- PAGE {i+1} ---\n" + page_text
    return text_content

# 4. Premium PDF Generator Engine
def generate_pdf(md_text):
    # Convert Markdown to HTML (enabling tables)
    html_content = markdown.markdown(md_text, extensions=['tables'])
    
    # Wrap in custom CSS for an "Investor Deck" aesthetic
    styled_html = f"""
    <html>
        <head>
            <style>
                @page {{ margin: 2cm; }}
                body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt; color: #222; line-height: 1.6; }}
                h1 {{ color: #1a365d; font-size: 18pt; border-bottom: 2px solid #1a365d; padding-bottom: 5px; }}
                h2 {{ color: #2b6cb0; font-size: 14pt; margin-top: 20px; }}
                h3 {{ color: #2d3748; font-size: 12pt; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 15px; margin-bottom: 15px; }}
                th, td {{ border: 1px solid #cbd5e0; padding: 10px; text-align: left; }}
                th {{ background-color: #edf2f7; color: #2d3748; font-weight: bold; }}
                blockquote {{ border-left: 4px solid #3182ce; background-color: #ebf8ff; padding: 10px 15px; margin: 10px 0; color: #2b6cb0; }}
                hr {{ border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
    </html>
    """
    
    # Stamp HTML into PDF Buffer
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(styled_html, dest=pdf_buffer)
    
    if pisa_status.err:
        return None
    return pdf_buffer.getvalue()

# 5. Main Execution Button Trigger
if st.sidebar.button("Run Comprehensive Forensic Analysis"):
    if not ticker_input:
        st.error("Please provide a valid stock ticker symbol.")
    else:
        with st.spinner("Analyzing data streams and generating PDF... Please wait..."):
            market_context = fetch_financial_metrics(ticker_input)
            
            if uploaded_file is not None:
                document_context = extract_text_from_pdf(uploaded_file)
            else:
                document_context = "No standalone PDF uploaded. Relying purely on internal knowledge and financial data parameters."
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            system_prompt = f"""
            You are an elite Forensic Equity Research Analyst. 
            Analyze the following target company using the provided real-time financial context and the uploaded annual report text extract.

            ### INPUT STRUCTURAL DATA CONTEXT:
            {market_context}

            ### DOCUMENT TEXT EXTRACT:
            {document_context[:60000]}
            
            ### 🛑 ARCHITECTURAL FORMATTING DIRECTIVE (CRITICAL):
            You must write with extreme analytical depth, but you are FORBIDDEN from outputting standard paragraphs or bulleted lists. You must use the "Premium Executive Brief" aesthetic.
            
            1. **The Tagging System:** Every single insight must start with a **Bolded Category Tag** followed by a colon. 
            2. **The Blockquote Wrap:** The detailed explanation for that tag must be placed on the next line inside a blockquote (`>`).
            3. **Section Spacing:** You must use HTML line breaks (`<br>`) to force whitespace between sections.
            4. **No Fluff:** Do not write introductory or concluding conversational filler. Start immediately with the title.

            ### EXACT REQUIRED TEMPLATE:

            # 🏢 Corporate Governance Audit: [Company Name]
            
            ### 🚨 Executive Verdict
            > [Write a comprehensive, multi-sentence bottom-line assessment. Cover management quality, integrity, structural stability, and valuation impact in deep detail.]
            
            ---
            <br>

            ## 🕵️ 1. Management Profile & Integrity Check

            **Leadership Profile:**
            > [Write an exhaustive assessment of KMP qualifications, tenure, historical track record, and "skin in the game".]

            **Political & Regulatory Exposure:**
            > [Write a detailed mapping of any potential political exposure, affiliations, or government alignments. Explain the potential risks.]

            **Litigation & Fraud Check:**
            > [Write a thorough check on past or present regulatory litigations, defaults, or corporate enforcement actions.]

            ---
            <br>

            ## ⚖️ 2. Board Efficiency & Remuneration

            **Attendance & Structure:**
            > [Detail the board structure, number of meetings, and specific attendance nuances.]

            **Pay vs. Performance Alignment:**
            > [Provide a deep-dive comparison of Management Remuneration Growth vs. Sales Growth and PBT Growth. Fully explain the alignment or decoupling.]

            **Internal Pay Equity:**
            > [Document and thoroughly explain the ratio of highest-paid director to median employee salary.]
            
            ### 📊 Top 10 Peer Capitalization Benchmark
            [Insert detailed Markdown Table: Peer Name | Market Cap | Detailed Governance Health Note]

            ---
            <br>

            ## 🚩 3. Shareholding Patterns & RPTs

            **Promoter Holding Trends:**
            > [Provide a deep analysis of structural dilution, pledges, and equity ownership patterns over time. Explain what this means for minority shareholders.]

            **Wealth Extraction Check (RPTs):**
            > [Thoroughly screen and detail any potential wealth extraction channels. Explicitly explain the nature of brand royalties, asset leases, or un-commercialized loans.]

            ---
            <br>

            ## 💸 4. CSR Deployments & Structural Stability

            **CSR Deployment Audit:**
            > [Audit and explain in detail where corporate social responsibility funds are deployed and if they are routed transparently.]

            **Cash Flow Trend Stability:**
            > [Provide a detailed evaluation of the fundamental trend stability of cash generation versus accounting earnings.]
            
            ---
            """
            
            try:
                # Run the AI Inference
                response = model.generate_content(system_prompt)
                report_markdown = response.text
                
                # Render the final report to the website screen
                st.success("Analysis Complete!")
                st.markdown(report_markdown, unsafe_allow_html=True)
                
                # Convert to PDF and create download button
                pdf_data = generate_pdf(report_markdown)
                if pdf_data:
                    st.sidebar.markdown("---")
                    st.sidebar.download_button(
                        label="📥 Download Forensic Report (.pdf)",
                        data=pdf_data,
                        file_name=f"{ticker_input}_Forensic_Governance_Report.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Report generated, but PDF conversion failed.")
                    
            except Exception as ai_err:
                st.error(f"AI Generation Failed: {str(ai_err)}")
