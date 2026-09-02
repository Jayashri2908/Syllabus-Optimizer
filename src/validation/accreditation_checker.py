"""
Accreditation Checker for SCDO
Validates NBA and NAAC compliance
"""

from typing import Dict, List, Any
import yaml
from pathlib import Path
import logging


class AccreditationChecker:
    """Check NBA and NAAC accreditation compliance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load accreditation configuration"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "accreditation.yaml"
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load accreditation config: {e}")
            return {}
            
    def check_nba_compliance(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check NBA (National Board of Accreditation) compliance
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            NBA compliance report
        """
        checks = {
            'po_mapping': self._check_po_mapping(syllabus_data),
            'assessment_pattern': self._check_nba_assessment(syllabus_data),
            'co_completeness': self._check_co_completeness(syllabus_data),
            'lab_component': self._check_lab_component(syllabus_data)
        }
        
        # Calculate compliance score
        total_score = sum(check['score'] for check in checks.values())
        max_score = len(checks) * 100
        compliance_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            'status': 'success',
            'compliance_percentage': round(compliance_percentage, 1),
            'compliance_level': self._get_compliance_level(compliance_percentage),
            'checks': checks,
            'recommendations': self._generate_nba_recommendations(checks)
        }
        
    def check_naac_compliance(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check NAAC (National Assessment and Accreditation Council) compliance
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            NAAC compliance report
        """
        checks = {
            'learner_centric': self._check_learner_centric(syllabus_data),
            'ict_integration': self._check_ict_integration(syllabus_data),
            'quality_metrics': self._check_quality_metrics(syllabus_data)
        }
        
        total_score = sum(check['score'] for check in checks.values())
        max_score = len(checks) * 100
        compliance_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            'status': 'success',
            'compliance_percentage': round(compliance_percentage, 1),
            'compliance_level': self._get_compliance_level(compliance_percentage),
            'checks': checks,
            'recommendations': self._generate_naac_recommendations(checks)
        }
        
    def _check_po_mapping(self, syllabus_data: Dict) -> Dict:
        """Check if all 12 POs are mapped"""
        co_po_mapping = syllabus_data.get('co_po_mapping', {})
        
        # Expected 12 POs for engineering (NBA standard)
        expected_pos = [f'PO{i}' for i in range(1, 13)]
        
        # Collect all POs from mappings
        all_mapped_pos = set()
        for co, po_dict in co_po_mapping.items():
            all_mapped_pos.update(po_dict.keys())
            
        mapped_count = len(all_mapped_pos.intersection(expected_pos))
        coverage_percentage = (mapped_count / 12 * 100)
        
        compliant = coverage_percentage >= 80  # At least 80% PO coverage
        
        return {
            'compliant': compliant,
            'score': coverage_percentage,
            'mapped_pos': mapped_count,
            'total_pos': 12,
            'coverage': round(coverage_percentage, 1),
            'message': f"{'✓' if compliant else '✗'} PO Coverage: {mapped_count}/12 POs ({coverage_percentage:.0f}%)"
        }
        
    def _check_nba_assessment(self, syllabus_data: Dict) -> Dict:
        """Check NBA-recommended assessment pattern (40% IA + 60% ESE)"""
        assessment = syllabus_data.get('assessment_pattern', {})
        
        internal_total = 0
        external_total = 0
        
        if isinstance(assessment, dict):
            internal = assessment.get('internal', {})
            external = assessment.get('external', {})
            
            if isinstance(internal, dict):
                internal_total = internal.get('weightage', 0)
                if internal_total == 0 and isinstance(internal.get('components'), dict):
                    internal_total = sum(internal['components'].values())
            elif isinstance(internal, (int, float)):
                internal_total = internal
                
            if isinstance(external, dict):
                external_total = external.get('weightage', 0)
                if external_total == 0 and isinstance(external.get('components'), dict):
                    external_total = sum(external['components'].values())
            elif isinstance(external, (int, float)):
                external_total = external
        
        if internal_total == 0 and external_total == 0:
            internal_keys = ['internal', 'continuous', 'ia', 'assignment', 'quiz']
            external_keys = ['external', 'ese', 'end_semester', 'final']
            internal_total = sum(assessment.get(key, 0) for key in internal_keys if key in assessment and isinstance(assessment.get(key), (int, float)))
            external_total = sum(assessment.get(key, 0) for key in external_keys if key in assessment and isinstance(assessment.get(key), (int, float)))
        
        ia_compliant = 35 <= internal_total <= 45
        ese_compliant = 55 <= external_total <= 65
        
        compliant = ia_compliant and ese_compliant
        score = 0
        if ia_compliant:
            score += 50
        if ese_compliant:
            score += 50
            
        return {
            'compliant': compliant,
            'score': score,
            'internal_assessment': internal_total,
            'external_assessment': external_total,
            'recommended': '40% IA + 60% ESE',
            'message': f"{'✓' if compliant else '✗'} Assessment: IA={internal_total}%, ESE={external_total}% (NBA: 40%+60%)"
        }
        
    def _check_co_completeness(self, syllabus_data: Dict) -> Dict:
        """Check if course outcomes are complete and well-defined"""
        outcomes = syllabus_data.get('learning_outcomes', [])
        
        # NBA recommends 4-6 COs
        count = len(outcomes)
        optimal_count = 4 <= count <= 6
        
        # Check if outcomes have Bloom's levels
        with_blooms = 0
        for outcome in outcomes:
            if isinstance(outcome, dict):
                if outcome.get('bloom_level'):
                    with_blooms += 1
            elif isinstance(outcome, str):
                # Check for Bloom's verbs
                bloom_verbs = ['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create']
                if any(verb in outcome.lower() for verb in bloom_verbs):
                    with_blooms += 1
                    
        blooms_percentage = (with_blooms / count * 100) if count > 0 else 0
        
        compliant = optimal_count and blooms_percentage >= 80
        score = 0
        if optimal_count:
            score += 50
        if blooms_percentage >= 80:
            score += 50
            
        return {
            'compliant': compliant,
            'score': score,
            'co_count': count,
            'optimal_range': '4-6',
            'blooms_coverage': round(blooms_percentage, 1),
            'message': f"{'✓' if compliant else '✗'} COs: {count} outcomes, {blooms_percentage:.0f}% with Bloom's levels"
        }
        
    def _check_lab_component(self, syllabus_data: Dict) -> Dict:
        """Check for practical/lab component"""
        units = syllabus_data.get('units', [])
        
        # Check for lab keywords
        lab_keywords = ['lab', 'laboratory', 'practical', 'experiment', 'hands-on']
        
        all_text = " ".join([
            unit.get('title', '') + " " + " ".join([t.get('name', '') if isinstance(t, dict) else str(t) for t in unit.get('topics', [])])
            for unit in units
        ]).lower()
        
        has_lab = any(keyword in all_text for keyword in lab_keywords)
        
        # Check for lab hours
        total_hours = sum(unit.get('hours', 0) for unit in units)
        lab_hours = 0
        for unit in units:
            topics_text = " ".join([t.get('name', '') if isinstance(t, dict) else str(t) for t in unit.get('topics', [])])
            unit_text = (unit.get('title', '') + " " + topics_text).lower()
            if any(keyword in unit_text for keyword in lab_keywords):
                lab_hours += unit.get('hours', 0)
                
        lab_percentage = (lab_hours / total_hours * 100) if total_hours > 0 else 0
        
        # For practical courses, expect >= 40% lab hours
        compliant = has_lab and lab_percentage >= 20  # At least some lab component
        
        return {
            'compliant': compliant,
            'score': min(100, lab_percentage * 2.5) if has_lab else 0,
            'has_lab': has_lab,
            'lab_hours': lab_hours,
            'total_hours': total_hours,
            'lab_percentage': round(lab_percentage, 1),
            'message': f"{'✓' if compliant else '✗'} Lab Component: {'Present' if has_lab else 'Not found'} ({lab_percentage:.0f}% of total hours)"
        }
        
    def _check_learner_centric(self, syllabus_data: Dict) -> Dict:
        """Check for learner-centric approaches (NAAC)"""
        outcomes = syllabus_data.get('learning_outcomes', [])
        
        # Check for student-centric language
        student_centric_keywords = ['student', 'learner', 'will be able to', 'can demonstrate']
        
        outcomes_text = " ".join([
            outcome if isinstance(outcome, str) else outcome.get('description', '')
            for outcome in outcomes
        ]).lower()
        
        is_learner_centric = any(keyword in outcomes_text for keyword in student_centric_keywords)
        
        return {
            'compliant': is_learner_centric,
            'score': 100 if is_learner_centric else 50,
            'message': f"{'✓' if is_learner_centric else '✗'} Learner-centric outcomes: {'Present' if is_learner_centric else 'Not found'}"
        }
        
    def _check_ict_integration(self, syllabus_data: Dict) -> Dict:
        """Check for ICT integration (NAAC)"""
        units = syllabus_data.get('units', [])
        
        ict_keywords = ['ict', 'technology', 'digital', 'computer', 'software', 'online', 'e-learning']
        
        all_text = " ".join([
            unit.get('title', '') + " " + " ".join([t.get('name', '') if isinstance(t, dict) else str(t) for t in unit.get('topics', [])])
            for unit in units
        ]).lower()
        
        ict_mentions = sum(1 for keyword in ict_keywords if keyword in all_text)
        has_ict = ict_mentions > 0
        
        return {
            'compliant': has_ict,
            'score': min(100, ict_mentions * 33),
            'mentions': ict_mentions,
            'message': f"{'✓' if has_ict else '✗'} ICT Integration: {'Present' if has_ict else 'Not found'}"
        }
        
    def _check_quality_metrics(self, syllabus_data: Dict) -> Dict:
        """Check for quality assurance metrics (NAAC)"""
        # Check for CO-PO mapping (quality metric)
        has_mapping = len(syllabus_data.get('co_po_mapping', {})) > 0
        
        # Check for assessment diversity
        assessment = syllabus_data.get('assessment_pattern', {})
        diverse_assessment = len(assessment) >= 2
        
        compliant = has_mapping and diverse_assessment
        
        return {
            'compliant': compliant,
            'score': (50 if has_mapping else 0) + (50 if diverse_assessment else 0),
            'has_co_po_mapping': has_mapping,
            'diverse_assessment': diverse_assessment,
            'message': f"{'✓' if compliant else '✗'} Quality Metrics: CO-PO={has_mapping}, Diverse Assessment={diverse_assessment}"
        }
        
    def _get_compliance_level(self, percentage: float) -> str:
        """Get compliance level from percentage"""
        if percentage >= 90:
            return 'Excellent'
        elif percentage >= 75:
            return 'Good'
        elif percentage >= 60:
            return 'Satisfactory'
        else:
            return 'Needs Improvement'
            
    def _generate_nba_recommendations(self, checks: Dict) -> List[str]:
        """Generate NBA-specific recommendations"""
        recommendations = []
        
        for check_name, result in checks.items():
            if not result.get('compliant', False):
                if check_name == 'po_mapping':
                    recommendations.append("Map all 12 Program Outcomes (PO1-PO12) to Course Outcomes")
                elif check_name == 'assessment_pattern':
                    recommendations.append("Adjust assessment to follow NBA pattern: 40% Internal + 60% End Semester")
                elif check_name == 'co_completeness':
                    recommendations.append("Define 4-6 clear Course Outcomes with Bloom's taxonomy levels")
                elif check_name == 'lab_component':
                    recommendations.append("Include practical/lab component with adequate hours")
                    
        return recommendations if recommendations else ["✓ Meets all NBA requirements"]
        
    def _generate_naac_recommendations(self, checks: Dict) -> List[str]:
        """Generate NAAC-specific recommendations"""
        recommendations = []
        
        for check_name, result in checks.items():
            if not result.get('compliant', False):
                if check_name == 'learner_centric':
                    recommendations.append("Rewrite outcomes in learner-centric language (e.g., 'Students will be able to...')")
                elif check_name == 'ict_integration':
                    recommendations.append("Include ICT/technology integration in course content")
                elif check_name == 'quality_metrics':
                    recommendations.append("Implement CO-PO mapping and diverse assessment methods")
                    
        return recommendations if recommendations else ["✓ Meets all NAAC requirements"]
