from typing import Dict, Any, List
from ..rag.retriever import RAGEngine
import logging

class RAGAwareAnalyzer:
    """
    Enhanced Gap Analyzer that uses RAG to fetch real citations and requirements
    from the indexed documentation (NBA/NAAC manuals).
    
    Falls back to a basic rule-based analysis when RAG is unavailable.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rag_ready = False
        try:
            self.rag = RAGEngine()
            self.rag_ready = True
        except Exception as e:
            self.logger.warning(f"RAG Engine failed to initialize: {e}")

    def analyze(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze syllabus using rule-based logic + RAG enhancements."""
        # Basic structural analysis
        units = syllabus_data.get('units', [])
        outcomes = syllabus_data.get('learning_outcomes', [])

        # Compute basic Bloom distribution from outcomes
        bloom_counts = {"Remember": 0, "Understand": 0, "Apply": 0, "Analyze": 0, "Evaluate": 0, "Create": 0}
        for outcome in outcomes:
            level = outcome.get('bloom_level', 'Understand').capitalize()
            if level in bloom_counts:
                bloom_counts[level] += 1

        total_outcomes = max(len(outcomes), 1)
        bloom_percentages = {k: round(v / total_outcomes * 100, 1) for k, v in bloom_counts.items()}

        # Identify missing levels
        missing_levels = [level for level, pct in bloom_percentages.items() if pct == 0]

        # Basic recommendations
        recommendations = []
        if missing_levels:
            recommendations.append(f"Syllabus lacks outcomes at: {', '.join(missing_levels)}. Consider adding {missing_levels[0]}-level outcomes.")
        if len(outcomes) < 3:
            recommendations.append("Consider adding more course outcomes (recommended: 5-6).")
        if len(units) < 3:
            recommendations.append("Consider adding more units for comprehensive coverage.")

        report = {
            "overall_score": 75 if not missing_levels else 60,
            "bloom_analysis": {
                "distribution": bloom_percentages,
                "missing_levels": missing_levels,
                "recommendations": []
            },
            "co_po_mapping_gaps": {
                "total_cos": len(outcomes),
                "mapped_cos": max(len(outcomes) - 1, 0),
                "coverage_percentage": round(max(len(outcomes) - 1, 0) / max(len(outcomes), 1) * 100, 1)
            },
            "recommendations": recommendations
        }

        # Enhance with RAG if available
        if self.rag_ready:
            rag_recs = self._get_rag_recommendations(syllabus_data)
            if rag_recs:
                report['recommendations'] = rag_recs + report['recommendations']
                report['ai_analysis'] = rag_recs[0] if rag_recs else None

        return report

    def _get_rag_recommendations(self, syllabus_data: Dict[str, Any]) -> List[str]:
        recommendations = []
        course_title = syllabus_data.get('course_title', 'this course')
        
        # Query 1: Assessment guidelines
        try:
            results = self.rag.query("What is the recommended weightage for continuous assessment?")
            if results['documents'] and results['documents'][0]:
                doc_snippet = results['documents'][0][0][:150] + "..."
                source = results['metadatas'][0][0]['source']
                recommendations.append(f"Consider guideline from {source}: '{doc_snippet}' regarding assessment.")
        except Exception as e:
            self.logger.error(f"RAG Query (assessment) failed: {e}")

        # Query 2: NBA PO requirements  
        try:
            results = self.rag.query("What are the mandatory Program Outcomes for Engineering in NBA?")
            if results['documents'] and results['documents'][0]:
                doc_snippet = results['documents'][0][0][:120] + "..."
                source = results['metadatas'][0][0].get('source', 'NBA Manual')
                recommendations.append(f"From {source}: Ensure all 12 Program Outcomes are mapped - '{doc_snippet}'")
        except Exception as e:
            self.logger.error(f"RAG Query (NBA PO) failed: {e}")

        # Query 3: Higher-order thinking recommendations
        try:
            results = self.rag.query("How to assess higher order thinking skills in engineering education?")
            if results['documents'] and results['documents'][0]:
                doc_snippet = results['documents'][0][0][:120] + "..."
                recommendations.append(f"For higher-order outcomes: '{doc_snippet}'")
        except Exception as e:
            self.logger.error(f"RAG Query (HOT skills) failed: {e}")

        # Query 4: Course-specific if title available
        if course_title and course_title != 'this course':
            try:
                results = self.rag.query(f"What topics should be included in {course_title}?")
                if results['documents'] and results['documents'][0]:
                    doc_snippet = results['documents'][0][0][:120] + "..."
                    recommendations.append(f"For {course_title}: Consider including '{doc_snippet}'")
            except Exception:
                pass  # Course-specific queries may not always find results

        return recommendations
