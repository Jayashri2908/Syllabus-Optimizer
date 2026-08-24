from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from src.analysis.syllabus_parser import SyllabusParser
from src.analysis.gap_analyzer import GapAnalyzer
from src.analysis.outcome_extractor import OutcomeExtractor
from src.optimization.bloom_mapper import BloomMapper
from src.optimization.content_optimizer import ContentOptimizer
from src.optimization.objectives_optimizer import ObjectivesOptimizer
from src.optimization.reference_suggester import ReferenceSuggester
from src.generation.syllabus_generator import SyllabusGenerator
from src.mapping.co_po_mapper import COPOMapper
from src.export.pdf_exporter import PDFExporter
from src.ibm.local_storage import LocalStorage
from src.utils.mock_services import MockContentOptimizer, MockBloomMapper, MockGapAnalyzer
from src.analysis.rag_analyzer import RAGAwareAnalyzer
from src.utils.logging_utils import setup_logger

from app.dependencies import comps, CORS_ORIGINS
from app.routers import system, upload, analyze, generate, mapping, utils, export

logger = setup_logger("scdo_api", log_file="logs/api.log")

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup/shutdown lifecycle: initialize heavy components."""
    try:
        comps.parser = SyllabusParser()
        comps.outcome_extractor = OutcomeExtractor()
        comps.co_po_mapper = COPOMapper()
        comps.pdf_exporter = PDFExporter()
        comps.local_storage = LocalStorage()
        logger.info("Critical components initialized successfully")
    except Exception as e:
        logger.error(f"Critical component initialization failed: {e}")

    bloom_mapper_initialized = False
    content_optimizer_initialized = False
    try:
        comps.syllabus_generator = SyllabusGenerator()
        comps.gap_analyzer = GapAnalyzer()
        comps.bloom_mapper = BloomMapper()
        comps.content_optimizer = ContentOptimizer()
        comps.objectives_optimizer = ObjectivesOptimizer()
        comps.reference_suggester = ReferenceSuggester()
        bloom_mapper_initialized = True
        content_optimizer_initialized = True
        logger.info("[OK] AI components initialized successfully (AI models active)")
    except Exception as e:
        logger.error(f"[ERROR] AI component initialization failed: {e}")
        logger.error("[WARNING] IBM Granite credentials required! Run: python setup_credentials.py")

        try:
            comps.gap_analyzer = RAGAwareAnalyzer()
            logger.info("Initialized RAGAwareAnalyzer for analysis")
        except Exception as rag_err:
            logger.warning(f"RAG init failed: {rag_err}, using basic mock")
            comps.gap_analyzer = MockGapAnalyzer()

    if not bloom_mapper_initialized:
        comps.bloom_mapper = MockBloomMapper()
    if not content_optimizer_initialized:
        comps.content_optimizer = MockContentOptimizer()

    yield

    logger.info("Shutdown complete")

app = FastAPI(
    title="Syllabus and Curriculum Design Optimizer API",
    description="AI-powered syllabus analysis, optimization, and generation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("="*50)
logger.info("  SCDO BACKEND SERVER - AI-POWERED ONLY  ")
logger.info("  IBM Granite Integration Required  ")
logger.info("="*50)

# Include routers
app.include_router(system.router)
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(generate.router)
app.include_router(mapping.router)
app.include_router(utils.router)
app.include_router(export.router)
