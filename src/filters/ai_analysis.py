#!/usr/bin/env python3
"""
AI Analysis Filter (Layer 3) for txtIntelligentReader

This filter uses LLM for sentence completeness and meaning validation.
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
import time


class AIAnalysisFilter:
    """
    Third layer filter that uses LLM for sentence completeness and meaning validation.
    
    This filter handles:
    - Sentence completeness analysis
    - Meaning validation
    - Translation readiness assessment
    - Batch processing for efficiency
    - Response parsing and scoring
    """
    
    def __init__(self, llm_client=None, model: str = "llama3.1:8b", completeness_threshold: float = 0.6):
        """
        Initialize the AIAnalysisFilter with LLM client.
        
        Args:
            llm_client: LLM client instance (e.g., Ollama client)
            model: Model name to use for analysis
            completeness_threshold: Minimum completeness score to keep sentences
        """
        self.llm_client = llm_client
        self.model = model
        self.completeness_threshold = completeness_threshold
        
        # Analysis prompts
        self.completeness_prompt_template = self._create_completeness_prompt_template()
        self.meaning_prompt_template = self._create_meaning_prompt_template()
        self.batch_prompt_template = self._create_batch_prompt_template()
        
        # Statistics tracking
        self.stats = {
            'total_processed': 0,
            'llm_calls_made': 0,
            'complete_sentences': 0,
            'incomplete_sentences': 0,
            'meaningful_sentences': 0,
            'translation_ready': 0,
            'processing_time': 0.0,
            'average_completeness_score': 0.0,
            'average_meaning_score': 0.0
        }
    
    def analyze_completeness(self, sentence: str) -> Dict[str, Any]:
        """
        Analyze sentence completeness using LLM.
        
        Args:
            sentence: Sentence to analyze
            
        Returns:
            Dictionary with completeness analysis results
        """
        if not sentence or not sentence.strip():
            return {
                'completeness_score': 0.0,
                'is_complete': False,
                'reasoning': 'Empty or whitespace-only sentence',
                'has_subject': False,
                'has_predicate': False,
                'is_meaningful': False,
                'translation_ready': False
            }
        
        # If no LLM client, use rule-based analysis
        if not self.llm_client:
            return self._rule_based_completeness_analysis(sentence)
        
        try:
            start_time = time.time()
            
            # Create analysis prompt
            prompt = self.completeness_prompt_template.format(sentence=sentence.strip())
            
            # Make LLM call
            response = self._make_llm_call(prompt)
            self.stats['llm_calls_made'] += 1
            
            # Parse response
            analysis = self._parse_completeness_response(response, sentence)
            
            # Update timing stats
            self.stats['processing_time'] += time.time() - start_time
            
            return analysis
            
        except Exception as e:
            # Fallback to rule-based analysis on error
            return self._rule_based_completeness_analysis(sentence, error=str(e))
    
    def batch_analyze(self, sentences: List[str], batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Analyze multiple sentences efficiently using batch processing.
        
        Args:
            sentences: List of sentences to analyze
            batch_size: Number of sentences to process in each batch
            
        Returns:
            List of analysis results for each sentence
        """
        if not sentences:
            return []
        
        results = []
        self.stats['total_processed'] = len(sentences)
        
        # Process in batches for efficiency
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]
            
            if self.llm_client:
                batch_results = self._analyze_batch_with_llm(batch)
            else:
                batch_results = [self._rule_based_completeness_analysis(s) for s in batch]
            
            results.extend(batch_results)
            
            # Update statistics
            for result in batch_results:
                if result['is_complete']:
                    self.stats['complete_sentences'] += 1
                else:
                    self.stats['incomplete_sentences'] += 1
                
                if result['is_meaningful']:
                    self.stats['meaningful_sentences'] += 1
                
                if result['translation_ready']:
                    self.stats['translation_ready'] += 1
        
        # Calculate average scores
        if results:
            self.stats['average_completeness_score'] = sum(r['completeness_score'] for r in results) / len(results)
            self.stats['average_meaning_score'] = sum(r.get('meaning_score', 0) for r in results) / len(results)
        
        return results
    
    def filter_by_completeness(self, sentences: List[str], threshold: float = None) -> List[str]:
        """
        Filter sentences based on completeness analysis.
        
        Args:
            sentences: List of sentences to filter
            threshold: Override default completeness threshold
            
        Returns:
            Filtered list of complete sentences
        """
        if not sentences:
            return []
        
        threshold = threshold or self.completeness_threshold
        
        # Analyze all sentences
        analyses = self.batch_analyze(sentences)
        
        # Filter based on completeness
        filtered = []
        for sentence, analysis in zip(sentences, analyses):
            if analysis['completeness_score'] >= threshold and analysis['is_complete']:
                filtered.append(sentence)
        
        return filtered
    
    def _create_completeness_prompt_template(self) -> str:
        """Create prompt template for completeness analysis."""
        return """Analyze this sentence for completeness and meaning in the context of medical text translation:

Sentence: "{sentence}"

Please evaluate:
1. Is it a complete thought with subject and predicate?
2. Does it have clear meaning?
3. Is it suitable for translation?
4. Rate completeness from 0.0 to 1.0

Respond in JSON format:
{{
    "completeness_score": 0.0-1.0,
    "is_complete": true/false,
    "has_subject": true/false,
    "has_predicate": true/false,
    "is_meaningful": true/false,
    "translation_ready": true/false,
    "reasoning": "brief explanation"
}}"""
    
    def _create_meaning_prompt_template(self) -> str:
        """Create prompt template for meaning validation."""
        return """Evaluate the meaning and clarity of this sentence for medical translation:

Sentence: "{sentence}"

Rate the sentence on:
1. Clarity of meaning (0.0-1.0)
2. Medical relevance (0.0-1.0)
3. Translation suitability (0.0-1.0)

Respond in JSON format:
{{
    "meaning_score": 0.0-1.0,
    "clarity_score": 0.0-1.0,
    "medical_relevance": 0.0-1.0,
    "translation_suitability": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""
    
    def _create_batch_prompt_template(self) -> str:
        """Create prompt template for batch processing."""
        return """Analyze these sentences for completeness and meaning in medical translation context:

