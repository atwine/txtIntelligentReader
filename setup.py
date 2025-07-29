#!/usr/bin/env python3
"""
Setup script for txtIntelligentReader

Advanced Medical Text Processing System with Multi-Layer Filtering
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def read_requirements(filename):
    """Read requirements from file."""
    requirements_path = this_directory / filename
    if requirements_path.exists():
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Get version from src/__init__.py or set default
def get_version():
    """Get version from package or set default."""
    try:
        version_file = this_directory / "src" / "__init__.py"
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('__version__'):
                        return line.split('=')[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "1.0.0"

setup(
    # Package metadata
    name="txtintelligentreader",
    version=get_version(),
    author="txtIntelligentReader Team",
    author_email="support@txtintelligentreader.com",
    description="Advanced Medical Text Processing System with Multi-Layer Filtering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/txtIntelligentReader",
    project_urls={
        "Bug Reports": "https://github.com/your-username/txtIntelligentReader/issues",
        "Source": "https://github.com/your-username/txtIntelligentReader",
        "Documentation": "https://github.com/your-username/txtIntelligentReader/blob/main/docs/",
    },
    
    # Package discovery
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'': '.'},
    
    # Include additional files
    include_package_data=True,
    package_data={
        'src': [
            'data/*.json',
            'data/*.txt',
            'config/*.json',
        ],
    },
    
    # Dependencies
    install_requires=[
        # Core Python libraries (most are built-in)
        'pathlib2>=2.3.0;python_version<"3.4"',  # Backport for older Python
    ],
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.991',
            'pre-commit>=2.20.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
        'performance': [
            'memory-profiler>=0.60.0',
            'line-profiler>=4.0.0',
        ],
    },
    
    # Entry points for command-line interface
    entry_points={
        'console_scripts': [
            'txtintelligentreader=src.main:main',
            'txtir=src.main:main',  # Short alias
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Keywords for PyPI search
    keywords=[
        "medical", "text-processing", "nlp", "healthcare", "filtering",
        "translation", "clinical", "medical-records", "text-analysis",
        "sentence-extraction", "medical-nlp", "healthcare-ai"
    ],
    
    # License
    license="MIT",
    
    # Zip safe
    zip_safe=False,
    
    # Additional metadata
    platforms=["any"],
    
    # Test suite
    test_suite="tests",
    tests_require=[
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
    ],
)
