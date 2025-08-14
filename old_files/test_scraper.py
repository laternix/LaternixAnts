#!/usr/bin/env python3
"""
Simple test script for Evergabe.de scraper
"""

from evergabe_scraper import EvergabeScraper

def test_basic():
    """Test basic functionality with headless mode"""
    print("Testing Evergabe.de scraper in headless mode...")
    print("=" * 60)
    
    # Use headless mode for testing
    scraper = EvergabeScraper(headless=True)
    
    try:
        # Search with limited scope for testing
        scraper.search_orders(
            search_terms=["Straßenbeleuchtung"],
            max_pages=1
        )
        
        # Show results
        print(f"\nTotal results found: {len(scraper.results)}")
        
        # Filter relevant ones
        relevant = scraper.filter_relevant_orders()
        print(f"Relevant streetlamp orders: {len(relevant)}")
        
        # Save if we found anything
        if scraper.results:
            scraper.save_results('test_results.json')
            print("\nFirst 3 results:")
            for i, result in enumerate(scraper.results[:3], 1):
                print(f"\n{i}. {result['title']}")
                print(f"   Search term: {result['search_term']}")
                if result['url']:
                    print(f"   URL: {result['url'][:80]}...")
        else:
            print("\nNo results found - the website structure might have changed.")
            print("Try running with headless=False to see what's happening.")
            
    except Exception as e:
        print(f"Error during test: {e}")
        
    finally:
        scraper.close()
        print("\nTest completed.")

if __name__ == "__main__":
    test_basic()