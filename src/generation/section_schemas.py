"""
Section Schemas for Staggered LLM Chaining
Pydantic models for validating each syllabus section's JSON output
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
import re


class BloomLevel(str, Enum):
    """Bloom's Taxonomy cognitive levels"""
    remember = "remember"
    understand = "understand"
    apply = "apply"
    analyze = "analyze"
    evaluate = "evaluate"
    create = "create"


# =============================================================================
# Section 1: Course Overview
# =============================================================================

class OverviewSection(BaseModel):
    """Schema for course overview section (4-5 sentences)"""
    overview_text: str = Field(
        ..., 
        min_length=100, 
        max_length=600,
        description="4-5 sentence course overview"
    )
    
    @field_validator('overview_text')
    @classmethod
    def validate_overview(cls, v: str) -> str:
        # Ensure it's not just placeholder text
        if v.lower().startswith(('todo', 'placeholder', 'insert')):
            raise ValueError("Overview cannot be placeholder text")
        return v.strip()


# =============================================================================
# Section 2: Course Objectives
# =============================================================================

class ObjectiveItem(BaseModel):
    """Single course objective"""
    text: str = Field(
        ..., 
        min_length=15, 
        max_length=200,
        description="1-2 line action-verb led objective"
    )
    
    @field_validator('text')
    @classmethod
    def validate_objective(cls, v: str) -> str:
        # Ensure it starts with action verb (capital letter)
        v = v.strip()
        if v and not v[0].isupper():
            v = v.capitalize()
        return v


class ObjectivesSection(BaseModel):
    """Schema for course objectives (5-6 items)"""
    objectives: List[ObjectiveItem] = Field(
        ..., 
        min_length=4, 
        max_length=8,
        description="List of 5-6 course objectives"
    )


# =============================================================================
# Section 3: Learning Outcomes
# =============================================================================

class LearningOutcome(BaseModel):
    """Single learning outcome with Bloom's level"""
    code: str = Field(
        ..., 
        pattern=r"^CO\d+$",
        description="Course outcome code (e.g., CO1, CO2)"
    )
    description: str = Field(
        ..., 
        min_length=20, 
        max_length=250,
        description="Learning outcome description (1-2 lines)"
    )
    bloom_level: BloomLevel = Field(
        ...,
        description="Bloom's taxonomy level"
    )
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        # Remove leading CO code if accidentally included
        v = re.sub(r'^CO\d+[:\s-]*', '', v)
        return v


class LearningOutcomesSection(BaseModel):
    """Schema for learning outcomes (5-6 COs)"""
    outcomes: List[LearningOutcome] = Field(
        ..., 
        min_length=4, 
        max_length=8,
        description="List of course learning outcomes"
    )
    
    @field_validator('outcomes')
    @classmethod
    def validate_unique_codes(cls, v: List[LearningOutcome]) -> List[LearningOutcome]:
        codes = [o.code for o in v]
        if len(codes) != len(set(codes)):
            raise ValueError("Learning outcome codes must be unique")
        return v


# =============================================================================
# Section 4: Unit-wise Syllabus (Comprehensive Detailed)
# =============================================================================

class UnitTopic(BaseModel):
    """Single topic within a unit with comprehensive detailed description"""
    topic: str = Field(
        ..., 
        min_length=5, 
        max_length=200,
        description="Topic name (5-12 words, specific and descriptive)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1500,  # Increased for 4-6 sentence descriptions
        description="Comprehensive 4-6 sentence description of the topic"
    )
    subtopics: Optional[List[str]] = Field(
        default_factory=list,
        max_length=8,
        description="List of subtopics (3-5 items)"
    )
    key_concepts: Optional[List[str]] = Field(
        default_factory=list,
        max_length=6,
        description="Key concepts or principles (2-4 items)"
    )
    practical_examples: Optional[List[str]] = Field(
        default_factory=list,
        max_length=4,
        description="Practical examples or applications (1-2 items)"
    )
    
    @field_validator('topic')
    @classmethod
    def clean_topic(cls, v: str) -> str:
        # Remove numbering prefixes
        v = re.sub(r'^\d+[\.\)\-:\s]+', '', v.strip())
        return v
    
    @field_validator('subtopics', 'key_concepts', 'practical_examples')
    @classmethod
    def clean_list_items(cls, v: Optional[List[str]]) -> List[str]:
        if not v:
            return []
        cleaned = []
        for item in v:
            # Remove numbering and clean
            item = re.sub(r'^\d+[\.\)\-:\s]+', '', str(item).strip())
            if item and len(item) > 2:
                cleaned.append(item)
        return cleaned


