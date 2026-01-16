
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

# Mock Syllabus Data
mock_syllabus = {
    "course_code": "CS101",
    "course_title": "Introduction to Computer Science",
    "university_name": "Test University",
    "faculty_name": "Faculty of Engineering",
    "department": "Computer Science",
    "credits": "3-0-2",
    "semester": "I",
    "year": "2024-25",
    "overview": "This course provides a foundation in computer science concepts.",
    "objectives": [
        "Understand basic programming concepts",
        "Learn algorithm design",
        "Master Python syntax"
    ],
    "learning_outcomes": [
        {"code": "CO1", "description": "Write basic Python programs", "bloom_level": "Apply"},
        {"code": "CO2", "description": "Analyze algorithms for efficiency", "bloom_level": "Analyze"},
        {"code": "CO3", "description": "Debug code effectively", "bloom_level": "Apply"}
    ],
    "units": [
        {
            "unit_number": 1,
            "title": "Introduction to Programming",
            "hours": 10,
            "topics": [
                "Variables and Data Types",
                "Control Structures",
                {
                    "topic": "Functions",
                    "description": "Defining and calling functions",
                    "subtopics": ["Parameters", "Return values", "Scope"],
                    "key_concepts": ["Modular programming", "Abstraction"]
                }
            ]
        },
        {
            "unit_number": 2,
            "title": "Data Structures",
            "hours": 12,
            "topics": ["Lists", "Dictionaries", "Sets"]
        }
    ],
    "teaching_methodology": {
        "teaching_methods": ["Lectures", "Live Coding"],
        "learning_activities": ["Assignments", "Projects"]
    },
    "assessment_pattern": {
        "Continuous_Assessment": {"weightage": 40},
        "Semester_End_Exam": 60
    },
    "co_po_mapping": {
        "CO1": {"PO1": 3, "PO2": 2},
        "CO2": {"PO1": 2, "PO3": 3},
        "CO3": {"PO1": 3, "PO4": 2}
    },
    "references": {
        "textbooks": ["Python Crash Course"],
        "references": ["Learning Python"]
    }
}

def test_export():
    exporter = PDFExporter()
    output_path = "test_analyze_export.pdf"
    
    print(f"Attempting to export to {output_path}...")
    try:
        success = exporter.export(mock_syllabus, output_path)
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
    test_export()
