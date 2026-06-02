# CandidateComparator API Reference

Complete technical documentation for programmatic use of the bulk comparison service.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data Structures](#data-structures)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Error Handling](#error-handling)
- [Performance](#performance)

---

## Overview

The `CandidateComparator` service enables programmatic bulk resume analysis:

```python
from services.candidate_comparator import CandidateComparator

# Create comparator
comparator = CandidateComparator()

# Add resumes
comparator.add_resume_text("Candidate 1", resume_text, jd_text)
comparator.add_pdf_resume("Candidate 2", pdf_bytes, jd_text)

# Get ranked results
candidates = comparator.get_ranked_candidates(sort_by="overall")

# Export
results = comparator.export_results(format="json")
```

**Key Features:**
- Multi-resume analysis
- Configurable scoring weights
- Multiple ranking dimensions
- JSON/CSV export
- Per-candidate error handling
- Progress tracking support

---

## Installation

### Requirements

```
Python 3.8+
sentence-transformers>=2.2.0
scikit-learn>=1.0.0
numpy>=1.21.0
pandas>=1.5.0
PyPDF2>=3.0.0
```

### Import

```python
from services.candidate_comparator import CandidateComparator, CandidateScore
```

---

## Quick Start

### Basic Usage

```python
from services.candidate_comparator import CandidateComparator

# Initialize
comparator = CandidateComparator()

# Add resumes with JD
comparator.add_resume_text(
    candidate_id="john_doe_001",
    resume_text="John Doe\nPython Developer...",
    jd_text="Senior Backend Engineer\nRequired: Python...",
    candidate_name="John Doe"
)

# Get ranked candidates
ranked = comparator.get_ranked_candidates(sort_by="overall")

# Access top candidate
top = ranked[0]
print(f"Top Candidate: {top.name}")
print(f"Overall Score: {top.overall_score:.1f}")
print(f"Matched Skills: {top.matched_skills}")
```

### With PDF Resumes

```python
# Read PDF
with open("resume.pdf", "rb") as f:
    pdf_bytes = f.read()

# Add to comparator
comparator.add_pdf_resume(
    candidate_id="candidate_002",
    pdf_bytes=pdf_bytes,
    jd_text="Job description here...",
    candidate_name="Jane Smith"
)
```

### Export Results

```python
# Export as JSON
json_results = comparator.export_results(format="json")

# Export as CSV
csv_data = comparator.export_results(format="csv")

# Or get summary table
table = comparator.get_summary_table()
```

---

## Data Structures

### CandidateScore Dataclass

Represents a scored candidate with all metrics.

```python
@dataclass
class CandidateScore:
    candidate_id: str
    name: str
    email: str
    ats_score: float
    keyword_match: float
    semantic_match: float
    combined_jd_match: float
    total_skills: int
    matched_skills: List[str]
    skill_gaps: List[str]
    parsed_data: Dict
    
    @property
    def overall_score(self) -> float:
        """Weighted combination of all metrics.
        
        Formula: (ats*0.30) + (jd_match*0.40) + (semantic*0.30)
        """
        return (
            (self.ats_score * 0.30) +
            (self.combined_jd_match * 0.40) +
            (self.semantic_match * 0.30)
        )
```

**Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `candidate_id` | str | Unique identifier for candidate |
| `name` | str | Candidate's full name |
| `email` | str | Email address (if available) |
| `ats_score` | float | ATS compatibility (0-100) |
| `keyword_match` | float | Keyword match percentage (0-100) |
| `semantic_match` | float | Semantic similarity (0-100) |
| `combined_jd_match` | float | Combined JD match (0-100) |
| `total_skills` | int | Total skills identified in resume |
| `matched_skills` | List[str] | Skills matching JD |
| `skill_gaps` | List[str] | Skills in JD not in resume |
| `parsed_data` | Dict | Full LLM-extracted resume data |
| `overall_score` | float | Weighted overall score (property) |

**Properties:**

```python
candidate = CandidateScore(...)

# Weighted overall score (0-100)
score = candidate.overall_score  # 87.5

# Skill statistics
matched_count = len(candidate.matched_skills)
gap_count = len(candidate.skill_gaps)
total = candidate.total_skills
```

---

## API Reference

### CandidateComparator Class

Main service for bulk resume analysis.

#### Constructor

```python
comparator = CandidateComparator()
```

**Parameters:** None  
**Returns:** CandidateComparator instance

---

#### `add_resume_text()`

Add a resume as text string.

```python
comparator.add_resume_text(
    candidate_id: str,
    resume_text: str,
    jd_text: str,
    candidate_name: Optional[str] = None
) -> CandidateScore
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `candidate_id` | str | Unique identifier (e.g., "john_001") |
| `resume_text` | str | Full resume text |
| `jd_text` | str | Job description text |
| `candidate_name` | str (opt) | Candidate name (extracted if None) |

**Returns:** `CandidateScore` object for added candidate

**Raises:** 
- `ValueError` - Invalid inputs
- `Exception` - LLM processing error

**Example:**

```python
score = comparator.add_resume_text(
    candidate_id="resume_001",
    resume_text="John Smith\nSenior Python Developer...",
    jd_text="Backend Engineer required: Python, Django...",
    candidate_name="John Smith"
)

print(f"Added: {score.name} (Score: {score.overall_score:.1f})")
```

---

#### `add_pdf_resume()`

Add a resume from PDF bytes.

```python
comparator.add_pdf_resume(
    candidate_id: str,
    pdf_bytes: bytes,
    jd_text: str,
    candidate_name: Optional[str] = None
) -> CandidateScore
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `candidate_id` | str | Unique identifier |
| `pdf_bytes` | bytes | Raw PDF file bytes |
| `jd_text` | str | Job description text |
| `candidate_name` | str (opt) | Candidate name (extracted if None) |

**Returns:** `CandidateScore` object for added candidate

**Raises:**
- `ValueError` - Invalid PDF or candidate_id
- `Exception` - PDF extraction or LLM error

**Example:**

```python
# Read PDF
with open("resume.pdf", "rb") as f:
    pdf_data = f.read()

# Add to comparator
score = comparator.add_pdf_resume(
    candidate_id="candidate_002",
    pdf_bytes=pdf_data,
    jd_text="Senior Developer required: Python, AWS..."
)

print(f"Processed: {score.name}")
```

---

#### `get_ranked_candidates()`

Get all candidates ranked by metric.

```python
comparator.get_ranked_candidates(
    sort_by: str = "overall"
) -> List[CandidateScore]
```

**Parameters:**

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `sort_by` | str | "overall", "ats", "jd_match", "semantic" | Sort criterion |

**Returns:** List of `CandidateScore` objects, ranked highest to lowest

**Example:**

```python
# Get all candidates ranked by overall score
all_candidates = comparator.get_ranked_candidates(sort_by="overall")

# Get candidates ranked by ATS score only
by_ats = comparator.get_ranked_candidates(sort_by="ats")

# Print top 3
for i, candidate in enumerate(all_candidates[:3], 1):
    print(f"{i}. {candidate.name}: {candidate.overall_score:.1f}")
```

---

#### `get_top_candidates()`

Get top N candidates by overall score.

```python
comparator.get_top_candidates(
    top_n: int = 5
) -> List[CandidateScore]
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `top_n` | int | Number of top candidates to return |

**Returns:** List of top N candidates (ranked by overall score)

**Example:**

```python
# Get top 5 candidates
top_5 = comparator.get_top_candidates(top_n=5)

for candidate in top_5:
    print(f"{candidate.name}: {candidate.overall_score:.1f}")

# Get top 10
top_10 = comparator.get_top_candidates(top_n=10)
```

---

#### `get_summary_table()`

Get candidate data as dictionary for DataFrame conversion.

```python
comparator.get_summary_table() -> Dict[str, List]
```

**Returns:** Dictionary with lists of candidate metrics

**Example:**

```python
import pandas as pd

table_data = comparator.get_summary_table()
df = pd.DataFrame(table_data)

# Display
print(df)

# Export to CSV
df.to_csv("candidates.csv", index=False)

# Filter for score > 80
qualified = df[df['overall_score'] > 80]
```

**Column Structure:**

```python
{
    'rank': [1, 2, 3, ...],
    'name': ['John Doe', 'Jane Smith', ...],
    'email': ['john@ex.com', 'jane@ex.com', ...],
    'overall_score': [92, 87, 81, ...],
    'ats_score': [95, 90, 88, ...],
    'keyword_match': [91, 85, 78, ...],
    'semantic_match': [90, 88, 82, ...],
    'jd_match': [91, 86, 80, ...],
    'total_skills': [14, 12, 11, ...],
    'matched_skills': [13, 11, 10, ...],
    'skill_gaps': [1, 1, 1, ...]
}
```

---

#### `get_detailed_comparison()`

Get comprehensive comparison data for export.

```python
comparator.get_detailed_comparison() -> List[Dict]
```

**Returns:** List of candidate data dictionaries

**Example:**

```python
details = comparator.get_detailed_comparison()

# Detailed info per candidate
for candidate_data in details:
    print(candidate_data['name'])
    print(f"  Matched Skills: {candidate_data['matched_skills']}")
    print(f"  Skill Gaps: {candidate_data['skill_gaps']}")
    print(f"  Email: {candidate_data['email']}")
    print(f"  Experience: {candidate_data['years_experience']}")
```

---

#### `export_results()`

Export results in JSON or CSV format.

```python
comparator.export_results(
    format: str = "json"
) -> str
```

**Parameters:**

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `format` | str | "json", "csv" | Export format |

**Returns:** Formatted string (JSON or CSV)

**Example:**

```python
# Export as JSON
json_str = comparator.export_results(format="json")

# Save JSON
with open("candidates.json", "w") as f:
    f.write(json_str)

# Export as CSV
csv_str = comparator.export_results(format="csv")

# Save CSV
with open("candidates.csv", "w") as f:
    f.write(csv_str)
```

---

#### `clear()`

Reset the comparator, removing all candidates.

```python
comparator.clear() -> None
```

**Example:**

```python
# After processing one batch
comparator.clear()

# Now ready for new batch
comparator.add_resume_text(...)
```

---

## Usage Examples

### Example 1: Batch Processing Multiple PDFs

```python
from pathlib import Path
from services.candidate_comparator import CandidateComparator

# Initialize
comparator = CandidateComparator()
jd_text = "Senior Backend Engineer required..."

# Process all PDFs in directory
resume_dir = Path("resumes/")
for i, pdf_file in enumerate(resume_dir.glob("*.pdf"), 1):
    with open(pdf_file, "rb") as f:
        pdf_bytes = f.read()
    
    # Add to comparator
    score = comparator.add_pdf_resume(
        candidate_id=f"candidate_{i:03d}",
        pdf_bytes=pdf_bytes,
        jd_text=jd_text
    )
    print(f"✓ Processed: {score.name} (Score: {score.overall_score:.1f})")

# Get results
ranked = comparator.get_ranked_candidates(sort_by="overall")
print(f"\nTotal: {len(ranked)} candidates processed")
```

### Example 2: Filter Top Candidates

```python
# Get all candidates
all_candidates = comparator.get_ranked_candidates()

# Filter by score threshold
threshold = 80
qualified = [c for c in all_candidates if c.overall_score >= threshold]

print(f"Qualified candidates (>80): {len(qualified)}")
for candidate in qualified:
    print(f"  {candidate.name}: {candidate.overall_score:.1f}")
```

### Example 3: Analyze Skill Gaps

```python
# Get top candidate
top = comparator.get_top_candidates(top_n=1)[0]

print(f"Candidate: {top.name}")
print(f"Matched Skills: {top.matched_skills}")
print(f"Skill Gaps: {top.skill_gaps}")
print(f"Match Ratio: {len(top.matched_skills)} / {top.total_skills}")
```

### Example 4: Export and Create Report

```python
import json
import pandas as pd

# Get summary table
table_data = comparator.get_summary_table()
df = pd.DataFrame(table_data)

# Export CSV
df.to_csv("rankings.csv", index=False)

# Export JSON
details = comparator.get_detailed_comparison()
with open("candidates_detailed.json", "w") as f:
    json.dump(details, f, indent=2)

print("✓ Exported rankings.csv")
print("✓ Exported candidates_detailed.json")
```

### Example 5: Compare Multiple JDs

```python
# Same candidates, different JDs
candidates_data = [...]  # Your candidate data

jd_list = [
    "Backend Engineer: Python, Django, PostgreSQL",
    "Frontend Engineer: React, TypeScript, CSS",
    "DevOps Engineer: AWS, Docker, Kubernetes"
]

results = {}

for jd_title, jd_text in zip(["Backend", "Frontend", "DevOps"], jd_list):
    comparator.clear()
    
    # Re-analyze with new JD
    for candidate in candidates_data:
        comparator.add_resume_text(...)
    
    # Store results
    results[jd_title] = comparator.get_ranked_candidates()

# Now you can see how ranking changes per role
```

---

## Error Handling

### Common Errors and Solutions

#### ValueError: invalid candidate_id

```python
try:
    comparator.add_resume_text("", "", "")
except ValueError as e:
    print(f"Error: {e}")
    # Must provide non-empty candidate_id
```

#### PDF Extraction Error

```python
try:
    comparator.add_pdf_resume("id", invalid_bytes, jd_text)
except Exception as e:
    print(f"PDF Error: {e}")
    # Ensure pdf_bytes is valid PDF content
```

#### LLM Processing Error

```python
try:
    comparator.add_resume_text("id", resume, jd)
except Exception as e:
    print(f"LLM Error: {e}")
    # Ensure Ollama is running and Mistral model is available
```

### Error Recovery Pattern

```python
from services.candidate_comparator import CandidateComparator

comparator = CandidateComparator()
successful = 0
failed = 0

for candidate_data in candidates:
    try:
        score = comparator.add_resume_text(
            candidate_data['id'],
            candidate_data['resume'],
            jd_text
        )
        successful += 1
        print(f"✓ {candidate_data['name']}")
    except Exception as e:
        failed += 1
        print(f"✗ {candidate_data['name']}: {e}")

print(f"\nProcessed: {successful} successful, {failed} failed")
```

---

## Performance

### Processing Speed

| Batch Size | Typical Time | Per Resume |
|---------|-----|-----|
| 1 resume | ~20 sec | 20 sec (includes model load) |
| 5 resumes | ~90 sec | 18 sec each |
| 10 resumes | ~170 sec | 17 sec each |
| 50 resumes | ~850 sec | 17 sec each |

**Note:** First run slower (model download/load). Subsequent runs faster (cached model).

### Memory Usage

- Base system: ~400MB
- Per candidate: ~50-100MB (depends on resume length)
- 10 candidates: ~900MB-1.2GB
- 50 candidates: ~3-5GB

### Optimization Tips

1. **Batch in groups of 10-20** for memory efficiency
2. **Use `get_top_candidates(5)`** instead of processing all
3. **Clear between batches:** `comparator.clear()`
4. **Stream results** for large datasets

---

## Integration Examples

### With Flask API

```python
from flask import Flask, jsonify, request
from services.candidate_comparator import CandidateComparator

app = Flask(__name__)
comparator = CandidateComparator()

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    
    comparator.add_resume_text(
        candidate_id=data['id'],
        resume_text=data['resume'],
        jd_text=data['jd']
    )
    
    ranked = comparator.get_ranked_candidates()
    return jsonify([{
        'name': c.name,
        'score': c.overall_score,
        'matched_skills': c.matched_skills
    } for c in ranked])
```

### With Django

```python
from services.candidate_comparator import CandidateComparator

class CandidateAnalysis:
    def __init__(self, jd_text):
        self.comparator = CandidateComparator()
        self.jd_text = jd_text
    
    def add_candidate(self, resume_file):
        return self.comparator.add_pdf_resume(
            candidate_id=str(resume_file.id),
            pdf_bytes=resume_file.read(),
            jd_text=self.jd_text
        )
    
    def get_results(self):
        return self.comparator.export_results(format="json")
```

---

## Support & Troubleshooting

For issues:
1. Check error message and look above for solution
2. Verify Ollama + Mistral model running
3. Ensure valid input (non-empty strings, valid PDFs)
4. Check memory/CPU usage for performance issues

---

**Ready to integrate?** Start with the Quick Start section above! 🚀
