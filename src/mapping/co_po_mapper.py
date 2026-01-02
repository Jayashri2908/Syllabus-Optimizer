"""
CO-PO Mapper for SCDO
Maps Course Outcomes to Program Outcomes
"""

from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path
import logging

from ..utils.text_processing import TextProcessor


class COPOMapper:
    """Map Course Outcomes to Program Outcomes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        self.accreditation = self._load_accreditation_standards()
        
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
        Map course outcomes to program outcomes
        
        Args:
            course_outcomes: List of course outcomes with descriptions
            program_outcomes: List of PO codes (defaults to NBA engineering POs)
            domain: Academic domain
            
        Returns:
            CO-PO mapping matrix
        """
        if program_outcomes is None:
            # Use NBA engineering POs by default
            program_outcomes = [f'PO{i}' for i in range(1, 13)]
            
        mapping = {}
        
        for co in course_outcomes:
            co_code = co.get('code', '')
            co_description = co.get('description', '')
            bloom_level = co.get('bloom_level', 'unknown')
            
            # Map to each PO
            po_mapping = {}
            for po_code in program_outcomes:
                correlation = self._calculate_correlation(
                    co_description, bloom_level, po_code, domain
                )
                if correlation > 0:
                    po_mapping[po_code] = correlation
                    
            mapping[co_code] = po_mapping
            
        return mapping
        
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
