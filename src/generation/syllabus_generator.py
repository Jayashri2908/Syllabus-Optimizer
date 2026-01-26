"""
Syllabus Generator for SCDO
Generates complete syllabi using AI (Gemini/Granite) with enhanced prompts
"""

from typing import Dict, List, Any, Optional
import logging
from pathlib import Path
import yaml

from ..ai.model_manager import ModelManager
from ..ai.prompt_library import PromptLibrary
from ..optimization.bloom_mapper import BloomMapper
from ..validation.syllabus_validator import SyllabusValidator
from .domain_templates import (
    detect_domain, get_domain_context, get_domain_tools,
    get_domain_applications, get_domain_careers, get_domain_prerequisites
)
from .bloom_distribution import get_bloom_distribution, format_distribution_for_prompt, get_bloom_verb_list
from .iterative_refiner import IterativeRefiner
from .industry_data import format_industry_context, get_industry_skills
from .rubric_generator import RubricGenerator


class SyllabusGenerator:
    """Generate complete syllabi from minimal inputs with AI"""
    
    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.logger = logging.getLogger(__name__)
        
        # Use ModelManager instead of direct Granite client
        self.ai = model_manager or self._initialize_model_manager()
        
        # Initialize prompt library
        self.prompts = PromptLibrary()
        
        self.bloom_mapper = BloomMapper()
        self.validator = SyllabusValidator()
        self.refiner = IterativeRefiner(self.ai)
        self.rubric_gen = RubricGenerator()
        
        self.logger.info(f"Initialized Syllabus Generator with AI models")
    
    def _initialize_model_manager(self) -> ModelManager:
        """Initialize AI model manager with configuration"""
        try:
            # Load AI models config
            config_path = Path(__file__).parent.parent.parent / "configs" / "ai_models.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                config = {}
            
            manager = ModelManager(config)
            
            # Check if any models available
            if not manager.models:
                self.logger.warning("No AI models available! Please configure Gemini or Granite.")
            else:
                available = [name for name in manager.models.keys()]
                self.logger.info(f"Available AI models: {', '.join(available)}")
            
            return manager
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ModelManager: {e}")
            raise
    
    def _detect_and_cache_domain(self, course_title: str, keywords: List[str]) -> str:
        """Detect domain and cache for current generation"""
        if not hasattr(self, '_cached_domain'):
            self._cached_domain = detect_domain(course_title, keywords)
            self.logger.info(f"Auto-detected domain: {self._cached_domain}")
        return self._cached_domain
    
    def _suggest_applications(self, keywords: List[str], course_title: str = "") -> str:
        """Suggest real-world applications using domain detection"""
        domain = self._detect_and_cache_domain(course_title, keywords)
        applications = get_domain_applications(domain)
        return ', '.join(applications[:3])
    
    def _suggest_tools(self, keywords: List[str], course_title: str = "") -> str:
        """Suggest relevant tools using domain detection"""
        domain = self._detect_and_cache_domain(course_title, keywords)
        tools = get_domain_tools(domain)
        return ', '.join(tools[:5])
    
    def _suggest_careers(self, domain_param: str, course_title: str = "", keywords: List[str] = None) -> str:
        """Suggest career paths using domain detection"""
        if keywords:
            domain = self._detect_and_cache_domain(course_title, keywords)
        else:
            domain = domain_param.lower().replace(" ", "_")
        careers = get_domain_careers(domain)
        return ', '.join(careers[:3])
    
    def _suggest_prerequisites(self, keywords: List[str], course_title: str = "") -> str:
        """Suggest prerequisites using domain detection"""
        domain = self._detect_and_cache_domain(course_title, keywords)
        prereqs = get_domain_prerequisites(domain)
        return ', '.join(prereqs[:4])
    
    def _get_industry_context(self, keywords: List[str], course_title: str = "") -> str:
        """Get industry context with job market data"""
        domain = self._detect_and_cache_domain(course_title, keywords)
        return format_industry_context(domain)
    
    def _estimate_course_level(self, course_title: str) -> str:
        """Estimate course level from title"""
        title_lower = course_title.lower()
        
        if any(term in title_lower for term in ['advanced', 'graduate', 'phd', 'research']):
            return 'Advanced/Graduate'
        elif any(term in title_lower for term in ['intro', 'basic', 'fundamental', 'foundation']):
            return 'Introductory/Beginner'
        else:
            return 'Intermediate/Undergraduate'
        
    def generate(
        self,
        course_title: str,
        course_code: str,
        credits: str,
        program_outcomes: List[str],
        keywords: List[str] = None,
        unit_topics: List[Dict[str, Any]] = None,
        textbooks: List[str] = None,
        references: List[str] = None,
        online_resources: List[str] = None,
        domain: str = "engineering",
        num_units: int = 5,
        num_outcomes: int = 5,
        enable_refinement: bool = False,
        program: str = "",
        year: str = "",
        course_level: str = "",
        use_chained_generation: bool = False
    ) -> Dict[str, Any]:
        """
        Generate complete syllabus
        
        Args:
            course_title: Course title
            course_code: Course code
            credits: Credit hours (L-T-P format)
            program_outcomes: Relevant program outcomes
            keywords: Key topics/skills (backward compatibility)
            unit_topics: Unit-wise topics list [{"unit_number": 1, "topics": [...]}, ...]
            textbooks: User-provided textbooks
            references: User-provided reference books
            online_resources: User-provided online resources
            domain: Academic domain
            num_units: Number of units to generate
            num_outcomes: Number of course outcomes
            enable_refinement: Enable iterative refinement (slower but higher quality)
            program: Program name (e.g., "B.Tech Computer Science")
            year: Year/Semester (e.g., "3rd Year")
            course_level: Explicit course level (introductory/intermediate/advanced)
            use_chained_generation: Use staggered LLM chaining for structured JSON output
            
        Returns:
            Complete syllabus structure with quality score
        """
        
        # Use staggered LLM chaining if requested
        if use_chained_generation:
            self.logger.info(f"Using staggered LLM chaining for {course_title}")
            from .chained_generator import ChainedSyllabusGenerator
            
            chained = ChainedSyllabusGenerator(self.ai)
            return chained.generate_staggered(
                course_info={
                    "course_title": course_title,
                    "course_code": course_code,
                    "credits": credits,
                    "program_outcomes": program_outcomes,
                    "keywords": keywords or [],
                    "unit_topics": unit_topics,
                    "domain": domain,
                    "program": program,
                    "year": year,
                    "course_level": course_level
                },
                num_units=num_units,
                num_outcomes=num_outcomes,
                verbose=False
            )
        
        self.logger.info(f"Generating syllabus for {course_title} (refinement: {enable_refinement})")
        
        # Clear cached domain for new generation
        if hasattr(self, '_cached_domain'):
            delattr(self, '_cached_domain')
        
        # Handle keywords: use unit_topics or fallback to keywords
        keywords = keywords or []
        if unit_topics:
            # Extract all topics from unit_topics for general use
            all_topics = []
            for unit in unit_topics:
                all_topics.extend(unit.get('topics', []))
            if all_topics:
                keywords = all_topics
        
        # Determine course level: use explicit or auto-detect
        effective_level = course_level if course_level else self._estimate_course_level(course_title)
        
        # Generate course overview (4-5 lines)
        overview = self._generate_overview(course_title, keywords, domain, program, year)
        
        # Generate course objectives
        objectives = self._generate_objectives(course_title, keywords, domain)
        
        # Refine objectives if enabled
        if enable_refinement and objectives:
            self.logger.info("Refining objectives...")
            objectives = self.refiner.refine_objectives(objectives, course_title, keywords)
        
        # Generate learning outcomes
        outcomes = self._generate_learning_outcomes(
            course_title, keywords, program_outcomes, num_outcomes
        )
        
        # Refine outcomes if enabled
        if enable_refinement and outcomes:
            self.logger.info("Refining learning outcomes...")
            outcomes = self.refiner.refine_learning_outcomes(
                outcomes, course_title, keywords, program_outcomes, num_outcomes
            )
        
        # Generate unit-wise syllabus (use unit_topics if available)
        units = self._generate_units(course_title, keywords, num_units, credits, unit_topics)
        
        # Generate teaching methodology
        methodology = self._generate_methodology(domain)
        
        # Generate assessment pattern
        assessment = self._generate_assessment_pattern(outcomes, domain)
        
        # Handle references: use user-provided or generate
        # Check if any user-provided references exist (not None and not empty)
        has_user_refs = (
            (textbooks and len(textbooks) > 0) or 
            (references and len(references) > 0) or 
            (online_resources and len(online_resources) > 0)
        )
        
        if has_user_refs:
            # Use user-provided references
            refs = {
                'textbooks': textbooks if textbooks else [],
                'references': references if references else [],
                'online_resources': online_resources if online_resources else [],
                'raw_suggestions': ''
            }
        else:
            # Generate references using AI
            refs = self._generate_references(course_title, keywords)
        
        # Generate assessment rubrics
        rubrics = self.rubric_gen.generate_rubrics(assessment, domain)
        
        # Get industry context
        industry_context = self._get_industry_context(keywords, course_title)
        
        # Generate CO-PO summary (1 line)
        copo_summary = self._generate_copo_summary(outcomes, program_outcomes)
        
        # Create syllabus structure
        syllabus = {
            'course_title': course_title,
            'course_code': course_code,
            'credits': credits,
            'program': program,
            'year': year,
            'course_level': effective_level,
            'overview': overview,
            'objectives': objectives,
            'learning_outcomes': outcomes,
            'units': units,
            'teaching_methodology': methodology,
            'assessment_pattern': assessment,
            'references': refs,
            'rubrics': rubrics,
            'copo_summary': copo_summary,
            'generated': True,
            'metadata': {
                'domain_detected': self._detect_and_cache_domain(course_title, keywords),
                'course_level': effective_level,
                'industry_context': industry_context,
                'refinement_enabled': enable_refinement,
                'program': program,
                'year': year
            }
        }
        
        # Validate quality
        validation = self.validator.validate(syllabus)
        syllabus['quality_score'] = validation['score']
        syllabus['quality_grade'] = validation['grade']
        
        if not validation['passed']:
            self.logger.warning(f"Quality issues found (score: {validation['score']}): {validation['issues']}")
            self.logger.info(f"Recommendations: {validation['recommendations']}")
        else:
            self.logger.info(f"Syllabus quality: {validation['grade']} ({validation['score']}/100)")
        
        return syllabus
    

    


        
    def _generate_overview(
        self,
        course_title: str,
        keywords: List[str],
        domain: str,
        program: str = "",
        year: str = ""
    ) -> str:
        """Generate course overview using enhanced prompts (4-5 lines)"""
        
        # Get domain-specific context
        applications = get_domain_applications(detect_domain(course_title, keywords))
        careers = get_domain_careers(detect_domain(course_title, keywords))
        
        # Get enhanced prompts from library
        prompts = self.prompts.get_course_overview_prompt(
            course_title=course_title,
            keywords=keywords,
            domain=domain,
            applications=applications,
            careers=careers,
            program=program,
            year=year
        )
        
        # Generate using AI with optimized temperature (reduced tokens for 4-5 lines)
        return self.ai.generate(
            prompt=prompts['user'],
            system_prompt=prompts['system'],
            task_type='generation',
            temperature=0.65,
            max_tokens=350  # Reduced for 4-5 lines
        )
        
    def _generate_objectives(
        self,
        course_title: str,
        keywords: List[str],
        domain: str
    ) -> List[str]:
        """Generate course objectives using enhanced prompts"""
        
        # Get domain context
        domain_detected = detect_domain(course_title, keywords)
        tools = get_domain_tools(domain_detected)
        applications = get_domain_applications(domain_detected)
        course_level = self._estimate_course_level(course_title)
        
        # Get enhanced prompts
        prompts = self.prompts.get_objectives_prompt(
            course_title=course_title,
            keywords=keywords,
            domain=domain,
            course_level=course_level,
            tools=tools,
            applications=applications
        )
        
        # Generate with AI
        response = self.ai.generate(
            prompt=prompts['user'],
            system_prompt=prompts['system'],
            task_type='generation',
            temperature=0.5,
            max_tokens=200  # Reduced for shorter objectives
        )
        
        # Parse objectives
        objectives = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                obj = line.lstrip('0123456789.-•) ').strip()
                if obj and len(obj) > 10:  # Reduced min length for shorter objectives
                    objectives.append(obj)
                    
        return objectives[:6]
        
    def _generate_learning_outcomes(
        self,
        course_title: str,
        keywords: List[str],
        program_outcomes: List[str],
        num_outcomes: int
    ) -> List[Dict[str, str]]:
        """Generate course learning outcomes using enhanced prompts"""
        
        # Get level-appropriate Bloom's distribution
        course_level = self._estimate_course_level(course_title)
        bloom_dist = get_bloom_distribution(course_level, num_outcomes)
        
        # Get domain context
        domain_detected = detect_domain(course_title, keywords)
        
        # Generate one outcome per Bloom's level according to distribution
        outcomes = []
        outcome_num = 1
        
        for bloom_level, count in bloom_dist.items():
            for _ in range(count):
                if outcome_num > num_outcomes:
                    break
                
                # Get enhanced prompt for this Bloom's level
                prompts = self.prompts.get_learning_outcome_prompt(
                    course_title=course_title,
                    course_level=course_level,
                    bloom_level=bloom_level,
                    domain_context=domain_detected,
                    keywords=keywords
                )
                
                # Generate one outcome
                outcome_text = self.ai.generate(
                    prompt=prompts['user'],
                    system_prompt=prompts['system'],
                    task_type='generation',
                    temperature=0.4,  # Lower for more focused outcomes
                    max_tokens=80  # Reduced for 1-2 line output
                )
                
                # Clean up the outcome text
                outcome_text = outcome_text.strip().strip('"').strip("'").strip()
                
                # Only add if it's a valid outcome (min 15 chars for short outcomes)
                if outcome_text and len(outcome_text) > 15:
                    outcomes.append({
                        'code': f'CO{outcome_num}',
                        'description': outcome_text,
                        'bloom_level': bloom_level
                    })
                    outcome_num += 1
        
        # If we didn't get enough outcomes, pad with the AI model
        while len(outcomes) < num_outcomes:
            outcomes.append({
                'code': f'CO{len(outcomes) + 1}',
                'description': f"Apply {keywords[len(outcomes) % len(keywords)]} concepts to solve real-world problems effectively",
                'bloom_level': 'apply'
            })
        
        return outcomes[:num_outcomes]
        
    def _generate_units(
        self,
        course_title: str,
        keywords: List[str],
        num_units: int,
        credits: str,
        unit_topics: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate unit-wise syllabus using enhanced prompts"""
        
        # Calculate hours per unit
        try:
            l, t, p = map(int, credits.split('-'))
            total_hours = (l + t) * 15  # Assuming 15 weeks
            hours_per_unit = total_hours // num_units
        except:
            hours_per_unit = 10
        
        # Get domain context
        domain_detected = detect_domain(course_title, keywords)
        domain_tools = get_domain_tools(domain_detected)
        applications = get_domain_applications(domain_detected)
        
        # Build unit_topics lookup for quick access
        unit_topics_map = {}
        if unit_topics:
            for ut in unit_topics:
                unit_num = ut.get('unit_number', 0)
                if unit_num:
                    unit_topics_map[unit_num] = ut.get('topics', [])
        
        # Generate units one by one
        units = []
        for unit_num in range(1, num_units + 1):
            # Use unit-specific topics if available, otherwise use general keywords
            unit_keywords = unit_topics_map.get(unit_num, keywords)
            
            # Get enhanced prompt for this unit
            prompts = self.prompts.get_unit_generation_prompt(
                course_title=course_title,
                unit_number=unit_num,
                total_units=num_units,
                previous_units=units,
                keywords=unit_keywords,  # Use unit-specific topics
                domain_tools=domain_tools,
                applications=applications,
                hours_per_unit=hours_per_unit
            )
            
            # Generate unit content
            response = self.ai.generate(
                prompt=prompts['user'],
                system_prompt=prompts['system'],
                task_type='generation',
                temperature=0.6,
                max_tokens=1500  # Increased for comprehensive topic descriptions
            )
            
            # Parse unit
            unit = self._parse_unit_response(response, unit_num, hours_per_unit)
            if unit:
                units.append(unit)
        
        return units[:num_units]
    
    def _parse_unit_response(self, response: str, unit_number: int, hours: int) -> Dict[str, Any]:
        """Parse AI-generated unit response into structured format with comprehensive topics"""
        lines = response.split('\n')
        unit = None
        current_topics = []
        current_topic = None
        overview_lines = []
        learning_activities = []
        
        # State machine for parsing
        parsing_state = 'searching'  # searching, overview, topic, subtopics, concepts, examples, activities
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Look for unit title
            if ('unit' in line_stripped.lower() and ':' in line_stripped) or \
               (line_stripped.startswith('**Unit') and ':' in line_stripped):
                if ':' in line_stripped:
                    title = line_stripped.split(':', 1)[1].strip().strip('*').strip()
                else:
                    title = line_stripped.strip('*').strip()
                
                unit = {
                    'unit_number': unit_number,
                    'title': title,
                    'overview': '',
                    'topics': [],
                    'learning_activities': [],
                    'hours': hours
                }
                parsing_state = 'overview'
                continue
            
            # Look for overview section
            if 'overview' in line_stripped.lower() and ':' in line_stripped:
                parsing_state = 'overview'
                overview_text = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ''
                if overview_text:
                    overview_lines.append(overview_text)
                continue
            
            # Look for new topic (numbered or bold format)
            if (line_stripped and (
                (line_stripped[0].isdigit() and '.' in line_stripped[:3]) or
                line_stripped.startswith('**') or
                line_stripped.startswith('- **')
            )):
                # Save previous topic if exists
                if current_topic:
                    current_topics.append(current_topic)
                
                # Extract topic title
                topic_title = line_stripped.lstrip('0123456789.-) ').strip('*').strip()
                if ':' in topic_title and len(topic_title.split(':')[0]) < 80:
                    topic_title = topic_title.split(':')[0].strip()
                
                if len(topic_title) > 8:  # Valid topic
                    current_topic = {
                        'topic': topic_title,
                        'description': '',
                        'subtopics': [],
                        'key_concepts': [],
                        'practical_examples': []
                    }
                    parsing_state = 'topic'
                continue
            
            # Parse description
            if current_topic and parsing_state == 'topic':
                if 'description:' in line_stripped.lower():
                    desc = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ''
                    current_topic['description'] = desc
                    continue
                elif 'subtopic' in line_stripped.lower():
                    parsing_state = 'subtopics'
                    subtopics_text = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ''
                    if subtopics_text:
                        current_topic['subtopics'] = [s.strip() for s in subtopics_text.split(',')]
                    continue
                elif 'key concept' in line_stripped.lower() or 'concepts:' in line_stripped.lower():
                    parsing_state = 'concepts'
                    concepts_text = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ''
                    if concepts_text:
                        current_topic['key_concepts'] = [c.strip() for c in concepts_text.split(',')]
                    continue
                elif 'practical' in line_stripped.lower() or 'example' in line_stripped.lower():
                    parsing_state = 'examples'
                    examples_text = line_stripped.split(':', 1)[1].strip() if ':' in line_stripped else ''
                    if examples_text:
                        current_topic['practical_examples'] = [e.strip() for e in examples_text.split(',')]
                    continue
                elif not current_topic['description'] and len(line_stripped) > 20:
                    # This is likely the description
                    current_topic['description'] = line_stripped
                    continue
            
            # Parse subtopics
            if parsing_state == 'subtopics' and current_topic:
                if line_stripped.startswith('-') or line_stripped.startswith('•'):
                    subtopic = line_stripped.lstrip('-•* ').strip()
                    if subtopic:
                        current_topic['subtopics'].append(subtopic)
                continue
            
            # Parse learning activities
            if 'learning activit' in line_stripped.lower() or 'activities:' in line_stripped.lower():
                parsing_state = 'activities'
                continue
            
            if parsing_state == 'activities':
                if line_stripped.startswith('-') or line_stripped.startswith('•') or line_stripped[0].isdigit():
                    activity = line_stripped.lstrip('0123456789.-•) ').strip()
                    if activity:
                        learning_activities.append(activity)
            
            # Collect overview text
            if parsing_state == 'overview' and unit and 'topic' not in line_stripped.lower():
                if not line_stripped.startswith('**') and not line_stripped[0].isdigit():
                    overview_lines.append(line_stripped)
        
        # Save last topic
        if current_topic:
            current_topics.append(current_topic)
        
        # Add topics to unit
        if unit:
            unit['topics'] = current_topics[:6]  # Max 6 topics
            unit['overview'] = ' '.join(overview_lines[:4])  # First 4 sentences
            unit['learning_activities'] = learning_activities[:4]
        
        # Fallback if parsing failed
        if not unit:
            unit = {
                'unit_number': unit_number,
                'title': f"Unit {unit_number}",
                'overview': f"This unit covers key concepts for unit {unit_number}.",
                'topics': current_topics[:5] if current_topics else [
                    {'topic': 'Introduction and Fundamentals', 'description': 'Core concepts and foundational knowledge.', 'subtopics': [], 'key_concepts': [], 'practical_examples': []},
                    {'topic': 'Key Principles and Theory', 'description': 'Theoretical foundations and principles.', 'subtopics': [], 'key_concepts': [], 'practical_examples': []},
                    {'topic': 'Practical Applications', 'description': 'Real-world applications and use cases.', 'subtopics': [], 'key_concepts': [], 'practical_examples': []},
                    {'topic': 'Advanced Techniques', 'description': 'Advanced methods and optimization strategies.', 'subtopics': [], 'key_concepts': [], 'practical_examples': []},
                    {'topic': 'Integration and Best Practices', 'description': 'Integration approaches and industry standards.', 'subtopics': [], 'key_concepts': [], 'practical_examples': []}
                ],
                'learning_activities': learning_activities if learning_activities else [],
                'hours': hours
            }
        
        return unit
    
    def _generate_copo_summary(
        self,
        outcomes: List[Dict[str, str]],
        program_outcomes: List[str]
    ) -> str:
        """Generate concise 1-line CO-PO mapping summary"""
        if not outcomes or not program_outcomes:
            return "CO-PO mapping: All course outcomes align with program outcomes."
        
        # Create a simple mapping summary
        co_codes = [o.get('code', f'CO{i+1}') for i, o in enumerate(outcomes)]
        po_codes = program_outcomes[:5]  # Use first 5 POs for brevity
        
        # Generate concise summary
        summary = f"Course outcomes ({', '.join(co_codes)}) map to program outcomes ({', '.join(po_codes)}) with strong alignment in technical competency and problem-solving skills."
        
        return summary
        
    def _generate_methodology(self, domain: str) -> Dict[str, List[str]]:
        """Generate teaching-learning methodology"""
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
        
    def _generate_assessment_pattern(
        self,
        outcomes: List[Dict[str, str]],
        domain: str
    ) -> Dict[str, Any]:
        """Generate assessment pattern"""
        # Standard assessment pattern
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
        
        # Add lab component if applicable
        if domain in ['engineering', 'science']:
            pattern['internal']['components']['lab_work'] = 10
            pattern['internal']['components']['assignments'] = 5
            
        return pattern
        
    def _generate_references(
        self,
        course_title: str,
        keywords: List[str]
    ) -> Dict[str, List[str]]:
        """Generate reference materials"""
        
        # Get enhanced prompts for references
        prompts = self.prompts.get_references_prompt(
            course_title=course_title,
            keywords=keywords,
            course_level=self._estimate_course_level(course_title),
            domain=detect_domain(course_title, keywords)
        )
        
        response = self.ai.generate(
            prompt=prompts['user'],
            system_prompt=prompts['system'],
            task_type='generation',
            temperature=0.3,
            max_tokens=600
        )
        
        # Parse the response into categories
        textbooks = []
        references = []
        online_resources = []
        
        current_section = None
        for line in response.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Detect section headers
            lower_line = line.lower()
            if 'textbook' in lower_line or 'text book' in lower_line:
                current_section = 'textbooks'
                continue
            elif 'reference' in lower_line or 'additional' in lower_line:
                current_section = 'references'
                continue
            elif 'online' in lower_line or 'course' in lower_line or 'resource' in lower_line or 'web' in lower_line:
                current_section = 'online'
                continue
            
            # Parse line items (numbered or bulleted)
            if line[0].isdigit() or line.startswith('-') or line.startswith('•') or line.startswith('*'):
                item = line.lstrip('0123456789.-•*) ').strip()
                if item and len(item) > 10:
                    if current_section == 'textbooks':
                        textbooks.append(item)
                    elif current_section == 'references':
                        references.append(item)
                    elif current_section == 'online':
                        online_resources.append(item)
                    else:
                        # Default: add to textbooks if no section detected
                        textbooks.append(item)
        
        # If parsing failed, try to split by common patterns
        if not textbooks and not references and not online_resources:
            lines = [l.strip() for l in response.split('\n') if l.strip() and len(l.strip()) > 15]
            # Distribute evenly
            for i, line in enumerate(lines[:10]):
                clean_line = line.lstrip('0123456789.-•*) ').strip()
                if i < 4:
                    textbooks.append(clean_line)
                elif i < 7:
                    references.append(clean_line)
                else:
                    online_resources.append(clean_line)
        
        return {
            'textbooks': textbooks[:4],
            'references': references[:3],
            'online_resources': online_resources[:4],
            'raw_suggestions': response
        }
