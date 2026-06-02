# Bulk Candidate Comparison Feature Guide

## Overview

The **Bulk Candidate Comparison** feature enables you to:
- Upload multiple resumes at once
- Compare them against a single job description
- Rank candidates by multiple scoring criteria
- Export results in JSON or CSV format

This is perfect for hiring teams who need to evaluate many candidates quickly and objectively.

---

## How It Works

### Processing Pipeline

```
Multiple Resumes (PDFs)
        ↓
[Extract Text from Each PDF]
        ↓
[Parse Each Resume with LLM]
        ↓
[Calculate Metrics for Each Candidate]
        ├─ ATS Score (0-100)
        ├─ Keyword Match (0-100%)
        ├─ Semantic Similarity (0-100%)
        └─ Combined JD Match
        ↓
[Rank Candidates by Selected Metric]
        ↓
[Display Rankings & Details]
        ↓
[Export Results]
```

### Scoring Methodology

Each candidate is scored on three dimensions:

1. **ATS Score (30% weight in overall)**
   - Measures compatibility with Applicant Tracking Systems
   - Looks for: name, email, phone, skills, experience, projects
   - Range: 0-100
   - Higher is better

2. **Keyword Match (20% of JD match)**
   - Percentage of resume skills found in job description
   - Objective measure of exact skill overlap
   - Range: 0-100%
   - Concrete, factual metric

3. **Semantic Similarity (20% of JD match)**
   - Conceptual alignment between resume and JD
   - Captures paraphrasing and related concepts
   - Range: 0-100%
   - Context-aware matching

4. **Overall Score (Combined)**
   - Weighted combination of all metrics
   - Formula: (ATS × 0.30) + (Keyword × 0.20) + (Semantic × 0.20) + (Additional factors × 0.30)
   - Range: 0-100
   - Primary ranking metric

### Ranking Options

You can rank candidates by:
- **Overall Score** (default) - Balanced assessment
- **ATS Score** - System compatibility
- **JD Match** - Keyword + semantic combined
- **Semantic Similarity** - Conceptual fit only

---

## Step-by-Step Usage

### Step 1: Select Bulk Mode
```
📌 Select Analysis Mode: [Single Resume] [Bulk Candidate Comparison]
                                           ← Click here
```

### Step 2: Paste Job Description
```
📋 Job Description (Required)
[Text area]
Paste the job description you want to match candidates against
```

### Step 3: Select Ranking Metric
```
📊 Ranking By
[Dropdown]
- Overall Score (recommended)
- ATS Score
- JD Match
- Semantic Similarity
```

### Step 4: Upload Resumes
```
📄 Upload Resumes
[Drag & drop or select PDFs]
Select multiple PDF files to analyze
```

### Step 5: Run Analysis
```
[🔍 Analyze & Compare] (button)
```

The system will:
1. Extract text from each PDF
2. Parse each resume
3. Calculate all metrics
4. Rank by your selected criterion
5. Display results

### Step 6: Review Rankings
```
📊 Candidate Rankings
[Table with all candidates ranked]

Columns:
- Rank (1, 2, 3, etc.)
- Name
- Email
- Overall Score
- ATS Score
- Keyword Match %
- Semantic Match %
- JD Match %
- Total Skills
- Matched Skills
- Skill Gaps
```

### Step 7: View Details
For each candidate, expand to see:
- Detailed scores
- Matched skills
- Skill gaps
- Resume metadata

### Step 8: Export Results
```
⬇️ Export Results
[📥 Download JSON] [📊 Download CSV]
```

---

## Output Formats

### JSON Export Structure
```json
[
  {
    "rank": 1,
    "candidate_id": "candidate_1",
    "name": "John Smith",
    "email": "john@example.com",
    "overall_score": 87.5,
    "ats_score": 90,
    "keyword_match": 85,
    "semantic_match": 88,
    "combined_jd_match": 86,
    "total_skills": 12,
    "matched_skills": ["Python", "Django", "AWS"],
    "skill_gaps": ["Kubernetes", "GraphQL"],
    "parsed_resume": {
      "name": "John Smith",
      "email": "john@example.com",
      "phone": "123-456-7890",
      "skills": {...},
      "experience": {...}
    }
  },
  ...
]
```

