# SCDO - Syllabus and Curriculum Design Optimizer

An AI-powered system for analyzing, optimizing, and generating academic syllabi using **OpenRouter** (Nvidia Nemotron) and **Google Gemini** — both free.

## Features

- **Syllabus Analysis**: Parse and extract structured information from PDF/DOCX syllabi
- **Gap Analysis**: Identify gaps in Bloom's taxonomy coverage, CO-PO mappings, and assessment patterns
- **Content Optimization**: AI-powered suggestions for improving syllabus content
- **Syllabus Generation**: Generate complete syllabi from minimal inputs
- **CO-PO Mapping**: Intelligent mapping of Course Outcomes to Program Outcomes
- **Export**: Generate professional PDF documents and Excel mapping sheets

## Project Structure

```
d:/Syllabus Optimizer/
├── src/
│   ├── analysis/          # Syllabus parsing and gap analysis
│   ├── optimization/      # Bloom's mapper and content optimizer
│   ├── generation/        # Syllabus generator
│   ├── mapping/           # CO-PO mapping utilities
│   ├── export/            # PDF/Excel exporters
│   ├── rag/               # Vector store and RAG retrieval
│   └── utils/             # Utilities and helpers
├── webapp/
│   └── backend/          # FastAPI server
├── configs/              # Configuration files
├── templates/            # Syllabus templates
├── scripts/              # Demo and utility scripts
└── tests/               # Unit and integration tests
```

## Installation

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLP Models (Optional)

```bash
python -m spacy download en_core_web_sm
```

### 5. Frontend Setup
```bash
cd webapp/frontend
npm install
```

## Configuration

### Environment Variables

Copy the example environment file and update it with your credentials:

```bash
# Windows (PowerShell)
cp .env.example .env

# Linux/Mac
cp .env.example .env
```

Open `.env` and populate the following keys:
- `OPENROUTER_API_KEY`: Required for primary AI features (get from [openrouter.ai](https://openrouter.ai))
- `GEMINI_API_KEY`: Optional fallback (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

## Usage

### Running the API Server

```bash
cd webapp/backend
python main.py
```

API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Demo Script

Generate a sample syllabus:

```bash
python scripts/sample_syllabus_gen.py
```

### Python API

```python
from src.generation.syllabus_generator import SyllabusGenerator
from src.mapping.co_po_mapper import COPOMapper

# Generate syllabus
generator = SyllabusGenerator()
syllabus = generator.generate(
    course_title="Machine Learning",
    course_code="CS401",
    credits="3-0-2",
    program_outcomes=["PO1", "PO2", "PO3"],
    keywords=["neural networks", "deep learning"]
)

# Generate CO-PO mapping
mapper = COPOMapper()
mapping = mapper.map_co_to_po(
    course_outcomes=syllabus['learning_outcomes']
)
```

## API Endpoints

- `POST /api/upload` - Upload and parse syllabus file
- `POST /api/analyze` - Analyze syllabus for gaps
- `POST /api/optimize` - Get optimization suggestions
- `POST /api/generate` - Generate new syllabus
- `POST /api/map-outcomes` - Perform CO-PO mapping
- `POST /api/export/pdf` - Export syllabus to PDF

## Accreditation Standards

The system supports:
- **NBA** (National Board of Accreditation) - India
- **NAAC** (National Assessment and Accreditation Council) - India
- **NEP 2020** (National Education Policy 2020) - India
- **ABET** (Accreditation Board for Engineering and Technology) - International

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

## License

This project is developed for academic purposes.

## Acknowledgments

- OpenRouter and Nvidia Nemotron for free AI capabilities
- Google Gemini for fallback AI capabilities
- Bloom's Taxonomy framework for learning outcome classification
- NBA, NAAC, and NEP 2020 for accreditation standards

## Support

For issues and questions, please refer to the project documentation or contact the development team.
