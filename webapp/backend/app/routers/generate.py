from fastapi import APIRouter, HTTPException, Depends

from app.schemas import GenerateRequest
from app.dependencies import verify_api_key, get_components
from src.utils.logging_utils import setup_logger

logger = setup_logger("scdo_api", log_file="logs/api.log")

router = APIRouter(dependencies=[Depends(verify_api_key)])

@router.post("/api/generate")
async def generate_syllabus(request: GenerateRequest, comps=Depends(get_components)):
    """Generate new syllabus from minimal inputs using AI"""
    if not comps.syllabus_generator:
        raise HTTPException(
            status_code=503,
            detail="AI Syllabus Generator unavailable. Check credentials."
        )
    
    try:
        syllabus = comps.syllabus_generator.generate(
            course_title=request.course_title,
            course_code=request.course_code,
            credits=request.credits,
            program=request.program,
            year=request.year,
            course_level=request.course_level,
            program_outcomes=request.program_outcomes,
            keywords=request.keywords,
            unit_topics=request.unit_topics,
            textbooks=request.textbooks,
            references=request.references,
            online_resources=request.online_resources,
            domain=request.domain,
            num_units=request.num_units,
            num_outcomes=request.num_outcomes,
            use_chained_generation=request.use_chained_generation
        )
        
        # Add institution details to syllabus
        syllabus['university_name'] = request.university_name
        syllabus['faculty_name'] = request.faculty_name
        syllabus['department'] = request.department
        syllabus['course_type'] = request.course_type
        syllabus['semester'] = request.semester
        
        return {
            "success": True,
            "syllabus": syllabus
        }
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail="Syllabus generation failed. Check API configurations.")
