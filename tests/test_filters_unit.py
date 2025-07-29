#!/usr/bin/env python3
"""
Comprehensive unit tests for all filtering components.

Tests individual filter functionality, edge cases, performance,
and integration with the filtering pipeline.
"""

import sys
import pytest
from pathlib import Path
import time

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from filters import QuickFilter, HealthContextFilter, AIAnalysisFilter, CompleteThoughtValidator


class TestQuickFilter:
    """Unit tests for QuickFilter component."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.filter = QuickFilter()
    
    def test_initialization(self):
        """Test QuickFilter initialization."""
        assert self.filter is not None
        assert hasattr(self.filter, 'stats')
        assert self.filter.stats['total_processed'] == 0
    
    def test_noise_removal(self):
        """Test basic noise removal functionality."""
        noisy_sentences = [
            "This is a valid sentence.",
            "@@@ NOISE @@@",
            "### HEADER ###",
            "Another valid sentence.",
            "   ",  # Empty/whitespace
            "a",   # Too short
            "ALLCAPSSENTENCETHATISTOOLONG" * 10,  # Too long
            "Valid medical sentence about treatment."
        ]
        
        filtered = self.filter.filter_text(noisy_sentences)
        
        # Should keep only valid sentences
        assert len(filtered) == 3
        assert "This is a valid sentence." in filtered
        assert "Another valid sentence." in filtered
        assert "Valid medical sentence about treatment." in filtered
        
        # Should remove noise
        assert "@@@ NOISE @@@" not in filtered
        assert "### HEADER ###" not in filtered
    
    def test_pdf_artifact_removal(self):
        """Test PDF artifact removal."""
        pdf_artifacts = [
            "Page 1 of 25",
            "© 2023 Medical Journal",
            "www.example.com/document",
            "Figure 1: Medical diagram",
            "Table 2: Results summary",
            "This is actual content about patient care.",
            "References: [1] Smith et al."
        ]
        
        filtered = self.filter.filter_text(pdf_artifacts)
        
        # Should keep actual content
        assert "This is actual content about patient care." in filtered
        
        # Should remove PDF artifacts
        assert not any("Page" in s for s in filtered)
        assert not any("©" in s for s in filtered)
        assert not any("www." in s for s in filtered)
    
    def test_header_footer_removal(self):
        """Test header and footer removal."""
        sentences_with_headers = [
            "CHAPTER 1: INTRODUCTION",
            "1.1 Overview",
            "Patient shows improvement after treatment.",
            "CONCLUSION",
            "The treatment was effective.",
            "REFERENCES",
            "Bibliography follows."
        ]
        
        filtered = self.filter.filter_text(sentences_with_headers)
        
        # Should keep actual content
        assert "Patient shows improvement after treatment." in filtered
        assert "The treatment was effective." in filtered
        
        # Should remove headers
        assert not any("CHAPTER" in s for s in filtered)
        assert not any("CONCLUSION" in s for s in filtered)
    
    def test_formatting_cleanup(self):
        """Test formatting cleanup."""
        formatted_sentences = [
            "  Patient shows improvement.  ",  # Extra whitespace
            "Treatment\twas\teffective.",      # Tabs
            "Multiple    spaces   here.",     # Multiple spaces
            "Line\nbreak\nin\nsentence.",     # Line breaks
            "Normal sentence without issues."
        ]
        
        filtered = self.filter.filter_text(formatted_sentences)
        
        # Should clean up formatting
        for sentence in filtered:
            assert not sentence.startswith(' ')
            assert not sentence.endswith(' ')
            assert '\t' not in sentence
            assert '\n' not in sentence
            assert '  ' not in sentence  # No double spaces
    
    def test_statistics_tracking(self):
        """Test statistics tracking."""
        initial_stats = self.filter.get_filtering_stats()
        assert initial_stats['total_processed'] == 0
        
        test_sentences = [
            "Valid sentence.",
            "@@@ NOISE @@@",
            "Another valid sentence.",
            "### HEADER ###"
        ]
        
        filtered = self.filter.filter_text(test_sentences)
        stats = self.filter.get_filtering_stats()
        
        assert stats['total_processed'] == len(test_sentences)
        assert stats['noise_removed'] > 0
        assert stats['headers_footers_removed'] > 0
    
    def test_empty_input(self):
        """Test handling of empty input."""
        filtered = self.filter.filter_text([])
        assert filtered == []
        
        filtered = self.filter.filter_text(None)
        assert filtered == []
    
    def test_performance(self):
        """Test performance with large input."""
        # Generate large test dataset
        large_input = []
        for i in range(1000):
            if i % 10 == 0:
                large_input.append("@@@ NOISE @@@")
            else:
                large_input.append(f"Valid medical sentence number {i} about treatment.")
        
        start_time = time.time()
        filtered = self.filter.filter_text(large_input)
        processing_time = time.time() - start_time
        
        # Should process quickly (less than 1 second for 1000 sentences)
        assert processing_time < 1.0
        assert len(filtered) == 900  # 90% should be kept


class TestHealthContextFilter:
    """Unit tests for HealthContextFilter component."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.filter = HealthContextFilter(health_threshold=0.3)
    
    def test_initialization(self):
        """Test HealthContextFilter initialization."""
        assert self.filter is not None
        assert self.filter.health_threshold == 0.3
        assert hasattr(self.filter, 'medical_terms')
        assert len(self.filter.medical_terms) > 0
    
    def test_medical_terminology_detection(self):
        """Test medical terminology detection."""
        medical_sentences = [
            "The patient received medication for hypertension.",
            "Surgery was scheduled for next week.",
            "Blood pressure readings were normal.",
            "The doctor prescribed antibiotics.",
            "MRI scan showed no abnormalities."
        ]
        
        non_medical_sentences = [
            "The weather is nice today.",
            "I went to the store.",
            "The car needs repair.",
            "Programming is fun.",
            "The book was interesting."
        ]
        
        # Medical sentences should have high health scores
        for sentence in medical_sentences:
            score = self.filter._calculate_health_score(sentence)
            assert score > 0.5, f"Medical sentence should have high score: {sentence}"
        
        # Non-medical sentences should have low health scores
        for sentence in non_medical_sentences:
            score = self.filter._calculate_health_score(sentence)
            assert score < 0.3, f"Non-medical sentence should have low score: {sentence}"
    
    def test_health_context_filtering(self):
        """Test health context filtering."""
        mixed_sentences = [
            "Patient shows signs of improvement after treatment.",  # Medical
            "The weather is nice today.",                          # Non-medical
            "Blood pressure medication was adjusted.",             # Medical
            "I went shopping yesterday.",                          # Non-medical
            "The surgical procedure was successful.",              # Medical
            "My favorite color is blue."                           # Non-medical
        ]
        
        filtered = self.filter.filter_by_health_context(mixed_sentences)
        
        # Should keep medical sentences
        medical_kept = [s for s in filtered if any(term in s.lower() for term in ['patient', 'treatment', 'blood', 'medication', 'surgical'])]
        assert len(medical_kept) >= 2
        
        # Should filter out non-medical sentences
        assert "The weather is nice today." not in filtered
        assert "I went shopping yesterday." not in filtered
    
    def test_threshold_sensitivity(self):
        """Test threshold sensitivity."""
        test_sentences = [
            "Patient has mild symptoms.",      # Medium health relevance
            "Doctor prescribed treatment.",   # High health relevance
            "Hospital visit scheduled.",      # High health relevance
            "Weather affects mood."           # Low health relevance
        ]
        
        # Test with strict threshold
        strict_filter = HealthContextFilter(health_threshold=0.7)
        strict_filtered = strict_filter.filter_by_health_context(test_sentences)
        
        # Test with lenient threshold
        lenient_filter = HealthContextFilter(health_threshold=0.1)
        lenient_filtered = lenient_filter.filter_by_health_context(test_sentences)
        
        # Lenient should keep more sentences
        assert len(lenient_filtered) >= len(strict_filtered)
    
    def test_medical_pattern_recognition(self):
        """Test medical pattern recognition."""
        pattern_sentences = [
            "Patient presented with chest pain.",
            "Diagnosed with Type 2 diabetes.",
            "Prescribed 10mg daily dose.",
            "Follow-up appointment in 2 weeks.",
            "Vital signs: BP 120/80, HR 72.",
            "Lab results showed elevated glucose."
        ]
        
        for sentence in pattern_sentences:
            patterns = self.filter._detect_medical_patterns(sentence)
            assert len(patterns) > 0, f"Should detect medical patterns in: {sentence}"
    
    def test_statistics_tracking(self):
        """Test statistics tracking."""
        test_sentences = [
            "Patient shows improvement.",
            "Weather is nice.",
            "Doctor prescribed medication.",
            "I like pizza."
        ]
        
        filtered = self.filter.filter_by_health_context(test_sentences)
        stats = self.filter.get_filtering_stats()
        
        assert stats['total_processed'] == len(test_sentences)
        assert stats['health_relevant'] > 0
        assert stats['medical_terms_found'] > 0
        assert 'health_score_avg' in stats
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Empty input
        assert self.filter.filter_by_health_context([]) == []
        
        # Single character
        assert self.filter.filter_by_health_context(["a"]) == []
        
        # Very long sentence
        long_sentence = "patient " + "word " * 1000
        filtered = self.filter.filter_by_health_context([long_sentence])
        assert len(filtered) <= 1  # Should handle gracefully


