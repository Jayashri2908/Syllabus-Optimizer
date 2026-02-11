"""
Gap Analyzer for SCDO
Identifies gaps and issues in syllabus content
"""

from typing import Dict, List, Any
import yaml
from pathlib import Path
import logging

from ..utils.text_processing import TextProcessor
from .lesson_plan_extractor import LessonPlanExtractor
from .redundancy_detector import RedundancyDetector
from .content_analyzer import ContentAnalyzer
from ..validation.nep_2020_validator import NEP2020Validator
from ..validation.accreditation_checker import AccreditationChecker


class GapAnalyzer:
    """Analyze syllabus for gaps and improvement opportunities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        self.bloom_taxonomy = self._load_bloom_taxonomy()
        self.accreditation_standards = self._load_accreditation_standards()
        self.lesson_plan_extractor = LessonPlanExtractor()
        self.redundancy_detector = RedundancyDetector()
        self.content_analyzer = ContentAnalyzer()
        self.nep_validator = NEP2020Validator()
        self.accreditation_checker = AccreditationChecker()
        
    def _load_bloom_taxonomy(self) -> dict:
        """Load Bloom's taxonomy configuration"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "bloom_taxonomy.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def _load_accreditation_standards(self) -> dict:
        """Load accreditation standards"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "accreditation.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def analyze(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive gap analysis
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            Gap analysis report
        """
        report = {
            'bloom_coverage': self._analyze_bloom_coverage(syllabus_data),
            'co_po_mapping_gaps': self._analyze_co_po_mapping(syllabus_data),
            'assessment_gaps': self._analyze_assessment(syllabus_data),
            'content_gaps': self._analyze_content(syllabus_data),
            'structural_issues': self._analyze_structure(syllabus_data),
            'lesson_plan_analysis': self._analyze_lesson_plans(syllabus_data),
            'redundancies': self._analyze_redundancies(syllabus_data),
            'content_quality': self.content_analyzer.analyze(syllabus_data),
            'nep_2020_compliance': self.nep_validator.validate(syllabus_data),
            'accreditation_compliance': {
                'nba': self.accreditation_checker.check_nba_compliance(syllabus_data),
                'naac': self.accreditation_checker.check_naac_compliance(syllabus_data)
            },
            'recommendations': []
        }
        
        # Generate recommendations based on gaps
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
        
    def _analyze_bloom_coverage(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Bloom's taxonomy coverage"""
        outcomes = syllabus_data.get('learning_outcomes', [])
        
        # Count outcomes by Bloom's level
        level_counts = {
            'remember': 0,
            'understand': 0,
            'apply': 0,
            'analyze': 0,
            'evaluate': 0,
            'create': 0,
            'unknown': 0
        }
        
        for outcome in outcomes:
            level = outcome.get('bloom_level', 'unknown')
            level_counts[level] = level_counts.get(level, 0) + 1
            
        total = sum(level_counts.values())
        
        # Calculate percentages
        percentages = {}
        if total > 0:
            percentages = {level: (count / total) * 100 
                          for level, count in level_counts.items()}
        
        # Get recommended distribution
        recommended = self.bloom_taxonomy.get('recommended_distribution', {})
        
        # Identify gaps
        gaps = []
        for level, percentage in percentages.items():
            if level == 'unknown':
                continue
                
            rec_range = recommended.get(level, '0-0%')
            # Parse range (e.g., "10-15%")
            if isinstance(rec_range, str) and '-' in rec_range:
                min_val = int(rec_range.split('-')[0])
                max_val = int(rec_range.split('-')[1].rstrip('%'))
                
                if percentage < min_val:
                    gaps.append({
                        'level': level,
                        'current': percentage,
                        'recommended': rec_range,
                        'issue': 'underrepresented'
                    })
                elif percentage > max_val:
                    gaps.append({
                        'level': level,
                        'current': percentage,
                        'recommended': rec_range,
                        'issue': 'overrepresented'
                    })
        
        return {
            'level_counts': level_counts,
            'percentages': percentages,
            'gaps': gaps,
            'total_outcomes': total
        }
        
    def _analyze_co_po_mapping(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CO-PO mapping completeness"""
        mapping = syllabus_data.get('co_po_mapping', {})
        outcomes = syllabus_data.get('learning_outcomes', [])
        
        # Expected POs (typically 12 for engineering)
        expected_pos = [f'PO{i}' for i in range(1, 13)]
        
        gaps = []
        
        # Check if all COs have mappings
        for outcome in outcomes:
            co_code = outcome.get('code', '')
            if co_code not in mapping:
                gaps.append({
                    'type': 'missing_co_mapping',
                    'co': co_code,
                    'description': f'{co_code} has no PO mappings'
                })
            else:
                # Check if all relevant POs are mapped
                co_mapping = mapping[co_code]
                mapped_pos = set(co_mapping.keys())
                
                # At least some POs should be mapped
                if len(mapped_pos) == 0:
                    gaps.append({
                        'type': 'empty_mapping',
                        'co': co_code,
                        'description': f'{co_code} mapping is empty'
                    })
                    
        return {
            'total_cos': len(outcomes),
            'mapped_cos': len(mapping),
            'gaps': gaps,
            'coverage_percentage': (len(mapping) / len(outcomes) * 100) if outcomes else 0
        }
        
    def _analyze_assessment(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze assessment pattern"""
        assessment = syllabus_data.get('assessment_pattern', {})
        
        gaps = []
        
        # Check if assessment adds up to 100%
        total = sum(assessment.values())
        if total != 100 and total > 0:
            gaps.append({
                'type': 'total_mismatch',
                'current_total': total,
                'expected_total': 100,
                'description': f'Assessment components total {total}% instead of 100%'
            })
            
        # Check for missing common components
        recommended_components = ['internal', 'external', 'assignment']
        for component in recommended_components:
            if component not in assessment:
                gaps.append({
                    'type': 'missing_component',
                    'component': component,
                    'description': f'Missing {component} assessment component'
                })
                
        # Check for balanced assessment
        if assessment:
            max_component = max(assessment.values())
            if max_component > 70:
                gaps.append({
                    'type': 'imbalanced',
                    'description': f'One component has {max_component}% weightage (too high)'
                })
                
        return {
            'total_percentage': total,
            'components': assessment,
            'gaps': gaps
        }
        
    def _analyze_content(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content quality and completeness"""
        gaps = []
        
        # Check for missing essential components
        essential = ['course_title', 'course_code', 'credits', 'learning_outcomes', 'units']
        
        for component in essential:
            value = syllabus_data.get(component)
            if not value or (isinstance(value, (list, dict)) and len(value) == 0):
                gaps.append({
                    'type': 'missing_component',
                    'component': component,
                    'description': f'Missing or empty {component}'
                })
                
        # Check unit hours
        units = syllabus_data.get('units', [])
        total_hours = sum(unit.get('hours', 0) for unit in units)
        
        if total_hours == 0:
            gaps.append({
                'type': 'missing_hours',
                'description': 'No unit hours specified'
            })
            
        # Check references
        references = syllabus_data.get('references', [])
        if len(references) < 3:
            gaps.append({
                'type': 'insufficient_references',
                'current_count': len(references),
                'recommended_min': 3,
                'description': 'Insufficient reference materials (minimum 3 recommended)'
            })
            
        return {
            'gaps': gaps,
            'total_units': len(units),
            'total_hours': total_hours,
            'reference_count': len(references)
        }
        
    def _analyze_structure(self, syllabus_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Analyze structural issues"""
        issues = []
        
        # Check number of learning outcomes
        outcomes = syllabus_data.get('learning_outcomes', [])
        if len(outcomes) < 4:
            issues.append({
                'type': 'insufficient_cos',
                'severity': 'high',
                'description': f'Only {len(outcomes)} course outcomes (minimum 4-6 recommended)'
            })
        elif len(outcomes) > 8:
            issues.append({
                'type': 'excessive_cos',
                'severity': 'medium',
                'description': f'{len(outcomes)} course outcomes (maximum 6-8 recommended)'
            })
            
        # Check unit distribution
        units = syllabus_data.get('units', [])
        if len(units) < 3:
            issues.append({
                'type': 'insufficient_units',
                'severity': 'medium',
                'description': f'Only {len(units)} units (typically 4-6 units recommended)'
            })
            
        return issues
        
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations with priority levels"""
        recommendations = []
        
        # Bloom's coverage recommendations (Medium priority)
        bloom_gaps = report['bloom_coverage'].get('gaps', [])
        for gap in bloom_gaps:
            level = gap['level']
            issue = gap['issue']
            if issue == 'underrepresented':
                recommendations.append({
                    'text': f"Add more learning outcomes at '{level}' level to meet recommended distribution",
                    'priority': 'medium',
                    'category': 'bloom_taxonomy'
                })
            elif issue == 'overrepresented':
                recommendations.append({
                    'text': f"Consider reducing '{level}' level outcomes and diversifying cognitive levels",
                    'priority': 'low',
                    'category': 'bloom_taxonomy'
                })
                
        # CO-PO mapping recommendations (High priority - accreditation critical)
        co_po_gaps = report['co_po_mapping_gaps'].get('gaps', [])
        if co_po_gaps:
            recommendations.append({
                'text': "Complete CO-PO mapping for all course outcomes to meet accreditation requirements",
                'priority': 'high',
                'category': 'accreditation'
            })
            
        # Assessment recommendations (High priority)
        assessment_gaps = report['assessment_gaps'].get('gaps', [])
        for gap in assessment_gaps:
            if gap['type'] == 'total_mismatch':
                recommendations.append({
                    'text': "Adjust assessment component weightages to total 100%",
                    'priority': 'high',
                    'category': 'assessment'
                })
            elif gap['type'] == 'missing_component':
                recommendations.append({
                    'text': f"Add {gap['component']} assessment component",
                    'priority': 'medium',
                    'category': 'assessment'
                })
                
        # Content recommendations (Medium priority)
        content_gaps = report['content_gaps'].get('gaps', [])
        for gap in content_gaps:
            if gap['type'] == 'insufficient_references':
                recommendations.append({
                    'text': "Add more reference materials (textbooks, research papers, online resources)",
                    'priority': 'medium',
                    'category': 'content'
                })
            elif gap['type'] == 'missing_hours':
                recommendations.append({
                    'text': "Specify contact hours for each unit",
                    'priority': 'high',
                    'category': 'structure'
                })
        
        # Sort by priority: high > medium > low
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
                
        return recommendations
        
    def _analyze_lesson_plans(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze lesson plan completeness and structure
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            Lesson plan analysis
        """
        units = syllabus_data.get('units', [])
        
        if not units:
            return {
                'status': 'no_units',
                'message': 'No units found in syllabus'
            }
            
        # Extract lesson plans
        lesson_analysis = self.lesson_plan_extractor.extract_lesson_plans(units)
        
        # Identify gaps
        gaps = []
        
        # Check for units without hours
        if lesson_analysis['units_without_hours']:
            gaps.append({
                'type': 'missing_hours',
                'severity': 'high',
                'units': lesson_analysis['units_without_hours'],
                'description': f"{len(lesson_analysis['units_without_hours'])} units missing hour allocation"
            })
            
        # Check for units without teaching methods
        if lesson_analysis['units_without_methods']:
            gaps.append({
                'type': 'missing_methods',
                'severity': 'medium',
                'units': lesson_analysis['units_without_methods'],
                'description': f"{len(lesson_analysis['units_without_methods'])} units without specified teaching methods"
            })
            
        # Check for unbalanced lesson distribution
        distribution = lesson_analysis.get('lesson_distribution', {})
        lessons_per_unit = distribution.get('lessons_per_unit', {})
        if lessons_per_unit:
            lesson_counts = list(lessons_per_unit.values())
            avg_lessons = sum(lesson_counts) / len(lesson_counts)
            
            for unit_num, count in lessons_per_unit.items():
                if count < avg_lessons * 0.5:  # Less than 50% of average
                    gaps.append({
                        'type': 'sparse_unit',
                        'severity': 'medium',
                        'unit_number': unit_num,
                        'lesson_count': count,
                        'average': avg_lessons,
                        'description': f"Unit {unit_num} has significantly fewer lessons ({count}) than average ({avg_lessons:.1f})"
                    })
                    
        lesson_analysis['gaps'] = gaps
        return lesson_analysis
        
    def _analyze_redundancies(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect content redundancies using semantic similarity
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            Redundancy analysis
        """
        return self.redundancy_detector.detect_redundancies(syllabus_data)
