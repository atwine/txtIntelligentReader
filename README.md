# 🩺 txtIntelligentReader

**AI-Powered Multi-Agent Text Processing System for Health Domain Translation**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.55.0+-green.svg)](https://github.com/joaomdmoura/crewAI)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange.svg)](https://ollama.ai/)

> A sophisticated CrewAI-powered multi-agent system that extracts high-quality, translation-ready sentences from health domain text files using specialized AI agents for content classification, medical expertise, grammar enhancement, and quality validation.

## 🌟 Features

### 🤖 **Multi-Agent Architecture**
- **ContentClassifierAgent**: Intelligent text classification with 8 categories and noise detection
- **HealthDomainExpertAgent**: Medical entity recognition and health relevance scoring
- **GrammarEnhancementAgent**: Advanced text enhancement and translation readiness optimization
- **QualityValidationAgent**: Comprehensive quality validation with medical accuracy checks
- **WorkflowCoordinatorAgent**: Orchestrates the entire multi-agent workflow

### 🏥 **Health Domain Specialization**
- **Medical Entity Recognition**: Powered by medspaCy for clinical NLP
- **Health Terminology Validation**: 200+ medical terms database
- **Medical Context Analysis**: Domain-specific relevance scoring
- **Clinical Text Enhancement**: Standardization for medical translation

### 🔍 **Advanced Filtering System**
- **4-Layer Filtering Pipeline**: QuickFilter → ContentFilter → HealthFilter → QualityFilter
- **Noise Detection**: PDF artifacts, headers, footers, and formatting issues
- **Quality Scoring**: Multi-factor confidence and quality metrics
- **Translation Readiness**: Grammar, punctuation, and completeness validation

### 🛠️ **Technical Excellence**
- **Offline Operation**: Local Ollama LLM integration (no external API dependencies)
- **Robust Error Handling**: Graceful degradation and recovery strategies
- **Comprehensive Testing**: Unit tests for all agents and components
- **Performance Monitoring**: Detailed metrics and workflow analytics

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Ollama** installed and running
- **llama3.1:8b** model (or compatible)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/atwine/txtIntelligentReader.git
   cd txtIntelligentReader
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Ollama**
   ```bash
   # Install Ollama (if not already installed)
   # Visit: https://ollama.ai/
   
   # Pull the required model
   ollama pull llama3.1:8b
   
   # Start Ollama service
   ollama serve
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Basic Usage

```python
from src.agents.workflow_coordinator import WorkflowCoordinatorAgent
from src.agents.content_classifier import ContentClassifierAgent
from src.agents.health_expert import HealthDomainExpertAgent
from src.agents.grammar_enhancer import GrammarEnhancementAgent
from src.agents.quality_validator import QualityValidationAgent
from ollama import Client

# Initialize Ollama client
llm = Client(host='http://localhost:11434')

# Create specialist agents
agents = [
    ContentClassifierAgent(llm),
    HealthDomainExpertAgent(llm),
    GrammarEnhancementAgent(llm),
    QualityValidationAgent(llm)
]

# Create workflow coordinator
coordinator = WorkflowCoordinatorAgent(llm, agents)

# Process text file
results = coordinator.coordinate_processing('path/to/medical_text.txt')

print(f"Processed {results['processed_segments']} segments")
print(f"Quality Score: {results['quality_score']:.2f}")
```

## 📁 Project Structure

```
txtIntelligentReader/
├── src/
│   ├── agents/              # Core AI agents
│   │   ├── content_classifier.py
│   │   ├── health_expert.py
│   │   ├── grammar_enhancer.py
│   │   ├── quality_validator.py
│   │   └── workflow_coordinator.py
│   ├── filters/             # Filtering system
│   │   ├── quick_filter.py
│   │   ├── content_filter.py
│   │   ├── health_filter.py
│   │   └── quality_filter.py
│   ├── utils/               # Utility functions
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── output_formatter.py
│   └── config/              # Configuration files
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── examples/                # Example usage
├── scripts/                 # Utility scripts
├── output/                  # Processing results
├── logs/                    # Application logs
├── requirements.txt         # Dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific agent tests
python tests/test_content_classifier.py
python tests/test_health_expert.py
python tests/test_grammar_enhancer.py
python tests/test_quality_validator.py
python tests/test_workflow_coordinator.py

# Run with coverage
python -m pytest tests/ --cov=src
```

## 📊 Performance Metrics

The system provides comprehensive metrics:

- **Processing Speed**: Average time per text segment
- **Quality Scores**: Multi-factor quality assessment
- **Success Rates**: Agent performance and workflow efficiency
- **Medical Accuracy**: Health domain relevance and terminology validation
- **Translation Readiness**: Grammar, completeness, and formatting scores

## 🔧 Configuration

Key configuration options in `.env`:

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TIMEOUT=300

# Health Domain Settings
HEALTH_RELEVANCE_THRESHOLD=0.7
MEDICAL_ENTITY_THRESHOLD=0.6
QUALITY_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/txtintelligentreader.log

# Performance
ENABLE_CACHING=true
MAX_PARALLEL_AGENTS=4
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI** for the multi-agent framework
- **Ollama** for local LLM capabilities
- **medspaCy** for medical NLP processing
- **spaCy** for natural language processing

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/atwine/txtIntelligentReader/issues)
- **Discussions**: [GitHub Discussions](https://github.com/atwine/txtIntelligentReader/discussions)
- **Documentation**: [Project Wiki](https://github.com/atwine/txtIntelligentReader/wiki)

---

**Made with ❤️ for the medical translation community**

A CrewAI-powered multi-agent text processing system that extracts high-quality, translation-ready sentences from health domain text files.

## Features

- **Multi-Agent Architecture**: 5 specialized AI agents working together
- **4-Layer Filtering System**: Progressive quality enhancement
- **Health Domain Specialization**: Medical terminology recognition
- **Translation-Ready Output**: Grammatically perfect sentences
- **Multiple Output Formats**: Text, JSON, and Markdown
- **Batch Processing**: Handle multiple files efficiently
- **Local LLM Integration**: Uses Ollama for offline processing

## Architecture

### Agents
1. **ContentClassifierAgent**: Document analysis and classification
2. **HealthDomainExpertAgent**: Medical terminology expertise
3. **GrammarEnhancementAgent**: Text quality improvement
# Install Ollama (see https://ollama.ai)
ollama pull llama3.1:8b
```

## Usage

### Basic Usage
```bash
python main.py input.txt
```

### Advanced Usage
```bash
# Specify output format and file
python main.py input.txt --output results.json --format json

# Batch processing
python main.py --batch input_folder/ --output output_folder/

# Adjust quality thresholds
python main.py input.txt --health-threshold 0.8 --quality-threshold 0.9

# Verbose output with progress
python main.py input.txt --verbose --progress --stats
```

## Configuration

The system uses environment variables and configuration files:

- `.env`: Environment configuration
- `src/config/`: Configuration modules
- Command-line arguments override defaults

## Development Status

- ✅ **Phase 1**: Environment Setup and Project Structure
- 🚧 **Phase 2**: Core Agent Development (In Progress)
- ⏳ **Phase 3**: Filtering System Implementation
- ⏳ **Phase 4**: Integration and Testing

## Requirements

- Python 3.9+
- Ollama with Llama 3.1:8b model
- CrewAI framework
- medspaCy for medical NLP
- Additional dependencies in `requirements.txt`

## Performance Targets

- **Speed**: 1000+ sentences per minute
- **Precision**: >90% health domain detection accuracy
- **Quality**: >95% grammatical correctness
- **Recall**: >85% meaningful content retention

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
