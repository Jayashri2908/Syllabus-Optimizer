"""
Outcome Extractor for SCDO
Extracts and validates learning outcomes from course descriptions
"""

from typing import List, Dict, Any
import re
import logging

from ..utils.text_processing import TextProcessor


class OutcomeExtractor:
    """Extract and validate learning outcomes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        
    def extract_outcomes(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract learning outcomes from text
        
        Args:
            text: Course description or objectives text
            
        Returns:
            List of extracted outcomes with metadata
        """
        outcomes = []
        
        # Extract using text processor
        raw_outcomes = self.text_processor.extract_learning_outcomes(text)
        
        for idx, outcome_text in enumerate(raw_outcomes, 1):
            outcome = self._process_outcome(outcome_text, idx)
            outcomes.append(outcome)
            
        return outcomes
        
    def _process_outcome(self, text: str, index: int) -> Dict[str, Any]:
        """Process individual outcome"""
        # Classify Bloom's level
        bloom_level = self.text_processor.classify_bloom_level(text)
        
        # Check measurability
        measurability_score = self._assess_measurability(text)
        
        # Extract action verb
        action_verb = self._extract_action_verb(text)
        
        return {
            'code': f'CO{index}',
            'description': text,
            'bloom_level': bloom_level,
            'action_verb': action_verb,
            'measurability_score': measurability_score,
            'is_well_formed': measurability_score >= 0.7
        }
        
    def _assess_measurability(self, text: str) -> float:
        """
        Assess how measurable an outcome is (0-1 scale)
        
        Well-formed outcomes should:
        - Start with an action verb
        - Be specific and clear
        - Be measurable
        """
        score = 0.0
        
        # Check for action verb at start
        if self._has_action_verb(text):
            score += 0.4
            
        # Check for specificity (not too vague)
        vague_words = ['understand', 'know', 'learn', 'appreciate', 'be aware']
        if not any(word in text.lower() for word in vague_words):
            score += 0.3
        else:
            score += 0.1  # Partial credit
            
        # Check for measurable criteria
        measurable_indicators = ['calculate', 'design', 'implement', 'analyze', 
                                'evaluate', 'create', 'solve', 'demonstrate']
        if any(word in text.lower() for word in measurable_indicators):
            score += 0.3
            
        return min(score, 1.0)
        
    def _has_action_verb(self, text: str) -> bool:
        """Check if text starts with an action verb"""
        # Get first word
        words = text.strip().split()
        if not words:
            return False
            
        first_word = words[0].lower().rstrip('.,;:')
        
        # Check against Bloom's verbs
        for level_verbs in self.text_processor.bloom_verbs.values():
            if first_word in level_verbs:
                return True
                
        return False
        
    def _extract_action_verb(self, text: str) -> str:
        """Extract the action verb from outcome"""
        words = text.strip().split()
        if not words:
            return ""
            
        first_word = words[0].lower().rstrip('.,;:')
        
        # Check if it's a Bloom's verb
        for level_verbs in self.text_processor.bloom_verbs.values():
            if first_word in level_verbs:
                return first_word
                
        return ""
        
    def generate_outcomes(
        self,
        course_description: str,
        num_outcomes: int = 5,
        bloom_distribution: Dict[str, int] = None
    ) -> List[str]:
        """
        Generate learning outcomes from course description
        
        Args:
            course_description: Course description text
            num_outcomes: Number of outcomes to generate
            bloom_distribution: Desired distribution across Bloom's levels
            
        Returns:
            List of generated outcome templates
        """
        if bloom_distribution is None:
            # Default distribution
            bloom_distribution = {
                'understand': 1,
                'apply': 2,
                'analyze': 1,
                'evaluate': 1
            }
            
        # Extract keywords from description
        keywords = self.text_processor.extract_keywords(course_description, top_n=10)
        
        outcomes = []
        outcome_idx = 1
        
        for level, count in bloom_distribution.items():
            for _ in range(count):
                if outcome_idx > num_outcomes:
                    break
                    
                # Get appropriate verb for level
                verbs = list(self.text_processor.bloom_verbs.get(level, []))
                if verbs:
                    verb = verbs[0].capitalize()  # Use first verb
                    
                    # Create outcome template
                    if keywords:
                        keyword = keywords[(outcome_idx - 1) % len(keywords)]
                        outcome = f"{verb} {keyword} concepts and applications"
                    else:
                        outcome = f"{verb} course concepts effectively"
                        
                    outcomes.append(outcome)
                    outcome_idx += 1
                    
        return outcomes
        
    def validate_outcome(self, outcome: str) -> Dict[str, Any]:
        """
        Validate a learning outcome
        
        Args:
            outcome: Learning outcome text
            
        Returns:
            Validation report
        """
        issues = []
        suggestions = []
        
        # Check for action verb
        if not self._has_action_verb(outcome):
            issues.append("Does not start with a clear action verb")
            suggestions.append("Begin with a Bloom's taxonomy verb (e.g., analyze, design, evaluate)")
            
        # Check for vague language
        vague_words = ['understand', 'know', 'learn', 'appreciate', 'be aware of']
        for word in vague_words:
            if word in outcome.lower():
                issues.append(f"Contains vague term: '{word}'")
                suggestions.append(f"Replace '{word}' with more specific, measurable verbs")
                
        # Check length
        word_count = len(outcome.split())
        if word_count < 5:
            issues.append("Outcome is too brief")
            suggestions.append("Provide more specific details about what students will achieve")
        elif word_count > 30:
            issues.append("Outcome is too lengthy")
            suggestions.append("Break into multiple outcomes or simplify")
            
        # Get measurability score
        measurability = self._assess_measurability(outcome)
        
        return {
            'is_valid': len(issues) == 0,
            'measurability_score': measurability,
            'issues': issues,
            'suggestions': suggestions,
            'bloom_level': self.text_processor.classify_bloom_level(outcome)
        }
