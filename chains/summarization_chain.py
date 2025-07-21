import requests
from transformers import pipeline
import re


# Set up the Hugging Face summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def strip_html_tags(text):
    """Remove HTML tags from a string."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def fetch_abstracts_from_europepmc(query: str, max_results: int = 3):
    """Fetch abstracts from Europe PMC API given a search query, including PubMed ID and DOI."""
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
            results.append({
                "abstract": abstract,
                "pmid": pmid,
                "doi": doi
            })
    print("Europe PMC raw response:", data)
    print("Extracted abstracts:", results)
    return results


def summarize_abstract(query: str):
    """Fetch real abstracts and summarize them."""
    abstracts = fetch_abstracts_from_europepmc(query)
    if not abstracts:
        return "No abstracts found for that query."
    # Extract only the abstract text from each dict
    combined_text = " ".join(a["abstract"] for a in abstracts)
    summary = summarizer(combined_text, max_length=150, min_length=30, do_sample=False)[0]["summary_text"]
    return strip_html_tags(summary)
