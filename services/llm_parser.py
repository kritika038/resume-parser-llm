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
    Programmatically builds a strictly factual executive summary based on verified parsed details,
    completely bypassing the LLM to prevent subjective recruiter language and hallucinations.
    """
    if not parsed_data or not isinstance(parsed_data, dict):
        return "No candidate data available."
    
    name = parsed_data.get("name")
    if not name or name == "N/A":
        name = "The candidate"
        
    parts = []
    
    # 1. Employment and Internship Experience
    employment = parsed_data.get("employment", [])
    internships = parsed_data.get("internships", [])
    
    experience_phrases = []
    if employment and isinstance(employment, list):
        for emp in employment[:2]:
            role = emp.get("role", "N/A")
            company = emp.get("company", "N/A")
            duration = emp.get("duration", "N/A")
            if role != "N/A" and company != "N/A":
                dur_str = f" for {duration}" if (duration and duration != "N/A") else ""
                experience_phrases.append(f"worked as a {role} at {company}{dur_str}")
            elif role != "N/A":
                experience_phrases.append(f"worked as a {role}")
            elif company != "N/A":
                experience_phrases.append(f"worked at {company}")

    if internships and isinstance(internships, list):
        for item in internships[:2]:
            role = item.get("role", "N/A")
            company = item.get("company", "N/A")
            duration = item.get("duration", "N/A")
            if role != "N/A" and company != "N/A":
                dur_str = f" for {duration}" if (duration and duration != "N/A") else ""
                experience_phrases.append(f"completed an internship as a {role} at {company}{dur_str}")
            elif role != "N/A":
                experience_phrases.append(f"completed a {role} internship")
            elif company != "N/A":
                experience_phrases.append(f"completed an internship at {company}")

    if experience_phrases:
        if len(experience_phrases) == 1:
            parts.append(f"{name} has {experience_phrases[0]}.")
        else:
            parts.append(f"{name} has {experience_phrases[0]} and {experience_phrases[1]}.")
            
    # 2. Education
    education = parsed_data.get("education", [])
    edu_phrases = []
    if education and isinstance(education, list):
        for edu in education[:2]:
            degree = edu.get("degree", "N/A")
            field = edu.get("field", "N/A")
            institution = edu.get("institution", "N/A")
            
            deg_field = ""
            if degree != "N/A" and field != "N/A":
                deg_field = f"{degree} in {field}"
            elif degree != "N/A":
                deg_field = degree
            elif field != "N/A":
                deg_field = f"degree in {field}"
                
            if deg_field and institution != "N/A":
                edu_phrases.append(f"a {deg_field} from {institution}")
            elif deg_field:
                edu_phrases.append(f"a {deg_field}")
            elif institution != "N/A":
                edu_phrases.append(f"studies at {institution}")
                
    if edu_phrases:
        if len(edu_phrases) == 1:
            parts.append(f"Their education includes {edu_phrases[0]}.")
        else:
            parts.append(f"Their education includes {edu_phrases[0]} and {edu_phrases[1]}.")
            
    # 3. Skills
    skills = parsed_data.get("skills", [])
    flat_skills = []
    if isinstance(skills, list):
        flat_skills = [s for s in skills if s and s != "N/A"]
    elif isinstance(skills, dict):
        for val in skills.values():
            if isinstance(val, list):
                flat_skills.extend([s for s in val if s and s != "N/A"])
                
    if flat_skills:
        # deduplicate while keeping order
        seen = set()
        deduped_skills = []
        for s in flat_skills:
            s_lower = s.lower()
            if s_lower not in seen:
                seen.add(s_lower)
                deduped_skills.append(s)
        skills_str = ", ".join(deduped_skills[:8])
        parts.append(f"Listed skills include: {skills_str}.")
        
    # 4. Projects
    projects = parsed_data.get("projects", [])
    proj_names = []
    if projects and isinstance(projects, list):
        for proj in projects[:2]:
            p_name = proj.get("name", "N/A")
            if p_name != "N/A":
                proj_names.append(p_name)
    if proj_names:
        if len(proj_names) == 1:
            parts.append(f"Completed projects include {proj_names[0]}.")
        else:
            parts.append(f"Completed projects include {', and '.join(proj_names)}.")
        
    if not parts:
        return f"Resume data parsed for {name} with no specific employment, education, or skills listed."
        
    return " ".join(parts)

