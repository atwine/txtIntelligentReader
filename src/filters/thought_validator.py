#!/usr/bin/env python3
"""
Complete Thought Validator (Layer 4) for txtIntelligentReader

This filter provides final validation for complete thoughts and translation readiness.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import time


class CompleteThoughtValidator:
    """
    Fourth and final layer filter that validates complete thoughts and translation readiness.
    
    This filter handles:
    - Structural completeness validation
    - Semantic coherence checking
    - Actionability assessment
    - Translation readiness validation
    - Final quality scoring
    """
    
    def __init__(self, quality_threshold: float = 0.7, use_spacy: bool = False):
        """
        Initialize the CompleteThoughtValidator.
        
        Args:
            quality_threshold: Minimum quality score to keep sentences
            use_spacy: Whether to use spaCy for advanced NLP (optional dependency)
        """
        self.quality_threshold = quality_threshold
        self.use_spacy = use_spacy
        self.nlp = None
        
        # Initialize spaCy if requested and available
        if use_spacy:
            try:
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
            except (ImportError, OSError):
                print("Warning: spaCy not available, using rule-based validation")
                self.use_spacy = False
        
        # Structural patterns for validation
        self.subject_patterns = self._compile_subject_patterns()
        self.verb_patterns = self._compile_verb_patterns()
        self.actionable_patterns = self._compile_actionable_patterns()
        self.quality_indicators = self._compile_quality_indicators()
        
        # Statistics tracking
        self.stats = {
            'total_processed': 0,
            'structurally_complete': 0,
            'semantically_coherent': 0,
            'actionable_sentences': 0,
            'translation_ready': 0,
            'high_quality': 0,
            'processing_time': 0.0,
            'average_quality_score': 0.0,
            'validation_breakdown': {
                'structure_pass': 0,
                'coherence_pass': 0,
                'actionability_pass': 0,
                'translation_pass': 0
            }
        }
    
    def validate_structure(self, sentence: str) -> Dict[str, Any]:
        """
        Validate structural completeness of a sentence.
        
        Args:
            sentence: Sentence to validate
            
        Returns:
            Dictionary with structural validation results
        """
        if not sentence or not sentence.strip():
            return {
                'has_subject': False,
                'has_verb': False,
                'has_object': False,
                'is_structurally_complete': False,
                'structure_score': 0.0,
                'structural_elements': []
            }
        
        sentence = sentence.strip()
        
        if self.use_spacy and self.nlp:
            return self._spacy_structural_validation(sentence)
        else:
            return self._rule_based_structural_validation(sentence)
    
    def validate_semantic_coherence(self, sentence: str) -> Dict[str, Any]:
        """
        Validate semantic coherence and meaning clarity.
        
        Args:
            sentence: Sentence to validate
            
        Returns:
            Dictionary with semantic validation results
        """
        if not sentence or not sentence.strip():
            return {
                'is_coherent': False,
                'has_clear_meaning': False,
                'coherence_score': 0.0,
                'meaning_indicators': [],
                'coherence_issues': ['Empty sentence']
            }
        
        sentence = sentence.strip()
        words = sentence.split()
        
        # Coherence factors
        coherence_factors = []
        meaning_indicators = []
        coherence_issues = []
        
        # 1. Length appropriateness
        if 5 <= len(words) <= 30:
            coherence_factors.append(0.2)
            meaning_indicators.append('appropriate_length')
        elif len(words) < 5:
            coherence_issues.append('too_short')
        else:
            coherence_issues.append('too_long')
        
        # 2. Word variety (not too repetitive)
        unique_words = set(word.lower() for word in words)
        variety_ratio = len(unique_words) / len(words) if words else 0
        if variety_ratio > 0.7:
            coherence_factors.append(0.2)
            meaning_indicators.append('good_word_variety')
        elif variety_ratio < 0.5:
            coherence_issues.append('repetitive_words')
        
        # 3. Proper capitalization
        if sentence[0].isupper():
            coherence_factors.append(0.1)
            meaning_indicators.append('proper_capitalization')
        else:
            coherence_issues.append('improper_capitalization')
        
        # 4. Proper punctuation
        if sentence.endswith(('.', '!', '?')):
            coherence_factors.append(0.2)
            meaning_indicators.append('proper_punctuation')
        else:
            coherence_issues.append('missing_punctuation')
        
        # 5. Logical word order (basic check)
        if self._has_logical_word_order(sentence):
            coherence_factors.append(0.3)
            meaning_indicators.append('logical_word_order')
        else:
            coherence_issues.append('illogical_word_order')
        
        coherence_score = sum(coherence_factors)
        is_coherent = coherence_score >= 0.6
        has_clear_meaning = coherence_score >= 0.5 and len(coherence_issues) <= 2
        
        return {
            'is_coherent': is_coherent,
            'has_clear_meaning': has_clear_meaning,
            'coherence_score': coherence_score,
            'meaning_indicators': meaning_indicators,
            'coherence_issues': coherence_issues
        }
    
    def validate_actionability(self, sentence: str) -> Dict[str, Any]:
        """
        Validate if sentence contains actionable or informative content.
        
        Args:
            sentence: Sentence to validate
            
        Returns:
            Dictionary with actionability validation results
        """
        if not sentence or not sentence.strip():
            return {
                'is_actionable': False,
                'is_informative': False,
                'actionability_score': 0.0,
                'action_indicators': [],
                'information_type': 'none'
            }
        
        sentence_lower = sentence.lower()
        action_indicators = []
        actionability_score = 0.0
        
        # Check for actionable patterns
        for pattern_name, pattern in self.actionable_patterns.items():
            if pattern.search(sentence_lower):
                action_indicators.append(pattern_name)
                actionability_score += 0.2
        
        # Check for informative content
        information_types = []
        
        # Medical information
        medical_terms = ['patient', 'doctor', 'treatment', 'medication', 'diagnosis', 'symptoms', 'therapy']
        if any(term in sentence_lower for term in medical_terms):
            information_types.append('medical')
            actionability_score += 0.3
        
        # Procedural information
        procedural_terms = ['procedure', 'process', 'method', 'technique', 'approach', 'protocol']
        if any(term in sentence_lower for term in procedural_terms):
            information_types.append('procedural')
            actionability_score += 0.2
        
        # Factual information
        factual_patterns = [r'\d+', r'(is|are|was|were)\s+\w+', r'(has|have|had)\s+\w+']
        if any(re.search(pattern, sentence_lower) for pattern in factual_patterns):
            information_types.append('factual')
            actionability_score += 0.2
        
        # Instructional information
        instructional_terms = ['should', 'must', 'need to', 'required', 'recommended', 'advised']
        if any(term in sentence_lower for term in instructional_terms):
            information_types.append('instructional')
            actionability_score += 0.3
        
        actionability_score = min(1.0, actionability_score)
        is_actionable = actionability_score >= 0.4
        is_informative = len(information_types) > 0
        information_type = ', '.join(information_types) if information_types else 'none'
        
        return {
            'is_actionable': is_actionable,
            'is_informative': is_informative,
            'actionability_score': actionability_score,
            'action_indicators': action_indicators,
            'information_type': information_type
        }
    
    def validate_translation_readiness(self, sentence: str) -> Dict[str, Any]:
        """
        Validate if sentence is ready for translation.
        
        Args:
            sentence: Sentence to validate
            
        Returns:
            Dictionary with translation readiness results
        """
        if not sentence or not sentence.strip():
            return {
                'is_translation_ready': False,
                'translation_score': 0.0,
                'readiness_factors': [],
                'translation_issues': ['Empty sentence']
            }
        
        sentence = sentence.strip()
        readiness_factors = []
        translation_issues = []
        translation_score = 0.0
        
        # 1. Complete sentence structure
        structure_result = self.validate_structure(sentence)
        if structure_result['is_structurally_complete']:
            translation_score += 0.3
            readiness_factors.append('complete_structure')
        else:
            translation_issues.append('incomplete_structure')
        
        # 2. Semantic coherence
        coherence_result = self.validate_semantic_coherence(sentence)
        if coherence_result['is_coherent']:
            translation_score += 0.3
            readiness_factors.append('semantic_coherence')
        else:
            translation_issues.append('semantic_issues')
        
        # 3. Clear meaning
        if coherence_result['has_clear_meaning']:
            translation_score += 0.2
            readiness_factors.append('clear_meaning')
        else:
            translation_issues.append('unclear_meaning')
        
        # 4. Appropriate length
        words = sentence.split()
        if 3 <= len(words) <= 25:
            translation_score += 0.1
            readiness_factors.append('appropriate_length')
        else:
            translation_issues.append('inappropriate_length')
        
        # 5. No obvious errors
        if not self._has_obvious_errors(sentence):
            translation_score += 0.1
            readiness_factors.append('no_obvious_errors')
        else:
            translation_issues.append('contains_errors')
        
        is_translation_ready = translation_score >= 0.7
        
        return {
            'is_translation_ready': is_translation_ready,
            'translation_score': translation_score,
            'readiness_factors': readiness_factors,
            'translation_issues': translation_issues
        }
    
    def final_validation(self, sentence: str) -> Dict[str, Any]:
        """
        Perform comprehensive final validation of a sentence.
        
        Args:
            sentence: Sentence to validate
            
        Returns:
            Dictionary with complete validation results
        """
        start_time = time.time()
        
        # Perform all validations
        structure_result = self.validate_structure(sentence)
        coherence_result = self.validate_semantic_coherence(sentence)
        actionability_result = self.validate_actionability(sentence)
        translation_result = self.validate_translation_readiness(sentence)
        
        # Calculate overall quality score
        quality_components = [
            structure_result['structure_score'] * 0.3,
            coherence_result['coherence_score'] * 0.3,
            actionability_result['actionability_score'] * 0.2,
            translation_result['translation_score'] * 0.2
        ]
        
        overall_quality = sum(quality_components)
        
        # Determine final acceptance
        passes_validation = (
            structure_result['is_structurally_complete'] and
            coherence_result['is_coherent'] and
            actionability_result['is_informative'] and
            translation_result['is_translation_ready'] and
            overall_quality >= self.quality_threshold
        )
        
        # Update statistics
        self.stats['processing_time'] += time.time() - start_time
        
        return {
            'sentence': sentence,
            'passes_validation': passes_validation,
            'overall_quality': overall_quality,
            'structure_validation': structure_result,
            'coherence_validation': coherence_result,
            'actionability_validation': actionability_result,
            'translation_validation': translation_result,
            'quality_breakdown': {
                'structure': structure_result['structure_score'],
                'coherence': coherence_result['coherence_score'],
                'actionability': actionability_result['actionability_score'],
                'translation': translation_result['translation_score']
            },
            'validation_summary': {
                'structural_complete': structure_result['is_structurally_complete'],
                'semantically_coherent': coherence_result['is_coherent'],
                'actionable_informative': actionability_result['is_informative'],
                'translation_ready': translation_result['is_translation_ready']
            }
        }
    
    def batch_validate(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Validate multiple sentences efficiently.
        
        Args:
            sentences: List of sentences to validate
            
        Returns:
            List of validation results for each sentence
        """
        if not sentences:
            return []
        
        results = []
        self.stats['total_processed'] = len(sentences)
        
        for sentence in sentences:
            result = self.final_validation(sentence)
            results.append(result)
            
            # Update statistics
            if result['validation_summary']['structural_complete']:
                self.stats['structurally_complete'] += 1
                self.stats['validation_breakdown']['structure_pass'] += 1
            
            if result['validation_summary']['semantically_coherent']:
                self.stats['semantically_coherent'] += 1
                self.stats['validation_breakdown']['coherence_pass'] += 1
            
            if result['validation_summary']['actionable_informative']:
                self.stats['actionable_sentences'] += 1
                self.stats['validation_breakdown']['actionability_pass'] += 1
            
            if result['validation_summary']['translation_ready']:
                self.stats['translation_ready'] += 1
                self.stats['validation_breakdown']['translation_pass'] += 1
            
            if result['passes_validation']:
                self.stats['high_quality'] += 1
        
        # Calculate average quality score
        if results:
            self.stats['average_quality_score'] = sum(r['overall_quality'] for r in results) / len(results)
        
        return results
    
    def filter_by_quality(self, sentences: List[str], threshold: float = None) -> List[str]:
        """
        Filter sentences based on final quality validation.
        
        Args:
            sentences: List of sentences to filter
            threshold: Override default quality threshold
            
        Returns:
            Filtered list of high-quality sentences
        """
        if not sentences:
            return []
        
        threshold = threshold or self.quality_threshold
        
        # Validate all sentences
        validations = self.batch_validate(sentences)
        
        # Filter based on quality
        filtered = []
        for sentence, validation in zip(sentences, validations):
            if validation['passes_validation'] and validation['overall_quality'] >= threshold:
                filtered.append(sentence)
        
        return filtered
    
    def _compile_subject_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for subject detection."""
        return {
            'personal_pronouns': re.compile(r'\b(i|you|he|she|it|we|they)\b', re.IGNORECASE),
            'nouns': re.compile(r'\b(patient|doctor|treatment|medication|person|people|study|research)\b', re.IGNORECASE),
            'proper_nouns': re.compile(r'\b[A-Z][a-z]+\b'),
            'determiners': re.compile(r'\b(the|a|an|this|that|these|those)\s+\w+', re.IGNORECASE)
        }
    
    def _compile_verb_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for verb detection."""
        return {
            'action_verbs': re.compile(r'\b(take|give|perform|conduct|analyze|treat|diagnose|prescribe|monitor)\b', re.IGNORECASE),
            'being_verbs': re.compile(r'\b(is|are|was|were|am|be|being|been)\b', re.IGNORECASE),
            'auxiliary_verbs': re.compile(r'\b(have|has|had|will|would|can|could|should|may|might|must)\b', re.IGNORECASE),
            'modal_verbs': re.compile(r'\b(can|could|may|might|must|shall|should|will|would)\b', re.IGNORECASE)
        }
    
    def _compile_actionable_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for actionable content detection."""
        return {
            'instructions': re.compile(r'\b(take|administer|apply|follow|continue|stop|start|begin)\b', re.IGNORECASE),
            'recommendations': re.compile(r'\b(should|recommend|suggest|advise|propose)\b', re.IGNORECASE),
            'procedures': re.compile(r'\b(procedure|process|method|technique|protocol|guideline)\b', re.IGNORECASE),
            'measurements': re.compile(r'\d+\s*(mg|ml|cc|units|times|hours|days|weeks)', re.IGNORECASE),
            'medical_actions': re.compile(r'\b(diagnose|treat|prescribe|monitor|examine|test|scan)\b', re.IGNORECASE)
        }
    
    def _compile_quality_indicators(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for quality indicators."""
        return {
            'specific_terms': re.compile(r'\b(specific|particular|exact|precise|detailed)\b', re.IGNORECASE),
            'quantifiers': re.compile(r'\b(\d+|several|many|few|some|all|most)\b', re.IGNORECASE),
            'temporal_markers': re.compile(r'\b(before|after|during|while|when|then|now|today|yesterday)\b', re.IGNORECASE),
            'causal_markers': re.compile(r'\b(because|since|due to|caused by|results in|leads to)\b', re.IGNORECASE)
        }
    
    def _spacy_structural_validation(self, sentence: str) -> Dict[str, Any]:
        """Use spaCy for structural validation."""
        doc = self.nlp(sentence)
        
        # Find subjects
        subjects = [token for token in doc if token.dep_ in ["nsubj", "nsubjpass", "csubj"]]
        has_subject = len(subjects) > 0
        
        # Find verbs
        verbs = [token for token in doc if token.pos_ == "VERB"]
        has_verb = len(verbs) > 0
        
        # Find objects
        objects = [token for token in doc if token.dep_ in ["dobj", "iobj", "pobj"]]
        has_object = len(objects) > 0
        
        # Structural elements
        structural_elements = []
        if has_subject:
            structural_elements.extend([f"subject:{s.text}" for s in subjects[:2]])
        if has_verb:
            structural_elements.extend([f"verb:{v.text}" for v in verbs[:2]])
        if has_object:
            structural_elements.extend([f"object:{o.text}" for o in objects[:2]])
        
        # Calculate structure score
        structure_components = [has_subject, has_verb, has_object]
        structure_score = sum(structure_components) / len(structure_components)
        
        is_structurally_complete = has_subject and has_verb
        
        return {
            'has_subject': has_subject,
            'has_verb': has_verb,
            'has_object': has_object,
            'is_structurally_complete': is_structurally_complete,
            'structure_score': structure_score,
            'structural_elements': structural_elements
        }
    
    def _rule_based_structural_validation(self, sentence: str) -> Dict[str, Any]:
        """Use rule-based patterns for structural validation."""
        sentence_lower = sentence.lower()
        
        # Check for subjects
        has_subject = any(pattern.search(sentence_lower) for pattern in self.subject_patterns.values())
        
        # Check for verbs
        has_verb = any(pattern.search(sentence_lower) for pattern in self.verb_patterns.values())
        
        # Check for objects (basic pattern)
        object_patterns = [r'\b(the|a|an)\s+\w+(?:\s+\w+)?\s*$', r'\w+(?:s|ed|ing)\s+\w+']
        has_object = any(re.search(pattern, sentence_lower) for pattern in object_patterns)
        
        # Identify structural elements
        structural_elements = []
        for pattern_name, pattern in self.subject_patterns.items():
            matches = pattern.findall(sentence)
            if matches:
                structural_elements.extend([f"subject:{match}" for match in matches[:2]])
        
        for pattern_name, pattern in self.verb_patterns.items():
            matches = pattern.findall(sentence)
            if matches:
                structural_elements.extend([f"verb:{match}" for match in matches[:2]])
        
        # Calculate structure score
        structure_components = [has_subject, has_verb, has_object]
        structure_score = sum(structure_components) / len(structure_components)
        
        is_structurally_complete = has_subject and has_verb
        
        return {
            'has_subject': has_subject,
            'has_verb': has_verb,
            'has_object': has_object,
            'is_structurally_complete': is_structurally_complete,
            'structure_score': structure_score,
            'structural_elements': structural_elements
        }
    
    def _has_logical_word_order(self, sentence: str) -> bool:
        """Check for logical word order (basic heuristics)."""
        words = sentence.lower().split()
        
        # Basic checks for illogical patterns
        illogical_patterns = [
            r'\b(the|a|an)\s+(is|are|was|were)\b',  # "the is"
            r'\b(and|or|but)\s+\.',  # conjunction at end
            r'^\s*(and|or|but)\b',  # conjunction at start
            r'\b(\w+)\s+\1\b',  # repeated words - fixed group reference
        ]
        
        sentence_lower = sentence.lower()
        for pattern in illogical_patterns:
            if re.search(pattern, sentence_lower):
                return False
        
        return True
    
    def _has_obvious_errors(self, sentence: str) -> bool:
        """Check for obvious errors in the sentence."""
        # Check for common error patterns
        error_patterns = [
            r'\b(\w+)\s+\1\b',  # Repeated words - fixed group reference
            r'[.]{2,}',  # Multiple periods
            r'[?]{2,}',  # Multiple question marks
            r'[!]{2,}',  # Multiple exclamation marks
            r'\s{2,}',  # Multiple spaces
            r'[A-Z]{3,}',  # All caps words (might be acronyms, but often errors)
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, sentence):
                return True
        
        return False
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the validation process.
        
        Returns:
            Dictionary containing validation statistics
        """
        total = self.stats['total_processed']
        
        return {
            'total_processed': total,
            'structurally_complete': self.stats['structurally_complete'],
            'structure_rate': self.stats['structurally_complete'] / total if total > 0 else 0,
            'semantically_coherent': self.stats['semantically_coherent'],
            'coherence_rate': self.stats['semantically_coherent'] / total if total > 0 else 0,
            'actionable_sentences': self.stats['actionable_sentences'],
            'actionability_rate': self.stats['actionable_sentences'] / total if total > 0 else 0,
            'translation_ready': self.stats['translation_ready'],
            'translation_readiness_rate': self.stats['translation_ready'] / total if total > 0 else 0,
            'high_quality': self.stats['high_quality'],
            'quality_pass_rate': self.stats['high_quality'] / total if total > 0 else 0,
            'processing_time': self.stats['processing_time'],
            'average_processing_time': self.stats['processing_time'] / total if total > 0 else 0,
            'average_quality_score': self.stats['average_quality_score'],
            'quality_threshold': self.quality_threshold,
            'validation_breakdown': self.stats['validation_breakdown'],
            'spacy_enabled': self.use_spacy
        }
    
    def reset_stats(self):
        """Reset validation statistics."""
        self.stats = {
            'total_processed': 0,
            'structurally_complete': 0,
            'semantically_coherent': 0,
            'actionable_sentences': 0,
            'translation_ready': 0,
            'high_quality': 0,
            'processing_time': 0.0,
            'average_quality_score': 0.0,
            'validation_breakdown': {
                'structure_pass': 0,
                'coherence_pass': 0,
                'actionability_pass': 0,
                'translation_pass': 0
            }
        }
