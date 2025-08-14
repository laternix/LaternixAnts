#!/usr/bin/env python3
"""
Simple Evergabe.de scraper using requests first to test the website
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def test_website():
    """Test if we can access the website and understand its structure"""
    
    print("Testing evergabe.de website access...")
    print("=" * 60)
    
    # Test basic access
    url = "https://www.evergabe.de"
    
    try:
        # Try to get the main page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Successfully accessed the website!")
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for search form
            search_forms = soup.find_all('form')
            print(f"\nFound {len(search_forms)} forms on the page")
            
            # Look for input fields
            inputs = soup.find_all('input')
            print(f"Found {len(inputs)} input fields")
            
            for inp in inputs[:5]:  # Show first 5 inputs
                print(f"  - Input: type={inp.get('type')}, name={inp.get('name')}, placeholder={inp.get('placeholder')}")
            
            # Try to find search-related elements
            search_elements = soup.find_all(['input', 'button'], attrs={'class': lambda x: x and 'search' in str(x).lower()})
            print(f"\nFound {len(search_elements)} search-related elements")
            
            # Look for links that might be tenders
            links = soup.find_all('a', href=True)
            tender_links = [link for link in links if any(
                keyword in link.get('href', '').lower() 
                for keyword in ['tender', 'vergabe', 'ausschreibung', 'suche']
            )]
            print(f"\nFound {len(tender_links)} potential tender links")
            
            for link in tender_links[:3]:
                print(f"  - {link.get('href')[:80]}")
            
            # Try search URL directly
            search_terms = ["Straßenbeleuchtung", "Beleuchtung", "LED"]
            
            for term in search_terms:
                print(f"\n\nTrying search for: {term}")
                search_url = f"{url}/suche/{term}"
                
                try:
                    search_response = requests.get(search_url, headers=headers, timeout=10)
                    print(f"  Search URL status: {search_response.status_code}")
                    
                    if search_response.status_code == 200:
                        search_soup = BeautifulSoup(search_response.text, 'html.parser')
                        
                        # Look for results
                        possible_results = search_soup.find_all(['article', 'div', 'li'], 
                                                               class_=lambda x: x and any(
                                                                   keyword in str(x).lower() 
                                                                   for keyword in ['result', 'item', 'tender', 'vergabe']
                                                               ))
                        print(f"  Found {len(possible_results)} potential results")
                        
                except Exception as e:
                    print(f"  Error searching: {e}")
                
                time.sleep(1)  # Be polite
            
        else:
            print(f"Failed to access website. Status: {response.status_code}")
            
    except Exception as e:
        print(f"Error accessing website: {e}")
        print("\nThe website might require JavaScript rendering.")
        print("A Selenium-based approach would be needed for full functionality.")
    
    print("\n" + "=" * 60)
    print("Test completed.")
    print("\nRecommendations:")
    print("1. The website likely uses JavaScript for search functionality")
    print("2. Selenium with Firefox/Chrome would be needed for full scraping")
    print("3. Consider using the website's API if available")
    print("4. Check if there's a sitemap.xml or robots.txt for guidance")

if __name__ == "__main__":
    test_website()