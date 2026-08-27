"""
Content Analyzer for SCDO
Analyzes content depth, breadth, and alignment quality
"""

from typing import Dict, List, Any
import logging

from ..utils.text_processing import TextProcessor


class ContentAnalyzer:
    """Analyze syllabus content quality, depth, and breadth"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()

    def analyze(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform content quality analysis

        Args:
            syllabus_data: Parsed syllabus structure

        Returns:
            Content quality analysis report
        """
        units = syllabus_data.get('units', [])
        outcomes = syllabus_data.get('learning_outcomes', [])

        depth_score = self._assess_depth(units)
        breadth_score = self._assess_breadth(units, outcomes)
        alignment_score = self._assess_alignment(units, outcomes)
        issues = self._identify_issues(syllabus_data)

        overall_score = round(
            (depth_score + breadth_score + alignment_score) / 3, 2
        )

        return {
            'depth_score': depth_score,
            'breadth_score': breadth_score,
            'alignment_score': alignment_score,
            'overall_score': overall_score,
            'issues': issues,
        }

    def _assess_depth(self, units: List[Dict[str, Any]]) -> float:
        """
        Assess content depth based on topic detail and hour allocation

        Returns:
            Depth score between 0 and 1
        """
        if not units:
            return 0.0

        scores = []
        for unit in units:
            score = 0.0
            topics = unit.get('topics', [])
            hours = unit.get('hours', 0)

            # Topics present
            if topics:
                score += 0.3

            # Subtopics indicate depth
            has_subtopics = any(
                isinstance(t, dict) and t.get('subtopics')
                for t in topics
            )
            if has_subtopics:
                score += 0.3

            # Reasonable hours allocated
            if hours and hours >= 6:
                score += 0.2
            elif hours and hours >= 3:
                score += 0.1

            # Detailed descriptions
            descriptions = [
                t.get('description', '') for t in topics if isinstance(t, dict)
            ]
            if any(len(d) > 50 for d in descriptions):
                score += 0.2

            scores.append(min(score, 1.0))

        return round(sum(scores) / len(scores), 2) if scores else 0.0

    def _assess_breadth(
        self, units: List[Dict[str, Any]], outcomes: List[Any]
    ) -> float:
        """
        Assess content breadth across Bloom's taxonomy levels

        Returns:
            Breadth score between 0 and 1
        """
        if not outcomes:
            return 0.0

        # Count Bloom's levels represented
        levels_found = set()
        for outcome in outcomes:
            if isinstance(outcome, dict):
                text = outcome.get('description', '')
            else:
                text = str(outcome)
            level = self.text_processor.classify_bloom_level(text)
            if level != 'unknown':
                levels_found.add(level)

        # Ideal: at least 3 different Bloom's levels
        return min(1.0, round(len(levels_found) / 3, 2))

    def _assess_alignment(
        self, units: List[Dict[str, Any]], outcomes: List[Any]
    ) -> float:
        """
        Assess alignment between outcomes and unit content

        Returns:
            Alignment score between 0 and 1
        """
        if not units or not outcomes:
            return 0.0

        # Check if number of outcomes is reasonable relative to units
        outcome_count = len(outcomes)
        unit_count = len(units)

        # Typically 1-2 outcomes per unit
        expected_min = unit_count
        expected_max = unit_count * 2

        if expected_min <= outcome_count <= expected_max:
            ratio_score = 1.0
        elif outcome_count < expected_min:
            ratio_score = max(0.0, outcome_count / expected_min) if expected_min else 0.0
        else:
            ratio_score = max(0.0, expected_max / outcome_count) if outcome_count else 0.0

        # Check keyword overlap between outcomes and unit topics
        outcome_text = ' '.join(
            o.get('description', '') if isinstance(o, dict) else str(o)
            for o in outcomes
        )
        unit_text = ' '.join(
            t.get('title', '') if isinstance(t, dict) else str(t)
            for u in units
            for t in u.get('topics', [])
        )

        outcome_kw = set(self.text_processor.extract_keywords(outcome_text, top_n=15))
        unit_kw = set(self.text_processor.extract_keywords(unit_text, top_n=15))

        if outcome_kw and unit_kw:
            overlap = len(outcome_kw & unit_kw) / len(outcome_kw | unit_kw)
            keyword_score = min(1.0, overlap * 3)  # Scale up since some divergence is normal
        else:
            keyword_score = 0.5  # Neutral if can't determine

        return round((ratio_score + keyword_score) / 2, 2)

    def _identify_issues(self, syllabus_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Identify content quality issues

        Returns:
            List of issue dicts with type, severity, and description
        """
        issues = []
        units = syllabus_data.get('units', [])

        for idx, unit in enumerate(units, 1):
            topics = unit.get('topics', [])
            if not topics:
                issues.append({
                    'type': 'empty_unit',
                    'severity': 'high',
                    'unit': f'Unit {idx}',
                    'description': f'Unit {idx} has no topics defined',
                })

            hours = unit.get('hours', 0)
            if hours and topics and hours / max(len(topics), 1) < 1:
                issues.append({
                    'type': 'insufficient_hours',
                    'severity': 'medium',
                    'unit': f'Unit {idx}',
                    'description': f'Unit {idx} has insufficient hours for the number of topics',
                })

        return issues
