"""Tests for GapAnalyzer"""
import pytest
from src.analysis.gap_analyzer import GapAnalyzer


class TestGapAnalyzer:
    def test_analyze_bloom_coverage(self, sample_syllabus_data):
        analyzer = GapAnalyzer()
        result = analyzer._analyze_bloom_coverage(sample_syllabus_data)
        assert result["total_outcomes"] == 3
        assert "level_counts" in result
        assert "percentages" in result

    def test_analyze_co_po_mapping(self, sample_syllabus_data):
        analyzer = GapAnalyzer()
        result = analyzer._analyze_co_po_mapping(sample_syllabus_data)
        assert result["total_cos"] == 3
        assert "coverage_percentage" in result

    def test_analyze_assessment(self, sample_syllabus_data):
        analyzer = GapAnalyzer()
        result = analyzer._analyze_assessment(sample_syllabus_data)
        assert result["total_percentage"] == 100

    def test_analyze_content(self, sample_syllabus_data):
        analyzer = GapAnalyzer()
        result = analyzer._analyze_content(sample_syllabus_data)
        assert result["total_units"] == 2
        assert result["total_hours"] == 22

    def test_analyze_structure(self, sample_syllabus_data):
        analyzer = GapAnalyzer()
        issues = analyzer._analyze_structure(sample_syllabus_data)
        assert isinstance(issues, list)

    def test_generate_recommendations(self, sample_syllabus_data):
        analyzer = GapAnalyzer()
        report = {
            "bloom_coverage": {"gaps": [{"level": "evaluate", "issue": "underrepresented"}]},
            "co_po_mapping_gaps": {"gaps": [{"type": "missing_co_mapping"}]},
            "assessment_gaps": {"gaps": []},
            "content_gaps": {"gaps": []},
            "outcome_validation": {"issues_count": 0, "average_measurability": 0.8},
        }
        recs = analyzer._generate_recommendations(report)
        assert len(recs) > 0
        assert all("priority" in r for r in recs)

    def test_calculate_overall_score(self, sample_syllabus_data):
        analyzer = GapAnalyzer()
        report = {
            "content_quality": {"overall_score": 0.8},
            "bloom_coverage": {"gaps": [], "total_outcomes": 3},
            "co_po_mapping_gaps": {"coverage_percentage": 66.0},
            "assessment_gaps": {"total_percentage": 100, "gaps": []},
            "structural_issues": [],
            "redundancies": {"overlap_score": 0.1},
        }
        score = analyzer._calculate_overall_score(report)
        assert 0 <= score <= 100

    def test_validate_outcomes(self, sample_syllabus_data):
        analyzer = GapAnalyzer()
        result = analyzer._validate_outcomes(sample_syllabus_data)
        assert result["total_outcomes"] == 3
        assert "average_measurability" in result
