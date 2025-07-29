"""
Content Classifier Agent for txtIntelligentReader

This agent specializes in document analysis and text segment classification,
identifying meaningful content vs noise, headers, and formatting artifacts.
"""

from crewai import Agent
from crewai.tools import BaseTool
from typing import List, Dict, Any


class ContentClassifierAgent:
    """
    Agent specialized in classifying text segments with high precision for medical content.
    
    Role: Experienced Document Analyst
    Goal: Classify text segments with high precision for medical content
    Backstory: You have reviewed thousands of medical documents and can quickly 
               identify meaningful content vs noise, headers, and formatting artifacts.
    """
    
    def __init__(self, llm):
        """Initialize the Content Classifier Agent with LLM."""
        self.agent = Agent(
            role="Experienced Document Analyst",
            goal="Classify text segments with high precision for medical content",
            backstory="You have reviewed thousands of medical documents and can quickly identify meaningful content vs noise, headers, and formatting artifacts.",
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
    
    def classify_segments(self, text_segments: List[str]) -> List[Dict[str, Any]]:
        """
        Classify text segments into categories.
        
        Args:
            text_segments: List of text segments to classify
            
        Returns:
            List of classification results with confidence scores
        """
        results = []
        for segment in text_segments:
            classification = self._classify_single_segment(segment)
            results.append(classification)
        return results
    
    def is_meaningful_content(self, text: str) -> bool:
        """
        Determine if text segment contains meaningful content.
        
        Args:
            text: Text segment to analyze
            
        Returns:
            Boolean indicating if content is meaningful
        """
        # Quick checks for obvious non-content
        if self._is_noise_pattern(text):
            return False
        
        if self._is_pdf_artifact(text):
            return False
        
        if self._is_header_footer(text):
            return False
        
        # Check for meaningful content indicators
        return self._has_meaningful_structure(text)
    
    def get_classification_confidence(self, text: str) -> float:
        """
        Get confidence score for classification.
        
        Args:
            text: Text segment to analyze
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence_factors = []
        
        # Length factor (optimal length gets higher score)
        length_score = self._calculate_length_score(text)
        confidence_factors.append(length_score)
        
        # Structure factor (complete sentences get higher score)
        structure_score = self._calculate_structure_score(text)
        confidence_factors.append(structure_score)
        
        # Content factor (meaningful words get higher score)
        content_score = self._calculate_content_score(text)
        confidence_factors.append(content_score)
        
        # Grammar factor (proper grammar gets higher score)
        grammar_score = self._calculate_grammar_score(text)
        confidence_factors.append(grammar_score)
        
        # Return weighted average
        return sum(confidence_factors) / len(confidence_factors)
    
    def _classify_single_segment(self, text: str) -> Dict[str, Any]:
        """
        Classify a single text segment.
        
        Args:
            text: Text segment to classify
            
        Returns:
            Classification result with metadata
        """
        # Determine category
        category = self._determine_category(text)
        
        # Calculate confidence
        confidence = self.get_classification_confidence(text)
        
        # Check if meaningful
        is_meaningful = self.is_meaningful_content(text)
        
        # Detect artifacts
        has_artifacts = self._is_pdf_artifact(text)
        
        return {
            'text': text,
            'category': category,
            'confidence': confidence,
            'is_meaningful': is_meaningful,
            'has_artifacts': has_artifacts,
            'length': len(text),
            'word_count': len(text.split()),
            'classification_metadata': {
                'noise_detected': self._is_noise_pattern(text),
                'header_footer': self._is_header_footer(text),
                'complete_sentence': self._is_complete_sentence(text),
                'has_medical_indicators': self._has_medical_indicators(text)
            }
        }
    
    def _determine_category(self, text: str) -> str:
        """
        Determine the category of text segment.
        
        Args:
            text: Text to categorize
            
        Returns:
            Category string
        """
        text_lower = text.lower().strip()
        
        # Check for different categories
        if self._is_noise_pattern(text):
            return 'noise'
        elif self._is_header_footer(text):
            return 'header_footer'
        elif self._is_table_content(text):
            return 'table'
        elif self._is_list_item(text):
            return 'list_item'
        elif self._has_medical_indicators(text):
            return 'medical_content'
        elif self._is_complete_sentence(text):
            return 'sentence'
        elif len(text.split()) < 3:
            return 'fragment'
        else:
            return 'general_content'
    
    def _is_noise_pattern(self, text: str) -> bool:
        """
        Check if text matches common noise patterns.
        
        Args:
            text: Text to check
            
        Returns:
            True if noise pattern detected
        """
        import re
        
        text_stripped = text.strip()
        
        # Empty or very short
        if len(text_stripped) < 3:
            return True
        
        # Only numbers
        if re.match(r'^\d+$', text_stripped):
            return True
        
        # Only punctuation
        if re.match(r'^[^a-zA-Z0-9]+$', text_stripped):
            return True
        
        # Roman numerals
        if re.match(r'^[ivxlcdmIVXLCDM]+$', text_stripped):
            return True
        
        # Page references
        if re.match(r'^(page|Page)\s*\d+', text_stripped):
            return True
        
        return False
    
    def _is_pdf_artifact(self, text: str) -> bool:
        """
        Check for common PDF extraction artifacts.
        
        Args:
            text: Text to check
            
        Returns:
            True if PDF artifacts detected
        """
        # Common PDF artifacts
        artifacts = [
            '\x0c',  # Form feed
            '\ufeff',  # BOM
            '\u00a0',  # Non-breaking space
        ]
        
        for artifact in artifacts:
            if artifact in text:
                return True
        
        # Broken words (common in PDF extraction)
        words = text.split()
        broken_word_count = 0
        for word in words:
            if len(word) == 1 and word.isalpha():
                broken_word_count += 1
        
        # If more than 30% are single letters, likely broken
        if len(words) > 0 and (broken_word_count / len(words)) > 0.3:
            return True
        
        return False
    
    def _is_header_footer(self, text: str) -> bool:
        """
        Check if text looks like header or footer.
        
        Args:
            text: Text to check
            
        Returns:
            True if header/footer detected
        """
        text_lower = text.lower().strip()
        
        # Common header/footer indicators
        indicators = [
            'page', 'chapter', 'section', 'figure', 'table',
            'copyright', '©', 'all rights reserved', 'confidential',
            'draft', 'version', 'revision', 'date:', 'author:'
        ]
        
        # Short text with indicators
        if len(text.strip()) < 50:
            for indicator in indicators:
                if indicator in text_lower:
                    return True
        
        return False
    
    def _is_table_content(self, text: str) -> bool:
        """
        Check if text appears to be table content.
        
        Args:
            text: Text to check
            
        Returns:
            True if table content detected
        """
        # Look for table-like patterns
        if '\t' in text:  # Tab characters
            return True
        
        # Multiple numbers separated by spaces
        import re
        if re.search(r'\d+\s+\d+\s+\d+', text):
            return True
        
        # Pipe characters (markdown tables)
        if text.count('|') >= 2:
            return True
        
        return False
    
    def _is_list_item(self, text: str) -> bool:
        """
        Check if text is a list item.
        
        Args:
            text: Text to check
            
        Returns:
            True if list item detected
        """
        import re
        
        text_stripped = text.strip()
        
        # Bullet points
        if re.match(r'^[•·▪▫-]\s+', text_stripped):
            return True
        
        # Numbered lists
        if re.match(r'^\d+[.)\s]', text_stripped):
            return True
        
        # Lettered lists
        if re.match(r'^[a-zA-Z][.)\s]', text_stripped):
            return True
        
        return False
    
    def _has_medical_indicators(self, text: str) -> bool:
        """
        Check for basic medical terminology indicators.
        
        Args:
            text: Text to check
            
        Returns:
            True if medical indicators found
        """
        text_lower = text.lower()
        
        # Basic medical terms
        medical_terms = [
            'patient', 'treatment', 'diagnosis', 'symptoms', 'therapy',
            'medication', 'clinical', 'hospital', 'doctor', 'nurse',
            'disease', 'infection', 'surgery', 'medical', 'health'
        ]
        
        for term in medical_terms:
            if term in text_lower:
                return True
        
        return False
    
    def _is_complete_sentence(self, text: str) -> bool:
        """
        Check if text forms a complete sentence.
        
        Args:
            text: Text to check
            
        Returns:
            True if complete sentence
        """
        text_stripped = text.strip()
        
        # Must have reasonable length
        if len(text_stripped) < 10:
            return False
        
        # Must end with sentence-ending punctuation
        if not text_stripped.endswith(('.', '!', '?')):
            return False
        
        # Must have at least one verb (basic check)
        words = text_stripped.lower().split()
        common_verbs = [
            'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'can', 'may', 'might'
        ]
        
        for verb in common_verbs:
            if verb in words:
                return True
        
        return False
    
    def _has_meaningful_structure(self, text: str) -> bool:
        """
        Check if text has meaningful structure.
        
        Args:
            text: Text to check
            
        Returns:
            True if meaningful structure detected
        """
        words = text.split()
        
        # Must have minimum word count
        if len(words) < 3:
            return False
        
        # Must have reasonable word lengths
        avg_word_length = sum(len(word) for word in words) / len(words)
        if avg_word_length < 2:
            return False
        
        # Must have some alphabetic content
        alpha_chars = sum(1 for char in text if char.isalpha())
        if alpha_chars < len(text) * 0.5:
            return False
        
        return True
    
    def _calculate_length_score(self, text: str) -> float:
        """
        Calculate score based on text length.
        
        Args:
            text: Text to score
            
        Returns:
            Length score between 0.0 and 1.0
        """
        length = len(text.strip())
        
        # Optimal length range: 50-300 characters
        if 50 <= length <= 300:
            return 1.0
        elif 20 <= length < 50:
            return 0.7
        elif 300 < length <= 500:
            return 0.8
        elif 10 <= length < 20:
            return 0.4
        elif length > 500:
            return 0.6
        else:
            return 0.1
    
    def _calculate_structure_score(self, text: str) -> float:
        """
        Calculate score based on text structure.
        
        Args:
            text: Text to score
            
        Returns:
            Structure score between 0.0 and 1.0
        """
        score = 0.0
        
        # Complete sentence bonus
        if self._is_complete_sentence(text):
            score += 0.4
        
        # Proper capitalization
        if text.strip() and text.strip()[0].isupper():
            score += 0.2
        
        # Ends with punctuation
        if text.strip().endswith(('.', '!', '?', ':')):
            score += 0.2
        
        # Has reasonable word count
        word_count = len(text.split())
        if 5 <= word_count <= 50:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_content_score(self, text: str) -> float:
        """
        Calculate score based on content quality.
        
        Args:
            text: Text to score
            
        Returns:
            Content score between 0.0 and 1.0
        """
        score = 0.0
        
        # Has medical indicators
        if self._has_medical_indicators(text):
            score += 0.3
        
        # Not noise
        if not self._is_noise_pattern(text):
            score += 0.3
        
        # Not artifacts
        if not self._is_pdf_artifact(text):
            score += 0.2
        
        # Meaningful structure
        if self._has_meaningful_structure(text):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_grammar_score(self, text: str) -> float:
        """
        Calculate score based on grammar quality.
        
        Args:
            text: Text to score
            
        Returns:
            Grammar score between 0.0 and 1.0
        """
        score = 0.0
        
        # Basic grammar checks
        words = text.split()
        
        # Has reasonable word distribution
        if len(words) > 0:
            avg_word_length = sum(len(word) for word in words) / len(words)
            if 3 <= avg_word_length <= 8:
                score += 0.3
        
        # No excessive punctuation
        punct_ratio = sum(1 for char in text if not char.isalnum() and not char.isspace()) / len(text)
        if punct_ratio < 0.2:
            score += 0.3
        
        # Proper spacing
        if '  ' not in text:  # No double spaces
            score += 0.2
        
        # Starts with capital
        if text.strip() and text.strip()[0].isupper():
            score += 0.2
        
        return min(score, 1.0)
