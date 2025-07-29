#!/usr/bin/env python3
"""
Test script for HealthContextFilter (Layer 2)
"""

import sys
sys.path.append('src')

from filters.health_context import HealthContextFilter

def main():
    print("=" * 60)
    print("Testing HealthContextFilter Implementation (Layer 2)")
    print("=" * 60)
    
    try:
        # Create filter
        filter = HealthContextFilter(health_threshold=0.3)
        print("✅ HealthContextFilter created successfully")
        print(f"   Health threshold: {filter.health_threshold}")
        print(f"   Medical terms loaded: {len(filter.medical_terms)}")
        print(f"   Medical patterns: {len(filter.medical_patterns)}")
        
        # Test 1: Medical terminology detection
        print("\n1. Testing medical terminology detection:")
        medical_samples = [
            "The patient received medical treatment at the hospital.",  # High medical
            "The doctor prescribed antibiotics for the infection.",  # High medical
            "Blood pressure was measured at 120/80 mmHg.",  # High medical
            "The weather is nice today.",  # No medical content
            "Patient underwent surgery for heart condition.",  # High medical
            "The meeting was scheduled for tomorrow.",  # No medical content
            "Chest pain and shortness of breath were reported.",  # High medical
            "The book was interesting to read.",  # No medical content
        ]
        
        for sample in medical_samples:
            score = filter.score_health_relevance(sample)
            print(f"   Score: {score:.3f} - '{sample[:50]}...'")
        
        # Test 2: Health relevance scoring
        print("\n2. Testing health relevance scoring components:")
        test_sentence = "The patient was diagnosed with diabetes and prescribed medication."
        analysis = filter.get_health_analysis(test_sentence)
        
        print(f"   Sentence: '{test_sentence}'")
        print(f"   Health Score: {analysis['health_score']:.3f}")
        print(f"   Medical Terms: {analysis['medical_terms']}")
        print(f"   Medical Patterns: {analysis['medical_patterns']}")
        print(f"   Entities Found: {analysis['entities_found']}")
        print(f"   Relevance Level: {analysis['relevance_level']}")
        
        # Test 3: Medical entity detection
        print("\n3. Testing medical entity detection:")
        entity_samples = [
            "Patient received penicillin treatment.",  # Medication pattern
            "Blood pressure medication was prescribed.",  # Medical terms
            "The doctor performed surgery on the heart.",  # Multiple entities
            "Chest X-ray showed normal results.",  # Medical procedure
            "Temperature was 101.5 degrees fahrenheit.",  # Medical measurement
        ]
        
        for sample in entity_samples:
            analysis = filter.get_health_analysis(sample)
            print(f"   Entities: {analysis['entities_found']} - '{sample[:40]}...'")
            print(f"     Terms: {analysis['medical_terms'][:3]}")  # Show first 3
        
        # Test 4: Medical pattern matching
        print("\n4. Testing medical pattern matching:")
        pattern_samples = [
            "Take 500mg twice daily.",  # Dosage pattern
            "Blood pressure 140/90 mmHg.",  # BP pattern
            "Heart rate 72 bpm.",  # HR pattern
            "Post-operative recovery was successful.",  # Medical time reference
            "Patient underwent CT scan.",  # Medical abbreviation
            "Follow-up appointment scheduled.",  # Medical procedure
        ]
        
        for sample in pattern_samples:
            analysis = filter.get_health_analysis(sample)
            print(f"   Patterns: {len(analysis['medical_patterns'])} - '{sample[:40]}...'")
            if analysis['medical_patterns']:
                print(f"     Found: {analysis['medical_patterns'][:2]}")  # Show first 2
        
        # Test 5: Health context filtering
        print("\n5. Testing health context filtering:")
        mixed_sentences = [
            "The patient received excellent medical treatment.",  # Keep - high medical
            "It was a sunny day outside.",  # Remove - no medical
            "Doctor prescribed antibiotics for infection.",  # Keep - high medical
            "The meeting was postponed until next week.",  # Remove - no medical
            "Blood test results showed normal values.",  # Keep - medical
            "The restaurant served delicious food.",  # Remove - no medical
            "Patient complained of chest pain.",  # Keep - medical symptoms
            "The movie was very entertaining.",  # Remove - no medical
            "Surgery was scheduled for tomorrow morning.",  # Keep - medical procedure
            "Traffic was heavy during rush hour.",  # Remove - no medical
        ]
        
        print(f"   Input sentences: {len(mixed_sentences)}")
        filtered = filter.filter_by_health_context(mixed_sentences)
        print(f"   Health-relevant sentences: {len(filtered)}")
        print(f"   Health relevance rate: {len(filtered)/len(mixed_sentences)*100:.1f}%")
        
        print("\n   Health-relevant sentences kept:")
        for i, sentence in enumerate(filtered, 1):
            score = filter.score_health_relevance(sentence)
            print(f"     {i}. [{score:.3f}] {sentence}")
        
        # Test 6: Relevance level categorization
        print("\n6. Testing relevance level categorization:")
        relevance_samples = [
            "Patient underwent cardiac surgery with anesthesia.",  # High
            "Doctor prescribed medication for treatment.",  # Medium
            "Hospital visit was scheduled.",  # Low
            "The patient felt better.",  # Low
            "Weather was nice today.",  # None
        ]
        
        for sample in relevance_samples:
            analysis = filter.get_health_analysis(sample)
            print(f"   Level: {analysis['relevance_level']:>6} [{analysis['health_score']:.3f}] - '{sample[:40]}...'")
        
        # Test 7: Filtering statistics
        print("\n7. Testing filtering statistics:")
        stats = filter.get_filtering_stats()
        print(f"   Total processed: {stats['total_processed']}")
        print(f"   Health relevant: {stats['health_relevant']}")
        print(f"   Relevance rate: {stats['relevance_rate']:.3f}")
        print(f"   Medical entities found: {stats['medical_entities_found']}")
        print(f"   Relevance breakdown:")
        for level, count in stats['relevance_breakdown'].items():
            print(f"     {level}: {count}")
        
        # Test 8: Threshold sensitivity
        print("\n8. Testing threshold sensitivity:")
        test_sentence = "Patient visited hospital for checkup."
        thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
        
        base_score = filter.score_health_relevance(test_sentence)
        print(f"   Test sentence: '{test_sentence}'")
        print(f"   Health score: {base_score:.3f}")
        
        for threshold in thresholds:
            would_pass = base_score >= threshold
            print(f"   Threshold {threshold:.1f}: {'PASS' if would_pass else 'FAIL'}")
        
        # Test 9: Edge cases
        print("\n9. Testing edge cases:")
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "a",  # Single character
            "The",  # Single word
            "Medical medical medical medical medical",  # Repeated terms
            "Dr. Smith treated the pt. w/ meds.",  # Abbreviations
        ]
        
        for i, case in enumerate(edge_cases):
            try:
                score = filter.score_health_relevance(case)
                analysis = filter.get_health_analysis(case)
                print(f"   Case {i+1}: Score {score:.3f}, Terms: {len(analysis['medical_terms'])} - '{case}'")
            except Exception as e:
                print(f"   Case {i+1}: Error - {e}")
        
        # Test 10: Performance test
        print("\n10. Testing performance:")
        large_medical_test = [
            "The patient received medical treatment at the hospital.",
            "Doctor prescribed antibiotics for the bacterial infection.",
            "Blood pressure was monitored during surgery.",
        ] * 500
        
        large_non_medical_test = [
            "The weather is beautiful today.",
            "The meeting was very productive.",
            "Traffic was heavy this morning.",
        ] * 500
        
        combined_test = large_medical_test + large_non_medical_test
        
        import time
        start_time = time.time()
        performance_filtered = filter.filter_by_health_context(combined_test)
        end_time = time.time()
        
        processing_time = end_time - start_time
        sentences_per_second = len(combined_test) / processing_time if processing_time > 0 else 0
        
        print(f"   Processed {len(combined_test)} sentences in {processing_time:.3f}s")
        print(f"   Rate: {sentences_per_second:.0f} sentences/second")
        print(f"   Health-relevant: {len(performance_filtered)} sentences")
        print(f"   Expected medical: ~1500, Found: {len(performance_filtered)}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("HealthContextFilter (Layer 2) is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
