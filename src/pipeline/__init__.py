"""
Processing pipeline module for txtIntelligentReader

Contains the main processing pipeline that integrates all filtering layers
and provides a unified interface for text processing.
"""

from .text_processor import TextProcessor
from .filter_pipeline import FilterPipeline

__all__ = [
    'TextProcessor',
    'FilterPipeline'
]
