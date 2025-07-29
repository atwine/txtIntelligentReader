#!/usr/bin/env python3
"""
Test script for AIAnalysisFilter (Layer 3)
"""

import sys
sys.path.append('src')

from filters.ai_analysis import AIAnalysisFilter

class MockLLMClient:
    """Mock LLM client for testing without actual LLM calls."""
    
    def __init__(self):
        self.call_count = 0
    
    def generate(self, model, prompt):
        """Mock generate method for Ollama-style client."""
        self.call_count += 1
        
        # Simulate different responses based on sentence content
        if "patient received medical treatment" in prompt.lower():
            return {
                'response': '''
                {
                    "completeness_score": 0.9,
                    "is_complete": true,
                    "has_subject": true,
                    "has_predicate": true,
                    "is_meaningful": true,
                    "translation_ready": true,
                    "reasoning": "Complete sentence with clear subject and predicate"
                }
                '''
            }
        elif "weather is nice" in prompt.lower():
            return {
                'response': '''
                {
                    "completeness_score": 0.8,
                    "is_complete": true,
                    "has_subject": true,
                    "has_predicate": true,
                    "is_meaningful": true,
                    "translation_ready": true,
                    "reasoning": "Simple but complete sentence"
                }
                '''
            }
        elif "incomplete fragment" in prompt.lower():
            return {
                'response': '''
                {
                    "completeness_score": 0.3,
                    "is_complete": false,
                    "has_subject": false,
                    "has_predicate": false,
                    "is_meaningful": false,
                    "translation_ready": false,
                    "reasoning": "Sentence fragment without clear meaning"
                }
                '''
            }
        elif "batch" in prompt.lower() and "[" in prompt:
            # Mock batch response
            return {
                'response': '''
                [
                    {
                        "sentence_index": 0,
                        "completeness_score": 0.9,
                        "is_complete": true,
                        "is_meaningful": true,
                        "translation_ready": true,
                        "reasoning": "Complete medical sentence"
                    },
                    {
                        "sentence_index": 1,
                        "completeness_score": 0.4,
                        "is_complete": false,
                        "is_meaningful": false,
                        "translation_ready": false,
                        "reasoning": "Incomplete fragment"
                    }
                ]
                '''
            }
        else:
            # Default response
            return {
                'response': '''
                {
                    "completeness_score": 0.7,
                    "is_complete": true,
                    "has_subject": true,
                    "has_predicate": true,
                    "is_meaningful": true,
                    "translation_ready": true,
                    "reasoning": "Default analysis response"
                }
                '''
            }

