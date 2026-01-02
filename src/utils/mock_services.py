from typing import List, Dict, Any

class MockContentOptimizer:
    def optimize_unit_sequence(self, units: List[Dict]) -> Dict:
        return {
            "original_sequence": [u.get('title') for u in units],
            "optimized_sequence": [u.get('title') for u in units],
            "optimization_suggestions": "The current sequence follows a logical progression. Consider grouping related topics closer together for better flow."
        }
    
    def suggest_modern_content(self, course_title: str, current_topics: List[str]) -> List[str]:
        return [
            "AI in " + course_title,
            "Sustainability practices",
            "Industry 4.0 applications",
            "Ethics and Compliance"
        ]

class MockBloomMapper:
    def analyze_distribution(self, outcomes: List[str]) -> Dict[str, Any]:
        return {
            "distribution": {
                "Remember": 20.0,
                "Understand": 30.0,
                "Apply": 25.0,
                "Analyze": 15.0,
                "Evaluate": 5.0,
                "Create": 5.0
            },
            "comparison": {
                "remember": {"status": "optimal", "current": 20.0, "recommended_min": 15, "recommended_max": 25},
                "understand": {"status": "above", "current": 30.0, "recommended_min": 15, "recommended_max": 25},
                "apply": {"status": "optimal", "current": 25.0, "recommended_min": 20, "recommended_max": 30},
                "analyze": {"status": "below", "current": 15.0, "recommended_min": 20, "recommended_max": 30},
                "evaluate": {"status": "below", "current": 5.0, "recommended_min": 10, "recommended_max": 20},
                "create": {"status": "below", "current": 5.0, "recommended_min": 10, "recommended_max": 20}
            }
        }
    
    def suggest_rebalancing(self, bloom_analysis: Dict) -> List[str]:
        return [
            "Increase higher-order thinking (Evaluate, Create) by adding project-based outcomes.",
            "Reduce 'Remember' level outcomes to focus more on application."
        ]

class MockGapAnalyzer:
    def analyze(self, syllabus_data: Dict) -> Dict:
        return {
            "overall_score": 75,
            "bloom_coverage": {
                "percentages": {
                    "Remember": 20.0,
                    "Understand": 30.0,
                    "Apply": 25.0,
                    "Analyze": 15.0,
                    "Evaluate": 5.0,
                    "Create": 5.0
                }
            },
            "co_po_mapping_gaps": {
                "total_cos": 5,
                "mapped_cos": 3,
                "coverage_percentage": 60.0
            },
            "assessment_gaps": {
                "total_percentage": 100,
                "components": {
                    "end_semester_exam": 60,
                    "internal_assessment": 40
                }
            },
            "recommendations": [
                "Include a module on professional ethics.",
                "Update reference books to editions after 2020.",
                "Ensure all Course Outcomes are mapped to Program Outcomes.",
                "Increase weightage for continuous assessment."
            ]
        }
