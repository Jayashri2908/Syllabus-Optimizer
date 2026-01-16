"""
LaTeX Template and Exporter for Syllabus
Standard LaTeX layout with section placeholders filled by generated content
"""

import logging
import os
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path


# =============================================================================
# LaTeX Template
# =============================================================================

SYLLABUS_LATEX_TEMPLATE = r"""
\documentclass[11pt,a4paper]{article}

% ============================================================================
% Packages
% ============================================================================
\usepackage[margin=1in]{geometry}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{longtable}
\usepackage{array}
\usepackage{fancyhdr}
\usepackage{lastpage}

% ============================================================================
% Colors and Styling
% ============================================================================
\definecolor{headerblue}{RGB}{0, 51, 102}
\definecolor{sectionblue}{RGB}{0, 102, 153}
\definecolor{lightgray}{RGB}{245, 245, 245}

\hypersetup{
    colorlinks=true,
    linkcolor=sectionblue,
    urlcolor=sectionblue
}

% Section formatting
\titleformat{\section}
    {\normalfont\Large\bfseries\color{headerblue}}
    {}
    {0pt}
    {}
    [\titlerule]

\titleformat{\subsection}
    {\normalfont\large\bfseries\color{sectionblue}}
    {}
    {0pt}
    {}

% Header and footer
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small {{COURSE_CODE}}}
\fancyhead[R]{\small {{COURSE_TITLE}}}
\fancyfoot[C]{\small Page \thepage\ of \pageref{LastPage}}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% ============================================================================
% Document
% ============================================================================
\begin{document}

% Title
\begin{center}
    {\LARGE \bfseries \color{headerblue} {{COURSE_TITLE}}} \\[0.3cm]
    {\large {{COURSE_CODE}} \quad | \quad Credits: {{CREDITS}}} \\[0.2cm]
    {{PROGRAM_INFO}}
\end{center}

\vspace{0.5cm}

% ============================================================================
% Course Overview
% ============================================================================
\section*{Course Overview}
{{OVERVIEW}}

\vspace{0.3cm}

% ============================================================================
% Course Objectives
% ============================================================================
\section*{Course Objectives}
Upon completion of this course, students will be able to:
\begin{itemize}[leftmargin=*, itemsep=2pt]
{{OBJECTIVES}}
\end{itemize}

\vspace{0.3cm}

% ============================================================================
% Learning Outcomes
% ============================================================================
\section*{Course Learning Outcomes (CO-PO Mapping)}

\begin{longtable}{@{}>{\bfseries}p{1.2cm} p{10cm} >{\centering\arraybackslash}p{2.5cm}@{}}
\toprule
\textbf{Code} & \textbf{Learning Outcome Description} & \textbf{Bloom's Level} \\
\midrule
\endfirsthead
\toprule
\textbf{Code} & \textbf{Learning Outcome Description} & \textbf{Bloom's Level} \\
\midrule
\endhead
{{LEARNING_OUTCOMES}}
\bottomrule
\end{longtable}

\vspace{0.3cm}

% ============================================================================
% Unit-wise Syllabus
% ============================================================================
\section*{Unit-wise Syllabus}
{{UNITS}}

\vspace{0.3cm}

% ============================================================================
% Teaching Methodology
% ============================================================================
\section*{Teaching-Learning Methodology}
\begin{itemize}[leftmargin=*, itemsep=2pt]
{{TEACHING_METHODS}}
\end{itemize}

\vspace{0.3cm}

% ============================================================================
% Assessment Pattern
% ============================================================================
\section*{Assessment Pattern}
{{ASSESSMENT}}

\vspace{0.3cm}

% ============================================================================
% References
% ============================================================================
\section*{References}

\subsection*{Textbooks}
\begin{enumerate}[leftmargin=*, itemsep=2pt]
{{TEXTBOOKS}}
\end{enumerate}

{{REFERENCE_BOOKS_SECTION}}

\subsection*{Online Resources}
\begin{enumerate}[leftmargin=*, itemsep=2pt]
{{ONLINE_RESOURCES}}
\end{enumerate}

\end{document}
"""


# =============================================================================
# LaTeX Exporter Class
# =============================================================================

