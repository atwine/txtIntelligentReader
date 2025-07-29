#!/usr/bin/env python3
"""
File handling utilities for txtIntelligentReader

Provides comprehensive file I/O operations for text processing,
including loading, saving, and format conversion.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging
import re


class FileHandler:
    """
    Handles file operations for text processing.
    """
    
    def __init__(self):
        """Initialize the file handler."""
        self.logger = logging.getLogger(__name__)
    
    def load_text_file(self, file_path: str, encoding: str = 'utf-8') -> List[str]:
        """
        Load a text file and split into sentences.
        
        Args:
            file_path: Path to the text file
            encoding: File encoding (default: utf-8)
            
        Returns:
            List of sentences
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Split into sentences
            sentences = self._split_into_sentences(content)
            
            self.logger.info(f"Loaded {len(sentences)} sentences from {file_path}")
            return sentences
            
        except Exception as e:
            self.logger.error(f"Failed to load file {file_path}: {str(e)}")
            raise
    
    def save_text_file(self, sentences: List[str], file_path: str, 
                      encoding: str = 'utf-8', format_type: str = 'txt') -> None:
        """
        Save sentences to a text file.
        
        Args:
            sentences: List of sentences to save
            file_path: Output file path
            encoding: File encoding (default: utf-8)
            format_type: Output format ('txt' or 'json')
        """
        try:
            file_path = Path(file_path)
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type.lower() == 'json':
                # Save as JSON
                data = {
                    'sentences': sentences,
                    'count': len(sentences),
                    'format': 'txtIntelligentReader_output'
                }
                with open(file_path, 'w', encoding=encoding) as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            else:
                # Save as plain text
                with open(file_path, 'w', encoding=encoding) as f:
                    for sentence in sentences:
                        f.write(sentence.strip() + '\n')
            
            self.logger.info(f"Saved {len(sentences)} sentences to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save file {file_path}: {str(e)}")
            raise
    
    def load_json_file(self, file_path: str, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Load a JSON file.
        
        Args:
            file_path: Path to JSON file
            encoding: File encoding
            
        Returns:
            Parsed JSON data
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as f:
                data = json.load(f)
            
            self.logger.debug(f"Loaded JSON data from {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load JSON file {file_path}: {str(e)}")
            raise
    
    def save_json_file(self, data: Dict[str, Any], file_path: str, 
                      encoding: str = 'utf-8', indent: int = 2) -> None:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            file_path: Output file path
            encoding: File encoding
            indent: JSON indentation
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            self.logger.debug(f"Saved JSON data to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save JSON file {file_path}: {str(e)}")
            raise
    
    def load_lines_file(self, file_path: str, encoding: str = 'utf-8') -> List[str]:
        """
        Load a file as individual lines.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
            
        Returns:
            List of lines
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding=encoding) as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            self.logger.debug(f"Loaded {len(lines)} lines from {file_path}")
            return lines
            
        except Exception as e:
            self.logger.error(f"Failed to load lines from {file_path}: {str(e)}")
            raise
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File information dictionary
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = file_path.stat()
            
            return {
                'path': str(file_path.absolute()),
                'name': file_path.name,
                'size_bytes': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'modified_time': stat.st_mtime,
                'is_file': file_path.is_file(),
                'is_dir': file_path.is_dir(),
                'extension': file_path.suffix,
                'parent': str(file_path.parent)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {str(e)}")
            raise
    
    def validate_input_file(self, file_path: str) -> bool:
        """
        Validate that an input file is suitable for processing.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if file is valid
        """
        try:
            file_path = Path(file_path)
            
            # Check existence
            if not file_path.exists():
                self.logger.error(f"File does not exist: {file_path}")
                return False
            
            # Check if it's a file
            if not file_path.is_file():
                self.logger.error(f"Path is not a file: {file_path}")
                return False
            
            # Check file size (warn if too large)
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > 100:  # 100MB warning
                self.logger.warning(f"Large file detected ({size_mb:.1f}MB): {file_path}")
            
            # Check if file is readable
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1024)  # Read first 1KB to test
            except UnicodeDecodeError:
                self.logger.warning(f"File may not be UTF-8 encoded: {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"File validation failed for {file_path}: {str(e)}")
            return False
    
    def create_output_directory(self, output_path: str) -> Path:
        """
        Create output directory if it doesn't exist.
        
        Args:
            output_path: Output file or directory path
            
        Returns:
            Path object for the directory
        """
        try:
            path = Path(output_path)
            
            # If it's a file path, get the parent directory
            if path.suffix:
                directory = path.parent
            else:
                directory = path
            
            # Create directory
            directory.mkdir(parents=True, exist_ok=True)
            
            self.logger.debug(f"Created/verified output directory: {directory}")
            return directory
            
        except Exception as e:
            self.logger.error(f"Failed to create output directory: {str(e)}")
            raise
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using multiple methods.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Clean up text
        text = text.strip()
        if not text:
            return []
        
        # Basic sentence splitting patterns
        sentence_endings = r'[.!?]+(?:\s|$)'
        
        # Split on sentence endings
        sentences = re.split(sentence_endings, text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 3:  # Minimum sentence length
                # Remove excessive whitespace
                sentence = re.sub(r'\s+', ' ', sentence)
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def backup_file(self, file_path: str, backup_suffix: str = '.bak') -> str:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to the file to backup
            backup_suffix: Suffix for backup file
            
        Returns:
            Path to backup file
        """
        try:
            original_path = Path(file_path)
            backup_path = original_path.with_suffix(original_path.suffix + backup_suffix)
            
            if original_path.exists():
                # Copy file content
                with open(original_path, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                
                self.logger.info(f"Created backup: {backup_path}")
                return str(backup_path)
            else:
                raise FileNotFoundError(f"Original file not found: {original_path}")
                
        except Exception as e:
            self.logger.error(f"Failed to create backup of {file_path}: {str(e)}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return ['txt', 'json']
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding (basic implementation).
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding
        """
        try:
            # Try common encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        f.read(1024)  # Read first 1KB
                    return encoding
                except UnicodeDecodeError:
                    continue
            
            # Default fallback
            return 'utf-8'
            
        except Exception as e:
            self.logger.warning(f"Encoding detection failed for {file_path}: {str(e)}")
            return 'utf-8'
