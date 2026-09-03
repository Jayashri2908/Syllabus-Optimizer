"""
Iterative Refinement System
Multi-pass generation with critique and improvement for highest quality outputs
Uses structured JSON output with Pydantic validation for reliable parsing
"""

from typing import Dict, List, Any, Optional
import logging

from .section_schemas import LearningOutcomesSection, ObjectivesSection


class IterativeRefiner:
    """Refine generated content through critique and regeneration"""
    
    def __init__(self, ai_model):
        self.ai = ai_model
        self.logger = logging.getLogger(__name__)
    
    def refine_learning_outcomes(
        self,
        initial_outcomes: List[Dict[str, str]],
        course_title: str,
        keywords: List[str],
        program_outcomes: List[str],
        num_outcomes: int
    ) -> List[Dict[str, str]]:
        """Refine learning outcomes through critique and structured JSON regeneration"""
        if len(initial_outcomes) < num_outcomes:
            self.logger.warning(f"Only {len(initial_outcomes)} outcomes generated, expected {num_outcomes}")
            return initial_outcomes
        
        outcomes_text = "\n".join([
            f"{i+1}. [{o.get('bloom_level', 'unknown')}] {o.get('description', '')}"
            for i, o in enumerate(initial_outcomes)
        ])
        
        critique_prompt = f"""Review these learning outcomes for a {course_title} course:

{outcomes_text}

Evaluate each outcome for:
1. Measurability: Can student achievement be assessed?
2. Specificity: Is it clear what students will do?
3. Bloom's Verb: Does it start with an appropriate action verb?
4. Relevance: Is it relevant to the course topics: {', '.join(keywords)}?
5. Alignment: Does it align with program outcomes: {', '.join(program_outcomes[:3])}?

For each outcome, provide:
- What works well
- What could be improved
- Suggested revision (if needed)"""

        try:
            critique = self.ai.generate(
                prompt=critique_prompt,
                system_prompt="You are an expert curriculum reviewer specializing in learning outcome assessment.",
                task_type='analysis',
                temperature=0.3,
                max_tokens=800
            )
        except Exception as e:
            self.logger.warning(f"Critique generation failed: {e}. Returning original outcomes.")
            return initial_outcomes
        
        self.logger.info("Generated critique for learning outcomes")
        
        refinement_prompt = f"""Based on this critique, generate improved learning outcomes:

ORIGINAL OUTCOMES:
{outcomes_text}

EXPERT CRITIQUE:
{critique}

Generate {num_outcomes} IMPROVED learning outcomes that address the critique.
Ensure each outcome:
- Is measurable and specific
- Starts with a clear Bloom's taxonomy verb
- Addresses feedback from the critique
- Has an appropriate bloom_level

Respond with JSON:
{{
  "outcomes": [
    {{"code": "CO1", "description": "Improved outcome text", "bloom_level": "apply"}},
    {{"code": "CO2", "description": "Improved outcome text", "bloom_level": "analyze"}}
  ]
}}"""

        try:
            result = self.ai.generate_json(
                prompt=refinement_prompt,
                system_prompt="You are an expert in crafting perfect learning outcomes based on feedback.",
                schema=LearningOutcomesSection,
                task_type='generation',
                temperature=0.4,
                max_tokens=700,
                max_retries=1
            )
            
            refined = result.get('outcomes', [])
            if len(refined) >= num_outcomes:
                self.logger.info(f"Successfully refined {len(refined)} outcomes with JSON validation")
                return [
                    {
                        'code': o.get('code', f'CO{i+1}'),
                        'description': o.get('description', ''),
                        'bloom_level': o.get('bloom_level', 'apply'),
                        'refined': True
                    }
                    for i, o in enumerate(refined[:num_outcomes])
                ]
            else:
                self.logger.warning(f"Refinement produced {len(refined)} outcomes, expected {num_outcomes}")
                return initial_outcomes
                
        except Exception as e:
            self.logger.warning(f"JSON-based refinement failed: {e}. Returning original outcomes.")
            return initial_outcomes
    
    def refine_objectives(
        self,
        initial_objectives: List[str],
        course_title: str,
        keywords: List[str]
    ) -> List[str]:
        """Refine course objectives through critique with JSON output"""
        
        objectives_text = "\n".join([f"{i+1}. {obj}" for i, obj in enumerate(initial_objectives)])
        
        critique_prompt = f"""Review these course objectives for {course_title}:

{objectives_text}

Evaluate for:
- SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
- Clarity and actionability
- Alignment with course topics: {', '.join(keywords)}

Provide brief feedback for each objective and suggest improvements."""

        try:
            critique = self.ai.generate(
                prompt=critique_prompt,
                system_prompt="You are a curriculum design expert.",
                task_type='analysis',
                temperature=0.3,
                max_tokens=500
            )
        except Exception as e:
            self.logger.warning(f"Objectives critique failed: {e}. Returning originals.")
            return initial_objectives
        
        refinement_prompt = f"""Based on this critique, generate improved objectives:

ORIGINAL:
{objectives_text}

CRITIQUE:
{critique}

Generate 5-6 improved objectives addressing the feedback.

Respond with JSON:
{{
  "objectives": [
    {{"text": "First improved objective"}},
    {{"text": "Second improved objective"}},
    {{"text": "Third improved objective"}}
  ]
}}"""

        try:
            result = self.ai.generate_json(
                prompt=refinement_prompt,
                system_prompt="You are a curriculum design expert.",
                schema=ObjectivesSection,
                task_type='generation',
                temperature=0.5,
                max_tokens=500,
                max_retries=1
            )
            
            obj_list = result.get('objectives', [])
            refined = [
                o.get('text', '') if isinstance(o, dict) else str(o)
                for o in obj_list
            ]
            refined = [o for o in refined if len(o) > 15]
            
            if refined:
                self.logger.info(f"Successfully refined {len(refined)} objectives with JSON validation")
                return refined[:6]
            else:
                self.logger.warning("JSON refinement produced no valid objectives")
                return initial_objectives
                
        except Exception as e:
            self.logger.warning(f"JSON-based objectives refinement failed: {e}. Returning originals.")
            return initial_objectives
    
    def validate_and_refine_units(
        self,
        initial_units: List[Dict[str, Any]],
        course_title: str,
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Validate units for completeness and logical progression"""
        
        issues = []
        for i, unit in enumerate(initial_units):
            if len(unit.get('topics', [])) < 3:
                issues.append(f"Unit {i+1} has too few topics ({len(unit.get('topics', []))})")
            if not unit.get('title') or len(unit.get('title', '')) < 10:
                issues.append(f"Unit {i+1} has vague/short title")
        
        if not issues:
            self.logger.info("Units passed validation, no refinement needed")
            return initial_units
        
        self.logger.info(f"Found {len(issues)} issues with units, but unit refinement parsing is complex. Returning originals with logged issues.")
        for issue in issues:
            self.logger.warning(f"Unit issue: {issue}")
        
        return initial_units
