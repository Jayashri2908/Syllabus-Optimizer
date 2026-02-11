import unittest
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.generation.syllabus_generator import SyllabusGenerator

class MockAI:
    def __init__(self):
        self.models = {'mock': 'mock'}

    def generate_json(self, schema=None, **kwargs):
        schema_name = schema.__name__ if schema else "None"
        
        if schema_name == 'OverviewSection':
            return {"overview_text": "Mock overview text."}
        elif schema_name == 'ObjectivesSection':
            return {"objectives": [{"text": "Mock objective 1"}]}
        elif schema_name == 'LearningOutcomesSection':
            return {"outcomes": [{"code": "CO1", "description": "Mock outcome", "bloom_level": "apply"}]}
        elif schema_name == 'UnitsSection':
            return {"units": [{
                "unit_number": 1,
                "title": "Mock Unit",
                "topics": [{"topic": "Mock Topic"}],
                "hours": 10
            }]}
        elif schema_name == 'ReferencesSection':
            return {
                "textbooks": ["Mock Textbook 1", "Mock Textbook 2"],
                "reference_books": ["Mock Ref 1"],
                "online_resources": ["Mock Online 1"]
            }
        return {}
    
    def generate(self, **kwargs):
        # Fallback for any legacy calls (though we shouldn't have many left for core sections)
        return "Legacy text response"

class TestGenerationFix(unittest.TestCase):
    def test_references_structure(self):
        generator = SyllabusGenerator()
        generator.ai = MockAI() # Inject mock
        
        # Test generate_references directly
        refs = generator._generate_references("Test Course", ["keyword"])
        
        print(f"\nGenerated Refs: {refs}")
        
        self.assertEqual(refs['textbooks'], ["Mock Textbook 1", "Mock Textbook 2"])
        self.assertEqual(refs['references'], ["Mock Ref 1"])
        
    def test_full_generation_flow(self):
        generator = SyllabusGenerator()
        generator.ai = MockAI() # Inject mock
        
        # Mock other dependencies if needed, but simple generating might work if dependencies are light
        # SyllabusGenerator init creates other objects (BloomMapper, etc.) which might perform file IO.
        # We'll see if it runs.
        
        try:
            syllabus = generator.generate(
                course_title="Test Course",
                course_code="TEST101",
                credits="3-0-0",
                program_outcomes=["PO1"],
                domain="computer_science" # Prevent auto-detect if possible
            )
            
            self.assertIn("Mock Textbook 1", syllabus['references']['textbooks'])
            self.assertEqual(syllabus['overview'], "Mock overview text.")
            print("\nFull generation successful.")
            
        except Exception as e:
            print(f"\nGeneration failed with error: {e}")
            raise e

if __name__ == '__main__':
    unittest.main()
