"""
Demo script to test syllabus generation
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.generation.syllabus_generator import SyllabusGenerator
from src.mapping.co_po_mapper import COPOMapper
from src.export.pdf_exporter import PDFExporter
from src.utils.logging_utils import setup_logger
import json

# Setup logging
logger = setup_logger("demo", log_file="logs/demo.log")


def main():
    """Demo syllabus generation"""
    
    print("=" * 60)
    print("SCDO - Syllabus Generation Demo")
    print("=" * 60)
    
    # Initialize components
    print("\n[1/4] Initializing components...")
    generator = SyllabusGenerator()
    mapper = COPOMapper()
    exporter = PDFExporter()
    
    # Sample course details
    print("\n[2/4] Generating syllabus...")
    course_data = {
        'course_title': 'Machine Learning',
        'course_code': 'CS401',
        'credits': '3-0-2',
        'program_outcomes': ['PO1', 'PO2', 'PO3', 'PO5'],
        'keywords': [
            'supervised learning',
            'neural networks',
            'deep learning',
            'classification',
            'regression'
        ],
        'domain': 'engineering',
        'num_units': 5,
        'num_outcomes': 5
    }
    
    # Generate syllabus
    syllabus = generator.generate(**course_data)
    
    print(f"✓ Generated syllabus for: {syllabus['course_title']}")
    print(f"  - Course Outcomes: {len(syllabus['learning_outcomes'])}")
    print(f"  - Units: {len(syllabus['units'])}")
    
    # Generate CO-PO mapping
    print("\n[3/4] Generating CO-PO mapping...")
    mapping = mapper.map_co_to_po(
        course_outcomes=syllabus['learning_outcomes'],
        domain='engineering'
    )
    
    syllabus['co_po_mapping'] = mapping
    
    # Validate mapping
    validation = mapper.validate_mapping(mapping)
    print(f"✓ CO-PO Mapping generated")
    print(f"  - PO Coverage: {validation['po_coverage']:.1f}%")
    print(f"  - Valid: {validation['is_valid']}")
    
    # Export to PDF
    print("\n[4/4] Exporting to PDF...")
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    pdf_path = output_dir / f"{syllabus['course_code']}_syllabus.pdf"
    success = exporter.export(syllabus, str(pdf_path))
    
    if success:
        print(f"✓ PDF exported to: {pdf_path}")
    else:
        print("✗ PDF export failed")
    
    # Save JSON
    json_path = output_dir / f"{syllabus['course_code']}_syllabus.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(syllabus, f, indent=2)
    
    print(f"✓ JSON saved to: {json_path}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    
    # Display sample content
    print("\n--- Sample Course Outcomes ---")
    for outcome in syllabus['learning_outcomes'][:3]:
        print(f"{outcome['code']}: {outcome['description']}")
        print(f"   Bloom's Level: {outcome['bloom_level']}")
    
    print("\n--- Sample Unit ---")
    unit = syllabus['units'][0]
    print(f"Unit {unit['unit_number']}: {unit['title']} ({unit['hours']} hours)")
    for topic in unit['topics'][:3]:
        print(f"  • {topic}")


if __name__ == "__main__":
    main()
