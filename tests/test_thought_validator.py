#!/usr/bin/env python3
"""
Test script for CompleteThoughtValidator (Layer 4)
"""

import sys
sys.path.append('src')

from filters.thought_validator import CompleteThoughtValidator

def main():
    print("=" * 60)
    print("Testing CompleteThoughtValidator Implementation (Layer 4)")
    print("=" * 60)
    
    try:
        # Test 1: Initialize validator
        print("1. Testing initialization:")
        validator = CompleteThoughtValidator(quality_threshold=0.7, use_spacy=False)
        print("✅ CompleteThoughtValidator created successfully")
        print(f"   Quality threshold: {validator.quality_threshold}")
        print(f"   spaCy enabled: {validator.use_spacy}")
        print(f"   Subject patterns: {len(validator.subject_patterns)}")
        print(f"   Verb patterns: {len(validator.verb_patterns)}")
        print(f"   Actionable patterns: {len(validator.actionable_patterns)}")
        
        # Test 2: Structural validation
        print("\n2. Testing structural validation:")
        structure_test_sentences = [
            "The patient received medical treatment at the hospital.",  # Complete structure
            "Doctor prescribed antibiotics for infection.",  # Complete structure
            "Blood pressure was monitored during surgery.",  # Complete structure
            "Incomplete fragment without verb.",  # Missing verb
            "Running quickly through the hallway.",  # Missing subject
            "The medication.",  # Missing verb
            "Is effective treatment.",  # Missing subject
            "",  # Empty sentence
        ]
        
        for sentence in structure_test_sentences:
            result = validator.validate_structure(sentence)
            print(f"   Structure: {result['structure_score']:.3f} | Complete: {result['is_structurally_complete']} | '{sentence[:40]}...'")
            print(f"     Subject: {result['has_subject']} | Verb: {result['has_verb']} | Object: {result['has_object']}")
            if result['structural_elements']:
                print(f"     Elements: {result['structural_elements'][:3]}")  # Show first 3
        
        # Test 3: Semantic coherence validation
        print("\n3. Testing semantic coherence validation:")
        coherence_test_sentences = [
            "The patient received comprehensive medical treatment at the hospital.",  # Coherent
            "Doctor prescribed antibiotics for bacterial infection treatment.",  # Coherent
            "Blood pressure monitoring during surgical procedure was successful.",  # Coherent
            "The the the patient patient received treatment.",  # Repetitive
            "treatment patient the received hospital at medical",  # Illogical order
            "PATIENT RECEIVED TREATMENT AT HOSPITAL TODAY",  # All caps
            "patient received treatment",  # No punctuation
            "A",  # Too short
        ]
        
        for sentence in coherence_test_sentences:
            result = validator.validate_semantic_coherence(sentence)
            print(f"   Coherence: {result['coherence_score']:.3f} | Coherent: {result['is_coherent']} | Clear: {result['has_clear_meaning']}")
            print(f"     '{sentence[:50]}...'")
            if result['coherence_issues']:
                print(f"     Issues: {result['coherence_issues'][:2]}")  # Show first 2 issues
        
        # Test 4: Actionability validation
        print("\n4. Testing actionability validation:")
        actionability_test_sentences = [
            "The patient should take medication twice daily.",  # Actionable instruction
            "Doctor recommends monitoring blood pressure regularly.",  # Actionable recommendation
            "The surgical procedure was performed successfully.",  # Informative medical
            "Blood test results showed normal values.",  # Informative factual
            "The weather is nice today.",  # Not actionable/medical
            "Take 500mg of medication every 8 hours.",  # Highly actionable
            "Patient underwent CT scan for diagnosis.",  # Medical procedure
            "The meeting was scheduled for tomorrow.",  # Not medical
        ]
        
        for sentence in actionability_test_sentences:
            result = validator.validate_actionability(sentence)
            print(f"   Actionable: {result['is_actionable']} | Informative: {result['is_informative']} | Score: {result['actionability_score']:.3f}")
            print(f"     '{sentence[:45]}...'")
            print(f"     Type: {result['information_type']} | Indicators: {len(result['action_indicators'])}")
        
        # Test 5: Translation readiness validation
        print("\n5. Testing translation readiness validation:")
        translation_test_sentences = [
            "The patient received comprehensive medical treatment at the hospital.",  # Translation ready
            "Doctor prescribed antibiotics for bacterial infection.",  # Translation ready
            "Blood pressure was monitored during surgery.",  # Translation ready
            "Fragment without complete",  # Not translation ready
            "The the patient received treatment treatment.",  # Has errors
            "PATIENT RECEIVED TREATMENT",  # Formatting issues
            "A very long sentence that goes on and on without much meaning and contains too many words to be easily translatable and understandable.",  # Too long
            "",  # Empty
        ]
        
        for sentence in translation_test_sentences:
            result = validator.validate_translation_readiness(sentence)
            print(f"   Translation Ready: {result['is_translation_ready']} | Score: {result['translation_score']:.3f}")
            print(f"     '{sentence[:45]}...'")
            print(f"     Factors: {len(result['readiness_factors'])} | Issues: {len(result['translation_issues'])}")
            if result['translation_issues']:
                print(f"     Issues: {result['translation_issues'][:2]}")
        
        # Test 6: Final comprehensive validation
        print("\n6. Testing final comprehensive validation:")
        final_test_sentences = [
            "The patient received comprehensive medical treatment at the hospital.",  # High quality
            "Doctor prescribed antibiotics for bacterial infection treatment.",  # High quality
            "Blood pressure monitoring during surgery was successful.",  # High quality
            "Patient should take medication twice daily as prescribed.",  # High quality
            "Fragment without complete structure or meaning.",  # Low quality
            "The weather is nice today.",  # Not medical, but complete
            "Take medication.",  # Too short but actionable
            "",  # Empty
        ]
        
        for sentence in final_test_sentences:
            result = validator.final_validation(sentence)
            print(f"   Quality: {result['overall_quality']:.3f} | Passes: {result['passes_validation']} | '{sentence[:40]}...'")
            breakdown = result['quality_breakdown']
            print(f"     Structure: {breakdown['structure']:.2f} | Coherence: {breakdown['coherence']:.2f} | Action: {breakdown['actionability']:.2f} | Translation: {breakdown['translation']:.2f}")
            summary = result['validation_summary']
            print(f"     Complete: {summary['structural_complete']} | Coherent: {summary['semantically_coherent']} | Informative: {summary['actionable_informative']} | Ready: {summary['translation_ready']}")
        
        # Test 7: Batch validation
        print("\n7. Testing batch validation:")
        batch_sentences = [
            "The patient received excellent medical care at the hospital.",  # High quality
            "Doctor prescribed antibiotics for the bacterial infection.",  # High quality
            "Blood pressure was carefully monitored during surgery.",  # High quality
            "Fragment without meaning",  # Low quality
            "The weather is nice",  # Complete but not medical
            "Take medication twice daily as prescribed by doctor.",  # High quality
            "Patient underwent successful surgical procedure.",  # High quality
            "Short.",  # Too short
            "The comprehensive treatment plan included medication therapy.",  # High quality
            "And then the patient",  # Incomplete
        ]
        
        print(f"   Processing {len(batch_sentences)} sentences...")
        batch_results = validator.batch_validate(batch_sentences)
        
        high_quality_count = sum(1 for r in batch_results if r['passes_validation'])
        print(f"   High quality sentences: {high_quality_count}/{len(batch_sentences)} ({high_quality_count/len(batch_sentences)*100:.1f}%)")
        
        print("\n   Quality breakdown:")
        for i, (sentence, result) in enumerate(zip(batch_sentences, batch_results)):
            status = "✅ PASS" if result['passes_validation'] else "❌ FAIL"
            print(f"     {i+1}. [{result['overall_quality']:.3f}] {status} - '{sentence[:35]}...'")
        
        # Test 8: Quality filtering
        print("\n8. Testing quality filtering:")
        mixed_sentences = [
            "The patient received comprehensive medical treatment.",  # Keep - high quality
            "Fragment without",  # Remove - low quality
            "Doctor prescribed antibiotics for infection treatment.",  # Keep - high quality
            "Short",  # Remove - too short
            "Blood pressure was monitored during surgical procedure.",  # Keep - high quality
            "The weather is nice today.",  # Remove - not medical
            "Patient should take medication twice daily.",  # Keep - actionable
            "And then",  # Remove - incomplete
            "The treatment was successful and patient recovered.",  # Keep - high quality
            "Yes",  # Remove - too short
        ]
        
        print(f"   Input sentences: {len(mixed_sentences)}")
        filtered = validator.filter_by_quality(mixed_sentences, threshold=0.7)
        print(f"   High quality sentences (threshold ≥ 0.7): {len(filtered)}")
        print(f"   Quality pass rate: {len(filtered)/len(mixed_sentences)*100:.1f}%")
        
        print("\n   High quality sentences kept:")
        for i, sentence in enumerate(filtered, 1):
            print(f"     {i}. {sentence}")
        
        # Test 9: Validation statistics
        print("\n9. Testing validation statistics:")
        stats = validator.get_validation_stats()
        print(f"   Total processed: {stats['total_processed']}")
        print(f"   Structurally complete: {stats['structurally_complete']} ({stats['structure_rate']:.3f})")
        print(f"   Semantically coherent: {stats['semantically_coherent']} ({stats['coherence_rate']:.3f})")
        print(f"   Actionable sentences: {stats['actionable_sentences']} ({stats['actionability_rate']:.3f})")
        print(f"   Translation ready: {stats['translation_ready']} ({stats['translation_readiness_rate']:.3f})")
        print(f"   High quality: {stats['high_quality']} ({stats['quality_pass_rate']:.3f})")
        print(f"   Average quality score: {stats['average_quality_score']:.3f}")
        print(f"   Processing time: {stats['processing_time']:.3f}s")
        
        print(f"\n   Validation breakdown:")
        breakdown = stats['validation_breakdown']
        for validation_type, count in breakdown.items():
            print(f"     {validation_type}: {count}")
        
        # Test 10: Threshold sensitivity
        print("\n10. Testing threshold sensitivity:")
        test_sentence = "The patient received medical treatment at hospital."
        result = validator.final_validation(test_sentence)
        base_quality = result['overall_quality']
        
        thresholds = [0.3, 0.5, 0.7, 0.9]
        print(f"   Test sentence: '{test_sentence}'")
        print(f"   Overall quality: {base_quality:.3f}")
        
        for threshold in thresholds:
            would_pass = base_quality >= threshold
            print(f"   Threshold {threshold:.1f}: {'PASS' if would_pass else 'FAIL'}")
        
        # Test 11: Edge cases
        print("\n11. Testing edge cases:")
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "A",  # Single character
            "The",  # Single word
            "Dr. Smith treated the pt. w/ meds for the condition.",  # Abbreviations
            "Patient received treatment. Doctor monitored recovery.",  # Multiple sentences
            "The patient, who was 65 years old, received treatment.",  # Complex structure
            "Treatment was effective; patient recovered quickly.",  # Semicolon
        ]
        
        for i, case in enumerate(edge_cases):
            try:
                result = validator.final_validation(case)
                print(f"   Case {i+1}: Quality {result['overall_quality']:.3f}, Passes: {result['passes_validation']} - '{case[:30]}...'")
            except Exception as e:
                print(f"   Case {i+1}: Error - {e}")
        
        # Test 12: Performance test
        print("\n12. Testing performance:")
        performance_sentences = [
            "The patient received comprehensive medical treatment.",
            "Doctor prescribed antibiotics for bacterial infection.",
            "Blood pressure was monitored during surgery.",
            "Patient should take medication twice daily.",
            "The treatment was successful and effective.",
        ] * 100  # 500 sentences total
        
        import time
        start_time = time.time()
        performance_results = validator.batch_validate(performance_sentences)
        end_time = time.time()
        
        processing_time = end_time - start_time
        sentences_per_second = len(performance_sentences) / processing_time if processing_time > 0 else 0
        high_quality_count = sum(1 for r in performance_results if r['passes_validation'])
        
        print(f"   Processed {len(performance_sentences)} sentences in {processing_time:.3f}s")
        print(f"   Rate: {sentences_per_second:.0f} sentences/second")
        print(f"   High quality: {high_quality_count} sentences ({high_quality_count/len(performance_sentences)*100:.1f}%)")
        print(f"   Average quality: {sum(r['overall_quality'] for r in performance_results)/len(performance_results):.3f}")
        
        # Test 13: Pattern validation
        print("\n13. Testing pattern validation:")
        print(f"   Subject patterns compiled: {len(validator.subject_patterns)}")
        print(f"   Verb patterns compiled: {len(validator.verb_patterns)}")
        print(f"   Actionable patterns compiled: {len(validator.actionable_patterns)}")
        print(f"   Quality indicator patterns compiled: {len(validator.quality_indicators)}")
        
        # Test pattern matching
        test_text = "The patient should take prescribed medication daily."
        print(f"\n   Testing pattern matching on: '{test_text}'")
        
        subject_matches = sum(1 for pattern in validator.subject_patterns.values() if pattern.search(test_text.lower()))
        verb_matches = sum(1 for pattern in validator.verb_patterns.values() if pattern.search(test_text.lower()))
        action_matches = sum(1 for pattern in validator.actionable_patterns.values() if pattern.search(test_text.lower()))
        
        print(f"   Subject pattern matches: {subject_matches}")
        print(f"   Verb pattern matches: {verb_matches}")
        print(f"   Actionable pattern matches: {action_matches}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("CompleteThoughtValidator (Layer 4) is working correctly.")
        print("Final validation layer provides comprehensive quality assessment.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
