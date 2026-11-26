from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Dict, Any
from pathlib import Path
import tempfile
import os
import re

from app.dependencies import verify_api_key, MAX_UPLOAD_SIZE, get_components, get_cache_key, llm_cache, CACHE_TTL
from src.utils.logging_utils import setup_logger
from src.analysis.syllabus_parser import PDFParsingError, NoTextExtractedError

logger = setup_logger("scdo_api", log_file="logs/api.log")

router = APIRouter(dependencies=[Depends(verify_api_key)])


def _http_from_parse_error(exc: Exception, default_detail: str, default_status: int = 422) -> HTTPException:
    """Map a parser exception to a user-facing HTTPException with a helpful message."""
    if isinstance(exc, PDFParsingError):
        return HTTPException(status_code=400, detail=f"This PDF cannot be parsed: {exc}. Please re-export or upload the original.")
    if isinstance(exc, NoTextExtractedError):
        return HTTPException(
            status_code=422,
            detail=(
                "Could not extract any text from this PDF. "
                "It may be a scanned image without OCR, a password-protected file, "
                "or a non-PDF file with a .pdf extension. "
                "Try exporting it as text from your PDF viewer, or install Tesseract OCR "
                "(https://github.com/tesseract-ocr/tesseract) so we can read scanned pages."
            ),
        )
    return HTTPException(status_code=default_status, detail=f"{default_detail}: {exc}")


@router.post("/api/upload")
async def upload_syllabus(file: UploadFile = File(...), comps=Depends(get_components)):
    """
    Upload and parse syllabus file
    Accepts: PDF, DOCX, TXT files
    Returns: Parsed syllabus structure + parser diagnostics
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

        # Sanitize filename
        safe_filename = re.sub(r'[^\w\s\-.]', '_', Path(file.filename).stem) + file_ext

        # Read and validate size
        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_UPLOAD_SIZE // (1024*1024)} MB"
            )

        # Save temporarily
        if not comps.local_storage:
             with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
        else:
             tmp_path = await comps.local_storage.save_upload(file, content=content, filename=safe_filename)

        try:
            if not comps.parser:
                raise HTTPException(status_code=503, detail="Syllabus Parser unavailable")

            try:
                syllabus_data = comps.parser.parse_file(tmp_path)
            except (PDFParsingError, NoTextExtractedError) as parse_err:
                logger.warning(f"Parse failure for {file.filename}: {parse_err}")
                raise _http_from_parse_error(parse_err, "File parse failed")

            diagnostics = syllabus_data.get("parser_diagnostics", {}) or {}
            logger.info(
                f"Successfully parsed syllabus: {file.filename} "
                f"(units={len(syllabus_data.get('units', []))}, "
                f"outcomes={len(syllabus_data.get('learning_outcomes', []))}, "
                f"engine={diagnostics.get('engine_used')}, ocr={diagnostics.get('ocr_used')})"
            )

            return {
                "success": True,
                "filename": file.filename,
                "data": syllabus_data,
                "parser_diagnostics": diagnostics,
            }

        finally:
            if not comps.local_storage and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Upload failed unexpectedly: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed unexpectedly: {type(e).__name__}: {e}")


@router.post("/api/upload-and-analyze")
async def upload_and_analyze(file: UploadFile = File(...), comps=Depends(get_components)):
    """
    Combined upload + parse + analyze in a single request.
    Eliminates the extra HTTP round-trip of calling /upload then /analyze separately.
    Returns both parsed data and analysis results.
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

        # Sanitize filename
        safe_filename = re.sub(r'[^\w\s\-.]', '_', Path(file.filename).stem) + file_ext

        # Read and validate size
        content = await file.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_UPLOAD_SIZE // (1024*1024)} MB"
            )

        # Save temporarily
        if not comps.local_storage:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
        else:
            tmp_path = await comps.local_storage.save_upload(file, content=content, filename=safe_filename)

        try:
            # 1. Parse
            if not comps.parser:
                raise HTTPException(status_code=503, detail="Syllabus Parser unavailable")

            try:
                syllabus_data = comps.parser.parse_file(tmp_path)
            except (PDFParsingError, NoTextExtractedError) as parse_err:
                logger.warning(f"Parse failure for {file.filename}: {parse_err}")
                raise _http_from_parse_error(parse_err, "File parse failed")

            diagnostics = syllabus_data.get("parser_diagnostics", {}) or {}
            logger.info(
                f"Parsed syllabus: {file.filename} "
                f"(units={len(syllabus_data.get('units', []))}, "
                f"engine={diagnostics.get('engine_used')}, ocr={diagnostics.get('ocr_used')})"
            )

            # 2. Analyze (with cache check)
            course_title = syllabus_data.get('course_title', 'Unknown')
            analysis = None
            cache_hit = False

            if not comps.gap_analyzer:
                logger.warning("Gap Analyzer unavailable — returning parsed data without analysis")
            else:
                if llm_cache is not None:
                    key = get_cache_key("analyze", syllabus_data)
                    cached = llm_cache.get(key)
                    if cached is not None:
                        analysis = cached
                        cache_hit = True
                        logger.info(f"Cache HIT for analysis of '{course_title}'")

                if not cache_hit:
                    logger.info(f"Analyzing syllabus for course: {course_title}")
                    analysis = comps.gap_analyzer.analyze(syllabus_data)
                    if llm_cache is not None:
                        llm_cache.set(key, analysis, expire=CACHE_TTL)

            return {
                "success": True,
                "filename": file.filename,
                "data": syllabus_data,
                "analysis": analysis,
                "cached": cache_hit,
                "parser_diagnostics": diagnostics,
            }

        finally:
            if not comps.local_storage and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Upload-and-analyze failed unexpectedly: {e}")
        raise HTTPException(status_code=500, detail=f"Upload and analysis failed: {type(e).__name__}: {e}")
