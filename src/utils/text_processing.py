"""Text processing utilities for SCDO"""

import re
import unicodedata
from typing import List, Dict, Set, Optional
import yaml
from pathlib import Path


# Common OCR misreads observed in syllabus PDFs (scanned)
# Map each misread token to the canonical replacement.
OCR_CHAR_FIXES = {
    # Common character-level confusions
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote
    "\u201c": '"',  # left double quote
    "\u201d": '"',  # right double quote
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u00a0": " ",  # non-breaking space
    "\ufeff": "",   # BOM
}

# OCR word-level fixes specific to Indian university syllabi.
# Each rule ONLY fires when the pattern actually indicates OCR noise. We do
# NOT add punctuation that wasn't there in the original document, because
# adding fictitious punctuation silently breaks native PDFs that already use
# the same headings.
OCR_WORD_FIXES = [
    # Hours / Hrs variants commonly OCR'd from scans. We require the misread
    # substring to be present; legitimate "Hours" text is never touched.
    (r"\bHowrs?\b", "Hours"),
    (r"\bH0u?rs\b", "Hours"),
    (r"\bHou?rs\b(?=\s+\d)", "Hours"),
    (r"\bHRS\.?\b(?=\s+\d)", "Hours"),
    # UNIT heading with digit-letter confusion: "UN1T" etc., and "UNITS"
    # misread from scans. We do NOT alter plain "Unit No" because native
    # PDFs already spell it correctly.
    (r"\bUN[I1]T\s+NO[S5]?\b",
     lambda m: "UNIT NO" + ("S" if m.group(0).rstrip().endswith(("NOS", "NO5")) else "")),
    # "BTL" -> "Level" only when a Bloom's-tagging context follows (a CO
    # number or "Mapping" within ~40 chars), so it doesn't fire on legitimate
    # non-OCR documents that just happen to mention BTL.
    (r"\bBTL\b(?=[^\n]{0,40}(?:Mapping|CO\s*\d))", "Level"),
]

# Roman numerals commonly used for unit numbers
ROMAN_NUMERALS = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}


def normalize_ocr_text(text: str, aggressive: bool = False) -> str:
    """
    Clean up text extracted from OCR or noisy PDF sources.

    Fixes typical Tesseract/EasyOCR misreads of common syllabus terms.
    Conservative by default; pass aggressive=True to also collapse OCR
    noise like stray punctuation or repeated letters in a row.

    Args:
        text: Raw text from pdfplumber/pymupdf/Tesseract/EasyOCR
        aggressive: If True, apply extra noise reduction steps

    Returns:
        Cleaned text with common OCR errors corrected
    """
    if not text:
        return ""

    # 1. Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # 2. Replace special whitespace/quotes
    for bad, good in OCR_CHAR_FIXES.items():
        text = text.replace(bad, good)

    # 3. Word-level common misreads. We pass replacement through re.sub as a
    # function when needed so that lambdas are invoked with the Match object.
    for pattern, replacement in OCR_WORD_FIXES:
        if callable(replacement):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        else:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # 4. Trim whitespace on each line and collapse blank lines
    lines = [ln.rstrip() for ln in text.splitlines()]
    cleaned_lines = []
    blank_streak = 0
    for line in lines:
        # collapse runs of internal whitespace
        line = re.sub(r"[ \t]+", " ", line).strip()
        if not line:
            blank_streak += 1
            if blank_streak <= 1:
                cleaned_lines.append("")
            continue
        blank_streak = 0
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    if aggressive:
        # Aggressive: condense multi-line sentences produced by column wrapping in OCR.
        # Join a wrapped line to its predecessor if the line doesn't look like a sentence
        # start (no capital, no digit, no bullet) and the previous line didn't end with .!?:;
        merged = []
        for line in text.split("\n"):
            if merged and line and re.match(r"^[a-z][a-z\-]+", line):
                prev = merged[-1]
                if prev and not re.search(r"[.!?:;]\s*$", prev) and len(prev) > 0:
                    merged[-1] = prev + " " + line
                    continue
            merged.append(line)
        text = "\n".join(merged)

    return text


def roman_to_int(token: str) -> Optional[int]:
    """Convert a roman-numeral token (I, II, III, ...) to int, or None if not roman."""
    if not token:
        return None
    return ROMAN_NUMERALS.get(token.upper().strip())


class TextProcessor:
    """Utilities for text processing and NLP tasks"""
    
    def __init__(self):
        self.bloom_verbs = self._load_bloom_verbs()
        
    def _load_bloom_verbs(self) -> Dict[str, Set[str]]:
        """Load Bloom's taxonomy verbs from config"""
        config_path = Path(__file__).parent.parent.parent / "configs" / "bloom_taxonomy.yaml"
        
        with open(config_path, 'r') as f:
            taxonomy = yaml.safe_load(f)
            
        verbs = {}
        for level, data in taxonomy['taxonomy'].items():
            verbs[level] = set(v.lower() for v in data['verbs'])
            
        return verbs
        
    def extract_learning_outcomes(self, text: str) -> List[str]:
        """
        Extract learning outcomes from text
        
        Args:
            text: Input text
            
        Returns:
            List of learning outcomes
        """
        # Common patterns for learning outcomes
        patterns = [
            r'(?:CO\d+|Course Outcome \d+)[:\s]+(.+?)(?=CO\d+|Course Outcome|\n\n|$)',
            r'(?:Students will be able to|Upon completion)[:\s]+(.+?)(?=\n\n|$)',
            r'(?:Learning Outcome|Outcome)[:\s]+(.+?)(?=\n\n|$)'
        ]
        
        outcomes = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            outcomes.extend([m.group(1).strip() for m in matches])
            
        return outcomes
        
    def classify_bloom_level(self, text: str) -> str:
        """
        Classify text to Bloom's taxonomy level (highest matching level)
        
        Args:
            text: Text to classify (learning outcome or objective)
            
        Returns:
            Bloom's level (remember, understand, apply, analyze, evaluate, create)
        """
        text_lower = text.lower()
        
        HIGHEST_FIRST = ['create', 'evaluate', 'analyze', 'apply', 'understand', 'remember']
        
        for level in HIGHEST_FIRST:
            verbs = self.bloom_verbs.get(level, set())
            for verb in verbs:
                if re.search(rf'\b{re.escape(verb)}\b', text_lower):
                    return level
                    
        return "unknown"
        
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract keywords from text
        
        Args:
            text: Input text
            top_n: Number of keywords to return
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction (can be enhanced with TF-IDF or other methods)
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                     'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
                     'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Filter and count
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in sorted_words[:top_n]]
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?()\-]', '', text)
        
        return text.strip()
        
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
