"""
Section Prompts for Staggered LLM Chaining
User prompts for each section with strictness (temperature) tuning
"""

from typing import Dict, List, Any, Optional
import json


class SectionPrompts:
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
        Generate user prompt for unit-wise syllabus section.
        
        Args:
            context: Includes previous sections and unit structure hints
        """
        keywords = context.get('keywords', [])
        num_units = context.get('num_units', 5)
        course_title = context.get('course_title', 'Untitled Course')
        
        # Get hours per unit from credits
        credits = context.get('credits', '3-1-0')
        try:
            parts = credits.split('-')
            l, t = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            total_hours = (l + t) * 15  # 15 weeks
            hours_per_unit = total_hours // num_units
        except:
            hours_per_unit = 10
        
        # Get outline from previous sections
        outcomes = context.get('learning_outcomes', context.get('outcomes', {}))
        if isinstance(outcomes, dict):
            outcome_list = outcomes.get('outcomes', [])
            co_texts = [o.get('description', '')[:80] for o in outcome_list[:4] if isinstance(o, dict)]
            outcomes_summary = '; '.join(co_texts)
        else:
            outcomes_summary = ""
        
        # Check for user-provided unit topics
        unit_topics = context.get('unit_topics', [])
        unit_hints = ""
        if unit_topics:
            hints = []
            for ut in unit_topics[:num_units]:
                unit_num = ut.get('unit_number', 0)
                topics = ut.get('topics', [])
                if unit_num and topics:
                    hints.append(f"Unit {unit_num}: {', '.join(topics[:4])}")
            if hints:
                unit_hints = f"\n\nSuggested unit structure:\n" + "\n".join(hints)
        
        return f"""Generate a COMPREHENSIVE and DETAILED unit-wise syllabus for:

Course: {course_title}
Number of Units: {num_units}
Hours per Unit: {hours_per_unit}
Key Topics to Cover: {', '.join(keywords[:10])}
Domain: {context.get('domain', 'engineering')}

Previous Context:
Learning Outcomes: {outcomes_summary[:300]}{unit_hints}

IMPORTANT: Generate EXTENSIVE, DETAILED content. Each topic description should be 4-6 sentences covering theory, practical aspects, and applications.

Respond with JSON in this exact format:
{{
  "units": [
    {{
      "unit_number": 1,
      "title": "Comprehensive Descriptive Unit Title",
      "overview": "A detailed 4-5 sentence overview explaining what this unit covers, why it is important, what students will learn, and how it connects to the overall course objectives. This should give students a clear understanding of the unit's scope and significance.",
      "topics": [
        {{
          "topic": "Detailed Main Topic Title (5-12 words)",
          "description": "A comprehensive 4-6 sentence description that explains: (1) what this topic covers theoretically, (2) the key concepts and principles involved, (3) practical applications and real-world examples, (4) common techniques or methods used, (5) how it relates to other topics. Be specific and include technical details.",
          "subtopics": [
            "Specific subtopic covering a key concept or technique",
            "Another detailed subtopic with practical focus",
            "Advanced subtopic or application area",
            "Related tools, methods, or case studies"
          ],
          "key_concepts": ["Concept 1", "Concept 2", "Concept 3"],
          "practical_examples": ["Example application 1", "Real-world use case 2"]
        }},
        {{
          "topic": "Second Comprehensive Topic Title",
          "description": "Another detailed 4-6 sentence description covering theoretical foundations, practical implementation details, industry relevance, common challenges and solutions, and connections to prerequisite knowledge.",
          "subtopics": ["Subtopic A", "Subtopic B", "Subtopic C"],
          "key_concepts": ["Key principle 1", "Key principle 2"],
          "practical_examples": ["Industry example", "Lab exercise scenario"]
        }}
      ],
      "learning_activities": [
        "Hands-on laboratory exercise: Detailed description of the lab activity",
        "Case study analysis: Analysis of a real-world application",
        "Programming/Design assignment: Specific project or problem set",
        "Group discussion: Topic for collaborative learning"
      ],
      "suggested_readings": ["Chapter X from Textbook", "Research paper or article"],
      "assessment_ideas": ["Quiz on theoretical concepts", "Practical lab evaluation"],
      "hours": {hours_per_unit}
    }},
    ... (repeat this detailed structure for all {num_units} units)
  ]
}}

CRITICAL REQUIREMENTS - BE VERY DETAILED:

1. UNIT OVERVIEW (4-5 sentences each):
   - Explain what the unit covers in detail
   - Why this unit is important
   - Prerequisites or connections to previous units
   - Expected learning outcomes for this unit

2. TOPICS - Generate 5-6 topics per unit, each with:
   - Topic title: 5-12 words, specific and descriptive
   - Description: 4-6 FULL SENTENCES covering:
     * Theoretical foundations and key concepts
     * Practical implementation or application details
     * Real-world examples and industry relevance
     * Common techniques, algorithms, or methods
     * Connections to other topics or prerequisites
   - Subtopics: 3-5 specific sub-areas for each topic
   - Key concepts: 2-4 essential terms or principles
   - Practical examples: 1-2 real-world applications

3. LEARNING ACTIVITIES (3-4 per unit):
   - Specific, actionable activities
   - Mix of individual and group work
   - Include labs, projects, discussions, presentations

4. ADDITIONAL CONTENT:
   - Suggested readings for each unit
   - Assessment ideas (quizzes, assignments, projects)

5. PROGRESSION:
   - Unit 1: Foundation and fundamentals
   - Middle units: Core concepts with increasing complexity
   - Final units: Advanced topics, integration, and applications

Generate RICH, COMPREHENSIVE content. Do NOT be brief. Each unit should have substantial detail."""

    @staticmethod
    def get_references_prompt(context: Dict[str, Any]) -> str:
        """
        Generate user prompt for references section.
        
        Args:
            context: Includes all previous sections for topic alignment
        """
        keywords = context.get('keywords', [])
        domain = context.get('domain', 'general')
        
        # Get course level
        course_title = context.get('course_title', '')
        if any(term in course_title.lower() for term in ['advanced', 'graduate', 'phd']):
            level = "advanced/graduate"
        elif any(term in course_title.lower() for term in ['intro', 'basic', 'fundamental']):
            level = "introductory"
        else:
            level = "intermediate/undergraduate"
        
        return f"""Generate references for:

Course: {context.get('course_title', 'Untitled Course')}
Domain: {domain}
Level: {level}
Topics: {', '.join(keywords[:6])}

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
