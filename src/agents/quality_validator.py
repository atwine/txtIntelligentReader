"""
Quality Validation Agent for txtIntelligentReader

This agent specializes in final quality validation and translation readiness assessment.
"""

from crewai import Agent
from typing import List, Dict, Any, Tuple


class QualityValidationAgent:
    """
    Agent specialized in ensuring final output meets translation readiness standards.
    
    Role: Quality Control Specialist
    Goal: Ensure final output meets translation readiness standards
    Backstory: You validate content for international medical translation projects.
    """
    
    def __init__(self, llm):
        """Initialize the Quality Validation Agent with LLM."""
        self.agent = Agent(
            role="Quality Control Specialist",
            goal="Ensure final output meets translation readiness standards",
            backstory="You validate content for international medical translation projects.",
            llm=llm,
            verbose=True
        )
    
    def validate_sentence(self, sentence: str) -> Dict[str, Any]:
        """
        Perform final quality check on a sentence.
        
        Args:
            sentence: Sentence to validate
            
        Returns:
            Validation results with quality metrics
        """
        if not sentence or not sentence.strip():
            return {
                'is_valid': False,
                'quality_score': 0.0,
                'issues': ['Empty or whitespace-only sentence'],
                'recommendations': ['Provide meaningful content'],
                'translation_ready': False
            }
        
        # Comprehensive validation pipeline
        validation_results = {
            'is_valid': True,
            'quality_score': 0.0,
            'issues': [],
            'recommendations': [],
            'translation_ready': False,
            'validation_details': {}
        }
        
        # Step 1: Grammar and structure validation
        grammar_results = self._validate_grammar_structure(sentence)
        validation_results['validation_details']['grammar'] = grammar_results
        
        # Step 2: Medical accuracy validation
        medical_results = self.validate_medical_accuracy(sentence)
        validation_results['validation_details']['medical'] = medical_results
        
        # Step 3: Translation readiness check
        is_ready, issues = self.check_translation_readiness(sentence)
        validation_results['translation_ready'] = is_ready
        validation_results['issues'].extend(issues)
        
        # Step 4: Content completeness validation
        completeness_results = self._validate_content_completeness(sentence)
        validation_results['validation_details']['completeness'] = completeness_results
        
        # Step 5: Calculate overall quality score
        quality_score = self._calculate_overall_quality_score(validation_results['validation_details'])
        validation_results['quality_score'] = quality_score
        
        # Step 6: Determine if sentence meets quality threshold
        quality_threshold = 0.7  # Configurable threshold
        validation_results['is_valid'] = quality_score >= quality_threshold
        
        # Step 7: Generate recommendations
        recommendations = self._generate_quality_recommendations(validation_results)
        validation_results['recommendations'] = recommendations
        
        return validation_results
    
    def calculate_confidence_score(self, sentence: str, metadata: Dict[str, Any]) -> float:
        """
        Generate confidence score for sentence quality.
        
        Args:
            sentence: Sentence to score
            metadata: Additional metadata from previous agents
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not sentence or not sentence.strip():
            return 0.0
        
        confidence_factors = []
        
        # Factor 1: Grammar and structure confidence
        grammar_confidence = self._calculate_grammar_confidence(sentence)
        confidence_factors.append(grammar_confidence)
        
        # Factor 2: Medical content confidence (from metadata)
        medical_confidence = metadata.get('health_relevance_score', 0.5)
        confidence_factors.append(medical_confidence)
        
        # Factor 3: Content classification confidence (from metadata)
        classification_confidence = metadata.get('classification_confidence', 0.5)
        confidence_factors.append(classification_confidence)
        
        # Factor 4: Enhancement quality confidence
        enhancement_confidence = self._calculate_enhancement_confidence(sentence, metadata)
        confidence_factors.append(enhancement_confidence)
        
        # Factor 5: Translation readiness confidence
        translation_confidence = self._calculate_translation_confidence(sentence)
        confidence_factors.append(translation_confidence)
        
        # Weighted average with emphasis on critical factors
        weights = [0.25, 0.20, 0.15, 0.20, 0.20]  # grammar, medical, classification, enhancement, translation
        weighted_confidence = sum(conf * weight for conf, weight in zip(confidence_factors, weights))
        
        return min(weighted_confidence, 1.0)
    
    def check_translation_readiness(self, sentence: str) -> Tuple[bool, List[str]]:
        """
        Check if sentence is ready for translation.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            Tuple of (is_ready, list_of_issues)
        """
        issues = []
        
        if not sentence or not sentence.strip():
            return False, ['Empty sentence']
        
        import re
        
        # Check 1: Complete sentence structure
        if not sentence.strip().endswith(('.', '!', '?')):
            issues.append('Missing sentence-ending punctuation')
        
        # Check 2: Proper capitalization
        if sentence.strip() and not sentence.strip()[0].isupper():
            issues.append('Sentence should start with capital letter')
        
        # Check 3: No contractions (for formal medical translation)
        contractions = ["n't", "'re", "'ve", "'ll", "'d", "'s"]
        if any(contraction in sentence for contraction in contractions):
            issues.append('Contains contractions that should be expanded')
        
        # Check 4: No excessive spacing or formatting issues
        if re.search(r'\s{2,}', sentence):
            issues.append('Contains excessive spacing')
        
        # Check 5: No obvious artifacts
        artifacts = ['\x0c', '\ufeff', '\u00a0']
        if any(artifact in sentence for artifact in artifacts):
            issues.append('Contains text artifacts')
        
        # Check 6: Reasonable length for translation
        word_count = len(sentence.split())
        if word_count < 3:
            issues.append('Sentence too short for meaningful translation')
        elif word_count > 50:
            issues.append('Sentence may be too long for optimal translation')
        
        # Check 7: Clear meaning and context
        if not self._has_clear_meaning(sentence):
            issues.append('Sentence lacks clear meaning or context')
        
        # Check 8: Medical terminology consistency
        if not self._has_consistent_medical_terminology(sentence):
            issues.append('Inconsistent medical terminology usage')
        
        is_ready = len(issues) == 0
        return is_ready, issues
    
    def validate_medical_accuracy(self, sentence: str) -> Dict[str, Any]:
        """
        Validate medical accuracy and terminology usage.
        
        Args:
            sentence: Sentence with medical content
            
        Returns:
            Medical accuracy validation results
        """
        validation_results = {
            'is_medically_accurate': True,
            'accuracy_score': 1.0,
            'medical_issues': [],
            'terminology_issues': [],
            'recommendations': []
        }
        
        if not sentence or not sentence.strip():
            validation_results['is_medically_accurate'] = False
            validation_results['accuracy_score'] = 0.0
            return validation_results
        
        # Check medical terminology usage
        terminology_issues = self._check_medical_terminology(sentence)
        validation_results['terminology_issues'] = terminology_issues
        
        # Check for medical context consistency
        context_issues = self._check_medical_context_consistency(sentence)
        validation_results['medical_issues'].extend(context_issues)
        
        # Check for potential medical inaccuracies
        accuracy_issues = self._check_medical_accuracy_patterns(sentence)
        validation_results['medical_issues'].extend(accuracy_issues)
        
        # Calculate accuracy score
        total_issues = len(terminology_issues) + len(validation_results['medical_issues'])
        if total_issues == 0:
            validation_results['accuracy_score'] = 1.0
        else:
            # Reduce score based on number of issues
            validation_results['accuracy_score'] = max(0.0, 1.0 - (total_issues * 0.2))
        
        # Determine overall medical accuracy
        validation_results['is_medically_accurate'] = validation_results['accuracy_score'] >= 0.8
        
        # Generate recommendations
        if terminology_issues:
            validation_results['recommendations'].append('Review medical terminology for consistency')
        if validation_results['medical_issues']:
            validation_results['recommendations'].append('Verify medical accuracy with domain expert')
        
        return validation_results
    
    def get_quality_metrics(self, sentence: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive quality metrics for a sentence.
        
        Args:
            sentence: Sentence to analyze
            metadata: Metadata from previous processing steps
            
        Returns:
            Comprehensive quality metrics
        """
        metrics = {
            'sentence_length': len(sentence) if sentence else 0,
            'word_count': len(sentence.split()) if sentence else 0,
            'validation_results': self.validate_sentence(sentence),
            'confidence_score': self.calculate_confidence_score(sentence, metadata),
            'medical_validation': self.validate_medical_accuracy(sentence),
            'translation_readiness': self.check_translation_readiness(sentence),
            'quality_grade': self._assign_quality_grade(sentence, metadata)
        }
        
        return metrics
    
    def _validate_grammar_structure(self, sentence: str) -> Dict[str, Any]:
        """
        Validate grammar and sentence structure.
        
        Args:
            sentence: Sentence to validate
            
        Returns:
            Grammar validation results
        """
        results = {
            'has_proper_capitalization': False,
            'has_proper_punctuation': False,
            'has_complete_structure': False,
            'grammar_score': 0.0,
            'grammar_issues': []
        }
        
        if not sentence or not sentence.strip():
            results['grammar_issues'].append('Empty sentence')
            return results
        
        sentence = sentence.strip()
        
        # Check capitalization
        if sentence[0].isupper():
            results['has_proper_capitalization'] = True
        else:
            results['grammar_issues'].append('Should start with capital letter')
        
        # Check punctuation
        if sentence.endswith(('.', '!', '?')):
            results['has_proper_punctuation'] = True
        else:
            results['grammar_issues'].append('Missing sentence-ending punctuation')
        
        # Check complete structure
        if self._is_complete_sentence_structure(sentence):
            results['has_complete_structure'] = True
        else:
            results['grammar_issues'].append('Incomplete sentence structure')
        
        # Calculate grammar score
        score_factors = [
            results['has_proper_capitalization'],
            results['has_proper_punctuation'],
            results['has_complete_structure']
        ]
        results['grammar_score'] = sum(score_factors) / len(score_factors)
        
        return results
    
    def _validate_content_completeness(self, sentence: str) -> Dict[str, Any]:
        """
        Validate content completeness and meaningfulness.
        
        Args:
            sentence: Sentence to validate
            
        Returns:
            Content completeness results
        """
        results = {
            'is_complete_thought': False,
            'has_clear_meaning': False,
            'has_sufficient_context': False,
            'completeness_score': 0.0,
            'completeness_issues': []
        }
        
        if not sentence or not sentence.strip():
            results['completeness_issues'].append('No content to evaluate')
            return results
        
        # Check if it's a complete thought
        if self._is_complete_thought(sentence):
            results['is_complete_thought'] = True
        else:
            results['completeness_issues'].append('Not a complete thought')
        
        # Check for clear meaning
        if self._has_clear_meaning(sentence):
            results['has_clear_meaning'] = True
        else:
            results['completeness_issues'].append('Lacks clear meaning')
        
        # Check for sufficient context
        if self._has_sufficient_context(sentence):
            results['has_sufficient_context'] = True
        else:
            results['completeness_issues'].append('Insufficient context for understanding')
        
        # Calculate completeness score
        score_factors = [
            results['is_complete_thought'],
            results['has_clear_meaning'],
            results['has_sufficient_context']
        ]
        results['completeness_score'] = sum(score_factors) / len(score_factors)
        
        return results
    
    def _calculate_overall_quality_score(self, validation_details: Dict[str, Any]) -> float:
        """
        Calculate overall quality score from validation details.
        
        Args:
            validation_details: Results from various validation steps
            
        Returns:
            Overall quality score between 0.0 and 1.0
        """
        scores = []
        
        # Grammar score
        if 'grammar' in validation_details:
            scores.append(validation_details['grammar'].get('grammar_score', 0.0))
        
        # Medical accuracy score
        if 'medical' in validation_details:
            scores.append(validation_details['medical'].get('accuracy_score', 0.0))
        
        # Completeness score
        if 'completeness' in validation_details:
            scores.append(validation_details['completeness'].get('completeness_score', 0.0))
        
        # Return average if we have scores, otherwise 0
        return sum(scores) / len(scores) if scores else 0.0
    
    def _generate_quality_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """
        Generate quality improvement recommendations.
        
        Args:
            validation_results: Complete validation results
            
        Returns:
            List of improvement recommendations
        """
        recommendations = []
        
        # Grammar recommendations
        if 'grammar' in validation_results.get('validation_details', {}):
            grammar_issues = validation_results['validation_details']['grammar'].get('grammar_issues', [])
            for issue in grammar_issues:
                recommendations.append(f"Grammar: {issue}")
        
        # Medical recommendations
        if 'medical' in validation_results.get('validation_details', {}):
            medical_recs = validation_results['validation_details']['medical'].get('recommendations', [])
            recommendations.extend(medical_recs)
        
        # Completeness recommendations
        if 'completeness' in validation_results.get('validation_details', {}):
            completeness_issues = validation_results['validation_details']['completeness'].get('completeness_issues', [])
            for issue in completeness_issues:
                recommendations.append(f"Content: {issue}")
        
        # Translation readiness recommendations
        if not validation_results.get('translation_ready', False):
            recommendations.append('Review translation readiness issues')
        
        return recommendations
    
    def _calculate_grammar_confidence(self, sentence: str) -> float:
        """
        Calculate confidence in grammar quality.
        
        Args:
            sentence: Sentence to analyze
            
        Returns:
            Grammar confidence score
        """
        if not sentence or not sentence.strip():
            return 0.0
        
        grammar_results = self._validate_grammar_structure(sentence)
        return grammar_results.get('grammar_score', 0.0)
    
    def _calculate_enhancement_confidence(self, sentence: str, metadata: Dict[str, Any]) -> float:
        """
        Calculate confidence in enhancement quality.
        
        Args:
            sentence: Enhanced sentence
            metadata: Enhancement metadata
            
        Returns:
            Enhancement confidence score
        """
        # Check for enhancement indicators
        confidence = 0.5  # Base confidence
        
        # Check if sentence appears well-enhanced
        if sentence and sentence.strip():
            # Proper capitalization
            if sentence[0].isupper():
                confidence += 0.1
            
            # Proper punctuation
            if sentence.rstrip().endswith(('.', '!', '?')):
                confidence += 0.1
            
            # No excessive spacing
            if '  ' not in sentence:
                confidence += 0.1
            
            # Reasonable length
            word_count = len(sentence.split())
            if 5 <= word_count <= 30:
                confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _calculate_translation_confidence(self, sentence: str) -> float:
        """
        Calculate confidence in translation readiness.
        
        Args:
            sentence: Sentence to analyze
            
        Returns:
            Translation confidence score
        """
        is_ready, issues = self.check_translation_readiness(sentence)
        
        if is_ready:
            return 1.0
        else:
            # Reduce confidence based on number of issues
            issue_penalty = len(issues) * 0.15
            return max(0.0, 1.0 - issue_penalty)
    
    def _check_medical_terminology(self, sentence: str) -> List[str]:
        """
        Check medical terminology usage.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            List of terminology issues
        """
        issues = []
        
        # Check for informal medical terms that should be standardized
        informal_terms = {
            'doc': 'doctor',
            'meds': 'medication',
            'scrip': 'prescription',
            'bp': 'blood pressure'
        }
        
        sentence_lower = sentence.lower()
        for informal, formal in informal_terms.items():
            if informal in sentence_lower:
                issues.append(f"Use '{formal}' instead of '{informal}'")
        
        return issues
    
    def _check_medical_context_consistency(self, sentence: str) -> List[str]:
        """
        Check medical context consistency.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            List of context issues
        """
        issues = []
        
        # This could be expanded with more sophisticated medical context checking
        # For now, basic consistency checks
        
        return issues
    
    def _check_medical_accuracy_patterns(self, sentence: str) -> List[str]:
        """
        Check for potential medical accuracy issues.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            List of potential accuracy issues
        """
        issues = []
        
        # This could be expanded with medical knowledge base validation
        # For now, basic pattern checking
        
        return issues
    
    def _is_complete_sentence_structure(self, sentence: str) -> bool:
        """
        Check if sentence has complete structure.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if complete structure
        """
        if not sentence or len(sentence.split()) < 3:
            return False
        
        # Check for basic sentence components
        words = sentence.lower().split()
        
        # Must have some verb indicators
        verbs = ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'can', 'should', 'would']
        has_verb = any(verb in words for verb in verbs)
        
        return has_verb
    
    def _is_complete_thought(self, sentence: str) -> bool:
        """
        Check if sentence expresses a complete thought.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if complete thought
        """
        if not sentence or len(sentence.split()) < 4:
            return False
        
        # Must have subject and predicate
        return self._is_complete_sentence_structure(sentence)
    
    def _has_clear_meaning(self, sentence: str) -> bool:
        """
        Check if sentence has clear meaning.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if meaning is clear
        """
        if not sentence or len(sentence.split()) < 3:
            return False
        
        # Check for meaningful content words
        words = sentence.lower().split()
        
        # Must have some content words (not just function words)
        function_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        content_words = [word for word in words if word not in function_words]
        
        return len(content_words) >= 2
    
    def _has_sufficient_context(self, sentence: str) -> bool:
        """
        Check if sentence has sufficient context.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if sufficient context
        """
        if not sentence:
            return False
        
        # Must have reasonable length and content
        words = sentence.split()
        return len(words) >= 5 and self._has_clear_meaning(sentence)
    
    def _has_consistent_medical_terminology(self, sentence: str) -> bool:
        """
        Check for consistent medical terminology.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            True if terminology is consistent
        """
        # Check for mixed formal/informal usage
        informal_indicators = ['doc', 'meds', 'scrip']
        formal_indicators = ['physician', 'medication', 'prescription']
        
        sentence_lower = sentence.lower()
        has_informal = any(term in sentence_lower for term in informal_indicators)
        has_formal = any(term in sentence_lower for term in formal_indicators)
        
        # Inconsistent if both formal and informal terms present
        return not (has_informal and has_formal)
    
    def _assign_quality_grade(self, sentence: str, metadata: Dict[str, Any]) -> str:
        """
        Assign quality grade to sentence.
        
        Args:
            sentence: Sentence to grade
            metadata: Processing metadata
            
        Returns:
            Quality grade (A, B, C, D, F)
        """
        confidence = self.calculate_confidence_score(sentence, metadata)
        
        if confidence >= 0.9:
            return 'A'
        elif confidence >= 0.8:
            return 'B'
        elif confidence >= 0.7:
            return 'C'
        elif confidence >= 0.6:
            return 'D'
        else:
            return 'F'
