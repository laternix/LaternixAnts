#!/usr/bin/env python3
"""
Test improved filtering with new keywords
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evergabe_scraper import EvergabeScraper

def test_improved_filtering():
    """Test with examples from actual search results"""
    
    print("="*70)
    print("TESTING IMPROVED FILTERING WITH NEW KEYWORDS")
    print("="*70)
    
    scraper = EvergabeScraper(headless=True)
    
    # Get current config
    filter_keywords = scraper.config.get('search.filter_keywords', [])
    exclude_keywords = scraper.config.get('search.exclude_keywords', [])
    use_word_boundaries = scraper.config.get('search.use_word_boundaries', True)
    
    print(f"\nTotal filter keywords: {len(filter_keywords)}")
    print(f"Use word boundaries: {use_word_boundaries}")
    
    # Test with real examples from the search
    test_texts = [
        # Should be PROCESSED (lighting-related)
        "Beleuchtungstausch Neubau",
        "Erneuerung der Beleuchtungsanlagen Museum König",
        "Umrüstung Beleuchtung und SiBe",
        "Erneuerung Beleuchtungsanlage - Elektroarbeiten",
        "SZ Celle | Erneuerung Beleuchtung",
        "Beleuchtung des Weihnachtsmarkts 2025 -2027",
        "Erdarbeiten Beleuchtung Rad-Gehweg Bahntrasse",
        "Elektroarbeiten - Beleuchtung CIM-Labor",
        "Elektroanlagen und Beleuchtung - Hbst. Kabelkamp",
        "Umbau Mensa und LED-Umrüstung Beleuchtung",
        "Flutlichtanlage Osterfeld Goslar",
        "Errichtung von Flutlichtmasten, BSA Rosellen Neuss",
        "Präqualifikationsverfahren für Lichtmaste",
        "Straßenbeleuchtung LED Leuchten",
        "Lieferung und Montage von LED-Leuchten",
        "Leuchtentausch LED 2. Abschnitt",
        "Austausch Leuchtmittel",
        "LED-Straßenleuchten und Straßenbeleuchtungsmasten",
        "Ersatzneubau Straßenbeleuchtung Stadt Eckartsberga",
        
        # Should be SKIPPED (not lighting-related even if contains "licht" or "leucht")
        "Errichtung Feuerwehrgerätehaus Heinrichsort in Lichtenstein",
        "Bankett und Lichtraumprofil",
        "Metallbauarbeiten (Lichtbauelemente)",
        "Neubau des Wohnquartiers Lichtenrader Bogen",
        "Telematik Lichtbildbeschaffung",
        "Wartung Lichtrufanlagen und Rufbereitschaft",
        "Erneuerung RWA-Lichtkuppeln",
        "St 2027 Kreisverkehr Gut Lichtenberg",
        "Austausch Lichtrufanlage",
        "Zehntscheune Lampertheim - Los 26 - Parkettarbeiten",
        "Leasingvertrag große Kehrmaschine, Lampertheim",
        "Fertigung und Lieferung von PE-Basistonnen Leuchtonne B7",
    ]
    
    print("\n" + "-"*70)
    print("TESTING EACH RESULT:\n")
    
    processed = 0
    skipped = 0
    
    for text in test_texts:
        should_skip = scraper.should_skip_result(
            text, 
            filter_keywords, 
            exclude_keywords, 
            use_word_boundaries
        )
        
        if should_skip:
            print(f"❌ SKIP: {text[:60]}...")
            skipped += 1
        else:
            print(f"✅ PROCESS: {text[:60]}...")
            processed += 1
    
    print("\n" + "-"*70)
    print(f"SUMMARY: {processed} would be processed, {skipped} would be skipped")
    print("="*70)
    
    # Calculate accuracy
    expected_process = 19  # First 19 should be processed
    expected_skip = len(test_texts) - expected_process
    
    accuracy_message = ""
    if processed == expected_process and skipped == expected_skip:
        accuracy_message = "✅ PERFECT! Filter is working as expected."
    else:
        accuracy_message = f"⚠️  Expected {expected_process} processed, got {processed}"
    
    print(f"\n{accuracy_message}")
    
    scraper.close()

if __name__ == "__main__":
    test_improved_filtering()