{sentences}

For each sentence, provide:
- completeness_score (0.0-1.0)
- is_complete (true/false)
- is_meaningful (true/false)
- translation_ready (true/false)

Respond in JSON array format:
[
    {{
        "sentence_index": 0,
        "completeness_score": 0.0-1.0,
        "is_complete": true/false,
        "is_meaningful": true/false,
        "translation_ready": true/false,
        "reasoning": "brief explanation"
    }}
]"""
    
    def _make_llm_call(self, prompt: str) -> str:
        """
        Make LLM call with error handling.
        
        Args:
            prompt: Prompt to send to LLM
            
        Returns:
            LLM response text
        """
        try:
            if hasattr(self.llm_client, 'generate'):
                # Ollama client
                response = self.llm_client.generate(model=self.model, prompt=prompt)
                return response.get('response', '')
            elif hasattr(self.llm_client, 'chat'):
                # Chat-based client
                response = self.llm_client.chat(
                    model=self.model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response.get('message', {}).get('content', '')
            else:
                # Generic callable client
                return str(self.llm_client(prompt))
        except Exception as e:
            raise Exception(f"LLM call failed: {str(e)}")
    
    def _parse_completeness_response(self, response: str, original_sentence: str) -> Dict[str, Any]:
        """
        Parse LLM response for completeness analysis.
        
        Args:
            response: Raw LLM response
            original_sentence: Original sentence being analyzed
            
        Returns:
            Parsed analysis results
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                analysis = json.loads(json_str)
                
                # Validate and normalize fields
                return {
                    'completeness_score': float(analysis.get('completeness_score', 0.0)),
                    'is_complete': bool(analysis.get('is_complete', False)),
                    'has_subject': bool(analysis.get('has_subject', False)),
                    'has_predicate': bool(analysis.get('has_predicate', False)),
                    'is_meaningful': bool(analysis.get('is_meaningful', False)),
                    'translation_ready': bool(analysis.get('translation_ready', False)),
                    'reasoning': str(analysis.get('reasoning', 'LLM analysis')),
                    'meaning_score': float(analysis.get('meaning_score', 0.0))
                }
            else:
                # Fallback parsing if no JSON found
                return self._fallback_response_parsing(response, original_sentence)
                
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback to rule-based analysis
            return self._rule_based_completeness_analysis(
                original_sentence, 
                error=f"Response parsing failed: {str(e)}"
            )
    
    def _fallback_response_parsing(self, response: str, sentence: str) -> Dict[str, Any]:
        """Fallback response parsing when JSON extraction fails."""
        response_lower = response.lower()
        
        # Simple keyword-based parsing
        is_complete = any(word in response_lower for word in ['complete', 'yes', 'true'])
        is_meaningful = any(word in response_lower for word in ['meaningful', 'clear', 'good'])
        
        # Estimate score based on keywords
        positive_words = ['complete', 'clear', 'good', 'meaningful', 'suitable']
        negative_words = ['incomplete', 'unclear', 'poor', 'meaningless', 'unsuitable']
        
        positive_count = sum(1 for word in positive_words if word in response_lower)
        negative_count = sum(1 for word in negative_words if word in response_lower)
        
        score = max(0.0, min(1.0, (positive_count - negative_count + 2) / 4))
        
        return {
            'completeness_score': score,
            'is_complete': is_complete,
            'has_subject': is_complete,
            'has_predicate': is_complete,
            'is_meaningful': is_meaningful,
            'translation_ready': is_complete and is_meaningful,
            'reasoning': 'Fallback parsing of LLM response',
            'meaning_score': score
        }
    
    def _rule_based_completeness_analysis(self, sentence: str, error: str = None) -> Dict[str, Any]:
        """
        Rule-based completeness analysis as fallback.
        
        Args:
            sentence: Sentence to analyze
            error: Optional error message
            
        Returns:
            Rule-based analysis results
        """
        if not sentence or not sentence.strip():
            return {
                'completeness_score': 0.0,
                'is_complete': False,
                'has_subject': False,
                'has_predicate': False,
                'is_meaningful': False,
                'translation_ready': False,
                'reasoning': error or 'Empty sentence',
                'meaning_score': 0.0
            }
        
        sentence = sentence.strip()
        words = sentence.split()
        
        # Basic completeness checks
        has_minimum_length = len(sentence) >= 10
        has_multiple_words = len(words) >= 3
        ends_properly = sentence.endswith(('.', '!', '?'))
        has_verb_indicators = any(word.lower() in ['is', 'was', 'are', 'were', 'has', 'have', 'had', 'will', 'would', 'can', 'could', 'should'] for word in words)
        
        # Calculate completeness score
        score_factors = [
            has_minimum_length,
            has_multiple_words,
            ends_properly,
            has_verb_indicators
        ]
        
        completeness_score = sum(score_factors) / len(score_factors)
        
        # Determine if complete
        is_complete = completeness_score >= 0.6
        is_meaningful = has_multiple_words and has_minimum_length
        translation_ready = is_complete and ends_properly
        
        reasoning = f"Rule-based analysis: {error}" if error else "Rule-based analysis (no LLM available)"
        
        return {
            'completeness_score': completeness_score,
            'is_complete': is_complete,
            'has_subject': has_multiple_words,
            'has_predicate': has_verb_indicators,
            'is_meaningful': is_meaningful,
            'translation_ready': translation_ready,
            'reasoning': reasoning,
            'meaning_score': completeness_score
        }
    
    def _analyze_batch_with_llm(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze a batch of sentences with LLM.
        
        Args:
            sentences: Batch of sentences to analyze
            
        Returns:
            List of analysis results
        """
        try:
            # Create batch prompt
            sentences_text = '\n'.join(f"{i+1}. {s}" for i, s in enumerate(sentences))
            prompt = self.batch_prompt_template.format(sentences=sentences_text)
            
            # Make LLM call
            response = self._make_llm_call(prompt)
            self.stats['llm_calls_made'] += 1
            
            # Parse batch response
            return self._parse_batch_response(response, sentences)
            
        except Exception as e:
            # Fallback to individual analysis
            return [self._rule_based_completeness_analysis(s, error=str(e)) for s in sentences]
    
    def _parse_batch_response(self, response: str, sentences: List[str]) -> List[Dict[str, Any]]:
        """Parse batch LLM response."""
        try:
            # Try to extract JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                batch_results = json.loads(json_str)
                
                # Process results
                results = []
                for i, sentence in enumerate(sentences):
                    if i < len(batch_results):
                        result = batch_results[i]
                        results.append({
                            'completeness_score': float(result.get('completeness_score', 0.0)),
                            'is_complete': bool(result.get('is_complete', False)),
                            'has_subject': bool(result.get('is_complete', False)),
                            'has_predicate': bool(result.get('is_complete', False)),
                            'is_meaningful': bool(result.get('is_meaningful', False)),
                            'translation_ready': bool(result.get('translation_ready', False)),
                            'reasoning': str(result.get('reasoning', 'Batch LLM analysis')),
                            'meaning_score': float(result.get('completeness_score', 0.0))
                        })
                    else:
                        # Fallback for missing results
                        results.append(self._rule_based_completeness_analysis(sentence))
                
                return results
            else:
                # Fallback if no JSON array found
                return [self._rule_based_completeness_analysis(s) for s in sentences]
                
        except (json.JSONDecodeError, ValueError, KeyError):
            # Fallback to rule-based analysis
            return [self._rule_based_completeness_analysis(s) for s in sentences]
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the AI analysis process.
        
        Returns:
            Dictionary containing AI analysis statistics
        """
        return {
            'total_processed': self.stats['total_processed'],
            'llm_calls_made': self.stats['llm_calls_made'],
            'complete_sentences': self.stats['complete_sentences'],
            'incomplete_sentences': self.stats['incomplete_sentences'],
            'completeness_rate': self.stats['complete_sentences'] / self.stats['total_processed'] if self.stats['total_processed'] > 0 else 0,
            'meaningful_sentences': self.stats['meaningful_sentences'],
            'translation_ready': self.stats['translation_ready'],
            'processing_time': self.stats['processing_time'],
            'average_processing_time': self.stats['processing_time'] / self.stats['llm_calls_made'] if self.stats['llm_calls_made'] > 0 else 0,
            'average_completeness_score': self.stats['average_completeness_score'],
            'average_meaning_score': self.stats['average_meaning_score'],
            'threshold_used': self.completeness_threshold
        }
    
    def reset_stats(self):
        """Reset analysis statistics."""
        self.stats = {
            'total_processed': 0,
            'llm_calls_made': 0,
            'complete_sentences': 0,
            'incomplete_sentences': 0,
            'meaningful_sentences': 0,
            'translation_ready': 0,
            'processing_time': 0.0,
            'average_completeness_score': 0.0,
            'average_meaning_score': 0.0
        }
