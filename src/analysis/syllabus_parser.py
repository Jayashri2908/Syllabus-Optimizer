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
                
    def _extract_first_course_text(self, text: str) -> str:
        """
        Extract only the first course's text from a multi-course PDF.
        
        Detects course boundaries by looking for course code patterns and
        returns only the text for the first complete course.
        
        Args:
            text: Raw PDF text potentially containing multiple courses
            
        Returns:
            Text for the first course only
        """
        # Pattern to detect course headers like "MSCCS24101: Design and Analysis"
        # or "Course Code Course Name" table format
        course_header_patterns = [
            # Pattern: "COURSECODE: Course Title" followed by Course Type
            r'([A-Z]{2,}\d{5,}):\s*[A-Za-z][^\n]+\nCourse\s*Type',
            # Pattern: Course code in structured section
            r'([A-Z]{2,}\d{5,})\s+[A-Za-z][A-Za-z\s]+\nCourse\s*Type',
        ]
        
        # Find all course code occurrences that mark course starts
        course_starts = []
        for pattern in course_header_patterns:
            for match in re.finditer(pattern, text):
                course_starts.append(match.start())
        
        # Sort and remove duplicates
        course_starts = sorted(set(course_starts))
        
        if len(course_starts) >= 2:
            # Multi-course document - extract only first course
            first_course_start = course_starts[0]
            second_course_start = course_starts[1]
            
            # Include some context before the first course (headers/metadata)
            prefix_start = max(0, first_course_start - 500)
            
            first_course_text = text[prefix_start:second_course_start]
            self.logger.info(f"Multi-course PDF detected. Extracting first course only (chars {first_course_start}-{second_course_start})")
            return first_course_text
        
        # Alternative detection: look for repeated "Course Content" sections
        course_content_matches = list(re.finditer(r'Course\s*Content\nUnit\s*No', text, re.IGNORECASE))
        
        if len(course_content_matches) >= 2:
            # Found multiple course content sections
            first_end = course_content_matches[1].start()
            
            # Find where the first course starts (after Programme Structure)
            prog_struct_match = re.search(r'Programme\s*Structure', text)
            first_start = prog_struct_match.end() if prog_struct_match else 0
            
            first_course_text = text[first_start:first_end]
            self.logger.info(f"Detected {len(course_content_matches)} courses. Extracting first course only.")
            return first_course_text
        
        # Single course or couldn't detect boundaries - use full text
        return text

    def _extract_structure(self, text: str) -> Dict[str, Any]:
        """
        Extract structured information from syllabus text
        
        Args:
            text: Raw syllabus text
            
        Returns:
            Structured syllabus data
        """
        # Extract only the first course's text if this is a multi-course document
        course_text = self._extract_first_course_text(text)
        
        structure = {
            'course_title': self._extract_course_title(course_text),
            'course_code': self._extract_course_code(course_text),
            'credits': self._extract_credits(course_text),
            'prerequisites': self._extract_prerequisites(course_text),
            'objectives': self._extract_objectives(course_text),
            'learning_outcomes': self._extract_learning_outcomes(course_text),
            'units': self._extract_units(course_text),
            'assessment_pattern': self._extract_assessment(course_text),
            'references': self._extract_references(course_text),
            'co_po_mapping': self._extract_co_po_mapping(course_text),
            'raw_text': text  # Keep original full text for reference
        }
        
        return structure
        
    def _extract_course_title(self, text: str) -> str:
        """Extract course title"""
        patterns = [
            # Pattern for "COURSECODE: Course Title" format
            r'([A-Z]{2,}\d+):\s*(.+?)(?=\n)',
            # Pattern for "Course Title:" format
            r'(?:Course Title|Course Name)[:\s]+(.+?)(?=\n|Course Code)',
            # Pattern for title followed by Course Type
            r'([A-Za-z][A-Za-z\s&]+?)\nCourse\s*Type',
            # Subject pattern
            r'(?:Subject|Course)[:\s]+(.+?)(?=\n)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Handle patterns with multiple groups
                if len(match.groups()) >= 2 and match.group(2):
                    return match.group(2).strip()
                return match.group(1).strip()
                
        return "Unknown Course"
        
    def _extract_course_code(self, text: str) -> str:
        """Extract course code"""
        patterns = [
            # Pattern for course codes like MSCCS24101, CSE301, etc.
            r'\b([A-Z]{2,}\d{4,6})\b',
            r'(?:Course Code|Code)[:\s]+([A-Z0-9]+)',
            r'\b([A-Z]{2,4}\d{3,4})\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
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
        
        # First, try to find the Course Outcomes section
        co_section_pattern = r'Course\s*Outcomes?(.+?)(?:Mapping|CO\s*PO|Unit|Course\s*Content|$)'
        co_section_match = re.search(co_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if co_section_match:
            co_text = co_section_match.group(1)
            
            # Pattern for numbered outcomes: "1 Analyze worst-case..."
            numbered_pattern = r'^\s*(\d+)\s+([A-Z][^\n]+?)(?=\n\s*\d+\s+[A-Z]|\nMapping|$)'
            matches = re.finditer(numbered_pattern, co_text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                num = match.group(1)
                description = match.group(2).strip()
                
                # Skip if it looks like a CO-PO mapping row (contains mostly numbers)
                if re.match(r'^[\d\s,.-]+$', description):
                    continue
                    
                # Skip very short descriptions
                if len(description) < 20:
                    continue
                
                bloom_level = self.text_processor.classify_bloom_level(description)
                
                outcomes.append({
                    'code': f'CO{num}',
                    'description': description,
                    'bloom_level': bloom_level
                })
        
        # Fallback: Pattern for CO1:, CO2:, etc.
        if not outcomes:
            pattern = r'(CO\d+)[:\s]+([A-Za-z][^\n]+?)(?=CO\d+|Mapping|$)'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                co_code = match.group(1).upper()
                co_text = match.group(2).strip()
                
                # Skip if it looks like mapping numbers
                if re.match(r'^[\d\s,.-]+$', co_text):
                    continue
                
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
        
        # Multiple patterns for different unit formats
        patterns = [
            # Format: "Unit No I Title Hours" or "Unit No 1 Title Hours"
            r'Unit\s*No\.?\s*([IVX]+|\d+)\s+(.+?)\s+(\d+)\s*Hours?',
            # Format: "Unit 1: Title" or "Unit I: Title"
            r'Unit\s+(\d+|[IVX]+)[:\s]+(.+?)(?=\n)',
        ]
        
        # Try first pattern (Unit No format)
        pattern = patterns[0]
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        if matches:
            for i, match in enumerate(matches):
                unit_num = match.group(1)
                title = match.group(2).strip()
                hours = int(match.group(3)) if match.group(3) else 0
                
                # Find content between this unit and next unit (or end)
                start = match.end()
                if i + 1 < len(matches):
                    end = matches[i + 1].start()
                else:
                    # Find next section marker
                    next_section = re.search(r'\n(Textbooks?|References?|Assessment)', text[start:], re.IGNORECASE)
                    end = start + next_section.start() if next_section else len(text)
                
                unit_content = text[start:end].strip()
                
                # Extract topics - lines that contain actual content
                topics = []
                for line in unit_content.split('\n'):
                    line = line.strip()
                    # Skip empty lines, page headers, and CO/BTL references
                    if line and len(line) > 10 and not re.match(r'^[\d\s,]+$', line):
                        if not re.match(r'^(Unit|CO|BTL|M\.Sc|Vishwakarma)', line, re.IGNORECASE):
                            topics.append(line)
                
                units.append({
                    'unit_number': unit_num,
                    'title': title,
                    'topics': topics[:10],  # Limit topics per unit
                    'hours': hours
                })
        else:
            # Try second pattern (Unit 1: format)
            pattern = patterns[1]
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                unit_num = match.group(1)
                unit_content = match.group(2).strip()
                
                lines = unit_content.split('\n')
                title = lines[0].strip() if lines else ""
                
                hours_match = re.search(r'(\d+)\s*(?:hours?|hrs?)', unit_content, re.IGNORECASE)
                hours = int(hours_match.group(1)) if hours_match else 0
                
                topics = [line.strip() for line in lines[1:] if line.strip() and len(line.strip()) > 10]
                
                units.append({
                    'unit_number': unit_num,
                    'title': title,
                    'topics': topics[:10],
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
