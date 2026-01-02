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

# Import SCDO modules
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.analysis.syllabus_parser import SyllabusParser
from src.analysis.gap_analyzer import GapAnalyzer
from src.analysis.outcome_extractor import OutcomeExtractor
from src.optimization.bloom_mapper import BloomMapper
from src.optimization.content_optimizer import ContentOptimizer
from src.generation.syllabus_generator import SyllabusGenerator
from src.utils.mock_services import MockContentOptimizer, MockBloomMapper, MockGapAnalyzer # Import Mocks
from src.analysis.rag_analyzer import RAGAwareAnalyzer # RAG
from src.mapping.co_po_mapper import COPOMapper
from src.export.pdf_exporter import PDFExporter
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
try:
    syllabus_generator = SyllabusGenerator()
    gap_analyzer = GapAnalyzer()
    bloom_mapper = BloomMapper()
    content_optimizer = ContentOptimizer()
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
        
    # Use mock services for non-critical features
    bloom_mapper = MockBloomMapper()
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
        
        return {
            "success": True,
            "bloom_analysis": bloom_analysis,
            "rebalancing_suggestions": rebalancing,
            "sequence_optimization": sequence_opt,
            "modern_topics": modern_topics
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
async def export_pdf(
    syllabus_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Export syllabus to PDF
    
    Returns: PDF file
    """
    try:
        # Create temp PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # Export to PDF
        success = pdf_exporter.export(syllabus_data, pdf_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="PDF export failed")
        
        # Schedule cleanup
        background_tasks.add_task(os.unlink, pdf_path)
        
        # Return PDF file
        filename = f"{syllabus_data.get('course_code', 'syllabus')}.pdf"
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=filename
        )
        
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
