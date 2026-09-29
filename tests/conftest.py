"""Shared test fixtures for SCDO"""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def sample_syllabus_data():
    return {
        "course_title": "Machine Learning",
        "course_code": "CS401",
        "credits": "3-0-2",
        "prerequisites": ["Python Programming", "Linear Algebra"],
        "objectives": [
            "Understand ML algorithms",
            "Apply ML to real problems",
        ],
        "learning_outcomes": [
            {"code": "CO1", "description": "Apply supervised learning algorithms", "bloom_level": "apply"},
            {"code": "CO2", "description": "Analyze model performance metrics", "bloom_level": "analyze"},
            {"code": "CO3", "description": "Design ML pipelines", "bloom_level": "create"},
        ],
        "units": [
            {
                "unit_number": 1,
                "title": "Introduction to ML",
                "topics": ["Supervised learning", "Unsupervised learning"],
                "hours": 10,
            },
            {
                "unit_number": 2,
                "title": "Neural Networks",
                "topics": ["Perceptrons", "Backpropagation", "CNNs"],
                "hours": 12,
            },
        ],
        "assessment_pattern": {
            "internal": {"weightage": 40, "components": {"midterm": 20, "assignments": 20}},
            "external": {"weightage": 60, "components": {"final": 60}},
        },
        "references": ["Bishop - Pattern Recognition", "Goodfellow - Deep Learning"],
        "co_po_mapping": {"CO1": {"PO1": 3, "PO2": 2}},
    }


@pytest.fixture
def mock_ai_model():
    mock = MagicMock()
    mock.generate.return_value = "Mock AI response"
    mock.generate_json.return_value = {"result": "mock"}
    mock.is_available.return_value = True
    return mock


@pytest.fixture
def sample_pdf_text():
    return """
    CS401: Machine Learning
    Course Type: DSC
    Credits: 3-0-2

    Course Outcomes:
    1. Apply supervised learning algorithms to classification problems
    2. Analyze model performance using various metrics
    3. Design ML pipelines for real-world applications

    Unit No 1: Introduction to ML 10 Hours
    Supervised learning
    Unsupervised learning

    Unit No 2: Neural Networks 12 Hours
    Perceptrons
    Backpropagation
    CNNs

    References:
    1. Bishop - Pattern Recognition and Machine Learning
    2. Goodfellow - Deep Learning
    """
