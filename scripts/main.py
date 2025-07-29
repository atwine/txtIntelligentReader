#!/usr/bin/env python3
"""
txtIntelligentReader - Main Entry Point

A CrewAI-powered multi-agent text processing system that extracts high-quality,
translation-ready sentences from health domain text files.

Usage:
    python main.py input.txt --output output.txt --format json --verbose
"""

import argparse
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import Settings
from src.utils.logger import Logger


def main():
    """Main entry point for txtIntelligentReader."""
    parser = argparse.ArgumentParser(
        description="txtIntelligentReader - CrewAI Multi-Agent Text Processing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py input.txt
  python main.py input.txt --output results.txt --format json
  python main.py input.txt --verbose --health-threshold 0.8
  python main.py --batch input_folder/ --output output_folder/
        """
    )
    
    # Input arguments
    parser.add_argument('input', help='Input text file or directory for batch processing')
    parser.add_argument('--output', '-o', help='Output file or directory (default: auto-generated)')
    parser.add_argument('--format', '-f', choices=['text', 'json', 'markdown'], 
                       default='text', help='Output format (default: text)')
    
    # Processing options
    parser.add_argument('--batch', '-b', action='store_true', 
                       help='Process all files in input directory')
    parser.add_argument('--health-threshold', type=float, default=0.7,
                       help='Health domain relevance threshold (0.0-1.0, default: 0.7)')
    parser.add_argument('--quality-threshold', type=float, default=0.8,
                       help='Quality validation threshold (0.0-1.0, default: 0.8)')
    
    # Output options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--progress', '-p', action='store_true',
                       help='Show progress bar')
    parser.add_argument('--stats', '-s', action='store_true',
                       help='Show processing statistics')
    
    # Advanced options
    parser.add_argument('--ollama-model', default='llama3.1:8b',
                       help='Ollama model to use (default: llama3.1:8b)')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Maximum worker threads (default: 4)')
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = Logger(verbose=args.verbose)
    logger.info("Starting txtIntelligentReader...")
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        sys.exit(1)
    
    # Initialize settings
    settings = Settings(
        health_threshold=args.health_threshold,
        quality_threshold=args.quality_threshold,
        ollama_model=args.ollama_model,
        max_workers=args.max_workers,
        verbose=args.verbose,
        show_progress=args.progress,
        show_stats=args.stats
    )
    
    logger.info(f"Configuration: {settings}")
    
    # TODO: Implement main processing logic in Phase 2
    logger.info("Processing logic will be implemented in Phase 2")
    logger.info("txtIntelligentReader setup complete!")


if __name__ == "__main__":
    main()
