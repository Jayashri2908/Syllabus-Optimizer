"""
Syllabus Generator for SCDO
Generates complete syllabi using IBM Granite and templates
"""

from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

from ..ibm.granite_client import GraniteClient
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
    """Generate complete syllabi from minimal inputs"""
    
    def __init__(self, granite_client: Optional[GraniteClient] = None):
        self.logger = logging.getLogger(__name__)
        self.granite = granite_client or GraniteClient()
        self.bloom_mapper = BloomMapper()
        self.validator = SyllabusValidator()
        self.refiner = IterativeRefiner(self.granite)
        self.rubric_gen = RubricGenerator()
    
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
        keywords: List[str],
        domain: str = "engineering",
        num_units: int = 5,
        num_outcomes: int = 5,
        enable_refinement: bool = False
    ) -> Dict[str, Any]:
        """
        Generate complete syllabus
        
        Args:
            course_title: Course title
            course_code: Course code
            credits: Credit hours (L-T-P format)
            program_outcomes: Relevant program outcomes
            keywords: Key topics/skills
            domain: Academic domain
            num_units: Number of units to generate
            num_outcomes: Number of course outcomes
            enable_refinement: Enable iterative refinement (slower but higher quality)
            
        Returns:
            Complete syllabus structure with quality score
        """
        self.logger.info(f"Generating syllabus for {course_title} (refinement: {enable_refinement})")
        
        # Clear cached domain for new generation
        if hasattr(self, '_cached_domain'):
            delattr(self, '_cached_domain')
        
        # Generate course overview
        overview = self._generate_overview(course_title, keywords, domain)
        
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
        
        # Generate unit-wise syllabus
        units = self._generate_units(course_title, keywords, num_units, credits)
        
        # Generate teaching methodology
        methodology = self._generate_methodology(domain)
        
        # Generate assessment pattern
        assessment = self._generate_assessment_pattern(outcomes, domain)
        
        # Generate references
        references = self._generate_references(course_title, keywords)
        
        # Generate assessment rubrics
        rubrics = self.rubric_gen.generate_rubrics(assessment, domain)
        
        # Get industry context
        industry_context = self._get_industry_context(keywords, course_title)
        
        # Create syllabus structure
        syllabus = {
            'course_title': course_title,
            'course_code': course_code,
            'credits': credits,
            'overview': overview,
            'objectives': objectives,
            'learning_outcomes': outcomes,
            'units': units,
            'teaching_methodology': methodology,
            'assessment_pattern': assessment,
            'references': references,
            'rubrics': rubrics,
            'generated': True,
            'metadata': {
                'domain_detected': self._detect_and_cache_domain(course_title, keywords),
                'course_level': self._estimate_course_level(course_title),
                'industry_context': industry_context,
                'refinement_enabled': enable_refinement
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
        domain: str
    ) -> str:
        """Generate course overview"""
        system_prompt = f"""You are a {domain} curriculum expert with 15+ years of experience.
Write an engaging course overview (2-3 paragraphs) that:
- Explains the course's relevance to modern {domain}
- Describes real-world applications and industry importance
- Highlights what makes this course valuable for students
- Mentions key skills and competencies students will develop"""

        prompt = f"""Course: {course_title}
Key Topics: {', '.join(keywords)}
Domain: {domain}
Target Audience: Undergraduate/Graduate students

Context:
- This course is essential for careers in {domain}
- Industry applications include: {self._suggest_applications(keywords, course_title)}
- Students will gain practical skills in: {', '.join(keywords[:3])}

Write a comprehensive, engaging course overview that makes students excited to take this course."""

        return self.granite.generate(prompt, system_prompt=system_prompt, temperature=0.6, max_tokens=500)
        
    def _generate_objectives(
        self,
        course_title: str,
        keywords: List[str],
        domain: str
    ) -> List[str]:
        """Generate course objectives"""
        system_prompt = f"""You are a {domain} curriculum expert with expertise in outcome-based education.
Generate 4-6 SMART (Specific, Measurable, Achievable, Relevant, Time-bound) course objectives.

GOOD EXAMPLES:
✓ "Develop proficiency in designing and implementing scalable web applications using modern frameworks"
✓ "Master advanced data structures and their applications in solving complex computational problems"

BAD EXAMPLES:
✗ "Learn programming" (too vague)
✗ "Understand computers" (not specific or measurable)

Requirements:
- Focus on skills students will gain, not just topics covered
- Use action verbs: develop, master, acquire, build, design
- Be specific about the level of proficiency expected
- Consider industry relevance and career preparation"""

        prompt = f"""Course: {course_title}
Key Topics: {', '.join(keywords)}
Domain: {domain}
Target Level: {self._estimate_course_level(course_title)}

Industry Context:
- Relevant tools/technologies: {self._suggest_tools(keywords, course_title)}
- Career paths: {self._suggest_careers(domain, course_title, keywords)}
- Practical applications: {self._suggest_applications(keywords, course_title)}
- Prerequisites: {self._suggest_prerequisites(keywords, course_title)}
- Job Market: {self._get_industry_context(keywords, course_title)}

Generate 4-6 SMART course objectives that prepare students for industry and further study.
Emphasize skills that are valuable in the current job market."""

        response = self.granite.generate(prompt, system_prompt=system_prompt, temperature=0.5, max_tokens=400)
        
        # Parse objectives
        objectives = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                obj = line.lstrip('0123456789.-•) ').strip()
                if obj:
                    objectives.append(obj)
                    
        return objectives[:6]
        
    def _generate_learning_outcomes(
        self,
        course_title: str,
        keywords: List[str],
        program_outcomes: List[str],
        num_outcomes: int
    ) -> List[Dict[str, str]]:
        """Generate course learning outcomes with strict Bloom's distribution"""
        
        # Get level-appropriate Bloom's distribution
        course_level = self._estimate_course_level(course_title)
        bloom_dist = get_bloom_distribution(course_level, num_outcomes)
        dist_str = format_distribution_for_prompt(bloom_dist)
        
        # Build verb requirements per level
        verb_requirements = []
        for level, count in bloom_dist.items():
            if count > 0:
                verbs = get_bloom_verb_list(level)
                verb_requirements.append(f"  {level.capitalize()} ({count}): {', '.join(verbs[:5])}")
        
        verb_list = "\n".join(verb_requirements)
        
        system_prompt = f"""You are an expert in writing measurable learning outcomes using Bloom's Taxonomy.
Course Level: {course_level}

CRITICAL REQUIREMENT - Bloom's Distribution:
You MUST generate EXACTLY this distribution:
{dist_str}

Use ONLY these verbs for each level:
{verb_list}

EXCELLENT EXAMPLES (Specific, Measurable, Action-oriented):
✓ "Design and implement a relational database system that meets third normal form requirements" [Create]
✓ "Analyze the time and space complexity of sorting algorithms using Big-O notation" [Analyze]
✓ "Apply object-oriented design patterns to solve real-world software engineering problems" [Apply]
✓ "Evaluate the trade-offs between different machine learning algorithms for classification tasks" [Evaluate]

POOR EXAMPLES (Vague, Not measurable):
✗ "Understand databases" - too vague, no action verb
✗ "Know about algorithms" - not measurable
✗ "Learn programming concepts" - no Bloom's verb, unclear

Requirements:
- MUST start with a Bloom's taxonomy verb from the specified level
- Be specific about what students will do
- Include measurable criteria when possible
- Follow the EXACT distribution specified above"""

        prompt = f"""Course: {course_title}
Key Topics: {', '.join(keywords)}
Program Outcomes: {', '.join(program_outcomes[:3])}
Course Level: {course_level}

REQUIRED DISTRIBUTION: {dist_str}

Generate EXACTLY {num_outcomes} measurable course learning outcomes following the EXACT Bloom's distribution above.
Each outcome must start with the appropriate Bloom's verb for its level.
Ensure specific, measurable language."""

        response = self.granite.generate(prompt, system_prompt=system_prompt, temperature=0.4, max_tokens=600)
        
        # Parse outcomes
        outcomes = []
        for i, line in enumerate(response.split('\n'), 1):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                outcome_text = line.lstrip('0123456789.-•) ').strip()
                if outcome_text:
                    # Classify Bloom's level
                    bloom_data = self.bloom_mapper.map_outcome(outcome_text)
                    
                    outcomes.append({
                        'code': f'CO{i}',
                        'description': outcome_text,
                        'bloom_level': bloom_data['bloom_level']
                    })
                    
                if len(outcomes) >= num_outcomes:
                    break
                    
        return outcomes
        
    def _generate_units(
        self,
        course_title: str,
        keywords: List[str],
        num_units: int,
        credits: str
    ) -> List[Dict[str, Any]]:
        """Generate unit-wise syllabus"""
        system_prompt = """You are a curriculum design expert specializing in structured learning paths.
Generate a detailed unit-wise syllabus with logical progression from fundamentals to advanced topics.

REQUIREMENTS:
- Each unit should have a clear, descriptive title
- 4-6 specific topics per unit
- Topics should progress logically within each unit
- Earlier units should cover prerequisites for later units
- Include both theoretical concepts and practical applications
- Topics should be specific, not generic

GOOD UNIT EXAMPLE:
Unit 1: Introduction to Machine Learning
- Supervised vs Unsupervised learning paradigms
- Training, validation, and test dataset splits
- Bias-variance tradeoff and overfitting prevention
- Performance metrics: accuracy, precision, recall, F1-score
- Python libraries for ML: scikit-learn, NumPy, Pandas

BAD UNIT EXAMPLE:
Unit 1: Basics
- Introduction
- Concepts
- Theory
- Practice"""

        # Calculate hours per unit
        try:
            l, t, p = map(int, credits.split('-'))
            total_hours = (l + t) * 15  # Assuming 15 weeks
            hours_per_unit = total_hours // num_units
        except:
            hours_per_unit = 10
            
        prompt = f"""Course: {course_title}
Key Topics: {', '.join(keywords)}
Number of Units: {num_units}
Hours per Unit: {hours_per_unit}

Context:
- Target Level: {self._estimate_course_level(course_title)}
- Industry Tools: {self._suggest_tools(keywords, course_title)}
- Applications: {self._suggest_applications(keywords, course_title)}
- Prerequisites: {self._suggest_prerequisites(keywords, course_title)}

Generate exactly {num_units} units with:
- Descriptive unit titles
- 4-6 specific topics per unit  
- Logical progression from introductory to advanced concepts
- Mix of theory and practical applications

Format:
Unit 1: [Title]
- Topic 1
- Topic 2
..."""

        response = self.granite.generate(prompt, system_prompt=system_prompt, temperature=0.7, max_tokens=2000)
        
        # Parse units (simplified parsing)
        units = []
        current_unit = None
        
        for line in response.split('\n'):
            line = line.strip()
            
            # Check for unit header
            if 'unit' in line.lower() and ':' in line:
                if current_unit:
                    units.append(current_unit)
                    
                # Extract unit number and title
                parts = line.split(':', 1)
                title = parts[1].strip() if len(parts) > 1 else "Untitled"
                
                current_unit = {
                    'unit_number': len(units) + 1,
                    'title': title,
                    'topics': [],
                    'hours': hours_per_unit
                }
            elif current_unit and line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                # Add topic
                topic = line.lstrip('0123456789.-•) ').strip()
                if topic:
                    current_unit['topics'].append(topic)
                    
        if current_unit:
            units.append(current_unit)
            
        return units[:num_units]
        
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
        system_prompt = """You are an academic librarian and subject matter expert.
Suggest REAL, well-known, authoritative books and resources that actually exist.

REQUIREMENTS:
- List actual textbooks with real authors  
- Include ISBN or publisher when possible
- Suggest relevant online courses (Coursera, edX, MIT OpenCourseWare)
- Provide recent and classic foundational texts
- Be specific with titles and authors, not generic suggestions

GOOD EXAMPLES:
✓ "Introduction to Algorithms by Thomas H. Cormen, Charles E. Leiserson (MIT Press)"
✓ "Deep Learning by Ian Goodfellow, Yoshua Bengio (MIT Press)"
✓ "Machine Learning Specialization on Coursera by Andrew Ng"

BAD EXAMPLES:
✗ "A book on programming"
✗ "Various online resources"
✗ "Standard textbooks"
"""

        prompt = f"""Course: {course_title}
Topics: {', '.join(keywords)}
Level: {self._estimate_course_level(course_title)}

Suggest specific, real resources:
1. 3-4 textbooks (include author names and publishers)
2. 2-3 reference books or research papers
3. 3-4 online resources (MOOCs, tutorials, documentation)

Be specific with titles and authors."""

        response = self.granite.generate(prompt, system_prompt=system_prompt, temperature=0.3, max_tokens=800)
        
        return {
            'textbooks': [],
            'references': [],
            'online_resources': [],
            'raw_suggestions': response
        }
