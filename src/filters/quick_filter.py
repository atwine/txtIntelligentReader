#!/usr/bin/env python3
"""
Quick Filter (Layer 1) for txtIntelligentReader

This filter removes obvious noise and formatting artifacts from text.
"""

import re
from typing import List, Dict, Any, Tuple


class QuickFilter:
    """
    First layer filter that removes obvious noise and formatting artifacts.
    
    This filter handles:
    - PDF extraction artifacts
    - Headers, footers, and page numbers
    - Table of contents entries
    - Standalone numbers and formatting
    - Obvious non-content text
    """
    
    def __init__(self):
        """Initialize the QuickFilter with noise patterns."""
        self.noise_patterns = self._compile_noise_patterns()
        self.pdf_artifact_patterns = self._compile_pdf_artifact_patterns()
        self.header_footer_patterns = self._compile_header_footer_patterns()
        self.formatting_patterns = self._compile_formatting_patterns()
        
        # Statistics tracking
        self.stats = {
            'total_processed': 0,
            'noise_removed': 0,
            'pdf_artifacts_removed': 0,
            'headers_footers_removed': 0,
            'formatting_removed': 0
        }
    
    def filter_text(self, sentences: List[str]) -> List[str]:
        """
        Filter out noise from a list of sentences.
        
        Args:
            sentences: List of sentences to filter
            
        Returns:
            Filtered list of sentences with noise removed
        """
        if not sentences:
            return []
        
        filtered = []
        self.stats['total_processed'] = len(sentences)
        
        for sentence in sentences:
            if sentence and isinstance(sentence, str):
                cleaned_sentence = sentence.strip()
                if cleaned_sentence and not self._is_noise(cleaned_sentence):
                    filtered.append(cleaned_sentence)
                else:
                    self.stats['noise_removed'] += 1
        
        return filtered
    
    def _is_noise(self, sentence: str) -> bool:
        """
        Check if a sentence is noise that should be filtered out.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if sentence is noise, False otherwise
        """
        # Check minimum length
        if len(sentence.strip()) < 3:
            return True
        
        # Check for PDF artifacts
        if self._is_pdf_artifact(sentence):
            self.stats['pdf_artifacts_removed'] += 1
            return True
        
        # Check for headers/footers
        if self._is_header_footer(sentence):
            self.stats['headers_footers_removed'] += 1
            return True
        
        # Check for formatting artifacts
        if self._is_formatting_artifact(sentence):
            self.stats['formatting_removed'] += 1
            return True
        
        # Check against general noise patterns
        for pattern in self.noise_patterns:
            if pattern.match(sentence.strip()):
                return True
        
        return False
    
    def _compile_noise_patterns(self) -> List[re.Pattern]:
        """
        Compile regex patterns for general noise detection.
        
        Returns:
            List of compiled regex patterns
        """
        patterns = [
            r'^\d+$',  # Standalone numbers
            r'^[ivxlcdm]+$',  # Roman numerals only
            r'^[ivxlcdm]+\.$',  # Roman numerals with period
            r'^\d+\.$',  # Numbers with period
            r'^\d+\)$',  # Numbers with parenthesis
            r'^[a-z]\)$',  # Single letter with parenthesis
            r'^[A-Z]\.$',  # Single capital letter with period
            r'^\s*$',  # Empty or whitespace only
            r'^\W+$',  # Only punctuation/symbols
            r'^\d+\s*-\s*\d+$',  # Page ranges like "1-5"
            r'^Chapter\s+\d+$',  # Chapter headings
            # Enhanced patterns for medical documents
            r'^\s*\d+\.\d+.*$',  # Section numbers like "3.1 Title"
            r'^\s*[A-Z]\.\d+.*$',  # Section numbers like "A.4 Title"
            r'^\s*\d+\.\d+\.\d+.*$',  # Subsection numbers like "1.2.3 Title"
            r'^\s*\d+\.\d+\s+[A-Z]',  # Section numbers followed by titles
            r'\bFor further reading,?\s+refer to\s+[\d,\s-]+',  # Reference citations
            r'\brefer to\s+[\d,\s-]+',  # Simple references
            r'^[\d,\s-]+\s+SECTION\s+\d+',  # Page numbers before sections
            r'SECTION\s+\d+:\s+[A-Z\s]+$',  # Section headers
            r'^\s*\d+\.\d+\s+\w+',  # Numbered subsections
            r'^\s*[A-Z]\.\d+\.\d+',  # Multi-level section numbers
            r'\b\d{3,}\s+SECTION\b',  # Page numbers before SECTION
            r'^\s*\d+\s+[A-Z][a-z]+\s+[A-Z][a-z]+',  # Page numbers with title words
            r'^Section\s+\d+',  # Section headings
            r'^Part\s+[IVX]+',  # Part headings with roman numerals
        ]
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _compile_pdf_artifact_patterns(self) -> List[re.Pattern]:
        """
        Compile regex patterns for PDF extraction artifacts.
        
        Returns:
            List of compiled regex patterns for PDF artifacts
        """
        patterns = [
            r'^Page\s+\d+',  # Page numbers
            r'^\d+\s+of\s+\d+',  # "1 of 10" style
            r'^\d+/\d+$',  # "1/10" style
            r'^\[\d+\]$',  # Bracketed numbers
            r'^\(\d+\)$',  # Parenthetical numbers
            r'^\d+\s*$',  # Standalone page numbers
            r'^\.{3,}',  # Multiple dots (table of contents)
            r'^-{3,}',  # Multiple dashes
            r'^_{3,}',  # Multiple underscores
            r'^={3,}',  # Multiple equals signs
            r'^\*{3,}',  # Multiple asterisks
            r'^#+',  # Multiple hash symbols
            r'^\s*\|.*\|\s*$',  # Table borders
            r'^\+[-+\s]+\+$',  # ASCII table borders
        ]
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _compile_header_footer_patterns(self) -> List[re.Pattern]:
        """
        Compile regex patterns for headers and footers.
        
        Returns:
            List of compiled regex patterns for headers/footers
        """
        patterns = [
            r'^LIST OF',  # Table of contents
            r'^TABLE OF CONTENTS',
            r'^CONTENTS$',
            r'^INDEX$',
            r'^REFERENCES$',
            r'^BIBLIOGRAPHY$',
            r'^APPENDIX',
            r'^FOREWORD$',
            r'^PREFACE$',
            r'^INTRODUCTION$',
            r'^ABSTRACT$',
            r'^SUMMARY$',
            r'^ACKNOWLEDGMENT',
            r'^COPYRIGHT',
            r'^\(C\)\s*\d{4}',  # Copyright notices
            r'^©\s*\d{4}',  # Copyright symbol
            r'^All rights reserved',
            r'^Printed in',
            r'^Published by',
            r'^ISBN',
            r'^DOI:',
            r'^www\.',  # Web addresses
            r'^https?://',  # URLs
            r'^[A-Z\s]{10,}$',  # Long uppercase strings (likely headers)
        ]
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _compile_formatting_patterns(self) -> List[re.Pattern]:
        """
        Compile regex patterns for formatting artifacts.
        
        Returns:
            List of compiled regex patterns for formatting
        """
        patterns = [
            r'^\s*[\*\-\+]\s*$',  # Bullet points alone
            r'^\s*[\*\-\+]\s+$',  # Bullet points with space
            r'^\s*•\s*$',  # Unicode bullet points
            r'^\s*→\s*$',  # Arrow symbols
            r'^\s*►\s*$',  # Triangle symbols
            r'^\s*\d+\.\s*$',  # Numbered list markers alone
            r'^\s*[a-z]\)\s*$',  # Letter list markers
            r'^\s*\([a-z]\)\s*$',  # Parenthetical letter markers
            r'^\s*\[[\*\-\+x]\]\s*$',  # Checkbox markers
            r'^\s*☐\s*$',  # Unicode checkboxes
            r'^\s*☑\s*$',  # Checked boxes
            r'^\s*✓\s*$',  # Check marks
            r'^\s*✗\s*$',  # X marks
        ]    
        
        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def _is_pdf_artifact(self, sentence: str) -> bool:
        """
        Check if sentence is a PDF extraction artifact.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if sentence is a PDF artifact
        """
        for pattern in self.pdf_artifact_patterns:
            if pattern.match(sentence.strip()):
                return True
        
        # Additional PDF artifact checks
        stripped = sentence.strip()
        
        # Check for OCR errors (random single characters)
        if len(stripped) == 1 and not stripped.isalnum():
            return True
        
        # Check for broken words (common in PDF extraction)
        if len(stripped.split()) == 1 and len(stripped) < 3:
            return True
        
        # Check for excessive spacing artifacts
        if '  ' in sentence and len(sentence.replace(' ', '')) < 5:
            return True
        
        return False
    
    def _is_header_footer(self, sentence: str) -> bool:
        """
        Check if sentence is a header or footer.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if sentence is a header/footer
        """
        for pattern in self.header_footer_patterns:
            if pattern.match(sentence.strip()):
                return True
        
        # Additional header/footer checks
        stripped = sentence.strip()
        
        # Check for date patterns (common in headers/footers)
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}-\d{1,2}-\d{2,4}',
            r'\w+\s+\d{1,2},?\s+\d{4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, stripped):
                return True
        
        return False
    
    def _is_formatting_artifact(self, sentence: str) -> bool:
        """
        Check if sentence is a formatting artifact.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if sentence is a formatting artifact
        """
        for pattern in self.formatting_patterns:
            if pattern.match(sentence.strip()):
                return True
        
        return False
    
    def get_filtering_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the filtering process.
        
        Returns:
            Dictionary containing filtering statistics
        """
        total_removed = (
            self.stats['noise_removed'] + 
            self.stats['pdf_artifacts_removed'] + 
            self.stats['headers_footers_removed'] + 
            self.stats['formatting_removed']
        )
        
        return {
            'total_processed': self.stats['total_processed'],
            'total_removed': total_removed,
            'total_kept': self.stats['total_processed'] - total_removed,
            'removal_rate': total_removed / self.stats['total_processed'] if self.stats['total_processed'] > 0 else 0,
            'breakdown': {
                'noise_removed': self.stats['noise_removed'],
                'pdf_artifacts_removed': self.stats['pdf_artifacts_removed'],
                'headers_footers_removed': self.stats['headers_footers_removed'],
                'formatting_removed': self.stats['formatting_removed']
            }
        }
    
    def reset_stats(self):
        """Reset filtering statistics."""
        self.stats = {
            'total_processed': 0,
            'noise_removed': 0,
            'pdf_artifacts_removed': 0,
            'headers_footers_removed': 0,
            'formatting_removed': 0
        }
