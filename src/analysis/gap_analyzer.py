"""
Gap Analyzer for SCDO
Identifies gaps and issues in syllabus content
"""

from typing import Dict, List, Any
import yaml
from pathlib import Path
import logging

from ..utils.text_processing import TextProcessor


class GapAnalyzer:
    """Analyze syllabus for gaps and improvement opportunities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        self.bloom_taxonomy = self._load_bloom_taxonomy()
        self.accreditation_standards = self._load_accreditation_standards()
        
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
        
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Bloom's coverage recommendations
        bloom_gaps = report['bloom_coverage'].get('gaps', [])
        for gap in bloom_gaps:
            level = gap['level']
            issue = gap['issue']
            if issue == 'underrepresented':
                recommendations.append(
                    f"Add more learning outcomes at '{level}' level to meet recommended distribution"
                )
            elif issue == 'overrepresented':
                recommendations.append(
                    f"Consider reducing '{level}' level outcomes and diversifying cognitive levels"
                )
                
        # CO-PO mapping recommendations
        co_po_gaps = report['co_po_mapping_gaps'].get('gaps', [])
        if co_po_gaps:
            recommendations.append(
                "Complete CO-PO mapping for all course outcomes to meet accreditation requirements"
            )
            
        # Assessment recommendations
        assessment_gaps = report['assessment_gaps'].get('gaps', [])
        for gap in assessment_gaps:
            if gap['type'] == 'total_mismatch':
                recommendations.append(
                    "Adjust assessment component weightages to total 100%"
                )
            elif gap['type'] == 'missing_component':
                recommendations.append(
                    f"Add {gap['component']} assessment component"
                )
                
        # Content recommendations
        content_gaps = report['content_gaps'].get('gaps', [])
        for gap in content_gaps:
            if gap['type'] == 'insufficient_references':
                recommendations.append(
                    "Add more reference materials (textbooks, research papers, online resources)"
                )
            elif gap['type'] == 'missing_hours':
                recommendations.append(
                    "Specify contact hours for each unit"
                )
                
        return recommendations
