# Project Structure Documentation

## Directory Layout

```
resume-parser-llm/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # Comprehensive documentation
├── PROMPT.md                       # Detailed prompt engineering guide
│
├── services/                       # Core business logic
│   ├── __init__.py                # Service module exports
│   ├── pdf_extractor.py           # PDF text extraction
│   ├── llm_parser.py              # LLM-based parsing & validation
│   ├── ats_scorer.py              # ATS compatibility scoring
│   └── jd_matcher.py              # Job description matching
│
├── utils/                          # Helper utilities
│   ├── __init__.py                # Utils module exports
│   ├── prompts.py                 # Prompt templates
│   └── validators.py              # JSON validation & cleaning
│
├── data/                           # Data storage
│   ├── sample_resumes/            # Test resume examples
│   ├── sample_outputs/            # Expected parsing outputs
│   └── job_descriptions/          # Test job descriptions
│
├── screenshots/                    # UI/UX documentation
│   ├── dashboard.png              # Dashboard view
│   ├── json_output.png            # JSON tab
│   └── suggestions.png            # Suggestions tab
│
└── docs/                           # Extended documentation
    ├── architecture.md            # System architecture
    ├── api_reference.md           # API documentation
    ├── deployment.md              # Deployment guide
    └── faq.md                     # Frequently asked questions
```

## Module Responsibilities

### `services/` - Core Business Logic

#### `pdf_extractor.py`
- **Purpose**: Extract text from PDF files
- **Key Functions**:
  - `extract_pdf(file_object)` - Multi-page PDF text extraction
  - `validate_pdf(file_object)` - PDF format validation
- **Dependencies**: PyPDF2
- **Error Handling**: Graceful fallback for corrupted pages

#### `llm_parser.py`
- **Purpose**: LLM-based resume parsing and validation
- **Key Functions**:
  - `call_llm(prompt)` - Call Ollama API
  - `parse_resume(resume_text)` - Complete parsing pipeline
  - `generate_suggestions(resume_data, jd_text)` - AI recommendations
- **Dependencies**: requests, validators
- **Error Handling**: Timeout handling, connection retry logic

#### `ats_scorer.py`
- **Purpose**: Calculate ATS compatibility scores
- **Key Functions**:
  - `calculate_ats_score(resume_data)` - Weighted component scoring
  - `get_ats_interpretation(score)` - Score assessment
  - `get_missing_ats_elements(resume_data)` - Gap analysis
- **Scoring Weights**:
  - Name: 10 points
  - Email: 10 points
  - Phone: 10 points
  - Skills: 30 points
  - Experience: 20 points
  - Projects: 20 points

#### `jd_matcher.py`
- **Purpose**: Match resume skills to job requirements
- **Key Functions**:
  - `match_with_jd(skills_dict, jd_text)` - Skill matching algorithm
  - `identify_skill_gaps(skills_dict, jd_text)` - Gap identification
  - `extract_tech_keywords(text)` - Technology extraction
  - `get_jd_match_interpretation(score)` - Score assessment
- **Algorithm**: Case-insensitive keyword matching with relevance scoring

### `utils/` - Helper Utilities

#### `prompts.py`
- **Purpose**: Centralized prompt management
- **Contents**:
  - `PARSE_PROMPT` - Resume extraction schema and rules
  - `SUGGEST_PROMPT` - Improvement suggestion template
  - `RESUME_EXTRACTION_CONTEXT` - Guidelines and best practices
- **Usage**: Imported by llm_parser.py

#### `validators.py`
- **Purpose**: Data validation and cleaning
- **Key Functions**:
  - `clean_json(raw_output)` - JSON artifact removal and validation
  - `validate_resume_schema(data)` - Schema compliance checking
  - `sanitize_text(text)` - Input text cleaning
  - `extract_json_from_mixed_output(text)` - JSON extraction from text
- **Operations**:
  - Markdown fence removal
  - Trailing comma fixing
  - Smart quote normalization
  - JSON.loads() validation

### `app.py` - Main Application

- **Framework**: Streamlit
- **Responsibilities**:
  - User interface orchestration
  - Service module integration
  - Result presentation and export
- **Workflow**:
  1. Accept resume input (PDF or text)
  2. Extract text (if PDF)
  3. Parse with LLM
  4. Calculate scores
  5. Generate suggestions
  6. Display results in tabs
  7. Enable export options

## Data Flow Architecture

