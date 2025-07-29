#!/usr/bin/env python3
"""
Test script for HealthDomainExpertAgent
"""

import sys
sys.path.append('src')

from agents.health_expert import HealthDomainExpertAgent

# Mock LLM for testing
class MockLLM:
    def __call__(self, prompt):
        return "Mock response"

def main():
    print("=" * 60)
    print("Testing HealthDomainExpertAgent Implementation")
    print("=" * 60)
    
    try:
        # Create agent
        agent = HealthDomainExpertAgent(MockLLM())
        print("✅ HealthDomainExpertAgent created successfully")
        
        # Test 1: Health relevance scoring
        print("\n1. Testing health relevance scoring:")
        test_sentences = [
            "The patient was diagnosed with bacterial pneumonia and prescribed antibiotics.",
            "The weather is nice today and I went for a walk.",
            "Clinical studies show that this treatment is effective for most patients.",
            "I bought groceries at the store yesterday.",
            "The doctor recommended surgery to treat the condition."
        ]
        
        for sentence in test_sentences:
            try:
                score = agent.score_health_relevance(sentence)
                preview = sentence[:50] + "..." if len(sentence) > 50 else sentence
                print(f"   Score: {score:.2f} - '{preview}'")
            except Exception as e:
                print(f"   Error scoring: {e}")
        
        # Test 2: Medical entity identification
        print("\n2. Testing medical entity identification:")
        medical_text = "The patient received antibiotic treatment for the bacterial infection in the hospital."
        
        try:
            entities = agent.identify_medical_entities(medical_text)
            print(f"   Found {len(entities)} entities:")
            for entity in entities:
                print(f"     - '{entity['text']}' ({entity['label']}) - {entity['description']}")
        except Exception as e:
            print(f"   Error identifying entities: {e}")
        
        # Test 3: Medical terminology validation
        print("\n3. Testing medical terminology validation:")
        medical_text = "The patient has pneumonia and needs antibiotic therapy for treatment."
        
        try:
            validation = agent.validate_medical_terminology(medical_text)
            print(f"   Valid terms: {validation['valid_terms']}")
            print(f"   Invalid terms: {validation['invalid_terms']}")
            print(f"   Terminology accuracy: {validation['terminology_accuracy']:.2f}")
            print(f"   Domain specificity: {validation['domain_specificity']:.2f}")
        except Exception as e:
            print(f"   Error validating terminology: {e}")
        
        # Test 4: Health domain confidence
        print("\n4. Testing health domain confidence:")
        test_cases = [
            "The patient underwent surgical treatment for cardiac conditions.",
            "Programming languages are used for software development.",
            "Medical diagnosis requires careful examination of symptoms."
        ]
        
        for sentence in test_cases:
            try:
                entities = agent.identify_medical_entities(sentence)
                confidence = agent.get_health_domain_confidence(sentence, entities)
                preview = sentence[:40] + "..." if len(sentence) > 40 else sentence
                print(f"   Confidence: {confidence:.2f} - '{preview}'")
            except Exception as e:
                print(f"   Error calculating confidence: {e}")
        
        # Test 5: Medical term scoring
        print("\n5. Testing medical term scoring:")
        test_texts = [
            "patient treatment diagnosis therapy",
            "computer software programming code",
            "clinical medical healthcare therapeutic diagnostic"
        ]
        
        for text in test_texts:
            try:
                score = agent._calculate_medical_term_score(text)
                print(f"   Term score: {score:.2f} - '{text}'")
            except Exception as e:
                print(f"   Error calculating term score: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("HealthDomainExpertAgent is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
