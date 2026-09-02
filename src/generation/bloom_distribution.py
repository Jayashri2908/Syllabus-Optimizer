"""
Bloom's Taxonomy Distribution Enforcer
Ensures proper distribution of learning outcomes across Bloom's levels
"""

from typing import Dict, List


# Recommended distributions for different course types
BLOOM_DISTRIBUTIONS = {
    "introductory": {
        "remember": 2,
        "understand": 2,
        "apply": 1,
        "analyze": 0,
        "evaluate": 0,
        "create": 0
    },
    "intermediate": {
        "remember": 1,
        "understand": 1,
        "apply": 2,
        "analyze": 1,
        "evaluate": 0,
        "create": 0
    },
    "advanced": {
        "remember": 0,
        "understand": 1,
        "apply": 1,
        "analyze": 2,
        "evaluate": 1,
        "create": 1
    }
}


def get_bloom_distribution(course_level: str, num_outcomes: int) -> Dict[str, int]:
    """
    Get Bloom's distribution based on course level
    
    Args:
        course_level: "Introductory/Beginner", "Intermediate/Undergraduate", or "Advanced/Graduate"
        num_outcomes: Total number of outcomes needed
        
    Returns:
        Dictionary with recommended count per Bloom's level
    """
    # Map course level to distribution template
    if "Advanced" in course_level or "Graduate" in course_level:
        template = BLOOM_DISTRIBUTIONS["advanced"]
    elif "Intro" in course_level or "Beginner" in course_level:
        template = BLOOM_DISTRIBUTIONS["introductory"]
    else:
        template = BLOOM_DISTRIBUTIONS["intermediate"]
    
    # Scale template to match num_outcomes
    total_template = sum(template.values())
    
    if total_template == 0:
        # Fallback
        return {"remember": 1, "understand": 1, "apply": num_outcomes - 2}
    
    # Scale proportionally
    distribution = {}
    allocated = 0
    
    for level, count in template.items():
        scaled = round((count / total_template) * num_outcomes)
        distribution[level] = scaled
        allocated += scaled
    
    # Adjust for rounding errors
    diff = num_outcomes - allocated
    if diff > 0:
        # Add to middle levels (Apply)
        distribution["apply"] = distribution.get("apply", 0) + diff
    elif diff < 0:
        # Remove from lower levels
        for level in ["remember", "understand", "apply"]:
            if distribution.get(level, 0) > 0:
                distribution[level] -= abs(diff)
                break
    
    return distribution


def format_distribution_for_prompt(distribution: Dict[str, int]) -> str:
    """Format distribution as human-readable string for prompt"""
    parts = []
    for level, count in distribution.items():
        if count > 0:
            parts.append(f"{count} {level.capitalize()}")
    return ", ".join(parts)


def get_bloom_verb_list(level: str) -> List[str]:
    """Get list of Bloom's verbs for a level"""
    BLOOM_VERBS = {
        'remember': ['Define', 'Label', 'List', 'Name', 'Recall', 'Recognize', 'State'],
        'understand': ['Describe', 'Explain', 'Summarize', 'Classify', 'Identify', 'Infer', 'Predict', 'Outline'],
        'apply': ['Apply', 'Calculate', 'Execute', 'Implement', 'Solve', 'Use', 'Demonstrate', 'Compute'],
        'analyze': ['Analyze', 'Compare', 'Contrast', 'Differentiate', 'Examine', 'Investigate', 'Categorize', 'Distinguish'],
        'evaluate': ['Evaluate', 'Assess', 'Critique', 'Judge', 'Justify', 'Rank', 'Recommend', 'Choose', 'Select'],
        'create': ['Design', 'Develop', 'Create', 'Formulate', 'Construct', 'Compose', 'Generate', 'Plan', 'Produce', 'Devise']
    }
    return BLOOM_VERBS.get(level.lower(), [])
