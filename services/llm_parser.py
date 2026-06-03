"""
LLM-based resume parsing service.
Handles communication with Ollama Mistral model and JSON output processing.
"""

import requests
import logging
from typing import Optional, Dict, Any

from utils.validators import clean_json, validate_resume_schema, clean_and_validate_resume
from utils.prompts import PARSE_PROMPT, SUGGEST_PROMPT

logger = logging.getLogger(__name__)

from services.llm_providers import get_llm_provider, OllamaProvider, GroqProvider
import os


def call_llm(prompt: str) -> Optional[str]:
    """
    Sends prompt to the active LLM provider (Ollama or Groq) with automatic failover.
    
    If the primary provider fails, it dynamically resolves the alternate provider 
    (Ollama offline fallback or Groq cloud upgrade) to ensure maximum operational uptime.
    
    Args:
        prompt: Complete prompt with task context and schema guidelines
        
    Returns:
        str: Raw LLM completion text
        None: If both primary and fallback providers fail
    """
    is_hf_space = "SPACE_ID" in os.environ
    default_provider = "groq" if is_hf_space else "ollama"
    primary_provider_name = os.environ.get("LLM_PROVIDER", default_provider).strip().lower()
    
    # 1. Attempt Primary provider execution
    try:
        provider = get_llm_provider()
        logger.info(f"Attempting inference via primary provider: {primary_provider_name.upper()}")
        result = provider.generate(prompt)
        if result and result.strip():
            return result
        logger.warning(f"Primary provider {primary_provider_name.upper()} returned empty completion.")
    except Exception as e:
        logger.error(f"Primary provider {primary_provider_name.upper()} execution failed: {e}")
        
    # 2. Automated Failover Channel
    fallback_provider = None
    fallback_name = ""
    
    if primary_provider_name == "groq":
        logger.warning("Groq Cloud API unreachable or failed. Initiating AUTOMATIC LOCAL OLLAMA FAILOVER...")
        fallback_provider = OllamaProvider()
        fallback_name = "OLLAMA (LOCAL)"
    else:
        # Fall back to Groq only if API key is provided
        if os.environ.get("GROQ_API_KEY"):
            logger.warning("Local Ollama endpoint unreachable. Initiating AUTOMATIC CLOUD GROQ FAILOVER...")
            fallback_provider = GroqProvider()
            fallback_name = "GROQ (CLOUD)"
        else:
            logger.warning("Local Ollama failed but GROQ_API_KEY is not configured. Failover skipped.")
            
    if fallback_provider:
        try:
            logger.info(f"Attempting failover inference via: {fallback_name}")
            result = fallback_provider.generate(prompt)
            if result and result.strip():
                logger.info(f"✅ Failover successful via {fallback_name}!")
                return result
        except Exception as e:
            logger.error(f"Fallback provider {fallback_name} also failed: {e}")
            
    logger.error("❌ Both primary and fallback LLM providers failed to generate completion.")
    return None


def parse_resume(resume_text: str) -> Optional[Dict[str, Any]]:
    """
    Parses resume text using LLM and returns structured JSON.
    
    Complete pipeline:
    1. Send resume + schema prompt to Mistral
    2. Get raw output (may contain markdown artifacts)
    3. Clean and validate JSON
    4. Validate against resume schema
    
    Args:
        resume_text: Plain text resume content
        
    Returns:
        dict: Structured resume data following schema
        None: If parsing fails at any step
    """
    if not resume_text or not resume_text.strip():
        logger.warning("Empty resume text provided")
        return None
    
    # Build complete prompt
    full_prompt = f"{PARSE_PROMPT}\n\nResume:\n{resume_text}"
    
    # Call LLM
    logger.info("Sending resume to LLM for parsing...")
    raw_output = call_llm(full_prompt)
    
    # Capture raw output & initialize parsing error in session state
    import streamlit as st
    st.session_state["raw_llm_response"] = raw_output or "No output received from LLM."
    st.session_state["parsing_error"] = ""
    
    if not raw_output:
        logger.error("No output received from LLM")
        st.session_state["parsing_error"] = "No output received from LLM provider (check connectivity or rate limits)."
        return None
    
    # Clean JSON
    logger.info("Cleaning and validating JSON output...")
    parsed = clean_json(raw_output)
    
    if not parsed:
        logger.error("Failed to parse JSON from LLM output")
        logger.debug(f"Raw output: {raw_output[:300]}...")
        st.session_state["parsing_error"] = "Failed to parse JSON from LLM output. The raw response was not valid JSON."
        return None
    
    # Clean and validate against factual extraction rules
    parsed = clean_and_validate_resume(parsed, resume_text)
    
    logger.info("Resume successfully parsed, validated, and filtered for factual alignment")
    return parsed


