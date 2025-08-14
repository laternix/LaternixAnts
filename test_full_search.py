#!/usr/bin/env python3
"""
Quick test search to verify all improvements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evergabe_scraper import EvergabeScraper

def test_full_search():
    """Do a quick search to test all improvements"""
    
    print("="*70)
    print("TESTING FULL SEARCH WITH ALL IMPROVEMENTS")
    print("="*70)
    
    # Use test config for limited results
    scraper = EvergabeScraper(headless=False, config_path='config_test.yaml')
    
    try:
        # Override config to limit results for faster testing
        print("\nSearching for 'LED' (limited to 5 results for testing)...")
        
        # Do a limited search
        import time
        start = time.time()
        
        # We'll just process first 5 results
        scraper.search_orders(
            search_terms=["LED"],
            max_pages=1
        )
        
        elapsed = time.time() - start
        
        print("\n" + "="*70)
        print("SEARCH COMPLETE - SUMMARY")
        print("="*70)
        print(f"Time taken: {elapsed:.1f} seconds")
        print(f"Results found: {len(scraper.results)}")
        
        if scraper.results:
            print("\nSample results with locations:")
            print("-"*70)
            
            for i, result in enumerate(scraper.results[:5], 1):
                print(f"\n{i}. {result['title'][:60]}...")
                if result['location']:
                    # Show first 100 chars of location
                    loc = result['location'][:100] + "..." if len(result['location']) > 100 else result['location']
                    print(f"   📍 Location: {loc}")
                else:
                    print(f"   📍 Location: Not specified")
                
                if result['vergabe_id']:
                    print(f"   🔢 Vergabe-ID: {result['vergabe_id']}")
                    
                if result['deadline']:
                    print(f"   ⏰ Deadline: {result['deadline']}")
        
        # Count how many have locations
        with_location = sum(1 for r in scraper.results if r['location'])
        print(f"\n{with_location}/{len(scraper.results)} results have location information")
        
        # Save results
        scraper.save_results()
        print("\n✓ Results saved to output directory")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    test_full_search()