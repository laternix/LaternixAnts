#!/usr/bin/env python3
"""
Analyze search results to find lighting-related keywords
"""

import sys
import os
import re
from collections import Counter
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.evergabe_scraper import EvergabeScraper

def analyze_keywords():
    """Search for various lighting terms and analyze the results"""
    
    print("="*70)
    print("ANALYZING SEARCH RESULTS FOR LIGHTING KEYWORDS")
    print("="*70)
    
    scraper = EvergabeScraper(headless=False)
    
    # Words found in results
    all_words = []
    lighting_related = []
    
    try:
        # Search with different broad terms
        search_terms = ["beleuchtung", "leucht", "licht", "lampe"]
        
        for term in search_terms:
            print(f"\n→ Searching for '{term}' to analyze results...")
            
            # Search and collect just titles/descriptions
            scraper.search_orders(
                search_terms=[term],
                max_pages=2  # Look at 2 pages per term
            )
        
        print("\n" + "="*70)
        print("ANALYZING COLLECTED RESULTS")
        print("="*70)
        
        # Analyze the HTML files we saved
        import glob
        from bs4 import BeautifulSoup
        
        for html_file in glob.glob("debug_search_page_*.html"):
            print(f"\nAnalyzing {html_file}...")
            
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Find all result items
            result_items = soup.find_all('li', class_='result-list-item')
            
            for item in result_items:
                # Get title
                title_elem = item.find('h3', class_='result-list-item-title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    # Get description
                    desc_elem = item.find('p')
                    desc = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Get metadata
                    meta_elems = item.find_all(['span', 'div'], class_=True)
                    meta_text = ' '.join([elem.get_text(strip=True) for elem in meta_elems])
                    
                    full_text = f"{title} {desc} {meta_text}"
                    
                    # Find potential lighting-related compound words
                    # Look for words containing common lighting roots
                    lighting_roots = ['leucht', 'licht', 'lamp', 'beleucht', 'strahl', 'leuchte', 'mast']
                    
                    words = re.findall(r'\b[a-züäößA-ZÜÄÖ]+\b', full_text)
                    for word in words:
                        word_lower = word.lower()
                        # Check if word contains lighting root
                        for root in lighting_roots:
                            if root in word_lower and len(word_lower) > len(root):
                                if word_lower not in lighting_related:
                                    lighting_related.append(word_lower)
                                    print(f"  Found: {word_lower}")
        
        # Sort and display unique lighting-related words
        lighting_related = sorted(set(lighting_related))
        
        print("\n" + "="*70)
        print("DISCOVERED LIGHTING-RELATED KEYWORDS")
        print("="*70)
        
        # Group by root word
        grouped = {}
        for word in lighting_related:
            # Find which root it contains
            for root in ['leucht', 'licht', 'lamp', 'beleucht', 'strahl', 'mast']:
                if root in word:
                    if root not in grouped:
                        grouped[root] = []
                    grouped[root].append(word)
                    break
        
        for root, words in grouped.items():
            print(f"\n{root.upper()}-based words:")
            for word in sorted(words):
                print(f"  - {word}")
        
        # Look for common prefixes/suffixes
        print("\n" + "="*70)
        print("COMMON PATTERNS")
        print("="*70)
        
        # Find compound patterns
        compounds = []
        for word in lighting_related:
            if 'beleuchtung' in word and word != 'beleuchtung':
                prefix = word.replace('beleuchtung', '')
                if prefix:
                    compounds.append(f"{prefix}beleuchtung")
            elif 'leuchte' in word and word != 'leuchte':
                if word.endswith('leuchte'):
                    prefix = word.replace('leuchte', '')
                    if prefix:
                        compounds.append(f"{prefix}leuchte")
                elif word.endswith('leuchten'):
                    prefix = word.replace('leuchten', '')
                    if prefix:
                        compounds.append(f"{prefix}leuchten")
        
        if compounds:
            print("\nCompound patterns found:")
            for comp in sorted(set(compounds)):
                print(f"  - {comp}")
        
        # Save results
        scraper.save_results()
        
    finally:
        scraper.close()
    
    return lighting_related

if __name__ == "__main__":
    keywords = analyze_keywords()