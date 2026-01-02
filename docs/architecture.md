# SCDO System Architecture

## Overview

The Syllabus and Curriculum Design Optimizer (SCDO) is a modular, AI-powered system for analyzing, optimizing, and generating academic syllabi. It leverages IBM Granite for natural language processing and follows outcome-based education (OBE) principles.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│                     (React Application)                      │
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
│  │           IBM watsonx.ai / Granite API               │  │
│  │           IBM Cloud Object Storage                   │  │
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
- **ContentOptimizer:** Uses IBM Granite for content improvement
- **TrendIntegrator:** Suggests modern topics (partial)

**Data Flow:**
```
Syllabus Data → Bloom Mapper → Distribution Analysis
              ↓
         Content Optimizer → Optimization Suggestions
              ↓
         IBM Granite API
```

### 3. Generation Module (`src/generation/`)

**Purpose:** Generate complete syllabi from minimal inputs

**Components:**
- **SyllabusGenerator:** AI-powered syllabus generation
- **TemplateEngine:** Domain-specific templates (partial)
- **RubricGenerator:** Assessment rubrics (pending)

**Data Flow:**
```
Course Metadata → Syllabus Generator → IBM Granite → Generated Syllabus
                                                    ↓
                                              Bloom Mapper
                                                    ↓
                                            Classified Outcomes
```

### 4. Mapping Module (`src/mapping/`)

**Purpose:** Map course outcomes to program outcomes

**Components:**
- **COPOMapper:** Intelligent CO-PO correlation
- **PSOMapper:** Program-specific outcome mapping (pending)
- **NEPAligner:** NEP 2020 alignment (pending)

**Data Flow:**
```
Course Outcomes → CO-PO Mapper → Correlation Matrix
                              ↓
                      Validation Report
```

### 5. Export Module (`src/export/`)

**Purpose:** Export syllabi in various formats

**Components:**
- **PDFExporter:** Professional PDF generation
- **ExcelExporter:** Excel mapping sheets (pending)
- **DOCXFormatter:** Word document formatting (pending)

**Data Flow:**
```
Syllabus Data → PDF Exporter → Formatted PDF
              → Excel Exporter → Mapping Sheets
              → DOCX Formatter → Word Document
```

### 6. IBM Integration Layer (`src/ibm/`)

**Purpose:** Interface with IBM Cloud services

**Components:**
- **GraniteClient:** IBM Granite API wrapper with rate limiting
- **CloudStorage:** IBM Cloud Object Storage integration
- **WatsonxUtils:** watsonx.ai utilities (pending)

**Features:**
- Authentication and credential management
- Rate limiting and retry logic
- Response caching
- Error handling

### 7. Utilities (`src/utils/`)

**Purpose:** Common utilities and helpers

**Components:**
- **TextProcessor:** NLP utilities, keyword extraction, Bloom's classification
- **LoggingUtils:** Centralized logging configuration

## API Architecture

### FastAPI Backend (`webapp/backend/`)

**Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload` | POST | Upload and parse syllabus |
| `/api/analyze` | POST | Analyze syllabus for gaps |
| `/api/optimize` | POST | Get optimization suggestions |
| `/api/generate` | POST | Generate new syllabus |
| `/api/map-outcomes` | POST | Perform CO-PO mapping |
| `/api/export/pdf` | POST | Export to PDF |
| `/api/extract-outcomes` | POST | Extract outcomes from text |
| `/api/validate-outcome` | POST | Validate learning outcome |

**Request/Response Flow:**
```
Client Request → CORS Middleware → Route Handler → Business Logic
                                                  ↓
                                            IBM Granite (if needed)
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

1. **ibm_config.yaml** - IBM Cloud and Granite settings
2. **bloom_taxonomy.yaml** - Bloom's taxonomy reference
3. **accreditation.yaml** - NBA, NAAC, NEP 2020, ABET standards

### Environment Variables
- `IBM_CLOUD_API_KEY` - IBM Cloud API key
- `IBM_PROJECT_ID` - watsonx.ai project ID
- `IBM_COS_API_KEY` - Cloud Object Storage API key

## Security Considerations

1. **API Keys:** Stored in environment variables, not in code
2. **Rate Limiting:** Implemented in Granite client
3. **Input Validation:** Pydantic models for API requests
4. **File Upload:** Type validation and temporary file handling
5. **CORS:** Configurable for production deployment

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

1. **Caching:** IBM Granite responses cached to reduce API calls
2. **Rate Limiting:** Prevents exceeding IBM Cloud quotas
3. **Lazy Loading:** Components initialized only when needed
4. **Async Processing:** FastAPI async endpoints for I/O operations

## Error Handling

1. **Graceful Degradation:** Fallback mechanisms for API failures
2. **Retry Logic:** Automatic retries for transient failures
3. **Logging:** Comprehensive error logging
4. **User Feedback:** Clear error messages in API responses

## Testing Strategy

### Unit Tests (Pending)
- Test individual modules in isolation
- Mock IBM Granite API calls
- Validate data transformations

### Integration Tests (Pending)
- Test complete workflows
- Validate API endpoints
- Test with sample syllabi

### Performance Tests (Pending)
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

- **Backend:** Python 3.8+, FastAPI
- **AI/NLP:** IBM watsonx.ai, IBM Granite, spaCy, NLTK
- **Document Processing:** PyPDF2, pdfplumber, python-docx
- **Export:** ReportLab (PDF), openpyxl (Excel)
- **Configuration:** YAML, python-dotenv
- **Testing:** pytest, pytest-asyncio
- **Frontend (Planned):** React, TypeScript
