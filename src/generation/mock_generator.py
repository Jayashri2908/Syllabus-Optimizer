from typing import List, Optional

class MockSyllabusGenerator:
    """Fallback generator when AI services are unavailable"""
    
    def generate(self, course_title: str, course_code: str, credits: str,
                 program_outcomes: List[str], keywords: List[str],
                 domain: str = "engineering", num_units: int = 5,
                 num_outcomes: int = 5):
        
        return {
            "course_title": course_title,
            "course_code": course_code,
            "credits": credits,
            "objectives": [
                f"Understand the fundamental principles of {course_title}",
                "Develop problem-solving skills in relevant domains",
                "Gain hands-on experience through practical applications",
                "Analyze recent trends and developments in the field"
            ],
            "learning_outcomes": [
                {
                    "code": f"CO{i+1}",
                    "description": outcome,
                    "bloom_level": level
                }
                for i, (outcome, level) in enumerate([
                    (f"Identify key concepts in {course_title}", "Remember"),
                    (f"Analyze problems related to {keywords[0] if keywords else 'subject'}", "Analyze"),
                    ("Apply theoretical knowledge to practical scenarios", "Apply"),
                    ("Evaluate different approaches to problem solving", "Evaluate"),
                    ("Create a project demonstrating course mastery", "Create")
                ])
            ],
            "units": [
                {
                    "unit_number": i + 1,
                    "title": self._get_unit_title(i, num_units, keywords, course_title),
                    "topics": self._get_topics_for_domain(domain, keywords, i),
                    "hours": 8
                }
                for i in range(num_units)
            ],
            "textbooks": [
                f"Fundamentals of {course_title} by Author A",
                f"Advanced {course_title} by Author B"
            ],
            "references": [
                "IEEE Transactions on Education",
                "Online Course Materials"
            ]
        }

    def _get_unit_title(self, index: int, total: int, keywords: List[str], title: str) -> str:
        if index == 0:
            return f"Introduction to {title}"
        elif index == total - 1:
            return f"Advanced Topics and Future Trends in {title}"
        else:
            k = keywords[index % len(keywords)] if keywords else "Core Concepts"
            return f"{k.title()} and its Applications"

    def _get_topics_for_domain(self, domain: str, keywords: List[str], unit_idx: int) -> List[str]:
        # Intelligent Subject Detection
        # Check course title/keywords to pick the best template
        
        # Extended Templates
        templates = {
            # Mathematics
            "math": [
                "Theorem proofs and corollaries",
                "Computational methods and algorithms",
                "Differential equations and modeling",
                "Vector spaces and linear transformations",
                "Statistical inference and probability",
                "Numerical analysis techniques",
                "Optimization problems"
            ],
            # Computer Science
            "cs": [
                "Data structures implementation",
                "Algorithm complexity analysis",
                "Object-oriented design patterns",
                "Database normalization forms",
                "Network protocols and security",
                "Cloud computing architectures",
                "Machine learning pipelines"
            ],
            # Electronics / Hardware
            "electronics": [
                "Circuit analysis and design",
                "Signal processing algorithms",
                "Embedded system architecture",
                "Power management systems",
                "Digital logic gates",
                "Sensor integration",
                "VLSI design principles"
            ],
            # Fallback Engineering
            "engineering": [
                "System design requirements",
                "Performance benchmarks",
                "Safety standards and compliance",
                "Scalability analysis",
                "Integration testing",
                "Project lifecycle management",
                "Case study: Industry application"
            ]
        }
        
        # Decide which template to use based on context
        context_str = " ".join(keywords).lower()
        if any(x in context_str for x in ['calc', 'math', 'stat', 'gebra', 'diff', 'integral']):
            chosen_key = "math"
        elif any(x in context_str for x in ['data', 'soft', 'algo', 'compute', 'program', 'python', 'java', 'web']):
            chosen_key = "cs"
        elif any(x in context_str for x in ['circuit', 'signal', 'volt', 'embed', 'hardw', 'sensor']):
            chosen_key = "electronics"
        else:
            # Fallback to general domain mapping
            chosen_key = domain.lower() if domain.lower() in templates else "engineering"

        chosen_templates = templates.get(chosen_key, templates["engineering"])
        
        # Create varied sentence structures
        current_keyword = keywords[unit_idx % len(keywords)] if keywords else "Core Concept"
        
        # Rotate through different topic formats
        formats = [
            f"Introduction to {current_keyword}: Theory and Practice",
            f"Advanced applications of {current_keyword}",
            f"{current_keyword} in modern systems",
            f"Critical analysis of {current_keyword}",
            f"Design principles for {current_keyword}",
            f"Solving problems using {current_keyword}"
        ]
        
        unit_topics = [
            formats[unit_idx % len(formats)], # Varied keyword topic
            chosen_templates[unit_idx % len(chosen_templates)], # Domain specific topic
            chosen_templates[(unit_idx + 1) % len(chosen_templates)], # Another domain topic
            f"Case Study: {current_keyword} in real-world scenarios"
        ]
        
        return unit_topics