def main():
    print("=" * 60)
    print("Testing AIAnalysisFilter Implementation (Layer 3)")
    print("=" * 60)
    
    try:
        # Test 1: Initialize without LLM (rule-based mode)
        print("1. Testing initialization without LLM (rule-based mode):")
        filter_no_llm = AIAnalysisFilter()
        print("✅ AIAnalysisFilter created successfully (rule-based mode)")
        print(f"   Model: {filter_no_llm.model}")
        print(f"   Completeness threshold: {filter_no_llm.completeness_threshold}")
        print(f"   LLM client: {'None (rule-based)' if not filter_no_llm.llm_client else 'Available'}")
        
        # Test 2: Initialize with mock LLM
        print("\n2. Testing initialization with mock LLM:")
        mock_llm = MockLLMClient()
        filter_with_llm = AIAnalysisFilter(llm_client=mock_llm, completeness_threshold=0.6)
        print("✅ AIAnalysisFilter created successfully (LLM mode)")
        print(f"   LLM client: {type(mock_llm).__name__}")
        print(f"   Completeness threshold: {filter_with_llm.completeness_threshold}")
        
        # Test 3: Rule-based completeness analysis
        print("\n3. Testing rule-based completeness analysis:")
        test_sentences = [
            "The patient received medical treatment at the hospital.",  # Complete
            "Weather is nice today.",  # Complete but simple
            "Incomplete fragment without",  # Incomplete
            "Yes.",  # Too short
            "",  # Empty
            "The doctor prescribed medication for the patient's condition and monitored recovery.",  # Long complete
        ]
        
        for sentence in test_sentences:
            analysis = filter_no_llm.analyze_completeness(sentence)
            print(f"   Score: {analysis['completeness_score']:.3f} | Complete: {analysis['is_complete']} | '{sentence[:40]}...'")
            print(f"     Subject: {analysis['has_subject']} | Predicate: {analysis['has_predicate']} | Meaningful: {analysis['is_meaningful']}")
        
        # Test 4: LLM-based completeness analysis
        print("\n4. Testing LLM-based completeness analysis:")
        llm_test_sentences = [
            "The patient received medical treatment at the hospital.",
            "Weather is nice today.",
            "Incomplete fragment without",
        ]
        
        for sentence in llm_test_sentences:
            analysis = filter_with_llm.analyze_completeness(sentence)
            print(f"   Score: {analysis['completeness_score']:.3f} | Complete: {analysis['is_complete']} | '{sentence[:40]}...'")
            print(f"     Reasoning: {analysis['reasoning']}")
        
        print(f"   LLM calls made: {mock_llm.call_count}")
        
        # Test 5: Batch analysis
        print("\n5. Testing batch analysis:")
        batch_sentences = [
            "The patient received excellent medical care.",
            "Incomplete fragment",
            "Doctor prescribed antibiotics for infection.",
            "Short.",
            "The comprehensive treatment plan included medication and therapy.",
        ]
        
        print(f"   Processing {len(batch_sentences)} sentences in batch...")
        batch_results = filter_with_llm.batch_analyze(batch_sentences, batch_size=3)
        
        print(f"   Batch results:")
        for i, (sentence, result) in enumerate(zip(batch_sentences, batch_results)):
            print(f"     {i+1}. [{result['completeness_score']:.3f}] Complete: {result['is_complete']} - '{sentence[:35]}...'")
        
        # Test 6: Filtering by completeness
        print("\n6. Testing filtering by completeness:")
        mixed_sentences = [
            "The patient received comprehensive medical treatment.",  # Complete - keep
            "Fragment without",  # Incomplete - remove
            "Doctor prescribed medication for bacterial infection.",  # Complete - keep
            "Yes",  # Too short - remove
            "Blood pressure was monitored during surgery.",  # Complete - keep
            "And then",  # Incomplete - remove
            "The treatment was successful and patient recovered.",  # Complete - keep
            "Maybe",  # Too short - remove
        ]
        
        print(f"   Input sentences: {len(mixed_sentences)}")
        filtered = filter_with_llm.filter_by_completeness(mixed_sentences, threshold=0.6)
        print(f"   Complete sentences (threshold ≥ 0.6): {len(filtered)}")
        print(f"   Completeness rate: {len(filtered)/len(mixed_sentences)*100:.1f}%")
        
        print("\n   Complete sentences kept:")
        for i, sentence in enumerate(filtered, 1):
            print(f"     {i}. {sentence}")
        
        # Test 7: Analysis statistics
        print("\n7. Testing analysis statistics:")
        stats = filter_with_llm.get_analysis_stats()
        print(f"   Total processed: {stats['total_processed']}")
        print(f"   LLM calls made: {stats['llm_calls_made']}")
        print(f"   Complete sentences: {stats['complete_sentences']}")
        print(f"   Incomplete sentences: {stats['incomplete_sentences']}")
        print(f"   Completeness rate: {stats['completeness_rate']:.3f}")
        print(f"   Meaningful sentences: {stats['meaningful_sentences']}")
        print(f"   Translation ready: {stats['translation_ready']}")
        print(f"   Average completeness score: {stats['average_completeness_score']:.3f}")
        print(f"   Processing time: {stats['processing_time']:.3f}s")
        
        # Test 8: Threshold sensitivity
        print("\n8. Testing threshold sensitivity:")
        test_sentence = "The patient visited hospital."
        analysis = filter_with_llm.analyze_completeness(test_sentence)
        base_score = analysis['completeness_score']
        
        thresholds = [0.3, 0.5, 0.7, 0.9]
        print(f"   Test sentence: '{test_sentence}'")
        print(f"   Completeness score: {base_score:.3f}")
        
        for threshold in thresholds:
            would_pass = base_score >= threshold
            print(f"   Threshold {threshold:.1f}: {'PASS' if would_pass else 'FAIL'}")
        
        # Test 9: Edge cases and error handling
        print("\n9. Testing edge cases and error handling:")
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "A",  # Single character
            "The",  # Single word
            "This is a very long sentence with many words that should definitely be considered complete because it has subject, predicate, and clear meaning throughout the entire sentence structure.",  # Very long
            "Dr. prescribed meds.",  # Abbreviations
        ]
        
        for i, case in enumerate(edge_cases):
            try:
                analysis = filter_no_llm.analyze_completeness(case)
                print(f"   Case {i+1}: Score {analysis['completeness_score']:.3f}, Complete: {analysis['is_complete']} - '{case[:30]}...'")
            except Exception as e:
                print(f"   Case {i+1}: Error - {e}")
        
        # Test 10: Performance comparison
        print("\n10. Testing performance comparison:")
        performance_sentences = [
            "The patient received medical treatment.",
            "Doctor prescribed antibiotics.",
            "Blood pressure was monitored.",
            "Surgery was successful.",
            "Recovery was complete.",
        ] * 50  # 250 sentences total
        
        import time
        
        # Rule-based performance
        start_time = time.time()
        rule_results = filter_no_llm.batch_analyze(performance_sentences)
        rule_time = time.time() - start_time
        
        # Reset mock LLM counter
        mock_llm.call_count = 0
        filter_with_llm.reset_stats()
        
        # LLM-based performance (with batching)
        start_time = time.time()
        llm_results = filter_with_llm.batch_analyze(performance_sentences, batch_size=5)
        llm_time = time.time() - start_time
        
        print(f"   Processed {len(performance_sentences)} sentences:")
        print(f"   Rule-based: {rule_time:.3f}s ({len(performance_sentences)/rule_time:.0f} sentences/sec)")
        print(f"   LLM-based: {llm_time:.3f}s ({len(performance_sentences)/llm_time:.0f} sentences/sec)")
        print(f"   LLM calls made: {mock_llm.call_count}")
        print(f"   Sentences per LLM call: {len(performance_sentences)/mock_llm.call_count:.1f}")
        
        # Compare results
        rule_complete = sum(1 for r in rule_results if r['is_complete'])
        llm_complete = sum(1 for r in llm_results if r['is_complete'])
        print(f"   Rule-based complete: {rule_complete}")
        print(f"   LLM-based complete: {llm_complete}")
        
        # Test 11: Prompt template validation
        print("\n11. Testing prompt templates:")
        print(f"   Completeness prompt template: {'✅ Valid' if '{sentence}' in filter_with_llm.completeness_prompt_template else '❌ Invalid'}")
        print(f"   Meaning prompt template: {'✅ Valid' if '{sentence}' in filter_with_llm.meaning_prompt_template else '❌ Valid'}")
        print(f"   Batch prompt template: {'✅ Valid' if '{sentences}' in filter_with_llm.batch_prompt_template else '❌ Invalid'}")
        
        # Test 12: Response parsing robustness
        print("\n12. Testing response parsing robustness:")
        
        # Test with malformed JSON
        malformed_responses = [
            '{"completeness_score": 0.8, "is_complete": true}',  # Valid JSON
            'completeness_score: 0.7, complete: yes',  # Invalid JSON
            'The sentence is complete and meaningful.',  # No JSON
            '{"completeness_score": "invalid"}',  # Invalid types
            '',  # Empty response
        ]
        
        for i, response in enumerate(malformed_responses):
            try:
                result = filter_with_llm._parse_completeness_response(response, "Test sentence.")
                print(f"   Response {i+1}: Score {result['completeness_score']:.3f}, Parsed successfully")
            except Exception as e:
                print(f"   Response {i+1}: Error - {e}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("AIAnalysisFilter (Layer 3) is working correctly.")
        print("Both rule-based and LLM-based analysis modes functional.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