def generate_suggestions(resume_data: Dict[str, Any], jd_text: Optional[str] = None) -> Optional[str]:
    """
    Generates AI-based resume improvement suggestions.
    
    Args:
        resume_data: Parsed resume dictionary
        jd_text: Optional job description for context
        
    Returns:
        str: AI-generated suggestions
        None: If generation fails
    """
    if not resume_data:
        logger.warning("No resume data provided for suggestions")
        return None
    
    import json
    
    # Build context
    context = f"{SUGGEST_PROMPT}\n\nResume:\n{json.dumps(resume_data, indent=2)}"
    
    if jd_text:
        context += f"\n\nJob Description:\n{jd_text}"
    
    logger.info("Generating suggestions from LLM...")
    suggestions = call_llm(context)
    
    if suggestions:
        logger.info("Suggestions generated successfully")
    else:
        logger.warning("Failed to generate suggestions")
    
    return suggestions


def generate_recruiter_summary(parsed_data: Dict[str, Any]) -> str:
    """
    Generates a concise, professional 2-3 sentence recruiter executive summary of the candidate.
    
    Tries to generate utilizing the LLM first, falling back to a structured summary 
    based on experience and skills if the LLM is unreachable or fails.
    
    Args:
        parsed_data: Parsed resume dictionary
        
    Returns:
        str: Recruiter executive summary of the candidate
    """
    if not parsed_data or not isinstance(parsed_data, dict):
        logger.warning("No candidate data available for summary")
        return "No candidate data available."
    
    employment_list = parsed_data.get("employment", [])
    internship_list = parsed_data.get("internships", [])
    skills = parsed_data.get("skills", [])
    name = parsed_data.get("name", "The Candidate")
    
    # 1. Structured fallback function to ensure visual resilience
    def get_structured_fallback():
        flat_skills = []
        if isinstance(skills, list):
            flat_skills = skills
        elif isinstance(skills, dict):
            for skill_list in skills.values():
                if isinstance(skill_list, list):
                    flat_skills.extend(skill_list)
        
        top_skills = ", ".join(flat_skills[:6]) if flat_skills else "software development"
        
        if employment_list and isinstance(employment_list, list) and len(employment_list) > 0:
            latest = employment_list[0]
            role = latest.get("role", "Professional")
            company = latest.get("company", "leading organization")
            duration = latest.get("duration", "")
            time_phrase = f" ({duration})" if (duration and duration != "N/A") else ""
            
            return f"{name} is a professional who most recently served as a {role} at {company}{time_phrase}. They possess key strengths in {top_skills}."
        elif internship_list and isinstance(internship_list, list) and len(internship_list) > 0:
            latest = internship_list[0]
            role = latest.get("role", "Intern")
            company = latest.get("company", "organization")
            duration = latest.get("duration", "")
            time_phrase = f" ({duration})" if (duration and duration != "N/A") else ""
            
            return f"{name} has internship experience as a {role} at {company}{time_phrase}, with key strengths in {top_skills}."
        else:
            return f"{name} is a candidate with experience specializing in {top_skills}."

    # 2. Try LLM summary generation
    import json
    prompt = f"""
    You are a factual resume summarizer.
    Analyze the following candidate's parsed resume data and generate a concise, cohesive 2-3 sentence Recruiter Executive Summary.
    
    STRICT RULES:
    - The summary must be strictly factual and grounded ONLY in the provided resume data.
    - Never include subjective praise, puffery, or fabricated claims (e.g. do NOT write "highly skilled AI specialist" or "expert" unless explicitly in the text).
    - If the candidate is a student or has internship-only experience, present them accurately as such (e.g., "Student with internship experience in...").
    - Only mention specific technologies, projects, and roles explicitly listed in the provided data.
    - Keep it under 3 sentences.
    - Do NOT include any markdown formatting, bullet points, greetings, introductory filler, or surrounding quotes.
    - Output only the plain text summary.
    
    Candidate Name: {name}
    Skills: {json.dumps(skills)}
    Employment: {json.dumps(employment_list[:3])}
    Internships: {json.dumps(internship_list[:3])}
    Projects: {json.dumps(parsed_data.get('projects', [])[:3])}
    """
    
    logger.info("Requesting LLM-generated recruiter executive summary...")
    raw_summary = call_llm(prompt)
    
    if raw_summary and raw_summary.strip():
        clean_sum = raw_summary.strip().replace('"', '').replace('**', '').replace('Executive Summary:', '')
        # Basic bounds-checking to filter out system responses
        if len(clean_sum) > 20 and not clean_sum.lower().startswith("here is"):
            logger.info("Recruiter summary generated successfully via LLM")
            return clean_sum
            
    logger.warning("LLM summary generation unavailable or invalid; using high-quality structured fallback.")
    return get_structured_fallback()

