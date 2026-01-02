"""
Domain-Specific Templates and Context
Provides rich, domain-specific context for better syllabus generation
"""

from typing import Dict, List, Any


# Comprehensive domain templates
DOMAIN_TEMPLATES = {
    "machine_learning": {
        "keywords": ["machine learning", "ml", "ai", "deep learning", "neural network", "tensorflow", "pytorch"],
        "industry_tools": ["TensorFlow", "PyTorch", "scikit-learn", "Keras", "Pandas", "NumPy"],
        "programming_languages": ["Python", "R", "Julia"],
        "key_skills": [
            "Model training and evaluation",
            "Feature engineering and selection",
            "Hyperparameter tuning",
            "Model deployment (MLOps)",
            "Data preprocessing and augmentation"
        ],
        "prerequisites": ["Linear Algebra", "Probability & Statistics", "Python Programming", "Calculus"],
        "applications": [
            "Recommendation systems",
            "Computer vision and image recognition",
            "Natural language processing",
            "Predictive analytics and forecasting",
            "Anomaly detection"
        ],
        "textbook_authors": ["Ian Goodfellow", "Andrew Ng", "Sebastian Raschka", "Aurélien Géron"],
        "career_paths": ["ML Engineer", "Data Scientist", "AI Researcher", "MLOps Engineer"]
    },
    
    "web_development": {
        "keywords": ["web", "frontend", "backend", "full stack", "react", "node", "javascript"],
        "industry_tools": ["React", "Node.js", "Express", "MongoDB", "PostgreSQL", "Docker"],
        "programming_languages": ["JavaScript", "TypeScript", "HTML/CSS"],
        "key_skills": [
            "Frontend framework development",
            "RESTful API design",
            "Database design and optimization",
            "Authentication and security",
            "Cloud deployment and DevOps"
        ],
        "prerequisites": ["HTML/CSS", "JavaScript Fundamentals", "HTTP/Networks"],
        "applications": [
            "E-commerce platforms",
            "Social media applications",
            "Content management systems",
            "SaaS products",
            "Progressive web apps"
        ],
        "textbook_authors": ["Kyle Simpson", "David Flanagan", "Marijn Haverbeke"],
        "career_paths": ["Full Stack Developer", "Frontend Engineer", "Backend Developer", "Web Architect"]
    },
    
    "data_science": {
        "keywords": ["data science", "data analytics", "big data", "visualization", "analytics"],
        "industry_tools": ["Python", "Pandas", "NumPy", "Jupyter", "Tableau", "Power BI", "Spark"],
        "programming_languages": ["Python", "R", "SQL"],
        "key_skills": [
            "Data wrangling and cleaning",
            "Statistical analysis",
            "Data visualization",
            "Exploratory data analysis",
            "Big data processing"
        ],
        "prerequisites": ["Statistics", "Python/R Programming", "SQL", "Mathematics"],
        "applications": [
            "Business intelligence dashboards",
            "Market analysis and segmentation",
            "Customer behavior analytics",
            "Financial forecasting",
            "Healthcare analytics"
        ],
        "textbook_authors": ["Wes McKinney", "Joel Grus", "Jake VanderPlas"],
        "career_paths": ["Data Scientist", "Data Analyst", "Business Intelligence Analyst", "Analytics Manager"]
    },
    
    "cybersecurity": {
        "keywords": ["security", "cyber", "cryptography", "network security", "ethical hacking", "penetration"],
        "industry_tools": ["Wireshark", "Metasploit", "Nmap", "Burp Suite", "Kali Linux"],
        "programming_languages": ["Python", "Bash", "PowerShell", "C/C++"],
        "key_skills": [
            "Threat detection and analysis",
            "Penetration testing",
            "Security auditing",
            "Incident response",
            "Cryptographic protocols"
        ],
        "prerequisites": ["Networking Fundamentals", "Operating Systems", "Programming"],
        "applications": [
            "Network intrusion detection",
            "Application security testing",
            "Cloud security architecture",
            "Compliance and governance",
            "Security operations centers (SOC)"
        ],
        "textbook_authors": ["William Stallings", "Bruce Schneier", "Kevin Mitnick"],
        "career_paths": ["Security Analyst", "Penetration Tester", "Security Architect", "CISO"]
    },
    
    "database": {
        "keywords": ["database", "sql", "nosql", "mongodb", "mysql", "postgresql", "data modeling"],
        "industry_tools": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Oracle", "SQL Server"],
        "programming_languages": ["SQL", "Python", "Java"],
        "key_skills": [
            "Database design and normalization",
            "Query optimization",
            "Transaction management",
            "NoSQL databases",
            "Database administration"
        ],
        "prerequisites": ["Data Structures", "Basic SQL", "Algorithms"],
        "applications": [
            "Enterprise data management",
            "E-commerce transaction systems",
            "Data warehousing",
            "Real-time analytics platforms",
            "Content management backends"
        ],
        "textbook_authors": ["Ramez Elmasri", "Abraham Silberschatz", "C.J. Date"],
        "career_paths": ["Database Administrator", "Data Engineer", "Database Developer", "Data Architect"]
    },
    
    "cloud_computing": {
        "keywords": ["cloud", "aws", "azure", "gcp", "devops", "kubernetes", "docker", "microservices"],
        "industry_tools": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins"],
        "programming_languages": ["Python", "Go", "Bash", "YAML"],
        "key_skills": [
            "Cloud architecture design",
            "Container orchestration",
            "CI/CD pipelines",
            "Infrastructure as Code",
            "Cloud security"
        ],
        "prerequisites": ["Linux/Unix", "Networking", "Programming"],
        "applications": [
            "Scalable web applications",
            "Microservices architectures",
            "Serverless computing",
            "Cloud-native applications",
            "Multi-cloud deployments"
        ],
        "textbook_authors": ["Thomas Erl", "Sam Newman", "Gene Kim"],
        "career_paths": ["Cloud Architect", "DevOps Engineer", "Site Reliability Engineer", "Cloud Consultant"]
    },
    
    "mobile_development": {
        "keywords": ["mobile", "android", "ios", "react native", "flutter", "swift", "kotlin"],
        "industry_tools": ["Android Studio", "Xcode", "React Native", "Flutter", "Firebase"],
        "programming_languages": ["Kotlin", "Swift", "JavaScript/TypeScript", "Dart"],
        "key_skills": [
            "Mobile UI/UX design",
            "Platform-specific APIs",
            "Cross-platform development",
            "Mobile performance optimization",
            "App store deployment"
        ],
        "prerequisites": ["Object-Oriented Programming", "UI/UX Basics", "APIs"],
        "applications": [
            "Consumer mobile apps",
            "Location-based services",
            "Mobile gaming",
            "Enterprise mobile solutions",
            "IoT companion apps"
        ],
        "textbook_authors": ["Bill Phillips", "Ray Wenderlich", "Frank McCown"],
        "career_paths": ["Mobile Developer", "iOS Developer", "Android Developer", "Mobile Architect"]
    },
    
    "computer_networks": {
        "keywords": ["network", "tcp/ip", "routing", "protocols", "osi", "networking"],
        "industry_tools": ["Cisco Packet Tracer", "Wireshark", "GNS3", "NetFlow"],
        "programming_languages": ["Python", "C", "Java"],
        "key_skills": [
            "Network protocol analysis",
            "Routing and switching",
            "Network security",
            "QoS and traffic management",
            "Wireless networking"
        ],
        "prerequisites": ["Computer Architecture", "Operating Systems"],
        "applications": [
            "Enterprise network infrastructure",
            "IoT network design",
            "Cloud networking",
            "Software-defined networking (SDN)",
            "5G networks"
        ],
        "textbook_authors": ["James Kurose", "Andrew Tanenbaum", "Behrouz Forouzan"],
        "career_paths": ["Network Engineer", "Network Architect", "Network Administrator", "Network Security Specialist"]
    }
}


