#!/usr/bin/env python3
"""
txtIntelligentReader - Main CLI Application

A CrewAI-powered multi-agent text processing system for extracting 
high-quality, translation-ready sentences from health domain text files.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import json

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from pipeline import TextProcessor
from utils import FileHandler, setup_logging, ErrorHandler, handle_error, safe_execute
from config import load_config


class TxtIntelligentReader:
    """
    Main application class that orchestrates the 4-layer filtering system.
    """
    
    def __init__(self, config: Dict[str, Any] = None, llm_client=None):
        """
        Initialize the txtIntelligentReader with configuration.
        
        Args:
            config: Configuration dictionary
            llm_client: LLM client for AI analysis
        """
        self.config = config or {}
        self.text_processor = TextProcessor(config=config, llm_client=llm_client)
    
    def process_file(self, input_file: str, output_file: str = None, 
                    layers: List[str] = None, verbose: bool = False, 
                    output_format: str = 'txt') -> Dict[str, Any]:
        """
        Process a text file through the filtering pipeline.
        
        Args:
            input_file: Path to input text file
            output_file: Path to output file (optional)
            layers: List of layers to apply (default: all)
            verbose: Enable verbose logging
            output_format: Output format ('txt' or 'json')
            
        Returns:
            Dictionary with processing results and statistics
        """
        # Create progress callback for verbose mode
        progress_callback = None
        if verbose:
            def progress_callback(message, step, total):
                print(f"🔄 {message}")
        
        # Process using TextProcessor
        result = self.text_processor.process_file(
            input_file=input_file,
            output_file=output_file,
            layers=layers,
            output_format=output_format,
            progress_callback=progress_callback
        )
        
        if verbose and result.get('success', False):
            self._print_processing_summary(result)
        
        return result
    
    def _print_processing_summary(self, result: Dict[str, Any]):
        """Print a summary of processing results."""
        print("\n" + "=" * 60)
        print("📈 PROCESSING SUMMARY")
        print("=" * 60)
        
        stats = result.get('statistics', {})
        print(f"📄 Input sentences: {stats.get('input_sentences', 0)}")
        print(f"📄 Output sentences: {stats.get('output_sentences', 0)}")
        print(f"⏱️  Processing time: {result.get('metadata', {}).get('processing_time', 0):.3f}s")
        print(f"🎯 Overall retention rate: {stats.get('overall_retention_rate', 0)*100:.1f}%")
        
        layers_applied = result.get('metadata', {}).get('layers_applied', [])
        print(f"\n🔍 Layers applied: {', '.join(layers_applied)}")
        
        # Layer-by-layer breakdown
        layer_results = stats.get('layer_results', [])
        for layer_result in layer_results:
            layer_name = layer_result.get('layer', '').title() + " Filter"
            output_count = layer_result.get('output_count', 0)
            retention_rate = layer_result.get('retention_rate', 0)
            print(f"   {layer_name}: {output_count} sentences ({retention_rate*100:.1f}% retained)")
        
        print("=" * 60)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics."""
        return self.text_processor.get_processing_statistics()


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="txtIntelligentReader - Multi-agent text processing for health domain translation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a file with all filters
  python main.py input.txt -o output.txt
  
  # Process with specific layers only
  python main.py input.txt -o output.txt --layers quick health
  
  # Verbose processing with custom thresholds
  python main.py input.txt -o output.txt -v --health-threshold 0.4 --quality-threshold 0.8
  
  # Process multiple files
  python main.py file1.txt file2.txt -o results/ --batch
        """
    )
    
    # Input/Output arguments
    parser.add_argument('input_files', nargs='+', help='Input text file(s) to process')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('--batch', action='store_true', help='Process multiple files in batch mode')
    
    # Filtering options
    parser.add_argument('--layers', nargs='+', choices=['quick', 'health', 'ai', 'thought'],
                       default=['quick', 'health', 'ai', 'thought'],
                       help='Filtering layers to apply (default: all)')
    
    # Threshold configurations
    parser.add_argument('--health-threshold', type=float, default=0.3,
                       help='Health relevance threshold (default: 0.3)')
    parser.add_argument('--completeness-threshold', type=float, default=0.6,
                       help='AI completeness threshold (default: 0.6)')
    parser.add_argument('--quality-threshold', type=float, default=0.7,
                       help='Final quality threshold (default: 0.7)')
    
    # Processing options
    parser.add_argument('--use-spacy', action='store_true',
                       help='Use spaCy for advanced NLP (requires spacy installation)')
    parser.add_argument('--llm-client', help='LLM client configuration (for AI layer)')
    
    # Output options
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with detailed error information')
    parser.add_argument('--stats', action='store_true', help='Save detailed statistics')
    parser.add_argument('--format', choices=['txt', 'json', 'md', 'csv', 'html'], default='txt',
                       help='Output format: txt, json, md (markdown), csv, html (default: txt)')
    
    # Configuration
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level')
    parser.add_argument('--error-report', action='store_true', help='Generate error report at completion')
    
    return parser


def main():
    """Main entry point for the CLI application."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose, level=args.log_level)
    
    # Initialize error handler
    error_handler = ErrorHandler(debug_mode=args.debug)
    
    try:
        # Load configuration
        config = load_config(args.config) if args.config else {}
        
        # Override config with command line arguments
        config.update({
            'health_threshold': args.health_threshold,
            'completeness_threshold': args.completeness_threshold,
            'quality_threshold': args.quality_threshold,
            'use_spacy': args.use_spacy
        })
        
        # Initialize the reader
        reader = TxtIntelligentReader(config)
        
        if args.verbose:
            print("🚀 txtIntelligentReader - Multi-agent Text Processing System")
            print("=" * 60)
        
        # Process files
        results = []
        
        if args.batch and len(args.input_files) > 1:
            # Batch processing mode
            if args.verbose:
                print(f"📦 Batch processing {len(args.input_files)} files...")
            
            for i, input_file in enumerate(args.input_files, 1):
                if args.verbose:
                    print(f"\n📄 Processing file {i}/{len(args.input_files)}: {input_file}")
                
                # Determine output file
                if args.output:
                    if os.path.isdir(args.output):
                        output_file = os.path.join(args.output, f"processed_{os.path.basename(input_file)}")
                    else:
                        output_file = f"{args.output}_{i}.txt"
                else:
                    output_file = f"processed_{os.path.basename(input_file)}"
                
                result = reader.process_file(
                    input_file=input_file,
                    output_file=output_file,
                    layers=args.layers,
                    verbose=args.verbose,
                    output_format=args.format
                )
                results.append(result)
        
        else:
            # Single file processing
            input_file = args.input_files[0]
            output_file = args.output
            
            result = reader.process_file(
                input_file=input_file,
                output_file=output_file,
                layers=args.layers,
                verbose=args.verbose,
                output_format=args.format
            )
            results.append(result)
        
        # Save statistics if requested
        if args.stats:
            stats_file = "processing_stats.json"
            with open(stats_file, 'w') as f:
                json.dump({
                    'results': results,
                    'configuration': config,
                    'arguments': vars(args)
                }, f, indent=2)
            
            if args.verbose:
                print(f"📊 Statistics saved to: {stats_file}")
        
        # Final summary for batch processing
        if args.batch and len(results) > 1:
            total_input = sum(r['input_sentences'] for r in results)
            total_output = sum(r['output_sentences'] for r in results)
            total_time = sum(r['processing_time'] for r in results)
            
            print(f"\n🎉 BATCH PROCESSING COMPLETE")
            print(f"📄 Files processed: {len(results)}")
            print(f"📄 Total input sentences: {total_input}")
            print(f"📄 Total output sentences: {total_output}")
            print(f"⏱️  Total processing time: {total_time:.3f}s")
            print(f"🎯 Overall retention rate: {total_output/total_input*100:.1f}%")
        
        if args.verbose:
            print("\n✅ Processing completed successfully!")
        
        # Generate error report if requested
        if args.error_report:
            error_summary = error_handler.get_error_summary()
            if error_summary['total_errors'] > 0:
                report_path = error_handler.export_error_report()
                print(f"📋 Error report generated: {report_path}")
            else:
                print("📋 No errors to report")
    
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
        error_handler.handle_error(
            Exception("User interrupted processing"),
            {'context': 'main_execution', 'stage': 'user_interrupt'}
        )
        sys.exit(1)
    
    except Exception as e:
        # Use comprehensive error handling
        context = {
            'context': 'main_execution',
            'arguments': vars(args),
            'stage': 'unknown'
        }
        
        error_result = error_handler.handle_error(e, context)
        
        print(f"❌ Fatal Error [{error_result['error_id']}]: {str(e)}")
        print(f"   Category: {error_result['category']}")
        print(f"   Severity: {error_result['severity']}")
        
        if args.debug:
            print("\n🔍 Debug Information:")
            import traceback
            traceback.print_exc()
        
        # Generate error report for critical errors
        if error_result['severity'] in ['HIGH', 'CRITICAL']:
            report_path = error_handler.export_error_report()
            print(f"📋 Error report generated: {report_path}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
