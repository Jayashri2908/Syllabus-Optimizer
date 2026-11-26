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
    SingleUnitSection,
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
                import traceback
                self.logger.error(f"Failed to generate {section}: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
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
        For 'units', delegates to per-unit generation for richer content.
        """
        # Units use per-unit generation strategy for rich content
        if section == "units":
            return self._generate_units_per_unit(context)
        
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
    
    def _generate_units_per_unit(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate units ONE AT A TIME for rich, detailed content.
        
        Instead of generating all 5 units in one massive LLM call (which
        token-starves the model and produces hollow stubs), we make 5
        separate calls — each producing 1 unit with full descriptions,
        subtopics, key_concepts, and practical_examples.
        """
        num_units = context.get('num_units', 5)
        keywords = context.get('keywords', [])
        course_title = context.get('course_title', 'Untitled Course')
        domain = context.get('domain', 'engineering')
        
        # Calculate hours per unit
        credits = context.get('credits', '3-1-0')
        try:
            parts = credits.split('-')
            l, t = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            total_hours = (l + t) * 15
            hours_per_unit = total_hours // num_units
        except Exception:
            hours_per_unit = 10
        
        # Distribute keywords across units
        # Check for user-provided unit topics first
        unit_topics = context.get('unit_topics', [])
        keyword_groups = []
        
        if unit_topics:
            # User provided unit structure — use those as themes
            for ut in unit_topics[:num_units]:
                keyword_groups.append(ut.get('topics', []))
            # Pad if fewer groups than units
            while len(keyword_groups) < num_units:
                keyword_groups.append(keywords[len(keyword_groups):] if len(keyword_groups) < len(keywords) else ['additional topics'])
        elif keywords:
            # Distribute keywords evenly across units
            kw_per_unit = max(1, len(keywords) // num_units)
            for i in range(num_units):
                start = i * kw_per_unit
                end = start + kw_per_unit if i < num_units - 1 else len(keywords)
                group = keywords[start:end] if start < len(keywords) else [keywords[-1]]
                keyword_groups.append(group)
        else:
            # No keywords at all — use course title words
            keyword_groups = [[course_title]] * num_units
        
        # Get strictness config for single_unit
        strictness = SectionPrompts.get_strictness('single_unit')
        system_prompt = SectionPrompts.MASTER_SYSTEM_PROMPT
        
        generated_units = []
        
        for i in range(num_units):
            unit_num = i + 1
            unit_kws = keyword_groups[i] if i < len(keyword_groups) else keyword_groups[-1]
            
            self.logger.info(f"  Generating unit {unit_num}/{num_units}: keywords={unit_kws}")
            
            # Build per-unit context
            unit_context = {
                **context,
                'unit_number': unit_num,
                'unit_keywords': unit_kws,
                'unit_theme': ', '.join(unit_kws),
                'hours_per_unit': hours_per_unit,
                'previous_units': generated_units,  # Dedup context
            }
            
            try:
                # Get focused single-unit prompt
                _, user_prompt, _ = SectionPrompts.get_prompt_for_section(
                    'single_unit', unit_context
                )
                
                # Generate one unit with generous token budget
                result = self.ai.generate_json(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    schema=SingleUnitSection,
                    task_type='generation',
                    temperature=strictness.get('temperature', 0.4),
                    max_tokens=strictness.get('max_tokens', 2500),
                    max_retries=2
                )
                
                # Force correct unit number
                result['unit_number'] = unit_num
                generated_units.append(result)
                
                self.logger.info(f"  Unit {unit_num} generated: {result.get('title', '?')} ({len(result.get('topics', []))} topics)")
                
            except Exception as e:
                self.logger.error(f"  Unit {unit_num} generation failed: {e}")
                # Fallback for this single unit
                fallback_unit = {
                    'unit_number': unit_num,
                    'title': f"{', '.join(unit_kws[:2]).title()} and Applications",
                    'topics': [
                        {
                            'topic': kw.strip().title() if len(kw.strip()) > 5 else f"{kw.strip()} in {course_title}",
                            'description': f"Covers key aspects of {kw.strip()} as applied in {course_title}. Students explore both theoretical foundations and practical implementations.",
                            'subtopics': [f"{kw.strip()} methodology", f"{kw.strip()} applications", f"{kw.strip()} analysis"],
                            'key_concepts': [kw.strip()],
                            'practical_examples': [f"Apply {kw.strip()} to a real-world problem"]
                        }
                        for kw in unit_kws[:5]
                    ],
                    'hours': hours_per_unit
                }
                generated_units.append(fallback_unit)
        
        self.logger.info(f"Per-unit generation complete: {len(generated_units)} units")
        return {'units': generated_units}
    
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
        
        # Create units dynamically from keywords — clean fallback, no template spam
        def generate_fallback_units():
            units = []
            keywords_per_unit = max(1, len(keywords) // num_units)

            for i in range(num_units):
                start_idx = i * keywords_per_unit
                end_idx = start_idx + keywords_per_unit if i < num_units - 1 else len(keywords)
                unit_keywords = keywords[start_idx:end_idx] if start_idx < len(keywords) else [keywords[0]]
                primary_keyword = unit_keywords[0] if unit_keywords else course_title

                # Use the keyword as-is for the unit title — don't template-spam it
                unit_title = primary_keyword.strip().title() if len(primary_keyword) > 3 else f"Unit {i+1}: {primary_keyword}"

                # Generate clean topic names — just use the keywords themselves
                topics = []
                for j, kw in enumerate(unit_keywords[:6]):
                    topics.append({
                        "topic": kw.strip().title() if len(kw.strip()) > 5 else f"{kw.strip()} in {course_title}",
                        "description": f"Covers key aspects of {kw.strip()} as applied in {course_title}.",
                        "subtopics": [],
                        "key_concepts": [],
                        "practical_examples": []
                    })

                # If too few topics, add simple numbered placeholders
                while len(topics) < 3:
                    topics.append({
                        "topic": f"{course_title} — Topic {len(topics) + 1}",
                        "description": f"Additional topic for Unit {i+1} of {course_title}.",
                        "subtopics": [],
                        "key_concepts": [],
                        "practical_examples": []
                    })
                
                units.append({
                    "unit_number": i + 1,
                    "title": unit_title,
                    "overview": "",
                    "topics": topics[:6],
                    "learning_activities": [],
                    "suggested_readings": [],
                    "hours": 10
                })
            
            self.logger.warning(
                f"Units fallback triggered for '{course_title}'. "
                f"LLM generation failed — using keyword-based placeholders. "
                f"Check API key, model availability, and token limits."
            )
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
