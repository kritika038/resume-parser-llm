# AI Resume Intelligence Platform - Architecture

## End-to-End System Architecture Diagram

Below is the conceptual and operational data flow architecture modeling how the platform ingests unstructured data and transforms it into rich candidate profiles and scoring matrices.

```mermaid
graph TD
    classDef user fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef ui fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#311b92;
    classDef pipeline fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#5d4037;
    classDef provider fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f;
    classDef backend fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;
    classDef engine fill:#e0f7fa,stroke:#00838f,stroke-width:2px,color:#006064;
    classDef dash fill:#fbe9e7,stroke:#d84315,stroke-width:2px,color:#bf360c;

    User["👤 User / Recruiter"]:::user
    UI["🖥️ Streamlit UI Dashboard"]:::ui
    Pipeline["⚙️ Resume Processing Pipeline<br/>(PyPDF2 Text Extraction)"]:::pipeline
    Provider["🔀 LLM Provider Layer<br/>(Base Abstraction Resolver)"]:::provider
    Ollama["🖥️ Ollama Provider<br/>(Local Offline Mistral-7B)"]:::backend
    Groq["⚡ Groq Provider<br/>(Cloud Serverless Llama-3)"]:::backend
    JSON["📝 Guided JSON Extraction<br/>(Structural Regex & Schema Validation)"]:::engine
    ATS["📊 ATS Scoring Engine<br/>(Deterministic Completeness Checking)"]:::engine
    Semantic["📐 Semantic Matching Engine<br/>(SentenceTransformers Cosine Alignments)"]:::engine
    SkillGap["🔍 Skill Gap Analysis<br/>(Missing Core Skills & Upskilling Pathway)"]:::engine
    Dashboard["🏆 Interactive Results Dashboard<br/>(Recruiter Leaderboard & Graphs)"]:::dash

    User ──► UI
    UI ──► Pipeline
    Pipeline ──► Provider
    Provider ──► Ollama
    Provider ──► Groq
    Ollama ──► JSON
    Groq ──► JSON
    JSON ──► ATS
    JSON ──► Semantic
    JSON ──► SkillGap
    ATS ──► Dashboard
    Semantic ──► Dashboard
    SkillGap ──► Dashboard
    Dashboard ──► UI
```

---

## Architectural Layers Spec Sheet

### 1. Presentation & User Experience Layer
* **Streamlit Web Application (`app.py`)**: Powers the single-page responsive dashboard. Incorporates visual component tabs, interactive radio selectors, progress bars, and CSS overrides supporting both system dark and light modes.
* **Environment Guardian checks**: Injected at application startup. Proactively tests connection urls and api secrets, providing step-by-step guidance cards instead of throwing silent parsing failures.

### 2. Processing & Extraction Pipeline
* **PyPDF2 Extractor (`services/pdf_extractor.py`)**: Extracts unicode streams from raw candidate PDF uploads and handles whitespace normalization.
* **Regularized parser (`services/llm_parser.py`)**: Constructs instruction-based prompts incorporating strict schema definitions, forcing models to output valid JSON representations.

### 3. LLM Provider Registry & Gateway
* **Registry Gateway (`services/llm_providers.py`)**: Intercepts downstream text parsing calls and dynamically routes them using factory resolution patterns.
* **Local offline engine (Ollama + Mistral-7B)**: Handles completely private, zero-network parsing workloads on local hardware.
* **Cloud LPU accelerator (Groq + Llama-3-8B)**: Utilizes official SDK APIs to deliver ultra-fast candidate extractions under **1.5 seconds**.

### 4. Downstream Analytics & Matching Engines
* **ATS Scoring Engine (`services/ats_scorer.py`)**: Applies structural scoring algorithms checking for verified contact tags, chronological role history, educational accomplishments, and projects list.
* **Semantic Matcher (`services/jd_matcher.py`)**: Directs **SentenceTransformers (`all-MiniLM-L6-v2`)** models to map CV and JD skill sets into high-dimensional vector spaces. Resolves synonyms using **Cosine Similarity** vector multiplication.
* **Upskilling Analyzer (`services/skill_gap_analyzer.py`)**: Calculates skill gaps (matched vs missing) and dynamically designs **📖 Study Pathways** matching missing requirements to official product document links.
* **Candidate Comparator (`services/candidate_comparator.py`)**: Executes bulk analysis loops, scoring large candidate pools and outputting structural pandas records to power leaderboard ranks.
