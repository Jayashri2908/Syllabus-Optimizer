"""
NEP 2020 Validator for SCDO
Validates syllabus compliance with National Education Policy 2020
"""

from typing import Dict, List, Any
import yaml
from pathlib import Path
import logging


class NEP2020Validator:
    """Validate syllabus against NEP 2020 guidelines"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.guidelines = self._load_guidelines()
        
    def _load_guidelines(self) -> dict:
        """Load NEP 2020 guidelines from config"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "nep_2020.yaml"
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load NEP 2020 config: {e}")
            return {}
            
    def validate(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate syllabus against NEP 2020 requirements
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            Compliance report with score and gaps
        """
        if not self.guidelines:
            return {'status': 'error', 'message': 'Guidelines not loaded'}
            
        checks = {
            'multidisciplinary': self._check_multidisciplinary(syllabus_data),
            'skill_development': self._check_skill_development(syllabus_data),
            'experiential_learning': self._check_experiential_learning(syllabus_data),
            'assessment_pattern': self._check_assessment_pattern(syllabus_data),
            'technology_integration': self._check_technology(syllabus_data),
            'obe_compliance': self._check_obe(syllabus_data)
        }
        
        # Calculate overall score
        total_score = sum(check['score'] for check in checks.values())
        max_score = len(checks) * 100
        compliance_percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Determine compliance level
        scoring = self.guidelines.get('compliance_scoring', {})
        if compliance_percentage >= scoring.get('excellent', 90):
            level = 'Excellent'
        elif compliance_percentage >= scoring.get('good', 75):
            level = 'Good'
        elif compliance_percentage >= scoring.get('satisfactory', 60):
            level = 'Satisfactory'
        else:
            level = 'Needs Improvement'
            
        return {
            'status': 'success',
            'compliance_percentage': round(compliance_percentage, 1),
            'compliance_level': level,
            'detailed_checks': checks,
            'summary': self._generate_summary(checks)
        }
        
    def _check_multidisciplinary(self, syllabus_data: Dict) -> Dict:
        """Check for multidisciplinary content"""
        guidelines = self.guidelines.get('nep_2020_guidelines', {}).get('multidisciplinary', {})
        min_percentage = guidelines.get('min_percentage', 10)
        
        # Simple heuristic: check for cross-domain keywords
        units = syllabus_data.get('units', [])
        cross_domain_keywords = ['interdisciplinary', 'multidisciplinary', 'cross-domain', 
                                 'holistic', 'integrated', 'ethics', 'society', 'environment']
        
        total_topics = sum(len(unit.get('topics', [])) for unit in units)
        cross_domain_count = 0
        
        for unit in units:
            for topic in unit.get('topics', []):
                topic_text = topic.get('name', '') if isinstance(topic, dict) else str(topic)
                if any(keyword in topic_text.lower() for keyword in cross_domain_keywords):
                    cross_domain_count += 1
                    
        percentage = (cross_domain_count / total_topics * 100) if total_topics > 0 else 0
        compliant = percentage >= min_percentage
        
        return {
            'compliant': compliant,
            'score': 100 if compliant else max(0, percentage / min_percentage * 100),
            'current': round(percentage, 1),
            'required': min_percentage,
            'message': f"{'✓' if compliant else '✗'} Multidisciplinary content: {percentage:.1f}% (required: {min_percentage}%)"
        }
        
    def _check_skill_development(self, syllabus_data: Dict) -> Dict:
        """Check for skill development focus"""
        guidelines = self.guidelines.get('nep_2020_guidelines', {}).get('skill_development', {})
        required_skills = guidelines.get('required_skills', [])
        min_skill_outcomes = guidelines.get('min_skill_outcomes', 2)
        
        outcomes = syllabus_data.get('learning_outcomes', [])
        skill_keywords = ['skill', 'ability', 'competency', 'proficiency', 'capability']
        
        skill_outcome_count = 0
        for outcome in outcomes:
            outcome_text = outcome if isinstance(outcome, str) else outcome.get('description', '')
            if any(keyword in outcome_text.lower() for keyword in skill_keywords):
                skill_outcome_count += 1
                
        compliant = skill_outcome_count >= min_skill_outcomes
        
        return {
            'compliant': compliant,
            'score': min(100, (skill_outcome_count / min_skill_outcomes) * 100),
            'current': skill_outcome_count,
            'required': min_skill_outcomes,
            'message': f"{'✓' if compliant else '✗'} Skill-based outcomes: {skill_outcome_count} (required: {min_skill_outcomes})"
        }
        
    def _check_experiential_learning(self, syllabus_data: Dict) -> Dict:
        """Check for experiential learning components"""
        guidelines = self.guidelines.get('nep_2020_guidelines', {}).get('experiential_learning', {})
        required_components = guidelines.get('required_components', [])
        min_components = guidelines.get('min_components', 1)
        
        # Check units and topics for experiential keywords
        units = syllabus_data.get('units', [])
        all_text = " ".join([
            unit.get('title', '') + " " + " ".join([t.get('name', '') if isinstance(t, dict) else str(t) for t in unit.get('topics', [])])
            for unit in units
        ]).lower()
        
        found_components = []
        for component in required_components:
            if component.replace('_', ' ') in all_text or component.replace('_', '-') in all_text:
                found_components.append(component)
                
        compliant = len(found_components) >= min_components
        
        return {
            'compliant': compliant,
            'score': min(100, (len(found_components) / min_components) * 100),
            'found': found_components,
            'required_count': min_components,
            'message': f"{'✓' if compliant else '✗'} Experiential learning: {len(found_components)} components found (required: {min_components})"
        }
        
    def _check_assessment_pattern(self, syllabus_data: Dict) -> Dict:
        """Check assessment pattern alignment"""
        guidelines = self.guidelines.get('nep_2020_guidelines', {}).get('assessment_pattern', {})
        formative_min = guidelines.get('formative_min', 30)
        formative_max = guidelines.get('formative_max', 50)
        
        assessment = syllabus_data.get('assessment_pattern', {})
        
        # Try to identify formative vs summative
        formative_keys = ['internal', 'continuous', 'assignment', 'quiz', 'lab', 'project']
        formative_total = sum(assessment.get(key, 0) for key in formative_keys if key in assessment)
        
        compliant = formative_min <= formative_total <= formative_max
        
        return {
            'compliant': compliant,
            'score': 100 if compliant else 70,
            'formative_percentage': formative_total,
            'required_range': f"{formative_min}-{formative_max}%",
            'message': f"{'✓' if compliant else '✗'} Continuous assessment: {formative_total}% (required: {formative_min}-{formative_max}%)"
       }
        
    def _check_technology(self, syllabus_data: Dict) -> Dict:
        """Check for technology integration"""
        # Check for ICT/technology keywords
        tech_keywords = ['ict', 'technology', 'digital', 'online', 'software', 'tools', 
                        'simulation', 'virtual', 'e-learning', 'computer']
        
        units = syllabus_data.get('units', [])
        all_text = " ".join([
            unit.get('title', '') + " " + " ".join([t.get('name', '') if isinstance(t, dict) else str(t) for t in unit.get('topics', [])])
            for unit in units
        ]).lower()
        
        tech_mentions = sum(1 for keyword in tech_keywords if keyword in all_text)
        compliant = tech_mentions > 0
        
        return {
            'compliant': compliant,
            'score': min(100, tech_mentions * 20),
            'mentions': tech_mentions,
            'message': f"{'✓' if compliant else '✗'} Technology integration: {'Present' if compliant else 'Not found'}"
        }
        
    def _check_obe(self, syllabus_data: Dict) -> Dict:
        """Check OBE compliance"""
        outcomes = syllabus_data.get('learning_outcomes', [])
        co_po_mapping = syllabus_data.get('co_po_mapping', {})
        
        has_outcomes = len(outcomes) >= 4
        has_mapping = len(co_po_mapping) > 0
        
        compliant = has_outcomes and has_mapping
        score = 0
        if has_outcomes:
            score += 50
        if has_mapping:
            score += 50
            
        return {
            'compliant': compliant,
            'score': score,
            'has_outcomes': has_outcomes,
            'has_mapping': has_mapping,
            'message': f"{'✓' if compliant else '✗'} OBE: Outcomes={has_outcomes}, CO-PO Mapping={has_mapping}"
        }
        
    def _generate_summary(self, checks: Dict) -> List[str]:
        """Generate summary recommendations"""
        summary = []
        
        for check_name, result in checks.items():
            if not result.get('compliant', False):
                check_title = check_name.replace('_', ' ').title()
                summary.append(f"Improve {check_title}: {result.get('message', '')}")
                
        if not summary:
            summary.append("✓ Syllabus meets all NEP 2020 guidelines")
            
        return summary
