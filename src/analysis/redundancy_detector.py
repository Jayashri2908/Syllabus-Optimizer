"""
Redundancy Detector for SCDO
Detects content redundancies and overlaps across syllabus units
"""

from typing import Dict, List, Any, Tuple
import logging

from ..utils.text_processing import TextProcessor


class RedundancyDetector:
    """Detect content redundancies using text similarity analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        self.similarity_threshold = 0.4

    def detect_redundancies(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect content redundancies across syllabus units

        Args:
            syllabus_data: Parsed syllabus structure

        Returns:
            Redundancy analysis report
        """
        units = syllabus_data.get('units', [])
        outcomes = syllabus_data.get('learning_outcomes', [])

        redundant_pairs = []
        unit_pairs_checked = 0

        # Check for overlap between unit topics
        unit_texts = self._extract_unit_texts(units)
        for i in range(len(unit_texts)):
            for j in range(i + 1, len(unit_texts)):
                unit_pairs_checked += 1
                similarity = self._compute_similarity(unit_texts[i][1], unit_texts[j][1])
                if similarity >= self.similarity_threshold:
                    redundant_pairs.append({
                        'unit_1': unit_texts[i][0],
                        'unit_2': unit_texts[j][0],
                        'similarity': round(similarity, 3),
                        'severity': 'high' if similarity >= 0.7 else 'medium',
                        'description': (
                            f"Significant overlap between {unit_texts[i][0]} and "
                            f"{unit_texts[j][0]} (similarity: {similarity:.0%})"
                        ),
                    })

        # Check for duplicate learning outcomes
        duplicate_outcomes = self._find_duplicate_outcomes(outcomes)

        # Calculate overall redundancy score
        overlap_score = self._calculate_overlap_score(redundant_pairs, len(units))

        return {
            'redundant_pairs': redundant_pairs,
            'duplicate_outcomes': duplicate_outcomes,
            'overlap_score': overlap_score,
            'unit_pairs_checked': unit_pairs_checked,
            'total_redundancies': len(redundant_pairs) + len(duplicate_outcomes),
        }

    def _extract_unit_texts(self, units: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
        """
        Extract combined text from each unit for comparison

        Returns:
            List of (unit_label, combined_text) tuples
        """
        result = []
        for idx, unit in enumerate(units, 1):
            label = unit.get('title', f'Unit {idx}')
            parts = []

            title = unit.get('title', '')
            if title:
                parts.append(title)

            topics = unit.get('topics', [])
            for topic in topics:
                if isinstance(topic, str):
                    parts.append(topic)
                elif isinstance(topic, dict):
                    parts.append(topic.get('title', '') or topic.get('name', ''))
                    subtopics = topic.get('subtopics', [])
                    parts.extend(st if isinstance(st, str) else st.get('title', '') for st in subtopics)

            combined = ' '.join(parts)
            result.append((label, combined))

        return result

    def _compute_similarity(self, text_a: str, text_b: str) -> float:
        """
        Compute similarity between two texts using keyword overlap

        Args:
            text_a: First text
            text_b: Second text

        Returns:
            Similarity score between 0 and 1
        """
        keywords_a = set(self.text_processor.extract_keywords(text_a, top_n=15))
        keywords_b = set(self.text_processor.extract_keywords(text_b, top_n=15))

        if not keywords_a or not keywords_b:
            return 0.0

        intersection = keywords_a & keywords_b
        union = keywords_a | keywords_b

        # Jaccard similarity
        return len(intersection) / len(union) if union else 0.0

    def _find_duplicate_outcomes(
        self, outcomes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find duplicate or highly similar learning outcomes

        Returns:
            List of duplicate outcome pairs
        """
        duplicates = []
        descriptions = []

        for outcome in outcomes:
            desc = outcome.get('description', '') if isinstance(outcome, dict) else str(outcome)
            descriptions.append(desc)

        for i in range(len(descriptions)):
            for j in range(i + 1, len(descriptions)):
                similarity = self._compute_similarity(descriptions[i], descriptions[j])
                if similarity >= self.similarity_threshold:
                    duplicates.append({
                        'outcome_1': descriptions[i][:80],
                        'outcome_2': descriptions[j][:80],
                        'similarity': round(similarity, 3),
                    })

        return duplicates

    def _calculate_overlap_score(
        self, redundant_pairs: List[Dict[str, Any]], total_units: int
    ) -> float:
        """
        Calculate an overall overlap score for the syllabus

        Returns:
            Overlap score between 0 (no overlap) and 1 (complete overlap)
        """
        if not redundant_pairs or total_units < 2:
            return 0.0

        max_possible_pairs = total_units * (total_units - 1) / 2
        # Weight high-severity pairs more
        weighted_count = sum(
            1.5 if p.get('severity') == 'high' else 1.0 for p in redundant_pairs
        )
        return min(1.0, round(weighted_count / max_possible_pairs, 3))
