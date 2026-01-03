"""
Course Objectives Optimizer for SCDO
Optimizes course objectives using SMART criteria
"""

from typing import Dict, List, Any
import logging
from pathlib import Path

try:
    from ..ibm.granite_client import GraniteClient
    GRANITE_AVAILABLE = True
except ImportError:
    GRANITE_AVAILABLE = False


class ObjectivesOptimizer:
    """Optimize course objectives using SMART criteria"""
    
    def __init__(self, granite_client=None):
        self.logger = logging.getLogger(__name__)
        
        if GRANITE_AVAILABLE:
            self.granite = granite_client or GraniteClient()
            self.enabled = True
        else:
            self.logger.warning("Granite client not available. Using rule-based optimization.")
            self.enabled = False
            
        # SMART criteria
        self.smart_criteria = {
            'specific': 'Clear and well-defined',
            'measurable': 'Can be quantified or verified',
            'achievable': 'Realistic and attainable',
            'relevant': 'Aligns with course and program goals',
            'time_bound': 'Has a clear timeline or duration'
        }
        
    def optimize_objectives(
        self, 
        objectives: List[str],
        course_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize course objectives using SMART criteria
        
        Args:
            objectives: List of course objectives
            course_info: Course context (title, level, domain, credits)
            
        Returns:
            Optimization results with enhanced objectives
        """
        if not objectives:
            return {
                'status': 'no_objectives',
                'message': 'No objectives provided',
                'optimized_objectives': []
            }
            
        optimized = []
        
        for idx, objective in enumerate(objectives):
            if self.enabled:
                # Use AI for optimization
                enhanced = self._optimize_with_ai(objective, course_info)
            else:
                # Use rule-based optimization
                enhanced = self._optimize_rule_based(objective, course_info)
                
            optimized.append({
                'original': objective,
                'optimized': enhanced['text'],
                'improvements': enhanced['improvements'],
                'smart_score': enhanced['smart_score']
            })
            
        return {
            'status': 'success',
            'total_objectives': len(objectives),
            'optimized_objectives': optimized,
            'overall_smart_score': sum(o['smart_score'] for o in optimized) / len(optimized) if optimized else 0
        }
        
    def _optimize_with_ai(
        self, 
        objective: str,
        course_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize objective using AI"""
        course_title = course_info.get('course_title', 'this course')
        course_level = course_info.get('course_level', 'undergraduate')
        domain = course_info.get('domain', 'engineering')
        
        system_prompt = f"""You are an expert curriculum designer specializing in {domain} education.
Your task is to enhance course objectives using SMART criteria:
- Specific: Clear and well-defined
- Measurable: Quantifiable or verifiable
- Achievable: Realistic for {course_level} level
- Relevant: Aligned with course goals
- Time-bound: Consider course duration

Provide the enhanced objective and explain what improvements were made."""

        prompt = f"""Course: {course_title}
Level: {course_level}
Domain: {domain}

Current Objective:
"{objective}"

Enhance this objective to be more SMART (Specific, Measurable, Achievable, Relevant, Time-bound).
Provide:
1. Enhanced objective
2. List of improvements made
3. SMART score (0-100)

Format:
ENHANCED: [enhanced objective text]
IMPROVEMENTS: [bullet list of improvements]
SCORE: [0-100]"""

        try:
            response = self.granite.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse response
            enhanced_text = objective  # Default to original
            improvements = []
            smart_score = 50  # Default score
            
            if 'ENHANCED:' in response:
                enhanced_text = response.split('ENHANCED:')[1].split('IMPROVEMENTS:')[0].strip()
            if 'IMPROVEMENTS:' in response:
                imp_text = response.split('IMPROVEMENTS:')[1].split('SCORE:')[0].strip()
                improvements = [line.strip('- ') for line in imp_text.split('\n') if line.strip()]
            if 'SCORE:' in response:
                try:
                    smart_score = int(response.split('SCORE:')[1].strip().split()[0])
                except:
                    pass
                    
            return {
                'text': enhanced_text,
                'improvements': improvements,
                'smart_score': smart_score
            }
            
        except Exception as e:
            self.logger.error(f"AI optimization failed: {e}")
            return self._optimize_rule_based(objective, course_info)
            
    def _optimize_rule_based(
        self,
        objective: str,
        course_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Rule-based optimization fallback"""
        improvements = []
        enhanced = objective
        score = 60  # Base score
        
        # Check for vague terms and suggest improvements
        vague_terms = ['understand', 'know', 'learn', 'appreciate']
        for term in vague_terms:
            if term.lower() in objective.lower():
                improvements.append(f"Replace '{term}' with more specific action verbs")
                score -= 5
                
        # Check for measurability
        measurable_keywords = ['demonstrate', 'apply', 'analyze', 'design', 'develop', 'evaluate']
        if not any(keyword in objective.lower() for keyword in measurable_keywords):
            improvements.append("Add measurable action verbs (e.g., demonstrate, apply, analyze)")
            score -= 10
        else:
            score += 10
            
        # Check for specificity
        if len(objective.split()) < 10:
            improvements.append("Add more specific details about what students will achieve")
            score -= 5
        else:
            score += 5
            
        # Check for time reference
        time_keywords = ['by end of course', 'during', 'throughout', 'semester']
        if any(keyword in objective.lower() for keyword in time_keywords):
            score += 10
        else:
            improvements.append("Consider adding time-bound element")
            
        if not improvements:
            improvements.append("Objective meets basic SMART criteria")
            enhanced = objective
        else:
            enhanced = f"{objective} (needs enhancement - see improvements)"
            
        return {
            'text': enhanced,
            'improvements': improvements,
            'smart_score': max(0, min(100, score))
        }
