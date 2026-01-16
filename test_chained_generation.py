"""
Test script for Staggered LLM Chaining Syllabus Generation
Demonstrates the new chained generation approach with structured JSON outputs
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.generation.chained_generator import ChainedSyllabusGenerator
from src.export.latex_template import LaTeXExporter
from pathlib import Path


def test_chained_generation():
    """Test the staggered LLM chaining approach"""
    
    print("=" * 60)
    print("STAGGERED LLM CHAINING TEST")
    print("=" * 60)
    print()
    
    # Initialize generator
    print("Initializing ChainedSyllabusGenerator...")
    try:
        generator = ChainedSyllabusGenerator()
        print("✓ Generator initialized\n")
    except Exception as e:
        print(f"✗ Failed to initialize generator: {e}")
        return
    
    # Test course info
    course_info = {
        "course_title": "Data Structures and Algorithms",
        "course_code": "CS301",
        "credits": "3-1-0",
        "keywords": [
            "arrays", "linked lists", "stacks", "queues", "trees",
            "graphs", "sorting", "searching", "dynamic programming"
        ],
        "domain": "engineering",
        "program": "B.Tech Computer Science",
        "year": "3rd Year"
    }
    
    print(f"Generating syllabus for: {course_info['course_title']}")
    print(f"Keywords: {', '.join(course_info['keywords'][:5])}...")
    print()
    
    # Generate using staggered chaining
    print("Starting staggered generation...")
    try:
        syllabus = generator.generate_staggered(
            course_info=course_info,
            num_units=5,
            num_outcomes=5,
            verbose=True
        )
        print()
        print("✓ Syllabus generation complete!")
    except Exception as e:
        print(f"✗ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Display results
    print("\n" + "=" * 60)
    print("GENERATED CONTENT")
    print("=" * 60)
    
    # Overview
    print("\n📄 OVERVIEW:")
    print("-" * 40)
    overview = syllabus.get('overview', '')
    print(overview[:500] if overview else "(No overview generated)")
    
    # Objectives
    print("\n🎯 OBJECTIVES:")
    print("-" * 40)
    objectives = syllabus.get('objectives', [])
    for i, obj in enumerate(objectives[:5], 1):
        obj_text = obj if isinstance(obj, str) else obj.get('text', str(obj))
        print(f"  {i}. {obj_text}")
    
    # Learning Outcomes
    print("\n📊 LEARNING OUTCOMES:")
    print("-" * 40)
    outcomes = syllabus.get('learning_outcomes', [])
    for outcome in outcomes[:5]:
        if isinstance(outcome, dict):
            code = outcome.get('code', '')
            desc = outcome.get('description', '')[:60]
            bloom = outcome.get('bloom_level', '')
            print(f"  {code}: {desc}... [{bloom}]")
    
    # Units
    print("\n📚 UNITS:")
    print("-" * 40)
    units = syllabus.get('units', [])
    for unit in units[:5]:
        if isinstance(unit, dict):
            num = unit.get('unit_number', 0)
            title = unit.get('title', '')
            topics = unit.get('topics', [])
            topic_count = len(topics)
            print(f"  Unit {num}: {title} ({topic_count} topics)")
    
    # References
    print("\n📖 REFERENCES:")
    print("-" * 40)
    refs = syllabus.get('references', {})
    textbooks = refs.get('textbooks', [])
    for book in textbooks[:3]:
        print(f"  • {book[:60]}...")
    
    # Quality
    print("\n⭐ QUALITY METRICS:")
    print("-" * 40)
    print(f"  Score: {syllabus.get('quality_score', 'N/A')}")
    print(f"  Grade: {syllabus.get('quality_grade', 'N/A')}")
    print(f"  Generated with chaining: {syllabus.get('generated_with_chaining', False)}")
    
    # Test LaTeX export
    print("\n" + "=" * 60)
    print("LATEX EXPORT TEST")
    print("=" * 60)
    
    try:
        exporter = LaTeXExporter()
        output_path = Path("output") / "test_chained_syllabus.tex"
        output_path.parent.mkdir(exist_ok=True)
        
        result_path = exporter.export(
            syllabus=syllabus,
            output_path=str(output_path),
            compile_pdf=False  # Set to True if LaTeX is installed
        )
        
        print(f"\n✓ LaTeX exported to: {result_path}")
        
        # Show first few lines
        with open(result_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:30]
            print("\nFirst 30 lines of LaTeX output:")
            print("-" * 40)
            for line in lines:
                print(line.rstrip())
        
    except Exception as e:
        print(f"✗ LaTeX export failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


def test_via_syllabus_generator():
    """Test using the main SyllabusGenerator with use_chained_generation flag"""
    
    print("\n" + "=" * 60)
    print("TESTING VIA SYLLABUS_GENERATOR")
    print("=" * 60)
    
    from src.generation.syllabus_generator import SyllabusGenerator
    
    generator = SyllabusGenerator()
    
    syllabus = generator.generate(
        course_title="Machine Learning Fundamentals",
        course_code="CS401",
        credits="3-0-2",
        program_outcomes=["PO1", "PO2", "PO3"],
        keywords=["supervised learning", "neural networks", "deep learning", "classification"],
        domain="engineering",
        use_chained_generation=True  # Use the new staggered chaining
    )
    
    print(f"\n✓ Generated via SyllabusGenerator with chained generation")
    print(f"  Quality: {syllabus.get('quality_grade', 'N/A')} ({syllabus.get('quality_score', 0)})")
    print(f"  Chaining used: {syllabus.get('generated_with_chaining', False)}")


if __name__ == "__main__":
    test_chained_generation()
    
    # Uncomment to also test via SyllabusGenerator
    # test_via_syllabus_generator()
