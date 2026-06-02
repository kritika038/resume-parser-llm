# 📂 Recruiter Demo Assets Folder

Welcome to the **AI Resume Intelligence Platform** recruiter playground! This directory contains a pre-packaged suite of high-fidelity, representative candidate profiles and industry job descriptions to allow recruiters, hiring managers, and QA teams to test the platform instantly in under **1 minute**.

---

## 🏗️ Folder Structure

```
demo_data/
├── README.md               <-- This Guide
├── resumes/
│   ├── alice_dev_ai.txt    <-- Senior AI Developer Profile
│   ├── bob_coder_fe.txt    <-- Junior Frontend React Specialist
│   └── charlie_ml_res.txt  <-- ML NLP Research Scientist
└── jds/
    ├── senior_ai_jd.txt    <-- Senior AI Engineer requirements
    ├── frontend_fe_jd.txt  <-- React Frontend Engineer requirements
    └── ml_scientist_jd.txt <-- Deep Learning Researcher requirements
```

---

## 👩‍💻 Candidate Tracks & Alignment Profiles

To evaluate both keyword overlap and deep conceptual semantic matching, the candidates represent three highly distinct engineering tracks:

### 1️⃣ Senior AI Specialist (Alice Dev)
*   **Target JD**: `senior_ai_developer_jd.txt`
*   **Profile Highlights**: Large Language Models, PyTorch, FastAPI, Docker, Kubernetes GPU scaling, Vector Databases (Qdrant).
*   **Expected Results**:
    *   **ATS Score**: **~80/100** (Exceptional structural compatibility, complete contact parameters, experience durations, academic levels).
    *   **JD Semantic Match**: **High (~76% - 80%)** against the Senior AI JD.
    *   **JD Match with Bob/Charlie JDs**: **Low (~30% - 50%)**. Semantic spaces isolate AI models from pure CSS layouts or computational math equations!

### 2️⃣ Frontend React Specialist (Bob Coder)
*   **Target JD**: `frontend_engineer_jd.txt`
*   **Profile Highlights**: React, Vite, CSS Grid, Flexbox, Tailwind, GitHub workflows, state management.
*   **Expected Results**:
    *   **ATS Score**: **~80/100** (Highly complete baseline profile).
    *   **JD Semantic Match**: **High (~78% - 82%)** against the Frontend React JD.
    *   **Skills Gaps Identified**: Proactively flags missing backend services (such as PostgreSQL or FastAPI) if compared to the AI track.

### 3️⃣ ML Specialist & Researcher (Charlie ML)
*   **Target JD**: `ml_scientist_jd.txt`
*   **Profile Highlights**: Python, Deep Learning, NLP, PyTorch, Transformers, SentenceTransformers, Pandas, Numpy.
*   **Expected Results**:
    *   **ATS Score**: **~80/100** (Clean, highly structured academic profile).
    *   **JD Semantic Match**: **High (~68% - 72%)** against the ML Scientist JD.
    *   **Upskilling Recommendations**: Highlights gaps in web microservices (Docker, FastAPI, Kubernetes) when compared against production system requirements, guiding Charlie ML toward active study paths!

---

## 🚀 How to Test in Under 1 Minute

### Test 1: Single Candidate In-Depth Analysis
1.  Open the Streamlit interface (e.g. `http://localhost:8501` or your live Hugging Face Space URL).
2.  Select **Single Resume** Mode.
3.  Choose **Paste Text** (or convert the sample TXT resumes into PDF and upload them!).
4.  Copy and paste the text from `demo_data/resumes/alice_dev_ai_resume.txt` into the Resume input box.
5.  Copy and paste the text from `demo_data/jds/senior_ai_developer_jd.txt` into the Job Description input box.
6.  Click **Analyze Resume**.
7.  *Watch the platform parse the data instantly, compute the metrics, plot the timelines, map the matching green/red skill gaps, and generate customized study pathway recommendations!*

### Test 2: Bulk Leaderboard Comparison
1.  Select **Bulk Candidate Comparison** Mode.
2.  Upload/paste the three resumes from the `resumes/` folder.
3.  Paste the **Senior AI Developer** Job Description into the JD input box.
4.  Click **Compare Candidates**.
5.  *Watch the platform compute scores, rank all three candidates, and output our premium Recruiter Leaderboard Table (instantly placing Alice Dev at the top with a gold medal 🥇, while Bob Coder and Charlie ML follow with appropriate rankings!).*
