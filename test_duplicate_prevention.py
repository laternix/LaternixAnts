#!/usr/bin/env python3
"""
Test duplicate prevention functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evergabe_scraper import EvergabeScraper

def test_duplicate_prevention():
    """Test that duplicate prevention works with multiple search terms"""
    
    print("="*70)
    print("TESTING DUPLICATE PREVENTION")
    print("="*70)
    print("\nSearching with multiple overlapping terms to test duplicate detection")
    print("Terms: 'beleuchtung' and 'LED' (should have overlapping results)")
    
    scraper = EvergabeScraper(headless=False)
    
    try:
        # Search with two terms that will likely have overlapping results
        scraper.search_orders(
            search_terms=["beleuchtung", "LED"],
            max_pages=1  # Just 1 page each to keep it quick
        )
        
        print("\n" + "="*70)
        print("DUPLICATE PREVENTION SUMMARY")
        print("="*70)
        
        # Check for duplicates in results
        vergabe_ids = []
        urls = []
        duplicates_found = 0
        
        for result in scraper.results:
            if result['vergabe_id'] and result['vergabe_id'] in vergabe_ids:
                duplicates_found += 1
                print(f"❌ Duplicate found in results: {result['vergabe_id']}")
            else:
                if result['vergabe_id']:
                    vergabe_ids.append(result['vergabe_id'])
            
            if result['url'] in urls:
                duplicates_found += 1
                print(f"❌ Duplicate URL found: {result['url'][:50]}...")
            else:
                urls.append(result['url'])
        
        print(f"\nTotal results: {len(scraper.results)}")
        print(f"Unique vergabe_ids: {len(vergabe_ids)}")
        print(f"Unique URLs: {len(urls)}")
        
        if duplicates_found == 0:
            print("✅ SUCCESS: No duplicates in final results!")
        else:
            print(f"⚠️  WARNING: Found {duplicates_found} duplicates in results")
        
        # Show some results
        print("\nSample results (first 5):")
        for i, result in enumerate(scraper.results[:5], 1):
            print(f"{i}. {result['title'][:60]}...")
            if result['vergabe_id']:
                print(f"   Vergabe-ID: {result['vergabe_id']}")
        
        # Save results
        scraper.save_results()
        
    finally:
        scraper.close()

if __name__ == "__main__":
    test_duplicate_prevention()