"""
Industry Skills and Job Market Data
Provides real industry requirements for better career alignment
"""

from typing import Dict, List


# Industry skills data based on job market analysis
INDUSTRY_SKILLS = {
    "machine_learning": {
        "hot_skills": [
            "Deep Learning (PyTorch/TensorFlow)",
            "MLOps and Model Deployment",
            "Feature Engineering",
            "Computer Vision (OpenCV, YOLO)",
            "NLP (Transformers, BERT, GPT)",
            "Time Series Forecasting",
            "A/B Testing and Experimentation"
        ],
        "certifications": [
            "TensorFlow Developer Certificate",
            "AWS Machine Learning Specialty",
            "Google Cloud ML Engineer"
        ],
        "avg_salary_range": "$95,000 - $165,000",
        "job_growth": "22% (Much faster than average)",
        "top_companies": ["Google", "Meta", "Amazon", "Microsoft", "NVIDIA"]
    },
    
    "web_development": {
        "hot_skills": [
            "React.js and Next.js",
            "Node.js and Express",
            "TypeScript",
            "GraphQL APIs",
            "Cloud Deployment (AWS/Vercel)",
            "Docker and Kubernetes",
            "CI/CD Pipelines"
        ],
        "certifications": [
            "AWS Certified Developer",
            "Meta Front-End Developer",
            "MongoDB Certified Developer"
        ],
        "avg_salary_range": "$75,000 - $135,000",
        "job_growth": "13% (Faster than average)",
        "top_companies": ["Meta", "Netflix", "Shopify", "Stripe", "Vercel"]
    },
    
    "data_science": {
        "hot_skills": [
            "Python (Pandas, NumPy, Scikit-learn)",
            "SQL and Database Management",
            "Data Visualization (Tableau, Power BI)",
            "Statistical Analysis",
            "Big Data (Spark, Hadoop)",
            "Cloud Platforms (AWS, Azure, GCP)",
            "Business Intelligence"
        ],
        "certifications": [
            "Google Data Analytics Certificate",
            "Microsoft Certified: Data Analyst",
            "Tableau Desktop Specialist"
        ],
        "avg_salary_range": "$85,000 - $140,000",
        "job_growth": "28% (Much faster than average)",
        "top_companies": ["Amazon", "Meta", "Uber", "Airbnb", "Netflix"]
    },
    
    "cybersecurity": {
        "hot_skills": [
            "Penetration Testing (Metasploit, Burp Suite)",
            "SIEM Tools (Splunk, QRadar)",
            "Cloud Security (AWS, Azure)",
            "Incident Response",
            "Zero Trust Architecture",
            "Security Compliance (GDPR, HIPAA)",
            "Threat Hunting"
        ],
        "certifications": [
            "CISSP (Certified Information Systems Security Professional)",
            "CEH (Certified Ethical Hacker)",
            "CompTIA Security+",
            "OSCP (Offensive Security Certified Professional)"
        ],
        "avg_salary_range": "$90,000 - $155,000",
        "job_growth": "33% (Much faster than average)",
        "top_companies": ["Palo Alto Networks", "CrowdStrike", "Cisco", "IBM", "Amazon"]
    },
    
    "cloud_computing": {
        "hot_skills": [
            "AWS Services (EC2, S3, Lambda)",
            "Azure and GCP",
            "Kubernetes Orchestration",
            "Infrastructure as Code (Terraform)",
            "Serverless Architecture",
            "CI/CD (Jenkins, GitLab CI)",
            "Monitoring (Prometheus, Grafana)"
        ],
        "certifications": [
            "AWS Solutions Architect",
            "Azure Solutions Architect Expert",
            "Google Cloud Professional Architect",
            "Kubernetes (CKA, CKAD)"
        ],
        "avg_salary_range": "$100,000 - $170,000",
        "job_growth": "22% (Much faster than average)",
        "top_companies": ["AWS", "Microsoft", "Google Cloud", "IBM", "Oracle"]
    },
    
    "mobile_development": {
        "hot_skills": [
            "React Native / Flutter",
            "Swift (iOS Development)",
            "Kotlin (Android Development)",
            "Mobile UI/UX Design",
            "Firebase / Backend Integration",
            "App Store Optimization",
            "Mobile Performance Optimization"
        ],
        "certifications": [
            "Google Associate Android Developer",
            "Meta React Native Developer",
            "Flutter Development Bootcamp"
        ],
        "avg_salary_range": "$80,000 - $145,000",
        "job_growth": "18% (Faster than average)",
        "top_companies": ["Meta", "Uber", "DoorDash", "Airbnb", "Spotify"]
    }
}


def get_industry_skills(domain: str) -> List[str]:
    """Get hot skills for a domain"""
    return INDUSTRY_SKILLS.get(domain, {}).get('hot_skills', [])


def get_industry_certifications(domain: str) -> List[str]:
    """Get relevant certifications"""
    return INDUSTRY_SKILLS.get(domain, {}).get('certifications', [])


def get_salary_range(domain: str) -> str:
    """Get average salary range"""
    return INDUSTRY_SKILLS.get(domain, {}).get('avg_salary_range', 'Competitive salary')


def get_job_growth(domain: str) -> str:
    """Get job growth projection"""
    return INDUSTRY_SKILLS.get(domain, {}).get('job_growth', 'Positive growth')


def get_top_companies(domain: str) -> List[str]:
    """Get top hiring companies"""
    return INDUSTRY_SKILLS.get(domain, {}).get('top_companies', [])


def format_industry_context(domain: str) -> str:
    """Format industry context for prompts"""
    skills = get_industry_skills(domain)
    certs = get_industry_certifications(domain)
    companies = get_top_companies(domain)
    
    context = []
    
    if skills:
        context.append(f"Hot Skills: {', '.join(skills[:5])}")
    if companies:
        context.append(f"Top Employers: {', '.join(companies[:4])}")
    if certs:
        context.append(f"Recommended Certifications: {', '.join(certs[:2])}")
    
    return " | ".join(context)
