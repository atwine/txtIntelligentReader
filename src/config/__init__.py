"""
Configuration module for txtIntelligentReader

Contains configuration settings for Ollama, CrewAI, and health domain processing.
"""

from .settings import load_config, save_config, create_default_config_file

__all__ = [
    'load_config',
    'save_config',
    'create_default_config_file'
]