### CSV Export Format
```
Rank,Name,Email,Overall Score,ATS Score,Keyword Match,Semantic Match,JD Match,Total Skills,Matched Skills,Skill Gaps
1,John Smith,john@example.com,87.5,90/100,85%,88%,86%,12,3,2
2,Jane Doe,jane@example.com,82.1,85/100,80%,84%,82%,10,2,3
...
```

---

## Interpretation Guide

### Overall Score Ranges

| Score | Rating | Recommendation | Action |
|-------|--------|---|---|
| 90-100 | ⭐⭐⭐⭐⭐ Excellent | Strong candidate | Fast-track to interview |
| 80-89 | ⭐⭐⭐⭐ Very Good | Solid candidate | Schedule interview |
| 70-79 | ⭐⭐⭐ Good | Qualified candidate | Consider for interview |
| 60-69 | ⭐⭐ Fair | Possible fit | Review individually |
| 50-59 | ⭐ Weak | Limited fit | Phone screen maybe |
| <50 | ❌ Poor | Unlikely fit | Pass on candidate |

### Component Score Analysis

**High ATS, Low JD Match**
- Good resume structure
- Missing specific skills
- Action: Consider for adjacent roles

**Low ATS, High JD Match**
- Resume lacks structure
- But has relevant skills
- Action: Request reformatted resume
- Semantic match shows competence

**High Semantic, Low Keyword**
- Transferable skills
- Different terminology
- Action: Consider for related roles
- May require training on specifics

**Low Semantic, High Keyword**
- Has specific skills
- Wrong domain
- Action: Pass for this role
- Maybe other positions

---

## Tips & Best Practices

### Preparing Job Descriptions

1. **Be Detailed**
   - Include specific technologies/tools
   - Mention required experience levels
   - List key responsibilities

2. **Structure Matters**
   - Use clear sections
   - Bullet points work well
   - Technical terms matter for keyword matching

3. **Example Good JD Section**
   ```
   Required Skills:
   - Python (3+ years)
   - Django framework
   - PostgreSQL
   - AWS services (EC2, S3)
   - Docker/Kubernetes
   - REST API design
   ```

### Preparing Resumes

1. **Clear Structure**
   - Name at top
   - Email/phone visible
   - Skills listed explicitly
   - Experience described well

2. **Keywords Matter**
   - Use exact technology names
   - Mention frameworks explicitly
   - List tools and platforms

3. **Good Resume Elements**
   - "Python developer" vs "developer who uses Python"
   - "Django REST Framework" vs "web frameworks"
   - "AWS" vs "cloud services"

### Batch Processing

1. **File Naming**
   - Use candidate names: `John_Smith.pdf`
   - Helps with identification
   - Shows in results

2. **Batch Size**
   - 10-20 resumes: ~1-2 minutes
   - 50 resumes: ~5-10 minutes
   - Depends on resume length and system speed

3. **Organization**
   - Sort resumes into folders by stage
   - Run batches for different JDs
   - Archive results

---

## Example Workflow

### Scenario: Hiring for Backend Engineer

**Step 1: Prepare**
- Create JD with technologies: Python, Django, PostgreSQL, AWS, Docker
- Collect 15 resume PDFs from applicants

**Step 2: Upload**
- Select "Bulk Candidate Comparison" mode
- Paste JD
- Choose "Overall Score" ranking
- Upload all 15 PDFs

**Step 3: Analyze**
- Click analyze
- Wait for processing (usually 2-3 minutes)

**Step 4: Review Rankings**
```
Rank 1: Alice Johnson - Overall: 92  ← Strong candidate
Rank 2: Bob Smith - Overall: 87      ← Good candidate
Rank 3: Carol Davis - Overall: 81    ← Solid candidate
...
```

