from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import time
import uuid

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

from app.dependencies import comps, CORS_ORIGINS, IS_PRODUCTION
from app.routers import system, upload, analyze, generate, mapping, utils, export

logger = setup_logger("scdo_api", log_file="logs/api.log")


@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        comps.parser = SyllabusParser()
        comps.outcome_extractor = OutcomeExtractor()
        comps.co_po_mapper = COPOMapper()
        comps.pdf_exporter = PDFExporter()
        comps.local_storage = LocalStorage()
        logger.info("Critical components initialized successfully")
    except Exception as e:
        logger.critical(f"Critical component initialization failed: {e}")
        raise RuntimeError(f"Cannot start server — critical component failed: {e}") from e

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
        logger.info("AI components initialized successfully (AI models active)")
    except Exception as e:
        logger.error(f"AI component initialization failed: {e}")
        logger.error("Set OPENROUTER_API_KEY or GEMINI_API_KEY for AI features")

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


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start_time = time.time()

    logger.info(f"[{request_id}] {request.method} {request.url.path} - Started")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}s"
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Completed {response.status_code} in {process_time:.3f}s"
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Failed {type(e).__name__}: {e} in {process_time:.3f}s"
        )
        raise


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id}] Unhandled exception on {request.method} {request.url.path}: {exc}")
    import traceback
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error.",
            "error_code": "INTERNAL_ERROR",
            "request_id": request_id
        }
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

logger.info("=" * 50)
logger.info("  SCDO BACKEND SERVER  ")
logger.info("  OpenRouter + Gemini  ")
logger.info(f"  Environment: {'production' if IS_PRODUCTION else 'development'}")
logger.info("=" * 50)

app.include_router(system.router)
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(generate.router)
app.include_router(mapping.router)
app.include_router(utils.router)
app.include_router(export.router)
