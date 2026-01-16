"""
Reference Suggester for SCDO
Suggests relevant textbooks and resources using AI
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

try:
    from ..ai.model_manager import ModelManager
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class ReferenceSuggester:
    """Suggest relevant academic references and resources"""
    
    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.logger = logging.getLogger(__name__)
        
        if AI_AVAILABLE:
            self.ai = model_manager or ModelManager()
            self.enabled = True
        else:
            self.logger.warning("AI models not available. Using fallback suggestions.")
            self.enabled = False
            
        self.current_year = datetime.now().year
        
    def suggest_references(
        self,
        course_title: str,
        topics: List[str],
        domain: str = "engineering",
        current_references: List[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest relevant references for the course
        
        Args:
            course_title: Course title
            topics: List of topics covered
            domain: Academic domain
            current_references: Existing references (optional)
            
        Returns:
            Categorized reference suggestions
        """
        if self.enabled:
            suggestions = self._suggest_with_ai(course_title, topics, domain, current_references)
        else:
            suggestions = self._suggest_fallback(course_title, domain)
            
        # Analyze current references
        analysis = self._analyze_current_references(current_references) if current_references else None
        
        return {
            'status': 'success',
            'current_analysis': analysis,
            'suggestions': suggestions,
            'total_suggested': sum(len(refs) for refs in suggestions.values())
        }
        
    def _suggest_with_ai(
        self,
        course_title: str,
        topics: List[str],
        domain: str,
        current_references: List[str]
    ) -> Dict[str, List[Dict]]:
        """Generate suggestions using AI"""
        
        topics_text = ", ".join(topics[:10])  # Limit to avoid token overflow
        current_refs_text = "\n".join(current_references[:5]) if current_references else "None"
        
        system_prompt = f"""You are an expert librarian and academic advisor in {domain}.
Suggest high-quality, relevant academic references including:
- Standard textbooks (well-established, multiple editions)
- Recent publications (last 5 years preferred)
- Reference books for deeper study
- Online resources (MOOCs, official documentation)
- Research journals for advanced topics

Focus on authoritative, peer-reviewed, and widely-used resources."""

        prompt = f"""Course: {course_title}
Domain: {domain}
Topics: {topics_text}

Current References:
{current_refs_text}

Suggest 10-15 high-quality references categorized as:
1. PRIMARY TEXTBOOKS (2-3 essential books)
2. REFERENCE BOOKS (2-3 for deeper study)
3. RECENT PUBLICATIONS (2-3 latest editions/new books)
4. ONLINE RESOURCES (2-3 MOOCs, documentation, websites)
5. RESEARCH JOURNALS (2-3 key journals for research)

For each, provide:
- Full citation (Author, Title, Edition, Year, Publisher)
- Why it's relevant
- Category

Format each as:
CATEGORY: [category]
TITLE: [full title]
AUTHOR: [author(s)]
YEAR: [publication year]
PUBLISHER: [publisher]
RELEVANCE: [why recommended]
---"""

        try:
            response = self.ai.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                task_type='generation',
                temperature=0.6,
                max_tokens=2000
            )
            
            # Parse response
            suggestions = {
                'primary_textbooks': [],
                'reference_books': [],
                'recent_publications': [],
                'online_resources': [],
                'research_journals': []
            }
            
            entries = response.split('---')
            for entry in entries:
                if 'TITLE:' in entry:
                    ref = self._parse_reference_entry(entry)
                    if ref:
                        category = ref.pop('category', 'reference_books')
                        category_key = category.lower().replace(' ', '_')
                        if category_key in suggestions:
                            suggestions[category_key].append(ref)
                        else:
                            suggestions['reference_books'].append(ref)
                            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"AI suggestion failed: {e}")
            return self._suggest_fallback(course_title, domain)
            
    def _parse_reference_entry(self, entry: str) -> Dict[str, str]:
        """Parse a single reference entry"""
        ref = {}
        
        for line in entry.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                ref[key] = value
                
        return ref if 'title' in ref else None
        
    def _suggest_fallback(self, course_title: str, domain: str) -> Dict[str, List[Dict]]:
        """Fallback suggestions when AI is not available"""
        
        # Generic suggestions based on domain
        domain_resources = {
            'computer_science': {
                'primary_textbooks': [
                    {
                        'title': 'Introduction to Algorithms',
                        'author': 'Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein',
                        'year': '2022',
                        'publisher': 'MIT Press',
                        'relevance': 'Comprehensive algorithms textbook'
                    }
                ],
                'online_resources': [
                    {
                        'title': 'MIT OpenCourseWare',
                        'author': 'MIT',
                        'url': 'https://ocw.mit.edu',
                        'relevance': 'Free course materials'
                    }
                ]
            },
            'engineering': {
                'primary_textbooks': [
                    {
                        'title': 'Engineering Fundamentals',
                        'author': 'Various Authors',
                        'year': str(self.current_year - 1),
                        'publisher': 'Leading Publishers',
                        'relevance': 'Core engineering concepts'
                    }
                ]
            }
        }
        
        return domain_resources.get(domain, domain_resources['engineering'])
        
    def _analyze_current_references(self, references: List[str]) -> Dict[str, Any]:
        """Analyze current reference list"""
        if not references:
            return None
            
        current_year = self.current_year
        
        # Extract years from references (simple pattern matching)
        years = []
        for ref in references:
            # Look for 4-digit years
            import re
            year_matches = re.findall(r'\b(19|20)\d{2}\b', ref)
            if year_matches:
                years.extend([int(y) for y in year_matches])
                
        avg_age = (current_year - sum(years) / len(years)) if years else 0
        oldest = min(years) if years else current_year
        newest = max(years) if years else current_year
        
        # Check for recent references (last 5 years)
        recent_count = sum(1 for y in years if current_year - y <= 5)
        recent_percentage = (recent_count / len(years) * 100) if years else 0
        
        issues = []
        if avg_age > 10:
            issues.append("References are outdated (average age > 10 years)")
        if recent_percentage < 30:
            issues.append("Less than 30% recent references (last 5 years)")
        if len(references) < 5:
            issues.append("Insufficient number of references (minimum 5 recommended)")
            
        return {
            'total_references': len(references),
            'average_age': round(avg_age, 1),
            'oldest_year': oldest,
            'newest_year': newest,
            'recent_percentage': round(recent_percentage, 1),
            'issues': issues,
            'recommendation': 'Add more recent references' if recent_percentage < 50 else 'Good reference mix'
        }
