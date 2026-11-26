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
            "max_tokens": 8000,  # Must accommodate rich topic content (descriptions, subtopics, examples)
            "description": "Units need extensive detailed topics with descriptions, subtopics, examples"
        },
        "single_unit": {
            "temperature": 0.4,
            "max_tokens": 2500,  # Per-unit generation: focused output with rich detail
            "description": "Single unit with 5-6 richly detailed topics"
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
        Generates RICH topic content with descriptions, subtopics, key concepts, and examples.
        Keywords are treated as thematic anchors that must be expanded into real subtopics.
        """
        keywords = context.get('keywords', [])
        num_units = context.get('num_units', 5)
        course_title = context.get('course_title', 'Untitled Course')
        domain = context.get('domain', 'engineering')
        
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
                unit_structure = "\n\n**USER-PROVIDED UNIT STRUCTURE (USE THESE AS UNIT THEMES):**\n" + "\n".join(hints)
        
        return f"""Generate a comprehensive university-style syllabus for:

Course: {course_title}
Domain: {domain}
Units: {num_units}
Hours/Unit: {hours_per_unit}

**USER KEYWORDS:** {', '.join(keywords) if keywords else 'Not provided'}{unit_structure}

**STEP 1 — KEYWORD EXPANSION (MANDATORY):**
Each keyword is a THEMATIC ANCHOR, not a literal topic name. Before generating units, mentally expand each keyword into the real subtopics that any {domain} professor would cover under that theme.

For example, in a Machine Learning course:
- Keyword "introduction" → EXPAND to: hypothesis space, bias-variance tradeoff, overfitting vs underfitting, train-test-validation split, no-free-lunch theorem, types of learning (supervised/unsupervised/reinforcement)
- Keyword "regression" → EXPAND to: ordinary least squares, gradient descent, polynomial regression, regularization (L1/L2), residual analysis, multicollinearity
- Keyword "neural networks" → EXPAND to: perceptron model, backpropagation algorithm, activation functions (ReLU/sigmoid/tanh), vanishing gradients, weight initialization, batch normalization
- Keyword "deep learning" → EXPAND to: CNN architectures (LeNet/VGG/ResNet), transfer learning, data augmentation, GPU training, model compression

You MUST apply this expansion logic to the user's actual keywords for "{course_title}". Each keyword should produce 5-6 distinct, specific subtopics that are NOT just rewordings of the keyword itself.

**STEP 2 — UNIT CONSTRUCTION RULES:**
1. Each keyword (or group of related keywords) becomes ONE unit. The unit title should capture the theme, not repeat the keyword literally.
2. The topics within that unit are the EXPANDED subtopics from Step 1 — the real, specific things a student would learn.
3. Topics: 5-6 SPECIFIC sub-topics per unit, each with FULL details.
4. Each topic must be a specific sub-topic that stands alone — something you could write a 2-hour lecture about.
5. FORBIDDEN WORDS in topic names: "concepts", "fundamentals", "theory", "basics", "introduction to", "principles", "techniques and methods", "overview", "essentials", "foundations"
6. DIVERSITY RULE: No two topics in the same unit may start with the same word or phrase.
7. NO REPETITION across units: If "overfitting" is covered in Unit 1, it must NOT appear again in Unit 3. Each topic in the entire syllabus must be unique.
8. Every topic MUST include: description (2-3 sentences), subtopics (3-4 items), key_concepts (2-3 items), practical_examples (1-2 items).

Respond with JSON:
{{
  "units": [
    {{
      "unit_number": 1,
      "title": "[Specific descriptive title - 5-10 words]",
      "topics": [
        {{
          "topic": "[Specific topic name - 5-12 words]",
          "description": "[2-3 sentence explanation of what this topic covers and why it matters]",
          "subtopics": ["[specific subtopic 1]", "[specific subtopic 2]", "[specific subtopic 3]"],
          "key_concepts": ["[concept 1]", "[concept 2]"],
          "practical_examples": ["[real-world application or exercise]"]
        }}
      ],
      "hours": {hours_per_unit}
    }}
  ]
}}

**EXAMPLE — User keywords: "Introduction, Regression, Neural Networks"**
Notice how "Introduction" is NOT used as a topic name. Instead it is EXPANDED into the real foundational ML topics:

{{
  "units": [
    {{
      "unit_number": 1,
      "title": "Machine Learning Landscape and Learning Frameworks",
      "topics": [
        {{
          "topic": "Supervised, unsupervised, and reinforcement learning paradigms",
          "description": "Classifies machine learning approaches by the nature of training signal. Students learn when to apply each paradigm and how to identify the learning type for a given problem.",
          "subtopics": ["Labeled vs unlabeled data pipelines", "Reward-based learning in sequential decisions", "Semi-supervised and self-supervised approaches"],
          "key_concepts": ["Hypothesis space", "Inductive bias"],
          "practical_examples": ["Classifying real-world problems into supervised/unsupervised categories"]
        }},
        {{
          "topic": "Bias-variance tradeoff and model complexity analysis",
          "description": "Explains how model complexity affects prediction error through the decomposition into bias and variance components. Students learn to diagnose whether a model suffers from underfitting or overfitting.",
          "subtopics": ["Error decomposition into bias, variance, and noise", "Learning curves for diagnosing fit quality", "Model complexity vs generalization gap"],
          "key_concepts": ["Underfitting vs overfitting", "Irreducible error"],
          "practical_examples": ["Plotting learning curves on polynomial regression with varying degrees"]
        }},
        {{
          "topic": "Train-test-validation split and data leakage prevention",
          "description": "Covers proper data partitioning strategies for model development and evaluation. Focuses on common pitfalls like data leakage, look-ahead bias, and information bleeding across splits.",
          "subtopics": ["Holdout method and stratified splitting", "K-fold cross-validation design", "Time-series aware splitting"],
          "key_concepts": ["Data leakage", "Generalization error estimation"],
          "practical_examples": ["Detecting and preventing data leakage in a credit scoring pipeline"]
        }},
        {{
          "topic": "Performance metrics for classification and regression tasks",
          "description": "Surveys evaluation metrics beyond accuracy, including precision-recall for imbalanced classes and RMSE/MAE for regression. Students learn metric selection based on business objectives.",
          "subtopics": ["Confusion matrix and ROC-AUC analysis", "Precision-recall tradeoff for rare events", "RMSE, MAE, and R-squared interpretation"],
          "key_concepts": ["Type I vs Type II errors", "Threshold optimization"],
          "practical_examples": ["Choosing the right metric for fraud detection vs spam filtering"]
        }},
        {{
          "topic": "Feature engineering and data preprocessing pipelines",
          "description": "Covers practical data preparation including missing value imputation, encoding categorical variables, and feature scaling. Students build reproducible preprocessing pipelines.",
          "subtopics": ["One-hot and ordinal encoding strategies", "Normalization vs standardization", "Handling missing data with imputation"],
          "key_concepts": ["Feature-target relationship", "Data distribution assumptions"],
          "practical_examples": ["Building a scikit-learn pipeline for Titanic survival prediction"]
        }}
      ],
      "hours": {hours_per_unit}
    }}
  ]
}}

Generate exactly {num_units} units with 5-6 richly detailed topics each. Remember: EXPAND each keyword into real subtopics — never just revolve around the keyword itself."""

    @staticmethod
    def get_single_unit_prompt(context: Dict[str, Any]) -> str:
        """
        Generate a focused prompt for ONE unit at a time.
        This produces much richer content since the LLM budget is focused on ~5 topics.
        """
        unit_number = context.get('unit_number', 1)
        unit_theme = context.get('unit_theme', '')
        unit_keywords = context.get('unit_keywords', [])
        course_title = context.get('course_title', 'Untitled Course')
        domain = context.get('domain', 'engineering')
        hours_per_unit = context.get('hours_per_unit', 10)
        previous_units = context.get('previous_units', [])

        # Build dedup context from previously generated units
        dedup_section = ""
        if previous_units:
            covered = []
            for pu in previous_units:
                title = pu.get('title', '')
                topics = [t.get('topic', '') if isinstance(t, dict) else str(t) for t in pu.get('topics', [])]
                covered.append(f"Unit {pu.get('unit_number')}: {title} -- {', '.join(topics)}")
            dedup_section = "\n\n**ALREADY COVERED (DO NOT REPEAT):**\n" + "\n".join(covered)

        kw_str = ', '.join(unit_keywords) if unit_keywords else unit_theme

        return f"""Generate Unit {unit_number} for a university course.

Course: {course_title}
Domain: {domain}
Unit Number: {unit_number}
Unit Theme/Keywords: {kw_str}
Hours: {hours_per_unit}{dedup_section}

**INSTRUCTIONS:**
1. The keywords above are THEMATIC ANCHORS -- expand each into the real subtopics a {domain} professor would teach.
2. Generate exactly 5-6 SPECIFIC topics. Each topic is something you could deliver a full 2-hour lecture on.
3. Every topic MUST have: a 2-3 sentence description, 3-4 subtopics, 2-3 key concepts, and 1-2 practical examples.
4. Topic names must be SPECIFIC (e.g., "Gradient descent optimization and convergence analysis"), never generic (e.g., "Introduction to optimization").
5. FORBIDDEN in topic names: "concepts", "fundamentals", "basics", "introduction to", "overview", "essentials".
6. No two topics may start with the same word.

Respond with JSON:
{{
  "unit_number": {unit_number},
  "title": "[Descriptive unit title -- 5-10 words]",
  "topics": [
    {{
      "topic": "[Specific topic name -- 5-12 words]",
      "description": "[2-3 sentences explaining what this covers and why it matters]",
      "subtopics": ["[specific subtopic 1]", "[specific subtopic 2]", "[specific subtopic 3]"],
      "key_concepts": ["[concept 1]", "[concept 2]"],
      "practical_examples": ["[real-world application or exercise]"]
    }}
  ],
  "hours": {hours_per_unit}
}}

Generate 5-6 richly detailed topics. Every field is REQUIRED -- do not skip descriptions or subtopics."""

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
            "single_unit": cls.get_single_unit_prompt,
            "references": cls.get_references_prompt,
        }
        
        method = prompt_methods.get(section.lower())
        if not method:
            raise ValueError(f"Unknown section: {section}")
        
        user_prompt = method(context)
        strictness = cls.get_strictness(section.lower().replace("learning_outcomes", "outcomes"))
        
        return cls.MASTER_SYSTEM_PROMPT, user_prompt, strictness
