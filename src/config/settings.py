#!/usr/bin/env python3
"""
Configuration settings for txtIntelligentReader

Handles loading and managing configuration from files and environment variables.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Default configuration values
DEFAULT_CONFIG = {
    # Filtering thresholds
    'health_threshold': 0.3,
    'completeness_threshold': 0.6,
    'quality_threshold': 0.7,
    
    # Processing options
    'use_spacy': False,
    'batch_size': 100,
    'max_sentence_length': 500,
    'min_sentence_length': 10,
    
    # LLM configuration
    'llm_model': 'llama3.1:8b',
    'llm_host': 'http://localhost:11434',
    'llm_timeout': 30,
    'llm_batch_size': 5,
    
    # Output options
    'output_format': 'txt',
    'include_statistics': True,
    'save_intermediate_results': False,
    
    # Logging configuration
    'log_level': 'INFO',
    'log_to_file': True,
    'log_file': 'logs/txtintelligentreader.log',
    'verbose': False,
    
    # Performance settings
    'enable_multiprocessing': False,
    'max_workers': 4,
    'memory_limit_mb': 1024,
    
    # Filter-specific settings
    'quick_filter': {
        'enable_pdf_artifact_removal': True,
        'enable_header_footer_detection': True,
        'enable_formatting_cleanup': True
    },
    
    'health_filter': {
        'medical_terms_file': None,
        'custom_patterns_file': None,
        'strict_medical_only': False
    },
    
    'ai_filter': {
        'enable_batch_processing': True,
        'fallback_to_rules': True,
        'max_retries': 3
    },
    
    'thought_validator': {
        'enable_spacy_validation': False,
        'strict_grammar_check': False,
        'require_actionable_content': False
    }
}


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file and environment variables.
    
    Args:
        config_file: Path to configuration file (JSON)
        
    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    # Load from file if specified
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
                logging.info(f"Configuration loaded from: {config_file}")
        except Exception as e:
            logging.warning(f"Failed to load config file {config_file}: {e}")
    
    # Override with environment variables
    config = _load_env_overrides(config)
    
    # Validate configuration
    config = _validate_config(config)
    
    return config


def _load_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load configuration overrides from environment variables."""
    env_mappings = {
        'TXTIR_HEALTH_THRESHOLD': ('health_threshold', float),
        'TXTIR_COMPLETENESS_THRESHOLD': ('completeness_threshold', float),
        'TXTIR_QUALITY_THRESHOLD': ('quality_threshold', float),
        'TXTIR_USE_SPACY': ('use_spacy', _str_to_bool),
        'TXTIR_BATCH_SIZE': ('batch_size', int),
        'TXTIR_LLM_MODEL': ('llm_model', str),
        'TXTIR_LLM_HOST': ('llm_host', str),
        'TXTIR_LLM_TIMEOUT': ('llm_timeout', int),
        'TXTIR_LOG_LEVEL': ('log_level', str),
        'TXTIR_VERBOSE': ('verbose', _str_to_bool),
        'TXTIR_OUTPUT_FORMAT': ('output_format', str),
        'TXTIR_ENABLE_MULTIPROCESSING': ('enable_multiprocessing', _str_to_bool),
        'TXTIR_MAX_WORKERS': ('max_workers', int),
    }
    
    for env_var, (config_key, converter) in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            try:
                config[config_key] = converter(env_value)
                logging.debug(f"Environment override: {config_key} = {config[config_key]}")
            except (ValueError, TypeError) as e:
                logging.warning(f"Invalid environment variable {env_var}={env_value}: {e}")
    
    return config


def _str_to_bool(value: str) -> bool:
    """Convert string to boolean."""
    return value.lower() in ('true', '1', 'yes', 'on', 'enabled')


