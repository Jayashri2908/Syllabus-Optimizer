"""Tests for COPOMapper"""
import pytest
from src.mapping.co_po_mapper import COPOMapper


class TestCOPOMapper:
    def test_rule_based_mapping(self):
        mapper = COPOMapper()
        outcomes = [
            {"code": "CO1", "description": "Apply machine learning algorithms", "bloom_level": "apply"},
        ]
        pos = [f"PO{i}" for i in range(1, 13)]
        mapping = mapper._map_co_to_po_rule_based(outcomes, pos, "engineering")
        assert "CO1" in mapping
        assert isinstance(mapping["CO1"], dict)

    def test_calculate_correlation(self):
        mapper = COPOMapper()
        score = mapper._calculate_correlation(
            "Apply machine learning algorithms",
            "apply",
            "PO1",
            "engineering"
        )
        assert 0 <= score <= 3

    def test_generate_mapping_matrix(self):
        mapper = COPOMapper()
        mapping = {"CO1": {"PO1": 3, "PO2": 1}, "CO2": {"PO1": 2}}
        matrix = mapper.generate_mapping_matrix(mapping)
        assert "CO1" in matrix
        assert "PO1" in matrix

    def test_validate_mapping(self):
        mapper = COPOMapper()
        mapping = {"CO1": {"PO1": 3}, "CO2": {"PO2": 2}}
        result = mapper.validate_mapping(mapping)
        assert "is_valid" in result
        assert "po_coverage" in result

    def test_validate_mapping_empty(self):
        mapper = COPOMapper()
        result = mapper.validate_mapping({})
        assert result["is_valid"] is False

    def test_calculate_po_attainment(self):
        mapper = COPOMapper()
        mapping = {"CO1": {"PO1": 3, "PO2": 1}}
        co_attainment = {"CO1": 0.8}
        result = mapper.calculate_po_attainment(mapping, co_attainment)
        assert "PO1" in result
        assert 0 <= result["PO1"] <= 1
