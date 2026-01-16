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
                print(f"  → Generating {section}...")
            
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
            print(f"  ✓ Generation complete (Quality: {validation['grade']})")
        
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
        
        Args:
            section: Section name
            context: Context with course info
            
        Returns:
            Basic fallback content for the section
        """
        course_title = context.get('course_title', 'Course')
        keywords = context.get('keywords', ['topic'])
        
        fallbacks = {
            "overview": {
                "overview_text": f"This course provides comprehensive coverage of {course_title}. "
                                f"Students will learn fundamental concepts and practical applications. "
                                f"The curriculum includes hands-on exercises and real-world case studies. "
                                f"Upon completion, students will be prepared for industry roles."
            },
            "objectives": {
                "objectives": [
                    {"text": f"Understand the fundamental concepts of {course_title}"},
                    {"text": f"Apply {keywords[0] if keywords else 'core'} concepts to solve problems"},
                    {"text": "Develop practical skills through hands-on projects"},
                    {"text": "Analyze real-world applications and case studies"},
                    {"text": "Design solutions using industry-standard practices"}
                ]
            },
            "outcomes": {
                "outcomes": [
                    {"code": "CO1", "description": f"Explain fundamental concepts of {course_title}", "bloom_level": "understand"},
                    {"code": "CO2", "description": f"Apply {keywords[0] if keywords else 'core'} techniques to solve problems", "bloom_level": "apply"},
                    {"code": "CO3", "description": "Analyze and evaluate different approaches", "bloom_level": "analyze"},
                    {"code": "CO4", "description": "Design and implement practical solutions", "bloom_level": "create"},
                    {"code": "CO5", "description": "Evaluate solutions against requirements", "bloom_level": "evaluate"}
                ]
            },
            "units": {
                "units": [
                    {
                        "unit_number": 1, 
                        "title": "Introduction and Fundamentals", 
                        "overview": f"This unit introduces the foundational concepts of {course_title}. Students will learn the basic terminology, history, and importance of the subject. The unit establishes a strong foundation for subsequent topics.",
                        "topics": [
                            {"topic": "Introduction and Background", "description": f"Overview of {course_title}, its evolution, and significance in the modern context. Historical developments and current trends.", "subtopics": ["Historical context", "Current relevance", "Future directions"], "key_concepts": ["Foundation", "Evolution"], "practical_examples": ["Industry overview"]},
                            {"topic": "Fundamental Concepts", "description": "Core principles and basic building blocks that form the foundation of the subject. Essential terminology and definitions.", "subtopics": ["Core principles", "Basic definitions", "Key terminology"], "key_concepts": ["Basics", "Foundations"], "practical_examples": ["Introductory examples"]},
                            {"topic": "Tools and Environment Setup", "description": "Setting up the development environment and tools required for practical work. Configuration and best practices.", "subtopics": ["Tool installation", "Configuration", "Environment setup"], "key_concepts": ["Setup", "Tools"], "practical_examples": ["Lab setup"]}
                        ], 
                        "learning_activities": ["Introduction lecture", "Environment setup lab", "Reading assignment"],
                        "suggested_readings": ["Chapter 1: Introduction"],
                        "hours": 10
                    },
                    {
                        "unit_number": 2, 
                        "title": "Core Concepts and Principles", 
                        "overview": "This unit covers the essential principles and techniques central to the subject. Students will develop a deep understanding of core methodologies and their applications.",
                        "topics": [
                            {"topic": "Core Principles and Theory", "description": "Detailed study of fundamental principles that govern the subject. Theoretical foundations and their practical implications.", "subtopics": ["Theory foundations", "Key principles", "Conceptual framework"], "key_concepts": ["Theory", "Principles"], "practical_examples": ["Theoretical applications"]},
                            {"topic": "Techniques and Methods", "description": "Standard techniques and methodologies used in practice. Step-by-step approaches and best practices.", "subtopics": ["Standard methods", "Techniques", "Best practices"], "key_concepts": ["Methods", "Techniques"], "practical_examples": ["Method demonstration"]},
                            {"topic": "Problem Analysis", "description": "Approaches to analyzing problems and identifying appropriate solutions. Analytical thinking and systematic problem-solving.", "subtopics": ["Problem identification", "Analysis methods", "Solution strategies"], "key_concepts": ["Analysis", "Problem-solving"], "practical_examples": ["Case analysis"]}
                        ], 
                        "learning_activities": ["Theory lecture", "Practice exercises", "Group discussion"],
                        "suggested_readings": ["Chapter 2: Core Concepts"],
                        "hours": 10
                    },
                    {
                        "unit_number": 3, 
                        "title": "Advanced Topics and Applications", 
                        "overview": "Building on foundational knowledge, this unit explores advanced concepts and their real-world applications. Students will learn sophisticated techniques and industry practices.",
                        "topics": [
                            {"topic": "Advanced Concepts", "description": "In-depth exploration of advanced topics that build upon fundamental concepts. Complex scenarios and sophisticated approaches.", "subtopics": ["Advanced theory", "Complex scenarios", "Edge cases"], "key_concepts": ["Advanced", "Complex"], "practical_examples": ["Advanced scenarios"]},
                            {"topic": "Real-world Applications", "description": "Practical applications in industry and research. Case studies demonstrating real-world implementation.", "subtopics": ["Industry applications", "Research applications", "Case studies"], "key_concepts": ["Applications", "Implementation"], "practical_examples": ["Industry case study"]},
                            {"topic": "Optimization and Best Practices", "description": "Techniques for optimization and industry best practices. Performance tuning and quality assurance.", "subtopics": ["Optimization strategies", "Performance tuning", "Quality practices"], "key_concepts": ["Optimization", "Best practices"], "practical_examples": ["Performance optimization"]}
                        ], 
                        "learning_activities": ["Advanced lecture", "Case study analysis", "Practical exercise"],
                        "suggested_readings": ["Chapter 3: Advanced Topics"],
                        "hours": 10
                    },
                    {
                        "unit_number": 4, 
                        "title": "Practical Implementation", 
                        "overview": "This unit focuses on hands-on implementation and practical skills development. Students will work on projects and gain experience with real-world scenarios.",
                        "topics": [
                            {"topic": "Implementation Strategies", "description": "Approaches to implementing solutions effectively. Planning, design, and execution strategies.", "subtopics": ["Planning", "Design", "Execution"], "key_concepts": ["Implementation", "Strategy"], "practical_examples": ["Project planning"]},
                            {"topic": "Tools and Technologies", "description": "Industry-standard tools and technologies used for implementation. Hands-on experience with practical tools.", "subtopics": ["Industry tools", "Technologies", "Frameworks"], "key_concepts": ["Tools", "Technologies"], "practical_examples": ["Tool demonstration"]},
                            {"topic": "Testing and Validation", "description": "Approaches to testing and validating implementations. Quality assurance and verification methods.", "subtopics": ["Testing methods", "Validation", "Quality assurance"], "key_concepts": ["Testing", "Validation"], "practical_examples": ["Testing exercise"]}
                        ], 
                        "learning_activities": ["Implementation lab", "Mini project", "Peer review"],
                        "suggested_readings": ["Chapter 4: Implementation"],
                        "hours": 10
                    },
                    {
                        "unit_number": 5, 
                        "title": "Integration and Project Work", 
                        "overview": "The final unit integrates all concepts through comprehensive project work. Students demonstrate mastery through practical application and presentation.",
                        "topics": [
                            {"topic": "System Integration", "description": "Techniques for integrating components into complete solutions. End-to-end implementation and deployment.", "subtopics": ["Component integration", "System design", "Deployment"], "key_concepts": ["Integration", "Systems"], "practical_examples": ["Full system implementation"]},
                            {"topic": "Project Development", "description": "Comprehensive project development applying all learned concepts. Planning, execution, and documentation.", "subtopics": ["Project planning", "Development", "Documentation"], "key_concepts": ["Projects", "Development"], "practical_examples": ["Capstone project"]},
                            {"topic": "Presentation and Evaluation", "description": "Presenting project work and receiving feedback. Professional presentation skills and evaluation criteria.", "subtopics": ["Presentation skills", "Demo", "Evaluation"], "key_concepts": ["Presentation", "Evaluation"], "practical_examples": ["Project demo"]}
                        ], 
                        "learning_activities": ["Project work", "Presentation preparation", "Final evaluation"],
                        "suggested_readings": ["Project guidelines"],
                        "hours": 10
                    }
                ]
            },
            "references": {
                "textbooks": [
                    f"Introduction to {course_title} by Standard Author (Publisher)",
                    f"Fundamentals of {keywords[0] if keywords else 'the Subject'} by Expert Author"
                ],
                "reference_books": [
                    f"Advanced {course_title} by Senior Author"
                ],
                "online_resources": [
                    "Official documentation and tutorials",
                    "Relevant online courses on Coursera/edX"
                ]
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
