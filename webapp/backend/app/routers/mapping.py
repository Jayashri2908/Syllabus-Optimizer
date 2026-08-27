from fastapi import APIRouter, HTTPException, Depends
from app.schemas import MapRequest
from app.dependencies import verify_api_key, get_components
from src.utils.logging_utils import setup_logger

logger = setup_logger("scdo_api", log_file="logs/api.log")

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.post("/api/map-outcomes")
async def map_outcomes(request: MapRequest, comps=Depends(get_components)):
    """Perform CO-PO mapping"""
    try:
        mapping = comps.co_po_mapper.map_co_to_po(
            course_outcomes=request.course_outcomes,
            program_outcomes=request.program_outcomes,
            domain=request.domain
        )
        matrix_text = comps.co_po_mapper.generate_mapping_matrix(mapping)
        validation = comps.co_po_mapper.validate_mapping(mapping)
        
        return {
            "success": True,
            "mapping": mapping,
            "matrix": matrix_text,
            "validation": validation
        }
    except Exception as e:
        logger.error(f"Mapping failed: {e}")
        raise HTTPException(status_code=500, detail="CO-PO mapping failed. Please try again.")
