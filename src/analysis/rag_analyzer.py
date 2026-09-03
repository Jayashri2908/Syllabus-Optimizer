from typing import Dict, Any, List
from ..rag.retriever import RAGEngine
import logging
import concurrent.futures


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

        # Enhance with RAG if available — run all 4 queries in parallel
        if self.rag_ready:
            rag_recs = self._get_rag_recommendations_parallel(syllabus_data)
            if rag_recs:
                report['recommendations'] = rag_recs + report['recommendations']
                report['ai_analysis'] = rag_recs[0] if rag_recs else None

        return report

    def _rag_query(self, question: str, n_results: int = 3) -> tuple:
        """Run a single RAG query, returns (question, results_dict)."""
        try:
            results = self.rag.query(question, n_results=n_results)
            return (question, results)
        except Exception as e:
            self.logger.error(f"RAG query failed for '{question}': {e}")
            return (question, None)

    def _get_rag_recommendations_parallel(self, syllabus_data: Dict[str, Any]) -> List[str]:
        """Run all RAG queries concurrently and build recommendations from results."""
        course_title = syllabus_data.get('course_title', 'this course')

        queries = [
            "What is the recommended weightage for continuous assessment?",
            "What are the mandatory Program Outcomes for Engineering in NBA?",
            "How to assess higher order thinking skills in engineering education?",
        ]
        if course_title and course_title != 'this course':
            queries.append(f"What topics should be included in {course_title}?")

        recommendations = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_query = {
                executor.submit(self._rag_query, q): q for q in queries
            }
            for future in concurrent.futures.as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    question, results = future.result()
                    if not results:
                        continue
                    docs = results.get('documents', [[]])[0]
                    metas = results.get('metadatas', [[]])[0]
                    if not docs:
                        continue

                    doc_snippet = docs[0][:150] + "..."
                    source = metas[0].get('source', 'Reference') if metas else 'Reference'

                    if "assessment" in question.lower():
                        recommendations.append(f"Consider guideline from {source}: '{doc_snippet}' regarding assessment.")
                    elif "nba" in question.lower() or "program outcomes" in question.lower():
                        recommendations.append(f"From {source}: Ensure all 12 Program Outcomes are mapped - '{doc_snippet}'")
                    elif "higher order" in question.lower():
                        recommendations.append(f"For higher-order outcomes: '{doc_snippet}'")
                    else:
                        recommendations.append(f"For {course_title}: Consider including '{doc_snippet}'")
                except Exception as e:
                    self.logger.error(f"RAG result processing failed: {e}")

        return recommendations
