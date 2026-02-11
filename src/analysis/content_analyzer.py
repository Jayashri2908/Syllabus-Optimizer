"""
Content Analyzer for SCDO
Provides advanced content quality analysis, modern topics detection, and scoring
"""

from typing import Dict, List, Any, Tuple
import logging
import re


class ContentAnalyzer:
    """Analyze syllabus content quality and relevance"""
    
    # Modern/Industry-relevant topics (2024+)
    MODERN_TOPICS = {
        'artificial_intelligence': ['artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning', 
                                     'neural network', 'nlp', 'natural language processing', 'computer vision',
                                     'reinforcement learning', 'generative ai', 'llm', 'transformer'],
        'cloud_computing': ['cloud computing', 'aws', 'azure', 'gcp', 'google cloud', 'serverless',
                            'docker', 'kubernetes', 'k8s', 'containerization', 'microservices'],
        'data_science': ['data science', 'big data', 'data analytics', 'data mining', 'hadoop',
                         'spark', 'data visualization', 'pandas', 'numpy', 'tensorflow', 'pytorch'],
        'cybersecurity': ['cybersecurity', 'security', 'encryption', 'cryptography', 'firewall',
                          'penetration testing', 'ethical hacking', 'network security', 'blockchain'],
        'web_technologies': ['react', 'angular', 'vue', 'node.js', 'django', 'flask', 'rest api',
                             'graphql', 'mongodb', 'nosql', 'progressive web app', 'pwa'],
        'devops': ['devops', 'ci/cd', 'continuous integration', 'jenkins', 'git', 'version control',
                   'agile', 'scrum', 'automation', 'terraform', 'ansible'],
        'iot': ['internet of things', 'iot', 'embedded systems', 'arduino', 'raspberry pi',
                'sensors', 'mqtt', 'edge computing'],
        'mobile': ['android', 'ios', 'flutter', 'react native', 'mobile app', 'kotlin', 'swift'],
    }
    
    # Topics indicating depth/complexity
    ADVANCED_INDICATORS = [
        'optimization', 'complexity analysis', 'advanced', 'distributed', 'parallel',
        'scalability', 'performance tuning', 'design patterns', 'architecture',
        'research', 'case study', 'real-world', 'industry', 'project'
    ]
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive content quality analysis
        
        Returns:
            Content analysis with scores and insights
        """
        return {
            'quality_score': self._calculate_quality_score(syllabus_data),
            'modern_topics': self._detect_modern_topics(syllabus_data),
            'content_depth': self._analyze_content_depth(syllabus_data),
            'hours_distribution': self._analyze_hours_distribution(syllabus_data),
            'learning_progression': self._analyze_learning_progression(syllabus_data),
            'topic_coverage': self._analyze_topic_coverage(syllabus_data),
            'unit_analysis': self._analyze_units(syllabus_data),
        }
    
    def _calculate_quality_score(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall content quality score (0-100)"""
        scores = {}
        
        # Completeness score (25 points max)
        completeness = 0
        if syllabus_data.get('course_title'): completeness += 5
        if syllabus_data.get('course_code'): completeness += 5
        if syllabus_data.get('learning_outcomes'): completeness += 5
        if syllabus_data.get('units'): completeness += 5
        if syllabus_data.get('references'): completeness += 5
        scores['completeness'] = completeness
        
        # Depth score (25 points max)
        depth = 0
        units = syllabus_data.get('units', [])
        outcomes = syllabus_data.get('learning_outcomes', [])
        
        # Score based on number of outcomes
        if len(outcomes) >= 5:
            depth += 10
        elif len(outcomes) >= 3:
            depth += 5
        
        # Score based on unit topics
        total_topics = sum(len(u.get('topics', [])) for u in units)
        if total_topics >= 20:
            depth += 10
        elif total_topics >= 10:
            depth += 5
        
        # Advanced topics bonus
        all_text = self._extract_all_text(syllabus_data).lower()
        advanced_count = sum(1 for ind in self.ADVANCED_INDICATORS if ind in all_text)
        depth += min(5, advanced_count)
        scores['depth'] = min(25, depth)
        
        # Modern relevance score (25 points max)
        modern_topics = self._detect_modern_topics(syllabus_data)
        modern_score = min(25, len(modern_topics['detected']) * 5)
        scores['modern_relevance'] = modern_score
        
        # Structure score (25 points max)
        structure = 0
        if len(units) >= 4: structure += 10
        if all(u.get('hours', 0) > 0 for u in units): structure += 10
        if syllabus_data.get('assessment_pattern'): structure += 5
        scores['structure'] = min(25, structure)
        
        # Calculate total
        total = sum(scores.values())
        
        # Determine grade
        if total >= 80:
            grade = 'A'
            status = 'Excellent'
        elif total >= 60:
            grade = 'B'
            status = 'Good'
        elif total >= 40:
            grade = 'C'
            status = 'Needs Improvement'
        else:
            grade = 'D'
            status = 'Significant Gaps'
        
        return {
            'total_score': total,
            'max_score': 100,
            'grade': grade,
            'status': status,
            'breakdown': scores
        }
    
    def _detect_modern_topics(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect modern/industry-relevant topics in syllabus"""
        all_text = self._extract_all_text(syllabus_data).lower()
        
        detected = []
        missing = []
        
        for category, keywords in self.MODERN_TOPICS.items():
            found_keywords = [kw for kw in keywords if kw in all_text]
            if found_keywords:
                detected.append({
                    'category': category.replace('_', ' ').title(),
                    'keywords': found_keywords[:3],  # Limit to 3 keywords per category
                    'count': len(found_keywords)
                })
            else:
                missing.append(category.replace('_', ' ').title())
        
        return {
            'detected': detected,
            'missing_suggestions': missing[:5],  # Suggest top 5 missing
            'modernity_score': len(detected) / len(self.MODERN_TOPICS) * 100
        }
    
    def _analyze_content_depth(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the depth and complexity of content"""
        units = syllabus_data.get('units', [])
        
        unit_depths = []
        for unit in units:
            topics = unit.get('topics', [])
            topics_text = ' '.join(str(t) for t in topics).lower()
            
            # Count advanced indicators
            advanced_count = sum(1 for ind in self.ADVANCED_INDICATORS if ind in topics_text)
            
            # Estimate depth level
            if advanced_count >= 3:
                depth_level = 'advanced'
            elif advanced_count >= 1:
                depth_level = 'intermediate'
            else:
                depth_level = 'basic'
            
            unit_depths.append({
                'unit_number': unit.get('unit_number', '?'),
                'title': unit.get('title', 'Untitled'),
                'topic_count': len(topics),
                'depth_level': depth_level,
                'advanced_concepts': advanced_count
            })
        
        # Calculate overall depth distribution
        depth_distribution = {
            'basic': sum(1 for u in unit_depths if u['depth_level'] == 'basic'),
            'intermediate': sum(1 for u in unit_depths if u['depth_level'] == 'intermediate'),
            'advanced': sum(1 for u in unit_depths if u['depth_level'] == 'advanced')
        }
        
        return {
            'unit_depths': unit_depths,
            'depth_distribution': depth_distribution,
            'total_topics': sum(u['topic_count'] for u in unit_depths)
        }
    
    def _analyze_hours_distribution(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze distribution of hours across units with theory/practical breakdown"""
        units = syllabus_data.get('units', [])
        
        if not units:
            return {
                'distribution': [],
                'total_hours': 0,
                'average_hours': 0,
                'imbalances': [],
                'is_balanced': True
            }
        
        hours_data = []
        total_hours = 0
        
        for unit in units:
            hours = unit.get('hours', 0)
            # Handle both numeric and string hours
            if isinstance(hours, str):
                try:
                    hours = int(hours.split()[0]) if hours else 0
                except (ValueError, IndexError):
                    hours = 0
            
            total_hours += hours
            topics = unit.get('topics', [])
            topic_count = len(topics) if topics else 0
            
            hours_data.append({
                'unit_number': unit.get('unit_number', '?'),
                'title': unit.get('title', 'Untitled')[:40],
                'hours': hours,
                'topic_count': topic_count,
                'hours_per_topic': round(hours / topic_count, 1) if topic_count > 0 else 0
            })
        
        # Calculate percentages (rounded to 1 decimal)
        for item in hours_data:
            item['percentage'] = round((item['hours'] / total_hours * 100), 1) if total_hours > 0 else 0
        
        # Find imbalances based on expected distribution
        avg_hours = total_hours / len(units) if units else 0
        expected_percentage = 100 / len(units) if units else 0
        imbalances = []
        
        for item in hours_data:
            deviation = abs(item['percentage'] - expected_percentage)
            if item['hours'] == 0:
                imbalances.append({
                    'unit': item['unit_number'],
                    'issue': 'no_hours',
                    'hours': item['hours'],
                    'expected': round(avg_hours, 1),
                    'description': f"Unit {item['unit_number']} has no hours specified"
                })
            elif deviation > 15:  # More than 15% deviation from expected
                issue_type = 'too_few_hours' if item['percentage'] < expected_percentage else 'too_many_hours'
                imbalances.append({
                    'unit': item['unit_number'],
                    'issue': issue_type,
                    'hours': item['hours'],
                    'percentage': item['percentage'],
                    'expected_percentage': round(expected_percentage, 1),
                    'description': f"Unit {item['unit_number']} has {item['percentage']}% (expected ~{round(expected_percentage)}%)"
                })
        
        # Analyze hours-per-topic ratio
        hours_per_topic_values = [item['hours_per_topic'] for item in hours_data if item['hours_per_topic'] > 0]
        avg_hours_per_topic = sum(hours_per_topic_values) / len(hours_per_topic_values) if hours_per_topic_values else 0
        
        return {
            'distribution': hours_data,
            'total_hours': total_hours,
            'average_hours': round(avg_hours, 1),
            'expected_per_unit': round(expected_percentage, 1),
            'average_hours_per_topic': round(avg_hours_per_topic, 1),
            'imbalances': imbalances,
            'is_balanced': len(imbalances) == 0
        }
    
    def _analyze_learning_progression(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze if content follows proper learning progression (basic -> advanced)"""
        units = syllabus_data.get('units', [])
        
        # Keywords indicating introductory content
        intro_keywords = ['introduction', 'basic', 'fundamental', 'overview', 'definition', 'concept']
        # Keywords indicating advanced content
        advanced_keywords = ['advanced', 'optimization', 'complex', 'case study', 'project', 'research']
        
        progression_analysis = []
        
        for i, unit in enumerate(units):
            title = unit.get('title', '').lower()
            topics = ' '.join(str(t) for t in unit.get('topics', [])).lower()
            all_text = title + ' ' + topics
            
            intro_count = sum(1 for kw in intro_keywords if kw in all_text)
            advanced_count = sum(1 for kw in advanced_keywords if kw in all_text)
            
            if intro_count > advanced_count:
                level = 'introductory'
            elif advanced_count > intro_count:
                level = 'advanced'
            else:
                level = 'intermediate'
            
            progression_analysis.append({
                'unit_number': unit.get('unit_number', i + 1),
                'level': level
            })
        
        # Check if progression is logical (intro -> intermediate -> advanced)
        level_order = {'introductory': 0, 'intermediate': 1, 'advanced': 2}
        is_proper_progression = True
        issues = []
        
        for i in range(1, len(progression_analysis)):
            prev_level = level_order[progression_analysis[i-1]['level']]
            curr_level = level_order[progression_analysis[i]['level']]
            
            # Advanced content appearing too early is a regression
            if curr_level < prev_level - 1:
                is_proper_progression = False
                issues.append(f"Unit {progression_analysis[i]['unit_number']} appears less complex than previous unit")
        
        return {
            'progression': progression_analysis,
            'is_proper_progression': is_proper_progression,
            'issues': issues
        }
    
    def _analyze_topic_coverage(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze topic coverage completeness"""
        units = syllabus_data.get('units', [])
        
        topics_per_unit = []
        for unit in units:
            topics = unit.get('topics', [])
            topics_per_unit.append({
                'unit_number': unit.get('unit_number', '?'),
                'topic_count': len(topics),
                'sample_topics': [str(t)[:50] for t in topics[:3]]  # First 3 topics, truncated
            })
        
        total_topics = sum(t['topic_count'] for t in topics_per_unit)
        avg_topics = total_topics / len(units) if units else 0
        
        # Coverage score (higher is better)
        if avg_topics >= 5:
            coverage_score = 100
        elif avg_topics >= 3:
            coverage_score = 70
        else:
            coverage_score = 40
        
        return {
            'topics_per_unit': topics_per_unit,
            'total_topics': total_topics,
            'average_per_unit': round(avg_topics, 1),
            'coverage_score': coverage_score
        }
    
    def _extract_all_text(self, syllabus_data: Dict[str, Any]) -> str:
        """Extract all text content from syllabus for analysis"""
        text_parts = []
        
        # Add basic fields
        text_parts.append(syllabus_data.get('course_title', ''))
        
        # Add objectives
        for obj in syllabus_data.get('objectives', []):
            text_parts.append(str(obj))
        
        # Add learning outcomes
        for outcome in syllabus_data.get('learning_outcomes', []):
            if isinstance(outcome, dict):
                text_parts.append(outcome.get('description', ''))
            else:
                text_parts.append(str(outcome))
        
        # Add unit content
        for unit in syllabus_data.get('units', []):
            text_parts.append(unit.get('title', ''))
            for topic in unit.get('topics', []):
                text_parts.append(str(topic))
        
        return ' '.join(text_parts)
    
    def _analyze_units(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze each unit's theory content in detail"""
        units = syllabus_data.get('units', [])
        
        if not units:
            return {'units': [], 'summary': 'No units found'}
        
        # Keywords for theory vs practical content
        theory_keywords = ['introduction', 'concept', 'principle', 'theory', 'definition', 
                          'overview', 'fundamental', 'basics', 'understanding', 'types',
                          'classification', 'properties', 'characteristics', 'architecture']
        practical_keywords = ['implementation', 'program', 'code', 'lab', 'exercise', 
                             'practical', 'example', 'application', 'project', 'demo',
                             'experiment', 'hands-on', 'practice']
        
        unit_details = []
        total_theory_topics = 0
        total_practical_topics = 0
        
        for unit in units:
            topics = unit.get('topics', [])
            topics_text = [str(t).lower() for t in topics]
            
            # Categorize topics
            theory_topics = []
            practical_topics = []
            uncategorized = []
            
            for i, topic_text in enumerate(topics_text):
                original_topic = str(topics[i]) if i < len(topics) else topic_text
                is_theory = any(kw in topic_text for kw in theory_keywords)
                is_practical = any(kw in topic_text for kw in practical_keywords)
                
                if is_practical:
                    practical_topics.append(original_topic[:60])
                elif is_theory:
                    theory_topics.append(original_topic[:60])
                else:
                    # Default to theory if no clear classification
                    uncategorized.append(original_topic[:60])
            
            # Calculate unit hours
            hours = unit.get('hours', 0)
            if isinstance(hours, str):
                try:
                    hours = int(hours.split()[0]) if hours else 0
                except (ValueError, IndexError):
                    hours = 0
            
            total_topics = len(topics)
            theory_count = len(theory_topics) + len(uncategorized)  # Uncategorized assumed theory
            practical_count = len(practical_topics)
            
            total_theory_topics += theory_count
            total_practical_topics += practical_count
            
            unit_details.append({
                'unit_number': unit.get('unit_number', '?'),
                'title': unit.get('title', 'Untitled'),
                'total_topics': total_topics,
                'theory_topics': theory_count,
                'practical_topics': practical_count,
                'hours': hours,
                'theory_percentage': round((theory_count / total_topics * 100), 1) if total_topics > 0 else 0,
                'key_concepts': theory_topics[:3],  # Top 3 theory topics
                'practical_elements': practical_topics[:2]  # Top 2 practical elements
            })
        
        # Summary statistics
        total_all_topics = total_theory_topics + total_practical_topics
        theory_ratio = round((total_theory_topics / total_all_topics * 100), 1) if total_all_topics > 0 else 0
        
        return {
            'units': unit_details,
            'total_theory_topics': total_theory_topics,
            'total_practical_topics': total_practical_topics,
            'theory_ratio': theory_ratio,
            'practical_ratio': round(100 - theory_ratio, 1),
            'summary': f"{len(units)} units with {theory_ratio}% theory / {round(100 - theory_ratio, 1)}% practical content"
        }


# Create singleton instance
content_analyzer = ContentAnalyzer()
