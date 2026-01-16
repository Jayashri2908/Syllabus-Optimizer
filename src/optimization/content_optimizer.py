"""
Content Optimizer for SCDO
Uses AI (Gemini/Granite) to provide actionable optimization suggestions
"""

from typing import Dict, List, Any, Optional
import logging

from ..ai.model_manager import ModelManager


class ContentOptimizer:
    """Optimize syllabus content using AI with actionable recommendations"""
    
    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.logger = logging.getLogger(__name__)
        self.ai = model_manager or ModelManager()
        
    def optimize_learning_outcomes(
        self,
        outcomes: List[str],
        context: str = ""
    ) -> List[Dict[str, str]]:
        """
        Optimize learning outcomes with specific, actionable improvements
        
        Args:
            outcomes: List of learning outcomes
            context: Course context
            
        Returns:
            Detailed analysis with specific improvements for each outcome
        """
        system_prompt = """You are a world-class learning outcomes expert with 20+ years experience in curriculum design and accreditation.

CRITICAL: For EACH outcome, provide:
1. **Current Issues**: Specific problems (be direct and critical)
2. **Improved Version**: Complete rewrite that fixes ALL issues
3. **Bloom's Level**: Correct taxonomy level
4. **Why Better**: 2-3 specific improvements made

QUALITY STANDARDS:
✓ Starts with precise Bloom's verb
✓ Includes measurable criteria
✓ Specifies WHAT students will do
✓ Includes HOW they'll demonstrate (when possible)
✓ Uses industry-standard terminology
✓ Specific, not generic

EXCELLENT OUTCOME EXAMPLE:
"Design and implement a RESTful API using Node.js and Express that performs CRUD operations with proper HTTP status codes (200, 201, 400, 404, 500), error handling, and JSON responses, deployable on cloud platforms"

[Bloom's: Create | Measurable: Can test API | Specific: Technologies and criteria listed]

POOR OUTCOME EXAMPLE:
"Understand web APIs"
[Too vague | No verb | Not measurable | No context]"""

        outcomes_text = "\n".join([f"{i+1}. {o}" for i, o in enumerate(outcomes)])
        
        prompt = f"""Course Context: {context if context else 'Not provided'}

ANALYZE THESE LEARNING OUTCOMES:
{outcomes_text}

For EACH outcome (1-{len(outcomes)}), provide:

**Outcome {'{N}'}:**
**Issues:** [Specific problems - be critical]
**Improved:** [Complete rewrite fixing all issues]
**Bloom's:** [{'{level}'}]
**Why Better:** [2-3 specific improvements]

Be thorough and specific. Every outcome should be dramatically improved."""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type='optimization',
            temperature=0.4,
            max_tokens=1500
        )
        
        return [{'analysis': response, 'count': len(outcomes)}]
        
    def optimize_unit_sequence(
        self,
        units: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimize unit sequencing for better learning progression
        
        Args:
            units: List of units with topics
            
        Returns:
            Optimized sequence with rationale
        """
        system_prompt = """You are a curriculum design expert.
Analyze the unit sequence and suggest optimal ordering based on:
- Prerequisite knowledge
- Cognitive complexity progression
- Logical topic flow
- Learning scaffolding principles"""

        units_text = "\n".join([
            f"Unit {u.get('unit_number', i+1)}: {u.get('title', 'Untitled')}\n"
            f"Topics: {', '.join(u.get('topics', []))}"
            for i, u in enumerate(units)
        ])
        
        prompt = f"""Current Unit Sequence:
{units_text}

Suggest optimal sequencing and explain the rationale."""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type='optimization',
            temperature=0.5,
            max_tokens=1000
        )
        
        return {
            'current_sequence': units,
            'optimization_suggestions': response
        }
        
    def suggest_modern_content(
        self,
        course_title: str,
        current_topics: List[str],
        domain: str = "engineering"
    ) -> List[str]:
        """
        Suggest modern/trending topics to include
        
        Args:
            course_title: Course title
            current_topics: Current topics covered
            domain: Academic domain
            
        Returns:
            List of suggested topics
        """
        system_prompt = f"""You are a {domain} industry expert and educator tracking latest trends.

CRITICAL: Suggest ONLY topics that are:
✓ Currently trending in industry (2024-2026)
✓ Highly demanded in job markets
✓ Practical and immediately applicable
✓ NOT already covered in current topics

For EACH suggestion, provide:
1. **Topic**: Specific technology/concept
2. **Why Important**: Industry demand/trend
3. **How to Integrate**: Where in curriculum
4. **Resources**: 1-2 learning resources"""

        topics_text = "\n".join([f"- {t}" for t in current_topics])
        
        prompt = f"""Course: {course_title}

Current Topics:
{topics_text}

Suggest 5-7 HIGH-PRIORITY modern topics that are:
- Trending in {domain} industry RIGHT NOW
- Missing from current curriculum
- Valued by employers

For each:
**Topic:** [specific name]
**Why:** [industry demand]
**Where:** [which unit to add]
**Learn:** [one resource]"""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type='optimization',
            temperature=0.6,
            max_tokens=1200
        )
        
        # Parse suggestions (simplified)
        suggestions = [line.strip('- ') for line in response.split('\n') 
                      if line.strip().startswith('-')]
        
        return suggestions[:10]
        
    def balance_workload(
        self,
        units: List[Dict[str, Any]],
        total_hours: int
    ) -> Dict[str, Any]:
        """
        Suggest balanced hour distribution across units
        
        Args:
            units: List of units
            total_hours: Total contact hours available
            
        Returns:
            Balanced distribution with rationale
        """
        system_prompt = """You are a curriculum planning expert.
Suggest optimal hour distribution across units based on:
- Topic complexity
- Number of subtopics
- Prerequisite requirements
- Practical vs theoretical content"""

        units_text = "\n".join([
            f"Unit {u.get('unit_number', i+1)}: {u.get('title', 'Untitled')}\n"
            f"Topics: {len(u.get('topics', []))} topics\n"
            f"Current hours: {u.get('hours', 0)}"
            for i, u in enumerate(units)
        ])
        
        prompt = f"""Total Available Hours: {total_hours}

Units:
{units_text}

Suggest optimal hour distribution."""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type='optimization',
            temperature=0.4,
            max_tokens=800
        )
        
        return {
            'total_hours': total_hours,
            'suggestions': response
        }
        
    def enhance_assessment_strategy(
        self,
        current_assessment: Dict[str, int],
        learning_outcomes: List[str]
    ) -> Dict[str, Any]:
        """
        Suggest improved assessment strategy
        
        Args:
            current_assessment: Current assessment pattern
            learning_outcomes: Course learning outcomes
            
        Returns:
            Enhanced assessment strategy
        """
        system_prompt = """You are an assessment design expert.
Suggest an improved assessment strategy that:
- Aligns with learning outcomes
- Covers multiple Bloom's levels
- Balances formative and summative assessment
- Includes diverse assessment methods"""

        assessment_text = "\n".join([f"{k}: {v}%" for k, v in current_assessment.items()])
        outcomes_text = "\n".join([f"- {o}" for o in learning_outcomes])
        
        prompt = f"""Current Assessment:
{assessment_text}

Learning Outcomes:
{outcomes_text}

Suggest an enhanced assessment strategy."""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type='optimization',
            temperature=0.5,
            max_tokens=1000
        )
        
        return {
            'current': current_assessment,
            'suggestions': response
        }
        
    def identify_redundancies(
        self,
        syllabus_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Identify redundant or overlapping content
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            List of identified redundancies
        """
        units = syllabus_data.get('units', [])
        
        # Extract all topics
        all_topics = []
        for unit in units:
            for topic in unit.get('topics', []):
                all_topics.append({
                    'unit': unit.get('unit_number', ''),
                    'topic': topic
                })
                
        system_prompt = """You are a curriculum analysis expert.
Identify redundant or overlapping topics that could be:
- Consolidated
- Removed
- Better distributed"""

        topics_text = "\n".join([
            f"Unit {t['unit']}: {t['topic']}" for t in all_topics
        ])
        
        prompt = f"""Topics across all units:
{topics_text}

Identify any redundancies or overlaps."""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type='analysis',
            temperature=0.3,
            max_tokens=1000
        )
        
        return [{'analysis': response}]
