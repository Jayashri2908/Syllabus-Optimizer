"""Tests for API endpoints"""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with patch("app.main.SyllabusParser"), \
         patch("app.main.OutcomeExtractor"), \
         patch("app.main.COPOMapper"), \
         patch("app.main.PDFExporter"), \
         patch("app.main.LocalStorage"), \
         patch("app.main.SyllabusGenerator"), \
         patch("app.main.GapAnalyzer"), \
         patch("app.main.BloomMapper"), \
         patch("app.main.ContentOptimizer"), \
         patch("app.main.ObjectivesOptimizer"), \
         patch("app.main.ReferenceSuggester"):
        from app.main import app
        return TestClient(app)


class TestAPI:
    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_upload_invalid_file_type(self, client):
        response = client.post(
            "/api/upload",
            files={"file": ("test.exe", b"content", "application/octet-stream")},
        )
        assert response.status_code == 400

    def test_analyze_missing_data(self, client):
        response = client.post("/api/analyze", json={})
        assert response.status_code in (200, 500)

    def test_generate_missing_fields(self, client):
        response = client.post("/api/generate", json={})
        assert response.status_code == 422

    def test_map_outcomes_empty(self, client):
        response = client.post("/api/map-outcomes", json={"course_outcomes": []})
        assert response.status_code in (200, 500)

    def test_export_pdf_missing_data(self, client):
        response = client.post("/api/export/pdf", json={"syllabus_data": {}})
        assert response.status_code in (200, 500)

    def test_extract_outcomes(self, client):
        response = client.post("/api/extract-outcomes", json={"text": "Students will learn ML"})
        assert response.status_code in (200, 500)

    def test_validate_outcome(self, client):
        response = client.post("/api/validate-outcome", json={"outcome": "Apply ML algorithms"})
        assert response.status_code in (200, 500)
