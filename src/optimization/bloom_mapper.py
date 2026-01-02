"""
Bloom's Taxonomy Mapper for SCDO
Maps learning activities and outcomes to Bloom's cognitive levels
"""

from typing import Dict, List, Any, Tuple
import yaml
from pathlib import Path
import logging

from ..utils.text_processing import TextProcessor


class BloomMapper:
    """Map content to Bloom's taxonomy levels"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        self.taxonomy = self._load_taxonomy()
        
    def _load_taxonomy(self) -> dict:
        """Load Bloom's taxonomy configuration"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "bloom_taxonomy.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def map_outcome(self, outcome: str) -> Dict[str, Any]:
        """
        Map learning outcome to Bloom's level
        
        Args:
            outcome: Learning outcome text
            
        Returns:
            Mapping with level, confidence, and suggestions
        """
        level = self.text_processor.classify_bloom_level(outcome)
        
        # Get level details
        level_data = self.taxonomy['taxonomy'].get(level, {})
        
        # Calculate confidence based on verb presence
        confidence = self._calculate_confidence(outcome, level)
        
        # Get suggested assessment types
        assessment_types = level_data.get('assessment_types', [])
        
        return {
            'bloom_level': level,
            'level_number': level_data.get('level', 0),
            'confidence': confidence,
            'description': level_data.get('description', ''),
            'suggested_assessments': assessment_types,
            'action_verbs': level_data.get('verbs', [])
        }
        
    def _calculate_confidence(self, text: str, classified_level: str) -> float:
        """Calculate confidence in classification"""
        text_lower = text.lower()
        
        # Count matching verbs for the classified level
        level_verbs = self.taxonomy['taxonomy'].get(classified_level, {}).get('verbs', [])
        matches = sum(1 for verb in level_verbs if verb in text_lower)
        
        if matches == 0:
            return 0.3  # Low confidence
        elif matches == 1:
            return 0.7  # Medium confidence
        else:
            return 0.9  # High confidence
            
    def map_assessment_to_bloom(self, assessment_type: str) -> List[str]:
        """
        Map assessment type to appropriate Bloom's levels
        
        Args:
            assessment_type: Type of assessment (e.g., "quiz", "project")
            
        Returns:
            List of appropriate Bloom's levels
        """
        assessment_type_lower = assessment_type.lower()
        appropriate_levels = []
        
        for level, data in self.taxonomy['taxonomy'].items():
            assessment_types = [at.lower() for at in data.get('assessment_types', [])]
            
            # Check if assessment type matches
            if any(assessment_type_lower in at for at in assessment_types):
                appropriate_levels.append(level)
                
        return appropriate_levels
        
    def suggest_activities(self, bloom_level: str) -> List[str]:
        """
        Suggest learning activities for a Bloom's level
        
        Args:
            bloom_level: Bloom's taxonomy level
            
        Returns:
            List of suggested activities
        """
        level_data = self.taxonomy['taxonomy'].get(bloom_level, {})
        
        activities = []
        
        # Get assessment types as activity suggestions
        assessment_types = level_data.get('assessment_types', [])
        activities.extend(assessment_types)
        
        # Add level-specific suggestions
        level_activities = {
            'remember': [
                'Flashcard exercises',
                'Memorization drills',
                'Vocabulary lists',
                'Timeline creation'
            ],
            'understand': [
                'Concept mapping',
                'Summarization exercises',
                'Explanation videos',
                'Discussion forums'
            ],
            'apply': [
                'Problem sets',
                'Simulations',
                'Hands-on labs',
                'Real-world scenarios'
            ],
            'analyze': [
                'Case study analysis',
                'Data interpretation',
                'Comparative studies',
                'Critical reviews'
            ],
            'evaluate': [
                'Peer review sessions',
                'Critique assignments',
                'Decision-making scenarios',
                'Evaluation reports'
            ],
            'create': [
                'Design projects',
                'Research proposals',
                'Prototype development',
                'Creative portfolios'
            ]
        }
        
        activities.extend(level_activities.get(bloom_level, []))
        
        return activities
        
    def analyze_distribution(self, outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze Bloom's taxonomy distribution in outcomes
        
        Args:
            outcomes: List of learning outcomes with bloom_level
            
        Returns:
            Distribution analysis
        """
        # Count by level
        level_counts = {}
        for outcome in outcomes:
            level = outcome.get('bloom_level', 'unknown')
            level_counts[level] = level_counts.get(level, 0) + 1
            
        total = len(outcomes)
        
        # Calculate percentages
        percentages = {}
        if total > 0:
            percentages = {level: (count / total) * 100 
                          for level, count in level_counts.items()}
                          
        # Get recommended distribution
        recommended = self.taxonomy.get('recommended_distribution', {})
        
        # Compare with recommended
        comparison = {}
        for level in ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']:
            current = percentages.get(level, 0)
            rec_range = recommended.get(level, '0-0%')
            
            # Parse recommended range
            if isinstance(rec_range, str) and '-' in rec_range:
                min_val = int(rec_range.split('-')[0])
                max_val = int(rec_range.split('-')[1].rstrip('%'))
                
                status = 'optimal'
                if current < min_val:
                    status = 'below'
                elif current > max_val:
                    status = 'above'
                    
                comparison[level] = {
                    'current': current,
                    'recommended_min': min_val,
                    'recommended_max': max_val,
                    'status': status
                }
                
        return {
            'level_counts': level_counts,
            'percentages': percentages,
            'total_outcomes': total,
            'comparison': comparison,
            'is_balanced': all(c['status'] == 'optimal' for c in comparison.values())
        }
        
    def suggest_rebalancing(self, current_distribution: Dict[str, Any]) -> List[str]:
        """
        Suggest how to rebalance Bloom's distribution
        
        Args:
            current_distribution: Current distribution analysis
            
        Returns:
            List of suggestions
        """
        suggestions = []
        comparison = current_distribution.get('comparison', {})
        
        for level, data in comparison.items():
            status = data['status']
            current = data['current']
            
            if status == 'below':
                suggestions.append(
                    f"Add more '{level}' level outcomes (currently {current:.1f}%, "
                    f"recommended {data['recommended_min']}-{data['recommended_max']}%)"
                )
            elif status == 'above':
                suggestions.append(
                    f"Reduce '{level}' level outcomes (currently {current:.1f}%, "
                    f"recommended {data['recommended_min']}-{data['recommended_max']}%)"
                )
                
        return suggestions
        
    def map_verb_to_level(self, verb: str) -> Tuple[str, int]:
        """
        Map an action verb to Bloom's level
        
        Args:
            verb: Action verb
            
        Returns:
            Tuple of (level_name, level_number)
        """
        verb_lower = verb.lower()
        
        for level, data in self.taxonomy['taxonomy'].items():
            verbs = [v.lower() for v in data.get('verbs', [])]
            if verb_lower in verbs:
                return (level, data.get('level', 0))
                
        return ('unknown', 0)
        
    def get_verbs_for_level(self, bloom_level: str) -> List[str]:
        """
        Get all action verbs for a Bloom's level
        
        Args:
            bloom_level: Bloom's taxonomy level
            
        Returns:
            List of action verbs
        """
        level_data = self.taxonomy['taxonomy'].get(bloom_level, {})
        return level_data.get('verbs', [])
