"""JSON export for SCDO"""
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONExporter:
    def export(self, syllabus_data: Dict[str, Any], output_path: str) -> bool:
        try:
            export_data = {
                "metadata": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "format": "json",
                    "version": "1.0",
                },
                "syllabus": syllabus_data,
            }
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"JSON exported to {output_path}")
            return True
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return False

    def export_batch(
        self,
        syllabi: List[Dict[str, Any]],
        output_path: str,
    ) -> bool:
        try:
            export_data = {
                "metadata": {
                    "exported_at": datetime.utcnow().isoformat(),
                    "format": "json",
                    "version": "1.0",
                    "count": len(syllabi),
                },
                "syllabi": syllabi,
            }
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Batch JSON exported ({len(syllabi)} items) to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Batch JSON export failed: {e}")
            return False

    def to_dict(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "metadata": {
                "exported_at": datetime.utcnow().isoformat(),
                "format": "json",
                "version": "1.0",
            },
            "syllabus": syllabus_data,
        }
