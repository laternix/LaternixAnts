#!/usr/bin/env python3
"""
Analyze the structure of evergabe.de search results
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from utils.login_manager import LoginManager

def analyze_search_results():
    """Analyze the search results page structure"""
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Login
        print("Logging in...")
        login_manager = LoginManager(driver)
        if not login_manager.login():
            print("Login failed")
            return
        
        # Search for "Beleuchtung"
        search_url = "https://www.evergabe.de/auftraege/auftrag-suchen?utf8=%E2%9C%93&search%5Bsource%5D=form_cms&search%5Bfilters%5D%5Bpublish_end%5D=0&search%5Bquery%5D=beleuchtung&commit=Auftr%C3%A4ge+suchen"
        
        print(f"\nNavigating to search...")
        driver.get(search_url)
        time.sleep(5)
        
        # Take screenshot
        driver.save_screenshot("search_results.png")
        print("Screenshot saved: search_results.png")
        
        # Parse page
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        print("\n" + "="*60)
        print("ANALYZING SEARCH RESULTS PAGE")
        print("="*60)
        
        # Look for tables
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables on page")
        for i, table in enumerate(tables):
            classes = table.get('class', [])
            print(f"  Table {i+1}: classes={classes}")
            # Count rows in table
            rows = table.find_all('tr')
            print(f"    - {len(rows)} rows")
            # Check for links in table
            links = table.find_all('a', href=True)
            print(f"    - {len(links)} links")
            if links:
                for j, link in enumerate(links[:3]):  # Show first 3
                    href = link.get('href', '')
                    text = link.get_text(strip=True)[:50]
                    print(f"      Link {j+1}: {text}")
                    print(f"        href: {href[:80]}")
        
        # Look for divs with class containing 'result'
        print("\n" + "="*60)
        print("LOOKING FOR RESULT CONTAINERS")
        print("="*60)
        
        result_divs = soup.find_all('div', class_=lambda x: x and 'result' in str(x).lower())
        print(f"Found {len(result_divs)} divs with 'result' in class")
        
        # Look for list items
        list_items = soup.find_all('li', class_=lambda x: x and ('item' in str(x).lower() or 'result' in str(x).lower()))
        print(f"Found {len(list_items)} list items with 'item' or 'result' in class")
        
        # Analyze all links on page
        print("\n" + "="*60)
        print("ANALYZING ALL LINKS")
        print("="*60)
        
        all_links = soup.find_all('a', href=True)
        print(f"Total links on page: {len(all_links)}")
        
        # Categorize links
        tender_links = []
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if it looks like a tender detail link
            if '/auftraege/' in href:
                # Check various patterns
                is_tender = False
                reason = ""
                
                if any(str(i) in href for i in range(100000, 999999)):
                    is_tender = True
                    reason = "contains 6-digit number"
                elif 'detail' in href.lower() or 'anzeigen' in href.lower():
                    is_tender = True
                    reason = "contains detail/anzeigen"
                elif href.count('/') >= 5:
                    is_tender = True
                    reason = "deep URL path"
                elif '?' in href and any(param in href.lower() for param in ['id=', 'nr=', 'tender=']):
                    is_tender = True
                    reason = "has ID parameter"
                
                if is_tender:
                    tender_links.append({
                        'href': href,
                        'text': text[:80],
                        'reason': reason
                    })
        
        print(f"\nFound {len(tender_links)} potential tender links:")
        for i, link in enumerate(tender_links[:10], 1):  # Show first 10
            print(f"\n{i}. {link['text']}")
            print(f"   Reason: {link['reason']}")
            print(f"   URL: {link['href'][:100]}")
        
        # Save the HTML for manual inspection
        with open('search_results.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("\n✓ Full HTML saved to search_results.html")
        
        # Try clicking on the first tender link
        if tender_links:
            print("\n" + "="*60)
            print("TESTING FIRST TENDER LINK")
            print("="*60)
            
            first_link = tender_links[0]['href']
            if not first_link.startswith('http'):
                first_link = f"https://www.evergabe.de{first_link}"
            
            print(f"Opening: {first_link}")
            driver.get(first_link)
            time.sleep(3)
            
            # Check if we're on a detail page
            current_url = driver.current_url
            print(f"Current URL: {current_url}")
            
            # Take screenshot
            driver.save_screenshot("tender_detail.png")
            print("Screenshot saved: tender_detail.png")
            
            # Check for detail page indicators
            detail_soup = BeautifulSoup(driver.page_source, 'html.parser')
            h1 = detail_soup.find('h1')
            if h1:
                print(f"Page title: {h1.get_text(strip=True)[:100]}")
        
        input("\nPress Enter to close browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_search_results()