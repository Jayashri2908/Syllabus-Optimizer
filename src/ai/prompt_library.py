"""
Enhanced Prompt Library for SCDO
Optimized prompts for all AI generation tasks
"""

from typing import Dict, List, Optional


class PromptLibrary:
    """Centralized, optimized prompts for high-quality generation"""
    
    @staticmethod
    def get_learning_outcome_prompt(
        course_title: str,
        course_level: str,
        bloom_level: str,
        domain_context: str,
        keywords: List[str]
    ) -> Dict[str, str]:
        """
        Enhanced prompt for learning outcome generation (concise 1-2 lines)
        
        Returns dict with 'system' and 'user' prompts
        """
        
        system_prompt = f"""You are a {domain_context} curriculum expert writing CONCISE learning outcomes.

CRITICAL: Generate outcomes in 1-2 LINES ONLY (15-25 words max).

FORMAT: [Bloom's verb] + [specific skill/knowledge] + [brief context]

EXCELLENT EXAMPLES (1-2 lines):
✓ "Apply machine learning algorithms to classify and predict outcomes using Python and scikit-learn."
✓ "Design RESTful APIs with proper authentication and error handling using Node.js."
✓ "Analyze algorithm complexity using Big-O notation to optimize code performance."
✓ "Evaluate database normalization techniques to eliminate data redundancy."

POOR EXAMPLES (TOO LONG - AVOID):
❌ Long paragraphs with multiple sentences
❌ Detailed explanations of how students will demonstrate competency
❌ Multiple action verbs in one outcome

Keep it SHORT: 1-2 lines, 15-25 words maximum."""

        user_prompt = f"""Course: {course_title}
Level: {course_level}
Bloom's Level: {bloom_level}
Topics: {', '.join(keywords[:4])}

Generate ONE {bloom_level}-level learning outcome in 1-2 LINES ONLY (15-25 words max).
Start with a Bloom's verb, be specific but BRIEF."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    @staticmethod
    def get_unit_generation_prompt(
        course_title: str,
        unit_number: int,
        total_units: int,
        previous_units: List[Dict],
        keywords: List[str],
        domain_tools: List[str],
        applications: List[str],
        hours_per_unit: int
    ) -> Dict[str, str]:
        """Enhanced prompt for unit generation (concise topics)"""
        
        prev_summary = ""
        if previous_units:
            prev_summary = "Previous units: " + ", ".join([
                f"Unit {u['unit_number']}: {u['title']}"
                for u in previous_units
            ])
        else:
            prev_summary = "This is the first unit"
        
        system_prompt = f"""You are a curriculum expert creating CONCISE unit syllabi.

CRITICAL: Each topic must be SHORT (3-8 words only).

EXCELLENT EXAMPLE (short topics):
Unit 3: Database Design
1. Normalization and BCNF
2. Query optimization techniques
3. Transaction management
4. NoSQL vs SQL databases
5. Database security basics

POOR EXAMPLE (TOO LONG - AVOID):
1. Database normalization up to BCNF: theory, anomalies, practical normalization exercises
2. Query optimization techniques: execution plans, indexing strategies, real-world performance tuning

Keep each topic to 3-8 words. Be specific but BRIEF."""

        user_prompt = f"""Course: {course_title}
Unit: {unit_number} of {total_units}
Topics to cover: {', '.join(keywords[:5])}
{prev_summary}

Generate Unit {unit_number} with:
- Descriptive title (3-5 words)
- 5 topics (3-8 words EACH, no detailed explanations)

Format:
Unit {unit_number}: [Short Title]
1. [Topic in 3-8 words]
2. [Topic in 3-8 words]
3. [Topic in 3-8 words]
4. [Topic in 3-8 words]
5. [Topic in 3-8 words]

Keep it SHORT and CONCISE."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    @staticmethod
    def get_course_overview_prompt(
        course_title: str,
        keywords: List[str],
        domain: str,
        applications: List[str],
        careers: List[str],
        program: str = "",
        year: str = ""
    ) -> Dict[str, str]:
        """Enhanced prompt for course overview (4-5 lines)"""
        
        program_context = ""
        if program or year:
            program_context = f"\nProgram Context: {program} - {year}" if program and year else f"\nProgram: {program or year}"
        
        system_prompt = f"""You are a {domain} education expert writing concise course descriptions.

Write a BRIEF course overview in EXACTLY 4-5 lines (60-80 words) that covers:
- What the course teaches (core topics and skills)
- Why it matters (industry relevance)
- What students will be able to do after completion

CRITICAL: Keep it to 4-5 lines only. Be concise but informative.

EXCELLENT EXAMPLE (4-5 lines):
"This course covers the fundamentals of machine learning, including supervised and unsupervised learning algorithms, neural networks, and model evaluation techniques. Students will gain hands-on experience with Python, TensorFlow, and scikit-learn to build and deploy ML models. The curriculum prepares students for roles in data science and AI development, with skills applicable to industries like healthcare, finance, and technology."

POOR EXAMPLE (TOO LONG - AVOID):
[Multiple paragraphs with 200+ words]

Quality Criteria:
✓ Exactly 4-5 lines
✓ 60-80 words maximum
✓ Specific technologies mentioned
✓ Clear learning outcomes
✓ Industry relevance"""

        user_prompt = f"""Course: {course_title}
Domain: {domain}
Key Topics: {', '.join(keywords[:6])}{program_context}

Write a CONCISE course overview in EXACTLY 4-5 lines (60-80 words) covering:
1. What students will learn (core topics)
2. Technologies/tools used
3. Career relevance

Keep it brief but impactful. Maximum 4-5 lines."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    @staticmethod
    def get_objectives_prompt(
        course_title: str,
        keywords: List[str],
        domain: str,
        course_level: str,
        tools: List[str],
        applications: List[str]
    ) -> Dict[str, str]:
        """Enhanced prompt for course objectives (concise 1-2 lines each)"""
        
        system_prompt = f"""You are a {domain} curriculum expert writing CONCISE course objectives.

