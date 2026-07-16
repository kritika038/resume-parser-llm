"""
AI Resume Intelligence Platform - Main Streamlit Application

Supports both single resume analysis and bulk candidate comparison.
"""

import streamlit as st
import json
import logging
import pandas as pd
from io import BytesIO

# Import service modules
from services.pdf_extractor import extract_pdf
from services.llm_parser import parse_resume, generate_suggestions
from services.ats_scorer import calculate_ats_score, get_ats_interpretation, get_missing_ats_elements
from services.jd_matcher import (
    get_jd_match_interpretation,
    identify_skill_gaps,
    combined_match_score
)
from services.candidate_comparator import CandidateComparator, extract_pdf_from_bytes
from utils.dashboard_components import render_recruiter_dashboard, render_bulk_leaderboard
from services.llm_providers import get_config_value

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== PAGE CONFIGURATION ==========
st.set_page_config(
    page_title="AI Resume Intelligence Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import requests

# ========== DETECT INFERENCE ENVIRONMENT ==========
def detect_env() -> str:
    if "SPACE_ID" in os.environ or get_config_value("SPACE_ID") is not None:
        return "Production (Hugging Face Spaces)"
    elif "RENDER" in os.environ or get_config_value("RENDER") is not None:
        return "Production (Render)"
    elif "RAILWAY_STATIC_URL" in os.environ or get_config_value("RAILWAY_STATIC_URL") is not None:
        return "Production (Railway)"
    elif os.environ.get("STREAMLIT_SERVER_PORT") or os.environ.get("HOSTNAME") == "streamlit":
        return "Production (Streamlit Cloud)"
    else:
        # Check if running inside Streamlit Cloud container by checking common env indicators
        is_sharing = os.environ.get("STREAMLIT_SHARING_ORGANIZATION") or os.environ.get("STREAMLIT_SHARING_USER_REPOS")
        if is_sharing:
            return "Production (Streamlit Cloud)"
        return "Local Development"

# ========== PROVIDER VALIDATION & HEALTH CHECKS ==========
is_hf_space = "SPACE_ID" in os.environ or get_config_value("SPACE_ID") is not None
is_prod = "RENDER" in os.environ or "RAILWAY_STATIC_URL" in os.environ or "PORT" in os.environ or get_config_value("RENDER") is not None or get_config_value("PORT") is not None or detect_env().startswith("Production")
default_provider = "groq" if (is_hf_space or is_prod) else "ollama"
provider = get_config_value("LLM_PROVIDER", default_provider).strip().lower()

# Render System Diagnostics in the sidebar at the top of configuration
st.sidebar.markdown("### 🔌 System Diagnostics")
st.sidebar.write(f"**Environment**: `{detect_env()}`")
st.sidebar.write(f"**Active Provider**: `{provider.upper()}`")
st.sidebar.write(f"**Groq API Key**: `{'Configured' if get_config_value('GROQ_API_KEY') else 'Missing'}`")
st.sidebar.divider()

if provider == "groq":
    groq_key = get_config_value("GROQ_API_KEY")
    if not groq_key:
        st.sidebar.error("⚠️ Groq API Key Missing!")
        st.error("### 🔑 Groq API Key Required")
        st.warning(
            "This application is configured to run cloud-hosted LLM analysis via **Groq**, but no "
            "valid `GROQ_API_KEY` was found in the environment variables or secrets.\n\n"
            "**How to configure on Streamlit Community Cloud / Hugging Face Spaces:**\n"
            "1. Open your Space/App Settings.\n"
            "2. Navigate to the **Secrets** or **Environment variables** tab.\n"
            "3. Add your authorization credentials:\n"
            "   * **Name**: `GROQ_API_KEY`\n"
            "   * **Value**: Your Groq API token (`gsk_...` from [console.groq.com](https://console.groq.com))\n"
            "4. Save and restart."
        )
        st.info("💡 **Local development fallback:** Set the environment variable `LLM_PROVIDER=ollama` to run the app completely offline using local Ollama model instances.")
        st.stop()
    else:
        st.sidebar.success("🟢 Connected to Groq Cloud")
        st.sidebar.caption(f"Active Model: `{get_config_value('GROQ_MODEL', 'llama-3.1-8b-instant')}`")
elif provider == "ollama":
    ollama_base_url = get_config_value("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    # Preserve backward compatibility with OLLAMA_API_URL
    ollama_url = get_config_value("OLLAMA_API_URL", f"{ollama_base_url}/api/generate")
    health_check_url = ollama_url.replace("/api/generate", "/api/tags")
    
    # We perform a health check connection with short timeout to not block UI startup time
    try:
        response = requests.get(health_check_url, timeout=1.5)
        if response.status_code == 200:
            is_local = "localhost" in health_check_url or "127.0.0.1" in health_check_url
            connection_label = "Local Ollama" if is_local else "Remote Ollama"
            st.sidebar.success(f"🟢 Connected to {connection_label}")
            st.sidebar.caption(f"Active Model: `{get_config_value('OLLAMA_MODEL', 'mistral')}`")
        else:
            st.sidebar.warning("⚠️ Ollama Connected (Status Warning)")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        is_local = "localhost" in health_check_url or "127.0.0.1" in health_check_url
        host_label = "Local Ollama" if is_local else "Remote Ollama"
        host_address = "localhost:11434" if is_local else ollama_base_url
        
        st.sidebar.error(f"🔴 {host_label} Offline")
        st.warning(f"### 🖥️ {host_label} Server Offline")
        st.error(
            f"The platform is trying to connect to {host_label.lower()} on `{host_address}` but the service "
            "is unresponsive.\n\n"
            "**If running locally:**\n"
            "Please ensure your Ollama service is active. Run `ollama serve` and verify `ollama list` contains the `mistral` model.\n\n"
            "**If running in the cloud:**\n"
            "Please ensure your remote Ollama server is running and the `OLLAMA_BASE_URL` environment variable is configured correctly.\n\n"
            "**If running in the cloud (Hugging Face Spaces):**\n"
            "Ollama offline models cannot run directly inside a CPU basic Space. You must switch to the **Groq API Cloud Provider**:\n"
            "1. Open your Space **Settings**.\n"
            "2. Under **Variables and secrets**, add a new **Variable**:\n"
            "   * **Name**: `LLM_PROVIDER`\n"
            "   * **Value**: `groq`\n"
            "3. Add a new **Secret**:\n"
            "   * **Name**: `GROQ_API_KEY`\n"
            "   * **Value**: Your Groq API token (`gsk_...` from [console.groq.com](https://console.groq.com))\n"
            "4. Restart the Space."
        )
        st.info("💡 Once environment variables are set in the settings, this application will automatically run the high-speed Groq inference pipeline!")
        st.stop()


# Injected Global Premium CSS for general application polish
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #0052e0 0%, #1D4ED8 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(0, 82, 224, 0.15) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(0, 82, 224, 0.25) !important;
        background: linear-gradient(135deg, #1D4ED8 0%, #0052e0 100%) !important;
    }
    .stDownloadButton>button {
        background-color: transparent !important;
        color: #0052e0 !important;
        border: 1px solid #0052e0 !important;
        border-radius: 12px !important;
        padding: 8px 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100% !important;
    }
    .stDownloadButton>button:hover {
        background-color: rgba(0, 82, 224, 0.05) !important;
        transform: translateY(-1px) !important;
    }
    /* Elegant loader container */
    .stSpinner > div {
        border-top-color: #0052e0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

logo_svg = """
<div style="display: flex; align-items: center; gap: 15px; margin-bottom: 25px; margin-top: 10px;">
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="48" height="48" rx="12" fill="url(#logo_grad)" />
        <path d="M14 18C14 15.7909 15.7909 14 18 14H30C32.2091 14 34 15.7909 34 18V30C34 32.2091 32.2091 34 30 34H18C15.7909 34 14 32.2091 14 30V18Z" stroke="white" stroke-width="2.5" stroke-linejoin="round"/>
        <path d="M20 20H28" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M20 24H28" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M20 28H25" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
        <defs>
            <linearGradient id="logo_grad" x1="0" y1="0" x2="48" y2="48" gradientUnits="userSpaceOnUse">
                <stop stop-color="#0052e0"/>
                <stop offset="1" stop-color="#8b5cf6"/>
            </linearGradient>
        </defs>
    </svg>
    <div>
        <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; line-height: 1.1; background: linear-gradient(135deg, #0052e0 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">RESUME.AI</h1>
        <div style="font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.15em; color: gray; margin-top: 2px;">Enterprise Resume Intelligence</div>
    </div>
</div>
"""

# Header Layout with GitHub Repository & Version Info
col_header_left, col_header_right = st.columns([3, 1])
with col_header_left:
    st.markdown(logo_svg, unsafe_allow_html=True)
with col_header_right:
    st.markdown(
        """
        <div style="text-align: right; margin-top: 15px;">
            <a href="https://github.com/kritika038/resume-parser-llm" target="_blank" style="text-decoration: none; color: inherit;">
                <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub Repo" />
            </a>
            <div style="font-size: 0.82rem; font-weight: 600; opacity: 0.7; margin-top: 5px;">Version 1.0.0</div>
        </div>
        """,
        unsafe_allow_html=True
    )
st.caption("Enterprise-Grade AI-Powered ATS Matching, Semantic Resume Parsing & Candidate Intelligence")

# ========== MODE SELECTION ==========
mode = st.radio(
    "📌 Select Analysis Mode:",
    ["Single Resume", "Bulk Candidate Comparison"],
    horizontal=True,
    key="analysis_mode"
)

# ========== SIDEBAR CONFIGURATION ==========
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    Supports both:
    - **Local inference**: Ollama (Mistral/Llama) for data privacy.
    - **Cloud inference**: Groq (Llama-3) for high-speed analysis.

    *The deployed demo is currently powered by Groq.*
    
    **Core Features**:
    - **ATS Score**: Compatibility assessment.
    - **JD Alignment**: Semantic Cosine Matching.
    - **Skill Gaps**: Actionable recommendations.
    """)
    
    st.divider()
    st.header("⚙️ Configuration")
    show_raw_response = st.checkbox("Show Debug Panel", value=False)

# ========== SINGLE RESUME MODE ==========
if mode == "Single Resume":
    st.header("📥 Single Resume Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Resume Source")
        input_method = st.radio(
            "Choose input method:",
            ["Upload PDF", "Paste Text"],
            key="input_method"
        )
        
        uploaded_file = None
        resume_text = ""
        
        if input_method == "Upload PDF":
            uploaded_file = st.file_uploader(
                "📄 Upload Resume (PDF)",
                type=["pdf"],
                help="Supported: PDF | Max Size: 200 MB"
            )
        else:
            resume_text = st.text_area(
                "Paste your resume text here",
                height=250,
                placeholder="Copy and paste your resume content...",
                key="single_resume_text"
            )
    
    with col2:
        st.subheader("Job Description (Optional)")
        
        # Load Sample JD button logic for single resume mode
        if st.button("📋 Load Sample JD", key="load_sample_jd_single_btn", use_container_width=True):
            st.session_state["single_jd_text"] = (
                "Role: AI/ML Engineer\n"
                "Requirements:\n"
                "- Strong experience in Python, PyTorch/TensorFlow, and Scikit-Learn.\n"
                "- Hands-on experience building and deploying Large Language Models (LLMs) and RAG systems.\n"
                "- Proficiency with vector databases (e.g. Qdrant, ChromaDB) and semantic search architectures.\n"
                "- Experience building REST APIs using FastAPI or Flask.\n"
                "- Containerization using Docker and orchestration tools (Kubernetes, Docker Compose).\n"
                "- Familiarity with MLOps pipelines, model profiling, and deployment on AWS/GCP."
            )
            st.rerun()

        jd_text = st.text_area(
            "Paste job description for skill matching",
            height=250,
            placeholder="Paste job description to enable JD matching...",
            key="single_jd_text"
        )
    
    # ========== SINGLE RESUME PROCESSING ==========
    if st.button("🔍 Analyze Resume", use_container_width=True, key="analyze_single"):
        try:
            # Get resume text from appropriate source
            if input_method == "Upload PDF":
                if not uploaded_file:
                    st.error("❌ Please upload a PDF resume file before clicking 'Analyze Resume'.")
                    st.stop()
                with st.spinner("📄 Extracting text from PDF..."):
                    resume_text = extract_pdf(uploaded_file)
                    if not resume_text:
                        st.error("❌ PDF extraction failed. The uploaded file is either password-protected, encrypted, or corrupted. Please upload a valid text-based PDF.")
                        st.stop()
            
            # Validate resume input
            if not resume_text or not resume_text.strip():
                st.error("❌ Please provide resume input.")
                st.stop()
            
            if show_raw_response:
                with st.expander("📋 Raw Resume Text"):
                    st.text(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)
            
            # Parse resume
            with st.spinner("🧠 Parsing resume with AI..."):
                parsed_data = parse_resume(resume_text)
            
            if not parsed_data:
                st.error("❌ AI Parsing Failed")
                st.info("""
                **Troubleshooting Guide:**
                1. **If using Groq Cloud**: Ensure your `GROQ_API_KEY` environment secret is valid and not rate-limited.
                2. **If using Local Ollama**: Ensure Ollama is active locally (`ollama serve`) and the `mistral` model is pulled (`ollama pull mistral`).
                3. Ensure the uploaded resume contains readable, copy-pasteable English text.
                """)
                st.stop()
            # Calculate metrics
            with st.spinner("📊 Calculating scores..."):
                ats_score = calculate_ats_score(parsed_data)
                
                if jd_text and jd_text.strip():
                    combined_score, matched_skills, match_details = combined_match_score(
                        parsed_data.get("skills", {}),
                        resume_text,
                        jd_text,
                        keyword_weight=0.4,
                        semantic_weight=0.6
                    )
                    jd_match_score = combined_score
                    keyword_match_score = match_details.get("keyword_score", 0)
                    semantic_match_score = match_details.get("semantic_score", 0)
                else:
                    jd_match_score = 0
                    keyword_match_score = 0
                    semantic_match_score = 0
                    matched_skills = []
                
                skill_gaps = identify_skill_gaps(parsed_data.get("skills", {}), jd_text) if jd_text else []
            
            # Generate suggestions
            with st.spinner("💡 Generating recommendations..."):
                suggestions = generate_suggestions(parsed_data, jd_text)
            
            st.success("✅ Resume analysis complete!")
            st.divider()
            
            # ========== RESULTS DISPLAY ==========
            st.header("📊 Analysis Results")
            
            # Results Tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "💼 Recruiter Dashboard",
                "📈 Detailed Scores & Gaps",
                "📄 Full JSON",
                "💡 AI Suggestions",
                "⬇️ Export"
            ])
            
            with tab1:
                match_details = {
                    "keyword_score": keyword_match_score,
                    "semantic_similarity": semantic_match_score / 100.0 if semantic_match_score else 0.0,
                    "matched_skills": matched_skills
                }
                render_recruiter_dashboard(
                    parsed_data=parsed_data,
                    ats_score=ats_score,
                    jd_match_score=jd_match_score,
                    match_details=match_details,
                    skill_gaps=skill_gaps,
                    resume_text=resume_text,
                    jd_text=jd_text
                )
            
            with tab2:
                col_l, col_r = st.columns([1, 1])
                
                with col_l:
                    st.subheader("ATS Compatibility")
                    st.write(f"**Score:** {ats_score}/100")
                    st.write(f"**Assessment:** {get_ats_interpretation(ats_score)}")
                    
                    missing = get_missing_ats_elements(parsed_data)
                    if missing:
                        st.warning("Missing elements:")
                        for item in missing:
                            st.write(f"• {item}")
                    else:
                        st.success("All elements present!")
                
                with col_r:
                    if jd_text:
                        st.subheader("Job Description Match")
                        st.write(f"**Combined:** {jd_match_score}%")
                        st.write(f"**Assessment:** {get_jd_match_interpretation(jd_match_score)}")
                        
                        st.divider()
                        col_s1, col_s2 = st.columns(2)
                        with col_s1:
                            st.metric("Keyword", f"{keyword_match_score}%")
                        with col_s2:
                            st.metric("Semantic", f"{semantic_match_score}%")
                        
                        if matched_skills:
                            st.success(f"**Matched ({len(matched_skills)}):** {', '.join(matched_skills)}")
                        
                        if skill_gaps:
                            st.warning(f"**Gaps ({len(skill_gaps)}):** {', '.join(skill_gaps)}")
                    else:
                        st.info("💡 Provide a JD for skill matching")
            
            with tab3:
                st.json(parsed_data)
            
            with tab4:
                if suggestions:
                    st.write(suggestions)
                else:
                    st.warning("Could not generate suggestions.")
            
            with tab5:
                json_str = json.dumps(parsed_data, indent=2)
                st.download_button(
                    "📥 JSON",
                    data=json_str,
                    file_name=f"resume_{parsed_data.get('name', 'candidate')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                
            # If Show Debug Panel is checked, show debug metrics & panels
            if show_raw_response:
                st.divider()
                st.subheader("🕵️‍♂️ Debug Panel")
                
                # 1. Raw Resume Text
                with st.expander("📄 Raw Resume Text", expanded=False):
                    if resume_text:
                        st.text_area("Raw Resume Text Content", value=resume_text, height=300, disabled=True)
                    else:
                        st.info("No raw resume text available.")
                        
                # 2. Extracted JSON
                with st.expander("🤖 Extracted JSON", expanded=False):
                    raw_output = st.session_state.get("raw_llm_response")
                    if raw_output:
                        st.code(raw_output, language="json")
                    else:
                        st.info("No raw LLM JSON response found.")
                        
                # 3. Rendered Dashboard Data
                with st.expander("📊 Rendered Dashboard Data", expanded=False):
                    if parsed_data:
                        st.markdown("**Cleaned & Validated Candidate JSON:**")
                        st.json(parsed_data)
                    else:
                        st.markdown("*No verified parsed candidate data.*")
                        
                    ats_breakdown = st.session_state.get("ats_breakdown")
                    if ats_breakdown:
                        st.markdown("**ATS Scoring Breakdown:**")
                        # Render metrics in two rows of 4 columns
                        items = list(ats_breakdown.items())
                        col_row1 = st.columns(4)
                        for col, (metric_name, metric_val) in zip(col_row1, items[:4]):
                            col.metric(label=metric_name, value=metric_val)
                        col_row2 = st.columns(4)
                        for col, (metric_name, metric_val) in zip(col_row2, items[4:]):
                            col.metric(label=metric_name, value=metric_val)
                    else:
                        st.info("No ATS score calculation details found.")
        except Exception as e:
            logger.error(f"Critical single resume processing exception: {e}", exc_info=True)
            st.error("❌ A Critical Processing Error Occurred")
            st.warning(f"Error Details: {str(e)}")
            st.info("Please verify your inputs, check platform environment logs, and try again.")
            st.stop()

# ========== BULK CANDIDATE COMPARISON MODE ==========
else:
    st.header("📊 Bulk Candidate Comparison")
    st.markdown("Upload multiple resumes and rank them against one job description.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Job Description (Required)")
        
        # Load Sample JD button logic for bulk mode
        if st.button("📋 Load Sample JD", key="load_sample_jd_bulk_btn", use_container_width=True):
            st.session_state["jd_bulk_text"] = (
                "Role: AI/ML Engineer\n"
                "Requirements:\n"
                "- Strong experience in Python, PyTorch/TensorFlow, and Scikit-Learn.\n"
                "- Hands-on experience building and deploying Large Language Models (LLMs) and RAG systems.\n"
                "- Proficiency with vector databases (e.g. Qdrant, ChromaDB) and semantic search architectures.\n"
                "- Experience building REST APIs using FastAPI or Flask.\n"
                "- Containerization using Docker and orchestration tools (Kubernetes, Docker Compose).\n"
                "- Familiarity with MLOps pipelines, model profiling, and deployment on AWS/GCP."
            )
            st.rerun()

        jd_bulk = st.text_area(
            "Paste the job description",
            height=200,
            placeholder="Paste job description to compare candidates...",
            key="jd_bulk_text"
        )
    
    with col2:
        st.subheader("📊 Ranking By")
        sort_option = st.selectbox(
            "Sort by:",
            ["Overall Score", "ATS Score", "JD Match", "Semantic Similarity"],
            key="sort_by_bulk"
        )
    
    st.divider()
    
    st.subheader("📄 Upload Resumes")
    use_demo = st.checkbox("💡 Preload Demo Resumes (Alice Dev, Bob Coder, Charlie ML)", value=True, key="use_demo_resumes")
    
    uploaded_files = None
    if not use_demo:
        uploaded_files = st.file_uploader(
            "Select PDF resumes (multiple allowed)",
            type=["pdf"],
            accept_multiple_files=True,
            key="bulk_resume_upload"
        )
    else:
        st.info("⚡ Demo mode active: Three highly representative candidate resumes (Alice Dev, Bob Coder, and Charlie ML) have been preloaded for comparison against your JD!")
    
    # ========== BULK PROCESSING ==========
    if st.button("🔍 Analyze & Compare", use_container_width=True, key="analyze_bulk"):
        try:
            if not jd_bulk or not jd_bulk.strip():
                st.error("❌ Please provide a job description")
                st.stop()
            
            if not use_demo and not uploaded_files:
                st.error("❌ Please upload at least one resume")
                st.stop()
            
            # Initialize comparator
            comparator = CandidateComparator()
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            successful = 0
            failed = 0
            
            # Determine files to process
            files_to_process = []
            if use_demo:
                files_to_process = [
                    {"name": "Alice_Dev.pdf", "path": "scratch/Alice_Dev.pdf"},
                    {"name": "Bob_Coder.pdf", "path": "scratch/Bob_Coder.pdf"},
                    {"name": "Charlie_ML.pdf", "path": "scratch/Charlie_ML.pdf"}
                ]
            else:
                files_to_process = [{"name": f.name, "file": f} for f in uploaded_files]
            
            # Process each resume
            for idx, item in enumerate(files_to_process):
                status_text.text(f"Processing: {item['name']} ({idx + 1}/{len(files_to_process)})")
                
                try:
                    if use_demo:
                        with open(item["path"], "rb") as f:
                            pdf_bytes = f.read()
                    else:
                        pdf_bytes = item["file"].read()
                        
                    candidate_id = f"candidate_{idx + 1}"
                    candidate_name = item["name"].replace(".pdf", "").replace("_", " ")
                    
                    comparator.add_pdf_resume(
                        candidate_id,
                        pdf_bytes,
                        jd_bulk,
                        candidate_name=candidate_name
                    )
                    successful += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {item['name']}: {e}")
                    failed += 1
                    st.warning(f"⚠️ Failed: {item['name']}")
                
                progress_bar.progress((idx + 1) / len(files_to_process))
            
            status_text.text(f"✅ Processed: {successful}, Failed: {failed}")
            
            if successful == 0:
                st.error("❌ No resumes successfully processed")
                st.stop()
            
            st.success(f"✅ Analyzed {successful} candidate(s)")
            st.divider()
            
            # ========== RESULTS DISPLAY ==========
            st.header("📊 Candidate Rankings")
            
            # Map sort option to key
            sort_map = {
                "Overall Score": "overall",
                "ATS Score": "ats",
                "JD Match": "jd_match",
                "Semantic Similarity": "semantic"
            }
            sort_key = sort_map[sort_option]
            
            # Get ranked candidates
            ranked_candidates = comparator.get_ranked_candidates(sort_by=sort_key)
            
            # Render gorgeous visual leaderboard
            render_bulk_leaderboard(ranked_candidates)
            
            st.divider()
            
            # ========== DETAILED ANALYSIS ==========
            st.header("📋 Detailed Candidate Analysis")
            
            ranked_candidates = comparator.get_ranked_candidates(sort_by=sort_key)
            
            for rank, candidate in enumerate(ranked_candidates, 1):
                with st.expander(
                    f"🏆 #{rank}: {candidate.name} "
                    f"(Overall: {candidate.overall_score:.1f})",
                    expanded=(rank == 1)
                ):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Overall", f"{candidate.overall_score:.1f}")
                    with col2:
                        st.metric("ATS", f"{candidate.ats_score}/100")
                    with col3:
                        st.metric("JD Match", f"{candidate.combined_jd_match}%")
                    with col4:
                        st.metric("Semantic", f"{int(candidate.semantic_match * 100)}%")
                    
                    st.divider()
                    
                    col_info, col_score = st.columns(2)
                    
                    with col_info:
                        st.write(f"**Email:** {candidate.email}")
                        st.write(f"**Total Skills:** {candidate.total_skills}")
                        st.write(f"**Matched:** {len(candidate.matched_skills)}")
                    
                    with col_score:
                        st.write(f"**Keyword:** {candidate.keyword_match}%")
                        st.write(f"**Semantic:** {candidate.semantic_match:.2%}")
                        st.write(f"**ATS:** {get_ats_interpretation(candidate.ats_score)}")
                    
                    st.divider()
                    
                    col_skills, col_gaps = st.columns(2)
                    
                    with col_skills:
                        st.write("**✅ Matched Skills:**")
                        st.write(", ".join(candidate.matched_skills) if candidate.matched_skills else "None")
                    
                    with col_gaps:
                        st.write("**❌ Skill Gaps:**")
                        st.write(", ".join(candidate.skill_gaps) if candidate.skill_gaps else "None")
            
            st.divider()
            
            # ========== EXPORT OPTIONS ==========
            st.header("⬇️ Export Results")
            
            col_j, col_c = st.columns(2)
            
            with col_j:
                json_export = comparator.export_results(format="json")
                st.download_button(
                    "📥 Download JSON",
                    data=json_export,
                    file_name="candidates.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_c:
                csv_export = comparator.export_results(format="csv")
                st.download_button(
                    "📊 Download CSV",
                    data=csv_export,
                    file_name="candidates.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        except Exception as e:
            logger.error(f"Critical bulk comparison exception: {e}", exc_info=True)
            st.error("❌ A Critical Bulk Processing Error Occurred")
            st.warning(f"Error Details: {str(e)}")
            st.info("Please verify your inputs, check platform environment logs, and try again.")
            st.stop()

# ========== FOOTER ==========
st.divider()
st.markdown(
    """
    <div style="text-align: center; font-size: 0.82rem; opacity: 0.7; padding: 15px 0;">
        Built with Python | Streamlit | SentenceTransformers | Ollama | Groq
    </div>
    """,
    unsafe_allow_html=True
)
