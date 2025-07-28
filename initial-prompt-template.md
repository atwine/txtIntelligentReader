# Intelligent Text Sentence Extraction System - Project Prompt Template
<!-- 
  This template defines the txtIntelligentReader project: an AI-powered system for extracting 
  high-quality, translation-ready sentences from text files using intelligent filtering.
-->

## 1. High-Level Goal
<!-- 
  **Your Goal:** Extract meaningful, complete sentences from text files (especially PDF-extracted content) 
  using intelligent filtering and AI-powered quality assessment for translation workflows.
-->

Build a command-line Python script that intelligently extracts high-quality, translation-ready sentences from text files using multi-layer filtering, health domain specialization, and LLM-powered analysis to eliminate noise, headers, fragments, and non-meaningful content.

## 2. Core Features & Requirements
<!-- 
  **Your Goal:** Essential features for intelligent text processing and sentence extraction.
-->

### **Input Processing**
- Accept single text files or batch process entire directories
- Handle various text formats (plain text, markdown-style formatting)
- Process PDF-extracted text files with formatting artifacts
- Support command-line arguments for file/directory paths

### **Intelligent Filtering System (4-Layer Architecture)**
- **Layer 1: Quick Filter** - Remove obvious noise (page numbers, roman numerals, standalone numbers, dots/lines)
- **Layer 2: Health Context Detection** - Identify medical/health terminology and domain relevance
- **Layer 3: AI Analysis** - Use Ollama/LLM for sentence completeness and meaning validation
- **Layer 4: Complete Thought Validation** - Ensure sentences have proper structure and actionable content

### **Sentence Quality Assessment**
- Extract only complete, meaningful sentences (not fragments or headers)
- Identify and filter out table of contents, references, navigation elements
- Preserve context and maintain sentence relationships within paragraphs
- Score sentences for translation readiness and domain relevance

### **Health Domain Specialization**
- Recognize 200+ medical terms and health concepts
- Prioritize public health, surveillance, and clinical content
- Filter content relevant for medical translation workflows
- Handle specialized medical formatting and terminology

### **Output & Reporting**
- Generate clean text files with filtered sentences
- Provide detailed analysis reports with filtering decisions and reasoning
- Include statistics (total sentences, kept/discarded, confidence scores)
- Support multiple output formats (clean text, JSON with metadata, markdown reports)

### **CrewAI Multi-Agent Architecture**
- **Agent 1: Content Classifier** - Experienced Document Analyst persona for text segment classification
- **Agent 2: Health Domain Expert** - Senior Medical Editor persona for medical relevance scoring
- **Agent 3: Grammar & Style Enhancer** - Professional Copy Editor persona for text enhancement
- **Agent 4: Quality Assurance Validator** - Quality Control Specialist persona for final validation
- **Agent 5: Workflow Coordinator** - Project Manager persona for crew orchestration
- **Sequential Processing Pipeline**: Classify → Health Score → Grammar Fix → Validate → Compile
- **Specialized Personas**: Each agent has distinct role, goal, and backstory for focused expertise
- **Coordinated Workflow**: CrewAI framework manages agent collaboration and task delegation

### **Performance & Usability**
- Display progress bars for large files and batch processing
- Provide verbose mode with detailed agent reasoning and decision explanations
- Handle errors gracefully with fallback coordination if individual agents fail
- Fast processing with efficient multi-agent workflow and parallel task execution

## 3. Technology Stack
<!-- 
  **Your Goal:** Simple, robust Python-based solution with AI integration.
-->

- **Language**: Python 3.9+
- **AI/LLM Framework**: CrewAI with Ollama + Llama 3.1:8b model (local inference)
- **Multi-Agent Architecture**: CrewAI framework for coordinated agent workflows
- **Core Libraries**: 
  - `crewai` - Multi-agent coordination framework
  - `requests` - Ollama API communication
  - `re` - Pattern matching and text cleaning
  - `json` - Structured output formatting
  - `pathlib` - File system operations
  - `argparse` - Command-line interface
- **Text Processing**: Built-in Python string methods and regex
- **Progress Tracking**: Custom progress bar implementation
- **Logging**: Detailed agent interaction logging with reasoning

## 4. Code Examples
<!-- 
  **Your Goal:** Reference the pdfIntelligentReader architecture and adapt for text processing.
-->

**Reference Implementation**: Adapt the intelligent filtering logic from `C:\Users\ic\OneDrive\Desktop\pdfIntelligentReader\enhanced_intelligent_processor.py` and `src\intelligence\ollama_agent.py`