def detect_domain(course_title: str, keywords: List[str]) -> str:
    """
    Auto-detect domain from course title and keywords
    
    Returns:
        Domain identifier (e.g., 'machine_learning', 'web_development')
    """
    # Combine title and keywords for matching
    search_text = f"{course_title} {' '.join(keywords)}".lower()
    
    # Score each domain
    domain_scores = {}
    
    for domain_id, template in DOMAIN_TEMPLATES.items():
        score = 0
        domain_keywords = template.get('keywords', [])
        
        # Check how many domain keywords match
        for keyword in domain_keywords:
            if keyword in search_text:
                score += 1
        
        domain_scores[domain_id] = score
    
    # Return domain with highest score, or 'general' if no match
    if max(domain_scores.values()) > 0:
        return max(domain_scores, key=domain_scores.get)
    else:
        return 'general'


def get_domain_context(domain_id: str) -> Dict[str, Any]:
    """
    Get complete context for a domain
    
    Args:
        domain_id: Domain identifier
        
    Returns:
        Domain context dictionary
    """
    return DOMAIN_TEMPLATES.get(domain_id, {
        "industry_tools": ["Modern development tools"],
        "key_skills": ["Problem solving", "Critical thinking"],
        "prerequisites": ["Basic fundamentals"],
        "applications": ["Industry applications"],
        "career_paths": ["Technical Professional"]
    })


def get_domain_tools(domain_id: str) -> List[str]:
    """Get industry tools for domain"""
    return get_domain_context(domain_id).get('industry_tools', [])


def get_domain_skills(domain_id: str) -> List[str]:
    """Get key skills for domain"""
    return get_domain_context(domain_id).get('key_skills', [])


def get_domain_applications(domain_id: str) -> List[str]:
    """Get applications for domain"""
    return get_domain_context(domain_id).get('applications', [])


def get_domain_careers(domain_id: str) -> List[str]:
    """Get career paths for domain"""
    return get_domain_context(domain_id).get('career_paths', [])


def get_domain_prerequisites(domain_id: str) -> List[str]:
    """Get prerequisites for domain"""
    return get_domain_context(domain_id).get('prerequisites', [])
