"""Data access layer for SCDO"""
import uuid
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

try:
    from . import SQLALCHEMY_AVAILABLE, SyllabusModel, AnalysisModel, SessionLocal
except ImportError:
    SQLALCHEMY_AVAILABLE = False


class SyllabusRepository:
    def __init__(self):
        self._available = SQLALCHEMY_AVAILABLE

    def create(self, course_title: str, course_code: str, data: Dict[str, Any], credits: str = "") -> Optional[str]:
        if not self._available:
            return None
        try:
            db = SessionLocal()
            syllabus_id = str(uuid.uuid4())
            entry = SyllabusModel(
                id=syllabus_id,
                course_title=course_title,
                course_code=course_code,
                credits=credits,
                data=data,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return syllabus_id
        except Exception as e:
            logger.error(f"Failed to create syllabus: {e}")
            return None
        finally:
            db.close()

    def get(self, syllabus_id: str) -> Optional[Dict[str, Any]]:
        if not self._available:
            return None
        try:
            db = SessionLocal()
            entry = db.query(SyllabusModel).filter(SyllabusModel.id == syllabus_id).first()
            return entry.data if entry else None
        except Exception as e:
            logger.error(f"Failed to get syllabus: {e}")
            return None
        finally:
            db.close()

    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not self._available:
            return []
        try:
            db = SessionLocal()
            entries = db.query(SyllabusModel).order_by(SyllabusModel.created_at.desc()).limit(limit).all()
            return [{"id": e.id, "course_title": e.course_title, "course_code": e.course_code, "created_at": e.created_at} for e in entries]
        except Exception as e:
            logger.error(f"Failed to list syllabi: {e}")
            return []
        finally:
            db.close()

    def delete(self, syllabus_id: str) -> bool:
        if not self._available:
            return False
        try:
            db = SessionLocal()
            entry = db.query(SyllabusModel).filter(SyllabusModel.id == syllabus_id).first()
            if entry:
                db.delete(entry)
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete syllabus: {e}")
            return False
        finally:
            db.close()


class AnalysisRepository:
    def __init__(self):
        self._available = SQLALCHEMY_AVAILABLE

    def create(self, syllabus_id: str, analysis_type: str, result: Dict[str, Any]) -> Optional[str]:
        if not self._available:
            return None
        try:
            db = SessionLocal()
            analysis_id = str(uuid.uuid4())
            entry = AnalysisModel(
                id=analysis_id,
                syllabus_id=syllabus_id,
                analysis_type=analysis_type,
                result=result,
                created_at=datetime.utcnow(),
            )
            db.add(entry)
            db.commit()
            return analysis_id
        except Exception as e:
            logger.error(f"Failed to create analysis: {e}")
            return None
        finally:
            db.close()

    def get_by_syllabus(self, syllabus_id: str) -> List[Dict[str, Any]]:
        if not self._available:
            return []
        try:
            db = SessionLocal()
            entries = db.query(AnalysisModel).filter(AnalysisModel.syllabus_id == syllabus_id).all()
            return [{"id": e.id, "type": e.analysis_type, "created_at": e.created_at} for e in entries]
        except Exception as e:
            logger.error(f"Failed to get analyses: {e}")
            return []
        finally:
            db.close()


syllabus_repo = SyllabusRepository()
analysis_repo = AnalysisRepository()
