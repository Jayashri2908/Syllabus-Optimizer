from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.dependencies import verify_api_key, get_components
from src.utils.logging_utils import setup_logger

logger = setup_logger("scdo_api", log_file="logs/api.log")

router = APIRouter(dependencies=[Depends(verify_api_key)])


class ExtractOutcomesRequest(BaseModel):
    text: str


class ValidateOutcomeRequest(BaseModel):
    outcome: str


@router.post("/api/extract-outcomes")
async def extract_outcomes(request: ExtractOutcomesRequest, comps=Depends(get_components)):
    """Extract learning outcomes from text"""
    try:
        outcomes = comps.outcome_extractor.extract_outcomes(request.text)
        return {
            "success": True,
            "outcomes": outcomes
        }
    except Exception as e:
        logger.error(f"Outcome extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Outcome extraction failed")


@router.post("/api/validate-outcome")
async def validate_outcome(request: ValidateOutcomeRequest, comps=Depends(get_components)):
    """Validate a learning outcome"""
    try:
        validation = comps.outcome_extractor.validate_outcome(request.outcome)
        return {
            "success": True,
            "validation": validation
        }
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail="Outcome validation failed")
