
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.validation.nep_2020_validator import NEP2020Validator
from src.validation.accreditation_checker import AccreditationChecker

def test_validators_with_dict_topics():
    print("Testing Validators with Dict Topics...")
    
    # Mock data with DICT topics
    mock_syllabus = {
        "learning_outcomes": [
            {"code": "CO1", "description": "Apply AI concepts", "bloom_level": "Apply"},
            {"code": "CO2", "description": "Analyze datasets", "bloom_level": "Analyze"},
            {"code": "CO3", "description": "Create models", "bloom_level": "Create"},
            {"code": "CO4", "description": "Evaluate results", "bloom_level": "Evaluate"}
        ],
        "units": [
            {
                "title": "Introduction to AI",
                "topics": [
                    {"name": "History of AI", "btl": 1},
                    {"name": "Technology and Ethics", "btl": 2}
                ],
                "hours": 10
            },
            {
                "title": "Machine Learning",
                "topics": [
                    {"name": "Supervised Learning", "btl": 3},
                    {"name": "Unsupervised Learning", "btl": 3}
                ],
                "hours": 10
            }
        ],
        "co_po_mapping": {"CO1": {"PO1": 3}},
        "assessment_pattern": {"internal": 40, "external": 60}
    }

    # Test NEP Validator
    print("\n--- NEP 2020 Validator ---")
    nep = NEP2020Validator()
    # Mock guidelines if loading fails (likely will since config path might be relative)
    nep.guidelines = {
        'nep_2020_guidelines': {
            'multidisciplinary': {'min_percentage': 10},
            'skill_development': {'min_skill_outcomes': 2},
            'experiential_learning': {'min_components': 1, 'required_components': ['project', 'internship']},
            'assessment_pattern': {'formative_min': 30, 'formative_max': 50},
            'technology_integration': {},
        },
        'compliance_scoring': {'excellent': 90}
    }
    
    try:
        nep_result = nep.validate(mock_syllabus)
        print("NEP Validation Success!")
        print(f"Compliance Level: {nep_result.get('compliance_level')}")
    except Exception as e:
        print(f"FAILED NEP Validation: {e}")
        import traceback
        traceback.print_exc()

    # Test Accreditation Checker
    print("\n--- Accreditation Checker ---")
    accred = AccreditationChecker()
    # Mock config
    accred.config = {}
    
    try:
        nba_result = accred.check_nba_compliance(mock_syllabus)
        print("NBA Check Success!")
        print(f"NBA Level: {nba_result.get('compliance_level')}")
    except Exception as e:
        print(f"FAILED NBA Check: {e}")
        import traceback
        traceback.print_exc()
        
    try:
        naac_result = accred.check_naac_compliance(mock_syllabus)
        print("NAAC Check Success!")
        print(f"NAAC Level: {naac_result.get('compliance_level')}")
    except Exception as e:
        print(f"FAILED NAAC Check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_validators_with_dict_topics()
