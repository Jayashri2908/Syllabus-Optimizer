from src.generation.mock_generator import MockSyllabusGenerator
import json

def test_gen():
    gen = MockSyllabusGenerator()
    result = gen.generate(
        course_title="Advanced Python", 
        course_code="CS505", 
        credits="3-0-0",
        program_outcomes=["PO1"], 
        keywords=["Data Structures", "Algorithms"],
        domain="engineering",
        num_units=5
    )
    
    print(json.dumps(result['units'], indent=2))

if __name__ == "__main__":
    test_gen()
