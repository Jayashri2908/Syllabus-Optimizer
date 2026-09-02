"""
CO-PO Mapper for SCDO
Maps Course Outcomes to Program Outcomes with LLM semantic analysis
"""

from typing import Dict, List, Any, Optional
import json
import yaml
from pathlib import Path
import logging

from ..utils.text_processing import TextProcessor

try:
    from ..ai.model_manager import ModelManager
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class COPOMapper:
    """Map Course Outcomes to Program Outcomes"""
    
    def __init__(self, model_manager=None):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        self.accreditation = self._load_accreditation_standards()
        self.ai = model_manager
        self._ai_initialized = False
        
    def _ensure_ai(self):
        if self._ai_initialized:
            return
        self._ai_initialized = True
        if self.ai is None and AI_AVAILABLE:
            try:
                config_path = Path(__file__).parent.parent.parent / "configs" / "ai_models.yaml"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                else:
                    config = {}
                self.ai = ModelManager(config)
            except Exception as e:
                self.logger.debug(f"AI model not available for CO-PO mapping: {e}")
                self.ai = None
        
    def _load_accreditation_standards(self) -> dict:
        """Load accreditation standards"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "accreditation.yaml"
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
            
    def map_co_to_po(
        self,
        course_outcomes: List[Dict[str, str]],
        program_outcomes: Optional[List[str]] = None,
        domain: str = "engineering"
    ) -> Dict[str, Dict[str, int]]:
        """
        Map course outcomes to program outcomes using LLM when available,
        falling back to rule-based keyword matching.
        """
        if program_outcomes is None:
            program_outcomes = [f'PO{i}' for i in range(1, 13)]
        
        self._ensure_ai()
        
        if self.ai is not None:
            try:
                semantic_mapping = self._map_co_to_po_semantic(
                    course_outcomes, program_outcomes, domain
                )
                if semantic_mapping:
                    return semantic_mapping
            except Exception as e:
                self.logger.warning(f"Semantic CO-PO mapping failed, using rule-based: {e}")
        
        return self._map_co_to_po_rule_based(course_outcomes, program_outcomes, domain)
    
    def _map_co_to_po_rule_based(
        self,
        course_outcomes: List[Dict[str, str]],
        program_outcomes: List[str],
        domain: str
    ) -> Dict[str, Dict[str, int]]:
        """Rule-based CO-PO mapping using keyword matching and Bloom's affinity"""
        mapping = {}
        for co in course_outcomes:
            co_code = co.get('code', '')
            co_description = co.get('description', '')
            bloom_level = co.get('bloom_level', 'unknown')
            po_mapping = {}
            for po_code in program_outcomes:
                correlation = self._calculate_correlation(
                    co_description, bloom_level, po_code, domain
                )
                if correlation > 0:
                    po_mapping[po_code] = correlation
            mapping[co_code] = po_mapping
        return mapping
    
    def _map_co_to_po_semantic(
        self,
        course_outcomes: List[Dict[str, str]],
        program_outcomes: List[str],
        domain: str
    ) -> Optional[Dict[str, Dict[str, int]]]:
        """LLM-based semantic CO-PO mapping"""
        po_descriptions = {}
        for po_code in program_outcomes:
            po_data = self._get_po_description(po_code, domain)
            if po_data:
                po_descriptions[po_code] = po_data.get('description', '')
        
        if not po_descriptions:
            return None
        
        co_list = []
        for co in course_outcomes:
            co_list.append({
                'code': co.get('code', ''),
                'description': co.get('description', ''),
                'bloom_level': co.get('bloom_level', '')
            })
        
        po_list = [{'code': k, 'description': v} for k, v in po_descriptions.items()]
        
        prompt = f"""Map each Course Outcome (CO) to Program Outcomes (PO) based on semantic alignment.

COURSE OUTCOMES:
{json.dumps(co_list, indent=2)}

PROGRAM OUTCOMES:
{json.dumps(po_list, indent=2)}

For each CO, assign a correlation level (0-3) to each PO:
- 0: No correlation
- 1: Low correlation (tangentially related)
- 2: Medium correlation (partially addresses the PO)
- 3: High correlation (directly addresses the PO)

Rules:
- A CO should map to 2-5 POs with correlation >= 1
- Only assign non-zero correlation where there is genuine alignment
- Consider both the CO description content AND Bloom's taxonomy level

Respond with ONLY valid JSON:
{{"CO1": {{"PO1": 3, "PO2": 1, "PO5": 2}}, "CO2": {{"PO1": 1, "PO3": 3}}}}"""

        response = self.ai.generate_json(
            prompt=prompt,
            system_prompt="You are an expert in Outcome-Based Education and NBA accreditation. Map course outcomes to program outcomes based on semantic content alignment.",
            task_type='analysis',
            temperature=0.2,
            max_tokens=1500,
            max_retries=1
        )
        
        if not response:
            return None
        
        mapping = {}
        for co_code, po_dict in response.items():
            if isinstance(po_dict, dict):
                cleaned = {}
                for po_code, level in po_dict.items():
                    try:
                        level_int = int(level)
                        if 0 <= level_int <= 3 and level_int > 0:
                            cleaned[po_code] = level_int
                    except (ValueError, TypeError):
                        continue
                if cleaned:
                    mapping[co_code] = cleaned
        
        return mapping if mapping else None
        
    def _calculate_correlation(
        self,
        co_description: str,
        bloom_level: str,
        po_code: str,
        domain: str
    ) -> int:
        """
        Calculate correlation level between CO and PO
        
        Returns:
            0 (no correlation), 1 (low), 2 (medium), 3 (high)
        """
        # Get PO description
        po_data = self._get_po_description(po_code, domain)
        if not po_data:
            return 0
            
        po_description = po_data.get('description', '').lower()
        co_lower = co_description.lower()
        
        # Keyword matching
        correlation_score = 0
        
        # Extract keywords from PO description
        po_keywords = self.text_processor.extract_keywords(po_description, top_n=5)
        co_keywords = self.text_processor.extract_keywords(co_lower, top_n=5)
        
        # Count keyword matches
        matches = len(set(po_keywords) & set(co_keywords))
        
        # Specific PO mappings based on Bloom's level
        bloom_po_affinity = {
            'remember': ['PO1'],  # Engineering knowledge
            'understand': ['PO1', 'PO2'],  # Knowledge and problem analysis
            'apply': ['PO3', 'PO5'],  # Design and modern tools
            'analyze': ['PO2', 'PO4'],  # Problem analysis and investigation
            'evaluate': ['PO4', 'PO6', 'PO8'],  # Investigation, society, ethics
            'create': ['PO3', 'PO4'],  # Design and investigation
        }
        
        # Check Bloom's affinity
        if po_code in bloom_po_affinity.get(bloom_level, []):
            correlation_score += 1
            
        # Add keyword match score
        if matches >= 3:
            correlation_score += 2
        elif matches >= 2:
            correlation_score += 1
            
        # Specific keyword checks for each PO
        po_specific_keywords = {
            'PO1': ['knowledge', 'mathematics', 'science', 'engineering', 'fundamentals'],
            'PO2': ['problem', 'analyze', 'formulate', 'identify'],
            'PO3': ['design', 'develop', 'solution', 'system'],
            'PO4': ['research', 'investigate', 'experiment', 'data'],
            'PO5': ['tool', 'technology', 'software', 'modern'],
            'PO6': ['society', 'social', 'health', 'safety', 'legal'],
            'PO7': ['environment', 'sustainability', 'impact'],
            'PO8': ['ethics', 'professional', 'responsibility'],
            'PO9': ['team', 'collaborate', 'group', 'leader'],
            'PO10': ['communicate', 'present', 'report', 'document'],
            'PO11': ['project', 'management', 'finance', 'plan'],
            'PO12': ['learning', 'lifelong', 'independent', 'self']
        }
        
        keywords = po_specific_keywords.get(po_code, [])
        if any(keyword in co_lower for keyword in keywords):
            correlation_score += 1
            
        # Cap at 3
        return min(correlation_score, 3)
        
    def _get_po_description(self, po_code: str, domain: str) -> Optional[Dict[str, str]]:
        """Get PO description from accreditation standards"""
        if domain == "engineering":
            pos = self.accreditation.get('nba', {}).get('program_outcomes', {}).get('engineering', {})
            return pos.get(po_code)
        return None
        
    def generate_mapping_matrix(
        self,
        co_po_mapping: Dict[str, Dict[str, int]]
    ) -> str:
        """
        Generate formatted CO-PO mapping matrix
        
        Args:
            co_po_mapping: CO-PO mapping dictionary
            
        Returns:
            Formatted matrix as string
        """
        if not co_po_mapping:
            return "No mapping available"
            
        # Get all POs
        all_pos = set()
        for po_dict in co_po_mapping.values():
            all_pos.update(po_dict.keys())
        all_pos = sorted(all_pos)
        
        # Create header
        header = "CO\t" + "\t".join(all_pos)
        lines = [header]
        lines.append("-" * len(header))
        
        # Add rows
        for co, po_dict in sorted(co_po_mapping.items()):
            row = [co]
            for po in all_pos:
                value = po_dict.get(po, 0)
                row.append(str(value) if value > 0 else "-")
            lines.append("\t".join(row))
            
        return "\n".join(lines)
        
    def calculate_po_attainment(
        self,
        co_po_mapping: Dict[str, Dict[str, int]],
        co_attainment: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate PO attainment based on CO attainment
        
        Args:
            co_po_mapping: CO-PO mapping matrix
            co_attainment: CO attainment levels (0-1 scale)
            
        Returns:
            PO attainment levels
        """
        po_attainment = {}
        po_counts = {}
        
        for co, po_dict in co_po_mapping.items():
            co_att = co_attainment.get(co, 0.0)
            
            for po, correlation in po_dict.items():
                if correlation > 0:
                    # Weighted contribution
                    contribution = (correlation / 3.0) * co_att
                    
                    po_attainment[po] = po_attainment.get(po, 0.0) + contribution
                    po_counts[po] = po_counts.get(po, 0) + 1
                    
        # Average attainment
        for po in po_attainment:
            if po_counts[po] > 0:
                po_attainment[po] /= po_counts[po]
                
        return po_attainment
        
    def validate_mapping(
        self,
        co_po_mapping: Dict[str, Dict[str, int]]
    ) -> Dict[str, Any]:
        """
        Validate CO-PO mapping completeness
        
        Args:
            co_po_mapping: CO-PO mapping matrix
            
        Returns:
            Validation report
        """
        issues = []
        
        # Check if all COs have at least one PO mapping
        for co, po_dict in co_po_mapping.items():
            if not po_dict or all(v == 0 for v in po_dict.values()):
                issues.append(f"{co} has no PO mappings")
                
        # Check PO coverage
        all_pos = set()
        for po_dict in co_po_mapping.values():
            all_pos.update(k for k, v in po_dict.items() if v > 0)
            
        expected_pos = {f'PO{i}' for i in range(1, 13)}
        missing_pos = expected_pos - all_pos
        
        if missing_pos:
            issues.append(f"POs not covered: {', '.join(sorted(missing_pos))}")
            
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'po_coverage': len(all_pos) / 12 * 100,
            'total_cos': len(co_po_mapping)
        }
