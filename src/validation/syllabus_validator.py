"""
Syllabus Quality Validator
Validates generated syllabi for quality and completeness
"""

from typing import Dict, List, Any
import re


class SyllabusValidator:
    """Validate syllabus quality and provide scores"""
    
    # Bloom's taxonomy verbs for validation
    BLOOM_VERBS = {
        'remember': ['define', 'label', 'list', 'name', 'recall', 'recognize', 'state'],
        'understand': ['describe', 'explain', 'summarize', 'interpret', 'classify', 'identify', 'infer', 'predict', 'outline'],
        'apply': ['apply', 'calculate', 'execute', 'implement', 'solve', 'use', 'demonstrate', 'operate', 'compute'],
        'analyze': ['analyze', 'compare', 'contrast', 'differentiate', 'examine', 'investigate', 'categorize', 'deconstruct', 'distinguish'],
        'evaluate': ['evaluate', 'assess', 'critique', 'judge', 'justify', 'rank', 'recommend', 'validate', 'choose', 'select', 'decide'],
        'create': ['create', 'design', 'develop', 'formulate', 'construct', 'compose', 'generate', 'plan', 'produce', 'devise']
    }
    
    def validate(self, syllabus: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate syllabus and return quality score
        
        Returns:
            Dict with score, issues, and recommendations
        """
        issues = []
        score = 100
        recommendations = []
        
        # Check 1: Learning outcomes exist and have Bloom's verbs
        outcomes = syllabus.get('learning_outcomes', [])
        if not outcomes:
            issues.append("No learning outcomes found")
            score -= 30
        else:
            bloom_counts = {'remember': 0, 'understand': 0, 'apply': 0, 
                          'analyze': 0, 'evaluate': 0, 'create': 0}
            
            for outcome in outcomes:
                description = outcome.get('description', '').lower()
                has_bloom_verb = False
                
                HIGHEST_FIRST = ['create', 'evaluate', 'analyze', 'apply', 'understand', 'remember']
                for level in HIGHEST_FIRST:
                    verbs = self.BLOOM_VERBS.get(level, [])
                    if any(description.startswith(verb) for verb in verbs):
                        bloom_counts[level] += 1
                        has_bloom_verb = True
                        break
                
                if not has_bloom_verb:
                    issues.append(f"Outcome '{outcome.get('code')}' lacks Bloom's taxonomy verb")
                    score -= 5
            
            # Check Bloom's distribution
            if bloom_counts.get('create', 0) == 0 and bloom_counts.get('evaluate', 0) == 0:
                issues.append("No higher-order thinking outcomes (Evaluate/Create level)")
                score -= 10
                recommendations.append("Add at least one Create or Evaluate level outcome")
            
            if bloom_counts.get('remember', 0) > len(outcomes) / 2:
                issues.append("Too many Remember-level outcomes (lower-order thinking)")
                score -= 5
                recommendations.append("Balance with more Apply/Analyze/Create outcomes")
        
        # Check 2: Units coverage
        units = syllabus.get('units', [])
        if not units:
            issues.append("No units/topics found")
            score -= 25
        else:
            # Check unit completeness
            for unit in units:
                if not unit.get('topics') or len(unit.get('topics', [])) < 3:
                    issues.append(f"Unit {unit.get('unit_number')} has too few topics")
                    score -= 5
                    
                if not unit.get('title') or len(unit.get('title', '')) < 10:
                    issues.append(f"Unit {unit.get('unit_number')} has vague title")
                    score -= 3
        
        # Check 3: Hour distribution
        if 'credits' in syllabus:
            expected_hours = self._calculate_expected_hours(syllabus['credits'])
            actual_hours = sum(u.get('hours', 0) for u in units)
            
            if abs(expected_hours - actual_hours) > 10:
                issues.append(f"Hour mismatch: expected ~{expected_hours}, got {actual_hours}")
                score -= 8
                recommendations.append(f"Adjust unit hours to total {expected_hours}")
        
        # Check 4: Essential components
        required_fields = ['course_title', 'course_code', 'objectives']
        for field in required_fields:
            if not syllabus.get(field):
                issues.append(f"Missing required field: {field}")
                score -= 10
        
        # Check 5: Objectives quality
        objectives = syllabus.get('objectives', [])
        if objectives:
            for obj in objectives:
                if len(obj) < 20:
                    issues.append("Objective is too brief/vague")
                    score -= 3
        
        return {
            'score': max(0, score),
            'grade': self._get_grade(score),
            'issues': issues,
            'recommendations': recommendations,
            'passed': score >= 70,
            'bloom_distribution': self._count_bloom_levels(outcomes)
        }
    
    def _calculate_expected_hours(self, credits: str) -> int:
        """Calculate expected contact hours from credits"""
        try:
            parts = credits.split('-')
            l = int(parts[0])  # Lecture
            t = int(parts[1]) if len(parts) > 1 else 0  # Tutorial
            return (l + t) * 15  # 15 weeks semester
        except:
            return 45  # Default
    
    def _count_bloom_levels(self, outcomes: List[Dict]) -> Dict[str, int]:
        """Count outcomes by Bloom's level"""
        counts = {'remember': 0, 'understand': 0, 'apply': 0,
                 'analyze': 0, 'evaluate': 0, 'create': 0}
        
        for outcome in outcomes:
            bloom_level = outcome.get('bloom_level', '').lower()
            if bloom_level in counts:
                counts[bloom_level] += 1
        
        return counts
    
    def _get_grade(self, score: int) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return 'A (Excellent)'
        elif score >= 80:
            return 'B (Good)'
        elif score >= 70:
            return 'C (Satisfactory)'
        elif score >= 60:
            return 'D (Needs Improvement)'
        else:
            return 'F (Poor Quality)'
