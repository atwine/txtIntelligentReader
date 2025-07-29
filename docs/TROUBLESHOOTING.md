# 🔧 Troubleshooting Guide

**Comprehensive troubleshooting for txtIntelligentReader**

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Performance Problems](#performance-problems)
4. [Output Issues](#output-issues)
5. [System-Specific Problems](#system-specific-problems)
6. [Debug Mode](#debug-mode)
7. [Getting Help](#getting-help)

## Quick Diagnostics

### System Check

Run this comprehensive system check first:

```bash
# Check Python version
python --version

# Check if in correct directory
pwd
ls src/

# Check dependencies
pip list | grep -E "(pathlib|json)"

# Test basic functionality
echo "The patient has diabetes." > test.txt
python src/main.py test.txt -o test_out.txt --debug
```

### Environment Verification

```bash
# Check environment variables
env | grep TXTIR

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check file permissions
ls -la src/main.py
```

## Common Issues

### 1. No Output Generated

#### Symptoms
- Processing completes successfully
- Output file is empty or contains only headers
- No filtered sentences in results

#### Diagnosis
```bash
# Run with debug mode to see filtering statistics
python src/main.py input.txt -o output.txt --debug --stats
```

Look for messages like:
```
No sentences remaining after quick filter
No sentences remaining after health filter
```

#### Solutions

**Solution 1: Lower Thresholds**
```bash
# Try very lenient settings
python src/main.py input.txt -o output.txt \
  --health-threshold 0.05 \
  --quality-threshold 0.2 \
  --completeness-threshold 0.1 \
  --debug
```

**Solution 2: Check Input Content**
```bash
# Verify input file has readable content
head -20 input.txt
wc -l input.txt

# Check for encoding issues
file -i input.txt
```

**Solution 3: Test with Known Good Input**
```bash
# Create test file with clear medical content
cat > medical_test.txt << EOF
The patient presented with acute myocardial infarction.
Blood pressure was elevated at 180/100 mmHg.
Treatment included aspirin and beta-blockers.
The patient showed improvement after 24 hours.
EOF

python src/main.py medical_test.txt -o test_output.txt --stats
```

### 2. Import/Module Errors

#### Symptoms
```
ModuleNotFoundError: No module named 'src'
ImportError: cannot import name 'FilterPipeline'
```

#### Diagnosis
```bash
# Check current directory
pwd
ls -la

# Check Python path
python -c "import sys; print(sys.path)"

# Test imports manually
python -c "from src.pipeline.filter_pipeline import FilterPipeline"
```

#### Solutions

**Solution 1: Correct Directory**
```bash
# Ensure you're in the project root
cd /path/to/txtIntelligentReader
ls src/
python src/main.py --help
```

**Solution 2: Fix Python Path**
```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use absolute path
python /full/path/to/txtIntelligentReader/src/main.py --help
```

**Solution 3: Check File Structure**
```bash
# Verify all required files exist
find src/ -name "*.py" | head -10
ls src/pipeline/
ls src/filters/
ls src/utils/
```

### 3. Processing Errors

#### Symptoms
```
AttributeError: 'NoneType' object has no attribute 'process'
ValueError: invalid literal for int() with base 10
```

#### Diagnosis
```bash
# Run with maximum debug information
python src/main.py input.txt -o output.txt \
  --debug \
  --error-report \
  --log-level DEBUG \
  --verbose
```

#### Solutions

**Solution 1: Check Input File**
```bash
# Verify file exists and is readable
ls -la input.txt
file input.txt
head -5 input.txt
```

**Solution 2: Clean Input**
```bash
# Remove problematic characters
sed 's/[^[:print:]]//g' input.txt > clean_input.txt
python src/main.py clean_input.txt -o output.txt
```

**Solution 3: Process in Smaller Chunks**
```bash
# Split large files
split -l 500 input.txt chunk_
for chunk in chunk_*; do
  python src/main.py "$chunk" -o "processed_$chunk"
done
```

### 4. Permission Errors

#### Symptoms
```
PermissionError: [Errno 13] Permission denied
OSError: [Errno 1] Operation not permitted
```

#### Solutions

**Solution 1: Check File Permissions**
```bash
# Check input file permissions
ls -la input.txt

# Check output directory permissions
ls -la output/
mkdir -p output
chmod 755 output/
```

**Solution 2: Use Different Output Location**
```bash
# Use home directory
python src/main.py input.txt -o ~/output.txt

# Use temporary directory
python src/main.py input.txt -o /tmp/output.txt
```

**Solution 3: Run with Appropriate Permissions**
```bash
# Change file ownership (Linux/macOS)
sudo chown $USER:$USER input.txt

# Run with sudo (not recommended for regular use)
sudo python src/main.py input.txt -o output.txt
```

## Performance Problems

### 1. Slow Processing

#### Symptoms
- Processing takes much longer than expected
- System becomes unresponsive
- High CPU or memory usage

#### Diagnosis
```bash
# Check file size
ls -lh input.txt

# Monitor system resources during processing
# Linux/macOS:
top -p $(pgrep -f "python src/main.py")

# Windows:
tasklist | findstr python
```

#### Solutions

**Solution 1: Optimize Settings**
```bash
# Use fastest settings
python src/main.py input.txt -o output.txt \
  --format txt \
  --health-threshold 0.1 \
  --quality-threshold 0.3
```

**Solution 2: Process in Batches**
```bash
# Split large files
split -l 1000 input.txt batch_

# Process batches
for batch in batch_*; do
  echo "Processing $batch..."
  python src/main.py "$batch" -o "output_$batch"
done

# Combine results
cat output_batch_* > final_output.txt
```

**Solution 3: Increase System Resources**
```bash
# Increase memory limits (Linux/macOS)
ulimit -v 8388608  # 8GB

# Set environment variables
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1
```

### 2. Memory Issues

#### Symptoms
```
MemoryError
OSError: [Errno 12] Cannot allocate memory
System becomes unresponsive
```

#### Diagnosis
```bash
# Check available memory
free -h  # Linux
vm_stat  # macOS
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory  # Windows

# Check file size
du -h input.txt
```

#### Solutions

**Solution 1: Process Smaller Files**
```bash
# Check file size first
wc -l input.txt

# If >10,000 lines, split it
split -l 2000 input.txt small_

# Process each part
for part in small_*; do
  python src/main.py "$part" -o "processed_$part"
done
```

**Solution 2: Use Text Output Only**
```bash
# Avoid memory-intensive formats
python src/main.py input.txt -o output.txt --format txt
# Avoid: --format json, --format html
```

**Solution 3: Restart System Services**
```bash
# Clear system cache (Linux)
sudo sync && sudo sysctl vm.drop_caches=3

# Restart if necessary
```

## Output Issues

### 1. Incorrect Output Format

#### Symptoms
- Output format doesn't match expectation
- Missing statistics or metadata
- Garbled or corrupted output

#### Solutions

**Solution 1: Specify Format Explicitly**
```bash
# For text output
python src/main.py input.txt -o output.txt --format txt

# For JSON with statistics
python src/main.py input.txt -o report.json --format json --stats

# For detailed markdown report
python src/main.py input.txt -o report.md --format md --stats
```

**Solution 2: Check Output File**
```bash
# Verify output was created
ls -la output.*

# Check file content
head -20 output.txt
file output.txt
```

### 2. Encoding Issues

#### Symptoms
- Strange characters in output
- UnicodeDecodeError
- Garbled text

#### Solutions

**Solution 1: Check Input Encoding**
```bash
# Check file encoding
file -i input.txt
chardet input.txt  # If chardet is installed
```

**Solution 2: Convert Encoding**
```bash
# Convert to UTF-8
iconv -f ISO-8859-1 -t UTF-8 input.txt > input_utf8.txt

# Or use Python
python -c "
with open('input.txt', 'r', encoding='latin1') as f:
    content = f.read()
with open('input_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(content)
"
```

**Solution 3: Force UTF-8 Processing**
```bash
# Set environment variable
export PYTHONIOENCODING=utf-8
python src/main.py input.txt -o output.txt
```

## System-Specific Problems

### Windows Issues

#### PowerShell Execution Policy
```powershell
# If virtual environment activation fails
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Path Length Limitations
```cmd
# Enable long paths
git config --system core.longpaths true

# Use shorter paths
cd C:\
mkdir txtir
cd txtir
# Move project here
```

#### Character Encoding
```cmd
# Set console to UTF-8
chcp 65001

# Set environment variable
set PYTHONIOENCODING=utf-8
```

### macOS Issues

#### Python Version Conflicts
```bash
# Use python3 explicitly
alias python=python3
alias pip=pip3

# Or use full path
/usr/bin/python3 src/main.py --help
```

#### Permission Issues
```bash
# Fix permissions
chmod +x src/main.py

# Use user directory for output
python src/main.py input.txt -o ~/Documents/output.txt
```

### Linux Issues

#### Missing Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-dev build-essential

# CentOS/RHEL
sudo yum install python3-devel gcc
```

#### SELinux Issues
```bash
# Check SELinux status
sestatus

# Temporarily disable if needed
sudo setenforce 0
```

## Debug Mode

### Enable Comprehensive Debugging

```bash
python src/main.py input.txt -o output.txt \
  --debug \
  --error-report \
  --log-level DEBUG \
  --verbose \
  --stats
```

### Understanding Debug Output

#### Filter Statistics
```
🔍 Quick Filter: 150 → 89 sentences (59.3% retained)
🏥 Health Filter: 89 → 45 sentences (50.6% retained)
🤖 AI Analysis: 45 → 32 sentences (71.1% retained)
✅ Complete Thought: 32 → 28 sentences (87.5% retained)
```

#### Performance Metrics
```
⏱️ Processing Time: 2.34 seconds
💾 Memory Usage: 45.2 MB peak
📊 Processing Speed: 3,846 sentences/minute
```

#### Error Information
```
⚠️ Warning: 3 sentences failed health context analysis
❌ Error: 1 sentence caused processing exception
🔧 Recovery: Continued with remaining sentences
```

### Log File Analysis

```bash
# View recent logs
tail -f logs/txtintelligentreader.log

# Search for errors
grep -i error logs/txtintelligentreader.log

# View debug information
grep -i debug logs/txtintelligentreader.log | tail -20
```

## Advanced Troubleshooting

### Memory Profiling

```python
# Create memory_profile.py
import tracemalloc
import subprocess
import sys

tracemalloc.start()

# Run your command
result = subprocess.run([
    'python', 'src/main.py', sys.argv[1], 
    '-o', 'output.txt', '--debug'
], capture_output=True, text=True)

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```

```bash
# Usage
python memory_profile.py input.txt
```

### Performance Profiling

```bash
# Install profiling tools
pip install cProfile

# Profile the application
python -m cProfile -o profile_output.prof src/main.py input.txt -o output.txt

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile_output.prof')
p.sort_stats('cumulative').print_stats(20)
"
```

### Network Diagnostics

```bash
# Check if any network calls are being made (shouldn't be any)
netstat -an | grep ESTABLISHED

# Monitor network during processing
# Linux:
sudo netstat -tuln | grep python

# macOS:
lsof -i -P | grep python
```

## Getting Help

### Information to Collect

Before seeking help, collect this information:

```bash
# System information
python --version
pip --version
uname -a  # Linux/macOS
systeminfo  # Windows

# Project information
pwd
ls -la src/
git log --oneline -5

# Error reproduction
python src/main.py input.txt -o output.txt --debug --error-report 2>&1 | tee error_log.txt
```

### Create Minimal Reproduction

```bash
# Create minimal test case
cat > minimal_test.txt << EOF
The patient has diabetes.
Blood sugar levels were elevated.
Treatment was prescribed.
EOF

# Test with minimal input
python src/main.py minimal_test.txt -o minimal_output.txt --debug
```

### Support Channels

1. **Check Documentation**
   - [User Guide](user-guide.md)
   - [Installation Guide](INSTALLATION.md)
   - [FAQ](../README.md#faq)

2. **Search Existing Issues**
   - GitHub Issues: `<repository-url>/issues`
   - Search for similar problems

3. **Create New Issue**
   Include:
   - Operating system and version
   - Python version
   - Complete error messages
   - Steps to reproduce
   - Input file sample (if possible)
   - Output of debug mode

4. **Community Support**
   - Stack Overflow (tag: `txtintelligentreader`)
   - Project discussions

### Emergency Recovery

If the system is completely broken:

```bash
# Clean reinstall
cd ..
rm -rf txtIntelligentReader
git clone <repository-url>
cd txtIntelligentReader

# Fresh virtual environment
python -m venv fresh_env
source fresh_env/bin/activate  # or fresh_env\Scripts\activate on Windows
pip install -r requirements.txt

# Test basic functionality
echo "Test sentence." > test.txt
python src/main.py test.txt -o test_out.txt
```

---

**Still having issues?** Don't hesitate to create a detailed issue report. The more information you provide, the faster we can help resolve the problem! 🚀
