# 🚀 Installation Guide

**Complete setup instructions for txtIntelligentReader**

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Installation](#quick-installation)
3. [Detailed Setup](#detailed-setup)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Setup](#advanced-setup)

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

### Recommended Requirements
- **Python**: 3.9 or higher
- **RAM**: 8GB or more
- **Storage**: 5GB free space
- **CPU**: Multi-core processor for better performance

### Dependencies
- Python standard library modules
- No external API dependencies (fully offline)

## Quick Installation

### Option 1: Standard Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd txtIntelligentReader

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python src/main.py --help
```

### Option 2: Virtual Environment (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd txtIntelligentReader

# 2. Create virtual environment
python -m venv txtir_env

# 3. Activate virtual environment
# Windows:
txtir_env\Scripts\activate
# macOS/Linux:
source txtir_env/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python src/main.py --help
```

## Detailed Setup

### Step 1: Python Installation

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
# Verify installation
python3 --version
pip3 --version
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

### Step 2: Clone Repository

```bash
# Using HTTPS
git clone https://github.com/your-username/txtIntelligentReader.git

# Using SSH (if configured)
git clone git@github.com:your-username/txtIntelligentReader.git

# Navigate to directory
cd txtIntelligentReader
```

### Step 3: Virtual Environment Setup

#### Why Use Virtual Environment?
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Easier dependency management
- Clean uninstallation

#### Create Virtual Environment

```bash
# Create virtual environment
python -m venv txtir_env

# Alternative name
python -m venv venv
```

#### Activate Virtual Environment

**Windows (Command Prompt)**:
```cmd
txtir_env\Scripts\activate
```

**Windows (PowerShell)**:
```powershell
txtir_env\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
source txtir_env/bin/activate
```

#### Verify Activation
Your prompt should show `(txtir_env)` or similar:
```bash
(txtir_env) user@computer:~/txtIntelligentReader$
```

### Step 4: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 5: Configuration

#### Create Configuration Directory
```bash
mkdir -p config
mkdir -p logs
mkdir -p output
```

#### Optional: Create Configuration File
```bash
# Create sample configuration
cat > config.json << EOF
{
  "thresholds": {
    "health_threshold": 0.15,
    "quality_threshold": 0.5,
    "completeness_threshold": 0.4
  },
  "output": {
    "default_format": "txt",
    "include_stats": true
  },
  "logging": {
    "level": "INFO",
    "enable_file_logging": true
  }
}
EOF
```

## Verification

### Basic Functionality Test

```bash
# Test help command
python src/main.py --help

# Create test file
echo "The patient presented with acute myocardial infarction. Treatment was initiated immediately." > test_input.txt

# Process test file
python src/main.py test_input.txt -o test_output.txt --stats

# Check output
cat test_output.txt
```

### Expected Output
```
=== txtIntelligentReader Processing Report ===
Input file: test_input.txt
Processing time: 0.12 seconds
Total sentences processed: 2
Sentences retained: 2 (100.0%)
Medical terms identified: 4

=== Filtered Sentences ===
The patient presented with acute myocardial infarction.
Treatment was initiated immediately.
```

### Run Test Suite

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python tests/test_filters_unit.py
python tests/test_integration_comprehensive.py
python tests/test_performance.py
```

### Performance Verification

```bash
# Run performance test
python tests/test_performance.py

# Expected output should show:
# - Processing speed: 150,000+ sentences/minute
# - Memory usage: <100KB per sentence
# - All performance tests passing
```

## Troubleshooting

### Common Installation Issues

#### 1. Python Not Found

**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
```bash
# Windows: Add Python to PATH or use full path
C:\Python39\python.exe src/main.py --help

# macOS/Linux: Use python3
python3 src/main.py --help
```

#### 2. Permission Denied

**Error**: `Permission denied` when installing packages

**Solution**:
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python -m venv txtir_env
source txtir_env/bin/activate  # or txtir_env\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 3. Module Not Found

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure you're in the correct directory
pwd
ls src/

# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run from project root
cd /path/to/txtIntelligentReader
python src/main.py --help
```

#### 4. Virtual Environment Issues

**Error**: Virtual environment not activating

**Solution**:
```bash
# Recreate virtual environment
rm -rf txtir_env
python -m venv txtir_env

# Windows activation issues
# Use Command Prompt instead of PowerShell
cmd
txtir_env\Scripts\activate

# macOS/Linux permission issues
chmod +x txtir_env/bin/activate
source txtir_env/bin/activate
```

#### 5. Dependency Installation Failures

**Error**: Package installation fails

**Solution**:
```bash
# Update pip
pip install --upgrade pip setuptools wheel

# Clear pip cache
pip cache purge

# Install with verbose output
pip install -r requirements.txt -v

# Install packages individually
pip install pathlib
pip install json
# ... etc
```

### Platform-Specific Issues

#### Windows

**PowerShell Execution Policy**:
```powershell
# If activation fails in PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Long Path Issues**:
```cmd
# Enable long paths in Windows
git config --system core.longpaths true
```

#### macOS

**Command Line Tools**:
```bash
# Install Xcode command line tools if needed
xcode-select --install
```

**Python Version Issues**:
```bash
# Use python3 explicitly
alias python=python3
alias pip=pip3
```

#### Linux

**Missing Development Headers**:
```bash
# Ubuntu/Debian
sudo apt install python3-dev build-essential

# CentOS/RHEL
sudo yum install python3-devel gcc
```

## Advanced Setup

### Development Environment

```bash
# Clone with development branch
git clone -b develop <repository-url>

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run development tests
python -m pytest tests/ --cov=src --cov-report=html
```

### Docker Setup (Optional)

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "src/main.py", "--help"]
```

```bash
# Build and run
docker build -t txtintelligentreader .
docker run -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output txtintelligentreader python src/main.py input/document.txt -o output/processed.txt
```

### Performance Optimization

#### System Tuning

```bash
# Increase file descriptor limits (Linux/macOS)
ulimit -n 4096

# Set environment variables for better performance
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1
```

#### Memory Optimization

```bash
# For large files, increase Python memory limits
export PYTHONMALLOC=malloc
```

### IDE Setup

#### VS Code Configuration

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./txtir_env/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm Configuration

1. Open project in PyCharm
2. Go to File → Settings → Project → Python Interpreter
3. Select "Add Interpreter" → "Existing Environment"
4. Point to `txtir_env/bin/python` (or `txtir_env\Scripts\python.exe` on Windows)

## Uninstallation

### Remove Virtual Environment

```bash
# Deactivate if active
deactivate

# Remove virtual environment
rm -rf txtir_env

# Remove project directory
cd ..
rm -rf txtIntelligentReader
```

### Clean System Installation

```bash
# Uninstall packages (if installed globally)
pip uninstall -r requirements.txt -y

# Remove project directory
rm -rf txtIntelligentReader
```

## Next Steps

After successful installation:

1. **Read the [User Guide](user-guide.md)** for detailed usage instructions
2. **Try the examples** in the [Examples section](user-guide.md#examples)
3. **Configure thresholds** based on your use case
4. **Run performance tests** to verify optimal setup
5. **Check the [FAQ](../README.md#faq)** for common questions

## Support

If you encounter issues not covered here:

1. Check the [Troubleshooting section](user-guide.md#troubleshooting) in the User Guide
2. Search existing [GitHub issues](../../issues)
3. Create a new issue with:
   - Your operating system and Python version
   - Complete error messages
   - Steps to reproduce the problem
   - Output of `pip list` and `python --version`

---

**Installation complete! You're ready to process medical text with txtIntelligentReader.** 🎉