class LaTeXExporter:
    """
    Export syllabus to LaTeX format with optional PDF compilation.
    
    Fills a standard LaTeX template with generated syllabus sections.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def export(
        self,
        syllabus: Dict[str, Any],
        output_path: str,
        compile_pdf: bool = False,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Export syllabus to LaTeX file.
        
        Args:
            syllabus: Complete syllabus dictionary
            output_path: Output .tex file path
            compile_pdf: If True, attempt to compile to PDF
            metadata: Optional metadata (department, university, academic_year)
            
        Returns:
            Path to the generated LaTeX file
        """
        self.logger.info(f"Exporting syllabus to LaTeX: {output_path}")
        
        # Start with template
        tex_content = SYLLABUS_LATEX_TEMPLATE
        
        # Fill basic info
        tex_content = self._fill_course_info(tex_content, syllabus, metadata)
        
        # Fill each section
        tex_content = self._fill_overview(tex_content, syllabus)
        tex_content = self._fill_objectives(tex_content, syllabus)
        tex_content = self._fill_learning_outcomes(tex_content, syllabus)
        tex_content = self._fill_units(tex_content, syllabus)
        tex_content = self._fill_methodology(tex_content, syllabus)
        tex_content = self._fill_assessment(tex_content, syllabus)
        tex_content = self._fill_references(tex_content, syllabus)
        
        # Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(tex_content)
        
        self.logger.info(f"LaTeX file created: {output_path}")
        
        # Optionally compile to PDF
        if compile_pdf:
            pdf_path = self._compile_pdf(output_path)
            if pdf_path:
                return str(pdf_path)
        
        return str(output_path)
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        replacements = [
            ('\\', r'\textbackslash{}'),
            ('&', r'\&'),
            ('%', r'\%'),
            ('$', r'\$'),
            ('#', r'\#'),
            ('_', r'\_'),
            ('{', r'\{'),
            ('}', r'\}'),
            ('~', r'\textasciitilde{}'),
            ('^', r'\textasciicircum{}'),
        ]
        
        for old, new in replacements:
            text = text.replace(old, new)
        
        return text
    
    def _fill_course_info(
        self,
        tex_content: str,
        syllabus: Dict[str, Any],
        metadata: Optional[Dict[str, str]]
    ) -> str:
        """Fill basic course information"""
        metadata = metadata or {}
        
        course_title = self._escape_latex(syllabus.get('course_title', 'Untitled Course'))
        course_code = self._escape_latex(syllabus.get('course_code', 'XXX000'))
        credits = self._escape_latex(syllabus.get('credits', '3-1-0'))
        
        # Program info line
        program = syllabus.get('program', '')
        year = syllabus.get('year', '')
        department = metadata.get('department', '')
        
        program_parts = [p for p in [program, year, department] if p]
        program_info = self._escape_latex(' | '.join(program_parts)) if program_parts else ''
        
        tex_content = tex_content.replace('{{COURSE_TITLE}}', course_title)
        tex_content = tex_content.replace('{{COURSE_CODE}}', course_code)
        tex_content = tex_content.replace('{{CREDITS}}', credits)
        tex_content = tex_content.replace('{{PROGRAM_INFO}}', program_info)
        
        return tex_content
    
    def _fill_overview(self, tex_content: str, syllabus: Dict[str, Any]) -> str:
        """Fill course overview section"""
        overview = syllabus.get('overview', '')
        if isinstance(overview, dict):
            overview = overview.get('overview_text', '')
        
        overview_escaped = self._escape_latex(str(overview))
        
        return tex_content.replace('{{OVERVIEW}}', overview_escaped)
    
    def _fill_objectives(self, tex_content: str, syllabus: Dict[str, Any]) -> str:
        """Fill course objectives section"""
        objectives = syllabus.get('objectives', [])
        
        items = []
        for obj in objectives:
            if isinstance(obj, dict):
                text = obj.get('text', '')
            else:
                text = str(obj)
            
            if text:
                items.append(f"    \\item {self._escape_latex(text)}")
        
        objectives_tex = '\n'.join(items) if items else "    \\item Course objectives to be defined"
        
        return tex_content.replace('{{OBJECTIVES}}', objectives_tex)
    
    def _fill_learning_outcomes(self, tex_content: str, syllabus: Dict[str, Any]) -> str:
        """Fill learning outcomes table"""
        outcomes = syllabus.get('learning_outcomes', [])
        
        rows = []
        for outcome in outcomes:
            if isinstance(outcome, dict):
                code = self._escape_latex(outcome.get('code', ''))
                desc = self._escape_latex(outcome.get('description', ''))
                bloom = self._escape_latex(outcome.get('bloom_level', '')).capitalize()
                
                if code and desc:
                    rows.append(f"{code} & {desc} & {bloom} \\\\")
        
        outcomes_tex = '\n'.join(rows) if rows else "CO1 & Learning outcomes to be defined & Apply \\\\"
        
        return tex_content.replace('{{LEARNING_OUTCOMES}}', outcomes_tex)
    
    def _fill_units(self, tex_content: str, syllabus: Dict[str, Any]) -> str:
        """Fill unit-wise syllabus section with comprehensive detailed content"""
        units = syllabus.get('units', [])
        
        units_tex_parts = []
        
        for unit in units:
            if isinstance(unit, dict):
                unit_num = unit.get('unit_number', 0)
                title = self._escape_latex(unit.get('title', 'Unit'))
                overview = unit.get('overview', '')
                topics = unit.get('topics', [])
                learning_activities = unit.get('learning_activities', [])
                suggested_readings = unit.get('suggested_readings', [])
                assessment_ideas = unit.get('assessment_ideas', [])
                hours = unit.get('hours', 10)
                
                # Unit header
                units_tex_parts.append(f"\\subsection*{{Unit {unit_num}: {title} ({hours} hours)}}")
                
                # Unit overview if present
                if overview:
                    units_tex_parts.append(f"\\textit{{{self._escape_latex(overview)}}}")
                    units_tex_parts.append("\\vspace{0.2cm}")
                
                # Topics with comprehensive detailed content
                if topics:
                    for topic in topics:
                        if isinstance(topic, dict):
                            topic_name = topic.get('topic', '')
                            description = topic.get('description', '')
                            subtopics = topic.get('subtopics', [])
                            key_concepts = topic.get('key_concepts', [])
                            practical_examples = topic.get('practical_examples', [])
                            
                            if topic_name:
                                # Topic name as bold header
                                units_tex_parts.append(f"\\textbf{{{self._escape_latex(topic_name)}}}")
                                
                                # Description paragraph if present
                                if description:
                                    units_tex_parts.append(f"\\\\{self._escape_latex(description)}")
                                
                                # Subtopics as nested list
                                if subtopics:
                                    units_tex_parts.append("\\begin{itemize}[leftmargin=2em, itemsep=0pt, topsep=2pt]")
                                    for st in subtopics:
                                        if st:
                                            units_tex_parts.append(f"    \\item {self._escape_latex(str(st))}")
                                    units_tex_parts.append("\\end{itemize}")
                                
                                # Key concepts inline
                                if key_concepts:
                                    concepts_str = ", ".join([self._escape_latex(str(c)) for c in key_concepts])
                                    units_tex_parts.append(f"\\textit{{Key Concepts: {concepts_str}}}")
                                
                                # Practical examples inline
                                if practical_examples:
                                    examples_str = "; ".join([self._escape_latex(str(e)) for e in practical_examples])
                                    units_tex_parts.append(f"\\textit{{Applications: {examples_str}}}")
                                
                                units_tex_parts.append("\\vspace{0.15cm}")
                        else:
                            # Simple string topic (backward compatibility)
                            topic_text = str(topic)
                            if topic_text:
                                units_tex_parts.append(f"\\textbf{{{self._escape_latex(topic_text)}}}")
                                units_tex_parts.append("\\vspace{0.1cm}")
                
                # Learning activities if present
                if learning_activities:
                    units_tex_parts.append("\\vspace{0.2cm}")
                    units_tex_parts.append("\\textbf{Learning Activities:}")
                    units_tex_parts.append("\\begin{itemize}[leftmargin=*, itemsep=0pt]")
                    for activity in learning_activities:
                        if activity:
                            units_tex_parts.append(f"    \\item {self._escape_latex(str(activity))}")
                    units_tex_parts.append("\\end{itemize}")
                
                # Suggested readings if present
                if suggested_readings:
                    units_tex_parts.append("\\vspace{0.1cm}")
                    units_tex_parts.append("\\textbf{Suggested Readings:}")
                    units_tex_parts.append("\\begin{itemize}[leftmargin=*, itemsep=0pt]")
                    for reading in suggested_readings:
                        if reading:
                            units_tex_parts.append(f"    \\item {self._escape_latex(str(reading))}")
                    units_tex_parts.append("\\end{itemize}")
                
                # Assessment ideas if present (condensed format)
                if assessment_ideas:
                    ideas_str = ", ".join([self._escape_latex(str(a)) for a in assessment_ideas])
                    units_tex_parts.append(f"\\textit{{Assessment: {ideas_str}}}")
                
                units_tex_parts.append("\\vspace{0.4cm}")  # Space between units
        
        units_tex = '\n'.join(units_tex_parts) if units_tex_parts else "\\subsection*{Unit 1: Introduction}\n\\begin{itemize}\n    \\item Topics to be defined\n\\end{itemize}"
        
        return tex_content.replace('{{UNITS}}', units_tex)
    
    def _fill_methodology(self, tex_content: str, syllabus: Dict[str, Any]) -> str:
        """Fill teaching methodology section"""
        methodology = syllabus.get('teaching_methodology', {})
        
        methods = methodology.get('teaching_methods', [])
        activities = methodology.get('learning_activities', [])
        
        all_items = methods + activities
        
        items = []
        for item in all_items[:8]:  # Limit to 8 items
            items.append(f"    \\item {self._escape_latex(str(item))}")
        
        methods_tex = '\n'.join(items) if items else "    \\item Lectures and interactive discussions"
        
        return tex_content.replace('{{TEACHING_METHODS}}', methods_tex)
    
    def _fill_assessment(self, tex_content: str, syllabus: Dict[str, Any]) -> str:
        """Fill assessment pattern section"""
        assessment = syllabus.get('assessment_pattern', {})
        
        internal = assessment.get('internal', {})
        external = assessment.get('external', {})
        
        lines = []
        
        # Internal assessment
        internal_weight = internal.get('weightage', 40)
        lines.append(f"\\textbf{{Internal Assessment ({internal_weight}\\%):}}")
        lines.append("\\begin{itemize}[leftmargin=*, itemsep=1pt]")
        
        for component, weight in internal.get('components', {}).items():
            component_name = component.replace('_', ' ').title()
            lines.append(f"    \\item {component_name}: {weight}\\%")
        
        lines.append("\\end{itemize}")
        lines.append("")
        
        # External assessment
        external_weight = external.get('weightage', 60)
        lines.append(f"\\textbf{{External Assessment ({external_weight}\\%):}}")
        lines.append("\\begin{itemize}[leftmargin=*, itemsep=1pt]")
        
        for component, weight in external.get('components', {}).items():
            component_name = component.replace('_', ' ').title()
            lines.append(f"    \\item {component_name}: {weight}\\%")
        
        lines.append("\\end{itemize}")
        
        assessment_tex = '\n'.join(lines)
        
        return tex_content.replace('{{ASSESSMENT}}', assessment_tex)
    
    def _fill_references(self, tex_content: str, syllabus: Dict[str, Any]) -> str:
        """Fill references section"""
        refs = syllabus.get('references', {})
        
        # Textbooks
        textbooks = refs.get('textbooks', [])
        textbook_items = []
        for book in textbooks:
            textbook_items.append(f"    \\item {self._escape_latex(str(book))}")
        textbooks_tex = '\n'.join(textbook_items) if textbook_items else "    \\item Textbooks to be recommended"
        
        # Reference books
        reference_books = refs.get('references', refs.get('reference_books', []))
        if reference_books:
            ref_items = []
            for book in reference_books:
                ref_items.append(f"    \\item {self._escape_latex(str(book))}")
            ref_section = "\\subsection*{Reference Books}\n\\begin{enumerate}[leftmargin=*, itemsep=2pt]\n" + '\n'.join(ref_items) + "\n\\end{enumerate}\n"
        else:
            ref_section = ""
        
        # Online resources
        online = refs.get('online_resources', [])
        online_items = []
        for resource in online:
            online_items.append(f"    \\item {self._escape_latex(str(resource))}")
        online_tex = '\n'.join(online_items) if online_items else "    \\item Online resources to be provided"
        
        tex_content = tex_content.replace('{{TEXTBOOKS}}', textbooks_tex)
        tex_content = tex_content.replace('{{REFERENCE_BOOKS_SECTION}}', ref_section)
        tex_content = tex_content.replace('{{ONLINE_RESOURCES}}', online_tex)
        
        return tex_content
    
    def _compile_pdf(self, tex_path: Path) -> Optional[Path]:
        """
        Compile LaTeX to PDF using pdflatex.
        
        Args:
            tex_path: Path to the .tex file
            
        Returns:
            Path to the PDF if successful, None otherwise
        """
        try:
            # Check if pdflatex is available
            result = subprocess.run(
                ['pdflatex', '--version'],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.logger.warning("pdflatex not available, skipping PDF compilation")
                return None
            
            # Compile (run twice for references)
            for _ in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', str(tex_path)],
                    cwd=tex_path.parent,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            
            pdf_path = tex_path.with_suffix('.pdf')
            if pdf_path.exists():
                self.logger.info(f"PDF compiled successfully: {pdf_path}")
                return pdf_path
            else:
                self.logger.warning("PDF compilation failed")
                return None
                
        except FileNotFoundError:
            self.logger.warning("pdflatex not found, skipping PDF compilation")
            return None
        except subprocess.TimeoutExpired:
            self.logger.warning("PDF compilation timed out")
            return None
        except Exception as e:
            self.logger.error(f"PDF compilation error: {e}")
            return None