CRITICAL: Each objective must be 1-2 LINES ONLY (10-20 words max).

FORMAT: [Action verb] + [specific skill] + [brief context]

EXCELLENT EXAMPLES (1-2 lines each):
✓ "Develop proficiency in RESTful API design using Node.js and Express."
✓ "Master data structures and algorithms for problem-solving."
✓ "Build machine learning models using Python and scikit-learn."
✓ "Design secure database systems with proper normalization."
✓ "Implement cloud-native applications using Docker and Kubernetes."

POOR EXAMPLES (TOO LONG - AVOID):
❌ Long sentences with multiple clauses and detailed explanations
❌ Objectives with extensive context and multiple technologies listed

Keep it SHORT: 1-2 lines, 10-20 words maximum per objective."""

        user_prompt = f"""Course: {course_title}
Domain: {domain}
Topics: {', '.join(keywords[:4])}

Generate 5 CONCISE course objectives (1-2 lines each, 10-20 words max).
Start each with action verb (Develop, Master, Build, Design, Implement).
Be brief but specific."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    @staticmethod
    def get_references_prompt(
        course_title: str,
        keywords: List[str],
        course_level: str,
        domain: str
    ) -> Dict[str, str]:
        """Enhanced prompt for reference materials"""
        
        system_prompt = f"""You are an academic librarian and {domain} subject matter expert.

Suggest REAL, authoritative, well-known resources that actually exist.

CRITICAL: Only suggest books and resources you are CERTAIN exist. Better to suggest 5 real resources than 10 questionable ones.

CATEGORIES TO COVER:
1. **Textbooks** (3-4): Foundational, widely-used textbooks
2. **Reference Books** (2-3): Advanced or specialized resources
3. **Online Courses** (3-4): Coursera, edX, Udemy, MIT OpenCourseWare
4. **Documentation/Websites** (2-3): Official docs, tutorials

FORMAT for each:
- Book: "Title by Author Name (Publisher, Year)" or "Title by Author (Edition)"
- Course: "Course Name on Platform by Instructor/Institution"
- Website: "Resource Name - URL or description"

EXCELLENT EXAMPLES:

TEXTBOOKS:
✓ "Introduction to Algorithms by Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, and Clifford Stein (MIT Press, 4th Edition)"
✓ "Deep Learning by Ian Goodfellow, Yoshua Bengio, and Aaron Courville (MIT Press)"
✓ "Clean Code: A Handbook of Agile Software Craftsmanship by Robert C. Martin"

ONLINE COURSES:
✓ "Machine Learning Specialization on Coursera by Andrew Ng (Stanford University)"
✓ "The Complete Web Developer Course on Udemy by Rob Percival"
✓ "Introduction to Computer Science and Programming using Python - MIT OpenCourseWare (6.00.1x)"

POOR EXAMPLES (NEVER):
❌ "A book on programming" - Not specific
❌ "Standard textbooks" - Too vague
❌ "Various online resources" - Not helpful
❌ "Bob's Guide to Databases by Unknown Author" - Questionable if real

Quality Criteria:
✓ Real books/courses that definitely exist
✓ Include author names and publishers
✓ Mix of classic and recent resources
✓ Appropriate for course level
✓ Reputable publishers/platforms
✓ Specific titles, not generic suggestions"""

        user_prompt = f"""Course: {course_title}
Topics: {', '.join(keywords[:6])}
Level: {course_level}
Domain: {domain}

Suggest specific, real resources organized as:

1. TEXTBOOKS (3-4 books):
   - Include author names and publishers
   - Mix of foundational and advanced
   
2. REFERENCE BOOKS (2-3):
   - Specialized or advanced resources
   - Include full citation
   
3. ONLINE COURSES (3-4):
   - Coursera, edX, Udemy, MIT OCW
   - Include instructor/institution
   
4. WEBSITES/DOCUMENTATION (2-3):
   - Official documentation
   - Reputable tutorials or resources

Only suggest resources you are CERTAIN exist. Be specific with titles, authors, and platforms."""

        return {
            "system": system_prompt,
            "user": user_prompt
        }
