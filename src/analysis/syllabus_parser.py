"""
Syllabus Parser for SCDO
Extracts structured information from syllabus documents (PDF, DOCX, TXT)
"""

import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

try:
    import PyPDF2
    import pdfplumber
except ImportError:
    PyPDF2 = None
    pdfplumber = None
    logging.warning("PDF libraries not installed. Install with: pip install PyPDF2 pdfplumber")

try:
    from docx import Document
except ImportError:
    logging.warning("python-docx not installed. Install with: pip install python-docx")

from ..utils.text_processing import TextProcessor


class SyllabusParser:
    """Parse syllabus documents and extract structured information"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse syllabus file and extract structured data
        
        Args:
            file_path: Path to syllabus file
            
        Returns:
            Structured syllabus data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Determine file type and parse
        if file_path.suffix.lower() == '.pdf':
            text = self._parse_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            text = self._parse_docx(file_path)
        elif file_path.suffix.lower() == '.txt':
            text = self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
        # Extract structured information
        return self._extract_structure(text)
        
    def _parse_pdf(self, file_path: Path) -> str:
        """Extract text from PDF"""
        text = ""
        
        if pdfplumber is None and PyPDF2 is None:
            raise ImportError("PDF libraries not installed. Please install PyPDF2 and pdfplumber.")
        
        try:
            # Try pdfplumber first (better for tables)
            if pdfplumber:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            else:
                raise ImportError("pdfplumber not installed")
                
        except Exception as e:
            self.logger.warning(f"pdfplumber failed or missing, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            if PyPDF2:
                try:
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                except Exception as e2:
                    self.logger.error(f"PDF parsing failed: {e2}")
                    raise
            else:
                if not text: # Only raise if we haven't extracted anything yet and both failed/missing
                     raise ImportError("PyPDF2 not installed and pdfplumber failed") from e
                
        return text
        
    def _parse_docx(self, file_path: Path) -> str:
        """Extract text from DOCX"""
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            
            # Also extract from tables
            for table in doc.tables:
                for row in table.rows:
                    text += "\n" + "\t".join([cell.text for cell in row.cells])
                    
            return text
            
        except Exception as e:
            self.logger.error(f"DOCX parsing failed: {e}")
            raise
            
    def _parse_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
                
    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """
        Extract structured information from syllabus text
        
        Args:
            text: Raw syllabus text
            
        Returns:
            Structured syllabus data
        """
        structure = {
            'course_title': self._extract_course_title(text),
            'course_code': self._extract_course_code(text),
            'credits': self._extract_credits(text),
            'prerequisites': self._extract_prerequisites(text),
            'objectives': self._extract_objectives(text),
            'learning_outcomes': self._extract_learning_outcomes(text),
            'units': self._extract_units(text),
            'assessment_pattern': self._extract_assessment(text),
            'references': self._extract_references(text),
            'co_po_mapping': self._extract_co_po_mapping(text),
            'raw_text': text
        }
        
        return structure
        
    def _extract_course_title(self, text: str) -> str:
        """Extract course title"""
        patterns = [
            r'(?:Course Title|Course Name)[:\s]+(.+?)(?=\n|Course Code)',
            r'^(.+?)(?=\n.*Course Code)',
            r'(?:Subject|Course)[:\s]+(.+?)(?=\n)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
                
        return "Unknown Course"
        
    def _extract_course_code(self, text: str) -> str:
        """Extract course code"""
        patterns = [
            r'(?:Course Code|Code)[:\s]+([A-Z]{2,4}\d{3,4})',
            r'\b([A-Z]{2,4}\d{3,4})\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()
                
        return "UNKNOWN"
        
    def _extract_credits(self, text: str) -> str:
        """Extract credit hours (L-T-P format)"""
        patterns = [
            r'(?:Credits?|Credit Hours?)[:\s]+(\d+-\d+-\d+)',
            r'(?:L-T-P)[:\s]+(\d+-\d+-\d+)',
            r'(\d+)\s*:\s*(\d+)\s*:\s*(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 3:
                    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                return match.group(1)
                
        return "0-0-0"
        
    def _extract_prerequisites(self, text: str) -> List[str]:
        """Extract prerequisites"""
        pattern = r'(?:Prerequisites?|Pre-requisites?)[:\s]+(.+?)(?=\n\n|\n[A-Z])'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            prereq_text = match.group(1)
            # Split by common delimiters
            prereqs = re.split(r'[,;]|\band\b', prereq_text)
            return [p.strip() for p in prereqs if p.strip()]
            
        return []
        
    def _extract_objectives(self, text: str) -> List[str]:
        """Extract course objectives"""
        pattern = r'(?:Course Objectives?|Objectives?)[:\s]+(.+?)(?=\n\n|Course Outcomes?|Learning Outcomes?)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            obj_text = match.group(1)
            # Extract numbered or bulleted items
            objectives = re.findall(r'(?:\d+\.|•|\*)\s*(.+?)(?=\n\d+\.|\n•|\n\*|$)', obj_text, re.DOTALL)
            return [obj.strip() for obj in objectives if obj.strip()]
            
        return []
        
    def _extract_learning_outcomes(self, text: str) -> List[Dict[str, str]]:
        """Extract course outcomes with Bloom's classification"""
        outcomes = []
        
        # Pattern for CO1, CO2, etc.
        pattern = r'(CO\d+)[:\s]+(.+?)(?=CO\d+|Unit|Assessment|$)'
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            co_code = match.group(1).upper()
            co_text = match.group(2).strip()
            
            # Classify Bloom's level
            bloom_level = self.text_processor.classify_bloom_level(co_text)
            
            outcomes.append({
                'code': co_code,
                'description': co_text,
                'bloom_level': bloom_level
            })
            
        return outcomes
        
    def _extract_units(self, text: str) -> List[Dict[str, Any]]:
        """Extract unit-wise syllabus"""
        units = []
        
        # Pattern for Unit 1, Unit 2, etc.
        pattern = r'Unit\s+(\d+|[IVX]+)[:\s]+(.+?)(?=Unit\s+\d+|Unit\s+[IVX]+|Assessment|References|$)'
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            unit_num = match.group(1)
            unit_content = match.group(2).strip()
            
            # Extract unit title (usually first line)
            lines = unit_content.split('\n')
            title = lines[0].strip() if lines else ""
            
            # Extract hours if mentioned
            hours_match = re.search(r'(\d+)\s*(?:hours?|hrs?)', unit_content, re.IGNORECASE)
            hours = int(hours_match.group(1)) if hours_match else 0
            
            # Extract topics
            topics = [line.strip() for line in lines[1:] if line.strip()]
            
            units.append({
                'unit_number': unit_num,
                'title': title,
                'topics': topics,
                'hours': hours
            })
            
        return units
        
    def _extract_assessment(self, text: str) -> Dict[str, Any]:
        """Extract assessment pattern"""
        assessment = {}
        
        # Common assessment components
        components = ['internal', 'external', 'midterm', 'final', 'assignment', 'quiz', 'project', 'lab']
        
        for component in components:
            pattern = rf'{component}[:\s]+(\d+)%?'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                assessment[component] = int(match.group(1))
                
        return assessment
        
    def _extract_references(self, text: str) -> List[str]:
        """Extract reference books and materials"""
        pattern = r'(?:References?|Text\s*Books?|Bibliography)[:\s]+(.+?)(?=\n\n|$)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            ref_text = match.group(1)
            # Extract numbered or bulleted items
            references = re.findall(r'(?:\d+\.|•|\*)\s*(.+?)(?=\n\d+\.|\n•|\n\*|$)', ref_text, re.DOTALL)
            return [ref.strip() for ref in references if ref.strip()]
            
        return []
        
    def _extract_co_po_mapping(self, text: str) -> Dict[str, Dict[str, int]]:
        """Extract CO-PO mapping matrix"""
        mapping = {}
        
        # Look for mapping table
        # This is a simplified version - real implementation would need table parsing
        pattern = r'(CO\d+).*?(PO\d+)[:\s]+(\d+)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            co = match.group(1).upper()
            po = match.group(2).upper()
            level = int(match.group(3))
            
            if co not in mapping:
                mapping[co] = {}
            mapping[co][po] = level
            
        return mapping
