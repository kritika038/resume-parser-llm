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

# ========== PROVIDER VALIDATION & HEALTH CHECKS ==========
provider = os.environ.get("LLM_PROVIDER", "ollama").strip().lower()

if provider == "groq":
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        st.sidebar.error("⚠️ Groq API Key Missing!")
        st.error("### 🔑 Groq API Key Required")
        st.warning(
            "This space is configured to run cloud-hosted LLM analysis via **Groq**, but no "
            "valid `GROQ_API_KEY` was found in the environment secrets.\n\n"
            "**How to configure on Hugging Face Spaces:**\n"
            "1. Open your Space **Settings**.\n"
            "2. Scroll down to the **Variables and secrets** section.\n"
            "3. Click **New secret** to add your authorization credentials:\n"
            "   * **Name**: `GROQ_API_KEY`\n"
            "   * **Value**: Your Groq API token (`gsk_...` from [console.groq.com](https://console.groq.com))\n"
            "4. Click **Save** and restart the Space."
        )
        st.info("💡 **Local development fallback:** Set the environment variable `LLM_PROVIDER=ollama` to run the app completely offline using local Ollama model instances.")
        st.stop()
    else:
        st.sidebar.success("🟢 Connected to Groq Cloud")
        st.sidebar.caption(f"Active Model: `{os.environ.get('GROQ_MODEL', 'llama3-8b-8192')}`")
elif provider == "ollama":
    ollama_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    try:
        # Quick health check connection to Ollama server
        health_check_url = ollama_url.replace("/api/generate", "/api/tags")
        response = requests.get(health_check_url, timeout=1)
        if response.status_code == 200:
            st.sidebar.success("🟢 Connected to Local Ollama")
            st.sidebar.caption(f"Active Model: `{os.environ.get('OLLAMA_MODEL', 'mistral')}`")
        else:
            st.sidebar.warning("⚠️ Ollama Connected (Status Warning)")
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        st.sidebar.error("🔴 Local Ollama Offline")
        st.warning("### 🖥️ Local Ollama Server Offline")
        st.error(
            "The platform is trying to connect to local Ollama on `localhost:11434` but the service "
            "is unresponsive.\n\n"
            "**If running locally:**\n"
            "Please ensure your Ollama service is active. Run `ollama serve` and verify `ollama list` contains the `mistral` model.\n\n"
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

st.title("🚀 AI Resume Intelligence Platform")
st.caption("Enterprise-Grade Resume Analysis using Advanced LLM Technology")

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
    This platform uses **Mistral LLM** (via Ollama) to:
    - Extract structured resume data
    - Calculate ATS compatibility
    - Match skills to job requirements
    - Generate AI recommendations
    - Compare multiple candidates
    
    **Privacy First:** All processing is local. No data leaves your machine.
    """)
    
    st.divider()
    st.header("⚙️ Configuration")
    show_debug = st.checkbox("Show Debug Information", value=False)

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
            uploaded_file = st.file_uploader("Select PDF resume", type=["pdf"])
        else:
            resume_text = st.text_area(
                "Paste your resume text here",
                height=250,
                placeholder="Copy and paste your resume content...",
                key="single_resume_text"
            )
    
    with col2:
        st.subheader("Job Description (Optional)")
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
            
            if show_debug:
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
with st.expander("ℹ️ About This Platform"):
    st.markdown("""
    ### 🚀 AI Resume Intelligence Platform
    
    **Modes:**
    - **Single Resume:** Detailed analysis with ATS, JD matching, and suggestions
    - **Bulk Comparison:** Compare multiple candidates, rank by multiple metrics
    
    **Scoring Metrics:**
    - **ATS Score (0-100):** Applicant Tracking System compatibility
    - **Keyword Match (0-100%):** Exact skill overlap with JD
    - **Semantic Similarity (0-100%):** Conceptual alignment with JD
    - **Overall Score:** Weighted combination for final ranking
    
    **Technology:**
    - Mistral LLM (via Ollama) for resume parsing
    - SentenceTransformers for semantic analysis
    - Streamlit for interactive UI
    - All processing is local - no cloud uploads
    
    **Features:**
    - 🧠 LLM-powered extraction
    - 🔐 100% local processing
    - 📊 Multi-dimensional scoring
    - 🎯 Semantic job matching
    - 📋 Bulk comparison
    - ⬇️ JSON/CSV export
    """)
