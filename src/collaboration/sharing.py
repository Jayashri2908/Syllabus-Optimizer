"""Syllabus sharing and version history"""
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class SharingManager:
    def __init__(self):
        self._shares: Dict[str, Dict[str, Any]] = {}

    def create_share(
        self,
        syllabus_data: Dict[str, Any],
        owner_id: str,
        expires_hours: int = 168,
        read_only: bool = True,
    ) -> str:
        share_id = str(uuid.uuid4())[:12]
        self._shares[share_id] = {
            "id": share_id,
            "syllabus_data": syllabus_data,
            "owner_id": owner_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=expires_hours),
            "read_only": read_only,
            "views": 0,
        }
        logger.info(f"Created share {share_id} for owner {owner_id}")
        return share_id

    def get_share(self, share_id: str) -> Optional[Dict[str, Any]]:
        share = self._shares.get(share_id)
        if not share:
            return None
        if datetime.utcnow() > share["expires_at"]:
            del self._shares[share_id]
            return None
        share["views"] += 1
        return share

    def revoke_share(self, share_id: str, owner_id: str) -> bool:
        share = self._shares.get(share_id)
        if share and share["owner_id"] == owner_id:
            del self._shares[share_id]
            return True
        return False

    def list_shares(self, owner_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "id": s["id"],
                "course_title": s["syllabus_data"].get("course_title", "Untitled"),
                "created_at": s["created_at"],
                "expires_at": s["expires_at"],
                "views": s["views"],
            }
            for s in self._shares.values()
            if s["owner_id"] == owner_id
        ]


class VersionManager:
    def __init__(self):
        self._versions: Dict[str, List[Dict[str, Any]]] = {}

    def add_version(
        self,
        syllabus_id: str,
        syllabus_data: Dict[str, Any],
        change_summary: str = "",
    ) -> str:
        version_id = str(uuid.uuid4())[:8]
        if syllabus_id not in self._versions:
            self._versions[syllabus_id] = []

        self._versions[syllabus_id].append({
            "version_id": version_id,
            "syllabus_data": syllabus_data,
            "change_summary": change_summary,
            "created_at": datetime.utcnow(),
        })
        return version_id

    def get_versions(self, syllabus_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "version_id": v["version_id"],
                "change_summary": v["change_summary"],
                "created_at": v["created_at"],
            }
            for v in self._versions.get(syllabus_id, [])
        ]

    def get_version(self, syllabus_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        for v in self._versions.get(syllabus_id, []):
            if v["version_id"] == version_id:
                return v
        return None

    def compare_versions(
        self,
        syllabus_id: str,
        version_id_1: str,
        version_id_2: str,
    ) -> Dict[str, Any]:
        v1 = self.get_version(syllabus_id, version_id_1)
        v2 = self.get_version(syllabus_id, version_id_2)
        if not v1 or not v2:
            return {"error": "Version not found"}

        changes = []
        d1 = v1["syllabus_data"]
        d2 = v2["syllabus_data"]

        if d1.get("course_title") != d2.get("course_title"):
            changes.append({"field": "course_title", "old": d1.get("course_title"), "new": d2.get("course_title")})
        if d1.get("credits") != d2.get("credits"):
            changes.append({"field": "credits", "old": d1.get("credits"), "new": d2.get("credits")})

        return {"changes": changes, "total_changes": len(changes)}


sharing_manager = SharingManager()
version_manager = VersionManager()