**Step 5: Interview Strategy**
- Invite Ranks 1-3 directly
- Phone screen Ranks 4-6
- Maybe consider Ranks 7-8
- Pass on Ranks 9-15

**Step 6: Export**
- Download CSV for recruiting team
- Share results with hiring manager

---

## Troubleshooting

### Issue: "Failed to process [resume]"

**Cause:** PDF parsing error  
**Solutions:**
- Ensure PDF is not corrupted
- Try re-exporting from another format
- Check file is actually a PDF

### Issue: Low scores for good candidates

**Causes:**
- Resume uses different terminology
- Skills not explicitly listed
- Different job domain

**Solutions:**
- Review "Skill Gaps" section
- Check semantic vs keyword scores
- Adjust JD for clarity

### Issue: Processing takes long time

**Cause:** Many resumes or long resumes  
**Solutions:**
- Process in smaller batches
- Shorter JD helps slightly
- Resume length is main factor

### Issue: Scores seem inconsistent

**Possible Reasons:**
- Different models (semantic is probabilistic)
- Variation in parsing (LLM based)
- Resume formatting affects extraction

**Note:** Small variations (1-2%) are normal

---

## Advanced Features

### Filtering Results

After analysis, you can:
1. Export to CSV
2. Use spreadsheet software to filter
3. Sort by different criteria
4. Add custom columns

### Integration

Export JSON and integrate with:
- Applicant Tracking Systems (ATS)
- HR management tools
- Custom evaluation systems
- Hiring pipelines

### Batch Comparisons

Compare same candidates against different JDs:
1. Save results from first analysis
2. Re-upload same resumes
3. Try different JD
4. Compare scoring differences

---

## Performance Metrics

### Processing Speed

| Resumes | Typical Time | Factors |
|---------|---|---|
| 5 | 1-2 min | First run includes model load |
| 10 | 2-3 min | ~15-20 sec per resume |
| 20 | 4-6 min | ~15-20 sec per resume |
| 50 | 12-15 min | ~15-20 sec per resume |

**Note:** First run is slower (model downloads). Subsequent runs are faster (cached model).

### System Requirements

- **RAM:** 2GB+ (400MB per concurrent analysis)
- **Storage:** 500MB+ (for model cache)
- **Network:** Optional (local processing)
- **CPU:** Multi-core recommended for speed

---

## Comparison with Single Resume Mode

| Feature | Single | Bulk |
|---------|--------|------|
| **Resumes** | 1 | Multiple |
| **JD** | Optional | Required |
| **Speed** | Slower per resume | Faster bulk |
| **Ranking** | N/A | Yes |
| **Detailed Analysis** | More detailed | Summary view |
| **Suggestions** | Yes | No |
| **Export** | JSON | JSON + CSV |

---

## Use Cases

### 1. High-Volume Recruiting
- Screen 50+ applications
- Quick objective ranking
- Identify top candidates
- Speed up hiring process

### 2. Job Fair Analysis
- Many resumes collected
- Compare all at once
- Identify best matches
- Follow up appropriately

### 3. Internal Transfers
- Evaluate employees for new roles
- Assess skill transferability
- Objective comparison
- Fair internal competition

### 4. Talent Pool Analysis
- Periodically screen your database
- Quickly find candidates for new roles
- Quantify skill gaps
- Plan hiring strategy

### 5. Benchmarking
- How does candidate compare to others?
- Set expectations
- Understand quality level
- Inform offer decisions

---

## Data Privacy & Security

✅ **All local processing**
- Resumes stay on your machine
- No uploads to cloud
- No data sharing
- Complete privacy

✅ **Export complete control**
- You choose when to export
- You control distribution
- You manage retention

---

## Next Steps

1. **Try It:** Upload 5-10 test resumes
2. **Iterate:** Refine JD based on results
3. **Refine:** Adjust weights if needed
4. **Integrate:** Export and use in your ATS
5. **Scale:** Use for ongoing hiring

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review scoring methodology
- Verify JD quality
- Check resume formatting

---

**Ready to hire smarter?** Start with bulk comparison! 🚀
