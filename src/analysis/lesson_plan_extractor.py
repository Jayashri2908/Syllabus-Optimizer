"""
Lesson Plan Extractor for SCDO
Extracts and analyzes lesson plan structures from syllabus units
"""

from typing import Dict, List, Any
import logging

from ..utils.text_processing import TextProcessor


class LessonPlanExtractor:
    """Extract and analyze lesson plan structures from syllabus units"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()

    def extract_lesson_plans(self, units: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract lesson plan information from syllabus units

        Args:
            units: List of unit dicts from syllabus data

        Returns:
            Lesson plan analysis with distribution and gap info
        """
        units_without_hours = []
        units_without_methods = []
        lessons_per_unit = {}

        for idx, unit in enumerate(units, 1):
            unit_label = unit.get('title', f'Unit {idx}')
            unit_num = str(idx)

            # Check for hours
            hours = unit.get('hours')
            if not hours or hours == 0:
                units_without_hours.append(unit_label)

            # Check for teaching methods
            methods = unit.get('teaching_methods') or unit.get('pedagogy')
            if not methods:
                units_without_methods.append(unit_label)

            # Estimate lesson count from topics
            topics = unit.get('topics', [])
            lesson_count = self._estimate_lesson_count(unit, topics)
            lessons_per_unit[unit_num] = lesson_count

        # Calculate distribution stats
        total_lessons = sum(lessons_per_unit.values())
        avg_lessons = total_lessons / len(units) if units else 0

        return {
            'units_without_hours': units_without_hours,
            'units_without_methods': units_without_methods,
            'lesson_distribution': {
                'lessons_per_unit': lessons_per_unit,
                'total_lessons': total_lessons,
                'average_per_unit': round(avg_lessons, 1),
            },
            'total_units': len(units),
        }

    def _estimate_lesson_count(self, unit: Dict[str, Any], topics: List[Any]) -> int:
        """
        Estimate the number of lessons in a unit based on topics and hours

        Args:
            unit: Unit dict
            topics: List of topics

        Returns:
            Estimated lesson count
        """
        hours = unit.get('hours', 0)

        # If we have explicit lesson plans, count them
        lesson_plans = unit.get('lesson_plans', [])
        if lesson_plans:
            return len(lesson_plans)

        # If we have hours, estimate ~2 hours per lesson
        if hours and hours > 0:
            return max(1, round(hours / 2))

        # Fall back to topic count
        if topics:
            # Each topic could be 1-2 lessons
            return max(1, len(topics))

        return 0
