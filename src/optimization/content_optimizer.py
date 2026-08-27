"""
Content Optimizer for SCDO
Uses AI (OpenRouter/Gemini) to provide actionable optimization suggestions
"""

from typing import Dict, List, Any, Optional
import logging
import json

from ..ai.model_manager import ModelManager


class ContentOptimizer:
    """Optimize syllabus content using AI with actionable recommendations"""
    
    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.logger = logging.getLogger(__name__)
        self.ai = model_manager or ModelManager()
        
    def optimize_full_syllabus(
        self,
        syllabus_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform a COMPLETE optimization of the syllabus using a unified prompt.
        """
        system_prompt = """You are an expert curriculum designer and educational consultant with 20+ years of experience in higher education syllabus development, accreditation compliance, and learning outcome optimization.

YOUR TASK: Perform a COMPLETE optimization of the provided syllabus. You have FULL AUTHORITY to:
1. Rewrite all learning outcomes using proper Bloom's taxonomy verbs. 
2. Rearrange and restructure units for optimal learning progression (ensure prerequisite topics come first).
3. Add modern, industry-relevant topics (2024-2026 trends).
4. Remove redundant content and consolidate overlapping topics.
5. Balance workload across units (redistribute hours if needed).
6. Enhance assessment alignment with outcomes.
7. Recommend updated textbooks and reference materials (prioritize 2020-2026 editions, include at least one free/open resource if available).

CONSTRAINTS (MUST FOLLOW):
- Retain the core subject matter and course objectives.
- Maintain academic rigor appropriate for the course level.
- Ensure all changes are pedagogically sound.
- TOTAL HOURS: You MUST keep the TOTAL sum of hours constant, but you are encouraged to rebalance hours among individual units for optimal coverage.
- If the original syllabus has 5 units, try to maintain 5 units unless consolidation significantly improves the course.
- For textbooks/references, prioritize widely-adopted, industry-recognized books. Retain classics but add modern alternatives.

OUTPUT REQUIREMENTS:
You MUST return a valid JSON object with this EXACT structure:
{
  "optimized_syllabus": {
    "course_title": "...",
    "course_code": "...",
    "credits": "...",
    "objectives": ["..."],
    "learning_outcomes": [
      {"code": "CO1", "description": "...", "bloom_level": "Apply"}
    ],
    "units": [
      {
        "unit_number": 1,
        "title": "...",
        "hours": 8,
        "btl_levels": [1, 2],
        "mapped_cos": ["CO1", "CO2"],
        "topics": [
          {"name": "Topic name", "co": "CO1", "btl": 2},
          {"name": "Topic name", "co": "CO2", "btl": 1}
        ]
      }
    ],
    "assessment": {},
    "textbooks": ["Author - Title, Edition, Publisher, Year"],
    "references": ["Author - Title, Edition, Publisher, Year"]
  },
  "changes_summary": [
    {"aspect": "Units", "original": "4", "optimized": "5", "impact": "Better progression"},
    {"aspect": "Balance", "original": "High theory", "optimized": "Apply-focused", "impact": "Industry readiness"}
  ],
  "industry_relevance_score": 85,
  "modern_topics_added": ["Topic 1", "Topic 2"],
  "prerequisite_rationale": "Explanation of unit sequencing logic",
  "bloom_distribution": {
    "remember": 0, "understand": 0, "apply": 0, "analyze": 0, "evaluate": 0, "create": 0
  },
  "rationale": "Brief explanation of major optimization decisions"
}

CRITICAL: Return ONLY the JSON object. No markdown, no code blocks, no explanations outside the JSON."""

        prompt = f"""EXISTING SYLLABUS DATA:
{json.dumps(syllabus_data, indent=2)}

Please perform the complete optimization and return the structured JSON as requested."""

        # Use optimal parameters for Nemotron as requested
        try:
            response = self.ai.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                task_type='optimization',
                temperature=0.3,
                max_tokens=4096,
                top_p=0.85,
                top_k=40,
                frequency_penalty=0.2,
                presence_penalty=0.1,
                repetition_penalty=1.15
            )
            
            # Validate response structure
            if not response or 'optimized_syllabus' not in response:
                self.logger.error("LLM returned invalid or empty response")
                raise ValueError("Optimization failed: AI model returned an invalid response. Please try again.")
            
            # Post-optimization validation
            self._validate_optimization(syllabus_data, response)
            
            return response
        except Exception as e:
            self.logger.error(f"Unified optimization failed: {e}")
            raise ValueError(f"Optimization failed: {str(e)}")

    def _validate_optimization(self, original: Dict[str, Any], optimized: Dict[str, Any]):
        """Validate teaching hours and maintain unit integrity"""
        try:
            opt_syll = optimized.get('optimized_syllabus', {})
            
            # 1. Validate hours
            orig_units = original.get('units', [])
            opt_units = opt_syll.get('units', [])
            
            orig_total_hours = sum(int(u.get('hours', 0) or 0) for u in orig_units)
            opt_total_hours = sum(int(u.get('hours', 0) or 0) for u in opt_units)
            
            if orig_total_hours > 0 and opt_total_hours != orig_total_hours:
                self.logger.warning(f"Hour mismatch: original total={orig_total_hours}, optimized total={opt_total_hours}. AI rebalancing might have changed total hours.")
                # We don't raise error, but we log it
            
            # 2. Validate unit count
            if len(opt_units) < len(orig_units) and len(opt_units) < 4:
                self.logger.warning(f"Unit count dropped significantly: {len(orig_units)} -> {len(opt_units)}")

            # 3. Log industry relevance
            try:
                score = int(optimized.get('industry_relevance_score', 0) or 0)
            except (ValueError, TypeError):
                score = 0
            self.logger.info(f"Industry Relevance Score for optimized syllabus: {score}/100")
            
        except Exception as e:
            self.logger.warning(f"Optimization validation failed (non-critical): {e}")

