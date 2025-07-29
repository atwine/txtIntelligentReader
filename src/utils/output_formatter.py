#!/usr/bin/env python3
"""
Output Formatter for txtIntelligentReader

Provides multiple output formats including text, JSON, markdown reports,
and comprehensive statistics with metadata and versioning.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import platform
import sys

from .logger import LoggerMixin


class OutputFormatter(LoggerMixin):
    """
    Comprehensive output formatter supporting multiple formats and detailed reporting.
    
    Supports text, JSON, markdown, CSV, and HTML output formats with
    metadata, statistics, and versioning information.
    """
    
    VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize the output formatter."""
        self.creation_time = datetime.now()
    
    def save_text(self, sentences: List[str], output_path: Union[str, Path], 
                  metadata: Dict[str, Any] = None) -> bool:
        """
        Save sentences in clean text format.
        
        Args:
            sentences: List of filtered sentences
            output_path: Path to output file
            metadata: Optional metadata to include as header comment
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Add metadata header if provided
                if metadata:
                    f.write(f"# txtIntelligentReader Output\n")
                    f.write(f"# Generated: {datetime.now().isoformat()}\n")
                    f.write(f"# Input file: {metadata.get('input_file', 'Unknown')}\n")
                    f.write(f"# Processing time: {metadata.get('processing_time', 0):.3f}s\n")
                    f.write(f"# Sentences: {len(sentences)}\n")
                    f.write(f"# Layers applied: {', '.join(metadata.get('layers_applied', []))}\n")
                    f.write(f"#\n\n")
                
                # Write sentences
                for sentence in sentences:
                    f.write(sentence.strip() + '\n')
            
            self.log_info(f"Text output saved to: {output_path}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to save text output: {str(e)}")
            return False
    
    def save_json(self, sentences: List[str], metadata: Dict[str, Any], 
                  output_path: Union[str, Path], include_statistics: bool = True) -> bool:
        """
        Save sentences and metadata in JSON format.
        
        Args:
            sentences: List of filtered sentences
            metadata: Processing metadata
            output_path: Path to output JSON file
            include_statistics: Whether to include detailed statistics
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)
            
            # Prepare JSON structure
            json_data = {
                "txtIntelligentReader": {
                    "version": self.VERSION,
                    "generated_at": datetime.now().isoformat(),
                    "system_info": self._get_system_info()
                },
                "input": {
                    "file": metadata.get('input_file', 'Unknown'),
                    "original_sentence_count": metadata.get('statistics', {}).get('input_sentences', 0)
                },
                "processing": {
                    "layers_applied": metadata.get('layers_applied', []),
                    "processing_time_seconds": metadata.get('processing_time', 0),
                    "configuration": metadata.get('configuration', {})
                },
                "results": {
                    "filtered_sentences": sentences,
                    "output_sentence_count": len(sentences),
                    "retention_rate": metadata.get('statistics', {}).get('overall_retention_rate', 0)
                }
            }
            
            # Add detailed statistics if requested
            if include_statistics and 'statistics' in metadata:
                json_data["detailed_statistics"] = {
                    "layer_results": metadata['statistics'].get('layer_results', []),
                    "filter_statistics": metadata.get('filter_statistics', {}),
                    "quality_metrics": self._calculate_quality_metrics(sentences, metadata)
                }
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            self.log_info(f"JSON output saved to: {output_path}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to save JSON output: {str(e)}")
            return False
    
    def save_markdown_report(self, sentences: List[str], metadata: Dict[str, Any], 
                           output_path: Union[str, Path], detailed: bool = True) -> bool:
        """
        Generate and save a detailed markdown report.
        
        Args:
            sentences: List of filtered sentences
            metadata: Processing metadata
            output_path: Path to output markdown file
            detailed: Whether to include detailed analysis
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("# txtIntelligentReader Processing Report\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Version:** {self.VERSION}\n\n")
                
                # Input Information
                f.write("## Input Information\n\n")
                f.write(f"- **Input File:** `{metadata.get('input_file', 'Unknown')}`\n")
                f.write(f"- **Original Sentences:** {metadata.get('statistics', {}).get('input_sentences', 0)}\n")
                f.write(f"- **Processing Time:** {metadata.get('processing_time', 0):.3f} seconds\n\n")
                
                # Processing Configuration
                f.write("## Processing Configuration\n\n")
                config = metadata.get('configuration', {})
                f.write(f"- **Layers Applied:** {', '.join(metadata.get('layers_applied', []))}\n")
                f.write(f"- **Health Threshold:** {config.get('health_threshold', 'N/A')}\n")
                f.write(f"- **Completeness Threshold:** {config.get('completeness_threshold', 'N/A')}\n")
                f.write(f"- **Quality Threshold:** {config.get('quality_threshold', 'N/A')}\n")
                f.write(f"- **spaCy Enabled:** {config.get('use_spacy', False)}\n\n")
                
                # Results Summary
                f.write("## Results Summary\n\n")
                stats = metadata.get('statistics', {})
                f.write(f"- **Output Sentences:** {len(sentences)}\n")
                f.write(f"- **Retention Rate:** {stats.get('overall_retention_rate', 0)*100:.1f}%\n")
                f.write(f"- **Sentences Filtered:** {stats.get('input_sentences', 0) - len(sentences)}\n\n")
                
                # Layer-by-Layer Analysis
                if detailed and 'layer_results' in stats:
                    f.write("## Layer-by-Layer Analysis\n\n")
                    f.write("| Layer | Input | Output | Retention | Time (s) |\n")
                    f.write("|-------|-------|--------|-----------|----------|\n")
                    
                    for layer_result in stats['layer_results']:
                        layer_name = layer_result.get('layer', '').title()
                        input_count = layer_result.get('input_count', 0)
                        output_count = layer_result.get('output_count', 0)
                        retention = layer_result.get('retention_rate', 0) * 100
                        time_taken = layer_result.get('processing_time', 0)
                        
                        f.write(f"| {layer_name} | {input_count} | {output_count} | {retention:.1f}% | {time_taken:.3f} |\n")
                    
                    f.write("\n")
                
                # Quality Metrics
                if detailed:
                    quality_metrics = self._calculate_quality_metrics(sentences, metadata)
                    f.write("## Quality Metrics\n\n")
                    f.write(f"- **Average Sentence Length:** {quality_metrics['avg_sentence_length']:.1f} characters\n")
                    f.write(f"- **Medical Terms Detected:** {quality_metrics['medical_terms_count']}\n")
                    f.write(f"- **Complete Sentences:** {quality_metrics['complete_sentences_count']}\n")
                    f.write(f"- **Readability Score:** {quality_metrics['readability_score']:.2f}\n\n")
                
                # Filter Statistics
                if detailed and 'filter_statistics' in metadata:
                    f.write("## Filter Statistics\n\n")
                    filter_stats = metadata['filter_statistics']
                    
                    for filter_name, stats_data in filter_stats.items():
                        f.write(f"### {filter_name.replace('_', ' ').title()}\n\n")
                        if isinstance(stats_data, dict):
                            for key, value in stats_data.items():
                                if isinstance(value, (int, float)):
                                    f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
                        f.write("\n")
                
                # Output Sentences
                f.write("## Filtered Sentences\n\n")
                if sentences:
                    for i, sentence in enumerate(sentences, 1):
                        f.write(f"{i}. {sentence}\n\n")
                else:
                    f.write("*No sentences passed the filtering criteria.*\n\n")
                
                # System Information
                f.write("## System Information\n\n")
                sys_info = self._get_system_info()
                f.write(f"- **Platform:** {sys_info['platform']}\n")
                f.write(f"- **Python Version:** {sys_info['python_version']}\n")
                f.write(f"- **Architecture:** {sys_info['architecture']}\n")
                f.write(f"- **Processor:** {sys_info['processor']}\n\n")
                
                # Footer
                f.write("---\n")
                f.write(f"*Report generated by txtIntelligentReader v{self.VERSION}*\n")
            
            self.log_info(f"Markdown report saved to: {output_path}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to save markdown report: {str(e)}")
            return False
    
    def save_csv_statistics(self, metadata: Dict[str, Any], 
                          output_path: Union[str, Path]) -> bool:
        """
        Save processing statistics in CSV format.
        
        Args:
            metadata: Processing metadata
            output_path: Path to output CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Timestamp', 'Input_File', 'Input_Sentences', 'Output_Sentences',
                    'Retention_Rate', 'Processing_Time', 'Layers_Applied',
                    'Health_Threshold', 'Completeness_Threshold', 'Quality_Threshold'
                ])
                
                # Data row
                stats = metadata.get('statistics', {})
                config = metadata.get('configuration', {})
                
                writer.writerow([
                    datetime.now().isoformat(),
                    metadata.get('input_file', 'Unknown'),
                    stats.get('input_sentences', 0),
                    stats.get('output_sentences', 0),
                    f"{stats.get('overall_retention_rate', 0)*100:.1f}%",
                    f"{metadata.get('processing_time', 0):.3f}s",
                    '; '.join(metadata.get('layers_applied', [])),
                    config.get('health_threshold', 'N/A'),
                    config.get('completeness_threshold', 'N/A'),
                    config.get('quality_threshold', 'N/A')
                ])
            
            self.log_info(f"CSV statistics saved to: {output_path}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to save CSV statistics: {str(e)}")
            return False
    
    def save_html_report(self, sentences: List[str], metadata: Dict[str, Any], 
                        output_path: Union[str, Path]) -> bool:
        """
        Generate and save an HTML report with interactive features.
        
        Args:
            sentences: List of filtered sentences
            metadata: Processing metadata
            output_path: Path to output HTML file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path = Path(output_path)
            
            # Generate HTML content
            html_content = self._generate_html_report(sentences, metadata)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.log_info(f"HTML report saved to: {output_path}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to save HTML report: {str(e)}")
            return False
    
    def generate_processing_summary(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive processing summary.
        
        Args:
            metadata: Processing metadata
            
        Returns:
            Dictionary with summary statistics
        """
        stats = metadata.get('statistics', {})
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'version': self.VERSION,
            'input_file': metadata.get('input_file', 'Unknown'),
            'processing_time': metadata.get('processing_time', 0),
            'layers_applied': metadata.get('layers_applied', []),
            'sentence_counts': {
                'input': stats.get('input_sentences', 0),
                'output': stats.get('output_sentences', 0),
                'filtered_out': stats.get('input_sentences', 0) - stats.get('output_sentences', 0)
            },
            'retention_rate': stats.get('overall_retention_rate', 0),
            'layer_performance': []
        }
        
        # Add layer performance
        for layer_result in stats.get('layer_results', []):
            summary['layer_performance'].append({
                'layer': layer_result.get('layer', ''),
                'input_count': layer_result.get('input_count', 0),
                'output_count': layer_result.get('output_count', 0),
                'retention_rate': layer_result.get('retention_rate', 0),
                'processing_time': layer_result.get('processing_time', 0)
            })
        
        return summary
    
    def _calculate_quality_metrics(self, sentences: List[str], 
                                 metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality metrics for the filtered sentences."""
        if not sentences:
            return {
                'avg_sentence_length': 0,
                'medical_terms_count': 0,
                'complete_sentences_count': 0,
                'readability_score': 0
            }
        
        # Basic metrics
        total_length = sum(len(sentence) for sentence in sentences)
        avg_length = total_length / len(sentences)
        
        # Count complete sentences (ending with proper punctuation)
        complete_sentences = sum(1 for s in sentences if s.strip().endswith(('.', '!', '?')))
        
        # Simple medical terms detection
        medical_terms = [
            'patient', 'treatment', 'medication', 'diagnosis', 'symptoms', 'therapy',
            'doctor', 'hospital', 'medical', 'health', 'disease', 'condition',
            'clinical', 'surgery', 'prescription', 'dosage', 'recovery'
        ]
        
        medical_terms_count = 0
        for sentence in sentences:
            sentence_lower = sentence.lower()
            medical_terms_count += sum(1 for term in medical_terms if term in sentence_lower)
        
        # Simple readability score (based on sentence length and complexity)
        avg_words_per_sentence = sum(len(s.split()) for s in sentences) / len(sentences)
        readability_score = max(0, min(10, 10 - (avg_words_per_sentence - 15) * 0.1))
        
        return {
            'avg_sentence_length': avg_length,
            'medical_terms_count': medical_terms_count,
            'complete_sentences_count': complete_sentences,
            'readability_score': readability_score,
            'avg_words_per_sentence': avg_words_per_sentence
        }
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information for metadata."""
        return {
            'platform': platform.platform(),
            'python_version': sys.version.split()[0],
            'architecture': platform.architecture()[0],
            'processor': platform.processor() or 'Unknown',
            'machine': platform.machine()
        }
    
    def _generate_html_report(self, sentences: List[str], 
                            metadata: Dict[str, Any]) -> str:
        """Generate HTML report content."""
        stats = metadata.get('statistics', {})
        quality_metrics = self._calculate_quality_metrics(sentences, metadata)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>txtIntelligentReader Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .metric-label {{ color: #7f8c8d; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #3498db; color: white; }}
        .sentence-list {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .sentence-item {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #3498db; }}
        .footer {{ margin-top: 40px; text-align: center; color: #7f8c8d; border-top: 1px solid #ddd; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>txtIntelligentReader Processing Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Version:</strong> {self.VERSION}</p>
        
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{stats.get('input_sentences', 0)}</div>
                <div class="metric-label">Input Sentences</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(sentences)}</div>
                <div class="metric-label">Output Sentences</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{stats.get('overall_retention_rate', 0)*100:.1f}%</div>
                <div class="metric-label">Retention Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metadata.get('processing_time', 0):.3f}s</div>
                <div class="metric-label">Processing Time</div>
            </div>
        </div>
        
        <h2>Layer Performance</h2>
        <table>
            <thead>
                <tr><th>Layer</th><th>Input</th><th>Output</th><th>Retention</th><th>Time (s)</th></tr>
            </thead>
            <tbody>
"""
        
        # Add layer results to table
        for layer_result in stats.get('layer_results', []):
            layer_name = layer_result.get('layer', '').title()
            input_count = layer_result.get('input_count', 0)
            output_count = layer_result.get('output_count', 0)
            retention = layer_result.get('retention_rate', 0) * 100
            time_taken = layer_result.get('processing_time', 0)
            
            html_template += f"""
                <tr>
                    <td>{layer_name}</td>
                    <td>{input_count}</td>
                    <td>{output_count}</td>
                    <td>{retention:.1f}%</td>
                    <td>{time_taken:.3f}</td>
                </tr>
"""
        
        html_template += f"""
            </tbody>
        </table>
        
        <h2>Quality Metrics</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{quality_metrics['avg_sentence_length']:.1f}</div>
                <div class="metric-label">Avg Sentence Length</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{quality_metrics['medical_terms_count']}</div>
                <div class="metric-label">Medical Terms</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{quality_metrics['complete_sentences_count']}</div>
                <div class="metric-label">Complete Sentences</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{quality_metrics['readability_score']:.1f}</div>
                <div class="metric-label">Readability Score</div>
            </div>
        </div>
        
        <h2>Filtered Sentences</h2>
        <div class="sentence-list">
"""
        
        # Add sentences
        if sentences:
            for i, sentence in enumerate(sentences, 1):
                html_template += f'<div class="sentence-item"><strong>{i}.</strong> {sentence}</div>\n'
        else:
            html_template += '<div class="sentence-item"><em>No sentences passed the filtering criteria.</em></div>'
        
        html_template += f"""
        </div>
        
        <div class="footer">
            <p>Report generated by txtIntelligentReader v{self.VERSION}</p>
            <p>Input File: {metadata.get('input_file', 'Unknown')}</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html_template
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats."""
        return ['txt', 'json', 'md', 'csv', 'html']
    
    def validate_output_path(self, output_path: Union[str, Path], 
                           format_type: str) -> bool:
        """
        Validate output path and format compatibility.
        
        Args:
            output_path: Path to output file
            format_type: Output format type
            
        Returns:
            True if valid, False otherwise
        """
        try:
            path = Path(output_path)
            
            # Check if directory exists or can be created
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check format compatibility
            if format_type not in self.get_supported_formats():
                self.log_error(f"Unsupported format: {format_type}")
                return False
            
            # Check file extension matches format
            expected_extensions = {
                'txt': ['.txt'],
                'json': ['.json'],
                'md': ['.md', '.markdown'],
                'csv': ['.csv'],
                'html': ['.html', '.htm']
            }
            
            if format_type in expected_extensions:
                if path.suffix.lower() not in expected_extensions[format_type]:
                    self.log_warning(f"File extension {path.suffix} may not match format {format_type}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Invalid output path: {str(e)}")
            return False
