"""
Quick Filter (Layer 1) for txtIntelligentReader

Removes obvious noise and formatting artifacts like page numbers, 
roman numerals, headers, and table of contents entries.
"""

import re
from typing import List, Dict, Any


class QuickFilter:
    """
    Layer 1 filter for removing obvious noise and formatting artifacts.
    
    This filter quickly removes:
    - Standalone numbers and page references
    - Roman numerals
    - Table of contents entries
    - Headers and formatting lines
    - Dot and dash lines
    """
    
    def __init__(self):
        """Initialize the Quick Filter with noise patterns."""
        self.noise_patterns = [
            r'^\d+$',  # Standalone numbers
            r'^[ivxlcdm]+$',  # Roman numerals (lowercase)
            r'^[IVXLCDM]+$',  # Roman numerals (uppercase)
            r'^Page \d+',  # Page numbers
            r'^page \d+',  # Page numbers (lowercase)
            r'^\.{3,}',  # Dot lines (3 or more dots)
            r'^-{3,}',  # Dash lines (3 or more dashes)
            r'^_{3,}',  # Underscore lines
            r'^={3,}',  # Equal sign lines
            r'^LIST OF',  # Table of contents
            r'^list of',  # Table of contents (lowercase)
            r'^TABLE OF',  # Table of contents
            r'^table of',  # Table of contents (lowercase)
            r'^CONTENTS',  # Contents header
            r'^contents',  # Contents header (lowercase)
            r'^FOREWORD',  # Foreword header
            r'^foreword',  # Foreword header (lowercase)
            r'^PREFACE',  # Preface header
            r'^preface',  # Preface header (lowercase)
            r'^APPENDIX',  # Appendix markers
            r'^appendix',  # Appendix markers (lowercase)
            r'^BIBLIOGRAPHY',  # Bibliography header
            r'^bibliography',  # Bibliography header (lowercase)
            r'^REFERENCES',  # References header
            r'^references',  # References header (lowercase)
            r'^INDEX',  # Index header
            r'^index',  # Index header (lowercase)
            r'^\s*\d+\.\d+\s*$',  # Section numbers (e.g., "1.1", "2.3")
            r'^\s*Chapter \d+\s*$',  # Chapter headers
            r'^\s*chapter \d+\s*$',  # Chapter headers (lowercase)
            r'^\s*Section \d+\s*$',  # Section headers
            r'^\s*section \d+\s*$',  # Section headers (lowercase)
            r'^\s*\([a-z]\)\s*$',  # Single letter in parentheses
            r'^\s*\([0-9]+\)\s*$',  # Single number in parentheses
            r'^\s*[a-z]\.\s*$',  # Single letter with period
            r'^\s*[A-Z]\.\s*$',  # Single uppercase letter with period
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.noise_patterns]
    
    def filter_text(self, sentences: List[str]) -> List[str]:
        """
        Filter out noise sentences from the input list.
        
        Args:
            sentences: List of sentences to filter
            
        Returns:
            List of sentences with noise removed
        """
        filtered = []
        for sentence in sentences:
            if not self._is_noise(sentence.strip()):
                filtered.append(sentence)
        return filtered
    
    def _is_noise(self, sentence: str) -> bool:
        """
        Check if a sentence matches noise patterns.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if sentence is noise, False otherwise
        """
        # Skip empty or very short sentences
        if len(sentence.strip()) < 3:
            return True
        
        # Check against compiled patterns
        for pattern in self.compiled_patterns:
            if pattern.match(sentence.strip()):
                return True
        
        # Additional heuristic checks
        if self._is_mostly_punctuation(sentence):
            return True
        
        if self._is_page_header_footer(sentence):
            return True
            
        return False
    
    def _is_mostly_punctuation(self, sentence: str) -> bool:
        """
        Check if sentence is mostly punctuation marks.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if mostly punctuation, False otherwise
        """
        if len(sentence.strip()) == 0:
            return True
        
        # Count alphanumeric characters
        alphanumeric_count = sum(1 for char in sentence if char.isalnum())
        total_non_space = len(sentence.replace(' ', ''))
        
        if total_non_space == 0:
            return True
        
        # If less than 30% alphanumeric, consider it mostly punctuation
        return (alphanumeric_count / total_non_space) < 0.3
    
    def _is_page_header_footer(self, sentence: str) -> bool:
        """
        Check if sentence looks like a page header or footer.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if looks like header/footer, False otherwise
        """
        sentence_lower = sentence.lower().strip()
        
        # Common header/footer patterns
        header_footer_indicators = [
            'page',
            'chapter',
            'section',
            'figure',
            'table',
            'appendix',
            'copyright',
            '©',
            'all rights reserved',
            'confidential',
            'draft',
            'version',
            'revision',
            'date:',
            'author:',
            'title:',
        ]
        
        for indicator in header_footer_indicators:
            if indicator in sentence_lower:
                # If it's short and contains these indicators, likely header/footer
                if len(sentence.strip()) < 50:
                    return True
        
        return False
    
    def get_filter_stats(self, original_sentences: List[str], filtered_sentences: List[str]) -> Dict[str, Any]:
        """
        Get statistics about the filtering process.
        
        Args:
            original_sentences: Original list of sentences
            filtered_sentences: Filtered list of sentences
            
        Returns:
            Dictionary with filtering statistics
        """
        original_count = len(original_sentences)
        filtered_count = len(filtered_sentences)
        removed_count = original_count - filtered_count
        
        return {
            'original_count': original_count,
            'filtered_count': filtered_count,
            'removed_count': removed_count,
            'removal_rate': removed_count / original_count if original_count > 0 else 0,
            'filter_name': 'QuickFilter (Layer 1)'
        }
