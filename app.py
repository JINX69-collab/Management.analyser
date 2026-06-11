import streamlit as st
import google.generativeai as genai
import yfinance as yf
import pdfplumber
import markdown
from xhtml2pdf import pisa
from io import BytesIO

# --- PAGE SETUP ---
st.set_page_config(page_title="Forensic Governance Audit", layout="wide")
st.title("🛡️ Institutional Forensic Governance & Valuation Agent")

# --- AUTH & SECRETS ---
# Ensure GEMINI_API_KEY is in Streamlit Cloud Secrets
api_key = st.secrets["GEMINI_API_KEY"]
ticker_input = st.sidebar.text_input("Enter Ticker (e.g., INFY.NS):", value="")
uploaded_file = st.sidebar.file_uploader("Upload Annual Report (PDF)", type=["pdf"])

# --- DATA ENGINES ---
def extract_full_pdf_text(pdf_file):
    # Reads every page without truncation
    full_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text: full_text += text + "\n"
    return full_text

def fetch_financial_context(ticker):
    # Pulls real-time market data for benchmarking
    t = yf.Ticker(ticker)
    info = t.info
    return {
        "Name": info.get("longName"),
        "Sector": info.get("sector"),
        "MarketCap": info.get("marketCap"),
        "PeerList": info.get("industry") 
    }

def generate_pdf(md_text):
    html = f"<html><body>{markdown.markdown(md_text, extensions=['tables'])}</body></html>"
    buffer = BytesIO()
    pisa.CreatePDF(html, dest=buffer)
    return buffer.getvalue()

# --- EXECUTION ---
if st.sidebar.button("Run Forensic Audit"):
    if not ticker_input or not uploaded_file:
        st.error("Missing input.")
    else:
        with st.spinner("Analyzing all aspects..."):
            market_data = fetch_financial_context(ticker_input)
            doc_text = extract_full_pdf_text(uploaded_file)
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # THE COMPLETE FORENSIC PROMPT
            system_prompt = f"""
            You are a Senior Forensic Equity Research Analyst. 
            Analyze the following text with absolute exhaustiveness. Do not summarize. 
            Address every single bullet point below using the provided data: {doc_text[:100000]}
            
            MANDATORY ANALYSIS PILLARS:
            
            A. MANAGEMENT INTEGRITY: 
            - Extract age, qualifications, tenure, and operational track record of KMPs.
            - Screen for political exposure, government advisory roles, or party alignments.
            - Run a negative-news check for financial defaults, scams, or regulatory litigations (SEBI/MCA).

            B. BOARD EFFICIENCY & REMUNERATION: 
            - Report total board meetings and attendance percentages per director.
            - Compare Management Remuneration Growth vs. Sales Growth vs. PBT Growth.
            - Extract Director-to-Employee salary ratios and internal management equity ratios.
            - Benchmark these against top sector peers.

            C. SHAREHOLDING & RPTs:
            - Analyze promoter holding trends (stakes, pledges, hidden entities).
            - Audit Related Party Transactions: Flag brand royalties, inflated rents/leases, and unsecured loans to sister entities.

            D. CSR & CASH FLOW:
            - Audit CSR fund deployment: Verify transparency vs. routing through promoter-affiliated NGOs.
            - Steadystick Ratio: Evaluate the fundamental conversion of accounting profits into operating cash flow.

            FORMATTING: Provide a deep-dive report. Use bolding for figures and Markdown tables for all quantitative data.
            """
            
            response = model.generate_content(system_prompt)
            report = response.text
            
            st.markdown(report, unsafe_allow_html=True)
            
            pdf_data = generate_pdf(report)
            st.sidebar.download_button("📥 Download PDF", pdf_data, "Forensic_Audit.pdf", "application/pdf")
