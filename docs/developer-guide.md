# 🛠️ Developer Guide

**Technical documentation for txtIntelligentReader development and extension**

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [API Reference](#api-reference)
4. [Extension Guidelines](#extension-guidelines)
5. [Development Setup](#development-setup)
6. [Testing Framework](#testing-framework)
7. [Contributing](#contributing)

## Architecture Overview

### System Design Principles

txtIntelligentReader follows a **modular, layered architecture** designed for:
- **Extensibility**: Easy addition of new filters and processors
- **Maintainability**: Clear separation of concerns
- **Testability**: Isolated components with defined interfaces
- **Performance**: Efficient processing pipeline
- **Reliability**: Comprehensive error handling and recovery

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     txtIntelligentReader                    │
├─────────────────────────────────────────────────────────────┤
│  CLI Interface (src/main.py)                               │
├─────────────────────────────────────────────────────────────┤
│  Text Processor (src/pipeline/text_processor.py)           │
├─────────────────────────────────────────────────────────────┤
│  Filter Pipeline (src/pipeline/filter_pipeline.py)         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ Quick Filter│ │Health Filter│ │ AI Analysis │ │Complete │ │
│  │   Layer 1   │ │   Layer 2   │ │   Layer 3   │ │Layer 4  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Utilities (src/utils/)                                     │
│  ├── Logger          ├── Output Formatter                   │
│  ├── Error Handler   ├── Configuration Loader              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Input Text File → Text Processor → Filter Pipeline → Output Formatter
                      ↓               ↓                    ↓
                 Sentence Split   4-Layer Filtering   Multi-Format Output
```

### Performance Characteristics

- **Processing Speed**: 150,000+ sentences per minute
- **Memory Usage**: <100KB per sentence
- **Scalability**: Linear scaling to 20,000+ sentences
- **Concurrency**: Thread-safe processing

## System Components

### Core Pipeline Components

#### TextProcessor (`src/pipeline/text_processor.py`)

**Purpose**: Main orchestrator for text processing workflow.

**Key Methods**:
```python
class TextProcessor:
    def __init__(self, config: Dict[str, Any] = None)
    def process_file(self, input_file: str, output_file: str = None, **kwargs) -> Dict[str, Any]
    def process_text(self, text: str, **kwargs) -> Dict[str, Any]
    def get_statistics(self) -> Dict[str, Any]
```

#### FilterPipeline (`src/pipeline/filter_pipeline.py`)

**Purpose**: Manages the 4-layer filtering process.

**Filter Chain**:
1. **QuickFilter**: Noise removal and basic cleaning
2. **HealthContextFilter**: Medical relevance scoring
3. **AIAnalysisFilter**: Completeness and quality analysis
4. **CompleteThoughtValidator**: Final validation

### Filter Components

#### Base Filter Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseFilter(ABC):
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.statistics = {}
    
    @abstractmethod
    def process(self, sentences: List[str]) -> List[str]:
        """Process sentences and return filtered results."""
        pass
    
    @abstractmethod
    def get_filter_name(self) -> str:
        """Return the filter name for identification."""
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Return processing statistics."""
        return self.statistics
```

#### Filter Implementations

**1. QuickFilter**: Remove obvious noise and formatting artifacts
**2. HealthContextFilter**: Identify and score medical relevance (200+ medical terms)
**3. AIAnalysisFilter**: Analyze sentence completeness and quality
**4. CompleteThoughtValidator**: Ensure complete, actionable thoughts

### Utility Components

**Logger**: Centralized logging with multiple output destinations
**OutputFormatter**: Multi-format output (txt/json/md/csv/html)
**ErrorHandler**: Comprehensive error handling and recovery
**ConfigLoader**: Configuration management and validation

## API Reference

### Core Classes

#### TextProcessor

```python
def process_file(self, 
                input_file: str, 
                output_file: str = None,
                health_threshold: float = 0.3,
                quality_threshold: float = 0.7,
                completeness_threshold: float = 0.6,
                output_format: str = "txt",
                include_stats: bool = False) -> Dict[str, Any]:
    """
    Process a text file through the filtering pipeline.
    
    Args:
        input_file: Path to input text file
        output_file: Path to output file (auto-generated if None)
        health_threshold: Health relevance threshold (0.0-1.0)
        quality_threshold: Quality threshold (0.0-1.0)
        completeness_threshold: Completeness threshold (0.0-1.0)
        output_format: Output format (txt/json/md/csv/html)
        include_stats: Include processing statistics
        
    Returns:
        Dict containing processing results and metadata
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ProcessingError: If processing fails
    """
```

#### FilterPipeline

```python
def process_sentences(self, sentences: List[str]) -> Dict[str, Any]:
    """
    Process sentences through all filter layers.
    
    Args:
        sentences: List of sentences to process
        
    Returns:
        Dict containing filtered sentences and statistics
    """
```

## Extension Guidelines

### Adding New Filters

#### 1. Create Filter Class

```python
# src/filters/my_custom_filter.py
from src.filters.base_filter import BaseFilter
from typing import List, Dict, Any

class MyCustomFilter(BaseFilter):
    """Custom filter for specific processing needs."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.threshold = config.get('threshold', 0.5)
        
    def process(self, sentences: List[str]) -> List[str]:
        """Process sentences with custom logic."""
        filtered_sentences = []
        
        for sentence in sentences:
            if self._should_keep_sentence(sentence):
                filtered_sentences.append(sentence)
                
        # Update statistics
        self.statistics = {
            'input_count': len(sentences),
            'output_count': len(filtered_sentences),
            'retention_rate': len(filtered_sentences) / len(sentences) * 100
        }
        
        return filtered_sentences
        
    def get_filter_name(self) -> str:
        return "MyCustomFilter"
        
    def _should_keep_sentence(self, sentence: str) -> bool:
        """Custom logic to determine if sentence should be kept."""
        # Implement your filtering logic here
        return True
```

#### 2. Register Filter in Pipeline

```python
# src/pipeline/filter_pipeline.py
from src.filters.my_custom_filter import MyCustomFilter

# Add to pipeline initialization
if config.get('enable_custom_filter', False):
    custom_config = config.get('custom_filter_config', {})
    self.filters.append(MyCustomFilter(custom_config))
```

#### 3. Add Tests

```python
# tests/test_my_custom_filter.py
import unittest
from src.filters.my_custom_filter import MyCustomFilter

class TestMyCustomFilter(unittest.TestCase):
    def setUp(self):
        self.filter = MyCustomFilter({'threshold': 0.5})
        
    def test_basic_filtering(self):
        sentences = ["Good sentence.", "Bad sentence."]
        result = self.filter.process(sentences)
        self.assertIsInstance(result, list)
        
    def test_statistics(self):
        sentences = ["Test sentence."]
        self.filter.process(sentences)
        stats = self.filter.get_statistics()
        self.assertIn('retention_rate', stats)
```

### Adding New Output Formats

```python
# src/utils/output_formatter.py
class OutputFormatter:
    def format_xml(self, data: Dict[str, Any]) -> str:
        """Format data as XML."""
        # Implementation here
        return xml_output
```

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool

### Development Environment

```bash
# 1. Clone repository
git clone <repository-url>
cd txtIntelligentReader

# 2. Create development environment
python -m venv dev_env
source dev_env/bin/activate  # Windows: dev_env\Scripts\activate

# 3. Install development dependencies
pip install -r requirements-dev.txt

# 4. Run tests to verify setup
python -m pytest tests/ -v
```

### Project Structure

```
txtIntelligentReader/
├── src/                          # Source code
│   ├── main.py                   # CLI entry point
│   ├── pipeline/                 # Core pipeline
│   │   ├── text_processor.py
│   │   └── filter_pipeline.py
│   ├── filters/                  # Filter implementations
│   │   ├── base_filter.py
│   │   ├── quick_filter.py
│   │   ├── health_context_filter.py
│   │   ├── ai_analysis_filter.py
│   │   └── complete_thought_validator.py
│   └── utils/                    # Utility modules
│       ├── logger.py
│       ├── output_formatter.py
│       ├── error_handler.py
│       └── config_loader.py
├── tests/                        # Test suite
├── docs/                         # Documentation
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
└── README.md
```

## Testing Framework

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end workflow testing
3. **Performance Tests**: Speed and memory benchmarks
4. **Quality Tests**: Output quality validation

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_filters_unit.py -v
python -m pytest tests/test_integration_comprehensive.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run performance tests
python tests/test_performance.py
```

### Writing Tests

#### Unit Test Example

```python
import unittest
from src.filters.my_custom_filter import MyCustomFilter

class TestMyCustomFilter(unittest.TestCase):
    def setUp(self):
        self.config = {'threshold': 0.5}
        self.filter = MyCustomFilter(self.config)
        
    def test_initialization(self):
        self.assertEqual(self.filter.threshold, 0.5)
        self.assertEqual(self.filter.get_filter_name(), "MyCustomFilter")
        
    def test_basic_processing(self):
        sentences = ["Good sentence.", "Another good sentence."]
        result = self.filter.process(sentences)
        
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), len(sentences))
        
    def test_statistics(self):
        sentences = ["Test sentence."]
        self.filter.process(sentences)
        stats = self.filter.get_statistics()
        
        self.assertIn('input_count', stats)
        self.assertIn('output_count', stats)
        self.assertIn('retention_rate', stats)
```

## Contributing

### Development Workflow

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/my-new-feature`
3. **Set Up Development Environment**
4. **Make Changes**: Follow code style guidelines, add tests, update docs
5. **Test Changes**: Run full test suite
6. **Submit Pull Request**: Include description of changes and test results

### Code Style Guidelines

- Follow **PEP 8** with Black formatting
- Use type hints for all public methods
- Write comprehensive docstrings
- Add unit tests for all new functionality
- Update documentation for user-facing changes

### Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Add entry to CHANGELOG.md
4. Request review from maintainers
5. Address feedback and make necessary changes

---

**Ready to contribute?** Check out our [Contributing Guide](CONTRIBUTING.md) for detailed instructions on setting up your development environment and submitting your first pull request!
