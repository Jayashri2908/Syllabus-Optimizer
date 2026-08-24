from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Syllabus and Curriculum Design Optimizer API",
        "version": "1.0.0",
        "status": "operational"
    }

@router.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SCDO API"}
