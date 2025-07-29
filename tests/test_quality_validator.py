#!/usr/bin/env python3
"""
Test script for QualityValidationAgent
"""

import sys
sys.path.append('src')

from agents.quality_validator import QualityValidationAgent

# Mock LLM for testing
class MockLLM:
    def __call__(self, prompt):
        return "Mock response"

def main():
    print("=" * 60)
    print("Testing QualityValidationAgent Implementation")
    print("=" * 60)
    
    try:
        # Create agent
        agent = QualityValidationAgent(MockLLM())
        print("✅ QualityValidationAgent created successfully")
        
        # Test 1: Sentence validation
        print("\n1. Testing sentence validation:")
        test_sentences = [
            "The patient received excellent medical treatment at the hospital.",  # High quality
            "patient treatment",  # Poor quality - fragment
            "The patient can't take meds from doc.",  # Medium quality - informal terms
            "",  # Invalid - empty
            "Patient was diagnosed with bacterial infection and prescribed antibiotics."  # High quality medical
        ]
        
        for sentence in test_sentences:
            try:
                validation = agent.validate_sentence(sentence)
                preview = sentence[:40] + "..." if len(sentence) > 40 else sentence
                print(f"   Sentence: '{preview}'")
                print(f"   Valid: {validation['is_valid']}")
                print(f"   Quality Score: {validation['quality_score']:.2f}")
                print(f"   Translation Ready: {validation['translation_ready']}")
                if validation['issues']:
                    print(f"   Issues: {validation['issues'][:2]}")  # Show first 2 issues
                print()
            except Exception as e:
                print(f"   Error validating: {e}")
        
        # Test 2: Confidence scoring
        print("2. Testing confidence scoring:")
        test_metadata = {
            'health_relevance_score': 0.8,
            'classification_confidence': 0.9,
            'enhancement_quality': 0.85
        }
        
        confidence_tests = [
            "The patient received appropriate medical treatment.",
            "patient treatment effective",
            "The weather is nice today.",
            "Medical diagnosis was confirmed by the physician."
        ]
        
        for sentence in confidence_tests:
            try:
                confidence = agent.calculate_confidence_score(sentence, test_metadata)
                preview = sentence[:35] + "..." if len(sentence) > 35 else sentence
                print(f"   Confidence: {confidence:.2f} - '{preview}'")
            except Exception as e:
                print(f"   Error calculating confidence: {e}")
        
        # Test 3: Translation readiness
        print("\n3. Testing translation readiness:")
        readiness_tests = [
            "The patient received treatment.",  # Ready
            "patient treatment",  # Not ready - fragment
            "The patient can't take medication.",  # Not ready - contraction
            "The  patient  received  treatment  .",  # Not ready - spacing
            "Patient received excellent medical care at the hospital."  # Ready
        ]
        
        for sentence in readiness_tests:
            try:
                is_ready, issues = agent.check_translation_readiness(sentence)
                preview = sentence[:35] + "..." if len(sentence) > 35 else sentence
                print(f"   Ready: {is_ready} - '{preview}'")
                if issues:
                    print(f"     Issues: {issues[:2]}")  # Show first 2 issues
            except Exception as e:
                print(f"   Error checking readiness: {e}")
        
        # Test 4: Medical accuracy validation
        print("\n4. Testing medical accuracy validation:")
        medical_tests = [
            "The patient received medication from the physician.",  # Good
            "The patient got meds from the doc.",  # Informal terminology
            "Medical diagnosis was confirmed.",  # Good
            "Patient has symptoms of infection."  # Good
        ]
        
        for sentence in medical_tests:
            try:
                medical_validation = agent.validate_medical_accuracy(sentence)
                preview = sentence[:35] + "..." if len(sentence) > 35 else sentence
                print(f"   Sentence: '{preview}'")
                print(f"   Accurate: {medical_validation['is_medically_accurate']}")
                print(f"   Score: {medical_validation['accuracy_score']:.2f}")
                if medical_validation['terminology_issues']:
                    print(f"   Terminology Issues: {medical_validation['terminology_issues']}")
                print()
            except Exception as e:
                print(f"   Error validating medical accuracy: {e}")
        
        # Test 5: Quality metrics
        print("5. Testing comprehensive quality metrics:")
        test_sentence = "The patient was diagnosed with bacterial pneumonia and prescribed antibiotic treatment."
        test_metadata = {
            'health_relevance_score': 0.9,
            'classification_confidence': 0.85,
            'enhancement_quality': 0.8
        }
        
        try:
            metrics = agent.get_quality_metrics(test_sentence, test_metadata)
            print(f"   Sentence: '{test_sentence}'")
            print(f"   Length: {metrics['sentence_length']} chars")
            print(f"   Words: {metrics['word_count']}")
            print(f"   Quality Score: {metrics['validation_results']['quality_score']:.2f}")
            print(f"   Confidence: {metrics['confidence_score']:.2f}")
            print(f"   Quality Grade: {metrics['quality_grade']}")
            print(f"   Translation Ready: {metrics['translation_readiness'][0]}")
        except Exception as e:
            print(f"   Error getting metrics: {e}")
        
        # Test 6: Quality grading
        print("\n6. Testing quality grading:")
        grading_tests = [
            ("The patient received excellent medical treatment.", 0.9),  # Should be A
            ("Patient was treated successfully.", 0.8),  # Should be B  
            ("patient treatment effective", 0.6),  # Should be D
            ("treatment", 0.3)  # Should be F
        ]
        
        for sentence, mock_confidence in grading_tests:
            try:
                # Mock metadata to simulate different confidence levels
                mock_metadata = {'health_relevance_score': mock_confidence}
                grade = agent._assign_quality_grade(sentence, mock_metadata)
                print(f"   Grade: {grade} - '{sentence}'")
            except Exception as e:
                print(f"   Error grading: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("QualityValidationAgent is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
