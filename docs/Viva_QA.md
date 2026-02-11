# Project Viva Q&A: Syllabus and Curriculum Design Optimizer (SCDO)

This document contains potential examiner questions and detailed answers categorized by project area. Use this to prepare for your viva-voce.

---

## 1. Project Overview & Motivation

**Q1: What is the core problem your project solves?**
**A:** The project addresses the inefficiency, inconsistency, and lack of pedagogical grounding in manual syllabus design. Faculty often spend 10-20+ hours on administrative documentation. Our system reduces this workload by 70-80% while ensuring alignment with Bloom's Taxonomy and accreditation standards like NBA and NAAC.

**Q2: What is the "SCDO" and what are its main pillars?**
**A:** SCDO stands for Syllabus and Curriculum Design Optimizer. Its three pillars are:
1. **Intelligent Analysis:** Parsing existing documents to identify gaps.
2. **AI-Powered Generation:** Creating a full syllabus from minimal inputs (Title, Credits, Keywords).
3. **Outcome Optimization:** Refining existing syllabi using RAG to ensure compliance with educational standards.

**Q3: Who are the primary stakeholders for this system?**
**A:** The primary stakeholders are faculty members (as designers), academic administrators (for quality assurance), and institutional accreditation cells (for NBA/NAAC compliance).

---

## 2. Technical Architecture

**Q4: Can you explain the system architecture in brief?**
**A:** The system follows a modular layered architecture:
- **Presentation Layer:** React-based interactive dashboard.
- **API Layer:** FastAPI (Python) backend providing RESTful endpoints.
- **Logic Layer:** Discrete modules for parsing, analysis, generation, and mapping.
- **Integration Layer:** Multi-model AI orchestration (IBM Granite, Google Gemini, etc.) and RAG with ChromaDB.

**Q5: Why did you choose FastAPI for the backend?**
**A:** FastAPI was chosen for its high performance (comparable to Node.js and Go), native support for asynchronous programming, and automatic generation of OpenAPI/Swagger documentation, which is crucial for a modular system.

**Q6: How does your system handle multi-model AI orchestration?**
**A:** We use an abstraction layer that allows the system to switch between different LLM providers (Google Gemini, IBM Granite via OpenRouter). This ensures resilience (fallback if one is down) and cost-effectiveness.

**Q7: What document formats do you support for parsing?**
**A:** We support PDF (using `PyPDF2` and `pdfplumber`), DOCX (using `python-docx`), and plain text. Our parser handles both direct text and table-based structures.

---

## 3. Artificial Intelligence & RAG

**Q8: What is RAG, and why is it used in your project?**
**A:** RAG stands for **Retrieval-Augmented Generation**. Instead of relying solely on the LLM's static training data, RAG retrieves relevant information from a verified knowledge base (like NBA/NAAC manuals) and provides it to the AI as context. This prevents "hallucinations" and ensures suggestions cite authoritative sources.

**Q9: Which Vector Database did you use and why?**
**A:** We used **ChromaDB**. It is a lightweight, open-source vector database that is easy to integrate with Python and efficient for storing and performing semantic searches on educational documents.

**Q10: How do you perform "Semantic Tagging" for Bloom's Taxonomy?**
**A:** We use Natural Language Processing (NLP) to identify action verbs in learning outcomes. These verbs are matched against a structured mapping (e.g., "Define" → Remember, "Design" → Create). In cases of multiple verbs, we use the highest cognitive level following the hierarchical principle of the taxonomy.

**Q11: Explain the "Industry Relevance Score."**
**A:** This is a custom metric (0-100) calculated by analyzing the keywords in the syllabus against a dynamic list of modern industry trends. It identifies if the curriculum includes contemporary skills (like Generative AI or Cloud Computing).

---

## 4. Educational Foundations (OBE & Bloom's)

**Q12: What is Outcome-Based Education (OBE)?**
**A:** OBE is a pedagogical philosophy where every part of the curriculum is designed backward from clearly defined "outcomes" (what a student should be able to do at the end). Our system helps achieve "Clarity of Focus" and "Designing Down."