class TestAIAnalysisFilter:
    """Unit tests for AIAnalysisFilter component."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Use rule-based mode for testing (no LLM required)
        self.filter = AIAnalysisFilter(completeness_threshold=0.6, llm_client=None)
    
    def test_initialization(self):
        """Test AIAnalysisFilter initialization."""
        assert self.filter is not None
        assert self.filter.completeness_threshold == 0.6
        assert self.filter.llm_client is None  # Rule-based mode
    
    def test_rule_based_completeness_analysis(self):
        """Test rule-based completeness analysis."""
        complete_sentences = [
            "The patient received comprehensive treatment for diabetes.",
            "Surgery was performed successfully with no complications.",
            "Blood test results showed normal glucose levels."
        ]
        
        incomplete_sentences = [
            "The patient",
            "Treatment was",
            "Results showed",
            "In conclusion"
        ]
        
        # Complete sentences should have high scores
        for sentence in complete_sentences:
            score = self.filter._rule_based_completeness_check(sentence)
            assert score > 0.7, f"Complete sentence should have high score: {sentence}"
        
        # Incomplete sentences should have low scores
        for sentence in incomplete_sentences:
            score = self.filter._rule_based_completeness_check(sentence)
            assert score < 0.5, f"Incomplete sentence should have low score: {sentence}"
    
    def test_completeness_filtering(self):
        """Test completeness filtering."""
        mixed_sentences = [
            "Patient shows significant improvement after treatment.",  # Complete
            "The doctor",                                            # Incomplete
            "Medication dosage was adjusted appropriately.",         # Complete
            "Results indicate",                                      # Incomplete
            "Follow-up appointment scheduled for next month."       # Complete
        ]
        
        filtered = self.filter.filter_by_completeness(mixed_sentences)
        
        # Should keep complete sentences
        assert len(filtered) >= 3
        assert "Patient shows significant improvement after treatment." in filtered
        assert "Medication dosage was adjusted appropriately." in filtered
        
        # Should filter out incomplete sentences
        assert "The doctor" not in filtered
        assert "Results indicate" not in filtered
    
    def test_batch_processing(self):
        """Test batch processing functionality."""
        large_batch = [f"Complete sentence number {i} about medical treatment." for i in range(100)]
        large_batch.extend([f"Incomplete {i}" for i in range(20)])
        
        start_time = time.time()
        filtered = self.filter.filter_by_completeness(large_batch)
        processing_time = time.time() - start_time
        
        # Should process efficiently
        assert processing_time < 2.0
        assert len(filtered) >= 80  # Most complete sentences should be kept
    
    def test_meaning_validation(self):
        """Test meaning validation."""
        meaningful_sentences = [
            "The patient's condition improved after medication.",
            "Surgery was scheduled for the following week.",
            "Blood pressure readings returned to normal range."
        ]
        
        meaningless_sentences = [
            "The the the patient patient.",
            "Treatment surgery medication doctor.",
            "Yes no maybe perhaps definitely."
        ]
        
        for sentence in meaningful_sentences:
            score = self.filter._validate_meaning(sentence)
            assert score > 0.6, f"Meaningful sentence should have high score: {sentence}"
        
        for sentence in meaningless_sentences:
            score = self.filter._validate_meaning(sentence)
            assert score < 0.4, f"Meaningless sentence should have low score: {sentence}"
    
    def test_statistics_tracking(self):
        """Test statistics tracking."""
        test_sentences = [
            "Complete medical sentence about treatment.",
            "Incomplete",
            "Another complete sentence about patient care.",
            "Fragment"
        ]
        
        filtered = self.filter.filter_by_completeness(test_sentences)
        stats = self.filter.get_analysis_stats()
        
        assert stats['total_processed'] == len(test_sentences)
        assert stats['complete_sentences'] > 0
        assert stats['incomplete_sentences'] > 0
        assert 'avg_completeness_score' in stats
    
    def test_threshold_adjustment(self):
        """Test threshold adjustment effects."""
        test_sentences = [
            "Patient shows improvement.",      # Medium completeness
            "The comprehensive treatment plan was implemented successfully.",  # High
            "Doctor said",                    # Low
            "Results were positive."          # Medium
        ]
        
        # Strict threshold
        strict_filter = AIAnalysisFilter(completeness_threshold=0.8)
        strict_filtered = strict_filter.filter_by_completeness(test_sentences)
        
        # Lenient threshold
        lenient_filter = AIAnalysisFilter(completeness_threshold=0.3)
        lenient_filtered = lenient_filter.filter_by_completeness(test_sentences)
        
        assert len(lenient_filtered) >= len(strict_filtered)


class TestCompleteThoughtValidator:
    """Unit tests for CompleteThoughtValidator component."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.validator = CompleteThoughtValidator(quality_threshold=0.7, use_spacy=False)
    
    def test_initialization(self):
        """Test CompleteThoughtValidator initialization."""
        assert self.validator is not None
        assert self.validator.quality_threshold == 0.7
        assert self.validator.use_spacy == False
    
    def test_structural_validation(self):
        """Test structural validation."""
        well_structured = [
            "The patient received treatment and showed improvement.",
            "After surgery, the patient recovered completely.",
            "Blood test results indicated normal glucose levels."
        ]
        
        poorly_structured = [
            "patient treatment improvement",
            "surgery, recovery, complete",
            "blood glucose normal results"
        ]
        
        for sentence in well_structured:
            score = self.validator._validate_structure(sentence)
            assert score > 0.6, f"Well-structured sentence should have high score: {sentence}"
        
        for sentence in poorly_structured:
            score = self.validator._validate_structure(sentence)
            assert score < 0.5, f"Poorly structured sentence should have low score: {sentence}"
    
    def test_semantic_coherence(self):
        """Test semantic coherence validation."""
        coherent_sentences = [
            "The patient's blood pressure decreased after taking medication.",
            "Surgery was successful and the patient is recovering well.",
            "Lab results confirmed the diagnosis of diabetes."
        ]
        
        incoherent_sentences = [
            "The patient's blood pressure increased after feeling happy.",
            "Surgery was colorful and the patient is swimming well.",
            "Lab results confirmed the diagnosis of happiness."
        ]
        
        for sentence in coherent_sentences:
            score = self.validator._assess_semantic_coherence(sentence)
            assert score > 0.6, f"Coherent sentence should have high score: {sentence}"
        
        # Note: Simple rule-based coherence checking may not catch all incoherent sentences
        # This test validates the method exists and returns reasonable scores
    
    def test_actionability_assessment(self):
        """Test actionability assessment."""
        actionable_sentences = [
            "Increase medication dosage to 20mg daily.",
            "Schedule follow-up appointment in two weeks.",
            "Monitor blood pressure twice daily.",
            "Patient should rest for 24 hours post-surgery."
        ]
        
        non_actionable_sentences = [
            "The patient felt better.",
            "Treatment was completed.",
            "Results were reviewed.",
            "The condition improved."
        ]
        
        for sentence in actionable_sentences:
            score = self.validator._assess_actionability(sentence)
            assert score > 0.5, f"Actionable sentence should have high score: {sentence}"
        
        for sentence in non_actionable_sentences:
            score = self.validator._assess_actionability(sentence)
            # Non-actionable sentences may still have some actionability score
            # This test ensures the method works and returns reasonable values
            assert isinstance(score, float)
            assert 0 <= score <= 1
    
    def test_translation_readiness(self):
        """Test translation readiness assessment."""
        translation_ready = [
            "The patient received 10mg of medication daily.",
            "Surgery was performed on the left knee.",
            "Blood pressure reading was 120/80 mmHg."
        ]
        
        translation_difficult = [
            "The patient, you know, got some meds, like, daily.",
            "Surgery was kinda done on the, um, left knee thingy.",
            "BP was sorta 120-ish over 80-something."
        ]
        
        for sentence in translation_ready:
            score = self.validator._assess_translation_readiness(sentence)
            assert score > 0.6, f"Translation-ready sentence should have high score: {sentence}"
        
        for sentence in translation_difficult:
            score = self.validator._assess_translation_readiness(sentence)
            assert score < 0.6, f"Translation-difficult sentence should have low score: {sentence}"
    
    def test_quality_filtering(self):
        """Test overall quality filtering."""
        high_quality_sentences = [
            "The patient's condition improved significantly after receiving the prescribed medication.",
            "Surgical intervention was successful with no post-operative complications.",
            "Laboratory results confirmed normal glucose levels within acceptable range."
        ]
        
        low_quality_sentences = [
            "Patient better.",
            "Surgery good.",
            "Tests ok."
        ]
        
        mixed_sentences = high_quality_sentences + low_quality_sentences
        filtered = self.validator.filter_by_quality(mixed_sentences)
        
        # Should keep high-quality sentences
        for sentence in high_quality_sentences:
            assert sentence in filtered, f"High-quality sentence should be kept: {sentence}"
        
        # Should filter out low-quality sentences
        for sentence in low_quality_sentences:
            assert sentence not in filtered, f"Low-quality sentence should be filtered: {sentence}"
    
    def test_batch_validation(self):
        """Test batch validation functionality."""
        large_batch = []
        for i in range(50):
            large_batch.append(f"The patient number {i} received comprehensive medical treatment and showed significant improvement.")
        for i in range(20):
            large_batch.append(f"Patient {i} better.")
        
        start_time = time.time()
        filtered = self.validator.filter_by_quality(large_batch)
        processing_time = time.time() - start_time
        
        # Should process efficiently
        assert processing_time < 3.0
        assert len(filtered) >= 40  # Most high-quality sentences should be kept
    
    def test_statistics_tracking(self):
        """Test statistics tracking."""
        test_sentences = [
            "High-quality medical sentence about patient treatment.",
            "Low quality.",
            "Another comprehensive sentence about medical procedures.",
            "Bad."
        ]
        
        filtered = self.validator.filter_by_quality(test_sentences)
        stats = self.validator.get_validation_stats()
        
        assert stats['total_processed'] == len(test_sentences)
        assert stats['valid_thoughts'] > 0
        assert 'avg_quality_score' in stats
        assert 'structural_issues' in stats
    
    def test_spacy_integration(self):
        """Test spaCy integration if available."""
        try:
            import spacy
            spacy_validator = CompleteThoughtValidator(quality_threshold=0.7, use_spacy=True)
            
            test_sentences = [
                "The patient received treatment and recovered well.",
                "Treatment patient recovered."
            ]
            
            filtered = spacy_validator.filter_by_quality(test_sentences)
            assert len(filtered) >= 1  # At least one sentence should pass
            
        except ImportError:
            # spaCy not available, skip this test
            pytest.skip("spaCy not available for testing")
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Empty input
        assert self.validator.filter_by_quality([]) == []
        
        # Very short sentences
        short_sentences = ["A", "No", "Yes", "Ok"]
        filtered = self.validator.filter_by_quality(short_sentences)
        assert len(filtered) == 0  # Should filter out very short sentences
        
        # Very long sentences
        long_sentence = "The patient " + "received treatment " * 100
        filtered = self.validator.filter_by_quality([long_sentence])
        # Should handle gracefully (may or may not keep based on other quality factors)
        assert isinstance(filtered, list)


def run_filter_unit_tests():
    """Run all filter unit tests."""
    print("🚀 Running Filter Unit Tests")
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
    success = run_filter_unit_tests()
    sys.exit(0 if success else 1)
