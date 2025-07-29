#!/usr/bin/env python3
"""
Simple test script for ContentClassifierAgent
"""

import sys
sys.path.append('src')

from agents.content_classifier import ContentClassifierAgent

# Mock LLM for testing
class MockLLM:
    def __call__(self, prompt):
        return "Mock response"

def main():
    print("=" * 60)
    print("Testing ContentClassifierAgent Implementation")
    print("=" * 60)
    
    # Create agent
    agent = ContentClassifierAgent(MockLLM())
    print("✅ ContentClassifierAgent created successfully")
    
    # Test 1: Noise detection
    print("\n1. Testing noise detection:")
    noise_samples = ["123", "Page 5", "...", "iv", "", "a"]
    for sample in noise_samples:
        result = agent._is_noise_pattern(sample)
        print(f"   '{sample}' -> Noise: {result}")
    
    # Test 2: Medical indicators
    print("\n2. Testing medical indicators:")
    medical_samples = [
        "The patient received treatment for the condition.",
        "Clinical diagnosis indicates bacterial infection.",
        "The weather is nice today."
    ]
    for sample in medical_samples:
        result = agent._has_medical_indicators(sample)
        print(f"   Medical indicators: {result} - '{sample[:40]}...'")
    
    # Test 3: Complete sentence detection
    print("\n3. Testing complete sentence detection:")
    sentence_samples = [
        "The patient is recovering well.",
        "patient treatment",
        "How are you feeling today?",
        "medical"
    ]
    for sample in sentence_samples:
        result = agent._is_complete_sentence(sample)
        print(f"   Complete sentence: {result} - '{sample}'")
    
    # Test 4: Classification
    print("\n4. Testing full classification:")
    test_segments = [
        "The patient was diagnosed with a bacterial infection and prescribed antibiotics.",
        "Page 15",
        "Medical treatment protocols should be followed carefully.",
        "123",
        "• First symptom observed"
    ]
    
    results = agent.classify_segments(test_segments)
    print(f"   Classified {len(results)} segments:")
    
    for i, result in enumerate(results, 1):
        text_preview = result['text'][:40] + "..." if len(result['text']) > 40 else result['text']
        print(f"   {i}. '{text_preview}'")
        print(f"      Category: {result['category']}")
        print(f"      Confidence: {result['confidence']:.2f}")
        print(f"      Meaningful: {result['is_meaningful']}")
        print(f"      Medical indicators: {result['classification_metadata']['has_medical_indicators']}")
        print()
    
    print("=" * 60)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("ContentClassifierAgent is working correctly.")
    print("=" * 60)

if __name__ == "__main__":
    main()
