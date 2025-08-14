#!/usr/bin/env python3
"""
Test LED search with early filtering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evergabe_scraper import EvergabeScraper

def test_led_search():
    """Test LED search with early filtering to show performance improvement"""
    
    print("="*70)
    print("TESTING LED SEARCH WITH EARLY FILTERING")
    print("="*70)
    
    scraper = EvergabeScraper(headless=False)
    
    try:
        # Search for LED with max 1 page
        print("\n→ Searching for 'LED' with early filtering enabled")
        print("  This will skip results that don't match our filter keywords")
        print("  Filter keywords include: led, beleuchtung, straßen, lampe, leuchte, etc.")
        print("  Exclusions: leder, lediglich, master, etc.")
        
        scraper.search_orders(
            search_terms=["LED"],
            max_pages=1
        )
        
        # Show summary
        print("\n" + "="*70)
        print("SEARCH SUMMARY")
        print("="*70)
        print(f"Total results extracted: {len(scraper.results)}")
        
        if scraper.results:
            print("\nExtracted results:")
            for idx, result in enumerate(scraper.results, 1):
                print(f"{idx}. {result['title'][:80]}...")
                
        # Save results
        scraper.save_results()
        
    finally:
        scraper.close()

if __name__ == "__main__":
    test_led_search()