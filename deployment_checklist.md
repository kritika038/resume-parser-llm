# AI Resume Intelligence Platform - Cloud Deployment Checklist

This document represents the definitive operational checklist and pre-flight runbook for deploying the **AI Resume Intelligence Platform** to serverless hosting environments like **Hugging Face Spaces**.

---

## 📋 1. Pre-Flight Local Checklist (Done)
Ensure all core features compile and function correctly in your local repository environment:

*   [x] **Syntactic Compilation**: Verify that all core services and files compile without cyclic imports or errors.
    ```bash
    python3 -m py_compile app.py services/llm_parser.py services/llm_providers.py
    ```
*   [x] **Dependencies Check**: Ensure `requirements.txt` contains all explicit runtime packages, including `groq`.
*   [x] **Provider Decoupling**: Confirm the LLM Provider abstraction class successfully routes calls based on `LLM_PROVIDER` environment selections.
*   [x] **Regression Suite Passes**: Run the automated evaluation suite locally under local Ollama to verify scoring consistency and parser assertions:
    ```bash
    LLM_PROVIDER=ollama python3 evaluation.py
    ```

---

## 🔑 2. Cloud Environment Setup (Hugging Face Spaces)
Follow these setup guidelines inside the Hugging Face Console:

*   [ ] **Create Streamlit SDK Space**: Ensure **Streamlit** is selected as the workspace SDK with Python 3.10+ container baselines.
*   [ ] **Configure Repository Metadata**: Prepend the YAML header to the absolute top of `README.md` (fully automated in our code base!):
    ```yaml
    ---
    title: AI Resume Intelligence Platform
    emoji: 🚀
    colorFrom: blue
    colorTo: indigo
    sdk: streamlit
    sdk_version: 1.30.0
    app_file: app.py
    pinned: false
    ---
    ```
*   [ ] **Configure Environment Variables (Settings Tab)**:
    *   *Automatic Defaulting*: If running on Hugging Face Spaces (detected via `SPACE_ID`), the platform automatically defaults `LLM_PROVIDER` to `groq`.
    *   *(Optional)* Add **Variable**: `LLM_PROVIDER = groq` (explicitly forces the platform to run high-speed cloud Groq LPU parsers).
    *   Add **Secret**: `GROQ_API_KEY = gsk_...` (protects your personal Groq access token from public exposure; required for Groq Cloud execution).
    *   *(Optional)* Add **Variable**: `GROQ_MODEL = llama-3.1-8b-instant` (targets the high-speed Llama-3.1 model).

---

## 🚀 3. Git Pushing & Deployment Pipelines
Push code to Hugging Face Spaces and monitor live container build pipelines:

*   [ ] **Add Remote Endpoint**: Link your Hugging Face Space repository:
    ```bash
    git remote add hf https://huggingface.co/spaces/your-username/your-space-name
    ```
*   [ ] **Force Sync Push**: Deploy all local project files to the Hugging Face remote branch:
    ```bash
    git push -f hf main
    ```
*   [ ] **Monitor Container Builds**: Go to the Space dashboard and click **Container Logs**. Verify:
    *   `pip` successfully resolves and installs all requirements (including `sentence-transformers` and `groq`).
    *   The container initializes without crashing on startup.
    *   The Streamlit service launches on port `7860`.

---

## 🩺 4. Post-Deployment Smoke Tests (Live Space Validation)
Conduct the following sanity checks on the live URL to confirm 100% operational health:

*   [ ] **Startup Validation Banner Check**:
    *   Verify **System Diagnostics** widget renders in the sidebar displaying:
        - **Environment**: `Hugging Face Space`
        - **Active Provider**: `GROQ`
        - **Groq API Key**: `Configured` (or `Missing` if secret is not set)
    *   Verify that if the space initializes with a missing `GROQ_API_KEY`, a gorgeous error card displays detailing configuration steps and halts execution safely with `st.stop()`.
    *   Verify that once the key is added in Settings, the banner changes to a clean `🟢 Connected to Groq Cloud` indicator.
*   [ ] **Single Resume Analysis Test**:
    *   Upload a PDF resume file.
    *   Set a Job Description.
    *   Click **Analyze Resume**. Verify that JSON parsing, ATS scoring, Jaccard matching, and SentenceTransformer semantic Cosine calculations render in under **4 seconds**!
*   [ ] **Upskilling Pathway Validation**:
    *   Confirm missing requirements badges render (red caps) and expand a recommended **📖 Study Pathway** to check that official URL reference links are active.
*   [ ] **Bulk Recruiter Comparison Leaderboard Test**:
    *   Switch to the **Bulk Candidate Comparison** tab.
    *   Upload multiple test resumes.
    *   Verify the CSS-injected **Interactive Recruiter Leaderboard Table** renders with medals, inline progress indicators, and overall score pills.
