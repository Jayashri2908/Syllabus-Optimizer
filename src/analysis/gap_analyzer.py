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

        # Flag unknown Bloom levels as a gap
        unknown_count = level_counts.get('unknown', 0)
        if unknown_count > 0 and total > 0:
            gaps.append({
                'level': 'unknown',
                'current': round((unknown_count / total) * 100, 1),
                'recommended': '0%',
                'issue': 'unknown_level',
                'count': unknown_count
            })

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
        total = 0
        for v in assessment.values():
            if isinstance(v, (int, float)):
                total += v
            elif isinstance(v, dict):
                total += v.get('weightage', 0)
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
        numeric_values = [v for v in assessment.values() if isinstance(v, (int, float))]
        if numeric_values:
            max_component = max(numeric_values)
            if max_component > 70:
                gaps.append({
                    'type': 'imbalanced',
                    'description': f'One component has {max_component}% weightage (too high)'
                })

        # Check continuous vs end-semester balance (NBA recommends 40% IA + 60% ESE)
        internal_total = 0
        external_total = 0
        if assessment:
            internal_keys = ['internal', 'continuous', 'ia', 'assignment', 'quiz', 'lab', 'project']
            external_keys = ['external', 'ese', 'end_semester', 'final']
            internal_total = sum(assessment.get(k, 0) for k in internal_keys if k in assessment and isinstance(assessment.get(k), (int, float)))
            external_total = sum(assessment.get(k, 0) for k in external_keys if k in assessment and isinstance(assessment.get(k), (int, float)))
            if internal_total > 0 and external_total > 0:
                if internal_total < 30:
                    gaps.append({
                        'type': 'low_continuous_assessment',
                        'current': internal_total,
                        'description': f'Continuous assessment is only {internal_total}% (NBA recommends 30-50%)'
                    })
                elif internal_total > 50:
                    gaps.append({
                        'type': 'high_continuous_assessment',
                        'current': internal_total,
                        'description': f'Continuous assessment is {internal_total}% (NBA recommends 30-50%)'
                    })

        return {
            'total_percentage': total,
            'components': assessment,
            'gaps': gaps,
            'internal_total': internal_total,
            'external_total': external_total
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

        # Check topic coverage vs course level
        course_level = syllabus_data.get('course_level', '').lower()
        total_topics = sum(len(unit.get('topics', [])) for unit in units)
        if course_level in ['undergraduate', 'ug', 'b.tech', 'b.e'] and total_topics < 15:
            gaps.append({
                'type': 'insufficient_topic_depth',
                'current_count': total_topics,
                'description': f'Only {total_topics} topics for an undergraduate course (15+ recommended)'
            })

        # Check keyword overlap between outcomes and unit topics
        outcomes = syllabus_data.get('learning_outcomes', [])
        if outcomes and units:
            outcome_text = ' '.join(
                o.get('description', '') if isinstance(o, dict) else str(o) for o in outcomes
            )
            unit_text = ' '.join(
                t.get('title', '') if isinstance(t, dict) else str(t)
                for u in units for t in u.get('topics', [])
            )
            outcome_kw = set(self.text_processor.extract_keywords(outcome_text, top_n=15))
            unit_kw = set(self.text_processor.extract_keywords(unit_text, top_n=15))
            if outcome_kw and unit_kw:
                overlap = len(outcome_kw & unit_kw) / len(outcome_kw | unit_kw)
                if overlap < 0.15:
                    gaps.append({
                        'type': 'outcome_content_misalignment',
                        'overlap': round(overlap, 3),
                        'description': f'Low keyword overlap between outcomes and unit topics ({overlap:.1%}) — outcomes may not be covered by content'
                    })

        return {
            'gaps': gaps,
            'total_units': len(units),
            'total_hours': total_hours,
            'reference_count': len(references),
            'total_topics': total_topics
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
        
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations with priority levels and specific details"""
        recommendations = []

        # Bloom's coverage recommendations
        bloom_gaps = report['bloom_coverage'].get('gaps', [])
        for gap in bloom_gaps:
            level = gap['level']
            issue = gap['issue']
            current = gap.get('current', 0)
            recommended = gap.get('recommended', 'N/A')
            if issue == 'underrepresented':
                recommendations.append({
                    'text': f"Add more learning outcomes at '{level}' level — currently {current:.1f}% (recommended: {recommended})",
                    'priority': 'medium',
                    'category': 'bloom_taxonomy',
                    'related_to': f"bloom_{level}"
                })
            elif issue == 'overrepresented':
                recommendations.append({
                    'text': f"Consider reducing '{level}' level outcomes — currently {current:.1f}% (recommended: {recommended})",
                    'priority': 'low',
                    'category': 'bloom_taxonomy',
                    'related_to': f"bloom_{level}"
                })

        # CO-PO mapping recommendations
        co_po_gaps = report['co_po_mapping_gaps'].get('gaps', [])
        if co_po_gaps:
            unmapped_cos = [g.get('co', 'unknown') for g in co_po_gaps if g['type'] == 'missing_co_mapping']
            empty_mapped = [g.get('co', 'unknown') for g in co_po_gaps if g['type'] == 'empty_mapping']
            detail_parts = []
            if unmapped_cos:
                detail_parts.append(f"unmapped: {', '.join(unmapped_cos[:5])}")
            if empty_mapped:
                detail_parts.append(f"empty mapping: {', '.join(empty_mapped[:5])}")
            recommendations.append({
                'text': f"Complete CO-PO mapping for all course outcomes ({'; '.join(detail_parts)})",
                'priority': 'high',
                'category': 'accreditation',
                'related_to': 'co_po_mapping'
            })

        # Assessment recommendations
        assessment_gaps = report['assessment_gaps'].get('gaps', [])
        for gap in assessment_gaps:
            if gap['type'] == 'total_mismatch':
                recommendations.append({
                    'text': f"Adjust assessment weightages — current total is {gap.get('current_total', 0)}% (must equal 100%)",
                    'priority': 'high',
                    'category': 'assessment',
                    'related_to': 'assessment_total'
                })
            elif gap['type'] == 'missing_component':
                recommendations.append({
                    'text': f"Add {gap['component']} assessment component to ensure comprehensive evaluation",
                    'priority': 'medium',
                    'category': 'assessment',
                    'related_to': f"assessment_{gap['component']}"
                })
            elif gap['type'] == 'imbalanced':
                recommendations.append({
                    'text': f"Rebalance assessment — one component has {gap.get('description', 'high')}% weightage",
                    'priority': 'medium',
                    'category': 'assessment',
                    'related_to': 'assessment_balance'
                })

        # Content recommendations
        content_gaps = report['content_gaps'].get('gaps', [])
        for gap in content_gaps:
            if gap['type'] == 'insufficient_references':
                current = gap.get('current_count', 0)
                recommended = gap.get('recommended_min', 3)
                recommendations.append({
                    'text': f"Add more reference materials — currently {current} (minimum {recommended} recommended)",
                    'priority': 'medium',
                    'category': 'content',
                    'related_to': 'references'
                })
            elif gap['type'] == 'missing_hours':
                recommendations.append({
                    'text': "Specify contact hours for each unit to ensure adequate time allocation",
                    'priority': 'high',
                    'category': 'structure',
                    'related_to': 'unit_hours'
                })
            elif gap['type'] == 'missing_component':
                component = gap.get('component', 'unknown')
                recommendations.append({
                    'text': f"Add missing essential component: {component}",
                    'priority': 'high',
                    'category': 'structure',
                    'related_to': f"missing_{component}"
                })

        # Outcome validation recommendations
        outcome_validation = report.get('outcome_validation', {})
        invalid_count = outcome_validation.get('issues_count', 0)
        if invalid_count > 0:
            invalid_outcomes = [o['code'] for o in outcome_validation.get('outcomes', []) if not o.get('is_valid', True)]
            recommendations.append({
                'text': f"{invalid_count} learning outcome(s) need improvement: {', '.join(invalid_outcomes[:5])} — use measurable action verbs and avoid vague terms",
                'priority': 'high',
                'category': 'outcome_quality',
                'related_to': 'outcome_validation'
            })
        avg_measurability = outcome_validation.get('average_measurability', 1)
        if avg_measurability < 0.5:
            recommendations.append({
                'text': f"Overall outcome measurability is low ({avg_measurability:.0%}) — rewrite outcomes with specific, assessable verbs",
                'priority': 'medium',
                'category': 'outcome_quality',
                'related_to': 'measurability'
            })

        # Structural issue recommendations
        structural_issues = report.get('structural_issues', [])
        for issue in structural_issues:
            recommendations.append({
                'text': issue.get('description', 'Structural issue detected'),
                'priority': issue.get('severity', 'medium'),
                'category': 'structure',
                'related_to': issue.get('type', 'structure')
            })

        # Redundancy recommendations
        redundancies = report.get('redundancies', {})
        if redundancies.get('total_redundancies', 0) > 0:
            pair_count = len(redundancies.get('redundant_pairs', []))
            dup_count = len(redundancies.get('duplicate_outcomes', []))
            recommendations.append({
                'text': f"Address {pair_count} overlapping unit pair(s) and {dup_count} duplicate outcome(s) to reduce content redundancy",
                'priority': 'medium',
                'category': 'content',
                'related_to': 'redundancy'
            })

        # Lesson plan recommendations
        lesson_gaps = report.get('lesson_plan_analysis', {}).get('gaps', [])
        for gap in lesson_gaps:
            recommendations.append({
                'text': gap.get('description', 'Lesson plan issue'),
                'priority': gap.get('severity', 'medium'),
                'category': 'lesson_plan',
                'related_to': gap.get('type', 'lesson_plan')
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
        """Calculate an overall quality score (0-100) from sub-analysis results with configurable weights."""
        weights = {
            'content_quality': 0.20,
            'bloom_coverage': 0.15,
            'co_po_mapping': 0.20,
            'assessment': 0.15,
            'structure': 0.15,
            'redundancy': 0.15,
        }

        scores = {}

        content_quality = report.get('content_quality', {})
        if content_quality:
            scores['content_quality'] = content_quality.get('overall_score', 0) * 100

        bloom_coverage = report.get('bloom_coverage', {})
        bloom_gaps = bloom_coverage.get('gaps', [])
        total_outcomes = bloom_coverage.get('total_outcomes', 0)
        if total_outcomes > 0:
            scores['bloom_coverage'] = max(0, 100 - len(bloom_gaps) * 15)

        co_po = report.get('co_po_mapping_gaps', {})
        scores['co_po_mapping'] = co_po.get('coverage_percentage', 0)

        assessment = report.get('assessment_gaps', {})
        assessment_gaps = assessment.get('gaps', [])
        if assessment.get('total_percentage') == 100 and not assessment_gaps:
            scores['assessment'] = 100
        elif assessment.get('total_percentage', 0) > 0:
            scores['assessment'] = max(0, 100 - len(assessment_gaps) * 20)
        else:
            scores['assessment'] = 50

        structural = report.get('structural_issues', [])
        scores['structure'] = max(0, 100 - len(structural) * 20)

        redundancies = report.get('redundancies', {})
        overlap = redundancies.get('overlap_score', 0)
        scores['redundancy'] = max(0, 100 - overlap * 100)

        weighted_sum = sum(scores.get(k, 0) * w for k, w in weights.items())
        total_weight = sum(w for k, w in weights.items() if k in scores)

        if total_weight > 0:
            return round(weighted_sum / total_weight, 1)
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
