"""
Section Prompts for Staggered LLM Chaining
User prompts for each section with strictness (temperature) tuning
"""

from typing import Dict, List, Any, Optional
import json
import yaml
from pathlib import Path


class SectionPrompts:
    
    _verified_refs = None
    
    @classmethod
    def _load_verified_references(cls) -> dict:
        if cls._verified_refs is None:
            config_path = Path(__file__).parent.parent.parent / "configs" / "verified_references.yaml"
            try:
                with open(config_path, 'r') as f:
                    cls._verified_refs = yaml.safe_load(f) or {}
            except Exception:
                cls._verified_refs = {}
        return cls._verified_refs
    """
    User prompts for each syllabus section.
    Uses a shared system prompt for overall structure consistency,
    with section-specific user prompts for each generation stage.
    """
    
    # Master system prompt declaring overall syllabus structure
    MASTER_SYSTEM_PROMPT = """You are an expert curriculum designer and academic content specialist creating a comprehensive course syllabus.

OVERALL SYLLABUS STRUCTURE:
1. Course Overview (4-5 sentences describing the course)
2. Course Objectives (5-6 action-verb led objectives)
3. Learning Outcomes with Bloom's Taxonomy levels (5-6 COs)
4. Unit-wise Syllabus (5 units with 5-6 topics each)
5. References (textbooks, reference books, online resources)

CRITICAL RULES:
1. ALWAYS respond with valid JSON matching the requested schema
2. Do NOT include markdown formatting, code blocks, or explanatory text
3. Be concise - quality over quantity
4. Use proper academic language
5. Each section builds on previous context

You will generate each section one at a time. The user will provide accumulated context from previous sections."""

    # Strictness configuration per section
    # Lower temperature = more consistent/deterministic output
    # Higher temperature = more creative/varied output
    STRICTNESS_CONFIG = {
        "overview": {
            "temperature": 0.3,  # Moderate - allow some creativity
            "max_tokens": 400,
            "description": "Course overview needs some creativity but consistency"
        },
        "objectives": {
            "temperature": 0.2,  # Low - objectives should be structured
            "max_tokens": 500,
            "description": "Objectives need consistent action-verb format"
        },
        "outcomes": {
            "temperature": 0.2,  # Low - outcomes must follow Bloom's structure
            "max_tokens": 700,
            "description": "Learning outcomes must be precise and measurable"
        },
        "units": {
            "temperature": 0.4,  # Allow variety in detailed content
            "max_tokens": 6000,  # Significantly increased for comprehensive unit content
            "description": "Units need extensive detailed topics with descriptions, subtopics, examples"
        },
        "references": {
            "temperature": 0.1,  # Very low - must cite real resources
            "max_tokens": 600,
            "description": "References must be real and accurate"
        },
    }
    
    @classmethod
    def get_strictness(cls, section: str) -> Dict[str, Any]:
        """Get temperature and token config for a section"""
        return cls.STRICTNESS_CONFIG.get(section, {
            "temperature": 0.3,
            "max_tokens": 500
        })
    
    @staticmethod
    def get_overview_prompt(context: Dict[str, Any]) -> str:
        """
        Generate user prompt for course overview section.
        
        Args:
            context: Contains course_title, course_code, domain, keywords, etc.
            
        Returns:
            User prompt for overview generation
        """
        keywords = context.get('keywords', [])
        keywords_str = ', '.join(keywords[:6]) if keywords else 'general topics'
        
        return f"""Generate the course overview for:

Course Title: {context.get('course_title', 'Untitled Course')}
Course Code: {context.get('course_code', 'XXX000')}
Credits: {context.get('credits', '3-0-0')}
Domain: {context.get('domain', 'general')}
Program: {context.get('program', '')}
Year/Semester: {context.get('year', '')}
Key Topics: {keywords_str}

Respond with JSON in this exact format:
{{"overview_text": "Your 4-5 sentence course overview here..."}}

Requirements:
- Write exactly 4-5 sentences (80-120 words)
- First sentence: What the course covers
- Second sentence: Core concepts and skills
- Third sentence: Tools/technologies used
- Fourth sentence: Industry relevance and applications
- Optional fifth: Career preparation

Be concise, specific, and avoid generic statements."""

    @staticmethod
    def get_objectives_prompt(context: Dict[str, Any]) -> str:
        """
        Generate user prompt for course objectives section.
        
        Args:
            context: Includes previous overview
        """
        overview = context.get('overview', {})
        overview_text = overview.get('overview_text', '') if isinstance(overview, dict) else str(overview)
        
        keywords = context.get('keywords', [])
        keywords_str = ', '.join(keywords[:5]) if keywords else ''
        
        return f"""Generate course objectives for:

Course: {context.get('course_title', 'Untitled Course')}
Domain: {context.get('domain', 'general')}
Key Topics: {keywords_str}

Previous Context:
Overview: {overview_text[:300]}...

Respond with JSON in this exact format:
{{
  "objectives": [
    {{"text": "First objective starting with action verb"}},
    {{"text": "Second objective starting with action verb"}},
    {{"text": "Third objective starting with action verb"}},
    {{"text": "Fourth objective starting with action verb"}},
    {{"text": "Fifth objective starting with action verb"}}
  ]
}}

Requirements:
- Generate exactly 5-6 objectives
- Each objective: 15-25 words maximum
- Start each with action verb (Develop, Master, Build, Design, Implement, Understand, Apply)
- Be specific to the course topics
- Cover both theoretical knowledge and practical skills"""

    @staticmethod
    def get_outcomes_prompt(context: Dict[str, Any]) -> str:
        """
        Generate user prompt for learning outcomes section.
        
        Args:
            context: Includes previous overview and objectives
        """
        objectives = context.get('objectives', {})
        if isinstance(objectives, dict):
            obj_list = objectives.get('objectives', [])
            obj_texts = [o.get('text', '') if isinstance(o, dict) else str(o) for o in obj_list[:3]]
            objectives_str = '; '.join(obj_texts)
        else:
            objectives_str = str(objectives)[:200]
        
        keywords = context.get('keywords', [])
        num_outcomes = context.get('num_outcomes', 5)
        
        return f"""Generate learning outcomes for:

Course: {context.get('course_title', 'Untitled Course')}
Domain: {context.get('domain', 'general')}
Topics: {', '.join(keywords[:5])}

Previous Context:
Objectives: {objectives_str[:300]}

Respond with JSON in this exact format:
{{
  "outcomes": [
    {{"code": "CO1", "description": "Learning outcome description", "bloom_level": "apply"}},
    {{"code": "CO2", "description": "Learning outcome description", "bloom_level": "analyze"}},
    {{"code": "CO3", "description": "Learning outcome description", "bloom_level": "evaluate"}},
    {{"code": "CO4", "description": "Learning outcome description", "bloom_level": "create"}},
    {{"code": "CO5", "description": "Learning outcome description", "bloom_level": "understand"}}
  ]
}}

Requirements:
- Generate exactly {num_outcomes} learning outcomes
- Each description: 20-40 words, starting with Bloom's verb
- bloom_level must be one of: remember, understand, apply, analyze, evaluate, create
- Distribute levels: mostly apply/analyze/evaluate, some create, minimal remember
- Each outcome must be measurable and specific
- Cover the main course topics"""

    @staticmethod
    def get_units_prompt(context: Dict[str, Any]) -> str:
        """
        Generate user prompt for unit-wise syllabus section - University format.
        """
        keywords = context.get('keywords', [])
        num_units = context.get('num_units', 5)
        course_title = context.get('course_title', 'Untitled Course')
        
        # Get hours per unit from credits
        credits = context.get('credits', '3-1-0')
        try:
            parts = credits.split('-')
            l, t = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            total_hours = (l + t) * 15
            hours_per_unit = total_hours // num_units
        except:
            hours_per_unit = 10
        
        # Check for user-provided unit topics
        unit_topics = context.get('unit_topics', [])
        unit_structure = ""
        if unit_topics:
            hints = []
            for ut in unit_topics[:num_units]:
                unit_num = ut.get('unit_number', 0)
                topics = ut.get('topics', [])
                if unit_num and topics:
                    hints.append(f"Unit {unit_num}: {', '.join(topics[:6])}")
            if hints:
                unit_structure = "\n\n**USER-PROVIDED UNIT STRUCTURE (USE THESE):**\n" + "\n".join(hints)
        
        # Distribute keywords across units
        keyword_hints = ""
        if keywords and not unit_topics:
            kw_per_unit = max(1, len(keywords) // num_units)
            keyword_hints = "\n\n**KEYWORD DISTRIBUTION (use for unit themes):**"
            for i in range(num_units):
                start = i * kw_per_unit
                end = start + kw_per_unit if i < num_units - 1 else len(keywords)
                unit_kw = keywords[start:end] if start < len(keywords) else []
                if unit_kw:
                    keyword_hints += f"\n- Unit {i+1}: {', '.join(unit_kw)}"
        
        return f"""Generate a CONCISE university-style syllabus for:

Course: {course_title}
Units: {num_units}
Hours/Unit: {hours_per_unit}

**KEYWORDS (use these as topic names):**
{', '.join(keywords) if keywords else 'Not provided'}{unit_structure}{keyword_hints}

**CRITICAL RULES:**
1. Unit titles: 5-10 words, using keywords
2. Topics: 8-10 SHORT names per unit (3-8 words each)
3. Use the keywords provided - DO NOT use generic names
4. NO descriptions, subtopics, or examples - just topic names
5. Cover ALL major aspects of each unit's theme

Respond with JSON:
{{
  "units": [
    {{
      "unit_number": 1,
      "title": "[Title from keywords - 5-10 words]",
      "topics": [
        {{"topic": "[Topic from keywords - 3-8 words]"}},
        {{"topic": "[Topic from keywords - 3-8 words]"}},
        {{"topic": "[Topic from keywords - 3-8 words]"}},
        {{"topic": "[Topic from keywords - 3-8 words]"}},
        {{"topic": "[Topic from keywords - 3-8 words]"}},
        {{"topic": "[Topic from keywords - 3-8 words]"}},
        {{"topic": "[Topic from keywords - 3-8 words]"}},
        {{"topic": "[Topic from keywords - 3-8 words]"}}
      ],
      "hours": {hours_per_unit}
    }}
  ]
}}

EXAMPLE for "Machine Learning, Neural Networks, Deep Learning, CNN, RNN":
{{
  "units": [
    {{
      "unit_number": 1,
      "title": "Introduction to Machine Learning Fundamentals",
      "topics": [
        {{"topic": "Machine learning concepts and types"}},
        {{"topic": "Supervised and unsupervised learning"}},
        {{"topic": "Training and validation techniques"}},
        {{"topic": "Feature engineering methods"}},
        {{"topic": "Model evaluation metrics"}},
        {{"topic": "Bias-variance tradeoff"}},
        {{"topic": "Overfitting and underfitting"}},
        {{"topic": "Cross-validation techniques"}}
      ],
      "hours": 10
    }},
    {{
      "unit_number": 2,
      "title": "Neural Networks Architecture and Training",
      "topics": [
        {{"topic": "Artificial neural network basics"}},
        {{"topic": "Perceptrons and multilayer networks"}},
        {{"topic": "Activation functions and layers"}},
        {{"topic": "Backpropagation algorithm"}},
        {{"topic": "Gradient descent optimization"}},
        {{"topic": "Weight initialization techniques"}},
        {{"topic": "Batch normalization methods"}},
        {{"topic": "Regularization and dropout"}}
      ],
      "hours": 10
    }}
  ]
}}

Generate exactly {num_units} units with 8-10 concise topic names each from the keywords."""

    @classmethod
    def get_references_prompt(cls, context: Dict[str, Any]) -> str:
        """
        Generate user prompt for references section with verified suggestions.
        """
        keywords = context.get('keywords', [])
        domain = context.get('domain', 'general')
        
        course_title = context.get('course_title', '')
        if any(term in course_title.lower() for term in ['advanced', 'graduate', 'phd']):
            level = "advanced/graduate"
        elif any(term in course_title.lower() for term in ['intro', 'basic', 'fundamental']):
            level = "introductory"
        else:
            level = "intermediate/undergraduate"
        
        verified_section = ""
        verified_refs = cls._load_verified_references()
        domain_refs = verified_refs.get(domain, verified_refs.get('general', {}))
        if domain_refs:
            verified_books = domain_refs.get('textbooks', [])
            verified_online = domain_refs.get('online_resources', [])
            if verified_books or verified_online:
                verified_section = f"""

**VERIFIED REFERENCES (choose from these - all are real and confirmed):**
Textbooks:
{chr(10).join(f'- {b}' for b in verified_books[:6])}

Online Resources:
{chr(10).join(f'- {r}' for r in verified_online[:4])}

IMPORTANT: Select 3-4 textbooks and 2-3 online resources from the verified list above. You may add 1-2 additional references if you are CERTAIN they exist."""
        
        return f"""Generate references for:

Course: {context.get('course_title', 'Untitled Course')}
Domain: {domain}
Level: {level}
Topics: {', '.join(keywords[:6])}{verified_section}

Respond with JSON in this exact format:
{{
  "textbooks": [
    "Title by Author Name (Publisher, Year/Edition)",
    "Title by Author Name (Publisher, Year/Edition)",
    "Title by Author Name (Publisher, Year/Edition)"
  ],
  "reference_books": [
    "Title by Author Name (Publisher)",
    "Title by Author Name (Publisher)"
  ],
  "online_resources": [
    "Course Name on Platform by Instructor/Institution",
    "Resource Name - Brief Description",
    "Official Documentation - URL or Description"
  ]
}}

Requirements:
- Textbooks: 3-4 REAL, well-known books with full citations
- Reference Books: 2-3 additional/specialized resources
- Online Resources: 3-4 real courses (Coursera, edX, Udemy) or official documentation
- Only suggest resources you are CERTAIN exist
- Include author names and publishers/platforms
- Mix classic and recent publications
- Appropriate for {level} level"""

    @classmethod
    def get_prompt_for_section(
        cls, 
        section: str, 
        context: Dict[str, Any]
    ) -> tuple[str, str, Dict[str, Any]]:
        """
        Get the complete prompt configuration for a section.
        
        Args:
            section: Section name (overview, objectives, outcomes, units, references)
            context: Accumulated context from previous sections
            
        Returns:
            Tuple of (system_prompt, user_prompt, strictness_config)
        """
        prompt_methods = {
            "overview": cls.get_overview_prompt,
            "objectives": cls.get_objectives_prompt,
            "outcomes": cls.get_outcomes_prompt,
            "learning_outcomes": cls.get_outcomes_prompt,
            "units": cls.get_units_prompt,
            "references": cls.get_references_prompt,
        }
        
        method = prompt_methods.get(section.lower())
        if not method:
            raise ValueError(f"Unknown section: {section}")
        
        user_prompt = method(context)
        strictness = cls.get_strictness(section.lower().replace("learning_outcomes", "outcomes"))
        
        return cls.MASTER_SYSTEM_PROMPT, user_prompt, strictness
