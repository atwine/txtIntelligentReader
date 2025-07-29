#!/usr/bin/env python3
"""
Configuration loader and management utilities.

Handles loading, validation, merging, and saving of configuration files
with support for environment variable overrides and default values.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from .logger import get_logger

logger = get_logger()


class ConfigLoader:
    """Configuration loader and manager."""
    
    def __init__(self):
        """Initialize ConfigLoader."""
        self.default_config = self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            # Filter thresholds
            'health_threshold': 0.3,
            'quality_threshold': 0.7,
            'completeness_threshold': 0.6,
            
            # Output settings
            'output_format': 'txt',
            'include_metadata': True,
            'include_statistics': True,
            
            # Processing settings
            'use_spacy': False,
            'llm_client': None,
            'batch_size': 100,
            'max_sentence_length': 1000,
            'min_sentence_length': 10,
            
            # Logging settings
            'enable_logging': True,
            'log_level': 'INFO',
            'log_file': 'txtintelligentreader.log',
            'enable_file_logging': True,
            
            # Performance settings
            'enable_progress_tracking': True,
            'enable_statistics': True,
            'enable_layer_tracking': True,
            
            # Error handling
            'debug_mode': False,
            'enable_error_recovery': True,
            'max_retry_attempts': 3,
            
            # Medical terminology
            'medical_terms_file': None,
            'custom_patterns_file': None,
            
            # Quality metrics
            'enable_quality_metrics': True,
            'readability_scoring': True,
            'medical_term_detection': True
        }
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file with environment variable overrides.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Loaded and merged configuration
        """
        try:
            # Start with default configuration
            config = self.default_config.copy()
            
            # Load from file if provided
            if config_path and Path(config_path).exists():
                file_config = self._load_config_file(config_path)
                if file_config:
                    config = self.merge_configs(config, file_config)
                    logger.info(f"Loaded configuration from {config_path}")
            
            # Apply environment variable overrides
            env_config = self._load_env_overrides()
            if env_config:
                config = self.merge_configs(config, env_config)
                logger.info("Applied environment variable overrides")
            
            # Validate final configuration
            if self.validate_config(config):
                logger.info("Configuration validation successful")
                return config
            else:
                logger.warning("Configuration validation failed, using defaults")
                return self.default_config.copy()
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.default_config.copy()
    
    def _load_config_file(self, config_path: str) -> Optional[Dict[str, Any]]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading config file {config_path}: {e}")
            return None
    
    def _load_env_overrides(self) -> Dict[str, Any]:
        """Load configuration overrides from environment variables."""
        env_config = {}
        env_prefix = "TXTIR_"
        
        # Define environment variable mappings
        env_mappings = {
            'TXTIR_HEALTH_THRESHOLD': ('health_threshold', float),
            'TXTIR_QUALITY_THRESHOLD': ('quality_threshold', float),
            'TXTIR_COMPLETENESS_THRESHOLD': ('completeness_threshold', float),
            'TXTIR_OUTPUT_FORMAT': ('output_format', str),
            'TXTIR_LOG_LEVEL': ('log_level', str),
            'TXTIR_DEBUG_MODE': ('debug_mode', self._str_to_bool),
            'TXTIR_USE_SPACY': ('use_spacy', self._str_to_bool),
            'TXTIR_ENABLE_LOGGING': ('enable_logging', self._str_to_bool),
            'TXTIR_BATCH_SIZE': ('batch_size', int),
            'TXTIR_MAX_SENTENCE_LENGTH': ('max_sentence_length', int),
            'TXTIR_MIN_SENTENCE_LENGTH': ('min_sentence_length', int)
        }
        
        for env_var, (config_key, converter) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = converter(os.environ[env_var])
                    env_config[config_key] = value
                    logger.debug(f"Environment override: {config_key} = {value}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid environment variable {env_var}: {e}")
        
        return env_config
    
    def _str_to_bool(self, value: str) -> bool:
        """Convert string to boolean."""
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration values.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if configuration is valid
        """
        try:
            # Validate thresholds
            thresholds = ['health_threshold', 'quality_threshold', 'completeness_threshold']
            for threshold in thresholds:
                if threshold in config:
                    value = config[threshold]
                    if not isinstance(value, (int, float)) or not 0 <= value <= 1:
                        logger.error(f"Invalid {threshold}: {value} (must be 0-1)")
                        return False
            
            # Validate output format
            if 'output_format' in config:
                valid_formats = ['txt', 'json', 'md', 'csv', 'html']
                if config['output_format'] not in valid_formats:
                    logger.error(f"Invalid output_format: {config['output_format']}")
                    return False
            
            # Validate log level
            if 'log_level' in config:
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if config['log_level'] not in valid_levels:
                    logger.error(f"Invalid log_level: {config['log_level']}")
                    return False
            
            # Validate numeric values
            numeric_fields = {
                'batch_size': (1, 10000),
                'max_sentence_length': (10, 10000),
                'min_sentence_length': (1, 1000),
                'max_retry_attempts': (0, 10)
            }
            
            for field, (min_val, max_val) in numeric_fields.items():
                if field in config:
                    value = config[field]
                    if not isinstance(value, int) or not min_val <= value <= max_val:
                        logger.error(f"Invalid {field}: {value} (must be {min_val}-{max_val})")
                        return False
            
            # Validate boolean fields
            boolean_fields = [
                'use_spacy', 'enable_logging', 'debug_mode', 'include_metadata',
                'include_statistics', 'enable_progress_tracking', 'enable_statistics',
                'enable_layer_tracking', 'enable_error_recovery', 'enable_quality_metrics',
                'readability_scoring', 'medical_term_detection', 'enable_file_logging'
            ]
            
            for field in boolean_fields:
                if field in config and not isinstance(config[field], bool):
                    logger.error(f"Invalid {field}: {config[field]} (must be boolean)")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation error: {e}")
            return False
    
    def merge_configs(self, base_config: Dict[str, Any], 
                     override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries.
        
        Args:
            base_config: Base configuration
            override_config: Override configuration
            
        Returns:
            Merged configuration
        """
        merged = base_config.copy()
        
        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                merged[key] = self.merge_configs(merged[key], value)
            else:
                # Override value
                merged[key] = value
        
        return merged
    
    def save_config(self, config: Dict[str, Any], output_path: str) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, sort_keys=True)
            
            logger.info(f"Configuration saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration to {output_path}: {e}")
            return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return self.default_config.copy()
    
    def create_sample_config(self, output_path: str) -> bool:
        """
        Create a sample configuration file with comments.
        
        Args:
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            sample_config = {
                "_comment": "txtIntelligentReader Configuration File",
                "_description": "Adjust these settings to customize text processing behavior",
                
                "filter_thresholds": {
                    "_comment": "Thresholds for filtering layers (0.0 to 1.0)",
                    "health_threshold": 0.3,
                    "quality_threshold": 0.7,
                    "completeness_threshold": 0.6
                },
                
                "output_settings": {
                    "_comment": "Output format and content settings",
                    "output_format": "txt",
                    "include_metadata": True,
                    "include_statistics": True
                },
                
                "processing_settings": {
                    "_comment": "Text processing configuration",
                    "use_spacy": False,
                    "batch_size": 100,
                    "max_sentence_length": 1000,
                    "min_sentence_length": 10
                },
                
                "logging_settings": {
                    "_comment": "Logging configuration",
                    "enable_logging": True,
                    "log_level": "INFO",
                    "log_file": "txtintelligentreader.log",
                    "enable_file_logging": True
                },
                
                "advanced_settings": {
                    "_comment": "Advanced processing options",
                    "debug_mode": False,
                    "enable_error_recovery": True,
                    "max_retry_attempts": 3,
                    "enable_quality_metrics": True
                }
            }
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2, sort_keys=False)
            
            logger.info(f"Sample configuration created at {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating sample configuration: {e}")
            return False
    
    def get_config_summary(self, config: Dict[str, Any]) -> str:
        """
        Generate a human-readable configuration summary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration summary string
        """
        summary_lines = [
            "📋 Configuration Summary",
            "=" * 50,
            "",
            "🎯 Filter Thresholds:",
            f"  • Health Context: {config.get('health_threshold', 'N/A')}",
            f"  • Quality: {config.get('quality_threshold', 'N/A')}",
            f"  • Completeness: {config.get('completeness_threshold', 'N/A')}",
            "",
            "📄 Output Settings:",
            f"  • Format: {config.get('output_format', 'N/A')}",
            f"  • Include Metadata: {config.get('include_metadata', 'N/A')}",
            f"  • Include Statistics: {config.get('include_statistics', 'N/A')}",
            "",
            "⚙️ Processing Settings:",
            f"  • Use spaCy: {config.get('use_spacy', 'N/A')}",
            f"  • Batch Size: {config.get('batch_size', 'N/A')}",
            f"  • Max Sentence Length: {config.get('max_sentence_length', 'N/A')}",
            "",
            "📝 Logging Settings:",
            f"  • Enabled: {config.get('enable_logging', 'N/A')}",
            f"  • Level: {config.get('log_level', 'N/A')}",
            f"  • File Logging: {config.get('enable_file_logging', 'N/A')}",
            "",
            "🔧 Advanced Settings:",
            f"  • Debug Mode: {config.get('debug_mode', 'N/A')}",
            f"  • Error Recovery: {config.get('enable_error_recovery', 'N/A')}",
            f"  • Quality Metrics: {config.get('enable_quality_metrics', 'N/A')}"
        ]
        
        return "\n".join(summary_lines)


# Convenience functions for common operations
def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration using default ConfigLoader."""
    loader = ConfigLoader()
    return loader.load_config(config_path)


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    loader = ConfigLoader()
    return loader.get_default_config()


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration."""
    loader = ConfigLoader()
    return loader.validate_config(config)


def create_sample_config(output_path: str) -> bool:
    """Create sample configuration file."""
    loader = ConfigLoader()
    return loader.create_sample_config(output_path)


if __name__ == "__main__":
    # Demo usage
    loader = ConfigLoader()
    
    # Create sample config
    sample_path = "sample_config.json"
    if loader.create_sample_config(sample_path):
        print(f"✅ Sample configuration created: {sample_path}")
    
    # Load and display config
    config = loader.load_config()
    print("\n" + loader.get_config_summary(config))