def _validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize configuration values."""
    # Validate thresholds
    for threshold_key in ['health_threshold', 'completeness_threshold', 'quality_threshold']:
        if not 0.0 <= config[threshold_key] <= 1.0:
            logging.warning(f"Invalid {threshold_key}: {config[threshold_key]}, using default")
            config[threshold_key] = DEFAULT_CONFIG[threshold_key]
    
    # Validate batch size
    if config['batch_size'] < 1:
        config['batch_size'] = DEFAULT_CONFIG['batch_size']
    
    # Validate sentence length limits
    if config['min_sentence_length'] < 1:
        config['min_sentence_length'] = DEFAULT_CONFIG['min_sentence_length']
    
    if config['max_sentence_length'] < config['min_sentence_length']:
        config['max_sentence_length'] = DEFAULT_CONFIG['max_sentence_length']
    
    # Validate output format
    if config['output_format'] not in ['txt', 'json']:
        config['output_format'] = DEFAULT_CONFIG['output_format']
    
    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if config['log_level'].upper() not in valid_log_levels:
        config['log_level'] = DEFAULT_CONFIG['log_level']
    
    # Validate multiprocessing settings
    if config['max_workers'] < 1:
        config['max_workers'] = DEFAULT_CONFIG['max_workers']
    
    return config


def save_config(config: Dict[str, Any], config_file: str):
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_file: Path to save configuration
    """
    try:
        # Create directory if it doesn't exist
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, sort_keys=True)
        
        logging.info(f"Configuration saved to: {config_file}")
    
    except Exception as e:
        logging.error(f"Failed to save configuration to {config_file}: {e}")
        raise


def create_default_config_file(config_file: str = "config.json"):
    """
    Create a default configuration file.
    
    Args:
        config_file: Path for the configuration file
    """
    save_config(DEFAULT_CONFIG, config_file)
    print(f"Default configuration created: {config_file}")


def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Get a configuration value with support for nested keys.
    
    Args:
        config: Configuration dictionary
        key: Configuration key (supports dot notation for nested keys)
        default: Default value if key not found
        
    Returns:
        Configuration value
    """
    keys = key.split('.')
    value = config
    
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default


def update_config_value(config: Dict[str, Any], key: str, value: Any):
    """
    Update a configuration value with support for nested keys.
    
    Args:
        config: Configuration dictionary
        key: Configuration key (supports dot notation for nested keys)
        value: New value
    """
    keys = key.split('.')
    current = config
    
    # Navigate to the parent dictionary
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    # Set the value
    current[keys[-1]] = value


def print_config(config: Dict[str, Any]):
    """Print configuration in a readable format."""
    print("Configuration Settings:")
    print("=" * 50)
    
    def print_dict(d: Dict[str, Any], indent: int = 0):
        for key, value in sorted(d.items()):
            if isinstance(value, dict):
                print("  " * indent + f"{key}:")
                print_dict(value, indent + 1)
            else:
                print("  " * indent + f"{key}: {value}")
    
    print_dict(config)
    print("=" * 50)


def validate_file_paths(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and resolve file paths in configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configuration with validated paths
    """
    file_keys = [
        'log_file',
        'health_filter.medical_terms_file',
        'health_filter.custom_patterns_file'
    ]
    
    for key in file_keys:
        file_path = get_config_value(config, key)
        if file_path:
            # Resolve relative paths
            resolved_path = Path(file_path).resolve()
            
            # Create parent directories if they don't exist
            if key == 'log_file':
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Update configuration with resolved path
            update_config_value(config, key, str(resolved_path))
    
    return config


# Configuration presets
PRESETS = {
    'strict': {
        'health_threshold': 0.5,
        'completeness_threshold': 0.8,
        'quality_threshold': 0.9,
        'thought_validator.strict_grammar_check': True,
        'thought_validator.require_actionable_content': True
    },
    
    'lenient': {
        'health_threshold': 0.2,
        'completeness_threshold': 0.4,
        'quality_threshold': 0.5,
        'ai_filter.fallback_to_rules': True
    },
    
    'fast': {
        'use_spacy': False,
        'ai_filter.enable_batch_processing': True,
        'llm_batch_size': 10,
        'enable_multiprocessing': True
    },
    
    'accurate': {
        'use_spacy': True,
        'ai_filter.max_retries': 5,
        'thought_validator.enable_spacy_validation': True,
        'llm_batch_size': 1
    }
}


def apply_preset(config: Dict[str, Any], preset_name: str) -> Dict[str, Any]:
    """
    Apply a configuration preset.
    
    Args:
        config: Base configuration
        preset_name: Name of preset to apply
        
    Returns:
        Configuration with preset applied
    """
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(PRESETS.keys())}")
    
    preset = PRESETS[preset_name]
    
    for key, value in preset.items():
        update_config_value(config, key, value)
    
    logging.info(f"Applied configuration preset: {preset_name}")
    return config
