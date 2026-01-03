"""
Instructional Strategy Recommender for SCDO
Recommends pedagogy approaches and assessment types based on course characteristics
"""

from typing import Dict, List, Any
import logging


class InstructionalStrategyRecommender:
    """Recommend instructional strategies based on course type and domain"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_strategy_templates()
        
    def _load_strategy_templates(self):
        """Load pedagogy and assessment templates"""
        
        # Pedagogy approaches with characteristics
        self.pedagogies = {
            'project_based_learning': {
                'name': 'Project-Based Learning (PBL)',
                'description': 'Students learn by actively engaging in real-world projects',
                'best_for': ['engineering', 'computer_science', 'architecture', 'design'],
                'course_types': ['practical', 'application-heavy', 'design'],
                'bloom_levels': ['Apply', 'Analyze', 'Evaluate', 'Create'],
                'activities': [
                    'Define real-world problem statements',
                    'Form teams for collaborative work',
                    'Research and prototype solutions',
                    'Iterative development and testing',
                    'Present final deliverables'
                ],
                'assessments': ['project_deliverables', 'presentations', 'peer_evaluation', 'prototype_demo'],
                'duration': 'Multi-week projects',
                'class_structure': 'Weekly progress reviews + independent work'
            },
            'flipped_classroom': {
                'name': 'Flipped Classroom',
                'description': 'Content delivery before class, active learning during class',
                'best_for': ['all_domains'],
                'course_types': ['theory-heavy', 'conceptual', 'foundation'],
                'bloom_levels': ['Remember', 'Understand', 'Apply', 'Analyze'],
                'activities': [
                    'Pre-class video lectures or readings',
                    'In-class problem-solving sessions',
                    'Group discussions and debates',
                    'Hands-on activities and experiments',
                    'Peer teaching and Q&A'
                ],
                'assessments': ['quizzes', 'in_class_activities', 'group_work', 'reflections'],
                'duration': 'Weekly cycle',
                'class_structure': 'Pre-class content + In-class application'
            },
            'case_based_learning': {
                'name': 'Case-Based Learning',
                'description': 'Learn through analysis of real-world scenarios and cases',
                'best_for': ['business', 'management', 'medicine', 'law', 'engineering'],
                'course_types': ['decision-making', 'analysis-heavy', 'professional'],
                'bloom_levels': ['Understand', 'Apply', 'Analyze', 'Evaluate'],
                'activities': [
                    'Case study distribution and reading',
                    'Individual case analysis',
                    'Group discussion and debate',
                    'Solution development',
                    'Presentation of recommendations'
                ],
                'assessments': ['case_analysis_reports', 'presentations', 'class_discussions', 'decision_matrices'],
                'duration': '1-2 cases per unit',
                'class_structure': 'Case introduction + Group work + Discussion'
            },
            'laboratory_integrated': {
                'name': 'Laboratory-Integrated Teaching',
                'description': 'Theory concepts immediately applied in lab experiments',
                'best_for': ['science', 'engineering', 'computer_science'],
                'course_types': ['experimental', 'hands-on', 'technical'],
                'bloom_levels': ['Apply', 'Analyze', 'Evaluate'],
                'activities': [
                    'Pre-lab theory sessions',
                    'Experimental design and setup',
                    'Data collection and observation',
                    'Analysis and interpretation',
                    'Lab report writing'
                ],
                'assessments': ['lab_reports', 'practical_exams', 'viva_voce', 'lab_notebooks'],
                'duration': 'Weekly lab sessions',
                'class_structure': 'Theory lecture + Lab session'
            },
            'inquiry_based_learning': {
                'name': 'Inquiry-Based Learning',
                'description': 'Students develop understanding through investigation',
                'best_for': ['science', 'mathematics', 'research'],
                'course_types': ['research-oriented', 'exploratory', 'advanced'],
                'bloom_levels': ['Analyze', 'Evaluate', 'Create'],
                'activities': [
                    'Formulate research questions',
                    'Literature review and exploration',
                    'Design investigations',
                    'Collect and analyze evidence',
                    'Draw conclusions and present findings'
                ],
                'assessments': ['research_papers', 'presentations', 'posters', 'peer_review'],
                'duration': 'Semester-long investigations',
                'class_structure': 'Guided inquiry sessions + Independent research'
            },
            'collaborative_learning': {
                'name': 'Collaborative Learning',
                'description': 'Students work together to achieve learning goals',
                'best_for': ['all_domains'],
                'course_types': ['team-based', 'interdisciplinary', 'soft-skills'],
                'bloom_levels': ['Apply', 'Analyze', 'Evaluate', 'Create'],
                'activities': [
                    'Team formation and norming',
                    'Collaborative problem-solving',
                    'Peer teaching and learning',
                    'Group presentations',
                    'Collective knowledge building'
                ],
                'assessments': ['group_projects', 'peer_evaluation', 'team_presentations', 'reflections'],
                'duration': 'Ongoing throughout course',
                'class_structure': 'Mini-lecture + Team activities'
            },
            'problem_based_learning': {
                'name': 'Problem-Based Learning (PBL)',
                'description': 'Learning driven by solving complex problems',
                'best_for': ['medicine', 'engineering', 'business'],
                'course_types': ['professional', 'applied', 'clinical'],
                'bloom_levels': ['Apply', 'Analyze', 'Evaluate', 'Create'],
                'activities': [
                    'Problem scenario presentation',
                    'Identify knowledge gaps',
                    'Self-directed learning',
                    'Group collaboration',
                    'Solution synthesis and presentation'
                ],
                'assessments': ['problem_solutions', 'learning_portfolios', 'presentations', 'self_assessment'],
                'duration': 'Multi-week problems',
                'class_structure': 'Problem introduction + Self-study + Discussion'
            }
        }
        
        # Assessment types with details
        self.assessment_types = {
            'quizzes': {
                'name': 'Quizzes',
                'type': 'Formative',
                'frequency': 'Weekly/Bi-weekly',
                'weightage': '5-10%',
                'best_for': ['Remember', 'Understand'],
                'format': 'MCQ, Short answer, Fill-in-blanks'
            },
            'case_analysis_reports': {
                'name': 'Case Analysis Reports',
                'type': 'Summative',
                'frequency': '2-3 per semester',
                'weightage': '15-20%',
                'best_for': ['Analyze', 'Evaluate'],
                'format': 'Written report with analysis and recommendations'
            },
            'presentations': {
                'name': 'Presentations',
                'type': 'Both',
                'frequency': '1-2 per semester',
                'weightage': '10-15%',
                'best_for': ['Create', 'Evaluate'],
                'format': 'Individual or group presentation with Q&A'
            },
            'lab_reports': {
                'name': 'Laboratory Reports',
                'type': 'Formative',
                'frequency': 'Weekly',
                'weightage': '10-15%',
                'best_for': ['Apply', 'Analyze'],
                'format': 'Structured reports with methodology and results'
            },
            'project_deliverables': {
                'name': 'Project Deliverables',
                'type': 'Summative',
                'frequency': '1 major per semester',
                'weightage': '20-30%',
                'best_for': ['Create', 'Evaluate'],
                'format': 'Working prototype + documentation + presentation'
            },
            'exams': {
                'name': 'Written Exams',
                'type': 'Summative',
                'frequency': 'Midterm + Final',
                'weightage': '50-70%',
                'best_for': ['Remember', 'Understand', 'Apply', 'Analyze'],
                'format': 'Mix of MCQ, short answer, and long answer questions'
            },
            'peer_evaluation': {
                'name': 'Peer Evaluation',
                'type': 'Formative',
                'frequency': 'After group activities',
                'weightage': '5-10%',
                'best_for': ['Evaluate'],
                'format': 'Structured rubrics for evaluating peers'
            },
            'portfolios': {
                'name': 'Learning Portfolios',
                'type': 'Both',
                'frequency': 'Continuous',
                'weightage': '10-15%',
                'best_for': ['Create', 'Evaluate'],
                'format': 'Collection of work with reflections'
            },
            'practical_exams': {
                'name': 'Practical Exams',
                'type': 'Summative',
                'frequency': 'End of semester',
                'weightage': '20-30%',
                'best_for': ['Apply', 'Analyze'],
                'format': 'Hands-on demonstration of skills'
            }
        }
        
    def recommend_strategies(
        self,
        course_title: str,
        domain: str,
        bloom_distribution: Dict[str, int],
        course_type: str = 'mixed',
        has_lab: bool = False
    ) -> Dict[str, Any]:
        """
        Recommend instructional strategies based on course characteristics
        
        Args:
            course_title: Course title
            domain: Academic domain
            bloom_distribution: Distribution of Bloom's levels
            course_type: Type of course (theory/practical/mixed)
            has_lab: Whether course has lab component
            
        Returns:
            Recommended strategies with implementation details
        """
        
        # Determine dominant Bloom's levels
        dominant_levels = self._get_dominant_bloom_levels(bloom_distribution)
        
        # Score each pedagogy
        pedagogy_scores = {}
        for ped_key, ped_data in self.pedagogies.items():
            score = self._score_pedagogy(
                ped_data, domain, dominant_levels, course_type, has_lab
            )
            if score > 0:
                pedagogy_scores[ped_key] = score
                
        # Get top 3 pedagogies
        top_pedagogies = sorted(
            pedagogy_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Recommend assessment types
        recommended_assessments = self._recommend_assessments(
            [self.pedagogies[p[0]] for p in top_pedagogies],
            dominant_levels
        )
        
        return {
            'recommended_pedagogies': [
                {
                    'pedagogy': self.pedagogies[ped[0]]['name'],
                    'score': ped[1],
                    'description': self.pedagogies[ped[0]]['description'],
                    'activities': self.pedagogies[ped[0]]['activities'],
                    'class_structure': self.pedagogies[ped[0]]['class_structure'],
                    'duration': self.pedagogies[ped[0]]['duration'],
                    'rationale': self._generate_rationale(ped[0], domain, dominant_levels)
                }
                for ped in top_pedagogies
            ],
            'recommended_assessments': recommended_assessments,
            'implementation_plan': self._generate_implementation_plan(top_pedagogies[0][0]),
            'bloom_alignment': {
                'dominant_levels': dominant_levels,
                'distribution': bloom_distribution
            }
        }
        
    def _get_dominant_bloom_levels(self, bloom_dist: Dict[str, int]) -> List[str]:
        """Get dominant Bloom's taxonomy levels"""
        if not bloom_dist:
            return ['Apply', 'Understand']
            
        # Get top 2-3 levels by count
        sorted_levels = sorted(
            bloom_dist.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [level[0] for level in sorted_levels[:3] if level[1] > 0]
        
    def _score_pedagogy(
        self,
        pedagogy: Dict,
        domain: str,
        bloom_levels: List[str],
        course_type: str,
        has_lab: bool
    ) -> float:
        """Score pedagogy fit for this course"""
        score = 0.0
        
        # Domain match
        if domain in pedagogy['best_for'] or 'all_domains' in pedagogy['best_for']:
            score += 30
            
        # Bloom's level match
        overlap = len(set(bloom_levels) & set(pedagogy['bloom_levels']))
        score += overlap * 15
        
        # Course type match
        if course_type in pedagogy['course_types']:
            score += 25
            
        # Lab component bonus
        if has_lab and 'laboratory' in pedagogy['name'].lower():
            score += 30
            
        return score
        
    def _recommend_assessments(
        self,
        pedagogies: List[Dict],
        bloom_levels: List[str]
    ) -> List[Dict]:
        """Recommend assessment types based on pedagogies"""
        
        assessment_scores = {}
        
        # Collect assessments from top pedagogies
        for pedagogy in pedagogies:
            for assess_key in pedagogy['assessments']:
                if assess_key not in assessment_scores:
                    assessment_scores[assess_key] = 0
                assessment_scores[assess_key] += 1
                
        # Add Bloom's level alignment
        for assess_key, assess_data in self.assessment_types.items():
            bloom_match = len(set(bloom_levels) & set(assess_data['best_for']))
            if bloom_match > 0:
                if assess_key not in assessment_scores:
                    assessment_scores[assess_key] = 0
                assessment_scores[assess_key] += bloom_match * 0.5
                
        # Sort and return top assessments
        top_assessments = sorted(
            assessment_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:6]
        
        return [
            {
                'assessment': self.assessment_types[assess[0]]['name'],
                'type': self.assessment_types[assess[0]]['type'],
                'frequency': self.assessment_types[assess[0]]['frequency'],
                'weightage': self.assessment_types[assess[0]]['weightage'],
                'format': self.assessment_types[assess[0]]['format'],
                'bloom_fit': ', '.join(self.assessment_types[assess[0]]['best_for'])
            }
            for assess in top_assessments
            if assess[0] in self.assessment_types
        ]
        
    def _generate_rationale(
        self,
        pedagogy_key: str,
        domain: str,
        bloom_levels: List[str]
    ) -> str:
        """Generate rationale for pedagogy recommendation"""
        
        pedagogy = self.pedagogies[pedagogy_key]
        
        rationale_parts = []
        
        # Domain fit
        if domain in pedagogy['best_for']:
            rationale_parts.append(f"Well-suited for {domain} courses")
            
        # Bloom's alignment
        matching_levels = set(bloom_levels) & set(pedagogy['bloom_levels'])
        if matching_levels:
            rationale_parts.append(
                f"Targets {', '.join(matching_levels)} cognitive levels"
            )
            
        # Unique benefits
        if 'project' in pedagogy_key:
            rationale_parts.append("Develops practical problem-solving skills")
        elif 'case' in pedagogy_key:
            rationale_parts.append("Enhances analytical and decision-making abilities")
        elif 'laboratory' in pedagogy_key:
            rationale_parts.append("Provides hands-on experimental experience")
        elif 'flipped' in pedagogy_key:
            rationale_parts.append("Maximizes active learning during class time")
            
        return ". ".join(rationale_parts) + "."
        
    def _generate_implementation_plan(self, pedagogy_key: str) -> Dict[str, Any]:
        """Generate implementation plan for primary pedagogy"""
        
        pedagogy = self.pedagogies[pedagogy_key]
        
        return {
            'week_1_2': 'Introduction and orientation to pedagogy approach',
            'week_3_6': 'First cycle implementation with guided support',
            'week_7_10': 'Independent application with monitoring',
            'week_11_14': 'Advanced implementation and peer collaboration',
            'week_15': 'Reflection and feedback collection',
            'key_success_factors': [
                'Clear communication of expectations',
                'Provide necessary resources and support',
                'Regular feedback and course corrections',
                'Student engagement and buy-in',
                'Adequate time for activities'
            ],
            'potential_challenges': [
                'Initial student resistance to new format',
                'Time management for complex activities',
                'Assessment alignment with pedagogy',
                'Resource availability'
            ]
        }
