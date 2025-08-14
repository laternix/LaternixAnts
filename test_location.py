#!/usr/bin/env python3
"""
Test location extraction improvement
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evergabe_scraper import EvergabeScraper

def test_location_extraction():
    """Test that location is properly extracted with full address details"""
    
    print("="*70)
    print("TESTING IMPROVED LOCATION EXTRACTION")
    print("="*70)
    print("\nSearching for 'beleuchtung' and checking location extraction...")
    
    scraper = EvergabeScraper(headless=False, config_path='config_test.yaml')
    
    try:
        # Search for beleuchtung to test location extraction
        scraper.search_orders(
            search_terms=["beleuchtung"],
            max_pages=1
        )
        
        print("\n" + "="*70)
        print("LOCATION EXTRACTION RESULTS")
        print("="*70)
        
        # Check locations in results
        locations_found = 0
        for i, result in enumerate(scraper.results, 1):
            print(f"\n{i}. {result['title'][:60]}...")
            print(f"   Location: {result['location'] if result['location'] else 'NOT FOUND'}")
            if result['location']:
                locations_found += 1
                # Check if we have more than just city name
                if ',' in result['location'] or len(result['location']) > 30:
                    print("   ✓ Detailed location with address/state")
                else:
                    print("   → Basic location only")
        
        print("\n" + "-"*70)
        print(f"Results with location: {locations_found}/{len(scraper.results)}")
        
        if locations_found > 0:
            print("✅ Location extraction is working!")
        else:
            print("⚠️  No locations found - may need further investigation")
        
        # Save results
        scraper.save_results()
        print("\nResults saved for manual inspection")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    test_location_extraction()