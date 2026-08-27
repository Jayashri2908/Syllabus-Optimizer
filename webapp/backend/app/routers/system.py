from fastapi import APIRouter, Depends
from app.dependencies import get_components, Components

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
async def health_check(comps: Components = Depends(get_components)):
    """Health check with downstream dependency verification"""
    result = {
        "status": "healthy",
        "service": "SCDO API",
    }

    # Check ChromaDB connectivity
    try:
        from src.rag.vector_store import VectorStore
        vs = VectorStore()
        count = vs.collection.count()
        result["chromadb"] = "connected" if count >= 0 else "error"
        result["chromadb_documents"] = count
    except Exception as e:
        result["chromadb"] = f"unavailable"
        result["status"] = "degraded"

    # Check LLM model availability
    try:
        from src.ai.model_manager import ModelManager
        import yaml
        from pathlib import Path

        config_path = Path(__file__).resolve().parents[3] / "configs" / "ai_models.yaml"
        config = {}
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)

        manager = ModelManager(config)
        available = list(manager.models.keys())
        if available:
            result["llm"] = f"{','.join(available)}/active"
        else:
            result["llm"] = "no_models_configured"
            result["status"] = "degraded"
    except Exception:
        result["llm"] = "unavailable"
        result["status"] = "degraded"

    return result
