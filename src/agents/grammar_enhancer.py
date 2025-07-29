"""
Grammar Enhancement Agent for txtIntelligentReader

This agent specializes in text quality improvement and grammar enhancement
for translation-ready output.
"""

from crewai import Agent
from typing import List, Dict, Any


class GrammarEnhancementAgent:
    """
    Agent specialized in transforming sentences into perfect, translation-ready text.
    
    Role: Professional Copy Editor
    Goal: Transform sentences into perfect, translation-ready text
    Backstory: You have edited thousands of medical translations and know how to 
               create grammatically perfect, clear sentences.
    """
    
    def __init__(self, llm):
        """Initialize the Grammar Enhancement Agent with LLM."""
        self.agent = Agent(
            role="Professional Copy Editor",
            goal="Transform sentences into perfect, translation-ready text",
            backstory="You have edited thousands of medical translations and know how to create grammatically perfect, clear sentences.",
            llm=llm,
            verbose=True
        )
    
    def enhance_grammar(self, sentence: str) -> str:
        """
        Enhance grammar and readability of a sentence.
        
        Args:
            sentence: Original sentence to enhance
            
        Returns:
            Enhanced sentence with improved grammar
        """
        if not sentence or not sentence.strip():
            return sentence
        
        # Apply enhancement pipeline
        enhanced = sentence
        
        # Step 1: Fix PDF artifacts
        enhanced = self.fix_pdf_artifacts(enhanced)
        
        # Step 2: Fix punctuation and capitalization
        enhanced = self._fix_punctuation_and_capitalization(enhanced)
        
        # Step 3: Fix spacing issues
        enhanced = self._fix_spacing_issues(enhanced)
        
        # Step 4: Standardize medical terminology
        enhanced = self.standardize_medical_terminology(enhanced)
        
        # Step 5: Ensure complete sentence structure
        enhanced = self.ensure_complete_sentences(enhanced)
        
        # Step 6: Optimize for translation readiness
        enhanced = self._optimize_for_translation(enhanced)
        
        return enhanced.strip()
    
    def fix_pdf_artifacts(self, text: str) -> str:
        """
        Fix common PDF extraction artifacts.
        
        Args:
            text: Text with potential PDF artifacts
            
        Returns:
            Cleaned text with artifacts removed
        """
        if not text:
            return text
        
        import re
        
        # Remove common PDF artifacts
        cleaned = text
        
        # Remove form feeds and other control characters
        cleaned = re.sub(r'[\x0c\ufeff\u00a0]', ' ', cleaned)
        
        # Fix broken words (single letters followed by spaces)
        cleaned = re.sub(r'\b([a-zA-Z])\s+([a-zA-Z])\s+([a-zA-Z])\b', r'\1\2\3', cleaned)
        
        # Fix hyphenated words split across lines
        cleaned = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', cleaned)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Fix common OCR errors in medical text
        ocr_fixes = {
            'patlent': 'patient',
            'medlcal': 'medical',
            'treatrnent': 'treatment',
            'dlagnosis': 'diagnosis',
            'hospltal': 'hospital',
            'medlcine': 'medicine',
            'therapv': 'therapy',
            'svmptom': 'symptom'
        }
        
        for error, correction in ocr_fixes.items():
            cleaned = re.sub(r'\b' + error + r'\b', correction, cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def ensure_complete_sentences(self, text: str) -> str:
        """
        Ensure text forms complete, well-structured sentences.
        
        Args:
            text: Text to process
            
        Returns:
            Text with complete sentence structure
        """
        if not text or not text.strip():
            return text
        
        import re
        
        # Ensure proper sentence ending
        text = text.strip()
        
        # Add period if sentence doesn't end with punctuation
        if text and not text.endswith(('.', '!', '?', ':', ';')):
            # Check if it looks like a complete thought
            if self._is_complete_thought(text):
                text += '.'
        
        # Fix sentence fragments by combining them
        text = self._combine_sentence_fragments(text)
        
        # Ensure proper capitalization at sentence start
        sentences = re.split(r'([.!?]\s*)', text)
        enhanced_sentences = []
        
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part.strip():  # Sentence content (not punctuation)
                part = part.strip()
                if part:
                    # Capitalize first letter
                    part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
                enhanced_sentences.append(part)
            else:
                enhanced_sentences.append(part)
        
        return ''.join(enhanced_sentences)
    
    def standardize_medical_terminology(self, text: str) -> str:
        """
        Standardize medical terminology for consistency.
        
        Args:
            text: Text with medical terms
            
        Returns:
            Text with standardized medical terminology
        """
        if not text:
            return text
        
        import re
        
        # Medical term standardizations
        standardizations = {
            # Common variations to standard forms
            r'\bpatients?\b': lambda m: 'patient' if m.group().lower() == 'patient' else 'patients',
            r'\bdoctors?\b': lambda m: 'physician' if m.group().lower() == 'doctor' else 'physicians',
            r'\bmeds?\b': 'medication',
            r'\bprescription\b': 'prescription',
            r'\bdiagnose\b': 'diagnosis',
            r'\btreatments?\b': lambda m: 'treatment' if m.group().lower() == 'treatment' else 'treatments',
            r'\bhospitals?\b': lambda m: 'hospital' if m.group().lower() == 'hospital' else 'hospitals',
            r'\bclinics?\b': lambda m: 'clinic' if m.group().lower() == 'clinic' else 'clinics',
            r'\btherapies\b': 'therapy',
            r'\bsymptoms?\b': lambda m: 'symptom' if m.group().lower() == 'symptom' else 'symptoms'
        }
        
        standardized = text
        
        for pattern, replacement in standardizations.items():
            if callable(replacement):
                standardized = re.sub(pattern, replacement, standardized, flags=re.IGNORECASE)
            else:
                standardized = re.sub(pattern, replacement, standardized, flags=re.IGNORECASE)
        
        # Standardize medical abbreviations
        abbreviations = {
            r'\bDr\.?\s': 'Dr. ',
            r'\bMD\b': 'MD',
            r'\bRN\b': 'RN',
            r'\bICU\b': 'ICU',
            r'\bER\b': 'emergency room',
            r'\bOR\b': 'operating room',
            r'\bBP\b': 'blood pressure',
            r'\bHR\b': 'heart rate'
        }
        
        for abbrev, expansion in abbreviations.items():
            standardized = re.sub(abbrev, expansion, standardized)
        
        return standardized
    
    def get_enhancement_metrics(self, original: str, enhanced: str) -> Dict[str, Any]:
        """
        Calculate metrics for grammar enhancement quality.
        
        Args:
            original: Original text
            enhanced: Enhanced text
            
        Returns:
            Dictionary with enhancement metrics
        """
        metrics = {
            'original_length': len(original),
            'enhanced_length': len(enhanced),
            'length_change': len(enhanced) - len(original),
            'artifacts_fixed': self._count_artifacts_fixed(original, enhanced),
            'grammar_improvements': self._count_grammar_improvements(original, enhanced),
            'readability_score': self._calculate_readability_score(enhanced),
            'translation_readiness': self._assess_translation_readiness(enhanced)
        }
        
        return metrics
    
    def _fix_punctuation_and_capitalization(self, text: str) -> str:
        """
        Fix punctuation and capitalization issues.
        
        Args:
            text: Text to fix
            
        Returns:
            Text with fixed punctuation and capitalization
        """
        import re
        
        if not text:
            return text
        
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s*([,.!?;:])\s*', r'\1 ', text)
        text = re.sub(r'\s+([,.!?;:])\s*', r'\1 ', text)
        
        # Remove space before punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        
        # Ensure space after punctuation
        text = re.sub(r'([,.!?;:])([a-zA-Z])', r'\1 \2', text)
        
        # Fix capitalization after periods
        text = re.sub(r'(\.\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        # Capitalize first letter of text
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        return text.strip()
    
    def _fix_spacing_issues(self, text: str) -> str:
        """
        Fix spacing issues in text.
        
        Args:
            text: Text to fix
            
        Returns:
            Text with fixed spacing
        """
        import re
        
        if not text:
            return text
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around parentheses
        text = re.sub(r'\s*\(\s*', ' (', text)
        text = re.sub(r'\s*\)\s*', ') ', text)
        
        # Fix spacing around quotes
        text = re.sub(r'\s*"\s*', ' "', text)
        text = re.sub(r'\s*"\s*', '" ', text)
        
        # Remove leading/trailing spaces
        text = text.strip()
        
        return text
    
    def _optimize_for_translation(self, text: str) -> str:
        """
        Optimize text for translation readiness.
        
        Args:
            text: Text to optimize
            
        Returns:
            Translation-ready text
        """
        import re
        
        if not text:
            return text
        
        # Ensure clear sentence boundaries
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
        
        # Expand contractions for clarity
        contractions = {
            r"can't": "cannot",
            r"won't": "will not",
            r"n't": " not",
            r"'re": " are",
            r"'ve": " have",
            r"'ll": " will",
            r"'d": " would"
        }
        
        for contraction, expansion in contractions.items():
            text = re.sub(contraction, expansion, text, flags=re.IGNORECASE)
        
        # Ensure consistent terminology
        text = self._ensure_consistent_terminology(text)
        
        return text
    
    def _is_complete_thought(self, text: str) -> bool:
        """
        Check if text represents a complete thought.
        
        Args:
            text: Text to check
            
        Returns:
            True if complete thought
        """
        import re
        
        # Must have reasonable length
        if len(text.strip()) < 10:
            return False
        
        # Must have subject and predicate indicators
        words = text.lower().split()
        
        # Check for common verbs
        verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would', 'can', 'could', 'should']
        has_verb = any(verb in words for verb in verbs)
        
        # Check for medical context indicators
        medical_indicators = ['patient', 'treatment', 'diagnosis', 'medical', 'clinical']
        has_medical_context = any(indicator in words for indicator in medical_indicators)
        
        return has_verb and (has_medical_context or len(words) >= 5)
    
    def _combine_sentence_fragments(self, text: str) -> str:
        """
        Combine sentence fragments into complete sentences.
        
        Args:
            text: Text with potential fragments
            
        Returns:
            Text with combined sentences
        """
        import re
        
        # Split into potential sentences
        parts = re.split(r'([.!?]\s*)', text)
        
        combined = []
        i = 0
        
        while i < len(parts):
            if i % 2 == 0:  # Sentence content
                sentence = parts[i].strip()
                
                # Check if this is a fragment that should be combined
                if (sentence and len(sentence.split()) < 4 and 
                    i + 2 < len(parts) and 
                    not self._is_complete_thought(sentence)):
                    
                    # Combine with next sentence
                    next_sentence = parts[i + 2].strip() if i + 2 < len(parts) else ''
                    if next_sentence:
                        combined_sentence = f"{sentence} {next_sentence}"
                        combined.append(combined_sentence)
                        if i + 1 < len(parts):  # Add punctuation
                            combined.append(parts[i + 1])
                        i += 4  # Skip the combined parts
                        continue
                
                combined.append(sentence)
            else:  # Punctuation
                combined.append(parts[i])
            
            i += 1
        
        return ''.join(combined)
    
    def _ensure_consistent_terminology(self, text: str) -> str:
        """
        Ensure consistent medical terminology usage.
        
        Args:
            text: Text to process
            
        Returns:
            Text with consistent terminology
        """
        # This could be expanded with a comprehensive medical terminology database
        # For now, handle basic consistency
        
        import re
        
        # Ensure consistent capitalization of medical terms
        medical_terms = {
            'covid-19': 'COVID-19',
            'hiv': 'HIV',
            'aids': 'AIDS',
            'dna': 'DNA',
            'rna': 'RNA',
            'mri': 'MRI',
            'ct scan': 'CT scan',
            'x-ray': 'X-ray'
        }
        
        for term, standard in medical_terms.items():
            text = re.sub(r'\b' + re.escape(term) + r'\b', standard, text, flags=re.IGNORECASE)
        
        return text
    
    def _count_artifacts_fixed(self, original: str, enhanced: str) -> int:
        """
        Count the number of artifacts fixed.
        
        Args:
            original: Original text
            enhanced: Enhanced text
            
        Returns:
            Number of artifacts fixed
        """
        import re
        
        # Count common artifacts in original
        artifacts = [
            r'[\x0c\ufeff\u00a0]',  # Control characters
            r'\b[a-zA-Z]\s+[a-zA-Z]\s+[a-zA-Z]\b',  # Broken words
            r'\s{2,}',  # Multiple spaces
            r'\s+[,.!?;:]',  # Space before punctuation
        ]
        
        original_count = sum(len(re.findall(pattern, original)) for pattern in artifacts)
        enhanced_count = sum(len(re.findall(pattern, enhanced)) for pattern in artifacts)
        
        return max(0, original_count - enhanced_count)
    
    def _count_grammar_improvements(self, original: str, enhanced: str) -> int:
        """
        Count grammar improvements made.
        
        Args:
            original: Original text
            enhanced: Enhanced text
            
        Returns:
            Number of grammar improvements
        """
        improvements = 0
        
        # Check for capitalization improvements
        if original and enhanced:
            if original[0].islower() and enhanced[0].isupper():
                improvements += 1
        
        # Check for punctuation improvements
        if not original.rstrip().endswith(('.', '!', '?')) and enhanced.rstrip().endswith(('.', '!', '?')):
            improvements += 1
        
        # Check for spacing improvements
        if '  ' in original and '  ' not in enhanced:
            improvements += 1
        
        return improvements
    
    def _calculate_readability_score(self, text: str) -> float:
        """
        Calculate readability score for text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Readability score between 0.0 and 1.0
        """
        if not text or not text.strip():
            return 0.0
        
        score = 0.0
        
        # Factor 1: Proper capitalization
        if text[0].isupper():
            score += 0.2
        
        # Factor 2: Proper punctuation
        if text.rstrip().endswith(('.', '!', '?')):
            score += 0.2
        
        # Factor 3: No excessive spacing
        if '  ' not in text:
            score += 0.2
        
        # Factor 4: Reasonable sentence length
        words = text.split()
        if 5 <= len(words) <= 30:
            score += 0.2
        
        # Factor 5: Complete sentence structure
        if self._is_complete_thought(text):
            score += 0.2
        
        return score
    
    def _assess_translation_readiness(self, text: str) -> float:
        """
        Assess how ready text is for translation.
        
        Args:
            text: Text to assess
            
        Returns:
            Translation readiness score between 0.0 and 1.0
        """
        if not text or not text.strip():
            return 0.0
        
        score = 0.0
        
        # Clear sentence boundaries
        if text.count('.') > 0 or text.count('!') > 0 or text.count('?') > 0:
            score += 0.3
        
        # No contractions
        contractions = ["n't", "'re", "'ve", "'ll", "'d"]
        if not any(contraction in text for contraction in contractions):
            score += 0.2
        
        # Consistent terminology
        if not any(term in text.lower() for term in ['dr', 'meds', 'docs']):
            score += 0.2
        
        # Proper spacing and punctuation
        import re
        if not re.search(r'\s+[,.!?;:]', text) and not re.search(r'\s{2,}', text):
            score += 0.3
        
        return score
