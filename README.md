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

> Recruiter-Grade Resume Parser, Semantic Screening, and ATS Compatibility Scoring Engine.

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version"/></a>
  <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-1.30.0-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit"/></a>
  <a href="https://groq.com/"><img src="https://img.shields.io/badge/Groq-Serverless-F55F23?style=flat-square" alt="Groq"/></a>
  <a href="https://ollama.com/"><img src="https://img.shields.io/badge/Ollama-Local-000000?style=flat-square&logo=ollama&logoColor=white" alt="Ollama"/></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License"/></a>
</p>

### 🚀 [Live Demo](https://resume-parser-llm-anccbxdbf8muzahbgkugdy.streamlit.app/) | 🎥 [Walkthrough Video](https://www.youtube.com/watch?v=PcdjDKe6LAE) | 💻 [GitHub Repo](https://github.com/kritika038/resume-parser-llm)

---

## 🎯 Overview
Traditional ATS screening systems rely on basic keyword matching, failing to recognize equivalent synonyms (e.g. flagging "AWS" as a mismatch for "Cloud Infrastructure"). 

This platform uses **384-dimensional vector embeddings** to compute semantic similarity between resumes and job descriptions (JDs), alongside structured **LLM inference** to parse CVs into schema-compliant profiles and evaluate ATS formatting compliance.

---

## 🏗️ Architecture

```mermaid
graph TD
    Resume[📄 Candidate Resume] --> Parser[⚙️ Resume Parser]
    Parser --> LLM[🤖 LLM Provider Channel]
    LLM -->|Cloud LPU| Groq[Groq Llama 3.1]
    LLM -->|Local CPU/GPU| Ollama[Ollama Mistral]
    LLM -->|Structured JSON| ATS[📊 ATS Scoring Engine]
    LLM -->|Structured JSON| Semantic[💼 Semantic Matcher]
    Semantic -->|Generate Embeddings| Embedding[🧠 SentenceTransformers]
    ATS --> Dashboard[🏆 Recruiter Dashboard]
    Semantic --> Dashboard
    Dashboard --> Export[📥 PDF / JSON / CSV Exports]
```

---

## ✨ Core Features

- **Structured Parser**: Extracts education, experience, and projects from PDF resumes into a clean JSON schema.
- **ATS Formatting Score**: Analyzes formatting layout compliance and document completeness.
- **Semantic JD Matcher**: Evaluates cosine similarity matching scores between resume details and target JDs.
- **Skill Gap Analyzer**: Automatically maps missing core requirements and matched technical skills.
- **Actionable AI Recommendations**: Delivers prioritized, bulleted suggestions (High/Medium/Low priority) to refine profiles.
- **Bulk Candidate Comparison**: Ranks multiple candidate resumes against a single job description.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit |
| **LLM Inference** | Groq Cloud (Llama 3.1 8B) & Ollama (Mistral 7B) |
| **Semantic Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) |
| **Parsing & Formatting** | PyPDF2, ReportLab (PDF generator), Pandas (CSV exports) |

---

## ⚙️ Installation & Setup

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/kritika038/resume-parser-llm.git
   cd resume-parser-llm
   ```
2. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install Packages**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Create a `.env` file in the root:
   ```env
   LLM_PROVIDER="groq"
   GROQ_API_KEY="your_groq_api_key"
   OLLAMA_BASE_URL="http://localhost:11434"
   ```
5. **Run App**:
   ```bash
   streamlit run app.py
   ```

---

## 🤖 Supported LLM Providers

| Provider | Latency | Offline Support | Use Case |
| :--- | :--- | :--- | :--- |
| **Groq Cloud** | **<1.5s** | ❌ (Online) | High-speed cloud screening. |
| **Ollama** | **~8-12s** | **✓ Yes (Offline)** | Privacy-first local screening (GDPR compliant). |

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more details.

---

## ✍️ Author
**Kritika Bansal**
* GitHub: [@kritika038](https://github.com/kritika038)
