# Syllabus and Curriculum Design Optimizer (SCDO) - Implementation Plan

> **For:** LLM Implementation Partner  
> **Technology:** IBM Cloud Lite / IBM Granite  
> **Reference:** [IBM Project No.14 Concept Note.txt](file:///d:/Projects_Pap/Verify/IBM%20Project%20No.14%20Concept%20Note.txt)

---

## Core Principles

Before beginning, internalize these principles:

> [!CAUTION]
> **Academic Integrity:** Never fabricate syllabus content, use copyrighted materials without attribution, or generate content that misrepresents accreditation compliance. All generated syllabi must be reviewed by qualified faculty.

| Principle | Guidance |
|-----------|----------|
| **Human Collaboration** | Faculty input is essential—AI assists, not replaces curriculum design |
| **No Placeholders** | Every generated syllabus section must be complete and meaningful |
| **No Demo Code** | All code must be production-intent, not illustrative |
| **Virtual Environment** | Always create and use `venv` for Python projects—never install globally |
| **Domain Accuracy** | Ensure alignment with NEP 2020, NBA, NAAC standards |
| **Modularity** | Keep files under 1500 lines; split logically when approaching limit |
| **IBM Cloud Integration** | Leverage IBM Granite for NLP tasks, respect API limits |
| **Quality First** | Prioritize syllabus quality over generation speed |
| **Verification First** | Write tests before or alongside implementation |
| **Documentation** | Document all template structures and mapping logic |

---

## Project Structure

Create this directory structure. The human partner may suggest modifications.

```
d:/Projects_Pap/SCDO/
├── docs/
│   ├── progress_tracker.md       # Detailed progress tracking
│   ├── bug_journal.md            # All bugs and solutions
│   ├── architecture.md           # System design docs
│   ├── accreditation_guide.md    # NBA/NAAC mapping reference
│   └── api_reference.md          # API documentation
│
├── src/
│   ├── analysis/
│   │   ├── syllabus_parser.py    # Extract structure from syllabi
│   │   ├── gap_analyzer.py       # Identify curriculum gaps
│   │   └── outcome_extractor.py  # Extract learning outcomes
│   │
│   ├── optimization/
│   │   ├── content_optimizer.py  # Suggest content improvements
│   │   ├── bloom_mapper.py       # Map to Bloom's taxonomy
│   │   └── trend_integrator.py   # Industry/academic trends
│   │
│   ├── generation/
│   │   ├── syllabus_generator.py # Generate new syllabi
│   │   ├── template_engine.py    # Syllabus templates
│   │   └── rubric_generator.py   # Assessment rubrics
│   │
│   ├── mapping/
│   │   ├── po_mapper.py          # Program Outcome mapping
│   │   ├── pso_mapper.py         # Program Specific Outcome
│   │   ├── co_mapper.py          # Course Outcome mapping
│   │   └── nep_aligner.py        # NEP 2020 alignment
│   │
│   ├── export/
│   │   ├── pdf_exporter.py       # PDF generation
│   │   ├── excel_exporter.py     # Excel mapping sheets
│   │   └── doc_formatter.py      # Document standardization
│   │
│   ├── ibm/
│   │   ├── granite_client.py     # IBM Granite API wrapper
│   │   ├── cloud_storage.py      # IBM Cloud object storage
│   │   └── watsonx_utils.py      # watsonx.ai utilities
│   │
│   └── utils/
│       ├── text_processing.py    # NLP utilities
│       └── logging_utils.py      # Logging configuration
│
├── tests/
│   ├── unit/                     # Unit tests per module
│   ├── integration/              # End-to-end tests
│   └── conftest.py               # Pytest fixtures
│
├── webapp/
│   ├── backend/                  # FastAPI server
│   └── frontend/                 # React application
│
├── templates/
│   ├── syllabus/                 # Syllabus templates by domain
│   ├── rubrics/                  # Assessment rubric templates
│   └── mappings/                 # Outcome mapping templates
│
├── configs/
│   ├── ibm_config.yaml           # IBM Cloud credentials
│   ├── bloom_taxonomy.yaml       # Bloom's taxonomy reference
│   └── accreditation.yaml        # Accreditation standards
│
├── scripts/
│   ├── setup_ibm_cloud.py        # IBM Cloud setup
│   ├── sample_syllabus_gen.py    # Demo syllabus generation
│   └── batch_process.py          # Bulk syllabus processing
│
└── requirements.txt
```

---

## Phase 1: Environment & IBM Cloud Setup

**Consult human partner on:** IBM Cloud account setup, API quotas, data storage preferences

### Step 1.1: Environment Setup

Create `requirements.txt` with pinned versions. Research current stable versions.

Key dependencies:
- ibm-watson, ibm-cloud-sdk-core (IBM integration)
- PyPDF2, python-docx (document processing)
- spacy, nltk (NLP processing)
- pandas, openpyxl (data/Excel handling)
- FastAPI, uvicorn (backend)
- React dependencies (frontend)

**IBM Cloud Configuration:**
```yaml
ibm_granite:
  model: granite-13b-chat-v2        # Primary NLP model
  max_tokens: 4096                   # Response limit
  temperature: 0.7                   # Creativity balance
  
cloud_object_storage:
  bucket: scdo-syllabi-storage
  region: us-south
  
rate_limits:
  requests_per_minute: 60           # Lite tier limits
  daily_quota: 50000                # Token limit
```

### Step 1.2: IBM Granite Integration

Create `src/ibm/granite_client.py`:
- Authenticate with IBM Cloud
- Handle rate limiting and retries
- Implement prompt templates for curriculum tasks
- Cache responses for repeated queries

### Step 1.3: Document Processing Pipeline

**Syllabus Input Formats:**
| Format | Handler | Priority |
|--------|---------|----------|
| PDF | PyPDF2 + OCR | High |
| DOCX | python-docx | High |
| Plain Text | Direct parse | Medium |
| HTML | BeautifulSoup | Low |

**Testing:** Verify parsing on sample syllabi from different departments

---

## Phase 2: Syllabus Analysis Module

**Consult human partner on:** Sample syllabi sources, domain priorities

### Step 2.1: Syllabus Parser

- **Input:** PDF/DOCX syllabus documents
- **Output:** Structured JSON with extracted components
- **Extract:**
  - Course objectives
  - Learning outcomes (COs)
  - Unit/module structure
  - Lesson plans
  - Assessment strategies
  - References and resources

**Tests:** Extraction accuracy on diverse syllabus formats

### Step 2.2: Gap Analyzer

- **Input:** Parsed syllabus structure
- **Output:** Gap report with recommendations
- **Identify:**
  - Missing Bloom's taxonomy levels
  - Incomplete CO-PO mappings
  - Outdated references
  - Assessment coverage gaps

**Target:** ≥90% accuracy in gap identification

### Step 2.3: Outcome Extractor

- **Input:** Course description and objectives
- **Output:** Well-formed learning outcomes
- **Features:**
  - Bloom's verb classification
  - Measurability scoring
  - Alignment suggestions

**Target:** Output outcomes meeting accreditation standards

---

## Phase 3: Curriculum Optimization Engine

**Consult human partner on:** Accreditation body priorities (NBA/NAAC), domain specializations

### Step 3.1: Bloom's Taxonomy Mapper

Map learning activities to cognitive levels:

| Level | Verbs | Assessment Types |
|-------|-------|-----------------|
| Remember | Define, List, Recall | MCQs, Quizzes |
| Understand | Explain, Describe | Short Answers |
| Apply | Implement, Solve | Labs, Exercises |
| Analyze | Compare, Examine | Case Studies |
| Evaluate | Critique, Assess | Reviews, Reports |
| Create | Design, Develop | Projects, Portfolios |

### Step 3.2: Content Optimizer

Using IBM Granite for:
- Topic relevance scoring
- Sequencing optimization
- Workload balancing
- Modern content suggestions

**Prompt Engineering:**
```
System: You are an academic curriculum expert specializing in 
{domain}. Analyze the following syllabus content and suggest 
improvements aligned with {accreditation_body} standards.

Context: {syllabus_content}
Task: {specific_optimization_task}
```

### Step 3.3: Trend Integrator

- Connect to academic databases (Google Scholar API)
- Analyze industry job postings for skill trends
- Suggest emerging topics for curriculum updates
- Flag potentially obsolete content

**Target:** Recommendations reflect trends from last 2 years

---

## Phase 4: Intelligent Generation Module

**Consult human partner on:** Template preferences, institutional formatting standards

### Step 4.1: Syllabus Generator

Generate complete syllabi from minimal inputs:
- Course title
- Program outcomes
- Keywords or skill areas
- Credit hours

**Output Structure:**
1. Course overview and objectives
2. Course outcomes (4-6 COs)
3. Unit-wise syllabus with hours
4. Teaching-learning methodology
5. Assessment pattern
6. CO-PO mapping matrix
7. References and resources
8. Rubrics (optional)

**Target:** Generated syllabi require <20% manual editing

### Step 4.2: Template Engine

Create domain-specific templates:
- Engineering courses
- Management courses
- Science courses
- Humanities courses
- Interdisciplinary programs

### Step 4.3: Rubric Generator

Auto-generate assessment rubrics:
- Performance criteria
- Rating scales (1-5 or letter grades)
- Descriptor statements
- Weightage distribution

---

## Phase 5: Outcome Mapping Module

**Consult human partner on:** Institution's POs and PSOs, mapping methodology

### Step 5.1: CO-PO-PSO Mapper

Automated mapping with justification:
- Course Outcomes → Program Outcomes
- Course Outcomes → Program Specific Outcomes
- Correlation levels (1=Low, 2=Medium, 3=High)

**Output Format:**
| CO | PO1 | PO2 | PO3 | ... | PSO1 | PSO2 |
|----|-----|-----|-----|-----|------|------|
| CO1| 3 | 2 | - | ... | 3 | 1 |
| CO2| 1 | 3 | 2 | ... | 2 | 2 |

### Step 5.2: NEP 2020 Aligner

Ensure alignment with:
- Multidisciplinary approach
- Flexibility in curriculum
- Outcome-based education (OBE)
- Research integration
- Skill development focus

### Step 5.3: Accreditation Export

Generate documentation for:
- NBA (National Board of Accreditation)
- NAAC (National Assessment and Accreditation Council)
- ABET (for engineering programs)

**Export Formats:** Excel, PDF, formatted DOCX

---

## Phase 6: Web Application

**Consult human partner on:** UI design, authentication requirements, deployment

### Step 6.1: Backend (FastAPI)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload` | POST | Upload syllabus for analysis |
| `/api/analyze` | POST | Analyze uploaded syllabus |
| `/api/optimize` | POST | Get optimization suggestions |
| `/api/generate` | POST | Generate new syllabus |
| `/api/map-outcomes` | POST | Perform CO-PO mapping |
| `/api/export` | GET | Export in various formats |
| `/api/health` | GET | Health check |

**Features:**
- Async processing for IBM Granite calls
- Job queue for batch operations
- Response caching for common requests

### Step 6.2: Frontend (React)

**Core Features:**
- Drag-drop syllabus upload
- Interactive gap analysis dashboard
- Side-by-side comparison (original vs optimized)
- Mapping matrix editor
- Export format selector
- Progress tracking for batch operations

**UI Components:**
- Rich text editor for syllabus editing
- Bloom's taxonomy visual selector
- CO-PO mapping grid
- Trend visualization charts

### Step 6.3: Integration Testing

Test complete workflows:
1. Upload syllabus → Analyze → View gaps
2. Input parameters → Generate syllabus → Export
3. Import outcomes → Auto-map → Export mapping

---

## Phase 7: Evaluation & Documentation

**Consult human partner on:** Evaluation metrics, pilot department selection

### Step 7.1: System Evaluation

| Metric | Target | Minimum |
|--------|--------|---------|
| Syllabus parsing accuracy | ≥95% | 90% |
| Gap identification precision | ≥90% | 85% |
| Outcome extraction quality | ≥90% | 85% |
| Generation relevance score | ≥85% | 80% |
| Mapping accuracy | ≥90% | 85% |
| User satisfaction | ≥4.0/5 | 3.5/5 |

### Step 7.2: Pilot Testing

- Select 2-3 departments for pilot
- Process 10+ syllabi per department
- Collect faculty feedback
- Iterate based on findings

### Step 7.3: Complete Documentation

- `progress_tracker.md`: Full progress log
- `bug_journal.md`: All issues and solutions  
- `architecture.md`: System design
- `api_reference.md`: API docs
- `accreditation_guide.md`: Mapping standards
- `user_manual.md`: End-user guide

---

## IBM Cloud Optimization

| Service | Usage |
|---------|-------|
| **IBM Granite** | NLP tasks: analysis, generation, optimization |
| **Cloud Object Storage** | Store syllabus documents and generated outputs |
| **Cloud Functions** | Serverless processing for batch jobs |
| **API Gateway** | Rate limiting and authentication |

**Lite Tier Considerations:**
- Implement request queuing to stay within limits
- Cache frequently used generations
- Use lighter prompts where possible
- Batch similar operations

---

## Testing Requirements

### Unit Tests

Every module needs tests in `tests/unit/`:

| Module | Test Focus |
|--------|------------|
| Syllabus Parser | Format handling, section extraction |
| Gap Analyzer | Gap detection accuracy |
| Bloom Mapper | Taxonomy classification |
| Granite Client | API calls, error handling |
| Exporters | Format correctness |

**Target:** 80%+ line coverage

### Integration Tests

In `tests/integration/`:
- Full syllabus analysis pipeline
- Complete generation workflow
- Mapping and export pipeline

---

## Human Partner Checkpoints

Pause and consult at:
1. ✅ After IBM Cloud setup verification
2. ✅ After parser handles pilot syllabi
3. ✅ After first complete syllabus generation
4. ✅ After CO-PO mapping accuracy review
5. ✅ Before pilot department deployment

---

## Accuracy Targets

| Component | Target | Minimum |
|-----------|--------|---------|
| Document Parsing | ≥95% | 90% |
| Gap Analysis | ≥90% | 85% |
| Bloom Classification | ≥90% | 85% |
| Syllabus Generation | ≥85% | 80% |
| CO-PO Mapping | ≥90% | 85% |
| **Overall System** | **≥90%** | **85%** |

> [!WARNING]
> If minimum thresholds cannot be met, document the gap and discuss with human partner. Do NOT manipulate results or generate misleading content.

---

## Use Cases Reference

| Use Case | Primary Modules | Expected Output |
|----------|-----------------|-----------------|
| New syllabus design | Generator, Mapper | Complete draft syllabus |
| NEP 2020 compliance | Analyzer, Aligner | Gap report + updated syllabus |
| Accreditation prep | Mapper, Exporter | Mapping matrices, documentation |
| Standardization project | Parser, Optimizer | Consistent department syllabi |
| Quick course outline | Generator | Draft structure for review |

---

## Final Notes

When uncertain:
1. **Search first:** Use web search for best practices and IBM Granite documentation
2. **Ask the partner:** When decisions affect curriculum quality or outcomes significantly
3. **Document decisions:** Record why you chose one approach over another
4. **Test thoroughly:** Verify before moving forward
5. **Validate outputs:** Faculty review before any deployment
6. **Respect constraints:** Stay within IBM Cloud Lite tier limits

Build something that empowers educators.
