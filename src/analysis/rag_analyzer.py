from typing import Dict, Any, List
from ..utils.mock_services import MockGapAnalyzer
from ..rag.retriever import RAGEngine
import logging

class RAGAwareAnalyzer(MockGapAnalyzer):
    """
    Enhanced Gap Analyzer that uses RAG to fetch real citations and requirements
    from the indexed documentation (NBA/NAAC manuals).
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        try:
            self.rag = RAGEngine()
            self.rag_ready = True
        except Exception as e:
            self.logger.warning(f"RAG Engine failed to initialize: {e}")
            self.rag_ready = False

    def analyze(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze syllabus using base logic + RAG enhancements.
        """
        # Get base analysis from the Mock/Logic analyzer
        report = super().analyze(syllabus_data)
        
        if not self.rag_ready:
            return report

        # Enhance recommendations with RAG
        enhanced_recommendations = self._get_rag_recommendations(syllabus_data)
        if enhanced_recommendations:
            # Replace or append to generic recommendations
            report['recommendations'] = enhanced_recommendations + report.get('recommendations', [])

        return report

    def _get_rag_recommendations(self, syllabus_data: Dict[str, Any]) -> List[str]:
        recommendations = []
        course_title = syllabus_data.get('course_title', 'this course')
        
        # Query 1: Assessment guidelines
        try:
            results = self.rag.query("What is the recommended weightage for continuous assessment?")
            if results['documents'][0]:
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

