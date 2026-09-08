"""
Gap Analyzer for SCDO
Identifies gaps and issues in syllabus content
"""

from typing import Dict, List, Any
import yaml
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import concurrent.futures

from ..utils.text_processing import TextProcessor
from .lesson_plan_extractor import LessonPlanExtractor
from .redundancy_detector import RedundancyDetector
from .content_analyzer import ContentAnalyzer
from .outcome_extractor import OutcomeExtractor
from ..validation.nep_2020_validator import NEP2020Validator
from ..validation.accreditation_checker import AccreditationChecker

try:
    from ..rag.retriever import RAGEngine
    RAG_AVAILABLE = True
except Exception:
    RAG_ENGINE = None
    RAG_AVAILABLE = False


class GapAnalyzer:
    """Analyze syllabus for gaps and improvement opportunities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        self.bloom_taxonomy = self._load_bloom_taxonomy()
        self.accreditation_standards = self._load_accreditation_standards()
        self.lesson_plan_extractor = LessonPlanExtractor()
        self.redundancy_detector = RedundancyDetector()
        self.content_analyzer = ContentAnalyzer()
        self.nep_validator = NEP2020Validator()
        self.accreditation_checker = AccreditationChecker()
        self.outcome_extractor = OutcomeExtractor()
        self.rag = None
        self.rag_ready = False
        self._init_rag()
        
    def _init_rag(self):
        """Initialize RAG engine if available"""
        if not RAG_AVAILABLE:
            self.logger.info("RAG engine not available — using rule-based analysis only")
            return
        try:
            self.rag = RAGEngine()
            self.rag_ready = True
            self.logger.info("RAG engine initialized successfully")
        except Exception as e:
            self.logger.warning(f"RAG engine initialization failed: {e}")
            self.rag = None
            self.rag_ready = False
        
    def _load_bloom_taxonomy(self) -> dict:
        """Load Bloom's taxonomy configuration"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "bloom_taxonomy.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def _load_accreditation_standards(self) -> dict:
        """Load accreditation standards"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "accreditation.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def analyze(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive gap analysis with parallel sub-analyses
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            Gap analysis report
        """
        # Define all independent analysis tasks
        tasks = {
            'bloom_coverage': lambda: self._analyze_bloom_coverage(syllabus_data),
            'co_po_mapping_gaps': lambda: self._analyze_co_po_mapping(syllabus_data),
            'assessment_gaps': lambda: self._analyze_assessment(syllabus_data),
            'content_gaps': lambda: self._analyze_content(syllabus_data),
            'structural_issues': lambda: self._analyze_structure(syllabus_data),
            'lesson_plan_analysis': lambda: self._analyze_lesson_plans(syllabus_data),
            'redundancies': lambda: self._analyze_redundancies(syllabus_data),
            'content_quality': lambda: self.content_analyzer.analyze(syllabus_data),
            'nep_2020_compliance': lambda: self.nep_validator.validate(syllabus_data),
            'nba_compliance': lambda: self.accreditation_checker.check_nba_compliance(syllabus_data),
            'naac_compliance': lambda: self.accreditation_checker.check_naac_compliance(syllabus_data),
            'outcome_validation': lambda: self._validate_outcomes(syllabus_data),
        }
        
        # Run all independent analyses in parallel
        results = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(fn): key for key, fn in tasks.items()}
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    self.logger.error(f"Analysis task '{key}' failed: {e}")
                    results[key] = {}
        
        report = {
            'bloom_coverage': results.get('bloom_coverage', {}),
            'co_po_mapping_gaps': results.get('co_po_mapping_gaps', {}),
            'assessment_gaps': results.get('assessment_gaps', {}),
            'content_gaps': results.get('content_gaps', {}),
            'structural_issues': results.get('structural_issues', []),
            'lesson_plan_analysis': results.get('lesson_plan_analysis', {}),
            'redundancies': results.get('redundancies', {}),
            'content_quality': results.get('content_quality', {}),
            'nep_2020_compliance': results.get('nep_2020_compliance', {}),
            'accreditation_compliance': {
                'nba': results.get('nba_compliance', {}),
                'naac': results.get('naac_compliance', {}),
            },
            'outcome_validation': results.get('outcome_validation', {}),
            'recommendations': []
        }
        
        # Generate recommendations based on gaps
        report['recommendations'] = self._generate_recommendations(report)
        
        # Enhance recommendations with RAG if available
        if self.rag_ready:
            rag_recs = self._get_rag_recommendations(syllabus_data)
            if rag_recs:
                report['ai_analysis'] = rag_recs[0]
                for rec in rag_recs:
                    report['recommendations'].append({
                        'text': rec,
                        'priority': 'medium',
                        'category': 'rag_insight'
                    })
        
        # Calculate overall quality score
        report['overall_quality_score'] = self._calculate_overall_score(report)
        
        return report
        
    def _analyze_bloom_coverage(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Bloom's taxonomy coverage"""
        outcomes = syllabus_data.get('learning_outcomes', [])
        
        # Count outcomes by Bloom's level
        level_counts = {
            'remember': 0,
            'understand': 0,
            'apply': 0,
            'analyze': 0,
            'evaluate': 0,
            'create': 0,
            'unknown': 0
        }
        
        for outcome in outcomes:
            level = outcome.get('bloom_level', 'unknown')
            level_counts[level] = level_counts.get(level, 0) + 1
            
        total = sum(level_counts.values())
        
        # Calculate percentages
        percentages = {}
        if total > 0:
            percentages = {level: (count / total) * 100 
                          for level, count in level_counts.items()}
        
        # Get recommended distribution
        recommended = self.bloom_taxonomy.get('recommended_distribution', {})
        
        # Identify gaps
        gaps = []
        for level, percentage in percentages.items():
            if level == 'unknown':
                continue
                
            rec_range = recommended.get(level, '0-0%')
            # Parse range (e.g., "10-15%")
            if isinstance(rec_range, str) and '-' in rec_range:
                min_val = int(rec_range.split('-')[0])
                max_val = int(rec_range.split('-')[1].rstrip('%'))
                
                if percentage < min_val:
                    gaps.append({
                        'level': level,
                        'current': percentage,
                        'recommended': rec_range,
                        'issue': 'underrepresented'
                    })
                elif percentage > max_val:
                    gaps.append({
                        'level': level,
                        'current': percentage,
                        'recommended': rec_range,
                        'issue': 'overrepresented'
                    })
        
        return {
            'level_counts': level_counts,
            'percentages': percentages,
            'gaps': gaps,
            'total_outcomes': total
        }
        
    def _analyze_co_po_mapping(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze CO-PO mapping completeness"""
        mapping = syllabus_data.get('co_po_mapping', {})
        outcomes = syllabus_data.get('learning_outcomes', [])
        
        # Expected POs (typically 12 for engineering)
        expected_pos = [f'PO{i}' for i in range(1, 13)]
        
        gaps = []
        
        # Check if all COs have mappings
        for outcome in outcomes:
            co_code = outcome.get('code', '')
            if co_code not in mapping:
                gaps.append({
                    'type': 'missing_co_mapping',
                    'co': co_code,
                    'description': f'{co_code} has no PO mappings'
                })
            else:
                # Check if all relevant POs are mapped
                co_mapping = mapping[co_code]
                mapped_pos = set(co_mapping.keys())
                
                # At least some POs should be mapped
                if len(mapped_pos) == 0:
                    gaps.append({
                        'type': 'empty_mapping',
                        'co': co_code,
                        'description': f'{co_code} mapping is empty'
                    })
                    
        return {
            'total_cos': len(outcomes),
            'mapped_cos': len(mapping),
            'gaps': gaps,
            'coverage_percentage': (len(mapping) / len(outcomes) * 100) if outcomes else 0
        }
        
    def _analyze_assessment(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze assessment pattern"""
        assessment = syllabus_data.get('assessment_pattern', {})
        
        gaps = []
        
        # Check if assessment adds up to 100%
        total = sum(assessment.values())
        if total != 100 and total > 0:
            gaps.append({
                'type': 'total_mismatch',
                'current_total': total,
                'expected_total': 100,
                'description': f'Assessment components total {total}% instead of 100%'
            })
            
        # Check for missing common components
        recommended_components = ['internal', 'external', 'assignment']
        for component in recommended_components:
            if component not in assessment:
                gaps.append({
                    'type': 'missing_component',
                    'component': component,
                    'description': f'Missing {component} assessment component'
                })
                
        # Check for balanced assessment
        if assessment:
            max_component = max(assessment.values())
            if max_component > 70:
                gaps.append({
                    'type': 'imbalanced',
                    'description': f'One component has {max_component}% weightage (too high)'
                })
                
        return {
            'total_percentage': total,
            'components': assessment,
            'gaps': gaps
        }
        
    def _analyze_content(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content quality and completeness"""
        gaps = []
        
        # Check for missing essential components
        essential = ['course_title', 'course_code', 'credits', 'learning_outcomes', 'units']
        
        for component in essential:
            value = syllabus_data.get(component)
            if not value or (isinstance(value, (list, dict)) and len(value) == 0):
                gaps.append({
                    'type': 'missing_component',
                    'component': component,
                    'description': f'Missing or empty {component}'
                })
                
        # Check unit hours
        units = syllabus_data.get('units', [])
        total_hours = sum(unit.get('hours', 0) for unit in units)
        
        if total_hours == 0:
            gaps.append({
                'type': 'missing_hours',
                'description': 'No unit hours specified'
            })
            
        # Check references
        references = syllabus_data.get('references', [])
        if len(references) < 3:
            gaps.append({
                'type': 'insufficient_references',
                'current_count': len(references),
                'recommended_min': 3,
                'description': 'Insufficient reference materials (minimum 3 recommended)'
            })
            
        return {
            'gaps': gaps,
            'total_units': len(units),
            'total_hours': total_hours,
            'reference_count': len(references)
        }
        
    def _analyze_structure(self, syllabus_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Analyze structural issues"""
        issues = []
        
        # Check number of learning outcomes
        outcomes = syllabus_data.get('learning_outcomes', [])
        if len(outcomes) < 4:
            issues.append({
                'type': 'insufficient_cos',
                'severity': 'high',
                'description': f'Only {len(outcomes)} course outcomes (minimum 4-6 recommended)'
            })
        elif len(outcomes) > 8:
            issues.append({
                'type': 'excessive_cos',
                'severity': 'medium',
                'description': f'{len(outcomes)} course outcomes (maximum 6-8 recommended)'
            })
            
        # Check unit distribution
        units = syllabus_data.get('units', [])
        if len(units) < 3:
            issues.append({
                'type': 'insufficient_units',
                'severity': 'medium',
                'description': f'Only {len(units)} units (typically 4-6 units recommended)'
            })
            
        return issues
        
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations with priority levels"""
        recommendations = []
        
        # Bloom's coverage recommendations (Medium priority)
        bloom_gaps = report['bloom_coverage'].get('gaps', [])
        for gap in bloom_gaps:
            level = gap['level']
            issue = gap['issue']
            if issue == 'underrepresented':
                recommendations.append({
                    'text': f"Add more learning outcomes at '{level}' level to meet recommended distribution",
                    'priority': 'medium',
                    'category': 'bloom_taxonomy'
                })
            elif issue == 'overrepresented':
                recommendations.append({
                    'text': f"Consider reducing '{level}' level outcomes and diversifying cognitive levels",
                    'priority': 'low',
                    'category': 'bloom_taxonomy'
                })
                
        # CO-PO mapping recommendations (High priority - accreditation critical)
        co_po_gaps = report['co_po_mapping_gaps'].get('gaps', [])
        if co_po_gaps:
            recommendations.append({
                'text': "Complete CO-PO mapping for all course outcomes to meet accreditation requirements",
                'priority': 'high',
                'category': 'accreditation'
            })
            
        # Assessment recommendations (High priority)
        assessment_gaps = report['assessment_gaps'].get('gaps', [])
        for gap in assessment_gaps:
            if gap['type'] == 'total_mismatch':
                recommendations.append({
                    'text': "Adjust assessment component weightages to total 100%",
                    'priority': 'high',
                    'category': 'assessment'
                })
            elif gap['type'] == 'missing_component':
                recommendations.append({
                    'text': f"Add {gap['component']} assessment component",
                    'priority': 'medium',
                    'category': 'assessment'
                })
                
        # Content recommendations (Medium priority)
        content_gaps = report['content_gaps'].get('gaps', [])
        for gap in content_gaps:
            if gap['type'] == 'insufficient_references':
                recommendations.append({
                    'text': "Add more reference materials (textbooks, research papers, online resources)",
                    'priority': 'medium',
                    'category': 'content'
                })
            elif gap['type'] == 'missing_hours':
                recommendations.append({
                    'text': "Specify contact hours for each unit",
                    'priority': 'high',
                    'category': 'structure'
                })
        
        # Outcome validation recommendations (High priority)
        outcome_validation = report.get('outcome_validation', {})
        invalid_count = outcome_validation.get('issues_count', 0)
        if invalid_count > 0:
            recommendations.append({
                'text': f"{invalid_count} learning outcome(s) need improvement — use measurable action verbs and avoid vague terms",
                'priority': 'high',
                'category': 'outcome_quality'
            })
        avg_measurability = outcome_validation.get('average_measurability', 1)
        if avg_measurability < 0.5:
            recommendations.append({
                'text': "Overall outcome measurability is low — rewrite outcomes with specific, assessable verbs",
                'priority': 'medium',
                'category': 'outcome_quality'
            })
        
        # Sort by priority: high > medium > low
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
                
        return recommendations
        
    def _analyze_lesson_plans(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze lesson plan completeness and structure
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            Lesson plan analysis
        """
        units = syllabus_data.get('units', [])
        
        if not units:
            return {
                'status': 'no_units',
                'message': 'No units found in syllabus'
            }
            
        # Extract lesson plans
        lesson_analysis = self.lesson_plan_extractor.extract_lesson_plans(units)
        
        # Identify gaps
        gaps = []
        
        # Check for units without hours
        if lesson_analysis['units_without_hours']:
            gaps.append({
                'type': 'missing_hours',
                'severity': 'high',
                'units': lesson_analysis['units_without_hours'],
                'description': f"{len(lesson_analysis['units_without_hours'])} units missing hour allocation"
            })
            
        # Check for units without teaching methods
        if lesson_analysis['units_without_methods']:
            gaps.append({
                'type': 'missing_methods',
                'severity': 'medium',
                'units': lesson_analysis['units_without_methods'],
                'description': f"{len(lesson_analysis['units_without_methods'])} units without specified teaching methods"
            })
            
        # Check for unbalanced lesson distribution
        distribution = lesson_analysis.get('lesson_distribution', {})
        lessons_per_unit = distribution.get('lessons_per_unit', {})
        if lessons_per_unit:
            lesson_counts = list(lessons_per_unit.values())
            avg_lessons = sum(lesson_counts) / len(lesson_counts)
            
            for unit_num, count in lessons_per_unit.items():
                if count < avg_lessons * 0.5:  # Less than 50% of average
                    gaps.append({
                        'type': 'sparse_unit',
                        'severity': 'medium',
                        'unit_number': unit_num,
                        'lesson_count': count,
                        'average': avg_lessons,
                        'description': f"Unit {unit_num} has significantly fewer lessons ({count}) than average ({avg_lessons:.1f})"
                    })
                    
        lesson_analysis['gaps'] = gaps
        return lesson_analysis
        
    def _analyze_redundancies(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect content redundancies using semantic similarity
        
        Args:
            syllabus_data: Parsed syllabus structure
            
        Returns:
            Redundancy analysis
        """
        return self.redundancy_detector.detect_redundancies(syllabus_data)

    def _rag_query(self, question: str, n_results: int = 3) -> tuple:
        """Run a single RAG query, returns (question, results_dict)."""
        try:
            results = self.rag.query(question, n_results=n_results)
            return (question, results)
        except Exception as e:
            self.logger.error(f"RAG query failed for '{question}': {e}")
            return (question, None)

    def _get_rag_recommendations(self, syllabus_data: Dict[str, Any]) -> List[str]:
        """Run all RAG queries concurrently and build recommendations from results."""
        if not self.rag_ready or not self.rag:
            return []

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

    def _calculate_overall_score(self, report: Dict[str, Any]) -> float:
        """Calculate an overall quality score (0-100) from sub-analysis results."""
        scores = []

        content_quality = report.get('content_quality', {})
        if content_quality:
            scores.append(content_quality.get('overall_score', 0) * 100)

        bloom_coverage = report.get('bloom_coverage', {})
        bloom_gaps = bloom_coverage.get('gaps', [])
        total_outcomes = bloom_coverage.get('total_outcomes', 0)
        if total_outcomes > 0:
            bloom_score = max(0, 100 - len(bloom_gaps) * 15)
            scores.append(bloom_score)

        co_po = report.get('co_po_mapping_gaps', {})
        coverage_pct = co_po.get('coverage_percentage', 0)
        scores.append(coverage_pct)

        assessment = report.get('assessment_gaps', {})
        assessment_gaps = assessment.get('gaps', [])
        if assessment.get('total_percentage') == 100 and not assessment_gaps:
            scores.append(100)
        elif assessment.get('total_percentage', 0) > 0:
            scores.append(max(0, 100 - len(assessment_gaps) * 20))
        else:
            scores.append(50)

        structural = report.get('structural_issues', [])
        struct_score = max(0, 100 - len(structural) * 20)
        scores.append(struct_score)

        redundancies = report.get('redundancies', {})
        overlap = redundancies.get('overlap_score', 0)
        scores.append(max(0, 100 - overlap * 100))

        if scores:
            return round(sum(scores) / len(scores), 1)
        return 0.0

    def _validate_outcomes(self, syllabus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate each learning outcome for measurability and quality"""
        outcomes = syllabus_data.get('learning_outcomes', [])
        validated = []
        issues_count = 0

        for outcome in outcomes:
            description = outcome.get('description', '') if isinstance(outcome, dict) else str(outcome)
            if not description:
                continue

            validation = self.outcome_extractor.validate_outcome(description)
            entry = {
                'code': outcome.get('code', '') if isinstance(outcome, dict) else '',
                'description': description,
                'is_valid': validation.get('is_valid', True),
                'measurability_score': validation.get('measurability_score', 0),
                'bloom_level': validation.get('bloom_level', 'unknown'),
                'issues': validation.get('issues', []),
                'suggestions': validation.get('suggestions', []),
            }
            if not entry['is_valid']:
                issues_count += 1
            validated.append(entry)

        avg_measurability = 0.0
        if validated:
            avg_measurability = round(
                sum(v['measurability_score'] for v in validated) / len(validated), 2
            )

        return {
            'outcomes': validated,
            'total_outcomes': len(validated),
            'valid_outcomes': len(validated) - issues_count,
            'issues_count': issues_count,
            'average_measurability': avg_measurability,
        }
