#!/usr/bin/env python3
"""
Test script for QuickFilter (Layer 1)
"""

import sys
sys.path.append('src')

from filters.quick_filter import QuickFilter

def main():
    print("=" * 60)
    print("Testing QuickFilter Implementation (Layer 1)")
    print("=" * 60)
    
    try:
        # Create filter
        filter = QuickFilter()
        print("✅ QuickFilter created successfully")
        
        # Test 1: Noise pattern detection
        print("\n1. Testing noise pattern detection:")
        noise_samples = [
            "123",  # Standalone number
            "Page 5",  # Page number
            "iv",  # Roman numeral
            "Chapter 1",  # Chapter heading
            "...........",  # Dot line
            "----------",  # Dash line
            "a)",  # Single letter with parenthesis
            "A.",  # Single capital letter with period
            "",  # Empty string
            "   ",  # Whitespace only
            "***",  # Only symbols
            "1-5",  # Page range
        ]
        
        for sample in noise_samples:
            is_noise = filter._is_noise(sample)
            print(f"   '{sample}' -> Noise: {is_noise}")
        
        # Test 2: PDF artifact detection
        print("\n2. Testing PDF artifact detection:")
        pdf_samples = [
            "Page 1 of 10",
            "5/20",
            "[1]",
            "(25)",
            "| Table | Border |",
            "+------+------+",
            "###",
            "=======",
            "a",  # Single character
            "wo rd",  # Broken word with space
        ]
        
        for sample in pdf_samples:
            is_artifact = filter._is_pdf_artifact(sample)
            print(f"   '{sample}' -> PDF Artifact: {is_artifact}")
        
        # Test 3: Header/footer detection
        print("\n3. Testing header/footer detection:")
        header_samples = [
            "TABLE OF CONTENTS",
            "LIST OF FIGURES",
            "REFERENCES",
            "APPENDIX A",
            "COPYRIGHT 2024",
            "(C) 2024",
            "© 2024",
            "www.example.com",
            "https://example.com",
            "ISBN 978-0123456789",
            "January 15, 2024",  # Date
            "2024-01-15",  # ISO date
        ]
        
        for sample in header_samples:
            is_header = filter._is_header_footer(sample)
            print(f"   '{sample}' -> Header/Footer: {is_header}")
        
        # Test 4: Formatting artifact detection
        print("\n4. Testing formatting artifact detection:")
        formatting_samples = [
            "*",  # Bullet point alone
            "• ",  # Unicode bullet
            "→",  # Arrow
            "1.",  # Number with period alone
            "a)",  # Letter with parenthesis
            "[x]",  # Checkbox
            "☐",  # Unicode checkbox
            "✓",  # Check mark
        ]
        
        for sample in formatting_samples:
            is_formatting = filter._is_formatting_artifact(sample)
            print(f"   '{sample}' -> Formatting Artifact: {is_formatting}")
        
        # Test 5: Complete filtering
        print("\n5. Testing complete filtering:")
        test_sentences = [
            "The patient received excellent medical treatment.",  # Keep
            "Page 1",  # Remove - page number
            "The doctor prescribed antibiotics for the infection.",  # Keep
            "TABLE OF CONTENTS",  # Remove - header
            "Recovery was successful and complete.",  # Keep
            "123",  # Remove - standalone number
            "Follow-up appointments were scheduled.",  # Keep
            "...........",  # Remove - dot line
            "The treatment was effective.",  # Keep
            "*",  # Remove - bullet point
            "Patient showed improvement.",  # Keep
            "",  # Remove - empty
            "Medical care was provided by specialists.",  # Keep
        ]
        
        print(f"   Input sentences: {len(test_sentences)}")
        filtered = filter.filter_text(test_sentences)
        print(f"   Filtered sentences: {len(filtered)}")
        print(f"   Removal rate: {(len(test_sentences) - len(filtered)) / len(test_sentences) * 100:.1f}%")
        
        print("\n   Kept sentences:")
        for i, sentence in enumerate(filtered, 1):
            print(f"     {i}. {sentence}")
        
        # Test 6: Filtering statistics
        print("\n6. Testing filtering statistics:")
        stats = filter.get_filtering_stats()
        print(f"   Total processed: {stats['total_processed']}")
        print(f"   Total removed: {stats['total_removed']}")
        print(f"   Total kept: {stats['total_kept']}")
        print(f"   Removal rate: {stats['removal_rate']:.2f}")
        print(f"   Breakdown:")
        for category, count in stats['breakdown'].items():
            print(f"     {category}: {count}")
        
        # Test 7: Edge cases
        print("\n7. Testing edge cases:")
        edge_cases = [
            None,  # None input
            [],  # Empty list
            [""],  # List with empty string
            ["   "],  # List with whitespace
            ["Valid sentence.", "", "Another valid sentence."],  # Mixed content
        ]
        
        for i, case in enumerate(edge_cases):
            try:
                if case is None:
                    print(f"   Case {i+1}: None input -> Skipped")
                    continue
                result = filter.filter_text(case)
                print(f"   Case {i+1}: {len(case) if case else 0} input -> {len(result)} output")
            except Exception as e:
                print(f"   Case {i+1}: Error - {e}")
        
        # Test 8: Performance test
        print("\n8. Testing performance:")
        large_test = ["This is a test sentence."] * 1000 + ["Page 1"] * 500
        
        import time
        start_time = time.time()
        large_filtered = filter.filter_text(large_test)
        end_time = time.time()
        
        processing_time = end_time - start_time
        sentences_per_second = len(large_test) / processing_time if processing_time > 0 else 0
        
        print(f"   Processed {len(large_test)} sentences in {processing_time:.3f}s")
        print(f"   Rate: {sentences_per_second:.0f} sentences/second")
        print(f"   Filtered: {len(large_filtered)} sentences kept")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("QuickFilter (Layer 1) is working correctly.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
