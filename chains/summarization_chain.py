import requests
import openai
import re
import os

client = openai.OpenAI()

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


def openai_summarize(text, prompt_prefix="Summarize the following scientific abstract:"):
    prompt = f"{prompt_prefix}\n{text}\nSummary:"
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "[Error from OpenAI: {}]".format(str(e))


def summarize_abstract(abstracts):
    """Summarize a list of abstracts using OpenAI: summarize each, then combine summaries."""
    if not abstracts:
        return "No abstracts found for that query."
    # Limit to top 2 abstracts
    abstracts = abstracts[:2]
    summaries = []
    for a in abstracts:
        try:
            text = a["abstract"][:800]
            summary = openai_summarize(text)
            summaries.append(summary)
        except Exception as e:
            summaries.append("[Error summarizing abstract]")
    if not summaries:
        return "No summaries could be generated."
    # Combine summaries and summarize again for a final summary
    combined = " ".join(summaries)
    if len(combined) > 2000:
        combined = combined[:2000]
    final_summary = openai_summarize(combined, prompt_prefix="Combine and summarize the following research summaries:")
    return strip_html_tags(final_summary)
