"""Background export tasks"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    from . import celery_app
    TASKS_AVAILABLE = True
except ImportError:
    TASKS_AVAILABLE = False


def _export_pdf_task(syllabus_data: Dict[str, Any], output_path: str, **kwargs) -> Dict[str, Any]:
    try:
        from src.export.pdf_exporter import PDFExporter
        exporter = PDFExporter()
        success = exporter.export(syllabus_data, output_path, **kwargs)
        return {"success": success, "output_path": output_path}
    except Exception as e:
        logger.error(f"PDF export task failed: {e}")
        return {"success": False, "error": str(e)}


def _export_excel_task(syllabus_data: Dict[str, Any], output_path: str, **kwargs) -> Dict[str, Any]:
    try:
        from src.export.excel_exporter import ExcelExporter
        exporter = ExcelExporter()
        success = exporter.export_complete_syllabus(syllabus_data, output_path, **kwargs)
        return {"success": success, "output_path": output_path}
    except Exception as e:
        logger.error(f"Excel export task failed: {e}")
        return {"success": False, "error": str(e)}


if TASKS_AVAILABLE:
    @celery_app.task(bind=True, name="tasks.export_pdf")
    def export_pdf_task(self, syllabus_data: Dict[str, Any], output_path: str, **kwargs):
        self.update_state(state="PROGRESS", meta={"progress": 10, "status": "Starting PDF export"})
        result = _export_pdf_task(syllabus_data, output_path, **kwargs)
        self.update_state(state="PROGRESS", meta={"progress": 100, "status": "Complete"})
        return result

    @celery_app.task(bind=True, name="tasks.export_excel")
    def export_excel_task(self, syllabus_data: Dict[str, Any], output_path: str, **kwargs):
        self.update_state(state="PROGRESS", meta={"progress": 10, "status": "Starting Excel export"})
        result = _export_excel_task(syllabus_data, output_path, **kwargs)
        self.update_state(state="PROGRESS", meta={"progress": 100, "status": "Complete"})
        return result
else:
    def export_pdf_task(syllabus_data: Dict[str, Any], output_path: str, **kwargs):
        return _export_pdf_task(syllabus_data, output_path, **kwargs)

    def export_excel_task(syllabus_data: Dict[str, Any], output_path: str, **kwargs):
        return _export_excel_task(syllabus_data, output_path, **kwargs)
