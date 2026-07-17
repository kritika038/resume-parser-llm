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
- **Resume parsing**: Converts PDF resumes into a standard JSON schema structure.
- **ATS formatting score**: Deterministically analyzes document layout and completeness.
- **Semantic JD match**: Computes cosine embedding similarity score against JDs.
- **Skill gap analysis**: Highlights matched requirements and missing skills.
- **Recruiter dashboard**: Interactive cards showing ratings, fit metrics, and advice.
- **PDF / JSON / CSV export**: Downloads structured profiles and briefing documents.
- **Groq + Ollama support**: Enables rapid cloud LPUs or private offline CPUs.

## Tech Stack
| Layer | Tools |
|---|---|
| Frontend | Streamlit |
| LLMs | Groq (Llama 3.1), Ollama (Mistral) |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| NLP | PyPDF2 |
| Export | reportlab, pandas |

## Architecture
```mermaid
graph LR
    Resume[Resume] --> Parser[Parser]
    Parser --> Embeddings[Embeddings]
    Embeddings --> ATS[ATS Score]
    ATS --> JD[JD Match]
    JD --> Suggestions[Suggestions]
    Suggestions --> Export[Export]
```

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

## License
MIT