class Unit(BaseModel):
    """Single syllabus unit with extensive comprehensive details"""
    unit_number: int = Field(
        ..., 
        ge=1, 
        le=10,
        description="Unit number (1-10)"
    )
    title: str = Field(
        ..., 
        min_length=5, 
        max_length=150,
        description="Unit title (4-10 words, descriptive)"
    )
    overview: Optional[str] = Field(
        default=None,
        max_length=1000,  # Increased for 4-5 sentence overviews
        description="4-5 sentence comprehensive overview of the unit"
    )
    topics: List[UnitTopic] = Field(
        ..., 
        min_length=1,
        max_length=10,
        description="List of detailed topics in this unit (5-6 recommended)"
    )
    learning_activities: Optional[List[str]] = Field(
        default_factory=list,
        max_length=6,
        description="Detailed learning activities (3-4 items)"
    )
    suggested_readings: Optional[List[str]] = Field(
        default_factory=list,
        max_length=5,
        description="Suggested readings (chapters, papers, articles)"
    )
    assessment_ideas: Optional[List[str]] = Field(
        default_factory=list,
        max_length=4,
        description="Assessment ideas (quizzes, assignments, projects)"
    )
    hours: int = Field(
        default=10, 
        ge=4, 
        le=25,
        description="Hours allocated to this unit"
    )
    
    @field_validator('title')
    @classmethod
    def clean_title(cls, v: str) -> str:
        # Remove "Unit X:" prefix if present
        v = re.sub(r'^Unit\s*\d+[\s:\-]*', '', v.strip(), flags=re.IGNORECASE)
        return v.strip()
    
    @field_validator('learning_activities', 'suggested_readings', 'assessment_ideas')
    @classmethod
    def clean_list_fields(cls, v: Optional[List[str]]) -> List[str]:
        if not v:
            return []
        cleaned = []
        for item in v:
            item = str(item).strip()
            if item and len(item) > 3:
                cleaned.append(item)
        return cleaned


class UnitsSection(BaseModel):
    """Schema for all units (5 units with detailed content)"""
    units: List[Unit] = Field(
        ..., 
        min_length=3, 
        max_length=8,
        description="List of syllabus units with detailed content"
    )
    
    @field_validator('units')
    @classmethod
    def validate_sequential(cls, v: List[Unit]) -> List[Unit]:
        # Ensure unit numbers are sequential
        numbers = [u.unit_number for u in v]
        expected = list(range(1, len(numbers) + 1))
        if numbers != expected:
            # Auto-fix unit numbers
            for i, unit in enumerate(v):
                unit.unit_number = i + 1
        return v


# =============================================================================
# Section 5: References
# =============================================================================

class ReferencesSection(BaseModel):
    """Schema for references"""
    textbooks: List[str] = Field(
        ..., 
        min_length=2, 
        max_length=6,
        description="List of textbooks with author and publisher"
    )
    reference_books: List[str] = Field(
        default_factory=list, 
        max_length=5,
        description="Additional reference books"
    )
    online_resources: List[str] = Field(
        default_factory=list, 
        max_length=6,
        description="Online courses, websites, documentation"
    )
    
    @field_validator('textbooks', 'reference_books', 'online_resources')
    @classmethod
    def clean_references(cls, v: List[str]) -> List[str]:
        cleaned = []
        for ref in v:
            # Remove numbering
            ref = re.sub(r'^\d+[\.\)\-:\s]+', '', ref.strip())
            if ref and len(ref) > 10:
                cleaned.append(ref)
        return cleaned


# =============================================================================
# Complete Syllabus Schema
# =============================================================================

class CompleteSyllabus(BaseModel):
    """Complete syllabus combining all sections"""
    course_title: str
    course_code: str
    credits: str
    department: Optional[str] = None
    university: Optional[str] = None
    academic_year: Optional[str] = None
    
    overview: OverviewSection
    objectives: ObjectivesSection
    learning_outcomes: LearningOutcomesSection
    units: UnitsSection
    references: ReferencesSection
    
    # Metadata
    generated_with_chaining: bool = True
    quality_score: Optional[float] = None


# =============================================================================
# Helper Functions
# =============================================================================

def get_schema_for_section(section_name: str) -> type[BaseModel]:
    """Get the Pydantic schema class for a section"""
    schemas = {
        "overview": OverviewSection,
        "objectives": ObjectivesSection,
        "outcomes": LearningOutcomesSection,
        "learning_outcomes": LearningOutcomesSection,
        "units": UnitsSection,
        "references": ReferencesSection,
    }
    return schemas.get(section_name.lower())


def get_json_schema(section_name: str) -> dict:
    """Get JSON schema for a section (for prompts)"""
    schema_class = get_schema_for_section(section_name)
    if schema_class:
        return schema_class.model_json_schema()
    return {}