```
User Input (PDF/Text)
    ↓
[services/pdf_extractor.py] - Extract text
    ↓
[services/llm_parser.py] - Parse resume
    ↓
[utils/validators.py] - Clean JSON
    ↓
Validated Resume JSON
    ├─→ [services/ats_scorer.py] - Calculate ATS
    ├─→ [services/jd_matcher.py] - Match with JD
    └─→ [services/llm_parser.py] - Generate suggestions
    ↓
Results
    ├─ Metrics (ATS, JD Match, Skills Count)
    ├─ Full JSON
    ├─ Suggestions
    └─ Export Options
    ↓
[app.py] - Display in Streamlit UI
```

## Import Hierarchy

```
app.py
├── services.pdf_extractor
├── services.llm_parser
├── services.ats_scorer
├── services.jd_matcher
├── utils.validators
└── utils.prompts

services/llm_parser.py
├── utils.validators
└── utils.prompts

services/ats_scorer.py
└── (no internal imports)

services/jd_matcher.py
└── (no internal imports)

services/pdf_extractor.py
└── PyPDF2
```

## Configuration Management

### Environment Variables
Currently none required. Future enhancements may include:
- `OLLAMA_URL` - Ollama API endpoint (default: localhost:11434)
- `OLLAMA_MODEL` - LLM model name (default: mistral)
- `REQUEST_TIMEOUT` - API timeout in seconds (default: 90)

### Constants
Defined in respective modules:
- `OLLAMA_API_URL` in llm_parser.py
- `OLLAMA_MODEL` in llm_parser.py
- `REQUEST_TIMEOUT` in llm_parser.py

## Testing Structure (Future)

Recommended test organization:
```
tests/
├── unit/
│   ├── test_pdf_extractor.py
│   ├── test_validators.py
│   ├── test_ats_scorer.py
│   └── test_jd_matcher.py
├── integration/
│   ├── test_parse_resume.py
│   └── test_full_pipeline.py
└── fixtures/
    ├── sample_resumes/
    └── expected_outputs/
```

## Error Handling Strategy

### By Layer

#### Input Layer (app.py)
- Validate file type
- Check input length
- Provide user-friendly error messages

#### Extraction Layer (pdf_extractor.py)
- Handle corrupted PDFs
- Handle empty PDFs
- Log extraction progress

#### Processing Layer (llm_parser.py)
- Handle API timeouts
- Handle connection errors
- Log LLM output for debugging

#### Validation Layer (validators.py)
- Handle malformed JSON
- Validate schema compliance
- Extract JSON from mixed output

#### Scoring Layer (ats_scorer.py, jd_matcher.py)
- Handle missing fields
- Handle invalid data types
- Return sensible defaults

## Logging

All modules include logging with INFO and DEBUG levels:
- `logging.getLogger(__name__)` for module-specific loggers
- INFO level: Normal flow tracking
- DEBUG level: Detailed debugging information
- ERROR level: Critical failures

View logs in console when running:
```bash
streamlit run app.py --logger.level=info
```

## Future Enhancement Opportunities

### Performance
- Add caching layer for repeated processing
- Implement batch processing API
- Add GPU support for Ollama

### Features
- Multi-language resume support
- Resume plagiarism detection
- Confidence scoring for extracted fields
- Historical candidate tracking
- Database backend for resume storage

### Integration
- REST API wrapper
- ATS platform connectors
- HRIS synchronization
- Slack/Teams notifications

### AI Improvements
- Fine-tune Mistral for resumes
- Multi-model ensemble scoring
- A/B testing framework for prompts
- Custom schema templates

## Development Guidelines

### Adding New Features

1. **Identify the layer**: UI (app.py), Service, or Utility
2. **Create appropriate module**: Follow naming conventions
3. **Add logging**: Use module logger for debugging
4. **Handle errors**: Never let exceptions propagate uncaught
5. **Document**: Add docstrings with examples
6. **Test**: Create unit and integration tests

### Code Style

- Follow PEP 8 conventions
- Use type hints for function signatures
- Add docstrings to all functions
- Use meaningful variable names
- Keep functions focused and testable
- Limit function length to ~30 lines

### Dependency Management

- Add to `requirements.txt` with pinned versions
- Document why each dependency is needed
- Minimize external dependencies
- Prefer standard library when possible

## Maintenance Checklist

- [ ] Update prompts as LLM behavior changes
- [ ] Monitor API response times
- [ ] Review and update error messages
- [ ] Keep dependencies up to date
- [ ] Monitor for deprecated Streamlit APIs
- [ ] Review logging output for issues
- [ ] Gather user feedback for improvements
