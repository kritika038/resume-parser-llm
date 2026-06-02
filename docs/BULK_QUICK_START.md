# Quick Start: Bulk Candidate Comparison

Get started with bulk analysis in 5 minutes! 🚀

## Prerequisites

- ✅ Project installed and running (`streamlit run app.py`)
- ✅ Ollama running with Mistral model
- ✅ At least 1 resume PDF file
- ✅ 1 job description (copy-paste)

## Step-by-Step Guide

### 1. Start the Application

```bash
streamlit run app.py
```

Open your browser to: `http://localhost:8501`

### 2. Select Bulk Mode

At the top of the page, you'll see:

```
Analysis Mode
○ Single Resume
● Bulk Candidate Comparison
```

**Click the Bulk Candidate Comparison radio button**

### 3. Paste Job Description

In the "Job Description" text area, paste the job posting:

```
Example:
Senior Python Developer

Requirements:
- 5+ years Python experience
- Django framework
- PostgreSQL
- AWS services
- Docker
- REST API design
```

> **Tip:** The more specific your JD, the better the matching!

### 4. Select Your Ranking Metric

Choose how to rank candidates:

```
📊 Ranking By: [Dropdown ▼]
```

Options:
- **Overall Score** (Recommended) - Balanced assessment
- **ATS Score** - System compatibility
- **JD Match** - Keyword + semantic combined
- **Semantic Similarity** - Conceptual fit only

**For most hiring:** Choose "Overall Score"

### 5. Upload Resumes

Click the upload area or drag-and-drop:

```
📄 Upload Resumes
   [Drag and drop PDFs here or click to select]
```

Select multiple PDF files (2-50 recommended for testing)

### 6. Click Analyze

```
[🔍 Analyze & Compare Candidates]
```

**Wait for processing:**
- A progress bar shows status
- Each candidate takes ~15-20 seconds
- Status updates appear below progress bar

### 7. Review Results

Once complete, you'll see:

```
📊 CANDIDATE RANKINGS

Name          │ Overall │ ATS  │ Keywords │ Semantic │ JD Match
──────────────┼─────────┼──────┼──────────┼──────────┼──────────
Alice Kumar   │   92    │ 95   │   91%    │   90%    │  91%
Bob Smith     │   87    │ 90   │   85%    │   88%    │  86%
Carol Davis   │   81    │ 88   │   78%    │   82%    │  80%
```

### 8. View Detailed Analysis

Click "View Detailed Analysis" next to each candidate:

```
✨ ALICE KUMAR - alice@example.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 SCORES
  Overall:        92/100
  ATS Score:      95/100
  Keyword Match:  91%
  Semantic Match: 90%

🎯 SKILLS
  ✅ Matched (13): Python, Django, PostgreSQL, AWS...
  ❌ Gaps (0): None

📋 METADATA
  Phone: (555) 123-4567
  Email: alice@example.com
  Years Experience: 7
```

### 9. Export Results

Two download options:

**📥 Download JSON**
- Detailed data for each candidate
- Use for integration with ATS
- Complete metadata included

**📊 Download CSV**
- Summary table format
- Open in Excel/Sheets
- Easy for sharing with team

## Example: Complete Workflow

### Your Scenario
You have 5 resumes for a Backend Engineer role.

### Timeline
1. Copy-paste JD: 1 minute
2. Select ranking metric: 30 seconds
3. Select 5 PDFs: 1 minute
4. Click analyze: 2-3 minutes (processing)
5. Review results: 2-3 minutes
6. Download CSV: 30 seconds

**Total: ~7-8 minutes**

### Results You Get

```
Backend Engineer Rankings

Top 3 Candidates:
1. John Doe (89) - Excellent fit, ready to interview
2. Jane Smith (84) - Good fit, minor gaps
3. Bob Johnson (78) - Solid fit, needs training

Export: Done ✓

Next Steps:
- Schedule interviews with top 2
- Review skill gaps for candidates 3-5
- Share CSV with hiring team
```

## Troubleshooting Quick Tips

### "Error processing candidate X"

✅ Solution: Check if PDF is corrupted
- Try opening PDF in another application
- Re-export from original format
- Use a different PDF

### "Processing is slow"

✅ Solution: Normal for large batches
- 15-20 seconds per resume is expected
- First run slower (model loading)
- Subsequent batches faster (cached)

### "Scores seem low"

✅ Check this:
1. Is your JD clear? (Use specific skill names)
2. Do resumes list skills explicitly? (Not just "experienced with X")
3. Compare semantic vs keyword scores
   - High semantic, low keyword = skills described differently
   - Low both = real skill gap

### "I can't see my resumes in the upload"

✅ Solution:
- Ensure files are PDF format (.pdf)
- Not DOCX or other formats
- Try uploading one at a time first

## Tips for Best Results

### For Job Descriptions

✅ **DO:**
- Include specific technologies
- List required years of experience
- Mention frameworks and tools
- Use standard terminology

❌ **DON'T:**
- Be vague ("experience required")
- Use internal jargon only
- Mix job levels
- Include company-specific terms

### For Resumes

✅ **DO:**
- List skills explicitly
- Include contact information
- Mention technology names
- Be quantitative

❌ **DON'T:**
- Hide skills in bullet points
- Use abbreviations alone ("JS" instead of "JavaScript")
- Omit contact details
- Be too generic ("worked with various tools")

## Next Steps

1. **Try your first batch** - Test with 3-5 resumes
2. **Review the detailed guide** - [Bulk Candidate Comparison Guide](BULK_CANDIDATE_COMPARISON_GUIDE.md)
3. **See real examples** - [Usage Examples](BULK_CANDIDATE_COMPARISON_EXAMPLES.md)
4. **Integrate results** - Export to CSV/JSON for your ATS

## FAQ

**Q: How many resumes can I upload?**  
A: Technically unlimited, but 50+ becomes time-consuming. Batch in groups of 10-20.

**Q: Does it work offline?**  
A: Yes! Everything runs locally. No cloud uploads.

**Q: Can I use different ranking metrics?**  
A: Yes! Re-upload same resumes, choose different sort option, re-analyze.

**Q: What about privacy?**  
A: All data stays on your machine. We don't store anything.

**Q: How accurate is the ranking?**  
A: Very good for initial screening. Always review top candidates yourself.

---

**Ready to bulk analyze?** Upload your first batch! 🚀

Questions? Check the full guides linked above!
