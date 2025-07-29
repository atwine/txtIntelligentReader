#!/usr/bin/env python3
"""
Text Processor for txtIntelligentReader

High-level text processing interface that coordinates file handling,
pipeline processing, and output generation.
"""

import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable
import json

from .filter_pipeline import FilterPipeline
from utils.file_handler import FileHandler
from utils.output_formatter import OutputFormatter
from utils.logger import LoggerMixin, log_processing_start, log_processing_complete, ProgressLogger


class TextProcessor(LoggerMixin):
    """
    High-level text processor that coordinates the entire processing workflow.
    
    Handles file I/O, pipeline processing, batch operations, and output generation.
    """
    
    def __init__(self, config: Dict[str, Any] = None, llm_client=None):
        """
        Initialize the text processor.
        
        Args:
            config: Configuration dictionary
            llm_client: LLM client for AI analysis
        """
        self.config = config or {}
        self.file_handler = FileHandler()
        self.output_formatter = OutputFormatter()
        self.pipeline = FilterPipeline(config=config, llm_client=llm_client)
        
        # Processing statistics
        self.processing_stats = {
            'files_processed': 0,
            'total_input_sentences': 0,
            'total_output_sentences': 0,
            'total_processing_time': 0.0,
            'successful_files': 0,
            'failed_files': 0,
            'batch_operations': 0
        }
    
    def process_file(self, input_file: Union[str, Path], 
                    output_file: Union[str, Path] = None,
                    layers: List[str] = None,
                    output_format: str = 'txt',
                    progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Process a single text file through the filtering pipeline.
        
        Args:
            input_file: Path to input text file
            output_file: Path to output file (optional)
            layers: List of layers to apply
            output_format: Output format ('txt' or 'json')
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        input_path = Path(input_file)
        
        self.log_info(f"Processing file: {input_path}")
        
        try:
            # Validate input file
            if not self.file_handler.validate_input_file(input_path):
                raise ValueError(f"Invalid input file: {input_path}")
            
            # Load sentences from file
            if progress_callback:
                progress_callback("Loading input file...", 0, 4)
            
            sentences = self.file_handler.load_text_file(input_path)
            self.log_info(f"Loaded {len(sentences)} sentences from {input_path}")
            
            # Process through pipeline
            if progress_callback:
                progress_callback("Processing through filters...", 1, 4)
            
            pipeline_result = self.pipeline.process_sentences(
                sentences=sentences,
                layers=layers,
                progress_callback=lambda msg, step, total: progress_callback(f"Pipeline: {msg}", 1, 4) if progress_callback else None
            )
            
            if not pipeline_result['success']:
                raise Exception(f"Pipeline processing failed: {pipeline_result.get('error', 'Unknown error')}")
            
            # Prepare output
            if progress_callback:
                progress_callback("Preparing output...", 2, 4)
            
            output_data = self._prepare_output_data(
                input_file=input_path,
                pipeline_result=pipeline_result,
                processing_time=time.time() - start_time
            )
            
            # Save output if specified
            if output_file:
                if progress_callback:
                    progress_callback("Saving output file...", 3, 4)
                
                self._save_output(output_data, output_file, output_format)
                self.log_info(f"Results saved to: {output_file}")
            
            # Update statistics
            self._update_processing_stats(
                input_count=len(sentences),
                output_count=pipeline_result['output_sentences'],
                processing_time=time.time() - start_time,
                success=True
            )
            
            if progress_callback:
                progress_callback("Processing complete!", 4, 4)
            
            log_processing_complete(
                str(input_path),
                len(sentences),
                pipeline_result['output_sentences'],
                time.time() - start_time
            )
            
            return output_data
            
        except Exception as e:
            self.log_error(f"Failed to process file {input_path}: {str(e)}")
            self._update_processing_stats(0, 0, time.time() - start_time, False)
            
            return {
                'success': False,
                'error': str(e),
                'input_file': str(input_path),
                'processing_time': time.time() - start_time
            }
    
    def process_directory(self, input_dir: Union[str, Path],
                         output_dir: Union[str, Path] = None,
                         layers: List[str] = None,
                         output_format: str = 'txt',
                         file_pattern: str = '*.txt',
                         progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Process all text files in a directory.
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            layers: List of layers to apply
            output_format: Output format
            file_pattern: File pattern to match
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary with batch processing results
        """
        start_time = time.time()
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else input_path / 'processed'
        
        self.log_info(f"Processing directory: {input_path}")
        
        try:
            # Find input files
            input_files = list(input_path.glob(file_pattern))
            if not input_files:
                raise ValueError(f"No files found matching pattern '{file_pattern}' in {input_path}")
            
            self.log_info(f"Found {len(input_files)} files to process")
            
            # Create output directory
            self.file_handler.create_output_directory(output_path)
            
            # Process files
            results = []
            progress_logger = ProgressLogger(len(input_files), "Batch Processing")
            
            for i, input_file in enumerate(input_files):
                if progress_callback:
                    progress_callback(f"Processing {input_file.name}...", i, len(input_files))
                
                # Determine output file path
                output_file = output_path / f"processed_{input_file.name}"
                if output_format == 'json':
                    output_file = output_file.with_suffix('.json')
                
                # Process the file
                result = self.process_file(
                    input_file=input_file,
                    output_file=output_file,
                    layers=layers,
                    output_format=output_format
                )
                
                results.append(result)
                progress_logger.update()
            
            progress_logger.complete()
            
            # Calculate batch statistics
            batch_stats = self._calculate_batch_statistics(results)
            
            # Update processing statistics
            self.processing_stats['batch_operations'] += 1
            
            self.log_info(f"Batch processing completed: {len(input_files)} files processed")
            
            return {
                'success': True,
                'input_directory': str(input_path),
                'output_directory': str(output_path),
                'files_processed': len(input_files),
                'processing_time': time.time() - start_time,
                'batch_statistics': batch_stats,
                'file_results': results
            }
            
        except Exception as e:
            self.log_error(f"Batch processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_directory': str(input_path),
                'processing_time': time.time() - start_time
            }
    
    def process_text(self, text: str, layers: List[str] = None) -> Dict[str, Any]:
        """
        Process raw text directly (without file I/O).
        
        Args:
            text: Raw text to process
            layers: List of layers to apply
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        
        try:
            # Split text into sentences
            sentences = self.file_handler._split_into_sentences(text)
            self.log_debug(f"Split text into {len(sentences)} sentences")
            
            # Process through pipeline
            pipeline_result = self.pipeline.process_sentences(
                sentences=sentences,
                layers=layers
            )
            
            if not pipeline_result['success']:
                raise Exception(f"Pipeline processing failed: {pipeline_result.get('error', 'Unknown error')}")
            
            # Prepare result
            result = {
                'success': True,
                'input_sentences': len(sentences),
                'output_sentences': pipeline_result['output_sentences'],
                'filtered_sentences': pipeline_result['filtered_sentences'],
                'processing_time': time.time() - start_time,
                'pipeline_result': pipeline_result
            }
            
            return result
            
        except Exception as e:
            self.log_error(f"Text processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _prepare_output_data(self, input_file: Path, pipeline_result: Dict[str, Any], 
                           processing_time: float) -> Dict[str, Any]:
        """Prepare comprehensive output data."""
        return {
            'success': True,
            'metadata': {
                'input_file': str(input_file),
                'processing_time': processing_time,
                'timestamp': time.time(),
                'layers_applied': pipeline_result['layers_applied'],
                'configuration': self.pipeline.config
            },
            'statistics': {
                'input_sentences': pipeline_result['input_sentences'],
                'output_sentences': pipeline_result['output_sentences'],
                'overall_retention_rate': pipeline_result['overall_retention_rate'],
                'layer_results': pipeline_result['layer_results']
            },
            'results': {
                'filtered_sentences': pipeline_result['filtered_sentences']
            },
            'filter_statistics': pipeline_result['filter_statistics']
        }
    
    def _save_output(self, output_data: Dict[str, Any], output_file: Union[str, Path], 
                    output_format: str):
        """Save output data in the specified format using OutputFormatter."""
        output_path = Path(output_file)
        sentences = output_data['results']['filtered_sentences']
        metadata = output_data.get('metadata', {})
        
        # Validate output path and format
        if not self.output_formatter.validate_output_path(output_path, output_format.lower()):
            raise ValueError(f"Invalid output path or format: {output_path}, {output_format}")
        
        # Save using appropriate formatter method
        format_lower = output_format.lower()
        
        if format_lower == 'json':
            success = self.output_formatter.save_json(sentences, output_data, output_path)
        elif format_lower in ['md', 'markdown']:
            success = self.output_formatter.save_markdown_report(sentences, output_data, output_path)
        elif format_lower == 'csv':
            success = self.output_formatter.save_csv_statistics(output_data, output_path)
        elif format_lower in ['html', 'htm']:
            success = self.output_formatter.save_html_report(sentences, output_data, output_path)
        else:  # Default to text format
            success = self.output_formatter.save_text(sentences, output_path, metadata)
        
        if not success:
            raise Exception(f"Failed to save output in {output_format} format")
    
    def _update_processing_stats(self, input_count: int, output_count: int, 
                               processing_time: float, success: bool):
        """Update processing statistics."""
        self.processing_stats['files_processed'] += 1
        self.processing_stats['total_input_sentences'] += input_count
        self.processing_stats['total_output_sentences'] += output_count
        self.processing_stats['total_processing_time'] += processing_time
        
        if success:
            self.processing_stats['successful_files'] += 1
        else:
            self.processing_stats['failed_files'] += 1
    
    def _calculate_batch_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for batch processing."""
        successful_results = [r for r in results if r.get('success', False)]
        
        if not successful_results:
            return {
                'total_files': len(results),
                'successful_files': 0,
                'failed_files': len(results),
                'total_input_sentences': 0,
                'total_output_sentences': 0,
                'overall_retention_rate': 0.0,
                'average_processing_time': 0.0
            }
        
        total_input = sum(r['statistics']['input_sentences'] for r in successful_results)
        total_output = sum(r['statistics']['output_sentences'] for r in successful_results)
        total_time = sum(r['metadata']['processing_time'] for r in successful_results)
        
        return {
            'total_files': len(results),
            'successful_files': len(successful_results),
            'failed_files': len(results) - len(successful_results),
            'total_input_sentences': total_input,
            'total_output_sentences': total_output,
            'overall_retention_rate': total_output / total_input if total_input > 0 else 0.0,
            'average_processing_time': total_time / len(successful_results),
            'total_processing_time': total_time
        }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics."""
        return {
            'processor_stats': self.processing_stats.copy(),
            'pipeline_stats': self.pipeline.get_pipeline_statistics()
        }
    
    def reset_statistics(self):
        """Reset all processing statistics."""
        self.processing_stats = {
            'files_processed': 0,
            'total_input_sentences': 0,
            'total_output_sentences': 0,
            'total_processing_time': 0.0,
            'successful_files': 0,
            'failed_files': 0,
            'batch_operations': 0
        }
        
        self.pipeline.reset_statistics()
        self.log_info("All processing statistics reset")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate the current configuration."""
        return self.pipeline.validate_configuration()
    
    def estimate_processing_time(self, input_file: Union[str, Path], 
                               layers: List[str] = None) -> Dict[str, Any]:
        """
        Estimate processing time for a file.
        
        Args:
            input_file: Path to input file
            layers: List of layers to apply
            
        Returns:
            Dictionary with time estimates
        """
        try:
            # Get file info
            file_info = self.file_handler.get_file_info(input_file)
            
            # Estimate sentence count based on file size
            # Rough estimate: ~100 characters per sentence
            estimated_sentences = max(1, int(file_info['size_bytes'] / 100))
            
            # Get pipeline estimate
            pipeline_time = self.pipeline.estimate_processing_time(estimated_sentences, layers)
            
            # Add file I/O overhead
            io_overhead = 0.1  # 100ms for file operations
            
            total_estimate = pipeline_time + io_overhead
            
            return {
                'file_size_mb': file_info['size_mb'],
                'estimated_sentences': estimated_sentences,
                'pipeline_time_estimate': pipeline_time,
                'io_overhead': io_overhead,
                'total_time_estimate': total_estimate,
                'layers': layers or self.pipeline.get_layer_names()
            }
            
        except Exception as e:
            self.log_error(f"Failed to estimate processing time: {str(e)}")
            return {
                'error': str(e),
                'total_time_estimate': 1.0  # Default fallback
            }
