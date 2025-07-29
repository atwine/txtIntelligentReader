"""
Unit tests for ContentClassifierAgent

Tests the classification logic, noise detection, and confidence scoring
for the ContentClassifierAgent.
"""

import unittest
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.agents.content_classifier import ContentClassifierAgent


class TestContentClassifierAgent:
    """Test class for ContentClassifierAgent (using simple assertions)."""
    
    def __init__(self):
        """Initialize test with mock LLM."""
        # Mock LLM for testing
        class MockLLM:
            def __call__(self, prompt):
                return "Mock response"
        
        self.agent = ContentClassifierAgent(MockLLM())
    
    def test_noise_detection(self):
        """Test noise pattern detection."""
        print("Testing noise detection...")
        
        # Test cases that should be detected as noise
        noise_samples = [
            "123",  # Only numbers
            "Page 5",  # Page reference
            "...",  # Only punctuation
            "iv",  # Roman numeral
            "",  # Empty
            "a",  # Too short
        ]
        
        for sample in noise_samples:
            result = self.agent._is_noise_pattern(sample)
            print(f"  '{sample}' -> Noise: {result}")
            assert result == True, f"Expected '{sample}' to be detected as noise"
        
        # Test cases that should NOT be detected as noise
        meaningful_samples = [
            "The patient was treated successfully.",
            "Medical diagnosis shows improvement.",
            "This is a complete sentence with meaning."
        ]
        
        for sample in meaningful_samples:
            result = self.agent._is_noise_pattern(sample)
            print(f"  '{sample}' -> Noise: {result}")
            assert result == False, f"Expected '{sample}' to NOT be detected as noise"
        
        print("✅ Noise detection tests passed")
    
    def test_medical_indicators(self):
        """Test medical terminology detection."""
        print("Testing medical indicators...")
        
        # Test cases with medical content
        medical_samples = [
            "The patient received treatment for the condition.",
            "Clinical diagnosis indicates bacterial infection.",
            "Hospital staff provided excellent medical care.",
            "Surgery was performed by the doctor."
        ]
        
        for sample in medical_samples:
            result = self.agent._has_medical_indicators(sample)
            print(f"  '{sample}' -> Medical: {result}")
            assert result == True, f"Expected '{sample}' to have medical indicators"
        
        # Test cases without medical content
        non_medical_samples = [
            "The weather is nice today.",
            "I went to the store yesterday.",
            "Programming is an interesting field."
        ]
        
        for sample in non_medical_samples:
            result = self.agent._has_medical_indicators(sample)
            print(f"  '{sample}' -> Medical: {result}")
            assert result == False, f"Expected '{sample}' to NOT have medical indicators"
        
        print("✅ Medical indicators tests passed")
    
    def test_complete_sentence_detection(self):
        """Test complete sentence detection."""
        print("Testing complete sentence detection...")
        
        # Test cases that are complete sentences
        complete_sentences = [
            "The patient is recovering well.",
            "Medical treatment was successful!",
            "How are you feeling today?",
            "The diagnosis was confirmed by the doctor."
        ]
        
        for sample in complete_sentences:
            result = self.agent._is_complete_sentence(sample)
            print(f"  '{sample}' -> Complete: {result}")
            assert result == True, f"Expected '{sample}' to be a complete sentence"
        
        # Test cases that are NOT complete sentences
        incomplete_samples = [
            "patient treatment",  # No verb, no punctuation
            "The patient",  # Incomplete
            "medical",  # Single word
            "In the hospital"  # No ending punctuation
        ]
        
        for sample in incomplete_samples:
            result = self.agent._is_complete_sentence(sample)
            print(f"  '{sample}' -> Complete: {result}")
            assert result == False, f"Expected '{sample}' to NOT be a complete sentence"
        
        print("✅ Complete sentence tests passed")
    
    def test_classification_categories(self):
        """Test text categorization."""
        print("Testing classification categories...")
        
        test_cases = [
            ("123", "noise"),
            ("Page 5", "noise"),
            ("The patient was treated successfully.", "medical_content"),
            ("This is a general sentence.", "sentence"),
            ("• First item", "list_item"),
            ("1. Numbered item", "list_item"),
            ("Chapter 5", "header_footer"),
            ("word", "fragment")
        ]
        
        for text, expected_category in test_cases:
            result = self.agent._determine_category(text)
            print(f"  '{text}' -> Category: {result} (expected: {expected_category})")
            assert result == expected_category, f"Expected '{text}' to be categorized as '{expected_category}', got '{result}'"
        
        print("✅ Classification category tests passed")
    
    def test_confidence_scoring(self):
        """Test confidence score calculation."""
        print("Testing confidence scoring...")
        
        # High-quality medical sentence should get high confidence
        high_quality = "The patient received appropriate medical treatment and showed significant improvement."
        confidence = self.agent.get_classification_confidence(high_quality)
        print(f"  High quality: {confidence:.2f}")
        assert confidence > 0.7, f"Expected high confidence for quality text, got {confidence}"
        
        # Low-quality text should get low confidence
        low_quality = "123 page"
        confidence = self.agent.get_classification_confidence(low_quality)
        print(f"  Low quality: {confidence:.2f}")
        assert confidence < 0.5, f"Expected low confidence for poor text, got {confidence}"
        
        print("✅ Confidence scoring tests passed")
    
    def test_full_classification(self):
        """Test complete classification workflow."""
        print("Testing full classification...")
        
        test_segments = [
            "The patient was diagnosed with a bacterial infection and prescribed antibiotics.",
            "Page 15",
            "Medical treatment protocols should be followed carefully.",
            "123",
            "• First symptom observed",
            "How is the patient feeling today?"
        ]
        
        results = self.agent.classify_segments(test_segments)
        
        print(f"  Classified {len(results)} segments:")
        for i, result in enumerate(results):
            print(f"    {i+1}. '{result['text'][:50]}...' -> {result['category']} (conf: {result['confidence']:.2f})")
            
            # Verify result structure
            required_keys = ['text', 'category', 'confidence', 'is_meaningful', 'has_artifacts', 'length', 'word_count', 'classification_metadata']
            for key in required_keys:
                assert key in result, f"Missing key '{key}' in classification result"
        
        print("✅ Full classification tests passed")
    
    def run_all_tests(self):
        """Run all tests."""
        print("=" * 60)
        print("Running ContentClassifierAgent Tests")
        print("=" * 60)
        
        try:
            self.test_noise_detection()
            self.test_medical_indicators()
            self.test_complete_sentence_detection()
            self.test_classification_categories()
            self.test_confidence_scoring()
            self.test_full_classification()
            
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("ContentClassifierAgent implementation is working correctly.")
            print("=" * 60)
            return True
            
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {e}")
            return False
        except Exception as e:
            print(f"\n💥 UNEXPECTED ERROR: {e}")
            return False


def main():
    """Run the tests."""
    tester = TestContentClassifierAgent()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
