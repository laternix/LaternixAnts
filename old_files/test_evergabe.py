#!/usr/bin/env python3
"""
Test script for evergabe.de with the correct URL pattern
"""

from evergabe_scraper import EvergabeScraper
import sys

def test():
    # Get profile path if provided
    profile_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("Testing evergabe.de scraper with correct URL pattern")
    print("=" * 60)
    
    if profile_path:
        print(f"Using Chrome profile: {profile_path}")
    else:
        print("No profile specified - may need login")
    
    # Create scraper instance
    scraper = EvergabeScraper(headless=False, profile_path=profile_path)
    
    try:
        # Test with just one search term and one page
        scraper.search_orders(
            search_terms=["Beleuchtung"],  # Just "lighting" 
            max_pages=1
        )
        
        print("\n" + "=" * 60)
        print(f"RESULTS: Found {len(scraper.results)} total listings")
        
        if scraper.results:
            print("\nFirst result:")
            result = scraper.results[0]
            for key, value in result.items():
                if value:
                    print(f"  {key}: {str(value)[:100]}")
        
        # Save results
        if scraper.results:
            scraper.save_results('test_results.json')
            scraper.save_to_excel('test_results.xlsx')
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    test()