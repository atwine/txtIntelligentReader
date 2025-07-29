"""
Agents module for txtIntelligentReader

Contains all CrewAI agents for specialized text processing:
- ContentClassifierAgent: Document analysis and classification
- HealthDomainExpertAgent: Medical terminology expertise
- GrammarEnhancementAgent: Text quality improvement
- QualityValidationAgent: Final validation
- WorkflowCoordinatorAgent: Multi-agent orchestration
"""

from .content_classifier import ContentClassifierAgent
from .health_expert import HealthDomainExpertAgent
from .grammar_enhancer import GrammarEnhancementAgent
from .quality_validator import QualityValidationAgent
from .workflow_coordinator import WorkflowCoordinatorAgent

__all__ = [
    'ContentClassifierAgent',
    'HealthDomainExpertAgent', 
    'GrammarEnhancementAgent',
    'QualityValidationAgent',
    'WorkflowCoordinatorAgent'
]
