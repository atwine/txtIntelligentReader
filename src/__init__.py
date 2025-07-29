"""
txtIntelligentReader - Advanced Medical Text Processing System

A sophisticated text processing system designed specifically for medical documents.
Uses a multi-layer filtering approach to extract high-quality, medically relevant
sentences from noisy text sources, making them ready for translation and further processing.

Key Features:
- 4-Layer Filtering Pipeline: Sequential noise removal and quality enhancement
- Medical Domain Specialization: Optimized for healthcare and medical content
- High Performance: Processes 150,000+ sentences per minute
- Multiple Output Formats: Text, JSON, Markdown, CSV, and HTML reports
- Offline Operation: No external API dependencies
- Comprehensive Testing: 100+ test scenarios with validation

Usage:
    from src.pipeline.text_processor import TextProcessor
    
    processor = TextProcessor()
    result = processor.process_file('medical_document.txt')
    print(f"Processed {len(result['filtered_sentences'])} sentences")

Author: txtIntelligentReader Team
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Atwine"
__description__ = "CrewAI Multi-Agent Text Processing System for Health Domain"
