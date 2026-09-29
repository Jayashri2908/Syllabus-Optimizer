"""Tests for SyllabusParser"""
import pytest
from src.analysis.syllabus_parser import SyllabusParser


class TestSyllabusParser:
    def test_extract_course_code(self, sample_pdf_text):
        parser = SyllabusParser(use_llm_fallback=False)
        code = parser._extract_course_code(sample_pdf_text)
        assert code == "CS401"

    def test_extract_credits(self, sample_pdf_text):
        parser = SyllabusParser(use_llm_fallback=False)
        credits = parser._extract_credits(sample_pdf_text)
        assert credits == "3-0-2"

    def test_extract_units(self, sample_pdf_text):
        parser = SyllabusParser(use_llm_fallback=False)
        units = parser._extract_units(sample_pdf_text)
        assert len(units) >= 1
        assert units[0]["title"] != ""

    def test_extract_learning_outcomes(self, sample_pdf_text):
        parser = SyllabusParser(use_llm_fallback=False)
        outcomes = parser._extract_learning_outcomes(sample_pdf_text)
        assert len(outcomes) >= 1
        assert outcomes[0]["code"].startswith("CO")

    def test_extract_references(self, sample_pdf_text):
        parser = SyllabusParser(use_llm_fallback=False)
        refs = parser._extract_references(sample_pdf_text)
        assert len(refs) >= 1

    def test_extract_structure(self, sample_pdf_text):
        parser = SyllabusParser(use_llm_fallback=False)
        structure = parser._extract_structure(sample_pdf_text)
        assert structure["course_code"] == "CS401"
        assert structure["credits"] == "3-0-2"
        assert len(structure["units"]) >= 1
        assert len(structure["learning_outcomes"]) >= 1

    def test_extract_course_title(self, sample_pdf_text):
        parser = SyllabusParser(use_llm_fallback=False)
        title = parser._extract_course_title(sample_pdf_text)
        assert "Machine Learning" in title

    def test_extract_co_po_mapping(self):
        parser = SyllabusParser(use_llm_fallback=False)
        text = "CO1: PO1: 3, PO2: 2\nCO2: PO1: 1, PO3: 3"
        mapping = parser._extract_co_po_mapping(text)
        assert "CO1" in mapping
        assert mapping["CO1"]["PO1"] == 3
