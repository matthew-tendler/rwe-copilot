import streamlit as st
from chains.summarization_chain import summarize_abstract, fetch_abstracts_from_europepmc

# --- MAIN APP ---

st.title("RWE Copilot: PubMed Abstract Summarizer")

# -- User Input --
query = st.text_input("Enter your PubMed/EuropePMC search terms:")
num_results = st.slider("How many abstracts?", 1, 10, 3)

if st.button("Fetch and Summarize"):
    with st.spinner("Fetching abstracts and generating AI summary..."):
        abstracts = fetch_abstracts_from_europepmc(query, num_results)
        summary = summarize_abstract(abstracts)
        st.subheader("AI Summary")
        st.markdown(f"**{summary}**")
        st.markdown("---")

        # --- FEEDBACK SECTION ---
        st.subheader("Was this summary helpful?")
        feedback_rating = st.radio(
            label="Your rating",
            options=["👍 Yes", "👎 No"],
            key="rating_radio"
        )
        feedback_text = st.text_area("Add a comment (optional)", key="feedback_text")

        if st.button("Submit feedback"):
            # You would replace this with your feedback-saving function
            st.success("Thank you for your feedback!")
            # e.g. save_feedback(summary, feedback_rating, feedback_text)

else:
    st.info("Enter your search terms above and click 'Fetch and Summarize'.")

# Optionally, show recent summaries or more info...
