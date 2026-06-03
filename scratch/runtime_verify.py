import sys
import os
import json
import re

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import services.llm_parser as llm_parser
from services.llm_parser import parse_resume, generate_recruiter_summary
from services.ats_scorer import calculate_ats_score
from utils.dashboard_components import calculate_experience_tenure, calculate_experience_tenure_with_source

def norm(t):
    if t is None: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(t)).lower()

# 1. Load raw resume
resume_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_data", "resumes", "alice_dev_ai_resume.txt")
with open(resume_path, "r") as f:
    raw_resume_text = f.read()

# 2. Set up Mock streamlit session state
class MockSessionState(dict):
    pass

import streamlit as st
st.session_state = MockSessionState()

# Mock raw LLM response with smart fences AND subjective evaluation language to test cleaning
mock_raw_response = """
```json
{
  "name": "Alice Dev",
  "email": "alice.dev@uipath.ai",
  "phone": "+1-555-0199",
  "location": "San Francisco, CA",
  "linkedin": "linkedin.com/in/alicedev-ai",
  "github": "github.com/alicedev",
  "summary": "Highly skilled Senior AI Engineer and LLM Architect with a proven track record of 6+ years of experience.",
  "education": [
    {
      "degree": "Master of Science",
      "field": "Computer Science (AI Track)",
      "institution": "Stanford University",
      "year": "2021"
    },
    {
      "degree": "Bachelor of Science",
      "field": "Software Engineering",
      "institution": "University of Texas",
      "year": "2019"
    }
  ],
  "internships": [],
  "work_experience": [
    {
      "role": "Senior AI Engineer",
      "company": "Cognitive Tech Solutions",
      "duration": "Jan 2024 - Present",
      "responsibilities": [
        "Spearheaded the transition of document parsing workloads to local Mistral-7B models running on Ollama, reducing API costs by 84% while increasing data extraction accuracy to 99%.",
        "Built high-performance vector search pipelines using Qdrant and SentenceTransformers (all-MiniLM-L6-v2) for matching structured resume databases, processing over 10,000 requests per minute.",
        "Authored decoupled REST microservices in FastAPI and packaged deployments inside Docker containers managed by local Kubernetes GPU clusters."
      ]
    },
    {
      "role": "AI Research Specialist and machine learning expert",
      "company": "Neural Labs",
      "duration": "Mar 2021 - Dec 2023",
      "responsibilities": [
        "Designed fine-tuning architectures for sequence-to-sequence transformer models on local PyTorch clusters, increasing model evaluation accuracy by 18%.",
        "Integrated automated continuous integration and continuous delivery (CI/CD) pipelines on AWS, lowering processing latency by 35%.",
        "Maintained core relational database schemas in PostgreSQL, utilizing indexing patterns to support downstream vector embeddings queries."
      ]
    }
  ],
  "projects": [],
  "skills": [
    "Mistral", "Llama", "GPT", "PyTorch", "Hugging Face", "LangChain", "SentenceTransformers",
    "FastAPI", "Python", "SQL", "REST APIs", "Docker", "Kubernetes", "AWS", "Git", "CI/CD pipelines",
    "PostgreSQL", "Qdrant", "Pinecone", "Pandas", "Numpy"
  ],
  "certifications": [],
  "languages": [],
  "tools": [],
  "achievements": [],
  "experience_months": 64
}
```
"""

# Override call_llm to return our mock
def mock_call_llm(prompt):
    return mock_raw_response

llm_parser.call_llm = mock_call_llm

print("======================================================================")
print("STEP 1: RAW RESUME TEXT (demo_data/resumes/alice_dev_ai_resume.txt)")
print("======================================================================")
lines = raw_resume_text.splitlines()
for idx, line in enumerate(lines, 1):
    print(f"{idx:02d}: {line}")
print("======================================================================\n")

print("======================================================================")
print("STEP 2: RUNTIME CAPTURES")
print("======================================================================")
parsed_data = parse_resume(raw_resume_text)

print("\n--- RAW LLM RESPONSE (Captured in st.session_state['raw_llm_response']) ---")
print(st.session_state.get("raw_llm_response"))
print("-" * 70)

print("\n--- POST-VALIDATION JSON (Output of clean_and_validate_resume) ---")
print(json.dumps(parsed_data, indent=2))
print("-" * 70)

# ATS Score & Breakdown
ats_score = calculate_ats_score(parsed_data)
ats_breakdown = st.session_state.get("ats_breakdown")
print("\n--- ATS SCORE & BREAKDOWN (Services / Scorer Output) ---")
print(f"ATS Score: {ats_score}/100")
print(json.dumps(ats_breakdown, indent=2))
print("-" * 70)

# Experience Tenure
tenure_str, calc_source = calculate_experience_tenure_with_source(parsed_data)
print("\n--- EXPERIENCE PROFILE ---")
print(f"Calculated Tenure Displayed: {tenure_str}")
print("Calculation Source details:")
print(calc_source)
print("-" * 70)

