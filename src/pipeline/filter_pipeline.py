#!/usr/bin/env python3
"""
Filter Pipeline for txtIntelligentReader

Integrates all 4 filtering layers into a unified processing pipeline
with comprehensive monitoring, statistics, and error handling.
"""

import time
from typing import List, Dict, Any, Optional, Callable
import logging
from pathlib import Path

from filters import QuickFilter, HealthContextFilter, AIAnalysisFilter, CompleteThoughtValidator
from utils.logger import LoggerMixin, log_layer_result, log_processing_start, log_processing_complete


class FilterPipeline(LoggerMixin):
    """
    Main processing pipeline that integrates all filtering layers.
    
    Provides a unified interface for processing text through the 4-layer
    filtering system with comprehensive monitoring and statistics.
    """
    
    def __init__(self, config: Dict[str, Any] = None, llm_client=None):
        """
        Initialize the filter pipeline.
        
        Args:
            config: Configuration dictionary
            llm_client: LLM client for AI analysis layer
        """
        self.config = config or {}
        self.llm_client = llm_client
        
        # Initialize all filters
        self._initialize_filters()
        
        # Pipeline statistics
        self.pipeline_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'total_input_sentences': 0,
            'total_output_sentences': 0,
            'overall_retention_rate': 0.0,
            'layer_performance': {
                'quick_filter': {'total_time': 0.0, 'avg_retention': 0.0},
                'health_filter': {'total_time': 0.0, 'avg_retention': 0.0},
                'ai_filter': {'total_time': 0.0, 'avg_retention': 0.0},
                'thought_validator': {'total_time': 0.0, 'avg_retention': 0.0}
            }
        }
    
    def _initialize_filters(self):
        """Initialize all filtering layers with configuration."""
        try:
            # Layer 1: Quick Filter
            self.quick_filter = QuickFilter()
            self.log_debug("QuickFilter initialized")
            
            # Layer 2: Health Context Filter
            health_threshold = self.config.get('health_threshold', 0.3)
            self.health_filter = HealthContextFilter(health_threshold=health_threshold)
            self.log_debug(f"HealthContextFilter initialized with threshold {health_threshold}")
            
            # Layer 3: AI Analysis Filter
            completeness_threshold = self.config.get('completeness_threshold', 0.6)
            self.ai_filter = AIAnalysisFilter(
                llm_client=self.llm_client,
                completeness_threshold=completeness_threshold
            )
            self.log_debug(f"AIAnalysisFilter initialized with threshold {completeness_threshold}")
            
            # Layer 4: Complete Thought Validator
            quality_threshold = self.config.get('quality_threshold', 0.7)
            use_spacy = self.config.get('use_spacy', False)
            self.thought_validator = CompleteThoughtValidator(
                quality_threshold=quality_threshold,
                use_spacy=use_spacy
            )
            self.log_debug(f"CompleteThoughtValidator initialized with threshold {quality_threshold}")
            
            self.log_info("All filtering layers initialized successfully")
            
        except Exception as e:
            self.log_error(f"Failed to initialize filters: {str(e)}")
            raise
    
    def process_sentences(self, sentences: List[str], 
                         layers: List[str] = None,
                         progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Process sentences through the filtering pipeline.
        
        Args:
            sentences: List of sentences to process
            layers: List of layer names to apply (default: all)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with processing results and statistics
        """
        start_time = time.time()
        layers = layers or self.config.get('layers', ['health'])
        
        self.log_info(f"Starting pipeline processing of {len(sentences)} sentences")
        self.log_info(f"Applying layers: {', '.join(layers)}")
        
        try:
            # Initialize processing state
            current_sentences = sentences.copy()
            layer_results = []
            
            # Process each layer
            for i, layer_name in enumerate(layers):
                layer_start_time = time.time()
                input_count = len(current_sentences)
                
                if progress_callback:
                    progress_callback(f"Applying {layer_name} filter...", i, len(layers))
                
                # Apply the layer
                current_sentences = self._apply_layer(layer_name, current_sentences)
                
                # Calculate layer statistics
                layer_time = time.time() - layer_start_time
                output_count = len(current_sentences)
                retention_rate = (output_count / input_count) if input_count > 0 else 0
                
                layer_result = {
                    'layer': layer_name,
                    'input_count': input_count,
                    'output_count': output_count,
                    'retention_rate': retention_rate,
                    'processing_time': layer_time
                }
                layer_results.append(layer_result)
                
                # Log layer result
                log_layer_result(layer_name.title() + " Filter", input_count, output_count, layer_time)
                
                # Update pipeline statistics
                self._update_layer_performance(layer_name, layer_time, retention_rate)
                
                # Break if no sentences remain
                if not current_sentences:
                    self.log_warning(f"No sentences remaining after {layer_name} filter")
                    break
            
            # Calculate overall statistics
            total_time = time.time() - start_time
            overall_retention = len(current_sentences) / len(sentences) if sentences else 0
            
            # Update pipeline statistics
            self._update_pipeline_stats(len(sentences), len(current_sentences), total_time, True)
            
            # Create result dictionary
            result = {
                'success': True,
                'input_sentences': len(sentences),
                'output_sentences': len(current_sentences),
                'filtered_sentences': current_sentences,
                'overall_retention_rate': overall_retention,
                'processing_time': total_time,
                'layers_applied': layers,
                'layer_results': layer_results,
                'filter_statistics': self._collect_filter_statistics()
            }
            
            self.log_info(f"Pipeline processing completed successfully")
            self.log_info(f"Results: {len(sentences)} → {len(current_sentences)} sentences ({overall_retention*100:.1f}% retained)")
            
            return result
            
        except Exception as e:
            self.log_error(f"Pipeline processing failed: {str(e)}")
            self._update_pipeline_stats(len(sentences), 0, time.time() - start_time, False)
            
            return {
                'success': False,
                'error': str(e),
                'input_sentences': len(sentences),
                'output_sentences': 0,
                'filtered_sentences': [],
                'processing_time': time.time() - start_time
            }
    
    def _apply_layer(self, layer_name: str, sentences: List[str]) -> List[str]:
        """
        Apply a specific filtering layer.
        
        Args:
            layer_name: Name of the layer to apply
            sentences: Input sentences
            
        Returns:
            Filtered sentences
        """
        try:
            if layer_name == 'quick':
                return self.quick_filter.filter_text(sentences)
            
            elif layer_name == 'health':
                return self.health_filter.filter_by_health_context(sentences)
            
            elif layer_name == 'ai':
                return self.ai_filter.filter_by_completeness(sentences)
            
            elif layer_name == 'thought':
                return self.thought_validator.filter_by_quality(sentences)
            
            else:
                raise ValueError(f"Unknown layer: {layer_name}")
                
        except Exception as e:
            self.log_error(f"Error applying {layer_name} layer: {str(e)}")
            raise
    
    def _update_layer_performance(self, layer_name: str, processing_time: float, retention_rate: float):
        """Update performance statistics for a specific layer."""
        layer_key = f"{layer_name}_filter"
        if layer_key in self.pipeline_stats['layer_performance']:
            perf = self.pipeline_stats['layer_performance'][layer_key]
            perf['total_time'] += processing_time
            
            # Update average retention rate
            runs = self.pipeline_stats['total_runs'] + 1
            current_avg = perf['avg_retention']
            perf['avg_retention'] = ((current_avg * (runs - 1)) + retention_rate) / runs
    
    def _update_pipeline_stats(self, input_count: int, output_count: int, 
                              processing_time: float, success: bool):
        """Update overall pipeline statistics."""
        self.pipeline_stats['total_runs'] += 1
        self.pipeline_stats['total_processing_time'] += processing_time
        self.pipeline_stats['total_input_sentences'] += input_count
        self.pipeline_stats['total_output_sentences'] += output_count
        
        if success:
            self.pipeline_stats['successful_runs'] += 1
        else:
            self.pipeline_stats['failed_runs'] += 1
        
        # Update averages
        total_runs = self.pipeline_stats['total_runs']
        self.pipeline_stats['average_processing_time'] = (
            self.pipeline_stats['total_processing_time'] / total_runs
        )
        
        if self.pipeline_stats['total_input_sentences'] > 0:
            self.pipeline_stats['overall_retention_rate'] = (
                self.pipeline_stats['total_output_sentences'] / 
                self.pipeline_stats['total_input_sentences']
            )
    
    def _collect_filter_statistics(self) -> Dict[str, Any]:
        """Collect detailed statistics from all filters."""
        return {
            'quick_filter': self.quick_filter.get_filtering_stats(),
            'health_filter': self.health_filter.get_filtering_stats(),
            'ai_filter': self.ai_filter.get_analysis_stats(),
            'thought_validator': self.thought_validator.get_validation_stats()
        }
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive pipeline statistics.
        
        Returns:
            Dictionary with pipeline performance statistics
        """
        return {
            'pipeline_stats': self.pipeline_stats.copy(),
            'filter_stats': self._collect_filter_statistics(),
            'configuration': {
                'health_threshold': self.config.get('health_threshold', 0.3),
                'completeness_threshold': self.config.get('completeness_threshold', 0.6),
                'quality_threshold': self.config.get('quality_threshold', 0.7),
                'use_spacy': self.config.get('use_spacy', False),
                'llm_enabled': self.llm_client is not None
            }
        }
    
    def reset_statistics(self):
        """Reset all pipeline and filter statistics."""
        self.pipeline_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'total_input_sentences': 0,
            'total_output_sentences': 0,
            'overall_retention_rate': 0.0,
            'layer_performance': {
                'quick_filter': {'total_time': 0.0, 'avg_retention': 0.0},
                'health_filter': {'total_time': 0.0, 'avg_retention': 0.0},
                'ai_filter': {'total_time': 0.0, 'avg_retention': 0.0},
                'thought_validator': {'total_time': 0.0, 'avg_retention': 0.0}
            }
        }
        
        # Reset individual filter statistics
        self.quick_filter.stats = {
            'total_processed': 0,
            'noise_removed': 0,
            'pdf_artifacts_removed': 0,
            'headers_footers_removed': 0,
            'formatting_removed': 0
        }
        
        self.health_filter.reset_stats()
        self.ai_filter.reset_stats()
        self.thought_validator.reset_stats()
        
        self.log_info("All pipeline and filter statistics reset")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current pipeline configuration.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Check thresholds
        health_threshold = self.config.get('health_threshold', 0.3)
        if not 0.0 <= health_threshold <= 1.0:
            validation_results['errors'].append(f"Invalid health_threshold: {health_threshold}")
            validation_results['valid'] = False
        
        completeness_threshold = self.config.get('completeness_threshold', 0.6)
        if not 0.0 <= completeness_threshold <= 1.0:
            validation_results['errors'].append(f"Invalid completeness_threshold: {completeness_threshold}")
            validation_results['valid'] = False
        
        quality_threshold = self.config.get('quality_threshold', 0.7)
        if not 0.0 <= quality_threshold <= 1.0:
            validation_results['errors'].append(f"Invalid quality_threshold: {quality_threshold}")
            validation_results['valid'] = False
        
        # Check for overly restrictive thresholds
        if health_threshold > 0.8:
            validation_results['warnings'].append("High health_threshold may filter out too many sentences")
        
        if completeness_threshold > 0.9:
            validation_results['warnings'].append("High completeness_threshold may be overly restrictive")
        
        if quality_threshold > 0.9:
            validation_results['warnings'].append("High quality_threshold may result in very few output sentences")
        
        # Check LLM availability
        if not self.llm_client:
            validation_results['warnings'].append("No LLM client configured - AI layer will use rule-based fallback")
        
        # Check spaCy availability
        if self.config.get('use_spacy', False):
            try:
                import spacy
                validation_results['recommendations'].append("spaCy is available for advanced NLP processing")
            except ImportError:
                validation_results['warnings'].append("spaCy requested but not available - using rule-based processing")
        
        return validation_results
    
    def get_layer_names(self) -> List[str]:
        """Get list of available layer names."""
        return ['quick', 'health', 'ai', 'thought']
    
    def get_layer_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all available layers."""
        return {
            'quick': 'Removes obvious noise, PDF artifacts, headers/footers, and formatting issues',
            'health': 'Filters for health/medical domain relevance using terminology and pattern matching',
            'ai': 'Uses LLM analysis to validate sentence completeness and meaning',
            'thought': 'Final validation for complete thoughts, structure, and translation readiness'
        }
    
    def estimate_processing_time(self, sentence_count: int, layers: List[str] = None) -> float:
        """
        Estimate processing time based on sentence count and layers.
        
        Args:
            sentence_count: Number of sentences to process
            layers: List of layers to apply
            
        Returns:
            Estimated processing time in seconds
        """
        layers = layers or ['quick', 'health', 'ai', 'thought']
        
        # Base estimates per sentence (in seconds)
        layer_estimates = {
            'quick': 0.0001,    # Very fast regex-based filtering
            'health': 0.0005,   # Medical terminology matching
            'ai': 0.01,         # LLM analysis (with batching)
            'thought': 0.001    # Rule-based validation
        }
        
        total_estimate = 0.0
        current_count = sentence_count
        
        # Estimate based on expected retention rates
        retention_rates = {
            'quick': 0.3,      # ~30% retention after noise removal
            'health': 0.4,     # ~40% of remaining after health filtering
            'ai': 0.7,         # ~70% of remaining after AI analysis
            'thought': 0.6     # ~60% of remaining after final validation
        }
        
        for layer in layers:
            if layer in layer_estimates:
                layer_time = current_count * layer_estimates[layer]
                total_estimate += layer_time
                
                # Update count for next layer
                if layer in retention_rates:
                    current_count = int(current_count * retention_rates[layer])
        
        return total_estimate
