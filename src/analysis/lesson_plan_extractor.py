"""
Lesson Plan Extractor for SCDO
Extracts detailed lesson plan structure from syllabus units
"""

from typing import Dict, List, Any
import re
import logging


class LessonPlanExtractor:
    """Extract detailed lesson plan information from syllabus units"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Keywords for teaching methods
        self.teaching_method_keywords = {
            'lecture': ['lecture', 'presentation', 'teaching', 'explanation'],
            'lab': ['lab', 'laboratory', 'practical', 'experiment', 'hands-on'],
            'tutorial': ['tutorial', 'problem solving', 'exercise', 'practice'],
            'project': ['project', 'assignment', 'case study', 'real-world'],
            'discussion': ['discussion', 'group work', 'collaborative', 'seminar'],
            'demonstration': ['demonstration', 'demo', 'show'],
            'self_study': ['self-study', 'reading', 'independent']
        }
        
        # Keywords for assessment activities
        self.assessment_keywords = {
            'quiz': ['quiz', 'test', 'mcq'],
            'assignment': ['assignment', 'homework', 'task'],
            'project': ['project', 'mini-project'],
            'presentation': ['presentation', 'seminar'],
            'lab_report': ['lab report', 'practical report'],
            'exam': ['exam', 'examination', 'end-term']
        }
        
    def extract_lesson_plans(self, units: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract detailed lesson plan structure from units
        
        Args:
            units: List of unit dictionaries
            
        Returns:
            Lesson plan analysis
        """
        lessons = []
        total_planned_hours = 0
        units_without_hours = []
        units_without_methods = []
        
        for unit_idx, unit in enumerate(units):
            unit_number = unit.get('unit_number', unit_idx + 1)
            unit_title = unit.get('title', f'Unit {unit_number}')
            unit_hours = unit.get('hours', 0)
            topics = unit.get('topics', [])
            
            # Extract lessons from topics
            unit_lessons = self._extract_lessons_from_topics(
                topics, unit_number, unit_title, unit_hours
            )
            
            lessons.extend(unit_lessons)
            total_planned_hours += sum(lesson['hours'] for lesson in unit_lessons)
            
            # Track gaps
            if unit_hours == 0:
                units_without_hours.append({
                    'unit_number': unit_number,
                    'title': unit_title
                })
                
            # Check for teaching methods
            methods_found = self._detect_teaching_methods(topics)
            if not methods_found:
                units_without_methods.append({
                    'unit_number': unit_number,
                    'title': unit_title
                })
                
        return {
            'lessons': lessons,
            'total_lessons': len(lessons),
            'total_planned_hours': total_planned_hours,
            'average_hours_per_lesson': total_planned_hours / len(lessons) if lessons else 0,
            'units_without_hours': units_without_hours,
            'units_without_methods': units_without_methods,
            'lesson_distribution': self._analyze_lesson_distribution(lessons),
            'teaching_methods_used': self._summarize_teaching_methods(lessons)
        }
        
    def _extract_lessons_from_topics(
        self, 
        topics: List[str], 
        unit_number: int,
        unit_title: str,
        total_hours: float
    ) -> List[Dict[str, Any]]:
        """Extract individual lessons from unit topics"""
        lessons = []
        
        if not topics:
            return lessons
            
        # Estimate hours per topic if not specified
        hours_per_topic = total_hours / len(topics) if total_hours > 0 else 2.0
        
        for topic_idx, topic in enumerate(topics):
            # Parse topic for embedded hours (e.g., "Introduction (2 hours)")
            topic_text, topic_hours = self._parse_topic_hours(topic, hours_per_topic)
            
            # Detect teaching methods from topic text
            methods = self._detect_teaching_methods([topic_text])
            
            # Detect assessment activities
            assessments = self._detect_assessments([topic_text])
            
            lesson = {
                'lesson_number': topic_idx + 1,
                'unit_number': unit_number,
                'unit_title': unit_title,
                'topic': topic_text,
                'hours': topic_hours,
                'teaching_methods': methods,
                'assessments': assessments
            }
            
            lessons.append(lesson)
            
        return lessons
        
    def _parse_topic_hours(self, topic: str, default_hours: float) -> tuple:
        """Parse topic text and extract hours if mentioned"""
        # Look for patterns like "(2 hours)", "[3h]", "- 2hrs"
        hour_pattern = r'\((\d+\.?\d*)\s*(?:hours?|hrs?|h)\)|[\[\(](\d+\.?\d*)h[\]\)]|[-–]\s*(\d+\.?\d*)\s*(?:hours?|hrs?)'
        
        match = re.search(hour_pattern, topic, re.IGNORECASE)
        if match:
            # Extract the number
            hours_str = next(g for g in match.groups() if g is not None)
            hours = float(hours_str)
            # Remove the hours notation from topic text
            topic_text = re.sub(hour_pattern, '', topic).strip()
            return topic_text, hours
        
        return topic, default_hours
        
    def _detect_teaching_methods(self, topics: List[str]) -> List[str]:
        """Detect teaching methods mentioned in topics"""
        methods = set()
        
        topics_text = ' '.join(topics).lower()
        
        for method, keywords in self.teaching_method_keywords.items():
            if any(keyword in topics_text for keyword in keywords):
                methods.add(method)
                
        return list(methods)
        
    def _detect_assessments(self, topics: List[str]) -> List[str]:
        """Detect assessment activities mentioned in topics"""
        assessments = set()
        
        topics_text = ' '.join(topics).lower()
        
        for assessment, keywords in self.assessment_keywords.items():
            if any(keyword in topics_text for keyword in keywords):
                assessments.add(assessment)
                
        return list(assessments)
        
    def _analyze_lesson_distribution(self, lessons: List[Dict]) -> Dict[str, Any]:
        """Analyze how lessons are distributed across units"""
        if not lessons:
            return {}
            
        unit_lesson_counts = {}
        unit_hour_counts = {}
        
        for lesson in lessons:
            unit_num = lesson['unit_number']
            unit_lesson_counts[unit_num] = unit_lesson_counts.get(unit_num, 0) + 1
            unit_hour_counts[unit_num] = unit_hour_counts.get(unit_num, 0) + lesson['hours']
            
        return {
            'lessons_per_unit': unit_lesson_counts,
            'hours_per_unit': unit_hour_counts,
            'most_dense_unit': max(unit_lesson_counts, key=unit_lesson_counts.get) if unit_lesson_counts else None,
            'least_dense_unit': min(unit_lesson_counts, key=unit_lesson_counts.get) if unit_lesson_counts else None
        }
        
    def _summarize_teaching_methods(self, lessons: List[Dict]) -> Dict[str, int]:
        """Summarize teaching methods used across all lessons"""
        method_counts = {}
        
        for lesson in lessons:
            for method in lesson.get('teaching_methods', []):
                method_counts[method] = method_counts.get(method, 0) + 1
                
        return method_counts
