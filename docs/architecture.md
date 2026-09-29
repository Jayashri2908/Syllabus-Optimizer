# SCDO System Architecture

## Overview

The Syllabus and Curriculum Design Optimizer (SCDO) is a modular, AI-powered system for analyzing, optimizing, and generating academic syllabi. It leverages OpenRouter (Nvidia Nemotron) as the primary AI provider and Google Gemini as a fallback — both free tiers.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│                  (React + TypeScript + Vite)                 │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────┴────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  ┌──────────┬──────────┬──────────┬──────────┬───────────┐ │
│  │  Upload  │ Analyze  │ Optimize │ Generate │  Export   │ │
│  └──────────┴──────────┴──────────┴──────────┴───────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                     Business Logic Layer                     │
│  ┌──────────────┬──────────────┬──────────────────────────┐│
│  │   Analysis   │ Optimization │      Generation          ││
│  │   Module     │   Module     │       Module             ││
│  ├──────────────┼──────────────┼──────────────────────────┤│
│  │   Mapping    │    Export    │      Utilities           ││
│  │   Module     │   Module     │       Module             ││
│  └──────────────┴──────────────┴──────────────────────────┘│
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Integration Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           OpenRouter (Primary) / Gemini (Fallback)   │  │
│  │           ChromaDB (RAG Vector Store)                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Module Architecture

### 1. Analysis Module (`src/analysis/`)

**Purpose:** Parse and analyze existing syllabi

**Components:**
- **SyllabusParser:** Extracts structured data from PDF/DOCX/TXT files
- **GapAnalyzer:** Identifies gaps in Bloom's coverage, CO-PO mapping, assessment
- **OutcomeExtractor:** Extracts and validates learning outcomes
- **RAGAnalyzer:** RAG-enhanced gap analysis with cited recommendations
- **RedundancyDetector:** Detects duplicate topics using semantic similarity
- **ContentAnalyzer:** Evaluates content quality, depth, and breadth
- **LessonPlanExtractor:** Extracts lesson structures from units

**Data Flow:**
```
Document File → Parser → Structured Data → Gap Analyzer → Analysis Report
                                        ↓
                                Outcome Extractor → Validated Outcomes
```

### 2. Optimization Module (`src/optimization/`)

**Purpose:** Provide AI-powered optimization suggestions

**Components:**
- **BloomMapper:** Maps content to Bloom's taxonomy levels
- **ContentOptimizer:** Uses OpenRouter/Gemini for content improvement
- **ObjectivesOptimizer:** Optimizes objectives using SMART criteria
- **ReferenceSuggester:** Suggests textbooks and resources

**Data Flow:**
```
Syllabus Data → Bloom Mapper → Distribution Analysis
              ↓
         Content Optimizer → Optimization Suggestions
              ↓
         OpenRouter/Gemini API
```

### 3. Generation Module (`src/generation/`)

**Purpose:** Generate complete syllabi from minimal inputs

**Components:**
- **SyllabusGenerator:** AI-powered syllabus generation
- **ChainedSyllabusGenerator:** Staggered LLM chaining for consistency
- **SectionPrompts:** User prompts for each syllabus section
- **SectionSchemas:** Pydantic schemas for JSON validation
- **RubricGenerator:** Assessment rubrics
- **DomainTemplates:** Domain-specific context (ML, Web Dev, etc.)
- **IndustryData:** Industry skills and job market data
- **IterativeRefiner:** Multi-pass critique and refinement

**Data Flow:**
```
Course Metadata → Syllabus Generator → OpenRouter/Gemini → Generated Syllabus
                                                            ↓
                                                      Bloom Mapper
                                                            ↓
                                                    Classified Outcomes
```

### 4. Mapping Module (`src/mapping/`)

**Purpose:** Map course outcomes to program outcomes

**Components:**
- **COPOMapper:** Intelligent CO-PO correlation (LLM + rule-based fallback)

**Data Flow:**
```
Course Outcomes → CO-PO Mapper → Correlation Matrix
                              ↓
                      Validation Report
```

### 5. Export Module (`src/export/`)

**Purpose:** Export syllabi in various formats

**Components:**
- **PDFExporter:** Professional PDF generation (ReportLab)
- **ExcelExporter:** Excel mapping sheets (openpyxl)
- **LaTeXExporter:** LaTeX PDF export (PyLaTeX)
- **LaTeXTemplate:** Standard LaTeX template with placeholders

**Data Flow:**
```
Syllabus Data → PDF Exporter → Formatted PDF
              → Excel Exporter → Mapping Sheets
              → LaTeX Exporter → LaTeX/PDF
```

### 6. RAG Module (`src/rag/`)

**Purpose:** Knowledge management and retrieval

**Components:**
- **VectorStore:** ChromaDB vector store for embeddings
- **DocumentIngestion:** Document ingestion into vector store
- **RAGEngine:** RAG query engine for context retrieval

### 7. AI Module (`src/ai/`)

**Purpose:** AI model integration and orchestration

**Components:**
- **ModelManager:** Orchestrates model selection and fallbacks
- **OpenRouterModel:** OpenRouter API (primary)
- **GeminiModel:** Google Gemini API (fallback)
- **PromptLibrary:** Centralized prompt templates

### 8. Utilities (`src/utils/`)

**Purpose:** Common utilities and helpers

**Components:**
- **TextProcessor:** NLP utilities, keyword extraction, Bloom's classification
- **LoggingUtils:** Centralized logging configuration
- **MockServices:** Mock services for testing
- **Exceptions:** Custom exception classes
- **Retry:** Retry and circuit breaker utilities

## API Architecture

