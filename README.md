---
title: AI Resume Intelligence Platform
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.30.0
app_file: app.py
pinned: false
tags:
  - ai-resume-parser
  - llm
  - generative-ai
  - prompt-engineering
  - semantic-search
  - embeddings
  - vector-search
  - ats-scoring
  - resume-intelligence
  - rag
  - json-validation
  - evaluation-framework
  - ai-engineering
  - production-ai
---

# AI Resume Intelligence Platform

AI-powered resume parsing, ATS analysis, semantic JD matching, and recruiter insights.

[🚀 Live Demo](https://resume-parser-llm-anccbxdbf8muzahbgkugdy.streamlit.app/) | [🎥 Demo Video](https://www.youtube.com/watch?v=PcdjDKe6LAE) | [💻 GitHub Repo](https://github.com/kritika038/resume-parser-llm)

## Features
- Resume parsing
- ATS formatting score
- Semantic JD match
- Skill gap analysis
- Recruiter dashboard
- PDF / JSON / CSV export
- Groq + Ollama support

## Tech Stack
| Layer | Tools |
|---|---|
| Frontend | Streamlit |
| LLMs | Groq, Ollama |
| Embeddings | SentenceTransformers |
| Parsing | PyPDF2, pdfplumber |
| Export | ReportLab, Pandas |

## Architecture
Resume → Parser → Embeddings → ATS → JD Match → Suggestions → Export

## Setup
```bash
# Clone the repository
git clone https://github.com/kritika038/resume-parser-llm.git
cd resume-parser-llm

# Initialize and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Environment Variables
Configure these inside a `.env` file at the root:
- `LLM_PROVIDER`: Set to `groq` or `ollama`.
- `GROQ_API_KEY`: Required if using Groq Cloud.
- `OLLAMA_BASE_URL`: Base URL for Ollama service (default: `http://localhost:11434`).

## Supported Providers
Groq / Ollama

## License
MIT
