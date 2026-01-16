"""
LaTeX PDF Exporter for SCDO
Generates professional academic PDFs with proper math formula rendering
"""

import os
import logging
import re
import subprocess
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from pylatex import Document, Section, Subsection, Tabular, Math, Command
    from pylatex import Package, NoEscape, NewLine, MiniPage, MultiColumn
    from pylatex.utils import italic, bold
    PYLATEX_AVAILABLE = True
except ImportError:
    PYLATEX_AVAILABLE = False
    logging.warning("pylatex not installed. Install with: pip install pylatex")


class LaTeXExporter:
    """Export syllabus to PDF using LaTeX for professional academic formatting"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def export_pdf(
        self,
        syllabus_data: Dict[str, Any],
        output_path: str,
        include_optimization: bool = False,
        optimization_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Export syllabus to PDF using LaTeX
        
        Args:
            syllabus_data: Parsed syllabus structure
            output_path: Output PDF file path
            include_optimization: Whether to include optimization results
            optimization_data: Optimization analysis results
            
        Returns:
            Path to generated PDF
        """
        if not PYLATEX_AVAILABLE:
            raise ImportError("pylatex is required for LaTeX PDF export. Install with: pip install pylatex")
        
        # Check if LaTeX is available
        latex_available = self._check_latex_installation()
        
        if not latex_available:
            self.logger.warning("LaTeX compiler not found. Generating .tex file instead.")
            return self._generate_tex_only(syllabus_data, output_path, include_optimization, optimization_data)
        
        # Create LaTeX document
        doc = self._create_document(syllabus_data, include_optimization, optimization_data)
        
        # Generate PDF
        output_base = output_path.replace('.pdf', '')
        try:
            doc.generate_pdf(output_base, clean_tex=False, compiler='pdflatex')
            self.logger.info(f"LaTeX PDF generated: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            # Fallback: save .tex file
            doc.generate_tex(output_base)
            return f"{output_base}.tex"
    
    def _check_latex_installation(self) -> bool:
        """Check if pdflatex is available"""
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                   capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _generate_tex_only(
        self,
        syllabus_data: Dict[str, Any],
        output_path: str,
        include_optimization: bool,
        optimization_data: Optional[Dict[str, Any]]
    ) -> str:
        """Generate only the .tex file without compilation"""
        doc = self._create_document(syllabus_data, include_optimization, optimization_data)
        output_base = output_path.replace('.pdf', '')
        doc.generate_tex(output_base)
        return f"{output_base}.tex"
    
    def _create_document(
        self,
        syllabus_data: Dict[str, Any],
        include_optimization: bool,
        optimization_data: Optional[Dict[str, Any]]
    ) -> Document:
        """Create LaTeX document structure"""
        # Document setup with academic formatting
        doc = Document(
            documentclass='article',
            document_options=['12pt', 'a4paper'],
        )
        
        # Add packages
        doc.packages.append(Package('geometry', options=['margin=1in']))
        doc.packages.append(Package('amsmath'))
        doc.packages.append(Package('amssymb'))
        doc.packages.append(Package('graphicx'))
        doc.packages.append(Package('booktabs'))
        doc.packages.append(Package('hyperref'))
        doc.packages.append(Package('xcolor'))
        doc.packages.append(Package('fancyhdr'))
        doc.packages.append(Package('lastpage'))
        doc.packages.append(Package('array'))
        doc.packages.append(Package('longtable'))  # For long tables
        
        # Header/Footer setup
        doc.preamble.append(NoEscape(r'\pagestyle{fancy}'))
        doc.preamble.append(NoEscape(r'\fancyhf{}'))
        doc.preamble.append(NoEscape(r'\rhead{\thepage\ of \pageref{LastPage}}'))
        doc.preamble.append(NoEscape(r'\lhead{Course Syllabus}'))
        
        # Title
        title = syllabus_data.get('course_title', 'Course Syllabus')
        code = syllabus_data.get('course_code', '')
        
        doc.preamble.append(Command('title', NoEscape(
            f'{self._escape_latex(title)}\\\\[0.5em]'
            f'\\large Course Code: {self._escape_latex(code)}'
        )))
        doc.preamble.append(Command('author', ''))
        doc.preamble.append(Command('date', NoEscape(r'\today')))
        
        doc.append(NoEscape(r'\maketitle'))
        doc.append(NoEscape(r'\tableofcontents'))
        doc.append(NoEscape(r'\newpage'))
        
        # Add sections
        self._add_course_overview(doc, syllabus_data)
        self._add_learning_outcomes(doc, syllabus_data)
        self._add_units(doc, syllabus_data)
        self._add_co_po_mapping(doc, syllabus_data)  # Add CO-PO mapping table
        self._add_assessment(doc, syllabus_data)
        self._add_references(doc, syllabus_data)
        
        # Add optimization results if provided OR if embedded in syllabus_data
        opt_data = optimization_data
        if not opt_data and syllabus_data.get('bloom_analysis'):
            opt_data = {
                'bloom_analysis': syllabus_data.get('bloom_analysis'),
                'rebalancing_suggestions': syllabus_data.get('rebalancing_suggestions', [])
            }
            include_optimization = True
        
        if include_optimization and opt_data:
            self._add_optimization_results(doc, opt_data)
        
        return doc
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters and sanitize Unicode"""
        if not text:
            return ""
        
        # Convert common math notation to LaTeX
        text = str(text)
        
        # Sanitize problematic Unicode characters first
        unicode_replacements = {
            '“': '"',   # U+201C Left double quotation mark
            '”': '"',   # U+201D Right double quotation mark
            '‟': '"',   # U+201F Double high-reversed-9 quotation mark
            '‘': "'",   # U+2018 Left single quotation mark
            '’': "'",   # U+2019 Right single quotation mark
            '‛': "'",   # U+201B Single high-reversed-9 quotation mark
            '–': '-',   # U+2013 En dash
            '—': '-',   # U+2014 Em dash
            '…': '...',  # U+2026 Horizontal ellipsis
            '•': r'$\bullet$',  # U+2022 Bullet
            '●': r'$\bullet$',  # U+25CF Black circle
            '○': r'$\circ$',    # U+25CB White circle
            '′': "'",   # U+2032 Prime
            '″': '"',   # U+2033 Double prime
            '‐': '-',   # U+2010 Hyphen
            '‑': '-',   # U+2011 Non-breaking hyphen
            '‒': '-',   # U+2012 Figure dash
            '™': r'\texttrademark{}',
            '©': r'\textcopyright{}',
            '®': r'\textregistered{}',
            '°': r'$^\circ$',  # Degree symbol
            '±': r'$\pm$',
            '×': r'$\times$',
            '÷': r'$\div$',
            '≤': r'$\leq$',
            '≥': r'$\geq$',
            '≠': r'$\neq$',
            '∞': r'$\infty$',
            'α': r'$\alpha$',
            'β': r'$\beta$',
            'γ': r'$\gamma$',
            'δ': r'$\delta$',
            'π': r'$\pi$',
            'σ': r'$\sigma$',
            'Σ': r'$\Sigma$',
            '→': r'$\rightarrow$',
            '←': r'$\leftarrow$',
            '↔': r'$\leftrightarrow$',
        }
        
        for char, replacement in unicode_replacements.items():
            text = text.replace(char, replacement)
        
        # Remove any remaining non-ASCII characters that could cause issues
        # (keep basic Latin extended like é, ü, etc if needed)
        text = ''.join(c if ord(c) < 256 or c.isalnum() else ' ' for c in text)
        
        # Escape special LaTeX characters
        special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        
        for char, escaped in special_chars.items():
            text = text.replace(char, escaped)
        
        # Convert math notations
        text = self._convert_math_notation(text)
        
        return text
    
    def _convert_math_notation(self, text: str) -> str:
        """Convert common algorithm complexity notation to proper LaTeX math"""
        # O(n^2) -> $O(n^2)$
        text = re.sub(r'\bO\(([^)]+)\)', r'$O(\1)$', text)
        
        # Omega notation
        text = re.sub(r'[Ωω]\(([^)]+)\)', r'$\\Omega(\1)$', text)
        
        # Theta notation  
        text = re.sub(r'[Θθ]\(([^)]+)\)', r'$\\Theta(\1)$', text)
        
        # Power notation: n^2 -> $n^2$
        text = re.sub(r'\b(\w)\^(\d+)\b', r'$\1^{\2}$', text)
        
        # log n -> $\log n$
        text = re.sub(r'\blog\s*n\b', r'$\\log n$', text, flags=re.IGNORECASE)
        text = re.sub(r'\blog\s*\(([^)]+)\)', r'$\\log(\1)$', text, flags=re.IGNORECASE)
        
        # 2^n -> $2^n$
        text = re.sub(r'\b2\^n\b', r'$2^n$', text)
        
        # n! -> $n!$
        text = re.sub(r'\bn!\b', r'$n!$', text)
        
        return text
    
    def _add_course_overview(self, doc: Document, syllabus_data: Dict[str, Any]):
        """Add course overview section"""
        with doc.create(Section('Course Overview')):
            # Course details table
            with doc.create(Tabular('ll')) as table:
                table.add_row([bold('Course Code:'), 
                              self._escape_latex(syllabus_data.get('course_code', 'N/A'))])
                table.add_row([bold('Credits:'), 
                              self._escape_latex(syllabus_data.get('credits', 'N/A'))])
                
                prereqs = syllabus_data.get('prerequisites', [])
                if prereqs:
                    table.add_row([bold('Prerequisites:'), 
                                  self._escape_latex(', '.join(prereqs))])
            
            # Objectives
            objectives = syllabus_data.get('objectives', [])
            if objectives:
                doc.append(NewLine())
                with doc.create(Subsection('Course Objectives', numbering=False)):
                    doc.append(NoEscape(r'\begin{itemize}'))
                    for obj in objectives[:5]:  # Limit to 5
                        obj_text = obj[:200] if len(obj) > 200 else obj
                        doc.append(NoEscape(f'\\item {self._escape_latex(obj_text)}'))
                    doc.append(NoEscape(r'\end{itemize}'))
    
    def _add_learning_outcomes(self, doc: Document, syllabus_data: Dict[str, Any]):
        """Add learning outcomes section with Bloom's levels"""
        outcomes = syllabus_data.get('learning_outcomes', [])
        if not outcomes:
            return
            
        with doc.create(Section('Course Outcomes (COs)')):
            with doc.create(Tabular('|c|p{10cm}|c|')) as table:
                table.add_hline()
                table.add_row([bold('CO'), bold('Description'), bold("Bloom's Level")])
                table.add_hline()
                
                for outcome in outcomes:
                    if isinstance(outcome, dict):
                        code = outcome.get('code', 'CO?')
                        desc = outcome.get('description', '')[:150]
                        bloom = outcome.get('bloom_level', 'N/A').capitalize()
                    else:
                        code = 'CO'
                        desc = str(outcome)[:150]
                        bloom = 'N/A'
                    
                    table.add_row([
                        self._escape_latex(code),
                        self._escape_latex(desc),
                        self._escape_latex(bloom)
                    ])
                    table.add_hline()
    
    def _add_units(self, doc: Document, syllabus_data: Dict[str, Any]):
        """Add unit-wise content"""
        units = syllabus_data.get('units', [])
        if not units:
            return
            
        with doc.create(Section('Course Content')):
            for unit in units:
                unit_num = unit.get('unit_number', '?')
                title = unit.get('title', 'Untitled')
                hours = unit.get('hours', 0)
                
                with doc.create(Subsection(
                    f'Unit {unit_num}: {self._escape_latex(title)} ({hours} Hours)'
                )):
                    topics = unit.get('topics', [])
                    if topics:
                        doc.append(NoEscape(r'\begin{itemize}'))
                        for topic in topics[:10]:
                            topic_text = str(topic)[:200] if len(str(topic)) > 200 else str(topic)
                            # Apply math notation conversion
                            topic_text = self._escape_latex(topic_text)
                            doc.append(NoEscape(f'\\item {topic_text}'))
                        doc.append(NoEscape(r'\end{itemize}'))
    
    def _add_co_po_mapping(self, doc: Document, syllabus_data: Dict[str, Any]):
        """Add CO-PO mapping matrix table"""
        co_po_mapping = syllabus_data.get('co_po_mapping', {})
        if not co_po_mapping:
            return
        
        # Handle both dict format {CO1: {PO1: 2, PO2: 3}, ...} and matrix format
        if isinstance(co_po_mapping, dict) and co_po_mapping:
            with doc.create(Section('CO-PO Mapping Matrix')):
                # Get all PO keys
                po_keys = set()
                for co_data in co_po_mapping.values():
                    if isinstance(co_data, dict):
                        po_keys.update(co_data.keys())
                
                if not po_keys:
                    # Handle array format from frontend
                    if 'mapping' in co_po_mapping:
                        mapping_data = co_po_mapping.get('mapping', [])
                        if mapping_data and isinstance(mapping_data, list):
                            # Create simplified table from mapping array
                            doc.append(NoEscape(r'\begin{center}'))
                            doc.append(NoEscape(r'\begin{tabular}{|l|c|c|c|}'))
                            doc.append(NoEscape(r'\hline'))
                            doc.append(NoEscape(r'\textbf{CO} & \textbf{Strongest PO} & \textbf{Affinity} & \textbf{Rationale} \\'))
                            doc.append(NoEscape(r'\hline'))
                            for item in mapping_data[:10]:  # Limit to 10 rows
                                co = self._escape_latex(str(item.get('co', '')))
                                po = self._escape_latex(str(item.get('strongest_po', '')))
                                aff = str(item.get('affinity', ''))
                                rationale = self._escape_latex(str(item.get('rationale', ''))[:50])
                                doc.append(NoEscape(f'{co} & {po} & {aff} & {rationale} \\\\'))
                                doc.append(NoEscape(r'\hline'))
                            doc.append(NoEscape(r'\end{tabular}'))
                            doc.append(NoEscape(r'\end{center}'))
                    return
                
                # Standard dict format
                po_keys = sorted(list(po_keys))
                co_keys = sorted(co_po_mapping.keys())
                
                # Create table header
                cols = 'l' + 'c' * len(po_keys)
                doc.append(NoEscape(r'\begin{center}'))
                doc.append(NoEscape(f'\\begin{{tabular}}{{|{cols}|}}'))
                doc.append(NoEscape(r'\hline'))
                
                # Header row
                header = r'\textbf{CO/PO}'
                for po in po_keys:
                    header += f' & \\textbf{{{self._escape_latex(str(po))}}}'
                header += r' \\'
                doc.append(NoEscape(header))
                doc.append(NoEscape(r'\hline'))
                
                # Data rows
                for co in co_keys:
                    row = self._escape_latex(str(co))
                    for po in po_keys:
                        val = co_po_mapping.get(co, {}).get(po, '-')
                        row += f' & {val}'
                    row += r' \\'
                    doc.append(NoEscape(row))
                    doc.append(NoEscape(r'\hline'))
                
                doc.append(NoEscape(r'\end{tabular}'))
                doc.append(NoEscape(r'\end{center}'))
                doc.append(NewLine())
                doc.append(NoEscape(r'\textit{Affinity Level: 1=Slight, 2=Moderate, 3=Substantial}'))
    
    def _add_assessment(self, doc: Document, syllabus_data: Dict[str, Any]):
        """Add assessment pattern"""
        assessment = syllabus_data.get('assessment_pattern', {})
        if not assessment:
            return
            
        with doc.create(Section('Assessment Pattern')):
            with doc.create(Tabular('|l|c|')) as table:
                table.add_hline()
                table.add_row([bold('Component'), bold('Weightage (%)')])
                table.add_hline()
                
                for component, weight in assessment.items():
                    table.add_row([
                        self._escape_latex(component.title()),
                        str(weight)
                    ])
                    table.add_hline()
    
    def _add_references(self, doc: Document, syllabus_data: Dict[str, Any]):
        """Add references section"""
        references = syllabus_data.get('references', [])
        if not references:
            return
            
        with doc.create(Section('References')):
            doc.append(NoEscape(r'\begin{enumerate}'))
            for ref in references[:10]:
                ref_text = str(ref)[:300] if len(str(ref)) > 300 else str(ref)
                doc.append(NoEscape(f'\\item {self._escape_latex(ref_text)}'))
            doc.append(NoEscape(r'\end{enumerate}'))
    
    def _add_optimization_results(self, doc: Document, optimization_data: Dict[str, Any]):
        """Add optimization analysis results"""
        with doc.create(Section('Optimization Analysis')):
            # Bloom's analysis
            bloom_analysis = optimization_data.get('bloom_analysis', {})
            if bloom_analysis:
                with doc.create(Subsection("Bloom's Taxonomy Distribution")):
                    level_counts = bloom_analysis.get('level_counts', {})
                    if level_counts:
                        with doc.create(Tabular('|l|c|')) as table:
                            table.add_hline()
                            table.add_row([bold('Level'), bold('Count')])
                            table.add_hline()
                            for level, count in level_counts.items():
                                table.add_row([level.capitalize(), str(count)])
                                table.add_hline()
            
            # Rebalancing suggestions
            suggestions = optimization_data.get('rebalancing_suggestions', [])
            if suggestions:
                with doc.create(Subsection('Rebalancing Suggestions')):
                    doc.append(NoEscape(r'\begin{itemize}'))
                    for suggestion in suggestions[:5]:
                        doc.append(NoEscape(f'\\item {self._escape_latex(str(suggestion))}'))
                    doc.append(NoEscape(r'\end{itemize}'))


# Create singleton instance
latex_exporter = LaTeXExporter()
