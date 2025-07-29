# 📚 API Reference

**Complete API documentation for txtIntelligentReader**

## Table of Contents

1. [Core Classes](#core-classes)
2. [Filter Classes](#filter-classes)
3. [Utility Classes](#utility-classes)
4. [Exception Classes](#exception-classes)
5. [Configuration Schema](#configuration-schema)
6. [Usage Examples](#usage-examples)

## Core Classes

### TextProcessor

**Module**: `src.pipeline.text_processor`

Main orchestrator for text processing workflow.

#### Constructor

```python
TextProcessor(config: Dict[str, Any] = None)
```

**Parameters**:
- `config` (Dict, optional): Configuration dictionary

#### Methods

##### process_file()

```python
process_file(
    input_file: str,
    output_file: str = None,
    health_threshold: float = 0.3,
    quality_threshold: float = 0.7,
    completeness_threshold: float = 0.6,
    output_format: str = "txt",
    include_stats: bool = False,
    debug: bool = False
) -> Dict[str, Any]
```

Process a text file through the filtering pipeline.

**Parameters**:
- `input_file` (str): Path to input text file
- `output_file` (str, optional): Path to output file (auto-generated if None)
- `health_threshold` (float): Health relevance threshold (0.0-1.0, default: 0.3)
- `quality_threshold` (float): Quality threshold (0.0-1.0, default: 0.7)
- `completeness_threshold` (float): Completeness threshold (0.0-1.0, default: 0.6)
- `output_format` (str): Output format ("txt", "json", "md", "csv", "html", default: "txt")
- `include_stats` (bool): Include processing statistics (default: False)
- `debug` (bool): Enable debug mode (default: False)

**Returns**:
- `Dict[str, Any]`: Processing results and metadata

**Raises**:
- `FileNotFoundError`: If input file doesn't exist
- `ProcessingError`: If processing fails
- `ConfigurationError`: If configuration is invalid

**Example**:
```python
from src.pipeline.text_processor import TextProcessor

processor = TextProcessor()
result = processor.process_file(
    "medical_document.txt",
    "processed_output.txt",
    health_threshold=0.2,
    quality_threshold=0.5,
    output_format="json",
    include_stats=True
)

print(f"Processed {result['statistics']['total_sentences']} sentences")
print(f"Retained {result['statistics']['retained_sentences']} sentences")
```

##### process_text()

```python
process_text(
    text: str,
    **kwargs
) -> Dict[str, Any]
```

Process raw text through the filtering pipeline.

**Parameters**:
- `text` (str): Raw text to process
- `**kwargs`: Same options as `process_file()`

**Returns**:
- `Dict[str, Any]`: Processing results and metadata

**Example**:
```python
text = "The patient has diabetes. Treatment was prescribed."
result = processor.process_text(text, health_threshold=0.2)
filtered_sentences = result['filtered_sentences']
```

##### get_statistics()

```python
get_statistics() -> Dict[str, Any]
```

Get processing statistics from the last operation.

**Returns**:
- `Dict[str, Any]`: Statistics dictionary

### FilterPipeline

**Module**: `src.pipeline.filter_pipeline`

Manages the multi-layer filtering process.

#### Constructor

```python
FilterPipeline(config: Dict[str, Any] = None)
```

#### Methods

##### process_sentences()

```python
process_sentences(sentences: List[str]) -> Dict[str, Any]
```

Process sentences through all filter layers.

**Parameters**:
- `sentences` (List[str]): List of sentences to process

**Returns**:
- `Dict[str, Any]`: Filtered sentences and statistics

##### add_filter()

```python
add_filter(filter_instance: BaseFilter, position: int = None) -> None
```

Add a filter to the pipeline.

**Parameters**:
- `filter_instance` (BaseFilter): Filter instance to add
- `position` (int, optional): Position in pipeline (None = append)

##### remove_filter()

```python
remove_filter(filter_name: str) -> None
```

Remove a filter from the pipeline by name.

**Parameters**:
- `filter_name` (str): Name of filter to remove

##### get_filter_statistics()

```python
get_filter_statistics() -> Dict[str, Any]
```

Get statistics for all filters in the pipeline.

**Returns**:
- `Dict[str, Any]`: Filter statistics

## Filter Classes

### BaseFilter

**Module**: `src.filters.base_filter`

Abstract base class for all filters.

#### Constructor

```python
BaseFilter(config: Dict[str, Any] = None)
```

#### Abstract Methods

##### process()

```python
@abstractmethod
def process(sentences: List[str]) -> List[str]
```

Process sentences and return filtered results.

##### get_filter_name()

```python
@abstractmethod
def get_filter_name() -> str
```

Return filter name for identification.

#### Methods

##### get_statistics()

```python
get_statistics() -> Dict[str, Any]
```

Return processing statistics.

### QuickFilter

**Module**: `src.filters.quick_filter`

Remove obvious noise and formatting artifacts.

#### Configuration Options

```python
{
    "min_length": 10,           # Minimum sentence length
    "max_length": 500,          # Maximum sentence length
    "remove_headers": True,     # Remove header patterns
    "remove_footers": True,     # Remove footer patterns
    "normalize_whitespace": True # Normalize whitespace
}
```

#### Methods

##### process()

```python
process(sentences: List[str]) -> List[str]
```

Filter sentences based on quick heuristics.

**Filtering Criteria**:
- Length-based filtering (min/max length)
- Header/footer pattern removal
- PDF artifact removal
- Whitespace normalization

### HealthContextFilter

**Module**: `src.filters.health_context_filter`

Identify and score medical relevance.

#### Configuration Options

```python
{
    "health_threshold": 0.3,    # Health relevance threshold
    "medical_terms": [...],     # Custom medical terms list
    "context_window": 5,        # Context analysis window
    "boost_medical_entities": True  # Boost medical entity scores
}
```

#### Methods

##### process()

```python
process(sentences: List[str]) -> List[str]
```

Filter sentences based on health domain relevance.

##### calculate_health_score()

```python
calculate_health_score(sentence: str) -> float
```

Calculate health relevance score (0.0-1.0).

**Scoring Factors**:
- Medical terminology frequency
- Health context patterns
- Medical entity recognition
- Domain-specific indicators

### AIAnalysisFilter

**Module**: `src.filters.ai_analysis_filter`

Analyze sentence completeness and quality.

#### Configuration Options

```python
{
    "quality_threshold": 0.7,       # Quality threshold
    "completeness_threshold": 0.6,  # Completeness threshold
    "grammar_weight": 0.3,          # Grammar score weight
    "coherence_weight": 0.4,        # Coherence score weight
    "completeness_weight": 0.3      # Completeness score weight
}
```

#### Methods

##### process()

```python
process(sentences: List[str]) -> List[str]
```

Filter sentences based on AI analysis.

##### analyze_completeness()

```python
analyze_completeness(sentence: str) -> float
```

Analyze sentence completeness (0.0-1.0).

##### analyze_grammar()

```python
analyze_grammar(sentence: str) -> float
```

Analyze grammatical correctness (0.0-1.0).

##### analyze_coherence()

```python
analyze_coherence(sentence: str) -> float
```

Analyze semantic coherence (0.0-1.0).

### CompleteThoughtValidator

**Module**: `src.filters.complete_thought_validator`

Ensure sentences express complete, actionable thoughts.

#### Configuration Options

```python
{
    "completeness_threshold": 0.6,  # Completeness threshold
    "require_subject": True,        # Require subject identification
    "require_predicate": True,      # Require predicate identification
    "check_actionability": True     # Check for actionable content
}
```

#### Methods

##### process()

```python
process(sentences: List[str]) -> List[str]
```

Validate sentences for complete thoughts.

##### validate_complete_thought()

```python
validate_complete_thought(sentence: str) -> bool
```

Validate if sentence expresses a complete thought.

**Validation Criteria**:
- Subject-predicate structure
- Semantic completeness
- Actionability assessment
- Translation readiness

## Utility Classes

### Logger

**Module**: `src.utils.logger`

Centralized logging system.

#### Methods

##### setup_logging()

```python
setup_logging(
    level: str = "INFO",
    log_file: str = None,
    console_output: bool = True
) -> None
```

Setup logging configuration.

##### log_function_call()

```python
log_function_call(
    func_name: str,
    args: Dict,
    result: Any
) -> None
```

Log function calls for debugging.

##### log_performance()

```python
log_performance(
    operation: str,
    duration: float,
    details: Dict
) -> None
```

Log performance metrics.

### OutputFormatter

**Module**: `src.utils.output_formatter`

Multi-format output generation.

#### Methods

##### format_text()

```python
format_text(data: Dict[str, Any]) -> str
```

Format data as plain text.

##### format_json()

```python
format_json(data: Dict[str, Any]) -> str
```

Format data as JSON.

##### format_markdown()

```python
format_markdown(data: Dict[str, Any]) -> str
```

Format data as Markdown.

##### format_csv()

```python
format_csv(data: Dict[str, Any]) -> str
```

Format data as CSV.

##### format_html()

```python
format_html(data: Dict[str, Any]) -> str
```

Format data as HTML.

### ErrorHandler

**Module**: `src.utils.error_handler`

Comprehensive error handling and recovery.

#### Methods

##### handle_processing_error()

```python
handle_processing_error(
    error: Exception,
    context: Dict
) -> None
```

Handle processing errors with context.

##### recover_from_filter_failure()

```python
recover_from_filter_failure(
    filter_name: str,
    sentences: List[str]
) -> List[str]
```

Recover from filter failures.

##### generate_error_report()

```python
generate_error_report(errors: List[Dict]) -> str
```

Generate comprehensive error report.

### ConfigLoader

**Module**: `src.utils.config_loader`

Configuration management and validation.

#### Methods

##### load_config()

```python
load_config(config_path: str = None) -> Dict[str, Any]
```

Load configuration from file or defaults.

##### validate_config()

```python
validate_config(config: Dict) -> bool
```

Validate configuration structure and values.

##### merge_configs()

```python
merge_configs(base: Dict, override: Dict) -> Dict
```

Merge configuration dictionaries.

##### get_env_overrides()

```python
get_env_overrides() -> Dict[str, Any]
```

Get configuration overrides from environment variables.

## Exception Classes

### ProcessingError

**Module**: `src.utils.error_handler`

Raised when text processing fails.

```python
class ProcessingError(Exception):
    """Raised when text processing fails."""
    pass
```

### ConfigurationError

**Module**: `src.utils.error_handler`

Raised when configuration is invalid.

```python
class ConfigurationError(Exception):
    """Raised when configuration is invalid."""
    pass
```

### FilterError

**Module**: `src.utils.error_handler`

Raised when filter processing fails.

```python
class FilterError(Exception):
    """Raised when filter processing fails."""
    pass
```

## Configuration Schema

### Default Configuration

```python
DEFAULT_CONFIG = {
    "thresholds": {
        "health_threshold": 0.3,
        "quality_threshold": 0.7,
        "completeness_threshold": 0.6
    },
    "filters": {
        "quick_filter": {
            "min_length": 10,
            "max_length": 500,
            "remove_headers": True,
            "remove_footers": True,
            "normalize_whitespace": True
        },
        "health_context_filter": {
            "medical_terms": [],  # Custom terms (empty = use defaults)
            "context_window": 5,
            "boost_medical_entities": True
        },
        "ai_analysis_filter": {
            "grammar_weight": 0.3,
            "coherence_weight": 0.4,
            "completeness_weight": 0.3
        },
        "complete_thought_validator": {
            "require_subject": True,
            "require_predicate": True,
            "check_actionability": True
        }
    },
    "output": {
        "default_format": "txt",
        "include_metadata": True,
        "include_statistics": False
    },
    "logging": {
        "level": "INFO",
        "enable_file_logging": True,
        "log_file": "logs/txtintelligentreader.log"
    },
    "processing": {
        "enable_error_recovery": True,
        "max_sentence_length": 1000,
        "min_sentence_length": 5,
        "batch_size": 1000
    }
}
```

### Environment Variable Overrides

Environment variables can override configuration values:

```bash
# Threshold overrides
export TXTIR_HEALTH_THRESHOLD=0.2
export TXTIR_QUALITY_THRESHOLD=0.5
export TXTIR_COMPLETENESS_THRESHOLD=0.4

# Output overrides
export TXTIR_OUTPUT_FORMAT=json
export TXTIR_INCLUDE_STATS=true

# Logging overrides
export TXTIR_LOG_LEVEL=DEBUG
export TXTIR_DEBUG_MODE=true
```

## Usage Examples

### Basic Usage

```python
from src.pipeline.text_processor import TextProcessor

# Initialize processor
processor = TextProcessor()

# Process file with default settings
result = processor.process_file("medical_document.txt")
print(f"Processed {len(result['filtered_sentences'])} sentences")
```

### Advanced Configuration

```python
# Custom configuration
config = {
    "thresholds": {
        "health_threshold": 0.2,
        "quality_threshold": 0.5,
        "completeness_threshold": 0.4
    },
    "output": {
        "default_format": "json",
        "include_statistics": True
    }
}

processor = TextProcessor(config)
result = processor.process_file(
    "input.txt",
    "output.json",
    output_format="json",
    include_stats=True
)
```

### Custom Filter Integration

```python
from src.pipeline.filter_pipeline import FilterPipeline
from src.filters.my_custom_filter import MyCustomFilter

# Create pipeline with custom filter
pipeline = FilterPipeline()
custom_filter = MyCustomFilter({"threshold": 0.6})
pipeline.add_filter(custom_filter, position=2)  # Insert at position 2

# Process sentences
sentences = ["Medical sentence.", "Non-medical sentence."]
result = pipeline.process_sentences(sentences)
```

### Programmatic Integration

```python
import json
from src.pipeline.text_processor import TextProcessor

def process_medical_documents(input_files, output_dir):
    """Process multiple medical documents."""
    processor = TextProcessor()
    results = []
    
    for input_file in input_files:
        try:
            result = processor.process_file(
                input_file,
                f"{output_dir}/{input_file.stem}_processed.json",
                health_threshold=0.15,
                quality_threshold=0.5,
                output_format="json",
                include_stats=True
            )
            results.append({
                "file": input_file,
                "status": "success",
                "sentences_retained": result["statistics"]["retained_sentences"],
                "retention_rate": result["statistics"]["retention_rate"]
            })
        except Exception as e:
            results.append({
                "file": input_file,
                "status": "error",
                "error": str(e)
            })
    
    return results

# Usage
input_files = ["doc1.txt", "doc2.txt", "doc3.txt"]
results = process_medical_documents(input_files, "output/")
print(json.dumps(results, indent=2))
```

### Error Handling

```python
from src.pipeline.text_processor import TextProcessor
from src.utils.error_handler import ProcessingError, ConfigurationError

processor = TextProcessor()

try:
    result = processor.process_file(
        "medical_document.txt",
        health_threshold=0.2,
        quality_threshold=0.5
    )
except FileNotFoundError as e:
    print(f"Input file not found: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except ProcessingError as e:
    print(f"Processing failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

**This API reference provides complete documentation for all public interfaces in txtIntelligentReader. For usage examples and tutorials, see the [User Guide](user-guide.md) and [Developer Guide](developer-guide.md).**
