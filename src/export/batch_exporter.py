"""Batch export functionality for SCDO"""
import os
import logging
import tempfile
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class BatchExporter:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def export_multiple(
        self,
        syllabi: List[Dict[str, Any]],
        output_dir: str,
        format: str = "pdf",
    ) -> Dict[str, Any]:
        os.makedirs(output_dir, exist_ok=True)
        results = {"successful": [], "failed": []}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for i, syllabus in enumerate(syllabi):
                course_code = syllabus.get("course_code", f"syllabus_{i}")
                output_path = os.path.join(output_dir, f"{course_code}.{format}")
                future = executor.submit(self._export_single, syllabus, output_path, format)
                futures[future] = course_code

            for future in as_completed(futures):
                course_code = futures[future]
                try:
                    success = future.result()
                    if success:
                        results["successful"].append(course_code)
                    else:
                        results["failed"].append(course_code)
                except Exception as e:
                    logger.error(f"Batch export failed for {course_code}: {e}")
                    results["failed"].append(course_code)

        logger.info(f"Batch export complete: {len(results['successful'])} succeeded, {len(results['failed'])} failed")
        return results

    def _export_single(
        self,
        syllabus_data: Dict[str, Any],
        output_path: str,
        format: str,
    ) -> bool:
        try:
            if format == "pdf":
                from src.export.pdf_exporter import PDFExporter
                exporter = PDFExporter()
                return exporter.export(syllabus_data, output_path)
            elif format == "excel":
                from src.export.excel_exporter import ExcelExporter
                exporter = ExcelExporter()
                return exporter.export_complete_syllabus(syllabus_data, output_path)
            elif format == "json":
                from src.export.json_exporter import JSONExporter
                exporter = JSONExporter()
                return exporter.export(syllabus_data, output_path)
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False
