import streamlit as st
from chains.summarization_chain import summarize_abstract, fetch_abstracts_from_europepmc
import pandas as pd
import openai
client = openai.OpenAI(api_key="sk-...your-key-here...")

st.title("🧠 RWE Copilot")

query = st.text_input("Enter a disease or drug:")
submitted = st.button("Search")

if query and submitted:
    with st.spinner("Fetching research and generating AI summary..."):
        abstracts = fetch_abstracts_from_europepmc(query)
        if not abstracts:
            st.error("No abstracts found for that query.")
        else:
            # --- AI Summary Section (TOP, big font) ---
            st.markdown("""
                <div style='background-color:#fff9c4;padding:1.5em 1em 1.5em 1em;border-radius:12px;margin-bottom:1.5em;border:2px solid #ffe082;'>
                    <span style='font-size:1.6em;font-weight:bold;color:#333;'>AI-Powered Summary</span><br>
            """, unsafe_allow_html=True)
            summary = summarize_abstract(abstracts)
            st.markdown(f"<div style='font-size:1.2em;margin-top:0.7em;color:#222;'>{summary}</div></div>", unsafe_allow_html=True)

            # --- Copy Summary Button ---
            st.text_area('Copy summary', summary, height=120, key='summary_copy', help='Click the copy button to copy the summary.', disabled=False)

            # --- Table of Abstracts ---
            table_data = []
            for abs_info in abstracts:
                title = abs_info.get("title", "N/A")
                journal = abs_info.get("journal", "N/A")
                pmid = abs_info.get("pmid")
                doi = abs_info.get("doi")
                abstract = abs_info.get("abstract", "N/A")
                pmid_link = f"[PubMed](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)" if pmid else ""
                doi_link = f"[DOI](https://doi.org/{doi})" if doi else ""
                table_data.append({
                    "Title": title,
                    "Journal": journal,
                    "PubMed ID": pmid_link,
                    "DOI": doi_link,
                    "Abstract": abstract
                })
            st.subheader("Table of Abstracts")
            st.dataframe(pd.DataFrame(table_data))

            # --- Show Full Abstracts (expand/collapse) ---
            st.subheader("Full Abstracts")
            for i, abs_info in enumerate(abstracts, 1):
                with st.expander(f"{i}. {abs_info.get('title', 'Untitled Study')}"):
                    st.markdown(f"**Journal:** {abs_info.get('journal', 'N/A')}")
                    pmid = abs_info.get("pmid")
                    doi = abs_info.get("doi")
                    links = []
                    if pmid:
                        links.append(f'[PubMed](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)')
                    if doi:
                        links.append(f'[DOI](https://doi.org/{doi})')
                    link_str = " | ".join(links)
                    st.markdown(link_str)
                    st.markdown(abs_info.get("abstract", "No abstract available."))

            # --- Optional: Feedback Section ---
            st.markdown("---")
            st.subheader("Was this summary helpful?")
            feedback_rating = st.radio(
                label="Your rating",
                options=["👍 Yes", "👎 No"],
                key="rating_radio"
            )
            feedback_text = st.text_area("Add a comment (optional)", key="feedback_text")
            if st.button("Submit feedback"):
                st.success("Thank you for your feedback!")
