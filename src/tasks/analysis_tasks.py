"""Background analysis tasks"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from . import celery_app
    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False


def _analyze_syllabus_task(syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from src.analysis.gap_analyzer import GapAnalyzer
        analyzer = GapAnalyzer()
        result = analyzer.analyze(syllabus_data)
        return {"success": True, "analysis": result}
    except Exception as e:
        logger.error(f"Analysis task failed: {e}")
        return {"success": False, "error": str(e)}


def _optimize_syllabus_task(syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        from src.optimization.content_optimizer import ContentOptimizer
        optimizer = ContentOptimizer()
        result = optimizer.optimize_full_syllabus(syllabus_data)
        return {"success": True, "optimization": result}
    except Exception as e:
        logger.error(f"Optimization task failed: {e}")
        return {"success": False, "error": str(e)}


if TASKS_AVAILABLE:
    @celery_app.task(bind=True, name="tasks.analyze_syllabus")
    def analyze_syllabus_task(self, syllabus_data: Dict[str, Any]):
        self.update_state(state="PROGRESS", meta={"progress": 10, "status": "Starting analysis"})
        result = _analyze_syllabus_task(syllabus_data)
        self.update_state(state="PROGRESS", meta={"progress": 100, "status": "Complete"})
        return result

    @celery_app.task(bind=True, name="tasks.optimize_syllabus")
    def optimize_syllabus_task(self, syllabus_data: Dict[str, Any]):
        self.update_state(state="PROGRESS", meta={"progress": 10, "status": "Starting optimization"})
        result = _optimize_syllabus_task(syllabus_data)
        self.update_state(state="PROGRESS", meta={"progress": 100, "status": "Complete"})
        return result
else:
    def analyze_syllabus_task(syllabus_data: Dict[str, Any]):
        return _analyze_syllabus_task(syllabus_data)

    def optimize_syllabus_task(syllabus_data: Dict[str, Any]):
        return _optimize_syllabus_task(syllabus_data)