**Q13: Explain the 6 levels of Revised Bloom's Taxonomy used in your project.**
**A:** The levels represent increasing cognitive complexity:
1. **Remember:** Recalling facts.
2. **Understand:** Explaining ideas.
3. **Apply:** Using information in new situations.
4. **Analyze:** Drawing connections between ideas.
5. **Evaluate:** Justifying a stand or decision.
6. **Create:** Producing new or original work.

**Q14: What is CO-PO Mapping?**
**A:** Course Outcome (CO) to Program Outcome (PO) mapping identifies how a specific course contributes to the overall attributes a graduate should possess. Our system uses semantic similarity to automate this mapping on a 1-3 scale (Slight, Moderate, Substantial correlation).

---

## 5. Functional Features

**Q15: How does the "Gap Analysis" module work?**
**A:** It evaluates four dimensions:
1. **Bloom's Coverage:** Is there a balance across cognitive levels?
2. **CO-PO Mapping:** Are there unmapped outcomes?
3. **Content Quality:** Are topics deep and current?
4. **Structural Analysis:** Is the workload (contact hours) distributed logically?

**Q16: Can you explain the "Unit Sequencing Analysis"?**
**A:** It checks if the topics follow a logical pedagogical progression—ensuring that foundational/prerequisite concepts are taught before advanced ones.

**Q17: How is the PDF report generated?**
**A:** We use the `ReportLab` library. It allows us to generate high-fidelity PDFs that include text, tables, and even dynamic charts generated via `matplotlib`.

---

## 6. Challenges & Implementation Details

**Q18: What were the major challenges in parsing PDFs?**
**A:** PDFs are non-structured; headers and tables can be formatted in thousands of ways. We solved this by using a combination of pattern matching and AI-assisted extraction to reconstruct the syllabus structure correctly.

**Q19: How do you handle AI "hallucinations"?**
**A:** Two ways:
1. **RAG:** Grounding the AI in source manuals.
2. **Human-in-the-loop:** The system allows the user to review and edit any AI-generated content before finalizing.

**Q20: Why do you claim a 70-80% reduction in faculty workload?**
**A:** Manual syllabus creation takes hours of drafting and cross-referencing manuals. Our system generates a primary draft in seconds, leaving only refinement for the faculty—transitioning them from "authors" to "editors."

---

## 7. Future Scope & Impact

**Q21: How can this project be extended in the future?**
**A:** Future directions include:
- Direct integration with Learning Management Systems (LMS) like Moodle.
- Automated generation of Assessment Rubrics and Question Banks.
- Real-time industry trend analysis using job board APIs (LinkedIn/Glassdoor).
- Multilingual support for regional Indian languages.

**Q22: How does this project align with NEP 2020?**
**A:** NEP 2020 emphasizes multidisciplinary approaches, critical thinking, and frequent curriculum revision. SCDO simplifies these revisions and ensures multidisciplinary keywords are appropriately integrated into the syllabus.

**Q23: Is the system scalable for an entire University?**
**A:** Yes. The backend is stateless (FastAPI), meaning we can deploy multiple instances. The use of a vector database (ChromaDB) allows us to store thousands of accreditation documents without performance loss.

**Q24: What is the significance of the "A-D" Quality Grade?**
**A:** It provides an immediate, objective quality check for administrators. A grade "A" syllabus is complete, balanced in Bloom's levels, and industry-relevant, while a grade "D" might indicate missing outcomes or outdated topics.

---

## 8. Development & Tools

**Q25: What technologies are in your tech stack?**
**A:** 
- **Frontend:** React, Recharts (for visualization).
- **Backend:** Python, FastAPI.
- **AI/NLP:** IBM Granite, Google Gemini, ChromaDB (Vector DB).
- **Export:** ReportLab, Matplotlib.

**Q26: How do you manage configuration and security?**
**A:** API keys are stored in environment variables (`.env` file) and never hardcoded. Configuration for different AI models is kept in structured YAML files.

**Q27: Did you perform any testing?**
**A:** Yes, we performed unit testing on the parser and integration testing on the analysis pipeline using real-world syllabi from Computer Science and Mechanical Engineering departments to ensure domain robustness.
