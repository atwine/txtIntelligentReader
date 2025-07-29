#!/usr/bin/env python3
"""
Comprehensive integration tests for txtIntelligentReader.

Tests end-to-end processing pipeline, batch processing, all output formats,
multi-file processing, error recovery scenarios, performance integration,
CLI integration, and real-world workflows.
"""

import sys
import pytest
import tempfile
import json
import time
import subprocess
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from pipeline.text_processor import TextProcessor
from pipeline.filter_pipeline import FilterPipeline
from utils.output_formatter import OutputFormatter
from utils.error_handler import ErrorHandler
from utils.config_loader import ConfigLoader


class TestFullPipelineIntegration:
    """Integration tests for full processing pipeline."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Default configuration
        self.config = {
            'health_threshold': 0.3,
            'quality_threshold': 0.7,
            'completeness_threshold': 0.6,
            'output_format': 'txt',
            'use_spacy': False,
            'llm_client': None
        }
        
        # Create test processor
        self.processor = TextProcessor(self.config)
        
        # Sample medical text content
        self.medical_content = """
        Patient Demographics and Medical History
        
        Patient shows significant improvement after receiving prescribed medication for hypertension.
        @@@ HEADER: MEDICAL RECORD @@@
        The weather outside is beautiful today with clear skies.
        
        Doctor adjusted medication dosage based on patient response to treatment.
        Blood pressure readings have returned to normal range after two weeks.
        
        ### FOOTER: Page 1 of 3 ###
        
        Surgery was performed successfully with no post-operative complications.
        Patient reported reduced symptoms and improved quality of life.
        
        Random noise text that should be filtered out.
        
        Follow-up appointment scheduled for next month to monitor progress.
        Lab results showed normal glucose levels within acceptable range.
        
        The patient's family history includes diabetes and cardiovascular disease.
        Treatment plan includes continued medication and lifestyle modifications.
        """
        
        # Create test input file
        self.test_file = self.temp_dir / "medical_record.txt"
        self.test_file.write_text(self.medical_content.strip())
    
    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_processing(self):
        """Test complete end-to-end processing pipeline."""
        output_file = self.temp_dir / "processed_output.txt"
        
        # Process file through complete pipeline
        result = self.processor.process_file(
            str(self.test_file),
            str(output_file),
            output_format='txt'
        )
        
        # Verify processing success
        assert result['success'] == True
        assert len(result['filtered_sentences']) > 0
        assert output_file.exists()
        
        # Verify content quality
        filtered_sentences = result['filtered_sentences']
        
        # Should contain medical sentences
        medical_sentences = [s for s in filtered_sentences if any(
            term in s.lower() for term in ['patient', 'medication', 'blood', 'surgery', 'treatment']
        )]
        assert len(medical_sentences) >= 5
        
        # Should filter out noise
        noise_sentences = [s for s in filtered_sentences if any(
            noise in s for noise in ['@@@', '###', 'weather', 'beautiful']
        )]
        assert len(noise_sentences) == 0
        
        # Verify statistics
        stats = result['statistics']
        assert stats['total_sentences'] > len(filtered_sentences)
        assert 0 < stats['retention_rate'] < 1
        assert stats['processing_time'] > 0
    
    def test_all_output_formats_integration(self):
        """Test integration with all output formats."""
        formats = ['txt', 'json', 'md', 'csv', 'html']
        results = {}
        
        for fmt in formats:
            output_file = self.temp_dir / f"output.{fmt}"
            
            result = self.processor.process_file(
                str(self.test_file),
                str(output_file),
                output_format=fmt
            )
            
            results[fmt] = result
            
            # Verify processing success
            assert result['success'] == True
            assert output_file.exists()
            assert output_file.stat().st_size > 0
        
        # All formats should have same filtered content
        base_sentences = results['txt']['filtered_sentences']
        for fmt in formats[1:]:  # Skip txt as it's the base
            assert results[fmt]['filtered_sentences'] == base_sentences
        
        # Verify format-specific content
        # JSON should be valid JSON
        json_file = self.temp_dir / "output.json"
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        assert 'filtered_sentences' in json_data
        assert 'statistics' in json_data
        
        # Markdown should have headers
        md_file = self.temp_dir / "output.md"
        md_content = md_file.read_text(encoding='utf-8')
        assert '# txtIntelligentReader' in md_content
        assert '## Processing Results' in md_content
        
        # HTML should have HTML tags
        html_file = self.temp_dir / "output.html"
        html_content = html_file.read_text(encoding='utf-8')
        assert '<html>' in html_content
        assert '<title>' in html_content
    
    def test_batch_processing_integration(self):
        """Test batch processing with multiple files."""
        # Create multiple test files
        test_files = []
        for i in range(5):
            test_file = self.temp_dir / f"medical_record_{i}.txt"
            content = f"""
            Patient {i} shows improvement after treatment.
            Doctor prescribed medication for condition {i}.
            Blood pressure readings are normal for patient {i}.
            Surgery was successful for case {i}.
            Follow-up scheduled for patient {i}.
            """
            test_file.write_text(content.strip())
            test_files.append(str(test_file))
        
        # Process all files
        batch_results = []
        total_processing_time = 0
        
        for i, test_file in enumerate(test_files):
            output_file = self.temp_dir / f"batch_output_{i}.txt"
            
            start_time = time.time()
            result = self.processor.process_file(test_file, str(output_file))
            processing_time = time.time() - start_time
            
            batch_results.append(result)
            total_processing_time += processing_time
        
        # Verify all processed successfully
        assert all(r['success'] for r in batch_results)
        assert all(len(r['filtered_sentences']) > 0 for r in batch_results)
        
        # Verify performance (should process 5 files in reasonable time)
        assert total_processing_time < 30.0  # Less than 30 seconds
        
        # Verify consistent processing
        sentence_counts = [len(r['filtered_sentences']) for r in batch_results]
        # All files have similar content, so sentence counts should be similar
        assert max(sentence_counts) - min(sentence_counts) <= 2
    
    def test_multi_file_processing_workflow(self):
        """Test multi-file processing workflow."""
        # Create different types of medical documents
        documents = {
            'patient_history.txt': """
            Patient has a history of hypertension and diabetes.
            Previous treatments included medication and lifestyle changes.
            Family history shows cardiovascular disease.
            """,
            'treatment_notes.txt': """
            Current treatment plan includes daily medication.
            Patient response to treatment has been positive.
            Side effects are minimal and manageable.
            """,
            'lab_results.txt': """
            Blood glucose levels are within normal range.
            Cholesterol levels have improved significantly.
            Liver function tests show normal results.
            """,
            'surgery_report.txt': """
            Surgical procedure was completed successfully.
            No complications occurred during surgery.
            Post-operative recovery is progressing well.
            """
        }
        
        # Create files and process each
        processing_results = {}
        
        for filename, content in documents.items():
            # Create file
            doc_file = self.temp_dir / filename
            doc_file.write_text(content.strip())
            
            # Process with different output formats
            for fmt in ['txt', 'json']:
                output_file = self.temp_dir / f"{filename.stem}_processed.{fmt}"
                
                result = self.processor.process_file(
                    str(doc_file),
                    str(output_file),
                    output_format=fmt
                )
                
                processing_results[f"{filename}_{fmt}"] = result
        
        # Verify all processed successfully
        assert all(r['success'] for r in processing_results.values())
        
        # Aggregate statistics
        total_sentences = sum(r['statistics']['total_sentences'] 
                            for r in processing_results.values() if 'txt' in str(r))
        total_filtered = sum(len(r['filtered_sentences']) 
                           for r in processing_results.values() if 'txt' in str(r))
        
        assert total_sentences > total_filtered
        assert total_filtered > 0
    
    def test_error_recovery_scenarios(self):
        """Test error recovery in various scenarios."""
        # Test 1: Non-existent input file
        result1 = self.processor.process_file(
            "nonexistent_file.txt",
            str(self.temp_dir / "output1.txt")
        )
        assert result1['success'] == False
        
        # Test 2: Invalid output directory
        result2 = self.processor.process_file(
            str(self.test_file),
            "/invalid/path/output.txt"
        )
        # Should handle gracefully (may succeed or fail based on implementation)
        assert isinstance(result2, dict)
        assert 'success' in result2
        
        # Test 3: Empty input file
        empty_file = self.temp_dir / "empty.txt"
        empty_file.write_text("")
        
        result3 = self.processor.process_file(
            str(empty_file),
            str(self.temp_dir / "output3.txt")
        )
        assert isinstance(result3, dict)
        assert result3['filtered_sentences'] == []
        
        # Test 4: Corrupted input file
        corrupted_file = self.temp_dir / "corrupted.txt"
        corrupted_file.write_bytes(b'\x00\x01\x02\x03\x04\x05')
        
        result4 = self.processor.process_file(
            str(corrupted_file),
            str(self.temp_dir / "output4.txt")
        )
        assert isinstance(result4, dict)
        # Should handle gracefully without crashing
    
    def test_performance_integration(self):
        """Test performance with realistic data volumes."""
        # Create large test file
        large_content = []
        for i in range(500):
            if i % 20 == 0:
                large_content.append("@@@ HEADER @@@")
            elif i % 15 == 0:
                large_content.append("The weather is nice today.")
            elif i % 10 == 0:
                large_content.append("Random noise text.")
            else:
                large_content.append(f"Patient {i} received medical treatment and showed improvement.")
        
        large_file = self.temp_dir / "large_medical_file.txt"
        large_file.write_text('\n'.join(large_content))
        
        # Performance test
        start_time = time.time()
        
        result = self.processor.process_file(
            str(large_file),
            str(self.temp_dir / "large_output.txt")
        )
        
        processing_time = time.time() - start_time
        
        # Verify performance
        assert result['success'] == True
        assert processing_time < 10.0  # Should process 500 sentences in < 10 seconds
        assert len(result['filtered_sentences']) > 200  # Should retain medical sentences
        
        # Verify memory efficiency (no memory leaks)
        import psutil
        import os
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        assert memory_mb < 500  # Should use less than 500MB
    
    def test_configuration_integration(self):
        """Test integration with different configurations."""
        configurations = [
            {
                'name': 'strict',
                'config': {
                    'health_threshold': 0.7,
                    'quality_threshold': 0.9,
                    'completeness_threshold': 0.8
                }
            },
            {
                'name': 'lenient',
                'config': {
                    'health_threshold': 0.1,
                    'quality_threshold': 0.3,
                    'completeness_threshold': 0.2
                }
            },
            {
                'name': 'balanced',
                'config': {
                    'health_threshold': 0.4,
                    'quality_threshold': 0.6,
                    'completeness_threshold': 0.5
                }
            }
        ]
        
        results = {}
        
        for config_set in configurations:
            # Create processor with specific configuration
            processor = TextProcessor(config_set['config'])
            
            output_file = self.temp_dir / f"output_{config_set['name']}.txt"
            
            result = processor.process_file(
                str(self.test_file),
                str(output_file)
            )
            
            results[config_set['name']] = result
        
        # Verify all configurations work
        assert all(r['success'] for r in results.values())
        
        # Verify configuration effects
        strict_count = len(results['strict']['filtered_sentences'])
        lenient_count = len(results['lenient']['filtered_sentences'])
        balanced_count = len(results['balanced']['filtered_sentences'])
        
        # Lenient should retain more sentences than strict
        assert lenient_count >= balanced_count >= strict_count
        
        # All should retain at least some sentences
        assert all(len(r['filtered_sentences']) > 0 for r in results.values())
    
    def test_real_world_medical_document_processing(self):
        """Test with realistic medical document content."""
        realistic_content = """
        PATIENT MEDICAL RECORD
        
        Patient ID: 12345
        Date: 2024-01-15
        
        Chief Complaint:
        Patient presents with chest pain and shortness of breath.
        
        History of Present Illness:
        The patient is a 65-year-old male with a history of hypertension and diabetes.
        He reports experiencing chest pain for the past 3 days.
        Pain is described as crushing and radiates to the left arm.
        Associated symptoms include nausea and diaphoresis.
        
        Past Medical History:
        - Hypertension diagnosed 10 years ago
        - Type 2 diabetes mellitus diagnosed 5 years ago
        - Previous myocardial infarction 2 years ago
        
        Medications:
        - Lisinopril 10mg daily
        - Metformin 500mg twice daily
        - Aspirin 81mg daily
        - Atorvastatin 20mg daily
        
        Physical Examination:
        Vital signs: BP 150/95, HR 88, RR 18, Temp 98.6°F
        Cardiovascular: Regular rate and rhythm, no murmurs
        Pulmonary: Clear to auscultation bilaterally
        
        Assessment and Plan:
        1. Acute coronary syndrome - Start heparin, obtain cardiac enzymes
        2. Hypertension - Continue current medications
        3. Diabetes - Monitor blood glucose closely
        
        The patient was admitted for further evaluation and treatment.
        Cardiology consultation was requested.
        Serial ECGs and cardiac enzymes will be monitored.
        
        Discharge planning will include medication reconciliation.
        Follow-up appointment scheduled with primary care physician.
        Patient education provided regarding warning signs.
        """
        
        # Create realistic medical document
        medical_doc = self.temp_dir / "patient_record.txt"
        medical_doc.write_text(realistic_content.strip())
        
        # Process with multiple output formats
        formats = ['txt', 'json', 'md', 'html']
        results = {}
        
        for fmt in formats:
            output_file = self.temp_dir / f"processed_record.{fmt}"
            
            result = self.processor.process_file(
                str(medical_doc),
                str(output_file),
                output_format=fmt
            )
            
            results[fmt] = result
        
        # Verify processing success
        assert all(r['success'] for r in results.values())
        
        # Verify medical content retention
        filtered_sentences = results['txt']['filtered_sentences']
        
        # Should retain key medical information
        medical_keywords = [
            'patient', 'chest pain', 'hypertension', 'diabetes',
            'medication', 'blood pressure', 'treatment', 'diagnosis'
        ]
        
        retained_medical_content = 0
        for sentence in filtered_sentences:
            if any(keyword in sentence.lower() for keyword in medical_keywords):
                retained_medical_content += 1
        
        assert retained_medical_content >= 10  # Should retain significant medical content
        
        # Verify statistics are reasonable
        stats = results['txt']['statistics']
        assert stats['retention_rate'] > 0.3  # Should retain at least 30% of content
        assert stats['retention_rate'] < 0.9   # Should filter out some content
    
    def test_concurrent_processing_integration(self):
        """Test concurrent processing scenarios."""
        import threading
        import queue
        
        # Create multiple test files
        test_files = []
        for i in range(3):
            test_file = self.temp_dir / f"concurrent_test_{i}.txt"
            content = f"""
            Patient {i} medical record.
            Treatment plan for patient {i} includes medication.
            Blood work results for patient {i} are normal.
            Follow-up scheduled for patient {i} next week.
            """
            test_file.write_text(content.strip())
            test_files.append(str(test_file))
        
        # Process files concurrently
        results_queue = queue.Queue()
        errors_queue = queue.Queue()
        
        def process_file_thread(file_path, output_path):
            try:
                processor = TextProcessor(self.config)
                result = processor.process_file(file_path, output_path)
                results_queue.put(result)
            except Exception as e:
                errors_queue.put(e)
        
        # Start concurrent processing
        threads = []
        for i, test_file in enumerate(test_files):
            output_file = self.temp_dir / f"concurrent_output_{i}.txt"
            
            thread = threading.Thread(
                target=process_file_thread,
                args=(test_file, str(output_file))
            )
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Collect results
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        errors = []
        while not errors_queue.empty():
            errors.append(errors_queue.get())
        
        # Verify concurrent processing
        assert len(errors) == 0  # No errors should occur
        assert len(results) == 3  # All files should be processed
        assert all(r['success'] for r in results)


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test input file
        self.test_content = """
        Patient shows improvement after treatment.
        @@@ NOISE @@@
        Doctor prescribed medication for hypertension.
        Weather is nice today.
        Surgery was successful with no complications.
        """
        
        self.test_file = self.temp_dir / "test_input.txt"
        self.test_file.write_text(self.test_content.strip())
    
    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_basic_cli_integration(self):
        """Test basic CLI functionality."""
        output_file = self.temp_dir / "cli_output.txt"
        
        # Run CLI command
        result = subprocess.run([
            'python', 'src/main.py',
            str(self.test_file),
            '-o', str(output_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Verify CLI execution
        assert result.returncode == 0
        assert output_file.exists()
        
        # Verify output content
        content = output_file.read_text(encoding='utf-8')
        assert len(content) > 0
        assert "Patient shows improvement" in content
    
    def test_cli_output_formats(self):
        """Test CLI with different output formats."""
        formats = ['txt', 'json', 'md', 'csv', 'html']
        
        for fmt in formats:
            output_file = self.temp_dir / f"cli_output.{fmt}"
            
            result = subprocess.run([
                'python', 'src/main.py',
                str(self.test_file),
                '-o', str(output_file),
                '--format', fmt
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            assert result.returncode == 0
            assert output_file.exists()
            assert output_file.stat().st_size > 0
    
    def test_cli_configuration_options(self):
        """Test CLI with configuration options."""
        output_file = self.temp_dir / "cli_config_output.txt"
        
        # Test with custom thresholds
        result = subprocess.run([
            'python', 'src/main.py',
            str(self.test_file),
            '-o', str(output_file),
            '--health-threshold', '0.2',
            '--quality-threshold', '0.6',
            '--completeness-threshold', '0.5'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        assert result.returncode == 0
        assert output_file.exists()
    
    def test_cli_error_handling(self):
        """Test CLI error handling."""
        # Test with non-existent input file
        result = subprocess.run([
            'python', 'src/main.py',
            'nonexistent_file.txt',
            '-o', str(self.temp_dir / "output.txt")
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Should handle error gracefully
        assert result.returncode != 0 or "error" in result.stderr.lower()
    
    def test_cli_debug_mode(self):
        """Test CLI debug mode."""
        output_file = self.temp_dir / "debug_output.txt"
        
        result = subprocess.run([
            'python', 'src/main.py',
            str(self.test_file),
            '-o', str(output_file),
            '--debug'
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        # Debug mode should provide additional output
        assert result.returncode == 0
        assert len(result.stdout) > 0 or len(result.stderr) > 0


def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Running Comprehensive Integration Tests")
    print("=" * 70)
    
    # Run pytest on this file
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, '-m', 'pytest', __file__, '-v', '--tb=short', '-x'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
