import streamlit as st
import requests
import google.generativeai as genai

st.set_page_config(page_title="Forensic Governance Agent", layout="wide")
st.title("🛡️ Forensic Governance Agent: Official Site Reader")

# --- AUTH ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Set GEMINI_API_KEY in Secrets.")
    st.stop()

# --- THE "HINDRANCE-FREE" ENGINE ---
def read_official_site(url):
    """
    Uses Jina Reader to bypass firewalls and convert the 
    official corporate page into clean text.
    """
    # The prefix 'https://r.jina.ai/' is the key that bypasses bot blockers
    jina_url = f"https://r.jina.ai/{url}"
    try:
        response = requests.get(jina_url, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            return "ERROR: Could not access site. URL might be blocked."
    except Exception as e:
        return f"Error: {e}"

def run_audit(text, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-3.5-flash")
    
    prompt = f"""
    You are a forensic auditor. Use the provided text from the official company website 
    to populate the governance table.
    
    TEXT FROM WEBSITE:
    {text[:150000]}
    
    TASK: 
    1. Extract all Directors/KMPs.
    2. Format into table: | Name | Designation | Info | Political | Fraud/Litigation |
    3. Use "N/A" if info is missing.
    """
    return model.generate_content(prompt).text

# --- UI ---
# PRO-TIP: You can find these links easily on Google: 'RELIANCE industries investor relations'
target_url = st.text_input("Paste the Official Investor Relations URL (e.g., https://www.ril.com/investor-relations/):")

if st.button("Read & Analyze Official Site"):
    if not target_url:
        st.error("Please provide a valid URL.")
    else:
        with st.spinner("Bypassing corporate firewall and reading site..."):
            site_content = read_official_site(target_url)
            if "ERROR" in site_content:
                st.error(site_content)
            else:
                st.markdown(run_audit(site_content, API_KEY))
