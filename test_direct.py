import sys
from pathlib import Path
sys.path.append(str(Path(".").absolute()))

from src.generation.syllabus_generator import SyllabusGenerator
import json
import os
from dotenv import load_dotenv

load_dotenv()

generator = SyllabusGenerator()
result = generator.generate(
    course_title="Machine Learning",
    course_code="CS401",
    credits="3-1-0",
    program_outcomes=["PO1"],
    keywords=["neural networks", "linear regression"],
    use_chained_generation=True
)

with open("test_result.json", "w") as f:
    json.dump(result, f, indent=2)

print("Done. Check test_result.json")
