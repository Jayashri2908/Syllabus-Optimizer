from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import Dict, Any
from pathlib import Path
import tempfile
import os
import re

from app.dependencies import verify_api_key, MAX_UPLOAD_SIZE, get_components
from src.utils.logging_utils import setup_logger

logger = setup_logger("scdo_api", log_file="logs/api.log")

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.post("/api/upload")
async def upload_syllabus(file: UploadFile = File(...), comps=Depends(get_components)):
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
                
            syllabus_data = comps.parser.parse_file(tmp_path)
            
            logger.info(f"Successfully parsed syllabus: {file.filename} ({len(syllabus_data.get('units', []))} units)")
            
            return {
                "success": True,
                "filename": file.filename,
                "data": syllabus_data
            }
            
        finally:
            if not comps.local_storage and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
