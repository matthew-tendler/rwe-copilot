---
title: RWE Copilot
emoji: 🧬
colorFrom: indigo
colorTo: green
sdk: streamlit
sdk_version: 1.35.0
app_file: app.py
pinned: false
---

# RWE Copilot

RWE Copilot is an AI-powered assistant for real-world evidence (RWE) teams. It retrieves and summarizes clinical literature for a given drug or disease using LangChain and Hugging Face models, and is built with Streamlit for interactivity.

## 🚀 Features

- Query PubMed for latest articles
- Summarize abstracts using BioGPT or SciBERT
- Interactive frontend built with Streamlit
- Modular chains for GenAI logic

## Technology Stack

- Python
- Streamlit
- LangChain
- Hugging Face Transformers
- PubMed API

## 📦 Setup

```bash
git clone <your_repo_url>
cd rwe-copilot
pip install -r requirements.txt
streamlit run app.py
```

## 📄 TODO

- Add vector search with FAISS
- Integrate Hugging Face MCP for prompt tuning
- Add eligibility simulation from RWD
