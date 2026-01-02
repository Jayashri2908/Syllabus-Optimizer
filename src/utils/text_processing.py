"""Text processing utilities for SCDO"""

import re
from typing import List, Dict, Set
import yaml
from pathlib import Path


class TextProcessor:
    """Utilities for text processing and NLP tasks"""
    
    def __init__(self):
        self.bloom_verbs = self._load_bloom_verbs()
        
    def _load_bloom_verbs(self) -> Dict[str, Set[str]]:
        """Load Bloom's taxonomy verbs from config"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "bloom_taxonomy.yaml"
        
        with open(config_path, 'r') as f:
            taxonomy = yaml.safe_load(f)
            
        verbs = {}
        for level, data in taxonomy['taxonomy'].items():
            verbs[level] = set(v.lower() for v in data['verbs'])
            
        return verbs
        
    def extract_learning_outcomes(self, text: str) -> List[str]:
        """
        Extract learning outcomes from text
        
        Args:
            text: Input text
            
        Returns:
            List of learning outcomes
        """
        # Common patterns for learning outcomes
        patterns = [
            r'(?:CO\d+|Course Outcome \d+)[:\s]+(.+?)(?=CO\d+|Course Outcome|\n\n|$)',
            r'(?:Students will be able to|Upon completion)[:\s]+(.+?)(?=\n\n|$)',
            r'(?:Learning Outcome|Outcome)[:\s]+(.+?)(?=\n\n|$)'
        ]
        
        outcomes = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            outcomes.extend([m.group(1).strip() for m in matches])
            
        return outcomes
        
    def classify_bloom_level(self, text: str) -> str:
        """
        Classify text to Bloom's taxonomy level
        
        Args:
            text: Text to classify (learning outcome or objective)
            
        Returns:
            Bloom's level (remember, understand, apply, analyze, evaluate, create)
        """
        text_lower = text.lower()
        
        # Check for verbs in each level
        for level, verbs in self.bloom_verbs.items():
            for verb in verbs:
                # Match whole words only
                if re.search(rf'\b{verb}\b', text_lower):
                    return level
                    
        return "unknown"
        
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            top_n: Number of keywords to extract
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction (can be enhanced with TF-IDF or other methods)
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                     'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
                     'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Filter and count
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in sorted_words[:top_n]]
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
        
        return text.strip()
        
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
