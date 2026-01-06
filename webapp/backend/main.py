"""
FastAPI Backend for SCDO
Main API server for syllabus optimization
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import tempfile
import os

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx not installed. Word export will not be available.")

# Import SCDO modules
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.analysis.syllabus_parser import SyllabusParser
from src.analysis.gap_analyzer import GapAnalyzer
from src.analysis.outcome_extractor import OutcomeExtractor
from src.optimization.bloom_mapper import BloomMapper
from src.optimization.content_optimizer import ContentOptimizer
from src.optimization.objectives_optimizer import ObjectivesOptimizer
from src.optimization.reference_suggester import ReferenceSuggester
from src.generation.syllabus_generator import SyllabusGenerator
from src.utils.mock_services import MockContentOptimizer, MockBloomMapper, MockGapAnalyzer # Import Mocks
from src.analysis.rag_analyzer import RAGAwareAnalyzer # RAG
from src.mapping.co_po_mapper import COPOMapper
from src.export.pdf_exporter import PDFExporter
from src.export.excel_exporter import ExcelExporter
from src.ibm.local_storage import LocalStorage
from src.utils.logging_utils import setup_logger

# Setup logging
logger = setup_logger("scdo_api", log_file="logs/api.log")

# Initialize FastAPI app
app = FastAPI(
    title="Syllabus and Curriculum Design Optimizer API",
    description="AI-powered syllabus analysis, optimization, and generation",
    version="1.0.0"
)

# Cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("\n" + "="*50)
print("  SCDO BACKEND SERVER - AI-POWERED ONLY  ")
print("  IBM Granite Integration Required  ")
print("="*50 + "\n")

# Initialize components
parser = None
gap_analyzer = None
outcome_extractor = None
bloom_mapper = None
content_optimizer = None
syllabus_generator = None
co_po_mapper = None
pdf_exporter = None
local_storage = None
objectives_optimizer = None # NEW
reference_suggester = None # NEW

# Initialize critical components (Local)
try:
    parser = SyllabusParser()
    outcome_extractor = OutcomeExtractor()
    co_po_mapper = COPOMapper()
    pdf_exporter = PDFExporter()
    local_storage = LocalStorage()  # FREE local storage instead of cloud
    logger.info("Critical components initialized successfully")
except Exception as e:
    logger.error(f"Critical component initialization failed: {e}")
    # We continue, but API will likely fail on specific endpoints

# Initialize AI components (IBM Cloud) - AI-ONLY MODE
bloom_mapper_initialized = False
content_optimizer_initialized = False
try:
    syllabus_generator = SyllabusGenerator()
    gap_analyzer = GapAnalyzer()
    bloom_mapper = BloomMapper()  # Initialize real BloomMapper
    content_optimizer = ContentOptimizer()  # Initialize real ContentOptimizer
    bloom_mapper_initialized = True
    content_optimizer_initialized = True
    logger.info("✅ AI components initialized successfully (IBM Granite active)")
except Exception as e:
    logger.error(f"❌ AI component initialization failed: {e}")
    logger.error("⚠️  IBM Granite credentials required! Run: python setup_credentials.py")
    logger.warning("Generation endpoint will return error until credentials are configured.")
    
    # Try to initialize RAG analyzer as fallback for analysis
    try:
        gap_analyzer = RAGAwareAnalyzer()
        logger.info("Initialized RAGAwareAnalyzer for analysis")
    except Exception as rag_err:
        logger.warning(f"RAG init failed: {rag_err}, using basic mock")
        gap_analyzer = MockGapAnalyzer()

# Ensure bloom_mapper and content_optimizer are always initialized
if not bloom_mapper_initialized:
    bloom_mapper = MockBloomMapper()
if not content_optimizer_initialized:
    content_optimizer = MockContentOptimizer()



# Pydantic models
class GenerateRequest(BaseModel):
    course_title: str
    course_code: str
    credits: str
    program_outcomes: List[str]
    keywords: List[str]
    domain: str = "engineering"
    num_units: int = 5
    num_outcomes: int = 5


class OptimizeRequest(BaseModel):
    syllabus_data: Dict[str, Any]
    optimization_goals: List[str] = []


class MapRequest(BaseModel):
    course_outcomes: List[Dict[str, str]]
    program_outcomes: Optional[List[str]] = None
    domain: str = "engineering"


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Syllabus and Curriculum Design Optimizer API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SCDO API"}


@app.post("/api/upload")
async def upload_syllabus(file: UploadFile = File(...)):
    """
    Upload and parse syllabus file
    
    Accepts: PDF, DOCX, TXT files
    Returns: Parsed syllabus structure
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        if not local_storage:
             # Fallback to temp file if local_storage failed init (though it shouldn't)
             with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name
        else:
             tmp_path = await local_storage.save_upload(file)
        
        try:
            # Parse syllabus
            if not parser:
                raise HTTPException(status_code=503, detail="Syllabus Parser unavailable")
                
            syllabus_data = parser.parse_file(tmp_path)
            
            return {
                "success": True,
                "filename": file.filename,
                "data": syllabus_data
            }
            
        finally:
            # Clean up temp file if it was a temp file (local_storage files persist)
            if not local_storage and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_syllabus(syllabus_data: Dict[str, Any]):
    """
    Analyze syllabus for gaps and issues
    
    Returns: Comprehensive gap analysis report
    """
    if not gap_analyzer:
        raise HTTPException(status_code=503, detail="Gap Analyzer service unavailable (check IBM credentials)")
        
    try:
        analysis = gap_analyzer.analyze(syllabus_data)
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize")
async def optimize_syllabus(request: OptimizeRequest):
    """
    Get optimization suggestions for syllabus
    
    Returns: Optimization recommendations
    """
    try:
        syllabus_data = request.syllabus_data
        
        # Get Bloom's distribution analysis
        outcomes = syllabus_data.get('learning_outcomes', [])
        bloom_analysis = bloom_mapper.analyze_distribution(outcomes)
        
        # Get rebalancing suggestions
        rebalancing = bloom_mapper.suggest_rebalancing(bloom_analysis)
        
        # Get content optimization suggestions
        units = syllabus_data.get('units', [])
        sequence_opt = content_optimizer.optimize_unit_sequence(units)
        
        # Get modern content suggestions
        course_title = syllabus_data.get('course_title', '')
        current_topics = []
        for unit in units:
            current_topics.extend(unit.get('topics', []))
            
        modern_topics = content_optimizer.suggest_modern_content(
            course_title, current_topics
        )
        
        # Generate CO-PO-PSO mapping matrix
        co_po_mapping = None
        co_po_matrix = None
        
        if co_po_mapper and outcomes:
            try:
                # Extract course outcomes with Bloom's levels
                course_outcomes = []
                for i, outcome in enumerate(outcomes):
                    if isinstance(outcome, dict):
                        course_outcomes.append({
                            'code': outcome.get('code', f'CO{i+1}'),
                            'description': outcome.get('description', ''),
                            'bloom_level': outcome.get('bloom_level', 'Apply')
                        })
                    elif isinstance(outcome, str):
                        course_outcomes.append({
                            'code': f'CO{i+1}',
                            'description': outcome,
                            'bloom_level': 'Apply'
                        })
                
                # Get program outcomes from request or use defaults
                program_outcomes = request.syllabus_data.get('program_outcomes', [
                    'PO1', 'PO2', 'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'PO9'
                ])
                
                # Map course outcomes to program outcomes
                co_po_mapping = co_po_mapper.map_co_to_po(
                    course_outcomes=course_outcomes,
                    program_outcomes=program_outcomes,
                    domain=syllabus_data.get('domain', 'engineering')
                )
                
                # Generate matrix string representation
                co_po_matrix = co_po_mapper.generate_mapping_matrix(co_po_mapping)
                
            except Exception as e:
                logger.error(f"CO-PO mapping failed: {e}")
        
        # NEW: Optimize course objectives
        objectives_optimization = None
        if objectives_optimizer:
            try:
                objectives = syllabus_data.get('objectives', [])
                if objectives:
                    course_info = {
                        'course_title': course_title,
                        'course_level': syllabus_data.get('level', 'undergraduate'),
                        'domain': syllabus_data.get('domain', 'engineering'),
                        'credits': syllabus_data.get('credits', 3)
                    }
                    objectives_optimization = objectives_optimizer.optimize_objectives(objectives, course_info)
            except Exception as e:
                logger.error(f"Objectives optimization failed: {e}")
        
        # NEW: Suggest references
        reference_suggestions = None
        if reference_suggester:
            try:
                current_refs = syllabus_data.get('references', [])
                reference_suggestions = reference_suggester.suggest_references(
                    course_title=course_title,
                    topics=current_topics,
                    domain=syllabus_data.get('domain', 'engineering'),
                    current_references=current_refs
                )
            except Exception as e:
                logger.error(f"Reference suggestion failed: {e}")
        
        # NEW: Validate NEP 2020 compliance
        nep_2020_compliance = None
        try:
            from src.validation.nep_2020_validator import NEP2020Validator
            nep_validator = NEP2020Validator()
            nep_2020_compliance = nep_validator.validate(syllabus_data)
        except Exception as e:
            logger.error(f"NEP 2020 validation failed: {e}")
        
        # NEW: Check accreditation compliance
        accreditation_compliance = None
        try:
            from src.validation.accreditation_checker import AccreditationChecker
            accred_checker = AccreditationChecker()
            accreditation_compliance = {
                'nba': accred_checker.check_nba_compliance(syllabus_data),
                'naac': accred_checker.check_naac_compliance(syllabus_data)
            }
        except Exception as e:
            logger.error(f"Accreditation check failed: {e}")
        
        # Get lesson plan analysis and redundancies from gap_analyzer
        lesson_plan_analysis = None
        redundancies = None
        try:
            # The gap analyzer should have these methods
            if hasattr(gap_analyzer, '_analyze_lesson_plans'):
                lesson_plan_analysis = gap_analyzer._analyze_lesson_plans(syllabus_data)
            if hasattr(gap_analyzer, '_analyze_redundancies'):
                redundancies = gap_analyzer._analyze_redundancies(syllabus_data)
        except Exception as e:
            logger.error(f"Additional analysis failed: {e}")
        
        return {
            'success': True,
            'optimization': {
                'bloom_analysis': bloom_analysis,
                'rebalancing_suggestions': rebalancing,
                'sequence_optimization': sequence_opt,
                'modern_topics': modern_topics,
                'co_po_mapping': co_po_mapping,
                'co_po_matrix': co_po_matrix,
                'lesson_plan_analysis': lesson_plan_analysis,  # Added
                'redundancies': redundancies,  # Added
                'objectives_optimization': objectives_optimization,  # NEW
                'reference_suggestions': reference_suggestions,  # NEW
                'nep_2020_compliance': nep_2020_compliance,  # NEW
                'accreditation_compliance': accreditation_compliance  # NEW
            },
            'syllabus': syllabus_data
        }
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def generate_syllabus(request: GenerateRequest):
    """
    Generate new syllabus from minimal inputs using AI
    
    Requires: IBM Granite credentials configured
    Returns: Complete generated syllabus with quality scoring
    """
    if not syllabus_generator:
        raise HTTPException(
            status_code=503,
            detail="AI Syllabus Generator unavailable. IBM Granite credentials required. Run: python setup_credentials.py"
        )
    
    try:
        syllabus = syllabus_generator.generate(
            course_title=request.course_title,
            course_code=request.course_code,
            credits=request.credits,
            program_outcomes=request.program_outcomes,
            keywords=request.keywords,
            domain=request.domain,
            num_units=request.num_units,
            num_outcomes=request.num_outcomes
        )
        
        return {
            "success": True,
            "syllabus": syllabus
        }
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/map-outcomes")
async def map_outcomes(request: MapRequest):
    """
    Perform CO-PO mapping
    
    Returns: CO-PO mapping matrix and validation
    """
    try:
        # Generate mapping
        mapping = co_po_mapper.map_co_to_po(
            course_outcomes=request.course_outcomes,
            program_outcomes=request.program_outcomes,
            domain=request.domain
        )
        
        # Generate formatted matrix
        matrix_text = co_po_mapper.generate_mapping_matrix(mapping)
        
        # Validate mapping
        validation = co_po_mapper.validate_mapping(mapping)
        
        return {
            "success": True,
            "mapping": mapping,
            "matrix": matrix_text,
            "validation": validation
        }
        
    except Exception as e:
        logger.error(f"Mapping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/pdf")
