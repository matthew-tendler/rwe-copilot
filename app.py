import os
import streamlit as st
import pandas as pd
import requests
import re

# --- Constants ---
HUGGINGFACE_SUMMARIZATION_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
HF_TOKEN = os.environ.get("RWE_THREE_COPILOT")

# --- Helper functions ---

def strip_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def fetch_abstracts_from_europepmc(query, max_results=3):
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": query,
        "format": "json",
        "pageSize": max_results,
        "resultType": "core"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    results = []
    for item in data.get("resultList", {}).get("result", []):
        if "abstractText" in item and item["abstractText"].strip():
            results.append({
                "Title": item.get("title"),
                "Journal": item.get("journalTitle"),
                "PMID": item.get("pmid"),
                "DOI": item.get("doi"),
                "Abstract": strip_html_tags(item["abstractText"])
            })
    return results

def hf_summarize(text):
    if not HF_TOKEN:
        return "[Error: Hugging Face API token not set. Please set RWE_THREE_COPILOT in your environment.]"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": text}
    response = requests.post(HUGGINGFACE_SUMMARIZATION_URL, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            return response.json()[0]["summary_text"]
        except Exception:
            return "[Error: Unexpected response from Hugging Face API]"
    else:
        return f"[Error: Hugging Face API returned status {response.status_code}]"

def summarize_abstracts(abstracts):
    if not abstracts:
        return "No abstracts found for that query."
    summaries = []
    for a in abstracts[:2]:
        abs_text = a.get("Abstract", "")
        if abs_text:
            summary = hf_summarize(abs_text[:800])
            summaries.append(summary)
    combined = " ".join(summaries)
    if len(combined) > 2000:
        combined = combined[:2000]
    return hf_summarize(combined)

# --- Streamlit App UI ---

st.set_page_config(page_title="RWE Copilot", layout="wide")

st.title("RWE Copilot")
st.write("PubMed abstracts, summarized by AI. Powered by Europe PMC and Hugging Face.")

query = st.text_input("Enter your search query (disease, gene, drug, etc.)")

if query:
    with st.spinner("Loading abstracts and generating summary..."):
        try:
            abstracts = fetch_abstracts_from_europepmc(query)
        except Exception as e:
            st.error(f"Error fetching abstracts: {e}")
            abstracts = []

        if abstracts:
            ai_summary = summarize_abstracts(abstracts)
            # --- Show AI Summary ---
            st.subheader("AI Summary")
            st.info(ai_summary)

            # --- Show study table ---
            st.subheader("Abstracts Table")
            df = pd.DataFrame(abstracts)
            st.dataframe(df[["Title", "Journal", "PMID", "DOI"]], use_container_width=True)
        else:
            st.warning("No abstracts found.")
else:
    st.info("Enter a query to get started.")

st.caption("Tech stack: Streamlit (UI), EuropePMC API (data), Hugging Face Inference API (summarization), Pandas, Python 3.")
