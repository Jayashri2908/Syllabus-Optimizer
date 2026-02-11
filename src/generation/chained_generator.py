"""
Chained Syllabus Generator
Staggered LLM chaining with structured JSON outputs for consistent syllabus generation
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml

from ..ai.model_manager import ModelManager
from .section_schemas import (
    OverviewSection,
    ObjectivesSection,
    LearningOutcomesSection,
    UnitsSection,
    ReferencesSection,
    get_schema_for_section
)
from .section_prompts import SectionPrompts
from ..validation.syllabus_validator import SyllabusValidator


class ChainedSyllabusGenerator:
    """
    Generate syllabi using staggered LLM chaining.
    
    Each section is generated sequentially, with context from previous
    sections passed to subsequent stages. Responses are validated
    using Pydantic schemas for consistent structure.
    
    Stages:
    1. Overview (4-5 sentences)
    2. Objectives (5-6 items)
    3. Learning Outcomes (5-6 COs with Bloom's levels)
    4. Units (5 units with topics)
    5. References (textbooks, online resources)
    """
    
    # Generation order - each stage builds on previous
    GENERATION_ORDER = [
        "overview",
        "objectives", 
        "outcomes",
        "units",
        "references"
    ]
    
    def __init__(self, model_manager: Optional[ModelManager] = None):
        """
        Initialize the chained generator.
        
        Args:
            model_manager: Optional ModelManager instance. If not provided,
                          a new one will be created from config.
        """
        self.logger = logging.getLogger(__name__)
        self.ai = model_manager or self._initialize_model_manager()
        self.validator = SyllabusValidator()
        
        self.logger.info("Initialized ChainedSyllabusGenerator")
    
    def _initialize_model_manager(self) -> ModelManager:
        """Initialize AI model manager with configuration"""
        try:
            config_path = Path(__file__).parent.parent.parent / "configs" / "ai_models.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                config = {}
            
            return ModelManager(config)
        except Exception as e:
            self.logger.error(f"Failed to initialize ModelManager: {e}")
            raise
    
    def generate_staggered(
        self,
        course_info: Dict[str, Any],
        num_units: int = 5,
        num_outcomes: int = 5,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Generate complete syllabus using staggered LLM chaining.
        
        Each section is generated sequentially with accumulated context.
        
        Args:
            course_info: Dictionary containing:
                - course_title: Course title (required)
                - course_code: Course code (required)
                - credits: Credits in L-T-P format (required)
                - keywords: List of key topics (optional)
                - domain: Academic domain (optional, default: engineering)
                - program: Program name (optional)
                - year: Year/semester (optional)
                - unit_topics: User-provided unit structure (optional)
            num_units: Number of units to generate (default: 5)
            num_outcomes: Number of learning outcomes (default: 5)
            verbose: Print progress messages
            
        Returns:
            Complete syllabus dictionary with all sections
        """
        self.logger.info(f"Starting staggered generation for: {course_info.get('course_title')}")
        
        # Initialize context with input info
        context = {
            **course_info,
            "num_units": num_units,
            "num_outcomes": num_outcomes
        }
        
        # Set defaults
        context.setdefault("domain", "engineering")
        context.setdefault("keywords", [])
        context.setdefault("credits", "3-1-0")
        
        # Generate each section in order
        results = {}
        
        for section in self.GENERATION_ORDER:
            if verbose:
                self.logger.info(f"  → Generating {section}...")
            
            self.logger.info(f"Generating section: {section}")
            
            try:
                section_data = self._generate_section(section, context)
                results[section] = section_data
                
                # Add to context for next section
                if section == "outcomes":
                    context["learning_outcomes"] = section_data
                else:
                    context[section] = section_data
                    
            except Exception as e:
                self.logger.error(f"Failed to generate {section}: {e}")
                results[section] = self._get_fallback_section(section, context)
        
        # Assemble complete syllabus
        syllabus = self._assemble_syllabus(course_info, results)
        
        # Validate quality
        validation = self.validator.validate(syllabus)
        syllabus['quality_score'] = validation['score']
        syllabus['quality_grade'] = validation['grade']
        
        if verbose:
            self.logger.info(f"  ✓ Generation complete (Quality: {validation['grade']})")
        
        self.logger.info(f"Syllabus generated with quality score: {validation['score']}")
        
        return syllabus
    
    def _generate_section(
        self,
        section: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a single section using the appropriate prompt and schema.
        
        Args:
            section: Section name (overview, objectives, etc.)
            context: Accumulated context from previous sections
            
        Returns:
            Validated section data as dict
        """
        # Get prompt configuration
        system_prompt, user_prompt, strictness = SectionPrompts.get_prompt_for_section(
            section, context
        )
        
        # Get schema for validation
        schema = get_schema_for_section(section)
        
        # Generate with JSON output
        result = self.ai.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            schema=schema,
            task_type='generation',
            temperature=strictness.get('temperature', 0.3),
            max_tokens=strictness.get('max_tokens', 500),
            max_retries=2
        )
        
        return result
    
    def _get_fallback_section(
        self,
        section: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate fallback content when section generation fails.
        Uses user-provided keywords to create specific content.
        
        Args:
            section: Section name
            context: Context with course info
            
        Returns:
            Basic fallback content for the section
        """
        course_title = context.get('course_title', 'Course')
        keywords = context.get('keywords', [])
        num_units = context.get('num_units', 5)
        
        # Ensure we have enough keywords
        if not keywords:
            keywords = [course_title.split()[0] if course_title else 'Topic']
        
        # Create units dynamically from keywords
        def generate_fallback_units():
            units = []
            keywords_per_unit = max(1, len(keywords) // num_units)
            
            for i in range(num_units):
                start_idx = i * keywords_per_unit
                end_idx = start_idx + keywords_per_unit if i < num_units - 1 else len(keywords)
                unit_keywords = keywords[start_idx:end_idx] if start_idx < len(keywords) else [keywords[0]]
                
                # Create unit title from keywords
                if unit_keywords:
                    primary_keyword = unit_keywords[0]
                    if i == 0:
                        unit_title = f"{primary_keyword} Fundamentals and Concepts"
                    elif i == num_units - 1:
                        unit_title = f"Advanced {primary_keyword} and Applications"
                    else:
                        unit_title = f"{primary_keyword} Techniques and Methods"
                else:
                    unit_title = f"Unit {i+1}: Core Concepts"
                
                # Create topics from unit keywords
                topics = []
                for j, kw in enumerate(unit_keywords[:5]):
                    topics.append({
                        "topic": f"{kw} - Theory and Principles",
                        "description": f"This topic covers the theoretical foundations and practical aspects of {kw}. Students will learn key concepts, techniques, and real-world applications. The topic includes hands-on exercises and case studies to reinforce understanding.",
                        "subtopics": [f"{kw} basics", f"{kw} techniques", f"{kw} best practices"],
                        "key_concepts": [kw, f"{kw} principles"],
                        "practical_examples": [f"{kw} implementation", f"{kw} case study"]
                    })
                
                # Ensure at least 3 topics per unit
                while len(topics) < 3:
                    idx = len(topics)
                    topics.append({
                        "topic": f"Advanced {keywords[idx % len(keywords)]} Concepts",
                        "description": f"Advanced exploration of {keywords[idx % len(keywords)]} with focus on practical applications and industry best practices.",
                        "subtopics": ["Advanced theory", "Implementation", "Optimization"],
                        "key_concepts": ["Advanced concepts", "Best practices"],
                        "practical_examples": ["Industry application"]
                    })
                
                units.append({
                    "unit_number": i + 1,
                    "title": unit_title,
                    "overview": f"This unit covers {', '.join(unit_keywords[:3])}. Students will learn fundamental concepts, techniques, and applications related to {primary_keyword}. The unit builds on previous knowledge and prepares students for advanced topics.",
                    "topics": topics[:5],
                    "learning_activities": [f"{primary_keyword} lab exercise", "Case study analysis", "Group project"],
                    "suggested_readings": [f"Chapter {i+1}: {primary_keyword}"],
                    "hours": 10
                })
            
            return units
        
        fallbacks = {
            "overview": {
                "overview_text": f"This course provides comprehensive coverage of {course_title}, focusing on {', '.join(keywords[:3]) if keywords else 'core topics'}. "
                                f"Students will learn fundamental concepts and practical applications including {', '.join(keywords[3:6]) if len(keywords) > 3 else 'advanced techniques'}. "
                                f"The curriculum includes hands-on exercises and real-world case studies. "
                                f"Upon completion, students will be prepared for industry roles in {keywords[0] if keywords else 'the field'}."
            },
            "objectives": {
                "objectives": [
                    {"text": f"Understand the fundamental concepts of {keywords[0] if keywords else course_title}"},
                    {"text": f"Apply {keywords[1] if len(keywords) > 1 else keywords[0] if keywords else 'core'} techniques to solve practical problems"},
                    {"text": f"Analyze {keywords[2] if len(keywords) > 2 else 'real-world'} applications and case studies"},
                    {"text": f"Design solutions using {keywords[3] if len(keywords) > 3 else 'industry-standard'} practices"},
                    {"text": f"Evaluate and optimize {keywords[4] if len(keywords) > 4 else 'implementations'} for performance"}
                ]
            },
            "outcomes": {
                "outcomes": [
                    {"code": "CO1", "description": f"Explain fundamental concepts of {keywords[0] if keywords else course_title}", "bloom_level": "understand"},
                    {"code": "CO2", "description": f"Apply {keywords[1] if len(keywords) > 1 else keywords[0] if keywords else 'core'} techniques to solve problems", "bloom_level": "apply"},
                    {"code": "CO3", "description": f"Analyze {keywords[2] if len(keywords) > 2 else 'different'} approaches and evaluate their effectiveness", "bloom_level": "analyze"},
                    {"code": "CO4", "description": f"Design and implement solutions using {keywords[3] if len(keywords) > 3 else 'learned'} techniques", "bloom_level": "create"},
                    {"code": "CO5", "description": f"Evaluate {keywords[4] if len(keywords) > 4 else 'solutions'} against requirements and standards", "bloom_level": "evaluate"}
                ]
            },
            "units": {
                "units": generate_fallback_units()
            },
            "references": {
                "textbooks": [],
                "reference_books": [],
                "online_resources": []
            }
        }
        
        return fallbacks.get(section, {})
    
    def _assemble_syllabus(
        self,
        course_info: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assemble all generated sections into complete syllabus structure.
        
        Args:
            course_info: Original input information
            results: Generated section results
            
        Returns:
            Complete syllabus dictionary
        """
        # Extract overview text
        overview = results.get('overview', {})
        overview_text = overview.get('overview_text', '') if isinstance(overview, dict) else str(overview)
        
        # Extract objectives list
        objectives = results.get('objectives', {})
        if isinstance(objectives, dict):
            obj_list = objectives.get('objectives', [])
            objectives_list = [o.get('text', '') if isinstance(o, dict) else str(o) for o in obj_list]
        else:
            objectives_list = []
        
        # Extract learning outcomes
        outcomes = results.get('outcomes', {})
        if isinstance(outcomes, dict):
            outcomes_list = outcomes.get('outcomes', [])
        else:
            outcomes_list = []
        
        # Extract units with comprehensive detailed content
        units = results.get('units', {})
        if isinstance(units, dict):
            units_list = units.get('units', [])
            # Preserve comprehensive topic structure with all fields
            formatted_units = []
            for u in units_list:
                if isinstance(u, dict):
                    topics = u.get('topics', [])
                    # Handle comprehensive topic format
                    formatted_topics = []
                    for t in topics:
                        if isinstance(t, dict):
                            # Comprehensive format with all detail fields
                            topic_data = {
                                'topic': t.get('topic', ''),
                                'description': t.get('description', ''),
                                'subtopics': t.get('subtopics', []),
                                'key_concepts': t.get('key_concepts', []),
                                'practical_examples': t.get('practical_examples', [])
                            }
                            formatted_topics.append(topic_data)
                        else:
                            # Simple string format (backward compatibility)
                            formatted_topics.append({
                                'topic': str(t),
                                'description': '',
                                'subtopics': [],
                                'key_concepts': [],
                                'practical_examples': []
                            })
                    
                    formatted_units.append({
                        'unit_number': u.get('unit_number', 0),
                        'title': u.get('title', ''),
                        'overview': u.get('overview', ''),
                        'topics': formatted_topics,
                        'learning_activities': u.get('learning_activities', []),
                        'suggested_readings': u.get('suggested_readings', []),
                        'assessment_ideas': u.get('assessment_ideas', []),
                        'hours': u.get('hours', 10)
                    })
            units_list = formatted_units
        else:
            units_list = []
        
        # Extract references
        refs = results.get('references', {})
        if not isinstance(refs, dict):
            refs = {}
        
        # Build syllabus structure
        syllabus = {
            'course_title': course_info.get('course_title', ''),
            'course_code': course_info.get('course_code', ''),
            'credits': course_info.get('credits', ''),
            'program': course_info.get('program', ''),
            'year': course_info.get('year', ''),
            'overview': overview_text,
            'objectives': objectives_list,
            'learning_outcomes': outcomes_list,
            'units': units_list,
            'teaching_methodology': self._get_default_methodology(),
            'assessment_pattern': self._get_default_assessment(course_info.get('domain', 'engineering')),
            'references': {
                'textbooks': refs.get('textbooks', []),
                'references': refs.get('reference_books', []),
                'online_resources': refs.get('online_resources', [])
            },
            'generated': True,
            'generated_with_chaining': True,
            'metadata': {
                'domain': course_info.get('domain', 'engineering'),
                'generation_method': 'staggered_chaining',
                'num_units': len(units_list),
                'num_outcomes': len(outcomes_list)
            }
        }
        
        return syllabus
    
    def _get_default_methodology(self) -> Dict[str, List[str]]:
        """Get default teaching methodology"""
        return {
            'teaching_methods': [
                'Lectures with multimedia presentations',
                'Interactive discussions and Q&A sessions',
                'Hands-on laboratory exercises',
                'Case study analysis',
                'Group projects and collaborative learning'
            ],
            'learning_activities': [
                'Problem-solving exercises',
                'Self-study and reading assignments',
                'Practical demonstrations',
                'Peer learning and presentations',
                'Online resources and tutorials'
            ]
        }
    
    def _get_default_assessment(self, domain: str) -> Dict[str, Any]:
        """Get default assessment pattern"""
        pattern = {
            'internal': {
                'weightage': 40,
                'components': {
                    'midterm_exam': 20,
                    'assignments': 10,
                    'quizzes': 5,
                    'class_participation': 5
                }
            },
            'external': {
                'weightage': 60,
                'components': {
                    'final_exam': 60
                }
            }
        }
        
        # Add lab component for engineering/science
        if domain in ['engineering', 'science']:
            pattern['internal']['components']['lab_work'] = 10
            pattern['internal']['components']['assignments'] = 5
        
        return pattern
