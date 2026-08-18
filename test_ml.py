"""Test ML.pdf parsing with updated OCR settings"""
import sys
sys.path.insert(0, 'd:/Syllabus Optimizer')

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

from src.analysis.syllabus_parser import SyllabusParser


def test_ml_pdf_parsing():
    """Test parsing of ML.pdf with OCR @ 300 DPI + LLM fallback"""
    parser = SyllabusParser()

    print("="*60)
    print("Parsing ML.pdf with OCR @ 300 DPI + LLM fallback...")
    print("="*60)

    result = parser.parse_file('docs/ML.pdf')

    print(f"\nCourse Title: {result.get('course_title', 'N/A')}")
    print(f"Course Code: {result.get('course_code', 'N/A')}")
    print(f"Learning Outcomes: {len(result.get('learning_outcomes', []))}")
    print(f"Units: {len(result.get('units', []))}")

    print("\n--- Units ---")
    for unit in result.get('units', []):
        print(f"  Unit {unit.get('unit_number')}: {unit.get('title')} ({unit.get('hours', 0)} hours)")


if __name__ == "__main__":
    test_ml_pdf_parsing()
