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
        
        # Query 1: Check for Program Outcomes specific to the domain
        # context = self.rag.get_context("What are the mandatory Program Outcomes for Engineering in NBA?")
        
        # Query 2: Check assessment guidelines
        try:
            results = self.rag.query("What is the recommended weightage for continuous assessment?")
            if results['documents'][0]:
                doc_snippet = results['documents'][0][0][:150] + "..."
                source = results['metadatas'][0][0]['source']
                recommendations.append(f"Consider guideline from {source}: '{doc_snippet}' regarding assessment.")
        except Exception as e:
            self.logger.error(f"RAG Query failed: {e}")

        # Query 3: Check curriculum gaps based on course title
        course_title = syllabus_data.get('course_title', 'this course')
        try:
            # Ask what is essential for this course
            # Note: This works best if the indexed docs actually contain subject specific info. 
            # If we only have manuals, it might not find much. 
            pass 
        except Exception:
            pass

        return recommendations
