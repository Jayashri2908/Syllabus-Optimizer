"""Tests for validators"""
import pytest
from src.validation.syllabus_validator import SyllabusValidator
from src.validation.nep_2020_validator import NEP2020Validator
from src.validation.accreditation_checker import AccreditationChecker


class TestSyllabusValidator:
    def test_validate_complete_syllabus(self, sample_syllabus_data):
        validator = SyllabusValidator()
        result = validator.validate(sample_syllabus_data)
        assert result["score"] > 0
        assert "grade" in result
        assert "issues" in result

    def test_validate_missing_outcomes(self):
        validator = SyllabusValidator()
        data = {"course_title": "Test", "course_code": "T101", "units": []}
        result = validator.validate(data)
        assert result["score"] < 100
        assert any("outcomes" in i.lower() for i in result["issues"])

    def test_calculate_expected_hours(self):
        validator = SyllabusValidator()
        assert validator._calculate_expected_hours("3-0-0") == 45
        assert validator._calculate_expected_hours("3-1-0") == 60

    def test_get_grade(self):
        validator = SyllabusValidator()
        assert "A" in validator._get_grade(95)
        assert "F" in validator._get_grade(30)


class TestNEP2020Validator:
    def test_validate_compliance(self, sample_syllabus_data):
        validator = NEP2020Validator()
        result = validator.validate(sample_syllabus_data)
        assert result["status"] == "success"
        assert "compliance_percentage" in result
        assert "detailed_checks" in result

    def test_check_multidisciplinary(self, sample_syllabus_data):
        validator = NEP2020Validator()
        result = validator._check_multidisciplinary(sample_syllabus_data)
        assert "compliant" in result
        assert "score" in result

    def test_check_obe(self, sample_syllabus_data):
        validator = NEP2020Validator()
        result = validator._check_obe(sample_syllabus_data)
        assert result["has_outcomes"] is True


class TestAccreditationChecker:
    def test_check_nba_compliance(self, sample_syllabus_data):
        checker = AccreditationChecker()
        result = checker.check_nba_compliance(sample_syllabus_data)
        assert result["status"] == "success"
        assert "compliance_percentage" in result

    def test_check_naac_compliance(self, sample_syllabus_data):
        checker = AccreditationChecker()
        result = checker.check_naac_compliance(sample_syllabus_data)
        assert result["status"] == "success"
        assert "compliance_percentage" in result

    def test_check_po_mapping(self, sample_syllabus_data):
        checker = AccreditationChecker()
        result = checker._check_po_mapping(sample_syllabus_data)
        assert "compliant" in result
        assert "coverage" in result

    def test_get_compliance_level(self):
        checker = AccreditationChecker()
        assert checker._get_compliance_level(95) == "Excellent"
        assert checker._get_compliance_level(50) == "Needs Improvement"