### FastAPI Backend (`webapp/backend/`)

**Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload` | POST | Upload and parse syllabus |
| `/api/upload-and-analyze` | POST | Combined upload + analyze |
| `/api/analyze` | POST | Analyze syllabus for gaps |
| `/api/optimize` | POST | Get optimization suggestions |
| `/api/generate` | POST | Generate new syllabus |
| `/api/map-outcomes` | POST | Perform CO-PO mapping |
| `/api/export/pdf` | POST | Export to PDF |
| `/api/export/latex-pdf` | POST | Export to LaTeX PDF |
| `/api/export/excel` | POST | Export to Excel |
| `/api/export/word` | POST | Export to Word |
| `/api/extract-outcomes` | POST | Extract outcomes from text |
| `/api/validate-outcome` | POST | Validate learning outcome |
| `/api/health` | GET | Health check |

**Request/Response Flow:**
```
Client Request → CORS Middleware → Security Headers → Rate Limit → Route Handler → Business Logic
                                                                                   ↓
                                                                         OpenRouter/Gemini (if needed)
                                                                                   ↓
                                                                         Response Formatter
                                                                                   ↓
                                                                             JSON Response
```

## Data Models

### Syllabus Structure
```python
{
    'course_title': str,
    'course_code': str,
    'credits': str,  # L-T-P format
    'prerequisites': List[str],
    'overview': str,
    'objectives': List[str],
    'learning_outcomes': List[{
        'code': str,
        'description': str,
        'bloom_level': str
    }],
    'units': List[{
        'unit_number': int,
        'title': str,
        'topics': List[str],
        'hours': int
    }],
    'teaching_methodology': {
        'teaching_methods': List[str],
        'learning_activities': List[str]
    },
    'assessment_pattern': Dict[str, Any],
    'co_po_mapping': Dict[str, Dict[str, int]],
    'references': List[str]
}
```

### CO-PO Mapping
```python
{
    'CO1': {'PO1': 3, 'PO2': 2, 'PO5': 1},
    'CO2': {'PO1': 2, 'PO3': 3, 'PO4': 2},
    ...
}
```

## Configuration Management

### Configuration Files

1. **ai_models.yaml** - AI model configurations
2. **bloom_taxonomy.yaml** - Bloom's taxonomy reference
3. **accreditation.yaml** - NBA, NAAC, NEP 2020, ABET standards
4. **nep_2020.yaml** - NEP 2020 guidelines
5. **verified_references.yaml** - Verified reference books

### Environment Variables
- `ENV` - Environment (development/staging/production)
- `API_KEY` - API authentication key (required in production)
- `OPENROUTER_API_KEY` - OpenRouter API key
- `GEMINI_API_KEY` - Google Gemini API key
- `CORS_ORIGINS` - Allowed CORS origins
- `MAX_UPLOAD_SIZE` - Maximum file upload size
- `RATE_LIMIT_REQUESTS` - Rate limit requests per window
- `RATE_LIMIT_WINDOW` - Rate limit window in seconds

## Security Considerations

1. **API Keys:** Stored in environment variables, not in code
2. **Rate Limiting:** Implemented per IP address
3. **Input Validation:** Pydantic models for API requests
4. **File Upload:** Type validation and size limits
5. **CORS:** Configurable for production deployment
6. **Security Headers:** HSTS, X-Frame-Options, X-Content-Type-Options

## Scalability

### Current Design
- Synchronous processing for simplicity
- In-memory caching for repeated requests
- Single-instance deployment

### Future Enhancements
- Background job queue for batch processing
- Redis caching for distributed deployment
- Horizontal scaling with load balancer
- Database for syllabus storage and versioning

## Performance Optimization

1. **Caching:** LLM responses cached to reduce API calls
2. **Rate Limiting:** Prevents exceeding API quotas
3. **Lazy Loading:** Components initialized only when needed
4. **Async Processing:** FastAPI async endpoints for I/O operations

## Error Handling

1. **Graceful Degradation:** Fallback mechanisms for API failures
2. **Retry Logic:** Automatic retries for transient failures
3. **Circuit Breaker:** Prevents cascading failures
4. **Logging:** Comprehensive error logging with correlation IDs
5. **User Feedback:** Clear error messages in API responses

## Testing Strategy

### Unit Tests
- Test individual modules in isolation
- Mock OpenRouter/Gemini API calls
- Validate data transformations

### Integration Tests
- Test complete workflows
- Validate API endpoints
- Test with sample syllabi

### Performance Tests
- API response times
- Concurrent request handling
- Rate limit compliance

## Deployment Architecture (Future)

```
┌─────────────┐
│   Nginx     │ ← Load Balancer
└──────┬──────┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│API 1│ │API 2│ │API 3│ │API 4│ ← FastAPI Instances
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │
   └───┬───┴───────┴───────┘
       │
   ┌───▼────┐
   │ Redis  │ ← Shared Cache
   └────────┘
       │
   ┌───▼────────┐
   │ PostgreSQL │ ← Database (optional)
   └────────────┘
```

## Technology Stack Summary

- **Backend:** Python 3.12+, FastAPI
- **AI/NLP:** OpenRouter (Nvidia Nemotron), Google Gemini, spaCy, NLTK
- **Document Processing:** pypdf, pdfplumber, python-docx
- **RAG:** ChromaDB, sentence-transformers
- **Export:** ReportLab (PDF), openpyxl (Excel), PyLaTeX (LaTeX)
- **Configuration:** YAML, python-dotenv
- **Testing:** pytest, pytest-asyncio
- **Frontend:** React, TypeScript, Vite, Tailwind CSS
