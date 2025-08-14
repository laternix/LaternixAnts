#!/usr/bin/env python3
"""
Test early filtering functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evergabe_scraper import EvergabeScraper

def test_early_filtering():
    """Test that early filtering correctly skips non-matching results"""
    
    print("="*70)
    print("TESTING EARLY FILTERING WITH 'LED' SEARCH")
    print("="*70)
    
    # Create a scraper instance (we won't actually run it)
    scraper = EvergabeScraper(headless=False)
    
    # Test cases: (text, should_skip_expected)
    test_cases = [
        # Should NOT skip (contain relevant keywords)
        ("LED-Straßenbeleuchtung modernisierung - Installation neuer LED Leuchten", False),
        ("Beleuchtung Straßenlampen - Umrüstung auf moderne Technik", False),
        ("Lichtmast Erneuerung - Austausch der Masten im Stadtgebiet", False),
        ("Öffentliche Beleuchtung - LED Umstellung 2025", False),
        
        # SHOULD skip (no relevant keywords or excluded)
        ("Masterstudium Elektrotechnik - Neue Studienplätze", True),
        ("Lederverarbeitung für Handwerksbetriebe", True),
        ("Gebäudereinigung und Hausmeisterdienste", True),
        ("IT-Dienstleistungen für Verwaltung", True),
        ("Lediglich Informationsveranstaltung", True),
        
        # Edge cases
        ("Belederung und Polsterarbeiten", True),  # Contains "led" but as part of "Belederung"
        ("Masterplan Stadtentwicklung", True),  # Contains "mast" but as part of "Master"
    ]
    
    # Get config values
    filter_keywords = scraper.config.get('search.filter_keywords', [])
    exclude_keywords = scraper.config.get('search.exclude_keywords', [])
    use_word_boundaries = scraper.config.get('search.use_word_boundaries', True)
    
    print(f"\nFilter keywords: {filter_keywords[:5]}...")
    print(f"Exclude keywords: {exclude_keywords[:5]}...")
    print(f"Word boundaries: {use_word_boundaries}")
    print("\n" + "-"*70)
    
    passed = 0
    failed = 0
    
    for text, expected_skip in test_cases:
        actual_skip = scraper.should_skip_result(
            text, 
            filter_keywords, 
            exclude_keywords, 
            use_word_boundaries
        )
        
        if actual_skip == expected_skip:
            result = "✅ PASS"
            passed += 1
        else:
            result = "❌ FAIL"
            failed += 1
        
        action = "SKIP" if actual_skip else "PROCESS"
        expected_action = "SKIP" if expected_skip else "PROCESS"
        
        print(f"\nText: {text[:60]}...")
        print(f"  Expected: {expected_action}, Actual: {action} - {result}")
    
    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    # Cleanup
    scraper.close()
    
    return failed == 0

if __name__ == "__main__":
    success = test_early_filtering()
    sys.exit(0 if success else 1)