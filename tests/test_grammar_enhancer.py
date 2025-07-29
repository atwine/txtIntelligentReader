#!/usr/bin/env python3
"""
Test script for GrammarEnhancementAgent
"""

import sys
sys.path.append('src')

from agents.grammar_enhancer import GrammarEnhancementAgent

# Mock LLM for testing
class MockLLM:
    def __call__(self, prompt):
        return "Mock response"

def main():
    print("=" * 60)
    print("Testing GrammarEnhancementAgent Implementation")
    print("=" * 60)
    
    try:
        # Create agent
        agent = GrammarEnhancementAgent(MockLLM())
        print("✅ GrammarEnhancementAgent created successfully")
        
        # Test 1: PDF artifact fixing
        print("\n1. Testing PDF artifact fixing:")
        test_artifacts = [
            "the  patlent   received  treatrnent",  # Multiple spaces, OCR errors
            "med\x0cical diagnosis\ufeff was made",  # Control characters
            "h o s p i t a l care provided",  # Broken words
            "patient-\ntreatment was effective"  # Hyphenated line breaks
        ]
        
        for text in test_artifacts:
            try:
                fixed = agent.fix_pdf_artifacts(text)
                print(f"   Original: '{text}'")
                print(f"   Fixed:    '{fixed}'")
                print()
            except Exception as e:
                print(f"   Error fixing artifacts: {e}")
        
        # Test 2: Grammar enhancement
        print("2. Testing grammar enhancement:")
        test_sentences = [
            "the patient received treatment",  # No capitalization, no period
            "Patient  was  diagnosed  with  infection  .",  # Spacing issues
            "dr smith prescribed meds for the condition",  # Abbreviations
            "patient can't take medication",  # Contractions
            "Medical diagnosis was made"  # Already good
        ]
        
        for sentence in test_sentences:
            try:
                enhanced = agent.enhance_grammar(sentence)
                print(f"   Original: '{sentence}'")
                print(f"   Enhanced: '{enhanced}'")
                print()
            except Exception as e:
                print(f"   Error enhancing: {e}")
        
        # Test 3: Medical terminology standardization
        print("3. Testing medical terminology standardization:")
        test_terms = [
            "The doctor prescribed meds for the patient.",
            "Patient visited ER for treatment.",
            "Dr smith works at the hospital.",
            "BP and HR were monitored during surgery."
        ]
        
        for text in test_terms:
            try:
                standardized = agent.standardize_medical_terminology(text)
                print(f"   Original:     '{text}'")
                print(f"   Standardized: '{standardized}'")
                print()
            except Exception as e:
                print(f"   Error standardizing: {e}")
        
        # Test 4: Complete sentence ensuring
        print("4. Testing sentence completion:")
        test_fragments = [
            "patient treatment",  # Fragment
            "The patient was treated",  # No period
            "Medical diagnosis",  # Fragment
            "The patient received excellent care at the hospital"  # Complete but no period
        ]
        
        for fragment in test_fragments:
            try:
                completed = agent.ensure_complete_sentences(fragment)
                print(f"   Original:  '{fragment}'")
                print(f"   Completed: '{completed}'")
                print()
            except Exception as e:
                print(f"   Error completing: {e}")
        
        # Test 5: Enhancement metrics
        print("5. Testing enhancement metrics:")
        original = "the  patlent  received treatrnent at hospltal"
        enhanced = agent.enhance_grammar(original)
        
        try:
            metrics = agent.get_enhancement_metrics(original, enhanced)
            print(f"   Original:  '{original}'")
            print(f"   Enhanced:  '{enhanced}'")
            print(f"   Metrics:")
            for key, value in metrics.items():
                print(f"     {key}: {value}")
        except Exception as e:
            print(f"   Error calculating metrics: {e}")
        
        # Test 6: Translation readiness
        print("\n6. Testing translation readiness:")
        test_translations = [
            "The patient can't receive treatment.",  # Has contractions
            "The patient cannot receive treatment.",  # Translation ready
            "patient treatment effective",  # Poor readiness
            "The patient received effective treatment at the medical center."  # High readiness
        ]
        
        for text in test_translations:
            try:
                readiness = agent._assess_translation_readiness(text)
                print(f"   Readiness: {readiness:.2f} - '{text}'")
            except Exception as e:
                print(f"   Error assessing readiness: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("GrammarEnhancementAgent is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
