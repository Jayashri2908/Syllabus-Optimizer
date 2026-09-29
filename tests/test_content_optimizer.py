"""Tests for ContentOptimizer"""
import pytest
from unittest.mock import MagicMock
from src.optimization.content_optimizer import ContentOptimizer


class TestContentOptimizer:
    def test_optimize_full_syllabus_structure(self, mock_ai_model):
        mock_ai_model.generate_json.return_value = {
            "optimized_syllabus": {
                "course_title": "Optimized ML",
                "course_code": "CS401",
                "learning_outcomes": [{"code": "CO1", "description": "Apply ML", "bloom_level": "apply"}],
                "units": [{"unit_number": 1, "title": "Intro", "hours": 10, "topics": ["Topic 1"]}],
            },
            "changes_summary": [{"aspect": "Units", "original": "2", "optimized": "3"}],
            "bloom_distribution": {"apply": 100},
            "rationale": "Better alignment",
            "industry_relevance_score": 85,
        }
        optimizer = ContentOptimizer(model_manager=mock_ai_model)
        result = optimizer.optimize_full_syllabus({"course_title": "ML", "units": []})
        assert "optimized_syllabus" in result
        assert "changes_summary" in result
        assert result["industry_relevance_score"] == 85

    def test_optimize_passes_correct_parameters(self, mock_ai_model):
        mock_ai_model.generate_json.return_value = {
            "optimized_syllabus": {"course_title": "Test"},
            "changes_summary": [],
            "bloom_distribution": {},
            "rationale": "",
        }
        optimizer = ContentOptimizer(model_manager=mock_ai_model)
        optimizer.optimize_full_syllabus({"course_title": "Test Course"})
        call_kwargs = mock_ai_model.generate_json.call_args.kwargs
        assert call_kwargs["task_type"] == "optimization"
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["max_tokens"] == 4096
        assert "Test Course" in call_kwargs["prompt"]

    def test_validate_optimization_hours_match(self, mock_ai_model):
        mock_ai_model.generate_json.return_value = {
            "optimized_syllabus": {
                "units": [{"unit_number": 1, "title": "A", "hours": 10}],
            },
            "changes_summary": [],
            "bloom_distribution": {},
            "rationale": "",
        }
        optimizer = ContentOptimizer(model_manager=mock_ai_model)
        original = {"units": [{"unit_number": 1, "title": "A", "hours": 10}]}
        result = optimizer.optimize_full_syllabus(original)
        assert result is not None

    def test_validate_optimization_hours_mismatch(self, mock_ai_model):
        mock_ai_model.generate_json.return_value = {
            "optimized_syllabus": {
                "units": [{"unit_number": 1, "title": "A", "hours": 15}],
            },
            "changes_summary": [],
            "bloom_distribution": {},
            "rationale": "",
        }
        optimizer = ContentOptimizer(model_manager=mock_ai_model)
        original = {"units": [{"unit_number": 1, "title": "A", "hours": 10}]}
        result = optimizer.optimize_full_syllabus(original)
        assert result is not None
