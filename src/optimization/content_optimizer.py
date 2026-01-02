"""
Content Optimizer for SCDO
Uses IBM Granite to optimize syllabus content
"""

from typing import Dict, List, Any, Optional
import logging

from ..ibm.granite_client import GraniteClient


class ContentOptimizer:
    """Optimize syllabus content using AI"""
    
    def __init__(self, granite_client: Optional[GraniteClient] = None):
        self.logger = logging.getLogger(__name__)
        self.granite = granite_client or GraniteClient()
        
    def optimize_learning_outcomes(
        self,
        outcomes: List[str],
        context: str = ""
    ) -> List[Dict[str, str]]:
        """
        Optimize learning outcomes for clarity and measurability
        
        Args:
            outcomes: List of learning outcomes
            context: Course context
            
        Returns:
            List of optimized outcomes with explanations
        """
        system_prompt = """You are an expert in writing measurable learning outcomes.
Improve the given outcomes to be:
- Clear and specific
- Measurable and observable
- Using appropriate Bloom's taxonomy verbs
- Aligned with outcome-based education principles

For each outcome, provide the improved version and a brief explanation of changes."""

        outcomes_text = "\n".join([f"{i+1}. {o}" for i, o in enumerate(outcomes)])
        
        prompt = f"""Course Context: {context}

Current Learning Outcomes:
{outcomes_text}

Provide optimized versions of these outcomes."""

        response = self.granite.generate(prompt, system_prompt=system_prompt)
        
        # Parse response (simplified - would need better parsing)
        return [{'original': o, 'optimized': response} for o in outcomes]
        
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

        response = self.granite.generate(prompt, system_prompt=system_prompt)
        
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
        system_prompt = f"""You are an expert in {domain} education and industry trends.
Suggest modern, relevant topics that should be included in the course
based on current industry needs and academic developments."""

        topics_text = "\n".join([f"- {t}" for t in current_topics])
        
        prompt = f"""Course: {course_title}

Current Topics:
{topics_text}

Suggest 5-10 modern topics or technologies that should be added or emphasized."""

        response = self.granite.generate(prompt, system_prompt=system_prompt)
        
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

        response = self.granite.generate(prompt, system_prompt=system_prompt)
        
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

        response = self.granite.generate(prompt, system_prompt=system_prompt)
        
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

        response = self.granite.generate(prompt, system_prompt=system_prompt)
        
        return [{'analysis': response}]
