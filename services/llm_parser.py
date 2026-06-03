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
    Programmatically constructs a Candidate Snapshot from verified extracted JSON fields.
    This replaces any AI-generated recruiter summary.
    """
    if not parsed_data or not isinstance(parsed_data, dict):
        return "No candidate data available."
        
    html_parts = []
    
    # Helper for lists
    def make_html_list(title: str, items: list) -> str:
        part = f"<div style='margin-bottom: 12px;'><strong>{title}:</strong><ul style='margin: 4px 0 0 20px; padding: 0; list-style-type: disc;'>"
        if items:
            for item in items:
                part += f"<li style='margin-bottom: 2px;'>{item}</li>"
        else:
            part += "<li style='margin-bottom: 2px;'>Not Found</li>"
        part += "</ul></div>"
        return part

    # 1. Education
    edu_items = []
    edu_list = parsed_data.get("education", [])
    if edu_list and isinstance(edu_list, list):
        for edu in edu_list:
            degree = edu.get("degree") or "Not Found"
            field = edu.get("field") or "Not Found"
            inst = edu.get("institution") or "Not Found"
            year = edu.get("year") or "Not Found"
            
            deg_field = f"{degree} in {field}" if (degree != "Not Found" and field != "Not Found") else (degree if degree != "Not Found" else field)
            edu_str = f"{deg_field} at {inst}" if inst != "Not Found" else deg_field
            if year != "Not Found":
                edu_str += f" ({year})"
            if edu_str != "Not Found":
                edu_items.append(edu_str)
            
    html_parts.append(make_html_list("Education", edu_items))

    # 2. Internships
    int_items = []
    internships = parsed_data.get("internships", [])
    if internships and isinstance(internships, list):
        for item in internships:
            role = item.get("role") or "Not Found"
            comp = item.get("company") or "Not Found"
            dur = item.get("duration") or "Not Found"
            
            int_str = f"{role} at {comp}" if (role != "Not Found" and comp != "Not Found") else (role if role != "Not Found" else comp)
            if dur != "Not Found":
                int_str += f" ({dur})"
            if int_str != "Not Found":
                int_items.append(int_str)
            
    html_parts.append(make_html_list("Internships", int_items))

    # 3. Projects
    proj_items = []
    projects = parsed_data.get("projects", [])
    if projects and isinstance(projects, list):
        for item in projects:
            name = item.get("name") or "Not Found"
            tech = item.get("tech_stack", [])
            
            proj_str = name
            if isinstance(tech, list) and tech:
                proj_str += f" (Tech: {', '.join(tech)})"
            if proj_str != "Not Found":
                proj_items.append(proj_str)
            
    html_parts.append(make_html_list("Projects", proj_items))

    # 4. Skills
    skills = parsed_data.get("skills", [])
    flat_skills = []
    if isinstance(skills, list):
        flat_skills = [s for s in skills if s and s != "Not Found"]
    elif isinstance(skills, dict):
        for val in skills.values():
            if isinstance(val, list):
                flat_skills.extend([s for s in val if s and s != "Not Found"])
                
    skills_items = []
    if flat_skills:
        seen = set()
        deduped = []
        for s in flat_skills:
            if s.lower() not in seen:
                seen.add(s.lower())
                deduped.append(s)
        skills_items.append(", ".join(deduped))
        
    html_parts.append(make_html_list("Skills", skills_items))
    
    return "".join(html_parts)

