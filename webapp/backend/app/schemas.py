from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class GenerateRequest(BaseModel):
    # Institution Details
    university_name: str = ""
    faculty_name: str = ""
    department: str = ""
    
    # Course Details
    course_title: str
    course_code: str
    course_type: str = "DSC"  # DSC, DSE, GEC, SEC, etc.
    credits: str
    semester: str = "I"
    program: str = ""
    year: str = ""
    course_level: str = "intermediate"
    
    # Content
    program_outcomes: List[str]
    keywords: List[str] = []
    unit_topics: List[Dict[str, Any]] = []
    
    # References
    textbooks: List[str] = []
    references: List[str] = []
    online_resources: List[str] = []
    
    # Settings
    domain: str = "engineering"
    num_units: int = 5
    num_outcomes: int = 5


class OptimizeRequest(BaseModel):
    syllabus_data: Dict[str, Any]
    optimization_goals: List[str] = []
    analysis_data: Optional[Dict[str, Any]] = None


class MapRequest(BaseModel):
    course_outcomes: List[Dict[str, str]]
    program_outcomes: Optional[List[str]] = None
    domain: str = "engineering"
