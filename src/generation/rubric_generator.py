"""
Rubric Generator for SCDO
Generates assessment rubrics for different evaluation types
"""

from typing import Dict, List, Any
import logging


class RubricGenerator:
    """Generate assessment rubrics for various evaluation methods"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate_rubrics(
        self,
        assessment_pattern: Dict[str, Any],
        domain: str = "engineering"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive rubrics for all assessment components
        
        Args:
            assessment_pattern: Assessment pattern with components
            domain: Academic domain
            
        Returns:
            Dictionary of rubrics for each assessment type
        """
        rubrics = {}
        
        # Get all assessment components
        internal = assessment_pattern.get('internal', {}).get('components', {})
        external = assessment_pattern.get('external', {}).get('components', {})
        
        # Generate rubric for each component
        all_components = {**internal, **external}
        
        for component_name, weightage in all_components.items():
            if 'exam' in component_name.lower():
                rubrics[component_name] = self._generate_exam_rubric(weightage)
            elif 'assignment' in component_name.lower():
                rubrics[component_name] = self._generate_assignment_rubric(weightage)
            elif 'quiz' in component_name.lower():
                rubrics[component_name] = self._generate_quiz_rubric(weightage)
            elif 'lab' in component_name.lower():
                rubrics[component_name] = self._generate_lab_rubric(weightage)
            elif 'project' in component_name.lower():
                rubrics[component_name] = self._generate_project_rubric(weightage)
            elif 'presentation' in component_name.lower():
                rubrics[component_name] = self._generate_presentation_rubric(weightage)
            elif 'participation' in component_name.lower():
                rubrics[component_name] = self._generate_participation_rubric(weightage)
                
        return rubrics
        
    def _generate_exam_rubric(self, weightage: int) -> Dict[str, Any]:
        """Generate rubric for written exams"""
        return {
            'type': 'exam',
            'total_marks': weightage,
            'criteria': [
                {
                    'name': 'Conceptual Understanding',
                    'weightage': 40,
                    'levels': {
                        'Excellent (90-100%)': 'Demonstrates deep understanding with accurate explanations',
                        'Good (75-89%)': 'Shows good grasp of concepts with minor gaps',
                        'Satisfactory (60-74%)': 'Basic understanding with some misconceptions',
                        'Needs Improvement (<60%)': 'Limited understanding of core concepts'
                    }
                },
                {
                    'name': 'Problem-Solving Skills',
                    'weightage': 35,
                    'levels': {
                        'Excellent (90-100%)': 'Creative solutions with optimal approach',
                        'Good (75-89%)': 'Correct solutions with standard methods',
                        'Satisfactory (60-74%)': 'Partial solutions or inefficient approaches',
                        'Needs Improvement (<60%)': 'Minimal problem-solving ability shown'
                    }
                },
                {
                    'name': 'Application & Analysis',
                    'weightage': 25,
                    'levels': {
                        'Excellent (90-100%)': 'Excellent application of theory to novel scenarios',
                        'Good (75-89%)': 'Good application with logical reasoning',
                        'Satisfactory (60-74%)': 'Basic application with guidance',
                        'Needs Improvement (<60%)': 'Unable to apply concepts effectively'
                    }
                }
            ],
            'instructions': 'Each criterion is evaluated independently and weighted accordingly'
        }
        
    def _generate_assignment_rubric(self, weightage: int) -> Dict[str, Any]:
        """Generate rubric for assignments"""
        return {
            'type': 'assignment',
            'total_marks': weightage,
            'criteria': [
                {
                    'name': 'Content Quality',
                    'weightage': 40,
                    'levels': {
                        'Excellent (9-10)': 'Comprehensive, accurate, well-researched content',
                        'Good (7-8)': 'Good content with minor gaps',
                        'Satisfactory (5-6)': 'Acceptable content, some inaccuracies',
                        'Poor (0-4)': 'Incomplete or inaccurate content'
                    }
                },
                {
                    'name': 'Analysis & Critical Thinking',
                    'weightage': 30,
                    'levels': {
                        'Excellent (9-10)': 'Insightful analysis with original perspectives',
                        'Good (7-8)': 'Good analytical skills demonstrated',
                        'Satisfactory (5-6)': 'Basic analysis present',
                        'Poor (0-4)': 'Minimal analytical effort'
                    }
                },
                {
                    'name': 'Organization & Presentation',
                    'weightage': 20,
                    'levels': {
                        'Excellent (9-10)': 'Exceptionally well-organized and formatted',
                        'Good (7-8)': 'Clear structure and formatting',
                        'Satisfactory (5-6)': 'Adequate organization',
                        'Poor (0-4)': 'Disorganized presentation'
                    }
                },
                {
                    'name': 'Timely Submission',
                    'weightage': 10,
                    'levels': {
                        'On Time (10)': 'Submitted before or on deadline',
                        'Late 1-2 days (7)': '10% penalty',
                        'Late 3-5 days (5)': '20% penalty',
                        'Very Late (0)': 'Not accepted or heavy penalty'
                    }
                }
            ]
        }
        
    def _generate_quiz_rubric(self, weightage: int) -> Dict[str, Any]:
        """Generate rubric for quizzes"""
        return {
            'type': 'quiz',
            'total_marks': weightage,
            'criteria': [
                {
                    'name': 'Accuracy',
                    'weightage': 70,
                    'description': 'Correctness of answers',
                    'levels': {
                        '90-100%': 'All or nearly all answers correct',
                        '75-89%': 'Most answers correct',
                        '60-74%': 'Majority correct with some errors',
                        'Below 60%': 'Significant errors or incomplete'
                    }
                },
                {
                    'name': 'Completeness',
                    'weightage': 30,
                    'description': 'All questions attempted',
                    'levels': {
                        '100%': 'All questions answered',
                        '75-99%': 'Most questions answered',
                        '50-74%': 'Some questions skipped',
                        'Below 50%': 'Many questions unanswered'
                    }
                }
            ],
            'duration': '15-30 minutes',
            'format': 'MCQ, Short Answer, or Fill in the Blanks'
        }
        
    def _generate_lab_rubric(self, weightage: int) -> Dict[str, Any]:
        """Generate rubric for lab work"""
        return {
            'type': 'lab_work',
            'total_marks': weightage,
            'criteria': [
                {
                    'name': 'Experimental Setup',
                    'weightage': 20,
                    'levels': {
                        'Excellent': 'Proper setup with safety considerations',
                        'Good': 'Correct setup with minor issues',
                        'Satisfactory': 'Setup functional but needs improvement',
                        'Poor': 'Incorrect or unsafe setup'
                    }
                },
                {
                    'name': 'Procedure Execution',
                    'weightage': 30,
                    'levels': {
                        'Excellent': 'Follows procedure accurately and efficiently',
                        'Good': 'Generally correct with minor deviations',
                        'Satisfactory': 'Requires guidance, some errors',
                        'Poor': 'Significant procedural errors'
                    }
                },
                {
                    'name': 'Data Collection & Analysis',
                    'weightage': 25,
                    'levels': {
                        'Excellent': 'Accurate data with insightful analysis',
                        'Good': 'Good data collection and reasonable analysis',
                        'Satisfactory': 'Basic data with limited analysis',
                        'Poor': 'Inaccurate data or no analysis'
                    }
                },
                {
                    'name': 'Lab Report',
                    'weightage': 25,
                    'levels': {
                        'Excellent': 'Comprehensive, well-written report',
                        'Good': 'Complete report with minor gaps',
                        'Satisfactory': 'Adequate report, some sections weak',
                        'Poor': 'Incomplete or poorly written'
                    }
                }
            ],
            'submission': 'Lab notebook and typed report required'
        }
        
    def _generate_project_rubric(self, weightage: int) -> Dict[str, Any]:
        """Generate rubric for projects"""
        return {
            'type': 'project',
            'total_marks': weightage,
            'criteria': [
                {
                    'name': 'Innovation & Creativity',
                    'weightage': 25,
                    'levels': {
                        'Exceptional (23-25)': 'Highly innovative with novel approach',
                        'Proficient (19-22)': 'Good creativity demonstrated',
                        'Developing (15-18)': 'Standard approach with some creativity',
                        'Beginning (0-14)': 'Minimal creativity or innovation'
                    }
                },
                {
                    'name': 'Technical Implementation',
                    'weightage': 35,
                    'levels': {
                        'Exceptional (32-35)': 'Excellent technical execution',
                        'Proficient (27-31)': 'Good implementation with best practices',
                        'Developing (21-26)': 'Functional but needs refinement',
                        'Beginning (0-20)': 'Significant technical issues'
                    }
                },
                {
                    'name': 'Documentation',
                    'weightage': 20,
                    'levels': {
                        'Exceptional (18-20)': 'Comprehensive, professional documentation',
                        'Proficient (15-17)': 'Good documentation coverage',
                        'Developing (11-14)': 'Basic documentation present',
                        'Beginning (0-10)': 'Minimal or missing documentation'
                    }
                },
                {
                    'name': 'Team Collaboration',
                    'weightage': 20,
                    'levels': {
                        'Exceptional (18-20)': 'Excellent teamwork and equal contribution',
                        'Proficient (15-17)': 'Good collaboration evident',
                        'Developing (11-14)': 'Adequate teamwork with some issues',
                        'Beginning (0-10)': 'Poor collaboration or unequal work'
                    }
                }
            ],
            'deliverables': ['Source code', 'Documentation', 'Presentation', 'Demo']
        }
        
    def _generate_presentation_rubric(self, weightage: int) -> Dict[str, Any]:
        """Generate rubric for presentations"""
        return {
            'type': 'presentation',
            'total_marks': weightage,
            'criteria': [
                {
                    'name': 'Content Knowledge',
                    'weightage': 40,
                    'levels': {
                        'Excellent': 'Deep understanding, handles questions excellently',
                        'Good': 'Good knowledge, answers most questions',
                        'Satisfactory': 'Basic knowledge, struggles with some questions',
                        'Poor': 'Limited knowledge evident'
                    }
                },
                {
                    'name': 'Communication Skills',
                    'weightage': 30,
                    'levels': {
                        'Excellent': 'Clear, confident, engaging delivery',
                        'Good': 'Generally clear communication',
                        'Satisfactory': 'Understandable but needs improvement',
                        'Poor': 'Difficult to follow or understand'
                    }
                },
                {
                    'name': 'Visual Aids',
                    'weightage': 20,
                    'levels': {
                        'Excellent': 'Professional, effective slides/materials',
                        'Good': 'Good visual support',
                        'Satisfactory': 'Basic visuals present',
                        'Poor': 'Poor or missing visual aids'
                    }
                },
                {
                    'name': 'Time Management',
                    'weightage': 10,
                    'levels': {
                        'Perfect': 'Within allocated time',
                        'Good': 'Slightly over/under time',
                        'Acceptable': 'Moderately off-time',
                        'Poor': 'Significantly over/under time'
                    }
                }
            ],
            'duration': '10-15 minutes + Q&A'
        }
        
    def _generate_participation_rubric(self, weightage: int) -> Dict[str, Any]:
        """Generate rubric for class participation"""
        return {
            'type': 'participation',
            'total_marks': weightage,
            'criteria': [
                {
                    'name': 'Attendance',
                    'weightage': 40,
                    'levels': {
                        'Excellent (90-100%)': '95%+ attendance',
                        'Good (75-89%)': '85-94% attendance',
                        'Satisfactory (60-74%)': '75-84% attendance',
                        'Poor (<60%)': 'Below 75% attendance'
                    }
                },
                {
                    'name': 'Active Participation',
                    'weightage': 35,
                    'levels': {
                        'Excellent': 'Regular contributions, asks thoughtful questions',
                        'Good': 'Participates frequently',
                        'Satisfactory': 'Occasional participation',
                        'Poor': 'Rarely participates'
                    }
                },
                {
                    'name': 'Preparation & Engagement',
                    'weightage': 25,
                    'levels': {
                        'Excellent': 'Always prepared, highly engaged',
                        'Good': 'Usually prepared and engaged',
                        'Satisfactory': 'Sometimes prepared',
                        'Poor': 'Often unprepared or disengaged'
                    }
                }
            ],
            'evaluation_period': 'Throughout the semester'
        }
        
    def generate_summary_table(self, rubrics: Dict[str, Any]) -> str:
        """Generate a formatted summary of all rubrics"""
        summary = "# Assessment Rubrics Summary\n\n"
        
        for component_name, rubric in rubrics.items():
            summary += f"## {component_name.replace('_', ' ').title()}\n"
            summary += f"**Type:** {rubric['type']}  \n"
            summary += f"**Total Marks:** {rubric['total_marks']}  \n\n"
            
            summary += "### Evaluation Criteria:\n\n"
            for criterion in rubric['criteria']:
                summary += f"**{criterion['name']}** ({criterion['weightage']}%):\n"
                for level, description in criterion.get('levels', {}).items():
                    summary += f"- {level}: {description}\n"
                summary += "\n"
            summary += "---\n\n"
            
        return summary
