# 🤝 Contributing Guide

**Welcome to txtIntelligentReader! We're excited to have you contribute.**

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Contribution Workflow](#contribution-workflow)
4. [Code Standards](#code-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Community Guidelines](#community-guidelines)

## Getting Started

### Ways to Contribute

We welcome contributions in many forms:

- **🐛 Bug Reports**: Found a bug? Let us know!
- **💡 Feature Requests**: Have an idea? We'd love to hear it!
- **📝 Documentation**: Help improve our docs
- **🔧 Code Contributions**: Fix bugs or add features
- **🧪 Testing**: Help improve test coverage
- **🎨 UI/UX**: Improve user experience
- **🌍 Translations**: Help make the project multilingual

### Before You Start

1. **Check existing issues**: Search for similar issues or feature requests
2. **Read the documentation**: Familiarize yourself with the project
3. **Join discussions**: Participate in issue discussions
4. **Start small**: Begin with small contributions to get familiar

## Development Setup

### Prerequisites

- **Python 3.8+**
- **Git**
- **Virtual environment tool** (venv, conda, etc.)

### Setup Instructions

```bash
# 1. Fork the repository on GitHub
# Click the "Fork" button on the repository page

# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/txtIntelligentReader.git
cd txtIntelligentReader

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/txtIntelligentReader.git

# 4. Create virtual environment
python -m venv dev_env
source dev_env/bin/activate  # Windows: dev_env\Scripts\activate

# 5. Install development dependencies
pip install -r requirements-dev.txt

# 6. Install pre-commit hooks
pre-commit install

# 7. Verify setup
python -m pytest tests/ -v
python src/main.py --help
```

### Development Dependencies

Create `requirements-dev.txt`:
```
# Core dependencies
-r requirements.txt

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.8.0

# Code quality
black>=22.0.0
flake8>=5.0.0
mypy>=0.991
isort>=5.10.0

# Development tools
pre-commit>=2.20.0
twine>=4.0.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0
```

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./dev_env/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## Contribution Workflow

### 1. Create Feature Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

### 2. Make Changes

- **Write code** following our style guidelines
- **Add tests** for new functionality
- **Update documentation** if needed
- **Run tests** to ensure everything works

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new medical term filter

- Add support for custom medical terminology
- Include configuration options for term weighting
- Add comprehensive tests for new functionality
- Update documentation with usage examples

Closes #123"
```

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```bash
feat: add XML output format support
fix: resolve memory leak in large file processing
docs: update installation guide for Windows
test: add integration tests for filter pipeline
refactor: simplify health context scoring algorithm
```

### 4. Push Changes

```bash
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Fill out the PR template
4. Request review from maintainers

## Code Standards

### Python Style Guide

We follow **PEP 8** with these specific guidelines:

#### Formatting

```python
# Use Black for automatic formatting
black src/ tests/

# Configuration in pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
```

#### Import Organization

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Third-party imports
import pytest

# Local imports
from src.pipeline.text_processor import TextProcessor
from src.filters.base_filter import BaseFilter
```

#### Naming Conventions

```python
# Classes: PascalCase
class TextProcessor:
    pass

# Functions and variables: snake_case
def process_sentences(input_sentences: List[str]) -> List[str]:
    filtered_results = []
    return filtered_results

# Constants: UPPER_SNAKE_CASE
MAX_SENTENCE_LENGTH = 500
DEFAULT_HEALTH_THRESHOLD = 0.3

# Private methods: leading underscore
def _internal_helper_method(self) -> None:
    pass
```

#### Type Hints

```python
from typing import Dict, List, Any, Optional, Union

def process_file(
    self,
    input_file: str,
    output_file: Optional[str] = None,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Process file with comprehensive type hints."""
    pass
```

#### Documentation

```python
def process_sentences(
    self, 
    sentences: List[str], 
    threshold: float = 0.5
) -> List[str]:
    """
    Process a list of sentences through the filtering pipeline.
    
    This method applies all configured filters in sequence to the input
    sentences, returning only those that meet the quality criteria.
    
    Args:
        sentences: List of sentences to process. Each sentence should be
            a complete string without newlines.
        threshold: Filtering threshold between 0.0 and 1.0. Higher values
            result in stricter filtering.
            
    Returns:
        List of filtered sentences that passed all quality checks.
        
    Raises:
        ValueError: If threshold is not between 0.0 and 1.0.
        ProcessingError: If processing fails due to malformed input.
        
    Example:
        >>> processor = TextProcessor()
        >>> sentences = ["Good medical sentence.", "Poor quality text."]
        >>> result = processor.process_sentences(sentences, 0.7)
        >>> len(result) <= len(sentences)
        True
        
    Note:
        The filtering process is destructive - sentences that don't meet
        the criteria are permanently removed from the result.
    """
```

### Error Handling

```python
# Define specific exception types
class ProcessingError(Exception):
    """Raised when text processing fails."""
    pass

class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass

# Proper exception handling
def process_file(self, input_file: str) -> Dict[str, Any]:
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = self._process_content(content)
        return result
        
    except FileNotFoundError as e:
        logger.error(f"Input file not found: {input_file}")
        raise ProcessingError(f"Cannot process file: {e}") from e
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error in file: {input_file}")
        raise ProcessingError(f"File encoding error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error processing {input_file}: {e}")
        raise ProcessingError(f"Processing failed: {e}") from e
```

### Logging

```python
import logging

# Use module-level logger
logger = logging.getLogger(__name__)

# Appropriate log levels with context
def process_sentences(self, sentences: List[str]) -> List[str]:
    logger.info(f"Processing {len(sentences)} sentences")
    
    try:
        filtered = self._apply_filters(sentences)
        logger.info(f"Retained {len(filtered)} sentences ({len(filtered)/len(sentences)*100:.1f}%)")
        return filtered
    except Exception as e:
        logger.error(f"Filter processing failed: {e}", exc_info=True)
        raise
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                     # Unit tests
│   ├── test_filters/
│   ├── test_pipeline/
│   └── test_utils/
├── integration/              # Integration tests
│   ├── test_end_to_end.py
│   └── test_cli_integration.py
├── performance/              # Performance tests
│   └── test_benchmarks.py
├── fixtures/                 # Test data
│   ├── sample_medical.txt
│   └── sample_config.json
└── conftest.py              # Pytest configuration
```

### Writing Tests

#### Unit Test Example

```python
import unittest
from unittest.mock import Mock, patch
from src.filters.health_context_filter import HealthContextFilter

class TestHealthContextFilter(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'health_threshold': 0.3,
            'medical_terms': ['diabetes', 'treatment']
        }
        self.filter = HealthContextFilter(self.config)
        
    def test_initialization(self):
        """Test filter initialization with config."""
        self.assertEqual(self.filter.health_threshold, 0.3)
        self.assertIn('diabetes', self.filter.medical_terms)
        
    def test_medical_sentence_processing(self):
        """Test processing of medical sentences."""
        sentences = [
            "The patient has diabetes and requires treatment.",
            "This is not a medical sentence."
        ]
        
        result = self.filter.process(sentences)
        
        # Should keep medical sentence
        self.assertIn("The patient has diabetes and requires treatment.", result)
        # May or may not keep non-medical sentence depending on threshold
        
    def test_empty_input(self):
        """Test handling of empty input."""
        result = self.filter.process([])
        self.assertEqual(result, [])
        
    def test_health_score_calculation(self):
        """Test health score calculation."""
        medical_sentence = "Patient diagnosed with diabetes"
        non_medical_sentence = "The weather is nice today"
        
        medical_score = self.filter.calculate_health_score(medical_sentence)
        non_medical_score = self.filter.calculate_health_score(non_medical_sentence)
        
        self.assertGreater(medical_score, non_medical_score)
        self.assertGreaterEqual(medical_score, 0.0)
        self.assertLessEqual(medical_score, 1.0)
        
    def test_statistics_generation(self):
        """Test statistics collection."""
        sentences = ["Medical sentence with diabetes.", "Non-medical sentence."]
        self.filter.process(sentences)
        
        stats = self.filter.get_statistics()
        
        self.assertIn('input_count', stats)
        self.assertIn('output_count', stats)
        self.assertIn('retention_rate', stats)
        self.assertEqual(stats['input_count'], 2)
        
    @patch('src.filters.health_context_filter.logger')
    def test_error_handling(self, mock_logger):
        """Test error handling and logging."""
        # Test with malformed input
        with self.assertRaises(Exception):
            self.filter.process(None)
            
        # Verify error was logged
        mock_logger.error.assert_called()
        
    def tearDown(self):
        """Clean up after tests."""
        pass
```

#### Integration Test Example

```python
import tempfile
import os
from pathlib import Path
from src.pipeline.text_processor import TextProcessor

class TestEndToEndProcessing(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = TextProcessor()
        
    def test_complete_workflow(self):
        """Test complete processing workflow."""
        # Create test input file
        input_file = Path(self.temp_dir) / "test_input.txt"
        input_file.write_text(
            "The patient presented with acute myocardial infarction.\n"
            "Treatment was initiated with aspirin and clopidogrel.\n"
            "PAGE 23\n"
            "Blood pressure was monitored continuously.\n"
            "FOOTER: Medical Center 2025\n"
        )
        
        # Process file
        output_file = Path(self.temp_dir) / "test_output.txt"
        result = self.processor.process_file(
            str(input_file),
            str(output_file),
            health_threshold=0.2,
            quality_threshold=0.5,
            include_stats=True
        )
        
        # Verify results
        self.assertTrue(output_file.exists())
        self.assertIn('filtered_sentences', result)
        self.assertIn('statistics', result)
        
        # Check that medical sentences were retained
        output_content = output_file.read_text()
        self.assertIn('myocardial infarction', output_content)
        self.assertIn('aspirin', output_content)
        
        # Check that artifacts were removed
        self.assertNotIn('PAGE 23', output_content)
        self.assertNotIn('FOOTER', output_content)
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
```

### Test Coverage

```bash
# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

**Coverage Goals**:
- **Unit tests**: >90% line coverage
- **Integration tests**: All major workflows
- **Critical paths**: 100% coverage for error handling

### Performance Testing

```python
import time
import tracemalloc
from src.pipeline.text_processor import TextProcessor

def test_processing_performance():
    """Test processing performance benchmarks."""
    # Generate test data
    sentences = ["The patient has diabetes and hypertension."] * 5000
    test_text = "\n".join(sentences)
    
    # Measure performance
    start_time = time.time()
    tracemalloc.start()
    
    processor = TextProcessor()
    result = processor.process_text(test_text)
    
    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Calculate metrics
    processing_time = end_time - start_time
    sentences_per_minute = (len(sentences) / processing_time) * 60
    memory_per_sentence = peak / len(sentences)
    
    # Performance assertions
    assert sentences_per_minute > 1000, f"Too slow: {sentences_per_minute:.0f} sentences/min"
    assert memory_per_sentence < 100000, f"Too much memory: {memory_per_sentence:.0f} bytes/sentence"
    
    print(f"Performance: {sentences_per_minute:.0f} sentences/min")
    print(f"Memory: {memory_per_sentence:.0f} bytes/sentence")
```

## Documentation

### Documentation Types

1. **Code Documentation**: Docstrings and inline comments
2. **User Documentation**: Installation, usage, tutorials
3. **Developer Documentation**: Architecture, API reference
4. **Process Documentation**: Contributing, release process

### Writing Guidelines

#### Docstrings

```python
def process_file(self, input_file: str, **kwargs) -> Dict[str, Any]:
    """
    Process a text file through the medical text filtering pipeline.
    
    This method reads a text file, splits it into sentences, and applies
    a series of filters to extract high-quality medical content suitable
    for translation or further processing.
    
    Args:
        input_file: Path to the input text file. Must be UTF-8 encoded.
        **kwargs: Additional processing options:
            - health_threshold (float): Medical relevance threshold (0.0-1.0)
            - quality_threshold (float): Quality threshold (0.0-1.0)
            - output_format (str): Output format ('txt', 'json', 'md', etc.)
            
    Returns:
        Dictionary containing:
            - 'filtered_sentences': List of processed sentences
            - 'statistics': Processing statistics and metrics
            - 'metadata': File and processing information
            
    Raises:
        FileNotFoundError: If the input file doesn't exist
        ProcessingError: If processing fails due to malformed content
        ConfigurationError: If configuration parameters are invalid
        
    Example:
        >>> processor = TextProcessor()
        >>> result = processor.process_file('medical_notes.txt')
        >>> print(f"Processed {len(result['filtered_sentences'])} sentences")
        
    Note:
        Large files (>50MB) should be processed in chunks for optimal
        memory usage. Consider using process_text() for batch processing.
    """
```

#### README Updates

When adding features, update the README:

```markdown
## New Feature: Custom Medical Terminology

You can now add custom medical terms to improve filtering accuracy:

```python
config = {
    "filters": {
        "health_context_filter": {
            "custom_medical_terms": [
                "myocardial infarction",
                "acute coronary syndrome",
                "percutaneous coronary intervention"
            ]
        }
    }
}

processor = TextProcessor(config)
```
```

## Pull Request Process

### PR Checklist

Before submitting a pull request, ensure:

- [ ] **Code follows style guidelines** (Black, flake8, mypy pass)
- [ ] **All tests pass** (`pytest tests/` succeeds)
- [ ] **New functionality has tests** (unit and integration)
- [ ] **Documentation is updated** (docstrings, README, etc.)
- [ ] **Commit messages follow convention** (Conventional Commits)
- [ ] **PR description is complete** (what, why, how)
- [ ] **Breaking changes are documented** (if any)

### PR Template

```markdown
## Description

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Changes Made

- List specific changes
- Include any new files or modules
- Mention configuration changes

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally
- [ ] Performance impact assessed

## Documentation

- [ ] Code comments updated
- [ ] Docstrings added/updated
- [ ] README updated (if needed)
- [ ] API documentation updated (if needed)

## Screenshots (if applicable)

Include screenshots for UI changes.

## Additional Notes

Any additional information for reviewers.
```

### Review Process

1. **Automated Checks**: CI runs tests and style checks
2. **Code Review**: Maintainers review code quality and design
3. **Testing**: Reviewers test functionality manually if needed
4. **Approval**: At least one maintainer approval required
5. **Merge**: Maintainer merges after all checks pass

## Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- **Be respectful** in all interactions
- **Be constructive** in feedback and discussions
- **Be patient** with new contributors
- **Be helpful** when others ask questions

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests, discussions
- **Pull Requests**: Code contributions and reviews
- **Discussions**: General questions and community chat

### Getting Help

- **Documentation**: Check existing docs first
- **Search Issues**: Look for similar problems/questions
- **Ask Questions**: Create an issue with the "question" label
- **Join Discussions**: Participate in community discussions

### Recognition

We appreciate all contributions! Contributors are recognized:

- **Contributors List**: Added to README
- **Release Notes**: Contributions mentioned in releases
- **Special Thanks**: Outstanding contributions highlighted

---

**Thank you for contributing to txtIntelligentReader! Your efforts help make medical text processing more accessible and effective for everyone.** 🚀

For questions about contributing, please create an issue or start a discussion. We're here to help!
