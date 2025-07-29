"""
Filters module for txtIntelligentReader

Contains the 4-layer filtering system:
- QuickFilter: Remove obvious noise and formatting artifacts (Layer 1)
- HealthContextFilter: Identify medical/health terminology (Layer 2)  
- AIAnalysisFilter: Use LLM for completeness validation (Layer 3)
- CompleteThoughtValidator: Ensure proper structure (Layer 4)
"""

from .quick_filter import QuickFilter
from .health_context import HealthContextFilter
from .ai_analysis import AIAnalysisFilter
from .thought_validator import CompleteThoughtValidator

__all__ = [
    'QuickFilter',
    'HealthContextFilter',
    'AIAnalysisFilter', 
    'CompleteThoughtValidator'
]
