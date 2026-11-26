"""
Syllabus Parser for SCDO
Extracts structured information from syllabus documents (PDF, DOCX, TXT)
"""

import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

try:
    import pypdf
    import pdfplumber
except ImportError:
    pypdf = None
    pdfplumber = None
    logging.warning("PDF libraries not installed. Install with: pip install pypdf pdfplumber")

try:
    from docx import Document
except ImportError:
    logging.warning("python-docx not installed. Install with: pip install python-docx")

# OCR support for scanned PDFs
try:
    import easyocr
    import pymupdf
    import numpy as np
    EASYOCR_AVAILABLE = True
    logging.info("EasyOCR and PyMuPDF found. Pip-only OCR available.")
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    import os
    import platform
    
    # Configure Tesseract path for Windows
    if platform.system() == 'Windows':
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'),
        ]
        for tess_path in tesseract_paths:
            if os.path.exists(tess_path):
                pytesseract.pytesseract.tesseract_cmd = tess_path
                logging.info(f"Tesseract found at: {tess_path}")
                break
    
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.info("OCR libraries not installed. Scanned PDFs won't be supported. Install with: pip install pytesseract pdf2image Pillow")

from ..utils.text_processing import TextProcessor, normalize_ocr_text, roman_to_int

# Import AI model for LLM-based parsing fallback
try:
    from ..ai.openrouter_model import OpenRouterModel
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logging.info("AI model not available for LLM-based parsing fallback")


# Custom exception classes raised by the parser so the API layer can
# surface actionable messages to the user instead of bare 500s.
class PDFParsingError(Exception):
    """Raised when a PDF cannot be opened or is structurally invalid."""
    pass


class NoTextExtractedError(Exception):
    """Raised when every extraction method (incl. OCR) returned zero useful text."""
    pass


