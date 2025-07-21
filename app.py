import streamlit as st
from chains.summarization_chain import summarize_abstract, fetch_abstracts_from_europepmc

st.title("🧠 RWE Copilot")

query = st.text_input("Enter a disease or drug:")

if query:
    abstracts = fetch_abstracts_from_europepmc(query)
    if not abstracts:
        st.error("No abstracts found for that query.")
    else:
        st.subheader("Latest Research Abstract(s)")
        for i, abs_info in enumerate(abstracts, 1):
            abs_text = abs_info["abstract"]
            pmid = abs_info.get("pmid")
            doi = abs_info.get("doi")
            links = []
            if pmid:
                links.append(f'[PubMed](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)')
            if doi:
                links.append(f'[DOI](https://doi.org/{doi})')
            link_str = " | ".join(links)
            st.markdown(f"**{i}.** {abs_text}  "+ (f"{link_str}" if link_str else ""))
        st.subheader("AI Summary")
        st.write(summarize_abstract(query))

