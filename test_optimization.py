# -*- coding: utf-8 -*-
"""
Test script to verify optimization output - UTF-8 safe version
"""
import sys
import json
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, '.')

from src.analysis.syllabus_parser import SyllabusParser
from src.optimization.bloom_mapper import BloomMapper
from src.mapping.co_po_mapper import COPOMapper

def test_optimization():
    print("=" * 60)
    print("SYLLABUS OPTIMIZATION TEST")
    print("=" * 60)
    
    # Parse syllabus
    parser = SyllabusParser()
    result = parser.parse_file('syllabus/SYLLABUS_AY_2024-25_FYMSCCS_SEM-I_P-24.pdf')
    
    print("\n=== PARSED SYLLABUS DATA ===")
    print(f"Course Title: {result.get('course_title', 'N/A')}")
    print(f"Course Code: {result.get('course_code', 'N/A')}")
    print(f"Number of Units: {len(result.get('units', []))}")
    print(f"Number of Learning Outcomes: {len(result.get('learning_outcomes', []))}")
    print(f"Number of Objectives: {len(result.get('objectives', []))}")
    
    # Show learning outcomes
    print("\n=== LEARNING OUTCOMES ===")
    outcomes = result.get('learning_outcomes', [])
    for i, o in enumerate(outcomes[:5]):
        if isinstance(o, dict):
            print(f"{i+1}. [{o.get('code', 'CO?')}] {o.get('description', '')[:100]}...")
            print(f"   Bloom Level: {o.get('bloom_level', 'N/A')}")
        else:
            print(f"{i+1}. {str(o)[:100]}...")
    
    # Test Bloom mapper
    print("\n=== BLOOM ANALYSIS ===")
    try:
        bloom_mapper = BloomMapper()
        
        # Format outcomes for analysis
        formatted_outcomes = []
        for o in outcomes:
            if isinstance(o, dict):
                formatted_outcomes.append(o)
            else:
                formatted_outcomes.append({'description': str(o), 'bloom_level': 'apply'})
        
        bloom_analysis = bloom_mapper.analyze_distribution(formatted_outcomes)
        print(f"Total Outcomes: {bloom_analysis.get('total_outcomes', 0)}")
        print(f"Level Counts: {bloom_analysis.get('level_counts', {})}")
        print(f"Is Balanced: {bloom_analysis.get('is_balanced', False)}")
        
        # Show comparison
        comparison = bloom_analysis.get('comparison', {})
        print("\nBloom Level Comparison:")
        for level, data in comparison.items():
            status = data['status'].upper()
            print(f"  [{status}] {level.capitalize()}: {data['current']:.1f}% (recommended: {data['recommended_min']}-{data['recommended_max']}%)")
        
        # Get rebalancing suggestions
        suggestions = bloom_mapper.suggest_rebalancing(bloom_analysis)
        if suggestions:
            print("\nRebalancing Suggestions:")
            for s in suggestions:
                print(f"  - {s}")
    except Exception as e:
        print(f"Bloom analysis error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test CO-PO Mapping
    print("\n=== CO-PO MAPPING ===")
    try:
        co_po_mapper = COPOMapper()
        
        # Format course outcomes
        course_outcomes = []
        for i, o in enumerate(outcomes):
            if isinstance(o, dict):
                course_outcomes.append({
                    'code': o.get('code', f'CO{i+1}'),
                    'description': o.get('description', ''),
                    'bloom_level': o.get('bloom_level', 'Apply')
                })
            else:
                course_outcomes.append({
                    'code': f'CO{i+1}',
                    'description': str(o),
                    'bloom_level': 'Apply'
                })
        
        # Map to program outcomes
        mapping = co_po_mapper.map_co_to_po(
            course_outcomes=course_outcomes[:5],  # First 5 COs
            program_outcomes=['PO1', 'PO2', 'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'PO9'],
            domain='engineering'
        )
        
        print("Mapping Matrix:")
        for co, po_data in mapping.items():
            mapped_pos = [f"{po}:{val}" for po, val in po_data.items() if val > 0]
            print(f"  {co}: {', '.join(mapped_pos) if mapped_pos else 'No mappings'}")
    except Exception as e:
        print(f"CO-PO mapping error: {e}")
        import traceback
        traceback.print_exc()
    
    # Show units - investigating the 25 units issue
    print("\n=== UNITS (First 10 for debugging) ===")
    units = result.get('units', [])
    print(f"Total units parsed: {len(units)}")
    
    for i, u in enumerate(units[:10]):
        title = u.get('title', 'Untitled')
        # Sanitize for output
        title = ''.join(c if ord(c) < 128 else '?' for c in str(title))
        print(f"\nUnit {u.get('unit_number', '?')}: {title[:50]} ({u.get('hours', 0)} hours)")
        topics = u.get('topics', [])
        print(f"  Topics count: {len(topics)}")
        for t in topics[:2]:
            topic_str = str(t)[:60]
            topic_str = ''.join(c if ord(c) < 128 else '?' for c in topic_str)
            print(f"    - {topic_str}")
    
    # Save full data to JSON for analysis
    print("\n=== SAVING FULL DATA TO JSON ===")
    with open('test_parsed_data.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, default=str)
    print("Saved to test_parsed_data.json")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_optimization()