async def export_pdf(request: OptimizeRequest):
    """
    Export syllabus to PDF
    
    Returns: PDF file
    """
    try:
        # Extract syllabus data from request
        syllabus_data = request.syllabus_data
        
        # Handle nested structure - if data is wrapped, unwrap it
        if 'data' in syllabus_data and isinstance(syllabus_data.get('data'), dict):
            # Frontend sent upload response structure
            syllabus_data = syllabus_data['data']
        elif 'syllabus' in syllabus_data and isinstance(syllabus_data.get('syllabus'), dict):
            # Frontend sent optimize response structure
            syllabus_data = syllabus_data['syllabus']
        
        # Log what we received for debugging
        logger.info(f"Exporting PDF for course: {syllabus_data.get('course_title', 'N/A')}")
        logger.info(f"Data keys: {list(syllabus_data.keys())}")
        
        # Create temp PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # Export to PDF with mapping
        success = pdf_exporter.export(syllabus_data, pdf_path, include_mapping=True)
        
        if not success:
            raise HTTPException(status_code=500, detail="PDF export failed")
        
        # Return PDF file
        filename = f"{syllabus_data.get('course_code', 'syllabus')}.pdf"
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract-outcomes")
async def extract_outcomes(text: str):
    """
    Extract learning outcomes from text
    
    Returns: Extracted and validated outcomes
    """
    try:
        outcomes = outcome_extractor.extract_outcomes(text)
        
        return {
            "success": True,
            "outcomes": outcomes
        }
        
    except Exception as e:
        logger.error(f"Outcome extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate-outcome")
