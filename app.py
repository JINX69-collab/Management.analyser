"""
Institutional Forensic Governance & Valuation Agent
Version: 1.1 (Dynamic Mode - Optional PDF)
"""

import streamlit as st
import google.generativeai as genai
import yfinance as yf
import pdfplumber
import markdown
import os
from xhtml2pdf import pisa
from io import BytesIO
import logging

# --- CONFIGURATION & LOGGING ---
logging.basicConfig(level=logging.INFO)
st.set_page_config(page_title="Forensic Governance Audit", layout="wide")

# --- UI HEADER ---
st.title("🛡️ Institutional Forensic Governance & Valuation Agent")
st.markdown("### Deep-dive forensic audit: Management Integrity, Board Efficiency, RPTs, and Cash Flows.")

# --- AUTH & SETUP ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key not found in Streamlit Secrets. Please set GEMINI_API_KEY.")
    st.stop()

# --- UTILITY FUNCTIONS ---
def extract_full_pdf_text(pdf_file):
    """Reads every page of the uploaded PDF if available."""
    if pdf_file is None:
        return "NO_PDF_UPLOADED"
    try:
        full_text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    full_text += f"\n--- PAGE {i+1} ---\n{text}\n"
        return full_text
    except Exception as e:
        logging.error(f"Error extracting PDF: {e}")
        return "ERROR_EXTRACTING_PDF"

def fetch_financial_metrics(ticker_symbol):
    """Fetches real-time financial context using yfinance."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        return {
            "Company": info.get("longName", ticker_symbol),
            "Sector": info.get("sector", "N/A"),
            "Market Cap": f"{info.get('marketCap', 0):,}",
            "Industry": info.get("industry", "N/A"),
            "P/E Ratio": info.get("forwardPE", "N/A"),
            "Debt to Equity": info.get("debtToEquity", "N/A")
        }
    except Exception as e:
        logging.error(f"Market fetch failed: {e}")
        return {"Error": "Financial fetch failed."}

def generate_pdf_from_markdown(md_text):
    """Converts the forensic Markdown output into a styled PDF."""
    try:
        html_content = markdown.markdown(md_text, extensions=['tables'])
        styled_html = f"""
        <html>
            <head>
                <style>
                    @page {{ size: A4; margin: 2cm; }}
                    body {{ font-family: 'Helvetica', sans-serif; font-size: 11pt; color: #333; }}
                    h1 {{ color: #1a365d; border-bottom: 2px solid #1a365d; }}
                    h2 {{ color: #2b6cb0; margin-top: 30px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; font-weight: bold; }}
                    blockquote {{ background: #f9f9f9; border-left: 5px solid #2b6cb0; padding: 10px; margin: 15px 0; }}
                </style>
            </head>
            <body>{html_content}</body>
        </html>
        """
        buffer = BytesIO()
        pisa.CreatePDF(styled_html, dest=buffer)
        return buffer.getvalue()
    except Exception as e:
        logging.error(f"PDF Gen Error: {e}")
        return None

# --- MAIN APPLICATION LOGIC ---

st.sidebar.header("🔑 Input Configuration")
ticker_input = st.sidebar.text_input("Enter Ticker (e.g., FINKURVE.NS):", value="")
uploaded_file = st.sidebar.file_uploader("Upload Annual Report (PDF - Optional)", type=["pdf"])

if st.sidebar.button("Run Exhaustive Forensic Audit"):
    if not ticker_input:
        st.error("Please provide a Ticker symbol.")
    else:
        with st.spinner("Executing forensic audit... (Checking market data & report content)"):
            # 1. Gather Data
            market_data = fetch_financial_metrics(ticker_input)
            doc_text = extract_full_pdf_text(uploaded_file)
            
            # 2. Configure Model
            genai.configure(api_key=API_KEY)
           model = genai.GenerativeModel("gemini-1.5-flash-latest")
            
            # 3. Dynamic Forensic Prompt
            mode_instruction = "Use the provided Annual Report text for all details." if uploaded_file else "No PDF provided. Use market knowledge and real-time data to perform a forensic estimation of governance risks."
            
            system_prompt = f"""
            You are a Senior Forensic Equity Research Analyst. 
            Analyze the following entity with total exhaustiveness. Do not summarize. 
            
            {mode_instruction}
            
            REPORT DATA (if present): {doc_text[:250000]} 
            MARKET DATA (Real-time): {market_data}
            
            MANDATORY AUDIT SECTIONS (Cover all):
            
            A. MANAGEMENT INTEGRITY:
            - Full Profile: Age, Qualifications, Tenure, Historical Track Record of KMPs.
            - Political Connections: Semantic screening for political exposure, govt advisory roles, party alignments.
            - Fraud/Litigation: Audit SEBI/MCA/ED/Regulatory actions, defaults, and legal history.
            
            B. BOARD GOVERNANCE & REMUNERATION:
            - Meetings: Total board meetings and attendance % for members.
            - Pay vs Performance: Map YoY Sales Growth vs Management Remuneration Growth.
            - Pay Equity: Calculate ratio of highest-paid director vs. median employee; management group median vs. employee median.
            - Peer Comparison: Benchmark against Top 10 sector peers (Market Cap).
            
            C. SHAREHOLDING & RPTs:
            - Promoter Trends: Audit multi-year holding changes, pledges, and hidden entities.
            - RPT Audit: Flag brand/trademark royalties, inflated rents/leases, and unsecured loans to sister entities.
            
            D. CSR & QUANTITATIVE STABILITY:
            - CSR Deployment: Identify specific NGOs/Trusts used. Audit for transparency and family connections.
            - Steadystick Ratio: Evaluate Operating Cash Flow vs. Accounting Profit consistency.
            
            FORMATTING: Provide 5-6 sentences per subsection. Use bolding and Markdown tables. 
            If data is missing, write: 'DATA NOT DISCLOSED IN REPORT'.
            """
            
            # Generate Report
            try:
                response = model.generate_content(
                    system_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=8192,
                        temperature=0.1
                    )
                )
                
                report_content = response.text
                
                # Render to Screen
                st.markdown(report_content, unsafe_allow_html=True)
                
                # Generate PDF
                pdf_data = generate_pdf_from_markdown(report_content)
                if pdf_data:
                    st.sidebar.download_button("📥 Download Final Forensic Audit PDF", pdf_data, "Forensic_Audit.pdf", "application/pdf")
            
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.info("System Ready. Upload optional.")
