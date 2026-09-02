"""
Syllabus Generator for SCDO
Generates complete syllabi using AI (OpenRouter/Gemini) with enhanced prompts
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
from .bloom_distribution import get_bloom_distribution, format_distribution_for_prompt
from .iterative_refiner import IterativeRefiner
from .industry_data import format_industry_context, get_industry_skills
from .rubric_generator import RubricGenerator
from .section_prompts import SectionPrompts
from .section_schemas import (
    OverviewSection,
    ObjectivesSection,
    LearningOutcomesSection,
    UnitsSection,
    ReferencesSection
)
from .chained_generator import ChainedSyllabusGenerator


class SyllabusGenerator:
    """Generate complete syllabi from minimal inputs with AI"""
    
    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.logger = logging.getLogger(__name__)
        
        # Use ModelManager for AI model orchestration
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
                self.logger.warning("No AI models available! Please configure OpenRouter or Gemini.")
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
        
        self.logger.info(f"Generating syllabus for {course_title} (chained: {use_chained_generation}, refinement: {enable_refinement})")
        
        # Clear cached domain for new generation
        if hasattr(self, '_cached_domain'):
            delattr(self, '_cached_domain')
        
        # Handle keywords: use unit_topics or fallback to keywords
        keywords = keywords or []
        if unit_topics:
            all_topics = []
            for unit in unit_topics:
                all_topics.extend(unit.get('topics', []))
            if all_topics:
                keywords = all_topics
        
        effective_level = course_level if course_level else self._estimate_course_level(course_title)
        
        if use_chained_generation:
            return self._generate_with_chaining(
                course_title=course_title,
                course_code=course_code,
                credits=credits,
                program_outcomes=program_outcomes,
                keywords=keywords,
                unit_topics=unit_topics,
                textbooks=textbooks,
                references=references,
                online_resources=online_resources,
                domain=domain,
                num_units=num_units,
                num_outcomes=num_outcomes,
                enable_refinement=enable_refinement,
                program=program,
                year=year,
                course_level=effective_level
            )
        
        return self._generate_standard(
            course_title=course_title,
            course_code=course_code,
            credits=credits,
            program_outcomes=program_outcomes,
            keywords=keywords,
            unit_topics=unit_topics,
            textbooks=textbooks,
            references=references,
            online_resources=online_resources,
            domain=domain,
            num_units=num_units,
            num_outcomes=num_outcomes,
            enable_refinement=enable_refinement,
            program=program,
            year=year,
            course_level=effective_level
        )
    
    def _generate_with_chaining(
        self,
        course_title: str,
        course_code: str,
        credits: str,
        program_outcomes: List[str],
        keywords: List[str],
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
        course_level: str = ""
    ) -> Dict[str, Any]:
        """Generate syllabus using chained (staggered) LLM calls with accumulated context."""
        self.logger.info("Using chained generation for context-aware syllabus creation")
        
        chained_gen = ChainedSyllabusGenerator(self.ai)
        
        course_info = {
            'course_title': course_title,
            'course_code': course_code,
            'credits': credits,
            'program': program,
            'year': year,
            'course_level': course_level,
            'keywords': keywords,
            'domain': domain,
            'program_outcomes': program_outcomes,
            'unit_topics': unit_topics,
        }
        
        try:
            syllabus = chained_gen.generate_staggered(
                course_info=course_info,
                num_units=num_units,
                num_outcomes=num_outcomes,
                verbose=True
            )
        except Exception as e:
            self.logger.error(f"Chained generation failed: {e}. Falling back to standard generation.")
            return self._generate_standard(
                course_title=course_title,
                course_code=course_code,
                credits=credits,
                program_outcomes=program_outcomes,
                keywords=keywords,
                unit_topics=unit_topics,
                textbooks=textbooks,
                references=references,
                online_resources=online_resources,
                domain=domain,
                num_units=num_units,
                num_outcomes=num_outcomes,
                enable_refinement=enable_refinement,
                program=program,
                year=year,
                course_level=course_level
            )
        
        syllabus['course_level'] = course_level
        syllabus['domain'] = domain
        
        has_user_refs = (
            (textbooks and len(textbooks) > 0) or
            (references and len(references) > 0) or
            (online_resources and len(online_resources) > 0)
        )
        if has_user_refs:
            syllabus['references'] = {
                'textbooks': textbooks if textbooks else [],
                'references': references if references else [],
                'online_resources': online_resources if online_resources else [],
                'raw_suggestions': ''
            }
        
        syllabus['teaching_methodology'] = self._generate_methodology(domain)
        syllabus['assessment_pattern'] = self._generate_assessment_pattern(
            syllabus.get('learning_outcomes', []), domain, credits
        )
        
        industry_context = self._get_industry_context(keywords, course_title)
        syllabus['metadata'] = syllabus.get('metadata', {})
        syllabus['metadata'].update({
            'domain_detected': self._detect_and_cache_domain(course_title, keywords),
            'course_level': course_level,
            'industry_context': industry_context,
            'refinement_enabled': enable_refinement,
            'program': program,
            'year': year,
            'generation_method': 'staggered_chaining'
        })
        
        rubrics = self.rubric_gen.generate_rubrics(syllabus.get('assessment_pattern', {}), domain)
        syllabus['rubrics'] = rubrics
        
        copo_summary = self._generate_copo_summary(
            syllabus.get('learning_outcomes', []), program_outcomes
        )
        syllabus['copo_summary'] = copo_summary
        
        validation = self.validator.validate(syllabus)
        syllabus['quality_score'] = validation['score']
        syllabus['quality_grade'] = validation['grade']
        
        self.logger.info(f"Chained generation complete. Quality: {validation['grade']} ({validation['score']}/100)")
        return syllabus
    
    def _generate_standard(
        self,
        course_title: str,
        course_code: str,
        credits: str,
        program_outcomes: List[str],
        keywords: List[str],
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
        course_level: str = ""
    ) -> Dict[str, Any]:
        """Standard (non-chained) generation pipeline — original logic."""
        overview = self._generate_overview(course_title, keywords, domain, program, year)
        
        objectives = self._generate_objectives(course_title, keywords, domain)
        
        if enable_refinement and objectives:
            self.logger.info("Refining objectives...")
            objectives = self.refiner.refine_objectives(objectives, course_title, keywords)
        
        outcomes = self._generate_learning_outcomes(
            course_title, keywords, program_outcomes, num_outcomes
        )
        
        if enable_refinement and outcomes:
            self.logger.info("Refining learning outcomes...")
            outcomes = self.refiner.refine_learning_outcomes(
                outcomes, course_title, keywords, program_outcomes, num_outcomes
            )
        
        units = self._generate_units(course_title, keywords, num_units, credits, unit_topics)
        
        methodology = self._generate_methodology(domain)
        
        assessment = self._generate_assessment_pattern(outcomes, domain, credits)
        
        has_user_refs = (
            (textbooks and len(textbooks) > 0) or 
            (references and len(references) > 0) or 
            (online_resources and len(online_resources) > 0)
        )
        
        if has_user_refs:
            refs = {
                'textbooks': textbooks if textbooks else [],
                'references': references if references else [],
                'online_resources': online_resources if online_resources else [],
                'raw_suggestions': ''
            }
        else:
            refs = self._generate_references(course_title, keywords)
        
        rubrics = self.rubric_gen.generate_rubrics(assessment, domain)
        
        industry_context = self._get_industry_context(keywords, course_title)
        
        copo_summary = self._generate_copo_summary(outcomes, program_outcomes)
        
        syllabus = {
            'course_title': course_title,
            'course_code': course_code,
            'credits': credits,
            'program': program,
            'year': year,
            'course_level': course_level,
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
                'course_level': course_level,
                'industry_context': industry_context,
                'refinement_enabled': enable_refinement,
                'program': program,
                'year': year
            }
        }
        
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
        """Generate course overview using structured JSON"""
        
        context = {
            "course_title": course_title,
            "keywords": keywords,
            "domain": domain,
            "program": program,
            "year": year
        }
        
        # Get prompt configuration
        system_prompt, user_prompt, strictness = SectionPrompts.get_prompt_for_section(
            "overview", context
        )
        
        try:
            result = self.ai.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                schema=OverviewSection,
                task_type='generation',
                temperature=strictness.get('temperature', 0.3),
                max_tokens=strictness.get('max_tokens', 400)
            )
            return result.get('overview_text', '')
        except Exception as e:
            self.logger.error(f"Overview generation failed: {e}")
            # Fallback
            return f"This course provides a comprehensive introduction to {course_title}. Students will learn key concepts including {', '.join(keywords[:3])}."
        
    def _generate_objectives(
        self,
        course_title: str,
        keywords: List[str],
        domain: str,
        overview: str = ""
    ) -> List[str]:
        """Generate course objectives using structured JSON"""
        
        context = {
            "course_title": course_title,
            "domain": domain,
            "keywords": keywords,
            "overview": overview
        }
        
        system_prompt, user_prompt, strictness = SectionPrompts.get_prompt_for_section(
            "objectives", context
        )
        
        try:
            result = self.ai.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                schema=ObjectivesSection,
                task_type='generation',
                temperature=strictness.get('temperature', 0.2),
                max_tokens=strictness.get('max_tokens', 500)
            )
            
            # Extract text from outcome items
            objectives_list = result.get('objectives', [])
            return [obj.get('text', '') if isinstance(obj, dict) else str(obj) for obj in objectives_list]
            
        except Exception as e:
            self.logger.error(f"Objectives generation failed: {e}")
            # Fallback
            return [
                f"Understand the core principles of {course_title}",
                f"Apply {keywords[0] if keywords else 'key concepts'} to solve problems",
                f"Analyze real-world applications in the {domain} domain",
                "Design effective solutions using industry-standard tools",
                "Evaluate performance and optimize implementations"
            ]
        
    def _generate_learning_outcomes(
        self,
        course_title: str,
        keywords: List[str],
        program_outcomes: List[str],
        num_outcomes: int,
        objectives: List[str] = None
    ) -> List[Dict[str, str]]:
        """Generate learning outcomes using structured JSON"""
        
        context = {
            "course_title": course_title,
            "domain": detect_domain(course_title, keywords),
            "keywords": keywords,
            "num_outcomes": num_outcomes,
            "objectives": objectives or []
        }
        
        system_prompt, user_prompt, strictness = SectionPrompts.get_prompt_for_section(
            "outcomes", context
        )
        
        try:
            result = self.ai.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                schema=LearningOutcomesSection,
                task_type='generation',
                temperature=strictness.get('temperature', 0.2),
                max_tokens=strictness.get('max_tokens', 700)
            )
            
            # Convert to internal format if needed
            outcomes = result.get('outcomes', [])
            return [
                {
                    'code': o.get('code'),
                    'description': o.get('description'),
                    'bloom_level': o.get('bloom_level')
                }
                for o in outcomes
            ]
            
        except Exception as e:
            self.logger.error(f"Outcomes generation failed: {e}")
            # Fallback
            outcomes = []
            for i in range(num_outcomes):
                outcomes.append({
                    'code': f'CO{i+1}',
                    'description': f"Apply {keywords[i % len(keywords)] if keywords else 'concepts'} to solve problems",
                    'bloom_level': 'apply'
                })
            return outcomes
        
    def _generate_units(
        self,
        course_title: str,
        keywords: List[str],
        num_units: int,
        credits: str,
        unit_topics: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate unit-wise syllabus using structured JSON"""
        
        context = {
            "course_title": course_title,
            "keywords": keywords,
            "num_units": num_units,
            "credits": credits,
            "unit_topics": unit_topics,
            "domain": detect_domain(course_title, keywords)
        }
        
        system_prompt, user_prompt, strictness = SectionPrompts.get_prompt_for_section(
            "units", context
        )
        
        try:
            result = self.ai.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                schema=UnitsSection,
                task_type='generation',
                temperature=strictness.get('temperature', 0.4),
                max_tokens=strictness.get('max_tokens', 6000)
            )
            
            # Convert to internal format
            units = result.get('units', [])
            return [
                {
                    'unit_number': u.get('unit_number'),
                    'title': u.get('title'),
                    'overview': u.get('overview', ''),
                    'topics': [
                        {
                            'topic': t.get('topic'),
                            'description': t.get('description', ''),
                            'subtopics': t.get('subtopics', []),
                            'key_concepts': t.get('key_concepts', []),
                            'practical_examples': t.get('practical_examples', [])
                        } if isinstance(t, dict) else {'topic': str(t)}
                        for t in u.get('topics', [])
                    ],
                    'learning_activities': u.get('learning_activities', []),
                    'hours': u.get('hours', 10)
                }
                for u in units
            ]
            
        except Exception as e:
            self.logger.error(f"Units generation failed: {e}")
            return []
    

    
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
        
    def _generate_methodology(
        self,
        domain: str,
        course_title: str = "",
        outcomes: List[Dict[str, str]] = None
    ) -> Dict[str, List[str]]:
        """Generate domain-aware teaching-learning methodology"""
        domain_methodologies = {
            'machine_learning': {
                'teaching_methods': [
                    'Lectures with Jupyter notebook demonstrations',
                    'Hands-on ML model building workshops',
                    'Paper reading and discussion sessions',
                    'Kaggle-style competition projects',
                    'Code review and model debugging sessions'
                ],
                'learning_activities': [
                    'Implement ML algorithms from scratch in Python',
                    'Train and evaluate models on real datasets',
                    'Participate in ML hackathons and competitions',
                    'Write technical blog posts on ML concepts',
                    'Peer code review of ML pipelines'
                ]
            },
            'web_development': {
                'teaching_methods': [
                    'Live coding sessions with real project builds',
                    'Pair programming exercises',
                    'Code review and refactoring workshops',
                    'Agile sprint-based project development',
                    'Design review and UX critique sessions'
                ],
                'learning_activities': [
                    'Build full-stack web applications from specifications',
                    'Deploy applications to cloud platforms',
                    'Write unit and integration tests',
                    'Contribute to open-source web projects',
                    'Create responsive UI components'
                ]
            },
            'data_science': {
                'teaching_methods': [
                    'Exploratory data analysis workshops',
                    'Statistical inference case studies',
                    'Data visualization critique sessions',
                    'Guest lectures from industry data scientists',
                    'Capstone project with real-world datasets'
                ],
                'learning_activities': [
                    'Perform EDA on messy real-world datasets',
                    'Build interactive dashboards with Tableau/Power BI',
                    'Write SQL queries for complex data extraction',
                    'Present data-driven insights to stakeholders',
                    'Conduct A/B testing and experiment analysis'
                ]
            },
            'cybersecurity': {
                'teaching_methods': [
                    'CTF (Capture The Flag) challenge sessions',
                    'Red team / blue team simulation exercises',
                    'Security audit walkthroughs',
                    'Incident response tabletop exercises',
                    'Threat modeling workshops'
                ],
                'learning_activities': [
                    'Perform vulnerability assessments on lab environments',
                    'Configure firewalls and intrusion detection systems',
                    'Analyze network traffic for malicious patterns',
                    'Write security policies and procedures',
                    'Conduct penetration testing on authorized targets'
                ]
            },
            'database': {
                'teaching_methods': [
                    'Database design workshops with ER modeling',
                    'SQL query optimization challenges',
                    'Stored procedure and trigger development',
                    'Database administration lab sessions',
                    'NoSQL vs SQL comparison case studies'
                ],
                'learning_activities': [
                    'Design normalized database schemas',
                    'Write complex SQL queries with joins and subqueries',
                    'Implement indexing strategies for performance',
                    'Set up replication and backup procedures',
                    'Build data pipelines with ETL processes'
                ]
            },
            'cloud_computing': {
                'teaching_methods': [
                    'Cloud architecture design workshops',
                    'Infrastructure-as-Code labs with Terraform',
                    'Container orchestration with Kubernetes demos',
                    'CI/CD pipeline building sessions',
                    'Cloud cost optimization case studies'
                ],
                'learning_activities': [
                    'Deploy microservices on AWS/Azure/GCP',
                    'Configure auto-scaling and load balancing',
                    'Build CI/CD pipelines with Jenkins/GitLab CI',
                    'Implement monitoring with Prometheus/Grafana',
                    'Practice infrastructure automation with Ansible'
                ]
            },
            'mobile_development': {
                'teaching_methods': [
                    'App prototyping and UI/UX design sessions',
                    'Cross-platform development workshops',
                    'Mobile testing and debugging labs',
                    'App store deployment walkthroughs',
                    'Performance profiling exercises'
                ],
                'learning_activities': [
                    'Build mobile apps with native and cross-platform frameworks',
                    'Implement push notifications and offline storage',
                    'Write unit and UI tests for mobile apps',
                    'Optimize app performance and battery usage',
                    'Publish apps to Google Play and App Store'
                ]
            },
            'computer_networks': {
                'teaching_methods': [
                    'Network simulation labs with Cisco Packet Tracer/GNS3',
                    'Protocol analysis with Wireshark demos',
                    'Network design and subnetting exercises',
                    'SDN controller programming workshops',
                    'Network security configuration labs'
                ],
                'learning_activities': [
                    'Configure routers, switches, and firewalls',
                    'Capture and analyze network protocol traffic',
                    'Design enterprise network topologies',
                    'Implement VLANs and access control lists',
                    'Automate network tasks with Python scripts'
                ]
            }
        }
        
        return domain_methodologies.get(domain, {
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
        })
        
    def _generate_assessment_pattern(
        self,
        outcomes: List[Dict[str, str]],
        domain: str,
        credits: str = "3-0-0"
    ) -> Dict[str, Any]:
        """Generate assessment pattern based on credits (L-T-P), domain, and outcomes"""
        lecture_hours = 3
        tutorial_hours = 0
        practical_hours = 0
        try:
            parts = credits.split('-')
            lecture_hours = int(parts[0])
            tutorial_hours = int(parts[1]) if len(parts) > 1 else 0
            practical_hours = int(parts[2]) if len(parts) > 2 else 0
        except (ValueError, IndexError):
            pass
        
        has_lab = practical_hours > 0 or domain in ['engineering', 'science', 'computer_science']
        has_project_heavy_outcomes = any(
            o.get('bloom_level', '') in ['create', 'evaluate']
            for o in (outcomes or [])
        )
        
        internal_weight = 40
        external_weight = 60
        
        if has_lab:
            internal_components = {
                'midterm_exam': 15,
                'assignments': 5,
                'quizzes': 5,
                'class_participation': 5,
                'lab_work': 10
            }
        elif has_project_heavy_outcomes:
            internal_components = {
                'midterm_exam': 15,
                'assignments': 5,
                'quizzes': 5,
                'class_participation': 5,
                'project': 10
            }
        else:
            internal_components = {
                'midterm_exam': 20,
                'assignments': 10,
                'quizzes': 5,
                'class_participation': 5
            }
        
        external_components = {'final_exam': 60}
        
        return {
            'internal': {
                'weightage': internal_weight,
                'components': internal_components
            },
            'external': {
                'weightage': external_weight,
                'components': external_components
            }
        }
        
    def _generate_references(
        self,
        course_title: str,
        keywords: List[str]
    ) -> Dict[str, List[str]]:
        """Generate reference materials using structured JSON"""
        
        context = {
            "course_title": course_title,
            "keywords": keywords,
            "domain": detect_domain(course_title, keywords)
        }
        
        system_prompt, user_prompt, strictness = SectionPrompts.get_prompt_for_section(
            "references", context
        )
        
        try:
            result = self.ai.generate_json(
                prompt=user_prompt,
                system_prompt=system_prompt,
                schema=ReferencesSection,
                task_type='generation',
                temperature=strictness.get('temperature', 0.1),
                max_tokens=strictness.get('max_tokens', 600)
            )
            
            return {
                'textbooks': result.get('textbooks', []),
                'references': result.get('reference_books', []),
                'online_resources': result.get('online_resources', []),
                'raw_suggestions': ''
            }
            
        except Exception as e:
            self.logger.error(f"References generation failed: {e}")
            return {
                'textbooks': ["No textbooks generated"],
                'references': [],
                'online_resources': [],
                'raw_suggestions': ''
            }

