import os
import requests
import re

HUGGINGFACE_SUMMARIZATION_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"

def strip_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def fetch_abstracts_from_europepmc(query: str, max_results: int = 3):
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
            abstract = strip_html_tags(item["abstractText"])
            pmid = item.get("pmid")
            doi = item.get("doi")
            title = item.get("title")
            journal = item.get("journalTitle")
            results.append({
                "abstract": abstract,
                "pmid": pmid,
                "doi": doi,
                "title": title,
                "journal": journal
            })
    return results

def hf_summarize(text):
    payload = {"inputs": text}
    hf_token = os.environ.get("RWE_THREE_COPILOT")  # <-- your new variable name
    headers = {"Authorization": f"Bearer {hf_token}"}
    response = requests.post(HUGGINGFACE_SUMMARIZATION_URL, headers=headers, json=payload)
    if response.status_code == 200:
        try:
            return response.json()[0]["summary_text"]
        except Exception:
            return "[Error: Unexpected response from Hugging Face API]"
    else:
        return f"[Error: Hugging Face API returned status {response.status_code}]"

def summarize_abstract(abstracts):
    if not abstracts:
        return "No abstracts found for that query."
    abstracts = abstracts[:2]
    summaries = []
    for a in abstracts:
        try:
            text = a["abstract"][:800]
            summary = hf_summarize(text)
            summaries.append(summary)
        except Exception as e:
            summaries.append("[Error summarizing abstract]")
    if not summaries:
        return "No summaries could be generated."
    combined = " ".join(summaries)
    if len(combined) > 2000:
        combined = combined[:2000]
    final_summary = hf_summarize(combined)
    return strip_html_tags(final_summary)

def get_tech_stack():
    return (
        "Tech stack: Streamlit (UI), EuropePMC API (data), Hugging Face Inference API (DistilBART CNN summarization, free hosted), "
        "Pandas (table), Python 3."
    )
