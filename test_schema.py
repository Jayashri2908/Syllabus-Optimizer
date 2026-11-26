from src.generation.section_schemas import SingleUnitSection
import json

data = {
    "unit_number": 1,
    "title": "Machine Learning",
    "topics": [
        {
            "topic": "Machine learning definitions and scope",
            "description": None,
            "subtopics": [],
            "key_concepts": [],
            "practical_examples": []
        }
    ],
    "hours": 10
}

try:
    validated = SingleUnitSection.model_validate(data)
    print("Success:", validated.model_dump())
except Exception as e:
    print("Error:", e)
