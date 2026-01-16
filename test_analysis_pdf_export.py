
import os
import sys
import logging

# Add project root to path
sys.path.append(os.getcwd())

try:
    from src.export.pdf_exporter import PDFExporter
    print("Successfully imported PDFExporter")
except ImportError as e:
    print(f"Failed to import PDFExporter: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Mock Syllabus Data (Similar to before)
mock_syllabus = {
    "course_code": "CS102",
    "course_title": "Advanced AI",
    "university_name": "Tech Institute",
    "credits": "4-0-0",
    "units": [
        {"title": "Unit 1", "hours": 10, "topics": ["AI Basics", "Search Algorithms"]},
        {"title": "Unit 2", "hours": 12, "topics": ["Machine Learning", "Neural Networks"]}
    ]
}

# Mock Analysis Data (New)
mock_analysis = {
    "content_quality": {
        "quality_score": {
            "total_score": 85,
            "grade": "A",
            "status": "Excellent",
            "breakdown": {"completeness": 22, "clarity": 21, "structure": 25, "relevance": 17}
        }
    },
    "bloom_coverage": {
        "percentages": {
            "remember": 15.5,
            "understand": 25.0,
            "apply": 30.0,
            "analyze": 20.0,
            "evaluate": 5.0,
            "create": 4.5
        }
    },
    "validation_issues": {
        "missing_sections": ["textbooks", "outcomes"]
    },
    "gaps": [
        {"description": "Lack of practical assignments", "severity": "medium"},
        "Syllabus does not mention recent AI ethics guidelines"
    ],
    "recommendations": [
        "Add a section on AI Ethics",
        {"action": "Include hands-on lab sessions", "priority": "high"}
    ]
}

def test_analysis_export():
    exporter = PDFExporter()
    output_path = "test_analysis_report.pdf"
    
    print(f"Attempting to export Analysis Report to {output_path}...")
    try:
        # Pass both syllabus and analysis data
        success = exporter.export(
            syllabus_data=mock_syllabus, 
            output_path=output_path, 
            include_mapping=True,
            analysis_data=mock_analysis
        )
        
        if success:
            print("Export successful!")
            if os.path.exists(output_path):
                print(f"File created: {output_path} ({os.path.getsize(output_path)} bytes)")
            else:
                print("File not found despite success return!")
        else:
            print("Export returned False (failure).")
    except Exception as e:
        print(f"Export raised exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analysis_export()