class SyllabusParser:
    """Parse syllabus documents and extract structured information"""

    def __init__(self, use_llm_fallback: bool = True, ocr_engine: str = "auto",
                 ocr_dpi: int = 300, ocr_min_chars_per_page: int = 50):
        """
        Args:
            use_llm_fallback: If True, fall back to LLM-based extraction when
                the regex pass yields too few units/outcomes.
            ocr_engine: 'auto' (default), 'tesseract', 'easyocr', 'online', or 'none'.
                'auto' picks the fastest available engine for the platform.
            ocr_dpi: Rendering DPI used by PyMuPDF before running OCR.
                Higher = better quality, slower. 300 is the sweet spot.
            ocr_min_chars_per_page: Average chars/page below which OCR is triggered.
        """
        self.logger = logging.getLogger(__name__)
        self.text_processor = TextProcessor()
        self.use_llm_fallback = use_llm_fallback and LLM_AVAILABLE
        self.ai_model = None
        self.ocr_dpi = ocr_dpi
        self.ocr_min_chars_per_page = ocr_min_chars_per_page
        self.ocr_engine = self._resolve_ocr_engine(ocr_engine)
        # Last-call diagnostics populated by _parse_pdf.
        self.last_diagnostics: Dict[str, Any] = {}

        if self.use_llm_fallback:
            try:
                self.ai_model = OpenRouterModel()
                if not self.ai_model.is_available():
                    self.logger.info("LLM not available (no API key), using regex-only parsing")
                    self.use_llm_fallback = False
            except Exception as e:
                self.logger.warning(f"Failed to initialize AI model for parsing: {e}")
                self.use_llm_fallback = False

    @staticmethod
    def _resolve_ocr_engine(requested: str) -> str:
        """Pick an OCR engine that's actually available on this machine."""
        if requested == "auto":
            if OCR_AVAILABLE:
                return "tesseract"  # fastest, best for clean printed text
            if EASYOCR_AVAILABLE:
                return "easyocr"
            return "online"
        return requested
        
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
        """
        Extract text from a PDF using a layered strategy:

        1. Validate PDF integrity (PyMuPDF can read PDFs other libs choke on).
        2. PyMuPDF native text extraction (fast, robust to malformed files).
        3. pdfplumber with table-aware reconstruction (best for native PDFs
           whose syllabus is inside a table).
        4. pypdf (last resort for ancient PDFs).
        5. OCR (Tesseract -> EasyOCR -> OCR.space) if every text pass below
           the configured chars-per-page threshold.

        Populates ``self.last_diagnostics`` so the API layer can tell the
        user which engine actually produced the text and what to do next.
        """
        if pdfplumber is None and pypdf is None:
            raise ImportError("PDF libraries not installed. Please install pypdf and pdfplumber.")

        diagnostics: Dict[str, Any] = {
            "file": str(file_path),
            "file_size_bytes": file_path.stat().st_size if file_path.exists() else 0,
            "engines_tried": [],
            "engine_used": None,
            "page_count": None,
            "chars_per_page": {},
            "ocr_used": False,
            "ocr_engine": None,
            "warnings": [],
        }
        self.last_diagnostics = diagnostics

        self.logger.info(f"Parsing PDF: {file_path}")
        text = ""
        engines = []

        # -- 1. Integrity check -------------------------------------------------
        page_count = self._pdf_page_count(file_path)
        if page_count == 0:
            diagnostics["warnings"].append(
                "PDF has 0 readable pages — file may be corrupt or empty"
            )
            raise PDFParsingError(
                "This file appears to be corrupt: no readable pages were found. "
                "Please re-export the PDF or supply the original document."
            )

        diagnostics["page_count"] = page_count

        # -- 2. PyMuPDF native text ---------------------------------------------
        pymupdf_text, pymupdf_chars = self._extract_with_pymupdf(file_path)
        engines.append("pymupdf")
        if pymupdf_chars > 0:
            diagnostics["chars_per_page"]["pymupdf"] = pymupdf_chars
            if pymupdf_chars >= self.ocr_min_chars_per_page * max(page_count, 1):
                text = pymupdf_text
                diagnostics["engine_used"] = "pymupdf"
                self.logger.info(f"PyMuPDF extracted {pymupdf_chars} chars — using it as primary source")
                diagnostics["engines_tried"].append("pymupdf:ok")
                return normalize_ocr_text(text)
            self.logger.info(
                f"PyMuPDF returned only {pymupdf_chars} chars from {page_count} page(s); "
                "pdfplumber table-aware pass next"
            )
            diagnostics["engines_tried"].append("pymupdf:low")
        else:
            diagnostics["engines_tried"].append("pymupdf:empty")

        # -- 3. pdfplumber with table-reconstruction ----------------------------
        if pdfplumber:
            plumber_text, plumber_chars = self._extract_with_pdfplumber(file_path)
            engines.append("pdfplumber")
            diagnostics["chars_per_page"]["pdfplumber"] = plumber_chars
            if plumber_chars > pymupdf_chars:
                text = plumber_text
                diagnostics["engine_used"] = "pdfplumber"
                self.logger.info(
                    f"pdfplumber recovered {plumber_chars} chars (more than PyMuPDF's {pymupdf_chars})"
                )
                diagnostics["engines_tried"].append("pdfplumber:ok")
                return normalize_ocr_text(text)
            diagnostics["engines_tried"].append("pdfplumber:no-improvement")

        # -- 4. pypdf last-resort -----------------------------------------------
        if pypdf:
            pypdf_text, pypdf_chars = self._extract_with_pypdf(file_path)
            engines.append("pypdf")
            diagnostics["chars_per_page"]["pypdf"] = pypdf_chars
            if pypdf_chars > max(pymupdf_chars, len(text)):
                text = pypdf_text
                diagnostics["engine_used"] = "pypdf"
                self.logger.info(f"pypdf recovered {pypdf_chars} chars")
                diagnostics["engines_tried"].append("pypdf:ok")
                return normalize_ocr_text(text)
            diagnostics["engines_tried"].append("pypdf:no-improvement")

        # -- 5. OCR --------------------------------------------------------------
        self.logger.info(
            f"Native text extraction low ({len(text.strip())} chars from {page_count} pages). "
            f"Falling back to OCR (engine={self.ocr_engine}, dpi={self.ocr_dpi})."
        )
        diagnostics["ocr_used"] = True
        # Aggressive normalization on OCR output (it has wrapped/duplicated lines)
        ocr_text, ocr_engine_used = self._ocr_with_engine(file_path)
        diagnostics["ocr_engine"] = ocr_engine_used
        diagnostics["chars_per_page"]["ocr"] = len(ocr_text.strip())

        if len(ocr_text.strip()) > len(text.strip()):
            diagnostics["engine_used"] = f"ocr:{ocr_engine_used}"
            text = ocr_text
            self.logger.info(f"OCR ({ocr_engine_used}) extracted {len(text.strip())} chars")
        else:
            diagnostics["warnings"].append(
                f"OCR ({ocr_engine_used}) returned no improvement over native extraction"
            )
            self.logger.warning("OCR did not yield more text than native extraction")

        if len(text.strip()) == 0:
            diagnostics["warnings"].append("No text recovered from PDF by any method")
            raise NoTextExtractedError(
                "Could not extract text from this PDF. It may be an image-only scan; "
                "ensure Tesseract OCR or EasyOCR is installed and the file is not "
                "password-protected."
            )

        return normalize_ocr_text(text)

    # ------------------------------------------------------------------ #
    # Layered extractor helpers                                          #
    # ------------------------------------------------------------------ #
    def _pdf_page_count(self, file_path: Path) -> int:
        """Return the number of pages a PDF has, or 0 if it cannot be opened."""
        # PyMuPDF is the most tolerant PDF engine we have available.
        try:
            if EASYOCR_AVAILABLE:
                with pymupdf.open(file_path) as doc:
                    return len(doc)
        except Exception as e:
            self.logger.warning(f"PyMuPDF could not open PDF for page count: {e}")

        # Fallback: pdfplumber
        if pdfplumber:
            try:
                with pdfplumber.open(file_path) as pdf:
                    return len(pdf.pages)
            except Exception as e:
                self.logger.warning(f"pdfplumber could not open PDF for page count: {e}")

        # Last resort: pypdf
        if pypdf:
            try:
                with open(file_path, "rb") as f:
                    return len(pypdf.PdfReader(f).pages)
            except Exception as e:
                self.logger.warning(f"pypdf could not open PDF for page count: {e}")

        return 0

    def _extract_with_pymupdf(self, file_path: Path):
        """Use PyMuPDF's plain extract_text() — fast, robust to malformed PDFs."""
        if not EASYOCR_AVAILABLE:  # pymupdf imported in that branch
            return "", 0
        try:
            with pymupdf.open(file_path) as doc:
                chunks = []
                for page in doc:
                    chunks.append(page.get_text() or "")
                text = "\n".join(chunks)
                return text, len(text.strip())
        except Exception as e:
            self.logger.warning(f"PyMuPDF extraction failed: {e}")
            return "", 0

    def _extract_with_pdfplumber(self, file_path: Path):
        """pdfplumber with the existing table-aware reconstruction."""
        if not pdfplumber:
            return "", 0
        try:
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                self.logger.info(f"pdfplumber: PDF has {len(pdf.pages)} pages")
                for i, page in enumerate(pdf.pages):
                    page_text = self._extract_page_text(page)
                    if page_text:
                        text_parts.append(page_text)
                        self.logger.debug(f"Page {i+1}: extracted {len(page_text)} chars")
                    else:
                        self.logger.warning(f"Page {i+1}: no text extracted")
            text = "\n".join(text_parts) + "\n"
            return text, len(text.strip())
        except Exception as e:
            self.logger.warning(f"pdfplumber extraction failed: {e}")
            return "", 0

    def _extract_with_pypdf(self, file_path: Path):
        """Plain per-page extraction via pypdf. Sometimes the only thing that works."""
        if not pypdf:
            return "", 0
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                parts = []
                for page in reader.pages:
                    parts.append(page.extract_text() or "")
                text = "\n".join(parts) + "\n"
                return text, len(text.strip())
        except Exception as e:
            self.logger.warning(f"pypdf extraction failed: {e}")
            return "", 0

    def _ocr_with_engine(self, file_path: Path):
        """Run OCR using whatever engine is configured/available."""
        engine = self.ocr_engine
        if engine == "tesseract" and OCR_AVAILABLE:
            return self._ocr_pdf(file_path), "tesseract"
        if engine == "easyocr" and EASYOCR_AVAILABLE:
            return self._ocr_easyocr(file_path), "easyocr"
        if engine == "online":
            return self._ocr_online(file_path), "online"
        # Auto-degrade if the requested engine isn't available
        if OCR_AVAILABLE:
            return self._ocr_pdf(file_path), "tesseract"
        if EASYOCR_AVAILABLE:
            return self._ocr_easyocr(file_path), "easyocr"
        return self._ocr_online(file_path), "online"

    def _extract_page_text(self, page) -> str:
        """
        Extract text from a single pdfplumber page.

        Uses table-aware extraction: if the page contains tables, reconstructs
        text from table cells in proper reading order. Falls back to plain
        extract_text() for pages without tables.

        Reading order: interleaves non-table text and tables based on their
        vertical position on the page, so headings above a table appear before
        the table, and text below appears after.
        """
        # Try table-aware extraction first
        try:
            tables = page.find_tables()
        except Exception:
            tables = []

        if not tables:
            return page.extract_text() or ""

        table_bboxes = [t.bbox for t in tables]  # (x0, top, x1, bottom)

        # Collect non-table chars and group into lines
        chars = page.chars
        non_table_chars = [
            c for c in chars
            if not any(
                bbox[0] <= c['x0'] <= bbox[2] and bbox[1] <= c['top'] <= bbox[3]
                for bbox in table_bboxes
            )
        ]

        # Group non-table chars into text lines by vertical position
        non_table_lines = []
        if non_table_chars:
            # Tolerance for same-line grouping (chars within 3px vertically)
            sorted_chars = sorted(non_table_chars, key=lambda c: (c['top'], c['x0']))
            current_line = [sorted_chars[0]]
            for c in sorted_chars[1:]:
                if abs(c['top'] - current_line[0]['top']) <= 3:
                    current_line.append(c)
                else:
                    line_text = "".join(ch['text'] for ch in sorted(current_line, key=lambda x: x['x0']))
                    if line_text.strip():
                        non_table_lines.append((current_line[0]['top'], line_text))
                    current_line = [c]
            # Flush last line
            line_text = "".join(ch['text'] for ch in sorted(current_line, key=lambda x: x['x0']))
            if line_text.strip():
                non_table_lines.append((current_line[0]['top'], line_text))

        # Collect table text with their vertical position
        table_entries = []
        for table, bbox in zip(tables, table_bboxes):
            rows = table.extract()
            if not rows:
                continue
            row_texts = []
            for row in rows:
                cells = [(c or "") for c in row]
                line = "\t".join(cells)
                if line.strip():
                    row_texts.append(line)
            if row_texts:
                table_entries.append((bbox[1], "\n".join(row_texts)))  # bbox[1] = top

        # Merge both lists and sort by vertical position (reading order)
        all_blocks = non_table_lines + table_entries
        all_blocks.sort(key=lambda b: b[0])

        return "\n".join(text for _, text in all_blocks)
    
    def _ocr_online(self, file_path: Path) -> str:
        """Extract text from scanned PDF using free online OCR API (OCR.space)"""
        import requests
        import os
        
        text = ""
        
        # Check file size - free API has 1MB limit
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > 1:
            self.logger.warning(f"File is {file_size_mb:.1f}MB - OCR.space free API limit is 1MB")
            self.logger.info("Consider using a smaller PDF or installing local Tesseract OCR")
        
        # Retry logic for network issues
        max_retries = 2
        for attempt in range(max_retries):
            try:
                self.logger.info(f"OCR.space API attempt {attempt + 1}/{max_retries}...")
                
                # OCR.space free API - no signup required for basic usage
                api_url = "https://api.ocr.space/parse/image"
                
                with open(file_path, 'rb') as f:
                    response = requests.post(
                        api_url,
                        files={'file': f},
                        data={
                            'apikey': 'helloworld',  # Free demo API key
                            'language': 'eng',
                            'isOverlayRequired': False,
                            'filetype': 'PDF',
                            'detectOrientation': True,
                            'scale': True,
                            'OCREngine': 2  # Better for dense text
                        },
                        timeout=120  # Increased timeout for large files
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ParsedResults'):
                        for page_result in result['ParsedResults']:
                            page_text = page_result.get('ParsedText', '')
                            if page_text:
                                text += page_text + "\n"
                        if text:
                            self.logger.info(f"Online OCR extracted {len(text)} chars")
                            return text  # Success, return immediately
                    else:
                        error_msg = result.get('ErrorMessage', '') or result.get('OCRExitCode', 'Unknown error')
                        self.logger.warning(f"OCR.space returned no results: {error_msg}")
                        if 'limit' in str(error_msg).lower() or 'size' in str(error_msg).lower():
                            self.logger.info("File may be too large for free API")
                            break  # Don't retry if it's a size limit issue
                else:
                    self.logger.error(f"OCR.space API error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"OCR timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    self.logger.info("Retrying...")
                    continue
            except Exception as e:
                self.logger.error(f"Online OCR failed: {e}")
                break
            
        return text
    
    def _ocr_easyocr(self, file_path: Path) -> str:
        """Extract text using EasyOCR and PyMuPDF rendering (requires NO system dependencies)"""
        text = ""
        try:
            self.logger.info(f"Loading PDF with PyMuPDF for rendering...")
            doc = pymupdf.open(file_path)
            
            self.logger.info("Initializing EasyOCR reader (CPU mode)...")
            # Create reader once for all pages
            reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            
            for i, page in enumerate(doc):
                self.logger.info(f"OCR processing page {i+1}/{len(doc)}...")
                # Render to 300 DPI for OCR
                pix = page.get_pixmap(dpi=300)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                
                results = reader.readtext(img, detail=0, paragraph=True)
                page_text = "\n".join(results)
                
                if page_text:
                    text += page_text + "\n\n"
                    self.logger.info(f"Page {i+1}: EasyOCR extracted {len(page_text)} chars")
                else:
                    self.logger.warning(f"Page {i+1}: EasyOCR found no text")
                    
            doc.close()
            self.logger.info(f"EasyOCR extracted total {len(text)} chars")
            
        except Exception as e:
            self.logger.error(f"EasyOCR parsing failed: {e}")
            
        return text

    def _ocr_pdf(self, file_path: Path) -> str:
        """Extract text from scanned PDF using local OCR (Tesseract)"""
        text = ""
        try:
            self.logger.info(f"Converting PDF pages to images for OCR...")
            # Convert PDF pages to images at 300 DPI for better OCR quality
            # Higher DPI = more text extracted (tested: 300 DPI extracts 3x more than 200 DPI)
            images = convert_from_path(str(file_path), dpi=300)
            self.logger.info(f"Converted {len(images)} pages to images")
            
            for i, image in enumerate(images):
                self.logger.info(f"OCR processing page {i+1}...")
                page_text = pytesseract.image_to_string(image, lang='eng')
                if page_text:
                    text += page_text + "\n"
                    self.logger.info(f"Page {i+1}: OCR extracted {len(page_text)} chars")
                else:
                    self.logger.warning(f"Page {i+1}: OCR found no text")
                    
            self.logger.info(f"OCR extracted total {len(text)} chars")
            
        except Exception as e:
            self.logger.error(f"Local OCR failed: {e}")
            self.logger.info("Make sure Tesseract OCR is installed: https://github.com/tesseract-ocr/tesseract")
            
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
        Extract structured information from syllabus text.

        Args:
            text: Raw syllabus text

        Returns:
            Structured syllabus data, including parser_diagnostics
        """
        self.logger.info(f"Extracting structure from text of {len(text)} chars")

        # Extract only the first course's text if this is a multi-course document
        course_text = self._extract_first_course_text(text)

        # First, try regex-based extraction
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
            'raw_text': text,  # Keep original full text for reference
            # Surface parser diagnostics so the UI can show what happened.
            'parser_diagnostics': dict(self.last_diagnostics),
        }

        # Check if regex extraction yielded poor results - use LLM fallback
        regex_units = len(structure['units'])
        regex_outcomes = len(structure['learning_outcomes'])

        if self.use_llm_fallback and self.ai_model and len(text.strip()) > 50 and (regex_units < 2 or regex_outcomes < 2):
            self.logger.info(f"Regex extraction yielded poor results (units={regex_units}, outcomes={regex_outcomes}). Trying LLM fallback...")

            try:
                llm_structure = self._extract_structure_with_llm(course_text)

                # Merge LLM results - prefer LLM if it found more content
                if len(llm_structure.get('units', [])) > regex_units:
                    self.logger.info(f"LLM found {len(llm_structure['units'])} units vs regex's {regex_units}")
                    structure['units'] = llm_structure['units']

                if len(llm_structure.get('learning_outcomes', [])) > regex_outcomes:
                    self.logger.info(f"LLM found {len(llm_structure['learning_outcomes'])} outcomes vs regex's {regex_outcomes}")
                    structure['learning_outcomes'] = llm_structure['learning_outcomes']

                # Update other fields if regex got defaults
                if structure['course_title'] == 'Unknown Course' and llm_structure.get('course_title'):
                    structure['course_title'] = llm_structure['course_title']
                if structure['course_code'] == 'UNKNOWN' and llm_structure.get('course_code'):
                    structure['course_code'] = llm_structure['course_code']

            except Exception as e:
                self.logger.warning(f"LLM fallback parsing failed: {e}")

        structure['parser_diagnostics']['regex_results'] = {
            'units_found': len(structure['units']),
            'outcomes_found': len(structure['learning_outcomes']),
            'references_found': len(structure['references']),
            'title_found': structure['course_title'] != 'Unknown Course',
            'code_found': structure['course_code'] != 'UNKNOWN',
        }
        self.last_diagnostics = structure['parser_diagnostics']

        self.logger.info(
            f"Extraction complete: title='{structure['course_title']}', "
            f"outcomes={len(structure['learning_outcomes'])}, "
            f"units={len(structure['units'])}, raw_text={len(structure['raw_text'])} chars"
        )

        return structure
    
    def _extract_structure_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Use LLM to extract structured syllabus information.
        More robust for OCR'd text with errors or unusual formatting.
        """
        import json
        
        prompt = f"""Extract structured information from this syllabus text. The text may contain OCR errors.

Return a JSON object with these fields:
- course_title: string (the course name)
- course_code: string (e.g., "BTECCE25101")
- units: array of objects with:
  - unit_number: string or number
  - title: string (unit title)
  - topics: array of topic strings
  - hours: number (teaching hours)
- learning_outcomes: array of objects with:
  - code: string (e.g., "CO1", "CO2")
  - description: string (the learning outcome text)
  - bloom_level: string (one of: "Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create")

Syllabus text:
{text[:6000]}

Return ONLY valid JSON, no markdown formatting or code blocks."""

        system_prompt = """You are a syllabus parser assistant. Extract structured information from educational syllabus documents.
Be robust to OCR errors (e.g., 'Howrs' means 'Hours', '0' might be 'O', etc.).
Focus on finding units and learning outcomes even if the text is messy."""

        try:
            response = self.ai_model.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.1,  # Low temp for structured extraction
                max_tokens=2000
            )
            
            # Clean and parse JSON
            response = response.strip()
            if response.startswith('```'):
                # Remove markdown code blocks if present
                response = re.sub(r'^```(?:json)?\n?', '', response)
                response = re.sub(r'\n?```$', '', response)
            
            result = json.loads(response)
            
            self.logger.info(f"LLM extracted: {len(result.get('units', []))} units, {len(result.get('learning_outcomes', []))} outcomes")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"LLM returned invalid JSON: {e}")
            return {}
        except Exception as e:
            self.logger.warning(f"LLM extraction failed: {e}")
            return {}
        
    def _extract_course_title(self, text: str) -> str:
        """Extract course title.

        Tries structural patterns first (course code prefix, Course Title:,
        Subject: etc.), then falls back to "first plausible line" detection.
        Skips generic section headers like "Course Outcomes:" that would
        otherwise be mis-extracted as title.
        """
        # Negative lookbehind inside patterns to avoid matching section headers.
        patterns = [
            # Pattern for "COURSECODE: Course Title" format
            r'([A-Z]{2,}[\d]+):\s*(.+?)(?=\n)',
            # Pattern for "Course Title:" / "Course Name:" — guarded so it
            # does NOT match "Course Outcomes:", "Course Code:", etc.
            r'(?:Course\s*Title|Course\s*Name)\s*[:\-]\s*(.+?)(?=\n|Course\s*Code)',
            # Pattern for title followed by Course Type
            r'([A-Za-z][A-Za-z\s&]+?)\nCourse\s*Type',
            # Subject pattern — guarded so we don't capture section headers.
            r'(?:Subject\s*[:\-]|Course\s*[:\-])\s*(?!Outcomes?|Code|Type|Content|Objective|Prerequisite|Reference|Assessment|Mapping)\s*(.+?)(?=\n)',
            # Pattern for "Title: Something" at start
            r'^(.+?)\n(?:Course\s*Type|Credits?|L-T-P)',
            # Pattern for syllabus headers
            r'Syllabus\s*(?:for|of)?\s*:?\s*(.+?)(?=\n)',
            # Pattern for "Name of the Course:"
            r'(?:Name of the course|Course name)[:\s]+(.+?)(?=\n)',
            # Pattern for lines after department headers
            r'(?:Department\s*of\s*.+?\n+)(.+?)(?=\n)',
            # Pattern matching any bolded or emphasized title
            r'\*\*(.+?)\*\*',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Handle patterns with multiple groups
                if len(match.groups()) >= 2 and match.group(2):
                    title = match.group(2).strip()
                else:
                    title = match.group(1).strip()
                # Clean up title - remove extra whitespace and common prefixes
                title = re.sub(r'\s+', ' ', title)
                title = re.sub(r'^(Course|Subject|Title)[:\s]*', '', title, flags=re.IGNORECASE)
                # Final guard: reject section-header-like "titles"
                if title and len(title) > 3 and not re.match(
                    r'^(Outcome|Code|Type|Content|Objective|Prerequisite|Reference|Assessment|Mapping)s?$',
                    title,
                    re.IGNORECASE,
                ):
                    return title

        # Fallback: Try to find first meaningful line (often the title)
        lines = text.split('\n')
        exclude_re = re.compile(
            r'^(Course\s*Type|Course\s*Outcomes?|Course\s*Code|Course\s*Content|Course\s*Objective|'
            r'Credits?|L-T-P|Semester|University|Department|Programme|Text\s*Books?|References?|'
            r'Unit\s*No|Objectives?|Statement|Mapping|Assessment)',
            re.IGNORECASE,
        )
        for line in lines[:25]:  # Check first 25 lines
            line = line.strip()
            if line and len(line) > 10 and len(line) < 120:
                if exclude_re.match(line):
                    continue
                if re.match(r'[A-Z]', line):  # Starts with capital letter
                    return line

        return "Unknown Course"
        
    def _extract_course_code(self, text: str) -> str:
        """Extract course code"""
        patterns = [
            # Pattern for course codes like MSCCS24101, CSE301, CS101, etc.
            r'(?:Course\s*Code|Code)[:\s]+([A-Z]{2,}[\d]+[A-Z]?\d*)',
            r'\b([A-Z]{2,}\d{4,6})\b',
            r'\b([A-Z]{2,4}\d{3,4})\b',
            # Pattern for codes at the start of title line
            r'^([A-Z]{2,}\d+)[:\s]',
            # Pattern for codes in table format
            r'Course\s*Code\s*\n?\s*([A-Z]{2,}[\d]+)',
            # Pattern for codes like 22CS301
            r'\b(\d{2}[A-Z]{2,}\d{3})\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                code = match.group(1).upper()
                # Validate - should have both letters and numbers
                if re.match(r'^[A-Z]+\d+$', code) or re.match(r'^\d+[A-Z]+\d+$', code):
                    # Exclude CO patterns (CO1, CO2, etc.) - these are course outcomes, not course codes
                    if re.match(r'^CO\d+$', code):
                        continue
                    return code
        
        # Fallback: Look for any alphanumeric pattern that looks like a code (at least 5 chars)
        code_match = re.search(r'\b([A-Z]{2,}\d{3,}[A-Z]?\d*)\b', text)
        if code_match:
            code = code_match.group(1).upper()
            if not re.match(r'^CO\d+$', code):
                return code
            
        return "UNKNOWN"
        
    def _extract_credits(self, text: str) -> str:
        """Extract credit hours (L-T-P format)"""
        patterns = [
            # Standard L-T-P format
            r'(?:L-T-P|L T P|LTP)[:\s]*([\d]+)\s*[-:]\s*([\d]+)\s*[-:]\s*([\d]+)',
            r'(?:Credits?|Credit Hours?)[:\s]+([\d]+[-][\d]+[-][\d]+)',
            r'([\d]+)\s*[-]\s*([\d]+)\s*[-]\s*([\d]+)\s*(?:Credits?|Hours?)?',
            # Table format: L  T  P  Total
            r'L\s+T\s+P\s+Total\s*\n?\s*([\d]+)\s+([\d]+)\s+([\d]+)',
            # Credits as single number
            r'(?:Credits?|Credit\s*Hours?)[:\s]+(\d+)\s*$',
            # Pattern for "3:1:0" or "3 : 1 : 0"
            r'(\d+)\s*:\s*(\d+)\s*:\s*(\d+)',
            # Teaching Hours format
            r'(?:Teaching\s*Hours?|Lecture\s*Hours?)[:\s]*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                if len(match.groups()) == 3:
                    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                elif len(match.groups()) == 1:
                    # Single credit value - assume it's lecture only
                    credit = match.group(1)
                    if '-' in credit:
                        return credit
                    return f"{credit}-0-0"
        
        # Fallback: Look for any X-X-X pattern in first 500 chars
        ltp_match = re.search(r'\b(\d)\s*[-:]\s*(\d)\s*[-:]\s*(\d)\b', text[:500])
        if ltp_match:
            return f"{ltp_match.group(1)}-{ltp_match.group(2)}-{ltp_match.group(3)}"
                
        return "3-0-0"  # Default to typical lecture course
        
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
        """Extract course outcomes with Bloom's classification.

        Tolerant to OCR output where the table has been flattened: numbers
        on one line, statements on the next, with extra whitespace.
        """
        outcomes: List[Dict[str, str]] = []

        # First, locate the Course Outcomes section (OCR may have split the
        # header phrase across lines or capitalised it oddly).
        co_section_patterns = [
            r'(?:Course\s*Outcomes?|Course\s*Outcome|COs?)\s*[:\-\n]\s*(.+?)(?=\n\s*(?:Mapping|CO[\-\s]?PO|Unit|Course\s*Content|Reference|Text\s*Books?|$))',
            r'\bCO\s+Statement[s]?\s*[:\-\n]\s*(.+?)(?=\n\s*Mapping|$)',
        ]
        co_text = ""
        for pat in co_section_patterns:
            m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
            if m:
                co_text = m.group(1)
                break
        if not co_text:
            # Fall back to scanning the whole syllabus text
            co_text = text

        # ---- 1. Single-line numbered outcomes: "1 Analyze worst-case..." -----
        numbered_pattern = (
            r'^\s*(\d{1,2})[.\)]\s*([A-Z][^\n]+?)(?=\n\s*\d{1,2}[.\)]\s*[A-Z]|\n\s*Mapping|$)'
        )
        matches = list(re.finditer(numbered_pattern, co_text, re.MULTILINE | re.DOTALL))
        for match in matches:
            num = match.group(1)
            description = match.group(2).strip()
            if not self._is_valid_outcome_text(description):
                continue
            outcomes.append(self._make_outcome(f'CO{num}', description))

        # ---- 2. Flattened-table: "CO No. | 1 | 2 | 3 | Statement | first | second" ----
        if not outcomes:
            statement_match = re.search(
                r'(?:Statement[s]?|Statements)\s*[:\-\n]\s*(.+?)(?=\n\s*Mapping|$)',
                co_text,
                re.DOTALL | re.IGNORECASE,
            )
            if statement_match:
                statement_text = statement_match.group(1)
                co_num = 1
                current_outcome = ""
                for line in statement_text.split('\n'):
                    line = line.strip()
                    if not line or len(line) < 10:
                        continue
                    # skip table headers / pure numbers
                    if re.match(r'^(CO\s*No|PO|PSO|BTL|\d+\s*$)', line, re.IGNORECASE):
                        continue
                    if re.match(r'^[\d\s,.\-]+$', line):
                        continue
                    # OCR often drops the period: "1 Describe ..." or "1) Describe..."
                    m_num = re.match(r'^(\d{1,2})[.\)]?\s+(.+)$', line)
                    if m_num and self._is_valid_outcome_text(m_num.group(2)):
                        # Save previous outcome first
                        if current_outcome:
                            outcomes.append(self._make_outcome(f'CO{co_num}', current_outcome))
                            co_num += 1
                        current_outcome = m_num.group(2)
                        continue
                    if re.match(r'^[A-Z]', line) or current_outcome == "":
                        if current_outcome:
                            outcomes.append(self._make_outcome(f'CO{co_num}', current_outcome))
                            co_num += 1
                        current_outcome = line
                    else:
                        current_outcome += " " + line
                if current_outcome and self._is_valid_outcome_text(current_outcome):
                    outcomes.append(self._make_outcome(f'CO{co_num}', current_outcome))

        # ---- 3. Generic "CO1:" / "CO 1:" / "CO1 " labelled outcomes ----
        # The colon, dash or period is OPTIONAL because OCR often drops it
        # after a label like "CO1" followed directly by the statement.
        if not outcomes:
            pattern = (
                r'\b(CO\s*\d{1,2})\s*[:\-\.]?\s+([A-Z][^\n]+?)'
                r'(?=\s*\bCO\s*\d{1,2}\b|\n\s*Mapping|$)'
            )
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                co_code_raw = re.sub(r'\s+', '', match.group(1)).upper()
                co_code = "CO" + re.sub(r'^CO', '', co_code_raw)
                co_desc = match.group(2).strip()
                if not self._is_valid_outcome_text(co_desc):
                    continue
                outcomes.append(self._make_outcome(co_code, co_desc))

        return outcomes

    def _is_valid_outcome_text(self, text: str) -> bool:
        """Skip artifacts: pure-number mapping rows, short headers, table noise."""
        if not text or len(text.strip()) < 20:
            return False
        if re.match(r'^[\d\s,.\-]+$', text):
            return False
        if re.match(r'^(PO|PSO|BTL|CO\s*No|Mapping|Statement)', text.strip(), re.IGNORECASE):
            return False
        return True

    def _make_outcome(self, code: str, description: str) -> Dict[str, str]:
        """Return a normalised outcome dict, deduplicating trivially short ones."""
        description = re.sub(r'\s+', ' ', description).strip().rstrip(',;:')
        return {
            'code': code,
            'description': description,
            'bloom_level': self.text_processor.classify_bloom_level(description),
        }
        
    def _extract_units(self, text: str) -> List[Dict[str, Any]]:
        """Extract unit-wise syllabus.

        Tries several OCR-tolerant patterns in order of strictness:
          1. Single-line: ``Unit No 1 Title 8 Hours``
          2. Roman-numeral: ``Unit No I Title 8 Hours``
          3. Flattened-table: ``Unit No\n4\nTitle\nHours\n8`` (typical OCR output)
          4. Single-line with roman or arabic numeral & optional colon: ``Unit 1: Title``
        Returns dicts with ``unit_number``, ``title``, ``topics``, ``hours``.
        """
        units: List[Dict[str, Any]] = []

        # --- Patterns ordered from most-specific to least-specific ---
        # Capture groups: 1=unit_number, 2=title, 3=hours (when present)
        patterns = [
            # All-on-one line with arabic numeral and "Hours" suffix
            r'\bUnit\s*No\.?\s*(\d{1,2})\s*[:\-]?\s*(.+?)\s+(\d{1,2})\s*(?:H(?:ou)?rs?|Hrs?)\b',
            # Same with roman numeral (I-X)
            r'\bUnit\s*No\.?\s*([IVX]{1,4})\s*[:\-]?\s*(.+?)\s+(\d{1,2})\s*(?:H(?:ou)?rs?|Hrs?)\b',
            # OCR-flattened table: Unit No header, then number on its own
            # line, then title, then "Hours N". The header can have any case
            # because OCR flips case arbitrarily; we accept UNIT/Unit/UnIt,
            # the trailing "No." with or without the period, and either
            # arabic or roman numerals.
            (
                r'\b(?:U\s*N\s*I\s*T|UN?IT)\s*No?\.?\s*\n\s*'
                r'(\d{1,2}|[IVX]{1,4})\s*\n\s*'
                r'([A-Z][^\n]*?)\s*\n\s*'
                r'H(?:ou)?rs?\.?\s*(\d{1,2})'
            ),
            # All-on-one-line variant: "Unit No 4" then title and Hours come within ~120 chars
            r'\bUnit\s*No\.?\s*(\d{1,2})\s+([A-Za-z][A-Za-z0-9 &,/\-\(\)]+?)\s+H(?:ou)?rs?\.?\s*(\d{1,2})',
            # Pattern for the heading-only case: helps locate unit boundaries
            # even when title and hours don't appear nearby (handled in scanner below)
            r'\bUnit\s*No\.?\s*(\d{1,2})\s*[:\.\n]',
        ]

        section_end_re = re.compile(
            r'\n(?:Text\s*Books?|References?|Bibliograph|Assessment|Textbook| Suggested Reading)',
            re.IGNORECASE,
        )

        # ---------- Strict matched loop -----------------------------------------
        found_any = False
        # Only the first 4 patterns have full title+hours capture groups; the
        # 5th is just a heading boundary used by the fallback scanner.
        for pat in patterns[:4]:
            matches = list(re.finditer(pat, text, re.IGNORECASE | re.DOTALL))
            if not matches:
                continue
            found_any = True
            for i, m in enumerate(matches):
                unit_num_raw = m.group(1).strip()
                # Convert roman numerals to arabic for consistency
                unit_num_int = roman_to_int(unit_num_raw) or unit_num_raw
                title = m.group(2).strip().rstrip(',;.')
                hours_str = m.group(3) if m.lastindex and m.lastindex >= 3 else ""
                try:
                    hours = int(hours_str) if hours_str else 0
                except (TypeError, ValueError):
                    hours = 0

                # Determine content slice until next unit heading or next section
                start = m.end()
                if i + 1 < len(matches):
                    end = matches[i + 1].start()
                else:
                    nxt = section_end_re.search(text, start)
                    end = nxt.start() if nxt else len(text)

                topics = self._collect_unit_topics(text[start:end])
                units.append({
                    "unit_number": unit_num_int,
                    "title": title,
                    "topics": topics,
                    "hours": hours,
                })
            break  # use the first pattern that yielded matches

        # ---------- Fallback: scan for heading boundaries and pair nearby fields --
        if not found_any:
            # Find any "Unit No" or "Unit" header line and pair later content
            heading_re = re.compile(
                r'^\s*Unit\s*No\.?\s*(\d{1,2}|[IVX]{1,4})\s*[:\.\n]?',
                re.IGNORECASE | re.MULTILINE,
            )
            headings = list(heading_re.finditer(text))
            if headings:
                for i, m in enumerate(headings):
                    unit_num_raw = m.group(1).strip()
                    unit_num_int = roman_to_int(unit_num_raw) or unit_num_raw

                    # Look ahead ~600 chars for the title and hours
                    window_start = m.end()
                    window_end = headings[i + 1].start() if i + 1 < len(headings) else min(len(text), window_start + 1200)
                    window = text[window_start:window_end]

                    title = ""
                    title_match = re.search(
                        r'\n?\s*([A-Z][A-Za-z0-9 &,/\-\(\)]{4,80})\s*(?:\n|Hours|Hrs|H0urs|Howrs)',
                        window,
                    )
                    if title_match:
                        title = title_match.group(1).strip().rstrip(',;.')

                    hours = 0
                    hours_match = re.search(r'(?:Hours|Hrs|H0urs|Howrs|HOurs)\s*\.?\s*(\d{1,2})', window, re.IGNORECASE)
                    if hours_match:
                        try:
                            hours = int(hours_match.group(1))
                        except ValueError:
                            hours = 0

                    if not title:
                        continue
                    topics = self._collect_unit_topics(window)
                    units.append({
                        "unit_number": unit_num_int,
                        "title": title,
                        "topics": topics,
                        "hours": hours,
                    })

        return units

    @staticmethod
    def _collect_unit_topics(blob: str) -> List[str]:
        """Pull individual topic lines from a unit content block.

        Skips noise: page headers, BTL/CO references, mapping tables, all-digit lines.
        OCR output often pushes a single sentence onto multiple lines, so we
        also re-merge broken short lines that look like sentence fragments.
        """
        if not blob:
            return []
        lines = [ln.strip() for ln in blob.splitlines() if ln.strip()]
        topics: List[str] = []
        skip_prefixes = re.compile(
            r'^(Unit|UN[I1]T|CO\d+|BTL|M\.Sc|BTECH|B\.Tech|Vishwakarma|'
            r'Hours|Hrs?|H0urs|Howrs|Pattern|Department|University|'
            r'Semester|Course\s*Type|Credit|L-T-P|L\s+T\s+P|Programme)',
            re.IGNORECASE,
        )
        for line in lines:
            if len(line) <= 3:
                continue
            if re.match(r'^[\d\s,.\-]+$', line):  # only digits/punct
                continue
            if skip_prefixes.match(line):
                continue
            # Merge short fragment into previous topic (handles OCR line-breaks)
            if (
                topics
                and len(line) < 50
                and not line.endswith(('.', '!', '?', ':'))
                and not re.match(r'^[A-Z\d]', line)
            ):
                topics[-1] = topics[-1] + " " + line
                continue
            topics.append(line)
            if len(topics) >= 12:
                break
        return topics
        
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
        import re
        
        # Find the references section
        section_pattern = r'(?:Reference\s*Books?|References?|Text\s*Books?|Bibliography)[:\s]*(.+?)(?=\n\n[A-Z]|\nCourse\s*Outcome|\nMapping|\nUnit\s*No|\nAssessment|$)'
        match = re.search(section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if not match:
            return []
        
        ref_text = match.group(1).strip()
        references = []
        
        # Check if text has inline numbered items (1. ... 2. ... 3. ...)
        inline_pattern = r'(\d+)\.\s+'
        inline_matches = list(re.finditer(inline_pattern, ref_text))
        
        # Count how many inline number patterns we have
        if len(inline_matches) >= 2:
            # Multiple numbered items found - extract between them
            for idx, match_item in enumerate(inline_matches):
                start = match_item.end()
                if idx + 1 < len(inline_matches):
                    end = inline_matches[idx + 1].start()
                else:
                    end = len(ref_text)
                
                ref_clean = ref_text[start:end].strip()
                ref_clean = re.sub(r'\s+', ' ', ref_clean)
                if ref_clean and len(ref_clean) > 10:
                    references.append(ref_clean)
        
        # If inline method found items, we're done
        if references:
            return references
        
        # Method 2: Try newline-separated numbered items (1. Book\n2. Book)
        numbered_pattern = r'(?:^|\n)\s*(\d+)[.\)]\s*(.+?)(?=\n\s*\d+[.\)]|$)'
        numbered_matches = re.findall(numbered_pattern, ref_text, re.DOTALL)
        
        if len(numbered_matches) >= 2:
            for num, ref in numbered_matches:
                ref_clean = ref.strip().replace('\n', ' ')
                ref_clean = re.sub(r'\s+', ' ', ref_clean)
                if ref_clean and len(ref_clean) > 10:
                    references.append(ref_clean)
        
        if references:
            return references
        
        # Method 3: Try bulleted items
        bullet_pattern = r'[•\*]\s*(.+?)(?=[•\*]|\n|$)'
        bullet_matches = re.findall(bullet_pattern, ref_text, re.DOTALL)
        for ref in bullet_matches:
            ref_clean = ref.strip().replace('\n', ' ')
            ref_clean = re.sub(r'\s+', ' ', ref_clean)
            if ref_clean and len(ref_clean) > 10:
                references.append(ref_clean)
        
        if references:
            return references
        
        # Method 4: Single reference - just return the whole text if it looks like a reference
        if len(ref_text) > 20 and not re.match(r'^[\d\s,.-]+$', ref_text):
            return [re.sub(r'\s+', ' ', ref_text.strip())]
        
        return references
        
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
