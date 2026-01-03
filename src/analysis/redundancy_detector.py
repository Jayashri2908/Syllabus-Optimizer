"""
Redundancy Detector for SCDO
Detects semantic duplicates and redundant content in syllabi
"""

from typing import Dict, List, Any, Tuple
import logging
from collections import defaultdict

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class RedundancyDetector:
    """Detect content redundancies using semantic similarity"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Similarity thresholds
        self.HIGH_SIMILARITY = 0.85  # > 85% = likely redundant
        self.MODERATE_SIMILARITY = 0.70  # 70-85% = similar, review needed
        
        # Initialize sentence transformer if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.enabled = True
            except Exception as e:
                self.logger.warning(f"Failed to load sentence transformer: {e}")
                self.enabled = False
        else:
            self.logger.warning("sentence-transformers not installed. Redundancy detection disabled.")
            self.enabled = False
            self.model = None
            
    def detect_redundancies(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect content redundancies in syllabus
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            Redundancy analysis report
        """
        if not self.enabled:
            return {
                'enabled': False,
                'message': 'Redundancy detection requires sentence-transformers package',
                'duplicate_topics': [],
                'similar_outcomes': [],
                'redundant_objectives': []
            }
            
        # Detect redundancies in different components
        duplicate_topics = self._detect_duplicate_topics(syllabus_data.get('units', []))
        similar_outcomes = self._detect_similar_outcomes(syllabus_data.get('learning_outcomes', []))
        redundant_objectives = self._detect_redundant_objectives(syllabus_data.get('objectives', []))
        
        # Calculate overall redundancy score
        total_checks = (
            len(duplicate_topics) + 
            len(similar_outcomes) + 
            len(redundant_objectives)
        )
        
        return {
            'enabled': True,
            'duplicate_topics': duplicate_topics,
            'similar_outcomes': similar_outcomes,
            'redundant_objectives': redundant_objectives,
            'total_redundancies': total_checks,
            'severity': self._calculate_severity(total_checks)
        }
        
    def _detect_duplicate_topics(self, units: List[Dict]) -> List[Dict]:
        """Detect duplicate or highly similar topics across units"""
        if not units:
            return []
            
        # Collect all topics with their unit info
        topics_with_context = []
        for unit in units:
            unit_number = unit.get('unit_number', 0)
            unit_title = unit.get('title', '')
            for topic in unit.get('topics', []):
                topics_with_context.append({
                    'text': topic,
                    'unit_number': unit_number,
                    'unit_title': unit_title
                })
                
        if len(topics_with_context) < 2:
            return []
            
        # Compute embeddings
        topic_texts = [t['text'] for t in topics_with_context]
        embeddings = self.model.encode(topic_texts)
        
        # Find similar pairs
        duplicates = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = self._cosine_similarity(embeddings[i], embeddings[j])
                
                # Only report if high similarity and from different units
                if (similarity >= self.MODERATE_SIMILARITY and 
                    topics_with_context[i]['unit_number'] != topics_with_context[j]['unit_number']):
                    
                    duplicates.append({
                        'topic1': topics_with_context[i]['text'],
                        'unit1': f"Unit {topics_with_context[i]['unit_number']}: {topics_with_context[i]['unit_title']}",
                        'topic2': topics_with_context[j]['text'],
                        'unit2': f"Unit {topics_with_context[j]['unit_number']}: {topics_with_context[j]['unit_title']}",
                        'similarity': float(similarity),
                        'severity': 'high' if similarity >= self.HIGH_SIMILARITY else 'moderate'
                    })
                    
        return duplicates
        
    def _detect_similar_outcomes(self, outcomes: List[Any]) -> List[Dict]:
        """Detect similar learning outcomes"""
        if not outcomes or len(outcomes) < 2:
            return []
            
        # Extract outcome descriptions
        outcome_texts = []
        for outcome in outcomes:
            if isinstance(outcome, dict):
                text = outcome.get('description', '')
                code = outcome.get('code', '')
            elif isinstance(outcome, str):
                text = outcome
                code = f'CO{len(outcome_texts) + 1}'
            else:
                continue
                
            outcome_texts.append({'text': text, 'code': code})
            
        if len(outcome_texts) < 2:
            return []
            
        # Compute embeddings
        texts = [o['text'] for o in outcome_texts]
        embeddings = self.model.encode(texts)
        
        # Find similar pairs
        similar = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = self._cosine_similarity(embeddings[i], embeddings[j])
                
                if similarity >= self.MODERATE_SIMILARITY:
                    similar.append({
                        'outcome1': outcome_texts[i]['code'],
                        'text1': outcome_texts[i]['text'],
                        'outcome2': outcome_texts[j]['code'],
                        'text2': outcome_texts[j]['text'],
                        'similarity': float(similarity),
                        'severity': 'high' if similarity >= self.HIGH_SIMILARITY else 'moderate'
                    })
                    
        return similar
        
    def _detect_redundant_objectives(self, objectives: List[str]) -> List[Dict]:
        """Detect redundant course objectives"""
        if not objectives or len(objectives) < 2:
            return []
            
        # Compute embeddings
        embeddings = self.model.encode(objectives)
        
        # Find similar pairs
        redundant = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = self._cosine_similarity(embeddings[i], embeddings[j])
                
                if similarity >= self.MODERATE_SIMILARITY:
                    redundant.append({
                        'objective1': objectives[i],
                        'objective2': objectives[j],
                        'similarity': float(similarity),
                        'severity': 'high' if similarity >= self.HIGH_SIMILARITY else 'moderate'
                    })
                    
        return redundant
        
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors"""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            import numpy as np
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            return dot_product / (norm1 * norm2)
        return 0.0
        
    def _calculate_severity(self, total_redundancies: int) -> str:
        """Calculate overall redundancy severity"""
        if total_redundancies == 0:
            return 'none'
        elif total_redundancies <= 2:
            return 'low'
        elif total_redundancies <= 5:
            return 'moderate'
        else:
            return 'high'
