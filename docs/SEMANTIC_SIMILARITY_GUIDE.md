# Semantic Similarity Scoring Guide

## Overview

The AI Resume Intelligence Platform now includes **semantic similarity scoring** to enhance job description matching beyond simple keyword extraction. This guide explains how it works and how to use it.

## What is Semantic Similarity?

Semantic similarity measures how conceptually related two pieces of text are, rather than just checking for exact keyword matches.

### Example

**Keyword-based matching:**
- Resume has: "Python Developer"
- JD has: "Python engineer with coding skills"
- Result: Matches "Python" ✓, but misses conceptual alignment

**Semantic similarity:**
- Resume has: "Python Developer with 5 years experience building web applications"
- JD has: "We seek an experienced engineer to develop backend services"
- Result: Understands both are about software development and engineering ✓✓

## How It Works

### Step 1: Generate Embeddings
The system uses **SentenceTransformers** (pre-trained deep learning model) to convert text into numerical vectors (embeddings) that represent semantic meaning.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings
resume_embedding = model.encode("Python developer with AWS expertise")
jd_embedding = model.encode("Looking for cloud engineer with Python skills")
```

### Step 2: Calculate Similarity
The system calculates **cosine similarity** between the two embeddings, which measures the angle between vectors (0 = completely different, 1 = identical).

```python
from sklearn.metrics.pairwise import cosine_similarity

similarity = cosine_similarity([resume_embedding], [jd_embedding])[0][0]
# Returns a value between 0.0 and 1.0
```

### Step 3: Convert to Percentage
The similarity score (0-1) is converted to a percentage (0-100%) for easy interpretation.

## Combined Scoring System

The platform uses a **hybrid approach** combining keyword matching and semantic similarity:

```
Combined Score = (Keyword Score × 0.4) + (Semantic Score × 0.6)
```

### Component Explanation

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| **Keyword Match** | 40% | Percentage of resume skills found in JD |
| **Semantic Match** | 60% | Semantic relatedness of resume to JD |
| **Combined Score** | 100% | Overall job fit |

### Why These Weights?

- **Semantic emphasis (60%)**: Understands nuanced language and paraphrasing
- **Keyword balance (40%)**: Ensures concrete skills are still captured
- This combination gives you the best of both approaches

## Score Interpretation

### Keyword Match Score (0-100%)

| Score | Interpretation | Meaning |
|-------|---|---|
| 80-100% | Excellent Fit | Strong candidate with required skills |
| 60-79% | Good Fit | Qualified with minor skill gaps |
| 40-59% | Moderate Fit | Core skills present; learning curve needed |
| 20-39% | Poor Fit | Significant skill gaps; may require training |
| 0-19% | Not Recommended | Limited skill alignment |

### Semantic Similarity (0.0-1.0 / 0-100%)

| Score | Interpretation | Meaning |
|-------|---|---|
| 0.8-1.0 | Excellent | Very strong alignment with job requirements |
| 0.6-0.79 | Good | Strong conceptual alignment |
| 0.4-0.59 | Moderate | Reasonable but not strong alignment |
| 0.2-0.39 | Weak | Limited conceptual alignment |
| 0.0-0.19 | Poor | Minimal alignment |

### Combined Score (0-100%)

| Score | Hiring Decision | Recommendation |
|-------|---|---|
| 80-100 | **STRONG MATCH** | Highly recommended for interview |
| 60-79 | **GOOD MATCH** | Worth considering; qualifications are strong |
| 40-59 | **MODERATE MATCH** | Possible if other factors compelling |
| 20-39 | **WEAK MATCH** | Consider only if few alternatives |
| 0-19 | **POOR MATCH** | Not recommended; significant gaps |

## Using Semantic Similarity in the UI

### Dashboard Display

The main dashboard shows your combined JD Match score prominently.

### Detailed Analysis Tab

The "📈 Scores & Gaps" tab displays:

1. **ATS Compatibility** (left column)
   - Your ATS score and interpretation
   - Missing ATS elements if any

2. **Job Description Match** (right column)
   - **Combined Score**: Final 0-100% score
   - **Assessment**: Interpretation of your score
   - **Component Breakdown**:
     - Keyword Match percentage
     - Semantic Match percentage
   - **Matched Skills**: Skills found in both resume and JD
   - **Skill Gaps**: Skills in JD but missing from resume

### Practical Example

```
Resume: "Full-stack developer with React and Node.js experience"
JD: "Looking for frontend engineer proficient in JavaScript frameworks"

