#!/usr/bin/env python3
"""
Test script to demonstrate improved keyword filtering
"""

import re

def test_word_boundary_matching():
    """Test whole word matching vs substring matching"""
    
    # Test cases
    test_texts = [
        ("LED-Straßenbeleuchtung modernisierung", True, "LED street lighting - SHOULD match"),
        ("Lederverarbeitung für Handwerker", False, "Leather processing - should NOT match"),
        ("Lediglich eine Ausschreibung", False, "Merely a tender - should NOT match"),
        ("LED Leuchten für Straßen", True, "LED lights - SHOULD match"),
        ("Masterstudium Elektrotechnik", False, "Master's degree - should NOT match"),
        ("Lichtmast für Beleuchtung", True, "Light mast - SHOULD match"),
        ("Lampen und Leuchten LED", True, "Lamps and LED - SHOULD match"),
        ("Belederung von Fahrzeugen", False, "Vehicle upholstery - should NOT match"),
    ]
    
    # Keywords we're looking for
    keywords = ["led", "mast", "lampe", "leuchte", "beleuchtung", "licht", "straßen"]
    
    # Exclusion keywords
    exclude_keywords = ["leder", "lediglich", "master", "masterstudium", "semester"]
    
    print("="*70)
    print("TESTING WORD BOUNDARY MATCHING")
    print("="*70)
    print("\nKeywords to match:", keywords)
    print("Keywords to exclude:", exclude_keywords)
    print("\n" + "-"*70)
    
    for text, expected_match, description in test_texts:
        print(f"\nText: '{text}'")
        print(f"Expected: {description}")
        
        # Check with word boundaries
        text_lower = text.lower()
        
        # Check exclusions first
        excluded = False
        for ex_keyword in exclude_keywords:
            pattern = r'\b' + re.escape(ex_keyword) + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                excluded = True
                print(f"  ✗ EXCLUDED by '{ex_keyword}'")
                break
        
        if not excluded:
            # Check for matches
            matched = False
            matched_word = None
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower, re.IGNORECASE):
                    matched = True
                    matched_word = keyword
                    break
            
            if matched:
                print(f"  ✓ MATCHED by '{matched_word}'")
            else:
                print(f"  → No match found")
        
        # Verify result
        actual_match = (not excluded) and matched if not excluded else False
        if actual_match == expected_match:
            print(f"  ✅ Result correct!")
        else:
            print(f"  ❌ Result incorrect! Expected {expected_match}, got {actual_match}")
    
    print("\n" + "="*70)
    print("COMPARISON: With vs Without Word Boundaries")
    print("="*70)
    
    test_text = "LED-Beleuchtung vs Lederverarbeitung vs Masterstudium"
    print(f"\nTest text: '{test_text}'")
    print("\n1. WITHOUT word boundaries (substring match):")
    
    for keyword in ["led", "mast"]:
        if keyword in test_text.lower():
            print(f"  '{keyword}' matches in: {[word for word in test_text.split() if keyword in word.lower()]}")
    
    print("\n2. WITH word boundaries (whole word match):")
    
    for keyword in ["led", "mast"]:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        matches = re.findall(pattern, test_text, re.IGNORECASE)
        if matches:
            print(f"  '{keyword}' matches: {matches}")
        else:
            print(f"  '{keyword}' does NOT match (correct!)")

if __name__ == "__main__":
    test_word_boundary_matching()