async def validate_outcome(outcome: str):
    """
    Validate a learning outcome
    
    Returns: Validation report with suggestions
    """
    try:
        validation = outcome_extractor.validate_outcome(outcome)
        
        return {
            "success": True,
            "validation": validation
        }
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/excel")
async def export_excel(request: OptimizeRequest):
    """Export syllabus to Excel"""
    try:
        syllabus_data = request.syllabus_data
        
        # Handle nested structure - if data is wrapped, unwrap it
        if 'data' in syllabus_data and isinstance(syllabus_data.get('data'), dict):
            # Frontend sent upload response structure
            syllabus_data = syllabus_data['data']
        elif 'syllabus' in syllabus_data and isinstance(syllabus_data.get('syllabus'), dict):
            # Frontend sent optimize response structure
            syllabus_data = syllabus_data['syllabus']
        
        # Log what we received
        logger.info(f"Exporting Excel for course: {syllabus_data.get('course_title', 'N/A')}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            output_path = tmp.name
            
        excel_exporter = ExcelExporter()
        success = excel_exporter.export_complete_syllabus(
            syllabus_data, output_path, include_mapping=True, include_rubrics=True
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Excel export failed")
            
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=f"{syllabus_data.get('course_code', 'syllabus')}.xlsx"
        )
    except Exception as e:
        logger.error(f"Excel export failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export/word")
async def export_word(request: OptimizeRequest):
    """Export syllabus to Word document"""
    if not DOCX_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Word export not available. python-docx package is not installed."
        )
    
    try:
        syllabus_data = request.syllabus_data
        
        # Handle nested structure - if data is wrapped, unwrap it
        if 'data' in syllabus_data and isinstance(syllabus_data.get('data'), dict):
            syllabus_data = syllabus_data['data']
        elif 'syllabus' in syllabus_data and isinstance(syllabus_data.get('syllabus'), dict):
            syllabus_data = syllabus_data['syllabus']
        
        logger.info(f"Exporting Word for course: {syllabus_data.get('course_title', 'N/A')}")
        
        # Create Word document
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            output_path = tmp.name
        
        doc = Document()
        
        # Add title
        doc.add_heading(syllabus_data.get('course_title', 'Syllabus'), 0)
        
        # Add course info
        doc.add_paragraph(f"Course Code: {syllabus_data.get('course_code', 'N/A')}")
        doc.add_paragraph(f"Credits: {syllabus_data.get('credits', 'N/A')}")
        doc.add_paragraph("")  # Blank line
        
        # Add overview
        if syllabus_data.get('overview'):
            doc.add_heading('Course Overview', 1)
            doc.add_paragraph(syllabus_data['overview'])
        
        # Add learning outcomes
        if syllabus_data.get('learning_outcomes'):
            doc.add_heading('Learning Outcomes', 1)
            for outcome in syllabus_data['learning_outcomes']:
                if isinstance(outcome, dict):
                    text = f"{outcome.get('code', '')}: {outcome.get('description', '')}"
                    if outcome.get('bloom_level'):
                        text += f" ({outcome['bloom_level']})"
                    doc.add_paragraph(text, style='List Bullet')
                else:
                    doc.add_paragraph(str(outcome), style='List Bullet')
        
        # Add units
        if syllabus_data.get('units'):
            doc.add_heading('Course Units', 1)
            for unit in syllabus_data['units']:
                unit_title = f"Unit {unit.get('unit_number', '')}: {unit.get('title', '')}"
                if unit.get('hours'):
                    unit_title += f" ({unit['hours']} hours)"
                doc.add_heading(unit_title, 2)
                
                for topic in unit.get('topics', []):
                    doc.add_paragraph(topic, style='List Bullet')
        
        # Save document
        doc.save(output_path)
        logger.info(f"Word document saved to {output_path}")
        
        return FileResponse(
            output_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=f"{syllabus_data.get('course_code', 'syllabus')}.docx"
        )
        
    except Exception as e:
        logger.error(f"Word export failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
