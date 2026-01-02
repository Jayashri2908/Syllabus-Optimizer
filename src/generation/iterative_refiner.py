"""
Iterative Refinement System
Multi-pass generation with critique and improvement for highest quality outputs
"""

from typing import Dict, List, Any, Optional
import logging


class IterativeRefiner:
    """Refine generated content through critique and regeneration"""
    
    def __init__(self, granite_client):
        self.granite = granite_client
        self.logger = logging.getLogger(__name__)
    
    def refine_learning_outcomes(
        self,
        initial_outcomes: List[Dict[str, str]],
        course_title: str,
        keywords: List[str],
        program_outcomes: List[str],
        num_outcomes: int
    ) -> List[Dict[str, str]]:
        """
        Refine learning outcomes through critique and regeneration
        
        Args:
            initial_outcomes: Initially generated outcomes
            course_title: Course title
            keywords: Course keywords
            program_outcomes: Program outcomes
            num_outcomes: Target number of outcomes
            
        Returns:
            Refined outcomes
        """
        if len(initial_outcomes) < num_outcomes:
            self.logger.warning(f"Only {len(initial_outcomes)} outcomes generated, expected {num_outcomes}")
            return initial_outcomes
        
        # Format initial outcomes for critique
        outcomes_text = "\n".join([
            f"{i+1}. [{o['bloom_level']}] {o['description']}"
            for i, o in enumerate(initial_outcomes)
        ])
        
        # Critique phase
        critique_prompt = f"""Review these learning outcomes for a {course_title} course:

{outcomes_text}

Evaluate each outcome for:
1. **Measurability**: Can student achievement be assessed?
2. **Specificity**: Is it clear what students will do?
3. **Bloom's Verb**: Does it start with an appropriate action verb?
4. **Relevance**: Is it relevant to the course topics: {', '.join(keywords)}?
5. **Alignment**: Does it align with program outcomes: {', '.join(program_outcomes[:3])}?

For each outcome, provide:
- What works well
- What could be improved
- Suggested revision (if needed)

Format as:
Outcome 1: [feedback]
Outcome 2: [feedback]
..."""

        critique = self.granite.generate(
            critique_prompt,
            system_prompt="You are an expert curriculum reviewer specializing in learning outcome assessment.",
            temperature=0.3,
            max_tokens=800
        )
        
        self.logger.info("Generated critique for learning outcomes")
        
        # Refinement phase
        refinement_prompt = f"""Based on this critique, generate improved versions of the learning outcomes:

ORIGINAL OUTCOMES:
{outcomes_text}

EXPERT CRITIQUE:
{critique}

Generate {num_outcomes} IMPROVED learning outcomes that address the critique.
Maintain Bloom's taxonomy distribution and ensure each outcome is:
- Measurable and specific
- Starts with a clear Bloom's verb
- Addresses feedback from the critique

Format as numbered list."""

        refined_response = self.granite.generate(
            refinement_prompt,
            system_prompt="You are an expert in crafting perfect learning outcomes based on feedback.",
            temperature=0.4,
            max_tokens=600
        )
        
        self.logger.info("Generated refined learning outcomes")
        
        # Parse refined outcomes (similar to original parsing)
        refined_outcomes = []
        for i, line in enumerate(refined_response.split('\n'), 1):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                outcome_text = line.lstrip('0123456789.-•) ').strip()
                if outcome_text:
                    # Try to preserve Bloom's level from original or detect new one
                    bloom_level = initial_outcomes[i-1]['bloom_level'] if i-1 < len(initial_outcomes) else 'Apply'
                    
                    refined_outcomes.append({
                        'code': f'CO{i}',
                        'description': outcome_text,
                        'bloom_level': bloom_level,
                        'refined': True
                    })
                    
                if len(refined_outcomes) >= num_outcomes:
                    break
        
        # Return refined if we got enough, otherwise original
        if len(refined_outcomes) >= num_outcomes:
            self.logger.info(f"Successfully refined {len(refined_outcomes)} outcomes")
            return refined_outcomes[:num_outcomes]
        else:
            self.logger.warning("Refinement produced fewer outcomes, returning original")
            return initial_outcomes
    
    def refine_objectives(
        self,
        initial_objectives: List[str],
        course_title: str,
        keywords: List[str]
    ) -> List[str]:
        """Refine course objectives through critique"""
        
        objectives_text = "\n".join([f"{i+1}. {obj}" for i, obj in enumerate(initial_objectives)])
        
        critique_prompt = f"""Review these course objectives for {course_title}:

{objectives_text}

Evaluate for:
- SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
- Clarity and actionability
- Alignment with course topics: {', '.join(keywords)}

Provide brief feedback for each objective and suggest improvements."""

        critique = self.granite.generate(
            critique_prompt,
            system_prompt="You are a curriculum design expert.",
            temperature=0.3,
            max_tokens=500
        )
        
        refinement_prompt = f"""Based on this critique, generate improved objectives:

ORIGINAL:
{objectives_text}

CRITIQUE:
{critique}

Generate improved versions addressing the feedback. Maintain 4-6 objectives."""

        refined_response = self.granite.generate(
            refinement_prompt,
            temperature=0.5,
            max_tokens=400
        )
        
        # Parse refined objectives
        refined_objectives = []
        for line in refined_response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                obj = line.lstrip('0123456789.-•) ').strip()
                if obj and len(obj) > 15:
                    refined_objectives.append(obj)
        
        return refined_objectives[:6] if refined_objectives else initial_objectives
    
    def validate_and_refine_units(
        self,
        initial_units: List[Dict[str, Any]],
        course_title: str,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Validate units for completeness and logical progression"""
        
        # Check for issues
        issues = []
        for i, unit in enumerate(initial_units):
            if len(unit.get('topics', [])) < 3:
                issues.append(f"Unit {i+1} has too few topics ({len(unit.get('topics', []))})")
            if not unit.get('title') or len(unit.get('title', '')) < 10:
                issues.append(f"Unit {i+1} has vague/short title")
        
        if not issues:
            self.logger.info("Units passed validation, no refinement needed")
            return initial_units
        
        self.logger.info(f"Found {len(issues)} issues with units, refining...")
        
        # Unit-specific refinement
        units_text = "\n\n".join([
            f"Unit {u['unit_number']}: {u['title']}\nTopics: {', '.join(u['topics'])}"
            for u in initial_units
        ])
        
        refinement_prompt = f"""Improve these units for {course_title}:

{units_text}

Issues identified:
{chr(10).join(f'- {issue}' for issue in issues)}

Generate improved units with:
- Descriptive titles (>15 characters)
- 4-6 specific topics per unit
- Logical progression from basic to advanced

Maintain format:
Unit 1: [Title]
Topics: topic1, topic2, ..."""

        refined_response = self.granite.generate(
            refinement_prompt,
            system_prompt="You are a curriculum design expert.",
            temperature=0.6,
            max_tokens=1500
        )
        
        # For simplicity, return original if refinement parsing is complex
        # In production, would parse the refined response
        return initial_units
