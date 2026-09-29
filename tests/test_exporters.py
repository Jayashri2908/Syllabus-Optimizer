"""Tests for exporters"""
import pytest
import os
import tempfile
from src.export.excel_exporter import ExcelExporter


class TestExcelExporter:
    def test_export_complete_syllabus(self, sample_syllabus_data):
        exporter = ExcelExporter()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            output_path = f.name
        try:
            result = exporter.export_complete_syllabus(sample_syllabus_data, output_path)
            assert result is True
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_export_mapping_only(self, sample_syllabus_data):
        sample_syllabus_data["co_po_mapping"] = {"CO1": {"PO1": 3}}
        exporter = ExcelExporter()
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            output_path = f.name
        try:
            result = exporter.export_mapping_only(sample_syllabus_data, output_path)
            assert result is True
            assert os.path.exists(output_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
