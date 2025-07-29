# 📖 txtIntelligentReader User Guide

**Complete Guide to Medical Text Processing with Multi-Layer Filtering**

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Advanced Configuration](#advanced-configuration)
4. [Output Formats](#output-formats)
5. [Performance Tuning](#performance-tuning)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Getting Started

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended for large files)
- **Storage**: 1GB free space for processing and logs
- **OS**: Windows, macOS, or Linux

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd txtIntelligentReader
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv txtir_env
   
   # Windows
   txtir_env\Scripts\activate
   
   # macOS/Linux
   source txtir_env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**
   ```bash
   python src/main.py --help
   ```

### First Run

Test the system with a sample medical text:

```bash
# Create a sample input file
echo "The patient presented with acute myocardial infarction. Treatment was initiated immediately with aspirin and clopidogrel." > sample_medical.txt

# Process the file
python src/main.py sample_medical.txt -o processed_output.txt --stats

# View the results
cat processed_output.txt
```

## Basic Usage

### Command Structure

```bash
python src/main.py [INPUT_FILE] [OPTIONS]
```

### Essential Commands

#### 1. Basic Processing
```bash
python src/main.py medical_document.txt -o clean_output.txt
```

#### 2. Generate Statistics
```bash
python src/main.py input.txt -o output.txt --stats
```

#### 3. JSON Output with Metadata
```bash
python src/main.py input.txt -o report.json --format json
```

#### 4. Debug Mode
```bash
python src/main.py input.txt -o output.txt --debug
```

### Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `-o, --output` | Output file path | Auto-generated | `-o results.txt` |
| `--format` | Output format | `txt` | `--format json` |
| `--health-threshold` | Health relevance (0.0-1.0) | `0.3` | `--health-threshold 0.2` |
| `--quality-threshold` | Quality threshold (0.0-1.0) | `0.7` | `--quality-threshold 0.5` |
| `--completeness-threshold` | Completeness (0.0-1.0) | `0.6` | `--completeness-threshold 0.4` |
| `--stats` | Show processing statistics | `False` | `--stats` |
| `--debug` | Enable debug mode | `False` | `--debug` |
| `--error-report` | Generate error report | `False` | `--error-report` |
| `--log-level` | Logging level | `INFO` | `--log-level DEBUG` |
| `-v, --verbose` | Verbose output | `False` | `-v` |

## Advanced Configuration

### Threshold Configuration

The system uses three main thresholds to control filtering:

#### Health Threshold (0.0 - 1.0)
Controls medical relevance filtering:
- **0.1-0.2**: Very lenient (keeps most health-related content)
- **0.3**: Default (balanced filtering)
- **0.5-0.7**: Strict (only clear medical content)

```bash
# Lenient health filtering
python src/main.py input.txt -o output.txt --health-threshold 0.15

# Strict health filtering
python src/main.py input.txt -o output.txt --health-threshold 0.6
```

#### Quality Threshold (0.0 - 1.0)
Controls sentence quality requirements:
- **0.3-0.4**: Lenient (accepts lower quality sentences)
- **0.5-0.6**: Balanced (good quality sentences)
- **0.7-0.9**: Strict (only high-quality sentences)

```bash
# Balanced quality filtering
python src/main.py input.txt -o output.txt --quality-threshold 0.5

# High quality only
python src/main.py input.txt -o output.txt --quality-threshold 0.8
```

#### Completeness Threshold (0.0 - 1.0)
Controls sentence completeness requirements:
- **0.2-0.3**: Basic completeness
- **0.4-0.5**: Good completeness (recommended)
- **0.6-0.8**: High completeness requirements

```bash
# Recommended completeness
python src/main.py input.txt -o output.txt --completeness-threshold 0.4
```

### Environment Variables

Set persistent configuration using environment variables:

```bash
# Windows
set TXTIR_HEALTH_THRESHOLD=0.2
set TXTIR_QUALITY_THRESHOLD=0.5
set TXTIR_DEBUG_MODE=true

# macOS/Linux
export TXTIR_HEALTH_THRESHOLD=0.2
export TXTIR_QUALITY_THRESHOLD=0.5
export TXTIR_DEBUG_MODE=true
```

### Configuration File

Create a `config.json` file in the project root:

```json
{
  "thresholds": {
    "health_threshold": 0.2,
    "quality_threshold": 0.5,
    "completeness_threshold": 0.4
  },
  "output": {
    "default_format": "json",
    "include_stats": true,
    "include_metadata": true
  },
  "logging": {
    "level": "INFO",
    "enable_file_logging": true,
    "debug_mode": false
  },
  "processing": {
    "enable_error_recovery": true,
    "max_sentence_length": 500,
    "min_sentence_length": 10
  }
}
```

## Output Formats

### 1. Text Format (`.txt`)

**Usage**: `--format txt`

Clean text output with processed sentences:

```
The patient presented with acute myocardial infarction requiring immediate intervention.
Treatment was initiated with dual antiplatelet therapy including aspirin and clopidogrel.
Cardiac catheterization revealed significant coronary artery disease.
```

**With Statistics** (`--stats`):
```
=== txtIntelligentReader Processing Report ===
Input file: medical_document.txt
Processing time: 2.34 seconds
Total sentences processed: 150
Sentences retained: 23 (15.3%)
Medical terms identified: 45

=== Filtered Sentences ===
The patient presented with acute myocardial infarction requiring immediate intervention.
...
```

### 2. JSON Format (`.json`)

**Usage**: `--format json`

Structured data with complete metadata:

```json
{
  "metadata": {
    "input_file": "medical_document.txt",
    "processing_time": 2.34,
    "timestamp": "2025-01-29T09:24:22+02:00",
    "system_info": {
      "python_version": "3.9.7",
      "platform": "Windows-10"
    }
  },
  "statistics": {
    "total_sentences": 150,
    "retained_sentences": 23,
    "retention_rate": 15.3,
    "medical_terms_count": 45,
    "average_sentence_length": 18.5,
    "processing_speed": 3846.15
  },
  "results": {
    "filtered_sentences": [
      "The patient presented with acute myocardial infarction requiring immediate intervention.",
      "Treatment was initiated with dual antiplatelet therapy including aspirin and clopidogrel."
    ]
  },
  "quality_metrics": {
    "completeness_score": 0.87,
    "readability_score": 8.2,
    "medical_relevance": 0.94
  }
}
```

### 3. Markdown Format (`.md`)

**Usage**: `--format md`

Formatted report with tables and analysis:

```markdown
# txtIntelligentReader Processing Report

## Processing Summary
- **Input File**: medical_document.txt
- **Processing Time**: 2.34 seconds
- **Sentences Processed**: 150
- **Sentences Retained**: 23 (15.3%)

## Quality Metrics
| Metric | Score |
|--------|-------|
| Completeness | 0.87 |
| Readability | 8.2/10 |
| Medical Relevance | 0.94 |

## Filtered Sentences
1. The patient presented with acute myocardial infarction requiring immediate intervention.
2. Treatment was initiated with dual antiplatelet therapy including aspirin and clopidogrel.
```

### 4. CSV Format (`.csv`)

**Usage**: `--format csv`

Statistics export for analysis:

```csv
metric,value,unit
total_sentences,150,count
retained_sentences,23,count
retention_rate,15.3,percentage
processing_time,2.34,seconds
medical_terms_count,45,count
average_sentence_length,18.5,words
processing_speed,3846.15,sentences_per_minute
completeness_score,0.87,score
readability_score,8.2,score
medical_relevance,0.94,score
```

### 5. HTML Format (`.html`)

**Usage**: `--format html`

Interactive web report with styling:

```html
<!DOCTYPE html>
<html>
<head>
    <title>txtIntelligentReader Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .metric { background: #f0f8ff; padding: 10px; margin: 5px; }
        .sentence { border-left: 3px solid #007acc; padding-left: 15px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>📊 Processing Report</h1>
    <div class="metric">
        <strong>Retention Rate:</strong> 15.3% (23/150 sentences)
    </div>
    <!-- ... more content ... -->
</body>
</html>
```

## Performance Tuning

### Optimizing Processing Speed

#### 1. Adjust Thresholds for Speed
Lower thresholds = faster processing:
```bash
python src/main.py input.txt -o output.txt \
  --health-threshold 0.1 \
  --quality-threshold 0.3
```

#### 2. Disable Detailed Analysis
For maximum speed:
```bash
python src/main.py input.txt -o output.txt --format txt
# Avoid JSON/HTML formats for large files
```

#### 3. Process in Batches
For very large files:
```bash
# Split large files first
split -l 1000 large_file.txt chunk_

# Process chunks
for chunk in chunk_*; do
  python src/main.py "$chunk" -o "processed_$chunk"
done
```

### Memory Optimization

#### Monitor Memory Usage
```bash
python src/main.py input.txt -o output.txt --debug
# Check debug output for memory statistics
```

#### For Large Files
- Use text format output (`--format txt`)
- Avoid debug mode for production runs
- Process files <10MB for optimal performance

### Expected Performance

| File Size | Sentences | Processing Time | Memory Usage |
|-----------|-----------|----------------|--------------|
| 100KB | 500 | <1 second | <50MB |
| 1MB | 5,000 | 3-5 seconds | <100MB |
| 10MB | 50,000 | 30-60 seconds | <500MB |
| 50MB | 250,000 | 5-10 minutes | <2GB |

## Troubleshooting

### Common Issues and Solutions

#### 1. No Output Generated

**Symptoms**: Processing completes but output file is empty or has no sentences.

**Cause**: Thresholds too strict for the input content.

**Solution**:
```bash
# Try with lenient thresholds
python src/main.py input.txt -o output.txt \
  --health-threshold 0.1 \
  --quality-threshold 0.3 \
  --completeness-threshold 0.2 \
  --debug
```

**Debug**: Check debug output for filtering statistics.

#### 2. Import/Module Errors

**Symptoms**: `ModuleNotFoundError` or import failures.

**Cause**: Missing dependencies or incorrect Python path.

**Solution**:
```bash
# Verify Python environment
python --version
pip list

# Reinstall dependencies
pip install -r requirements.txt

# Check if running from correct directory
pwd
ls src/
```

#### 3. Slow Processing

**Symptoms**: Processing takes much longer than expected.

**Cause**: Large file size or complex content.

**Solution**:
```bash
# Check file size
ls -lh input.txt

# Use performance monitoring
python src/main.py input.txt -o output.txt --stats --debug

# Consider splitting large files
split -l 2000 input.txt chunk_
```

#### 4. Memory Errors

**Symptoms**: `MemoryError` or system becomes unresponsive.

**Cause**: File too large for available memory.

**Solution**:
```bash
# Check available memory
free -h  # Linux/macOS
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory  # Windows

# Process smaller chunks
head -n 1000 input.txt > small_chunk.txt
python src/main.py small_chunk.txt -o output.txt
```

#### 5. Encoding Issues

**Symptoms**: `UnicodeDecodeError` or garbled text.

**Cause**: File encoding not UTF-8.

**Solution**:
```bash
# Check file encoding
file -i input.txt  # Linux/macOS
chcp  # Windows

# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 input.txt > input_utf8.txt
```

### Debug Mode

Enable comprehensive debugging:

```bash
python src/main.py input.txt -o output.txt \
  --debug \
  --error-report \
  --log-level DEBUG \
  --verbose
```

This provides:
- Layer-by-layer processing details
- Memory usage statistics
- Processing time breakdown
- Filter decision explanations
- Error traces and recovery actions

### Log Files

Check log files for detailed information:
```bash
# View recent logs
ls -la logs/
tail -f logs/txtintelligentreader.log
```

## Best Practices

### Input File Preparation

#### 1. File Format
- **Preferred**: Plain text files (`.txt`)
- **Encoding**: UTF-8
- **Line endings**: Unix (LF) or Windows (CRLF)

#### 2. Content Guidelines
- Medical documents work best
- Remove obvious formatting artifacts manually if possible
- Ensure text is readable and properly formatted

#### 3. File Size Recommendations
- **Optimal**: 1-10MB files
- **Maximum tested**: 50MB
- **For larger files**: Split into smaller chunks

### Threshold Selection

#### For Different Use Cases

**Research/Analysis** (Comprehensive):
```bash
--health-threshold 0.1 --quality-threshold 0.3 --completeness-threshold 0.2
```

**Translation Preparation** (Balanced):
```bash
--health-threshold 0.15 --quality-threshold 0.5 --completeness-threshold 0.4
```

**High-Quality Output** (Strict):
```bash
--health-threshold 0.4 --quality-threshold 0.8 --completeness-threshold 0.7
```

**Clinical Documentation** (Medical Focus):
```bash
--health-threshold 0.6 --quality-threshold 0.6 --completeness-threshold 0.5
```

### Output Management

#### 1. Organize Output Files
```bash
# Create organized directory structure
mkdir -p output/{processed,reports,logs}

# Use descriptive filenames
python src/main.py input.txt -o "output/processed/$(date +%Y%m%d)_processed.txt"
```

#### 2. Batch Processing
```bash
#!/bin/bash
# Process multiple files with consistent settings
for file in input/*.txt; do
    basename=$(basename "$file" .txt)
    python src/main.py "$file" \
      -o "output/processed/${basename}_processed.txt" \
      --format json \
      --stats \
      --health-threshold 0.15 \
      --quality-threshold 0.5
done
```

### Quality Assurance

#### 1. Validate Results
Always review a sample of output:
```bash
# Generate detailed report
python src/main.py input.txt -o report.json --format json --stats

# Review first 10 sentences
head -n 10 output.txt
```

#### 2. Compare Thresholds
Test different threshold combinations:
```bash
# Test lenient settings
python src/main.py input.txt -o lenient.txt --health-threshold 0.1 --quality-threshold 0.3

# Test strict settings
python src/main.py input.txt -o strict.txt --health-threshold 0.5 --quality-threshold 0.8

# Compare results
wc -l lenient.txt strict.txt
```

#### 3. Monitor Performance
Track processing metrics over time:
```bash
# Log processing statistics
python src/main.py input.txt -o output.txt --format csv --stats >> processing_log.csv
```

## Examples

### Example 1: Basic Medical Document Processing

**Input** (`medical_notes.txt`):
```
PATIENT HISTORY
================
The patient is a 65-year-old male with a history of hypertension and diabetes.
He presented to the emergency department with chest pain.
PAGE 2
Initial assessment revealed elevated troponin levels.
ECG showed ST-segment elevation in leads II, III, and aVF.
FOOTER: Medical Center 2025
The patient was diagnosed with acute inferior myocardial infarction.
```

**Command**:
```bash
python src/main.py medical_notes.txt -o processed_notes.txt --stats
```

**Output** (`processed_notes.txt`):
```
=== txtIntelligentReader Processing Report ===
Input file: medical_notes.txt
Processing time: 0.45 seconds
Total sentences processed: 7
Sentences retained: 4 (57.1%)
Medical terms identified: 12

=== Filtered Sentences ===
The patient is a 65-year-old male with a history of hypertension and diabetes.
Initial assessment revealed elevated troponin levels.
ECG showed ST-segment elevation in leads II, III, and aVF.
The patient was diagnosed with acute inferior myocardial infarction.
```

### Example 2: Research Paper Processing

**Command**:
```bash
python src/main.py research_paper.txt -o analysis.json \
  --format json \
  --health-threshold 0.2 \
  --quality-threshold 0.6 \
  --stats
```

**Output** (excerpt from `analysis.json`):
```json
{
  "metadata": {
    "input_file": "research_paper.txt",
    "processing_time": 3.21,
    "timestamp": "2025-01-29T09:24:22+02:00"
  },
  "statistics": {
    "total_sentences": 245,
    "retained_sentences": 67,
    "retention_rate": 27.3,
    "medical_terms_count": 89,
    "processing_speed": 4578.13
  },
  "results": {
    "filtered_sentences": [
      "Cardiovascular disease remains the leading cause of mortality worldwide.",
      "The study included 1,247 patients with acute coronary syndrome.",
      "Primary endpoint was major adverse cardiac events at 30 days."
    ]
  }
}
```

### Example 3: Batch Processing Multiple Files

**Script** (`process_batch.sh`):
```bash
#!/bin/bash

# Configuration
HEALTH_THRESHOLD=0.15
QUALITY_THRESHOLD=0.5
OUTPUT_DIR="processed_batch"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Process all .txt files in input directory
for file in input/*.txt; do
    if [ -f "$file" ]; then
        basename=$(basename "$file" .txt)
        echo "Processing: $file"
        
        python src/main.py "$file" \
          -o "$OUTPUT_DIR/${basename}_processed.txt" \
          --health-threshold $HEALTH_THRESHOLD \
          --quality-threshold $QUALITY_THRESHOLD \
          --stats
        
        echo "Completed: $basename"
    fi
done

echo "Batch processing complete!"
```

**Usage**:
```bash
chmod +x process_batch.sh
./process_batch.sh
```

### Example 4: Quality Comparison Analysis

**Script** (`compare_thresholds.py`):
```python
#!/usr/bin/env python3
import subprocess
import json
import sys

def process_with_thresholds(input_file, health_thresh, quality_thresh):
    """Process file with specific thresholds and return statistics."""
    output_file = f"temp_{health_thresh}_{quality_thresh}.json"
    
    cmd = [
        'python', 'src/main.py', input_file,
        '-o', output_file,
        '--format', 'json',
        '--health-threshold', str(health_thresh),
        '--quality-threshold', str(quality_thresh),
        '--stats'
    ]
    
    subprocess.run(cmd, capture_output=True)
    
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
            return data['statistics']
    except:
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python compare_thresholds.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Test different threshold combinations
    thresholds = [
        (0.1, 0.3),  # Lenient
        (0.15, 0.5), # Balanced
        (0.3, 0.7),  # Default
        (0.5, 0.8)   # Strict
    ]
    
    print(f"Threshold Comparison for: {input_file}")
    print("-" * 60)
    print(f"{'Health':>8} {'Quality':>8} {'Retained':>10} {'Rate':>8} {'Speed':>10}")
    print("-" * 60)
    
    for health, quality in thresholds:
        stats = process_with_thresholds(input_file, health, quality)
        if stats:
            print(f"{health:>8.1f} {quality:>8.1f} {stats['retained_sentences']:>10} "
                  f"{stats['retention_rate']:>7.1f}% {stats['processing_speed']:>9.0f}")

if __name__ == "__main__":
    main()
```

**Usage**:
```bash
python compare_thresholds.py medical_document.txt
```

**Output**:
```
Threshold Comparison for: medical_document.txt
------------------------------------------------------------
  Health  Quality   Retained     Rate      Speed
------------------------------------------------------------
     0.1      0.3         89     35.6%      4521
     0.2      0.5         67     26.8%      4623
     0.3      0.7         45     18.0%      4789
     0.5      0.8         23      9.2%      4856
```

---

This user guide provides comprehensive information for effectively using txtIntelligentReader. For additional support, see the [FAQ section in the README](../README.md#faq) or create an issue in the project repository.