**CrewAI Agent Implementation Patterns**:
```python
# Agent Example: Content Classifier
class ContentClassifierAgent:
    role = "Experienced Document Analyst"
    goal = "Classify text segments with high precision"
    backstory = "You have reviewed thousands of medical documents..."
    
# Agent Example: Grammar Enhancer  
class GrammarStyleEnhancer:
    role = "Professional Copy Editor"
    goal = "Transform sentences into perfect, translation-ready text"
    backstory = "You have edited thousands of medical translations..."
```

**Multi-Agent Workflow**:
- Sequential pipeline: Input → Classify → Health Score → Grammar Fix → Validate → Output
- Each agent provides reasoning and confidence scores
- Coordinated error handling and quality assurance

**Input Example**: 
```
LIST OF TABLES
patient with fever should isolated  
ii FOREWORD
treatment must be given immediately
Page 23
```

**Expected Output Quality**:
```
Example 1: Patients with fever should be isolated immediately.
Example 2: Treatment must be given immediately to ensure patient safety.
```

## 5. Documentation & References
<!-- 
  **Your Goal:** Ensure current and correct implementation methods.
-->

- [CrewAI Documentation](https://docs.crewai.com/)
- [CrewAI GitHub Repository](https://github.com/joaomdmoura/crewAI)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Llama 3.1 Model Information](https://ollama.ai/library/llama3.1)
- [Python argparse Documentation](https://docs.python.org/3/library/argparse.html)
- [Python re Module Documentation](https://docs.python.org/3/library/re.html)
- **Reference System**: `C:\Users\ic\OneDrive\Desktop\pdfIntelligentReader` - existing intelligent PDF processing system

## 6. Other Considerations & Gotchas
<!-- 
  **Your Goal:** Important constraints and technical considerations.
-->

### **CrewAI Multi-Agent Considerations**
- CrewAI framework must be installed and configured (`pip install crewai`)
- Ollama must be running locally on `http://localhost:11434`
- Llama 3.1:8b model must be pulled and available (`ollama pull llama3.1:8b`)
- Each agent needs distinct persona definition (role, goal, backstory)
- Implement agent coordination and task delegation through CrewAI workflow
- Use low temperature (0.1) for consistent agent analysis results
- Handle agent failures gracefully with crew-level error recovery

### **Text Processing Challenges**
- Handle PDF extraction artifacts (broken words, formatting issues)
- Preserve sentence context while filtering individual sentences
- Deal with multi-line sentences and paragraph breaks
- Recognize different text formatting patterns (headers, lists, tables)

### **Performance Requirements**
- Process large text files (500KB+) efficiently
- Batch processing should handle 10+ files without memory issues
- AI calls should timeout after 30 seconds to prevent hanging
- Progress tracking for files with 1000+ sentences

### **Domain Specificity**
- Focus on health/medical domain but make extensible for other domains
- Health keyword dictionary should be comprehensive but not overly restrictive
- Balance between domain relevance and general sentence quality

## 7. Success Criteria
<!-- 
  **Your Goal:** Define what "done" looks like for the intelligent text processor.
-->

### **Functional Success**
- Successfully processes single text files and batch directories via command line
- CrewAI multi-agent workflow coordinates 5 specialized agents effectively
- Filters out 80%+ of noise content while retaining meaningful sentences through agent collaboration
- Each agent provides specialized analysis with confidence scores and reasoning
- Generates clean, grammatically perfect, translation-ready output files

### **Quality Metrics**
- Extracted sentences are complete thoughts with subject and predicate
- Health domain content is prioritized and properly identified
- False positive rate <10% (keeping noise) and false negative rate <5% (discarding good content)
- Processing speed: 1000+ sentences per minute on average hardware

### **Usability & Reliability**
- Simple command-line interface: `python intelligent_text_processor.py input.txt`
- Batch processing: `python intelligent_text_processor.py /path/to/text/files/`
- Verbose mode shows detailed agent interactions, reasoning, and decisions
- CrewAI workflow coordination with graceful agent failure handling
- Works offline with local Ollama installation (no external API dependencies)
- Multi-agent progress tracking and comprehensive error reporting

### **Output Quality**
- Clean text files ready for translation workflows
- Detailed analysis reports with statistics and filtering rationale
- JSON output option for programmatic processing
- Maintains original sentence meaning and context while removing formatting artifacts

---

**Note**: This system should be a CrewAI-powered, multi-agent adaptation of the existing pdfIntelligentReader, removing PDF parsing complexity while enhancing intelligent filtering through specialized agent collaboration. Each agent brings focused expertise (classification, health domain knowledge, grammar enhancement, quality validation, and workflow coordination) to produce grammatically perfect, translation-ready sentences.
