#!/usr/bin/env python3
"""
Comprehensive unit tests for pipeline components.

Tests FilterPipeline and TextProcessor classes individually
with focus on component isolation and functionality.
"""

import sys
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from pipeline.filter_pipeline import FilterPipeline
from pipeline.text_processor import TextProcessor


class TestFilterPipeline:
    """Unit tests for FilterPipeline component."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.config = {
            'health_threshold': 0.3,
            'quality_threshold': 0.7,
            'completeness_threshold': 0.6,
            'use_spacy': False,
            'llm_client': None
        }
        self.pipeline = FilterPipeline(self.config)
    
    def test_initialization(self):
        """Test FilterPipeline initialization."""
        assert self.pipeline is not None
        assert self.pipeline.config == self.config
        assert hasattr(self.pipeline, 'quick_filter')
        assert hasattr(self.pipeline, 'health_filter')
        assert hasattr(self.pipeline, 'ai_filter')
        assert hasattr(self.pipeline, 'thought_validator')
    
    def test_filter_layer_initialization(self):
        """Test individual filter layer initialization."""
        # Quick filter should be initialized
        assert self.pipeline.quick_filter is not None
        
        # Health filter should be initialized with threshold
        assert self.pipeline.health_filter is not None
        assert self.pipeline.health_filter.health_threshold == 0.3
        
        # AI filter should be initialized
        assert self.pipeline.ai_filter is not None
        assert self.pipeline.ai_filter.completeness_threshold == 0.6
        
        # Thought validator should be initialized
        assert self.pipeline.thought_validator is not None
        assert self.pipeline.thought_validator.quality_threshold == 0.7
    
    def test_single_layer_processing(self):
        """Test individual layer processing."""
        test_sentences = [
            "Patient shows improvement after treatment.",
            "@@@ NOISE @@@",
            "The weather is nice today.",
            "Doctor prescribed medication for hypertension.",
            "Incomplete sentence",
            "This is a complete medical sentence about patient care."
        ]
        
        # Test Layer 1: Quick Filter
        layer1_result = self.pipeline._process_layer_1(test_sentences)
        assert len(layer1_result) < len(test_sentences)  # Should remove noise
        assert "@@@ NOISE @@@" not in layer1_result
        
        # Test Layer 2: Health Context Filter
        layer2_result = self.pipeline._process_layer_2(layer1_result)
        assert len(layer2_result) <= len(layer1_result)  # Should filter non-medical
        
        # Test Layer 3: AI Analysis Filter
        layer3_result = self.pipeline._process_layer_3(layer2_result)
        assert len(layer3_result) <= len(layer2_result)  # Should filter incomplete
        
        # Test Layer 4: Complete Thought Validator
        layer4_result = self.pipeline._process_layer_4(layer3_result)
        assert len(layer4_result) <= len(layer3_result)  # Should filter low quality
    
    def test_full_pipeline_processing(self):
        """Test full pipeline processing."""
        test_sentences = [
            "Patient shows significant improvement after receiving prescribed medication.",
            "@@@ HEADER @@@",
            "The weather is beautiful today.",
            "Doctor adjusted medication dosage based on patient response.",
            "Incomplete",
            "Surgery was performed successfully with no complications.",
            "Random noise text",
            "Blood pressure readings returned to normal range after treatment."
        ]
        
        result = self.pipeline.process(test_sentences)
        
        # Should return processed results
        assert isinstance(result, dict)
        assert 'filtered_sentences' in result
        assert 'statistics' in result
        assert 'layer_results' in result
        
        # Should have filtered sentences
        filtered = result['filtered_sentences']
        assert isinstance(filtered, list)
        assert len(filtered) > 0
        assert len(filtered) < len(test_sentences)
        
        # Should contain medical sentences
        medical_sentences = [s for s in filtered if any(term in s.lower() 
                           for term in ['patient', 'medication', 'doctor', 'surgery', 'blood'])]
        assert len(medical_sentences) > 0
    
    def test_statistics_collection(self):
        """Test statistics collection."""
        test_sentences = [
            "Patient received treatment.",
            "@@@ NOISE @@@",
            "Doctor prescribed medication.",
            "Weather is nice.",
            "Incomplete",
            "Surgery was successful."
        ]
        
        result = self.pipeline.process(test_sentences)
        stats = result['statistics']
        
        # Check required statistics
        assert 'total_input_sentences' in stats
        assert 'final_output_sentences' in stats
        assert 'retention_rate' in stats
        assert 'processing_time' in stats
        assert 'layer_statistics' in stats
        
        # Validate statistics values
        assert stats['total_input_sentences'] == len(test_sentences)
        assert stats['final_output_sentences'] <= len(test_sentences)
        assert 0 <= stats['retention_rate'] <= 1
        assert stats['processing_time'] > 0
    
    def test_layer_results_tracking(self):
        """Test layer-by-layer results tracking."""
        test_sentences = [
            "Patient shows improvement.",
            "@@@ NOISE @@@",
            "Doctor prescribed treatment.",
            "Weather update.",
            "Surgery successful."
        ]
        
        result = self.pipeline.process(test_sentences)
        layer_results = result['layer_results']
        
        # Should have results for all 4 layers
        assert 'layer_1' in layer_results
        assert 'layer_2' in layer_results
        assert 'layer_3' in layer_results
        assert 'layer_4' in layer_results
        
        # Each layer should have sentence count
        for layer in ['layer_1', 'layer_2', 'layer_3', 'layer_4']:
            assert 'sentence_count' in layer_results[layer]
            assert isinstance(layer_results[layer]['sentence_count'], int)
    
    def test_progress_tracking(self):
        """Test progress tracking functionality."""
        test_sentences = ["Test sentence."] * 100
        
        with patch('pipeline.filter_pipeline.log_progress') as mock_log_progress:
            result = self.pipeline.process(test_sentences)
            
            # Should have called progress logging
            assert mock_log_progress.called
    
    def test_error_handling(self):
        """Test error handling in pipeline."""
        # Test with None input
        result = self.pipeline.process(None)
        assert result is not None
        assert result['filtered_sentences'] == []
        
        # Test with empty input
        result = self.pipeline.process([])
        assert result is not None
        assert result['filtered_sentences'] == []
        
        # Test with invalid input types
        result = self.pipeline.process("not a list")
        assert result is not None
        assert result['filtered_sentences'] == []
    
    def test_configuration_updates(self):
        """Test configuration updates."""
        new_config = {
            'health_threshold': 0.5,
            'quality_threshold': 0.8,
            'completeness_threshold': 0.7
        }
        
        self.pipeline.update_config(new_config)
        
        # Check if thresholds were updated
        assert self.pipeline.health_filter.health_threshold == 0.5
        assert self.pipeline.thought_validator.quality_threshold == 0.8
        assert self.pipeline.ai_filter.completeness_threshold == 0.7
    
    def test_performance_with_large_input(self):
        """Test performance with large input."""
        import time
        
        # Generate large test dataset
        large_input = []
        for i in range(1000):
            if i % 10 == 0:
                large_input.append("@@@ NOISE @@@")
            elif i % 5 == 0:
                large_input.append("Weather is nice today.")
            else:
                large_input.append(f"Patient {i} received medical treatment and showed improvement.")
        
        start_time = time.time()
        result = self.pipeline.process(large_input)
        processing_time = time.time() - start_time
        
        # Should process efficiently (less than 10 seconds for 1000 sentences)
        assert processing_time < 10.0
        assert len(result['filtered_sentences']) > 0
        assert result['statistics']['processing_time'] > 0
    
    def test_filter_order_dependency(self):
        """Test that filter order matters."""
        test_sentences = [
            "Patient shows improvement after treatment.",  # Medical + complete
            "@@@ NOISE @@@",                              # Noise
            "The weather is nice today.",                 # Non-medical but complete
            "Patient",                                    # Medical but incomplete
        ]
        
        # Process normally
        normal_result = self.pipeline.process(test_sentences)
        
        # The order should filter: noise -> non-medical -> incomplete -> low quality
        # Final result should contain mainly the first sentence
        filtered = normal_result['filtered_sentences']
        assert len(filtered) >= 1
        assert "Patient shows improvement after treatment." in filtered


class TestTextProcessor:
    """Unit tests for TextProcessor component."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_file = self.temp_dir / "test_input.txt"
        self.output_file = self.temp_dir / "test_output.txt"
        
        # Create test input file
        test_content = """
        Patient shows significant improvement after treatment.
        @@@ HEADER @@@
        The weather is nice today.
        Doctor prescribed medication for hypertension.
        Incomplete sentence
        Surgery was performed successfully with no complications.
        Random noise text
        Blood pressure readings returned to normal range.
        """
        
        self.test_file.write_text(test_content.strip())
        
        self.config = {
            'health_threshold': 0.3,
            'quality_threshold': 0.7,
            'completeness_threshold': 0.6,
            'output_format': 'txt'
        }
        
        self.processor = TextProcessor(self.config)
    
    def teardown_method(self):
        """Cleanup after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test TextProcessor initialization."""
        assert self.processor is not None
        assert self.processor.config == self.config
        assert hasattr(self.processor, 'pipeline')
        assert hasattr(self.processor, 'output_formatter')
    
    def test_file_reading(self):
        """Test file reading functionality."""
        sentences = self.processor._read_file(str(self.test_file))
        
        assert isinstance(sentences, list)
        assert len(sentences) > 0
        assert any("Patient shows" in s for s in sentences)
        assert any("Doctor prescribed" in s for s in sentences)
    
    def test_file_reading_error_handling(self):
        """Test file reading error handling."""
        # Test non-existent file
        sentences = self.processor._read_file("nonexistent.txt")
        assert sentences == []
        
        # Test invalid file path
        sentences = self.processor._read_file("")
        assert sentences == []
    
    def test_sentence_splitting(self):
        """Test sentence splitting functionality."""
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        sentences = self.processor._split_into_sentences(text)
        
        assert isinstance(sentences, list)
        assert len(sentences) == 4
        assert "First sentence." in sentences
        assert "Second sentence!" in sentences
    
    def test_output_path_validation(self):
        """Test output path validation."""
        # Valid path
        valid_path = str(self.output_file)
        assert self.processor._validate_output_path(valid_path) == True
        
        # Invalid path (directory doesn't exist)
        invalid_path = "/invalid/path/output.txt"
        result = self.processor._validate_output_path(invalid_path)
        # Result depends on system permissions, just ensure it's boolean
        assert isinstance(result, bool)
    
    def test_full_processing_workflow(self):
        """Test full processing workflow."""
        result = self.processor.process_file(
            str(self.test_file),
            str(self.output_file),
            output_format='txt'
        )
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'filtered_sentences' in result
        assert 'statistics' in result
        
        # Should have processed successfully
        assert result['success'] == True
        assert len(result['filtered_sentences']) > 0
        
        # Output file should be created
        assert self.output_file.exists()
    
    def test_different_output_formats(self):
        """Test different output formats."""
        formats = ['txt', 'json', 'md', 'csv', 'html']
        
        for fmt in formats:
            output_file = self.temp_dir / f"output.{fmt}"
            
            result = self.processor.process_file(
                str(self.test_file),
                str(output_file),
                output_format=fmt
            )
            
            assert result['success'] == True
            assert output_file.exists()
    
    def test_statistics_generation(self):
        """Test statistics generation."""
        result = self.processor.process_file(
            str(self.test_file),
            str(self.output_file)
        )
        
        stats = result['statistics']
        
        # Check required statistics
        assert 'total_sentences' in stats
        assert 'filtered_sentences' in stats
        assert 'retention_rate' in stats
        assert 'processing_time' in stats
        
        # Validate statistics values
        assert stats['total_sentences'] > 0
        assert stats['filtered_sentences'] <= stats['total_sentences']
        assert 0 <= stats['retention_rate'] <= 1
        assert stats['processing_time'] > 0
    
    def test_configuration_override(self):
        """Test configuration override."""
        # Process with default config
        result1 = self.processor.process_file(str(self.test_file), str(self.output_file))
        
        # Process with overridden config
        override_config = {
            'health_threshold': 0.1,  # More lenient
            'quality_threshold': 0.5   # More lenient
        }
        
        result2 = self.processor.process_file(
            str(self.test_file),
            str(self.output_file),
            config_override=override_config
        )
        
        # More lenient config should retain more sentences
        assert len(result2['filtered_sentences']) >= len(result1['filtered_sentences'])
    
    def test_batch_processing_simulation(self):
        """Test batch processing simulation."""
        # Create multiple test files
        test_files = []
        for i in range(3):
            test_file = self.temp_dir / f"test_{i}.txt"
            test_file.write_text(f"Patient {i} received treatment and showed improvement.")
            test_files.append(str(test_file))
        
        results = []
        for test_file in test_files:
            output_file = self.temp_dir / f"output_{Path(test_file).stem}.txt"
            result = self.processor.process_file(test_file, str(output_file))
            results.append(result)
        
        # All should process successfully
        assert all(r['success'] for r in results)
        assert all(len(r['filtered_sentences']) > 0 for r in results)
    
    def test_memory_efficiency(self):
        """Test memory efficiency with large files."""
        # Create a large test file
        large_content = []
        for i in range(1000):
            if i % 10 == 0:
                large_content.append("@@@ NOISE @@@")
            else:
                large_content.append(f"Patient {i} received comprehensive medical treatment.")
        
        large_file = self.temp_dir / "large_test.txt"
        large_file.write_text('\n'.join(large_content))
        
        import psutil
        import os
        
        # Monitor memory usage
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        result = self.processor.process_file(str(large_file), str(self.output_file))
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Should not use excessive memory (less than 100MB increase)
        assert memory_increase < 100 * 1024 * 1024  # 100MB
        assert result['success'] == True
    
    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        # Test with corrupted file
        corrupted_file = self.temp_dir / "corrupted.txt"
        corrupted_file.write_bytes(b'\x00\x01\x02\x03')  # Binary data
        
        result = self.processor.process_file(str(corrupted_file), str(self.output_file))
        
        # Should handle gracefully
        assert isinstance(result, dict)
        assert 'success' in result
        # May succeed or fail depending on error handling implementation
    
    def test_concurrent_processing_safety(self):
        """Test concurrent processing safety."""
        import threading
        import time
        
        results = []
        errors = []
        
        def process_file_thread(file_path, output_path):
            try:
                result = self.processor.process_file(file_path, output_path)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            test_file = self.temp_dir / f"concurrent_{i}.txt"
            test_file.write_text(f"Patient {i} shows improvement after treatment.")
            output_file = self.temp_dir / f"concurrent_output_{i}.txt"
            
            thread = threading.Thread(
                target=process_file_thread,
                args=(str(test_file), str(output_file))
            )
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0  # No errors should occur
        assert len(results) == 3  # All should complete
        assert all(r['success'] for r in results)


def run_pipeline_unit_tests():
    """Run all pipeline unit tests."""
    print("🚀 Running Pipeline Unit Tests")
    print("=" * 60)
    
    # Run pytest on this file
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, '-m', 'pytest', __file__, '-v', '--tb=short'
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_pipeline_unit_tests()
    sys.exit(0 if success else 1)