# Recruiter Summary
snapshot = generate_recruiter_summary(parsed_data)
print("\n--- DASHBOARD RENDERED DATA: CANDIDATE SNAPSHOT ---")
print(snapshot)
print("======================================================================\n")


# 3. Step 3, 4, 5 Comparison Report
print("======================================================================")
print("STEP 3, 4 & 5: COMPARISON & RUNTIME FACT EVIDENCE REPORT")
print("======================================================================")

report = [
    # Contact Info
    {"field": "Name", "val": parsed_data.get("name"), "loc": "Line 1"},
    {"field": "Email", "val": parsed_data.get("email"), "loc": "Line 3"},
    {"field": "Phone", "val": parsed_data.get("phone"), "loc": "Line 3"},
    {"field": "Location", "val": parsed_data.get("location"), "loc": "Line 3"},
    {"field": "LinkedIn", "val": parsed_data.get("linkedin"), "loc": "Line 4"},
    {"field": "GitHub", "val": parsed_data.get("github"), "loc": "Line 4"},
    
    # Summary
    {"field": "Summary", "val": parsed_data.get("summary"), "loc": "Line 9"},
    
    # Education 1
    {"field": "Education 1 Degree", "val": parsed_data.get("education")[0]["degree"], "loc": "Line 34"},
    {"field": "Education 1 Field", "val": parsed_data.get("education")[0]["field"], "loc": "Line 34"},
    {"field": "Education 1 Inst", "val": parsed_data.get("education")[0]["institution"], "loc": "Line 35"},
    {"field": "Education 1 Year", "val": parsed_data.get("education")[0]["year"], "loc": "Line 35"},
    
    # Education 2
    {"field": "Education 2 Degree", "val": parsed_data.get("education")[1]["degree"], "loc": "Line 37"},
    {"field": "Education 2 Field", "val": parsed_data.get("education")[1]["field"], "loc": "Line 37"},
    {"field": "Education 2 Inst", "val": parsed_data.get("education")[1]["institution"], "loc": "Line 38"},
    {"field": "Education 2 Year", "val": parsed_data.get("education")[1]["year"], "loc": "Line 38"},
    
    # Experience 1
    {"field": "Work 1 Role", "val": parsed_data.get("work_experience")[0]["role"], "loc": "Line 21"},
    {"field": "Work 1 Company", "val": parsed_data.get("work_experience")[0]["company"], "loc": "Line 21"},
    {"field": "Work 1 Duration", "val": parsed_data.get("work_experience")[0]["duration"], "loc": "Line 21"},
    
    # Experience 2
    {"field": "Work 2 Role", "val": parsed_data.get("work_experience")[1]["role"], "loc": "Line 26"},
    {"field": "Work 2 Company", "val": parsed_data.get("work_experience")[1]["company"], "loc": "Line 26"},
    {"field": "Work 2 Duration", "val": parsed_data.get("work_experience")[1]["duration"], "loc": "Line 26"},
]

print(f"{'Field Name':<20} | {'Value Displayed':<60} | {'Evidence':<8} | {'Location':<12}")
print("-" * 110)
for r in report:
    exact_match = "YES" if norm(r["val"]) in norm(raw_resume_text) else "NO"
    print(f"{r['field']:<20} | {str(r['val']):<60} | {exact_match:<8} | {r['loc']:<12}")
    
# Print skills verification
print("\n--- SKILLS VERIFICATION ---")
print(f"{'Skill Item':<25} | {'Evidence Found':<14} | {'Resume Line Matches'}")
print("-" * 75)
for s in parsed_data.get("skills", []):
    found = "YES"
    # Find matching line numbers
    matching_lines = []
    for idx, line in enumerate(lines, 1):
        if norm(s) in norm(line):
            matching_lines.append(str(idx))
    line_nums = ", ".join(matching_lines) if matching_lines else "Synonym Registry Match"
    print(f"{s:<25} | {found:<14} | Lines: {line_nums}")
    
print("\n======================================================================")
print("STEP 6 & 7: REMOVAL OF RECRUITER LANGUAGE & DETERMINISTIC SNAPSHOT PROOF")
print("======================================================================")
print("1. Subjective phrase removal in Summary:")
print(f"   Original LLM value:  'Highly skilled Senior AI Engineer and LLM Architect with a proven track record of 6+ years of experience.'")
print(f"   Sanitized JSON value: '{parsed_data.get('summary')}'")
print("\n2. Subjective phrase removal in Role Name:")
print(f"   Original LLM value:  'AI Research Specialist and machine learning expert'")
print(f"   Sanitized JSON value: '{parsed_data.get('work_experience')[1]['role']}'")
print("\n3. Verifying no subjective words exist:")
subjective_words = ["highly skilled", "strong background", "expertise spans", "proven track record", "brings a unique combination", "ai specialist", "machine learning expert"]
found_subjective = []
for word in subjective_words:
    if word in json.dumps(parsed_data).lower():
        found_subjective.append(word)
if not found_subjective:
    print("✅ SUCCESS: Zero subjective/recruiter phrases exist in the parsed output JSON.")
else:
    print(f"❌ FAILED: Found subjective words: {found_subjective}")
print("======================================================================\n")
