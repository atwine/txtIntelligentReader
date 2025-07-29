#!/usr/bin/env python3
"""
LLM Client Utilities for txtIntelligentReader

Provides utilities for initializing and managing LLM clients,
particularly Ollama for local inference.
"""

import logging
from typing import Optional, Dict, Any
from .logger import LoggerMixin


class LLMClientManager(LoggerMixin):
    """
    Manager for LLM client initialization and configuration.
    
    Supports Ollama and other LLM clients for AI analysis.
    """
    
    def __init__(self):
        """Initialize the LLM client manager."""
        pass
    
    def create_ollama_client(self, host: str = "http://localhost:11434", 
                           model: str = "llama3.1:8b") -> Optional[object]:
        """
        Create and configure an Ollama client.
        
        Args:
            host: Ollama server host URL
            model: Model name to use
            
        Returns:
            Ollama client instance or None if failed
        """
        try:
            import ollama
            
            # Create client
            client = ollama.Client(host=host)
            
            # Test connection by listing models
            try:
                self.log_info(f"Testing connection to Ollama at {host}")
                models = client.list()
                self.log_info(f"Raw models response: {models}")
                
                # Handle different response formats
                if isinstance(models, dict):
                    models_list = models.get('models', [])
                else:
                    models_list = models
                
                available_models = []
                for m in models_list:
                    if isinstance(m, dict):
                        # Try different possible keys for model name
                        model_name = m.get('name') or m.get('model') or m.get('id')
                        if model_name:
                            available_models.append(model_name)
                    else:
                        available_models.append(str(m))
                
                self.log_info(f"Available models: {available_models}")
                
                if model not in available_models:
                    self.log_warning(f"Model '{model}' not found. Available models: {available_models}")
                    if available_models:
                        # Prefer llama models, then deepseek, then any available
                        preferred_models = ['llama3.1:8b', 'llama3:8b', 'llama2:7b', 'deepseek-r1:1.5b']
                        selected_model = None
                        
                        for preferred in preferred_models:
                            if preferred in available_models:
                                selected_model = preferred
                                break
                        
                        if not selected_model:
                            selected_model = available_models[0]
                        
                        model = selected_model
                        self.log_info(f"Using available model: {model}")
                    else:
                        self.log_error("No models available in Ollama")
                        return None
                
                self.log_info(f"Ollama client initialized successfully with model: {model}")
                
                # Add model attribute to client for easy access
                client.default_model = model
                return client
                
            except Exception as e:
                self.log_error(f"Failed to connect to Ollama server at {host}: {str(e)}")
                self.log_info("Make sure Ollama is running: 'ollama serve'")
                return None
                
        except ImportError:
            self.log_error("Ollama package not installed. Install with: pip install ollama")
            return None
        except Exception as e:
            self.log_error(f"Failed to create Ollama client: {str(e)}")
            return None
    
    def create_client_from_config(self, config: Dict[str, Any]) -> Optional[object]:
        """
        Create LLM client from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            LLM client instance or None
        """
        client_type = config.get('llm_client_type', 'ollama').lower()
        
        if client_type == 'ollama':
            host = config.get('ollama_host', 'http://localhost:11434')
            model = config.get('ollama_model', 'llama3.1:8b')
            return self.create_ollama_client(host=host, model=model)
        else:
            self.log_error(f"Unsupported LLM client type: {client_type}")
            return None
    
    def test_client(self, client: object, test_prompt: str = "Hello, how are you?") -> bool:
        """
        Test if an LLM client is working properly.
        
        Args:
            client: LLM client to test
            test_prompt: Test prompt to send
            
        Returns:
            True if client is working, False otherwise
        """
        try:
            if hasattr(client, 'generate'):
                # Ollama client
                response = client.generate(
                    model=getattr(client, 'default_model', 'llama3.1:8b'),
                    prompt=test_prompt
                )
                return bool(response.get('response', '').strip())
            elif hasattr(client, 'chat'):
                # Chat-based client
                response = client.chat(
                    model=getattr(client, 'default_model', 'llama3.1:8b'),
                    messages=[{'role': 'user', 'content': test_prompt}]
                )
                return bool(response.get('message', {}).get('content', '').strip())
            else:
                # Generic callable client
                response = str(client(test_prompt))
                return bool(response.strip())
        except Exception as e:
            self.log_error(f"Client test failed: {str(e)}")
            return False


def create_llm_client(client_config: str = None, config: Dict[str, Any] = None) -> Optional[object]:
    """
    Convenience function to create an LLM client.
    
    Args:
        client_config: Client configuration string (e.g., "ollama:localhost:11434")
        config: Configuration dictionary
        
    Returns:
        LLM client instance or None
    """
    manager = LLMClientManager()
    
    if client_config:
        # Parse client configuration string
        parts = client_config.split(':')
        if len(parts) >= 1 and parts[0].lower() == 'ollama':
            host = f"http://{parts[1]}:{parts[2]}" if len(parts) >= 3 else "http://localhost:11434"
            model = parts[3] if len(parts) >= 4 else "llama3.1:8b"
            return manager.create_ollama_client(host=host, model=model)
    
    if config:
        return manager.create_client_from_config(config)
    
    # Default: try to create Ollama client
    return manager.create_ollama_client()