Keyword Match: 50%
  - Matched: "developer" (partial), "React" ✓, "Node.js" ✗
  - Missing: JavaScript frameworks explicitly listed

Semantic Match: 78%
  - System understands React is a JavaScript framework
  - Recognizes relationship between "developer" and "engineer"
  - Understands full-stack relates to frontend work

Combined Score: 68% (Good Fit)
  - Assessment: "Qualified with minor skill gaps"
```

## Technical Details

### Model Used

The system uses **all-MiniLM-L6-v2**:
- Pre-trained on 1 billion sentence pairs
- Optimized for semantic similarity
- Fast inference (suitable for real-time)
- 384-dimensional embeddings

### Performance Characteristics

| Metric | Value |
|--------|-------|
| Embedding Dimension | 384 |
| Avg. Time per Embedding | ~100-300ms |
| Model Size | ~80MB (downloaded on first use) |
| Accuracy (Semantic Evaluation) | ~87% |

### Installation Requirements

The semantic similarity feature requires three additional packages:

```bash
pip install sentence-transformers>=2.2.0
pip install scikit-learn>=1.3.0
pip install numpy>=1.24.0
```

These are automatically included in `requirements.txt`.

## Code Integration

### Function: `semantic_similarity_score()`

Calculate semantic similarity between resume and JD:

```python
from services.jd_matcher import semantic_similarity_score

resume_text = "Python developer with AWS expertise..."
jd_text = "Looking for cloud engineer with Python skills..."

similarity, interpretation = semantic_similarity_score(resume_text, jd_text)
print(f"Similarity: {similarity:.2%}")  # e.g., "Similarity: 0.75 (75%)"
print(f"Interpretation: {interpretation}")
```

**Returns:**
- `similarity` (float): Score from 0.0 to 1.0
- `interpretation` (str): Human-readable assessment

### Function: `combined_match_score()`

Calculate hybrid score with keyword + semantic matching:

```python
from services.jd_matcher import combined_match_score

skills = {"languages": ["Python"], "tools": ["AWS"]}
resume_text = "Python developer with AWS..."
jd_text = "Cloud engineer with Python..."

score, matched_skills, details = combined_match_score(
    skills,
    resume_text,
    jd_text,
    keyword_weight=0.4,
    semantic_weight=0.6
)

print(f"Combined Score: {score}%")
print(f"Details: {details}")
```

**Returns:**
- `score` (int): 0-100 combined percentage
- `matched_skills` (list): Skills found in both resume and JD
- `details` (dict): Component scores and methodology

### Function: `match_with_jd()` (Keyword-only)

For keyword-based matching without semantic analysis:

```python
from services.jd_matcher import match_with_jd

skills = {"languages": ["Python"], "tools": ["AWS"]}
jd_text = "Python and AWS required..."

