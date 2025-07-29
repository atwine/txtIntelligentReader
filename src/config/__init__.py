"""
Configuration module for txtIntelligentReader

Contains configuration settings for Ollama, CrewAI, and health domain processing.
"""

from .settings import Settings
from .ollama_config import OllamaConfig
from .health_config import HealthConfig

__all__ = [
    'Settings',
    'OllamaConfig',
    'HealthConfig'
]