score, matched_skills = match_with_jd(skills, jd_text)
print(f"Keyword Match: {score}%")
print(f"Matched Skills: {matched_skills}")
```

## Limitations & Considerations

### When Semantic Similarity Works Well
- ✓ Understanding paraphrasing ("engineer" vs "developer")
- ✓ Capturing related concepts (Python is a language, frameworks use Python)
- ✓ Contextual understanding of roles
- ✓ Industry-specific terminology relationships

### When Semantic Similarity Has Limits
- ✗ Very niche technical acronyms (proprietary tools)
- ✗ Company-specific jargon not in training data
- ✗ Rare technologies not well-represented in model
- ✗ Multiple languages in text

### Best Practices

1. **Use Both Scores Together**
   - Don't rely solely on semantic similarity
   - Keyword match ensures concrete skills are captured
   - Combined approach gives most reliable assessment

2. **Review Skill Gaps**
   - Always check the "Skill Gaps" section
   - These are explicitly mentioned in JD but missing from resume
   - These are objective gaps, not interpretation-dependent

3. **Customize Weights if Needed**
   - Default is 40% keyword + 60% semantic
   - For jobs requiring specific tools: increase keyword weight
   - For conceptual/strategic roles: increase semantic weight

4. **Iterate and Improve**
   - Semantic scoring helps identify transferable skills
   - Use interpretation to guide resume improvements
   - High semantic score with low keyword = skill transferability
   - Low semantic score = significant domain shift

## Common Questions

### Q: Why is my semantic score different from keyword score?

**A:** They measure different things:
- **Keyword**: Exact skill matches (objective)
- **Semantic**: Conceptual relevance (contextual understanding)

A high semantic but low keyword score suggests your skills are transferable but you need to make concrete matches more explicit.

### Q: Can I customize the model used?

**A:** Currently, the system uses the optimized `all-MiniLM-L6-v2` model. For different use cases, you can modify `services/jd_matcher.py`:

```python
# In _get_model() function:
_model = SentenceTransformer('other-model-name')
```

Other options:
- `all-mpnet-base-v2`: Higher accuracy, slower (438MB)
- `paraphrase-MiniLM-L6-v2`: Optimized for paraphrases
- `all-roberta-large-v1`: Highest quality, largest model

### Q: Does semantic scoring work with short JD texts?

**A:** Yes, but with caveats:
- Very short JDs (< 50 words) may produce less reliable scores
- Longer JDs provide more context for similarity calculation
- Always review skill gaps alongside semantic score

### Q: How is the model loaded?

**A:** The SentenceTransformer model uses lazy loading:
1. First call to semantic functions downloads the model (~80MB)
2. Model cached locally for subsequent runs
3. No download on subsequent uses
4. Automatic if `sentence-transformers` is installed

### Q: What if SentenceTransformers is not installed?

**A:** The system falls back gracefully:
1. Logs a warning message
2. Returns to keyword-based matching only
3. Combined score = keyword score only
4. No error is raised

**To fix:** Run `pip install -r requirements.txt`

## Performance Optimization

### Batch Processing

For analyzing multiple resumes against the same JD, optimize by caching the JD embedding:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
jd_embedding = model.encode(jd_text)  # Cache this

for resume in resumes:
    resume_embedding = model.encode(resume)
    similarity = cosine_similarity([resume_embedding], [jd_embedding])
    # ... process results
```

### Reducing Model Size

For deployment on memory-constrained systems, consider:
- Using `distilbert` based models (smaller)
- Quantizing the model
- Using ONNX runtime for faster inference

## Troubleshooting

### Issue: "SentenceTransformer not installed"

**Solution:**
```bash
pip install sentence-transformers scikit-learn numpy
```

### Issue: Slow embedding generation

**Causes:**
- First run downloads the model (~80MB)
- Large resume/JD texts
- CPU-bound computation

**Solutions:**
- Be patient on first run
- Consider GPU support if available
- Limit text length if necessary

### Issue: Inconsistent scores

**Causes:**
- Model is probabilistic with slight variations
- Text preprocessing differences

**Solution:**
- Scores are highly consistent across runs
- Variations should be minimal (< 1-2%)

## Future Enhancements

Potential improvements to semantic similarity:

1. **Domain-Specific Models**: Fine-tune models for tech/finance/medical roles
2. **Multi-Language Support**: Add support for resumes in multiple languages
3. **Skill Importance Weighting**: Weight critical skills more heavily
4. **Dynamic Weight Adjustment**: Automatically adjust weights based on industry
5. **Explainability**: Show which resume sections contributed most to score

## Related Resources

- [SentenceTransformers Documentation](https://www.sbert.net/)
- [Cosine Similarity Explanation](https://en.wikipedia.org/wiki/Cosine_similarity)
- [Semantic Search Concepts](https://www.sbert.net/docs/usage/semantic_search/)

---

**Last Updated:** 2024
**Version:** 1.0
**Status:** Production-Ready
