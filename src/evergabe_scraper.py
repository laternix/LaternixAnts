#!/usr/bin/env python3
"""
Evergabe.de scraper for streetlamp work orders
"""

import os
import sys
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.login_manager import LoginManager
from utils.cookie_handler import CookieHandler
from utils.wait_helper import WaitHelper
from utils.config_manager import ConfigManager

class EvergabeScraper:
    def __init__(self, headless=None, config_path=None):
        """Initialize the scraper with Chrome driver
        
        Args:
            headless: Override headless setting from config
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = ConfigManager(config_path)
        
        # Use headless parameter or config value
        self.headless = headless if headless is not None else self.config.is_headless()
        
        self.setup_driver()
        self.results = []
        self.processed_vergabe_ids = set()  # Track processed vergabe_ids to avoid duplicates
        self.processed_urls = set()  # Also track URLs as backup
        self.logged_in = False
        self.login_manager = LoginManager(self.driver, self.config)
        self.cookie_handler = CookieHandler(self.driver)
        self.wait_helper = WaitHelper(
            self.driver, 
            default_timeout=self.config.get_timing('element_wait_timeout')
        )
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        
        if self.headless:
            # Use new headless mode for better compatibility
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            print("→ Running in headless mode")
        else:
            print("→ Running with visible browser")
            
        # Use profile if configured
        if self.config.get('browser.use_profile', True):
            import tempfile
            profile_dir = self.config.get('browser.profile_directory') or \
                         os.path.join(tempfile.gettempdir(), 'evergabe_chrome_profile')
            os.makedirs(profile_dir, exist_ok=True)
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument("--profile-directory=Default")
            print(f"→ Using Chrome profile at: {profile_dir}")
        
        # Window size from config
        width = self.config.get('browser.window_width', 1920)
        height = self.config.get('browser.window_height', 1080)
        chrome_options.add_argument(f"--window-size={width},{height}")
        
        # Add Chrome options from config
        for option in self.config.get_chrome_options():
            chrome_options.add_argument(option)
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Block tracking scripts and analytics that might interfere
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values": {
                "notifications": 2  # Block notifications
            }
        })
        
        # User agent to appear like regular browser
        chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✓ Chrome browser initialized")
        except Exception as e:
            print(f"✗ Error initializing Chrome: {e}")
            raise
    
    def ensure_logged_in(self):
        """Ensure we are logged in before proceeding"""
        if self.logged_in:
            # Check if still logged in
            self.driver.get("https://www.evergabe.de/auftraege/auftrag-suchen")
            self.wait_helper.wait_for_page_load()
            
            if 'anmelden' not in self.driver.current_url.lower():
                return True
            else:
                print("Session expired, logging in again...")
                self.logged_in = False
        
        # Perform login
        print("\n" + "="*60)
        print("LOGGING IN TO EVERGABE.DE")
        print("="*60)
        
        success = self.login_manager.login()
        if success:
            self.logged_in = True
            print("✓ Successfully logged in!")
        else:
            print("✗ Login failed - please check credentials")
            
        return self.logged_in
    
    def search_orders(self, search_terms=None, max_pages=None):
        """Search for work orders on evergabe.de"""
        
        # Ensure we're logged in first
        if not self.ensure_logged_in():
            print("Cannot proceed without login")
            return
        
        # Use config values if not provided
        if search_terms is None:
            search_terms = self.config.get_search_terms()
        
        if max_pages is None:
            max_pages = self.config.get_max_pages()
        
        print(f"\n{'='*60}")
        print(f"SEARCHING FOR ORDERS")
        print(f"{'='*60}")
        print(f"Search terms: {search_terms}")
        print(f"Max pages per term: {max_pages}")
        
        for term in search_terms:
            print(f"\n→ Searching for: {term}")
            self.search_term(term, max_pages)
            
    def search_term(self, search_term, max_pages=3):
        """Search for a specific term"""
        try:
            import urllib.parse
            
            # Build search URL
            params = {
                'utf8': '✓',
                'search[source]': 'form_cms',
                'search[filters][publish_end]': '0',
                'search[query]': search_term,
                'commit': 'Aufträge suchen'
            }
            
            base_url = "https://www.evergabe.de/auftraege/auftrag-suchen"
            query_string = urllib.parse.urlencode(params, safe='[]')
            search_url = f"{base_url}?{query_string}"
            
            print(f"  Navigating to search...")
            self.driver.get(search_url)
            
            # Smart wait for results
            self.wait_helper.wait_for_search_results()
            self.wait_helper.smart_wait(
                max_wait=self.config.get_timing('wait_after_search')
            )
            
            # Quick removal of any popups
            self.cookie_handler.quick_remove_usercentrics()
            
            # Check if we're still logged in
            if 'anmelden' in self.driver.current_url.lower():
                print("  Session lost, re-logging...")
                if not self.ensure_logged_in():
                    return
                # Try search again
                self.driver.get(search_url)
                self.wait_helper.wait_for_page_load()
            
            # Process results
            self.process_search_results(search_term, max_pages)
                
        except Exception as e:
            print(f"  Error searching: {e}")
            
    def process_search_results(self, search_term, max_pages):
        """Process the search results"""
        page = 1
        results_found = 0
        
        while page <= max_pages:
            print(f"\n  Page {page}:")
            
            # Smart wait for results
            self.wait_helper.smart_wait(
                max_wait=self.config.get_timing('wait_after_search')
            )
            
            # Parse page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Debug: Save page HTML for inspection
            with open(f'debug_search_page_{page}.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"    Saved page HTML to debug_search_page_{page}.html")
            
            # Look for the search results list items
            # evergabe.de uses <li class="result-list-item"> for results
            result_items = soup.find_all('li', class_='result-list-item')
            
            links = []
            
            if result_items:
                print(f"    Found {len(result_items)} result items")
                
                for item in result_items:
                    # Each result item has a data-href attribute with the tender URL
                    tender_url = item.get('data-href', '')
                    
                    if tender_url:
                        # Get the title from the h3 element
                        title_elem = item.find('h3', class_='result-list-item-title')
                        title = ''
                        if title_elem:
                            title_link = title_elem.find('a')
                            if title_link:
                                title = title_link.get_text(strip=True)
                        
                        # Get description/preview text from the result item
                        description = ''
                        # Look for description in various possible elements
                        desc_elem = item.find('p', class_='result-list-item-description')
                        if not desc_elem:
                            desc_elem = item.find('div', class_='description')
                        if not desc_elem:
                            desc_elem = item.find('p')  # Any paragraph in the item
                        
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)
                        
                        # Get any additional metadata (location, authority, etc.)
                        meta_text = ''
                        meta_elems = item.find_all(['span', 'div'], class_=lambda x: x and ('meta' in str(x).lower() or 'info' in str(x).lower()))
                        for meta in meta_elems:
                            meta_text += ' ' + meta.get_text(strip=True)
                        
                        # Combine all text for better filtering
                        full_text = f"{title} {description} {meta_text}"
                        
                        # Create an enhanced link object with all information
                        class ResultLink:
                            def __init__(self, href, title, full_text):
                                self.href = href
                                self.title = title
                                self.full_text = full_text
                            def get(self, attr, default=''):
                                if attr == 'href':
                                    return self.href
                                return default
                            def get_text(self, strip=True):
                                return self.title
                        
                        links.append(ResultLink(tender_url, title, full_text))
            else:
                print(f"    No result items found, checking for alternative structure")
                
                # Fallback: look for links in any result-related containers
                result_containers = soup.find_all(['div', 'ul'], class_=lambda x: x and 'result' in str(x).lower())
                
                for container in result_containers:
                    # Find links that look like tender details
                    container_links = container.find_all('a', href=lambda x: x and '/ausschreibung/' in x)
                    for link in container_links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        
                        # Skip if it's a navigation link
                        if any(skip in href.lower() for skip in ['merken', 'filter', 'sort']):
                            continue
                        
                        if text and len(text) > 10:
                            links.append(link)
            
            # Filter unique URLs and preserve full text for filtering
            unique_urls = []
            seen = set()
            for link in links:
                url = link.get('href', '')
                if not url.startswith('http'):
                    url = f"https://www.evergabe.de{url}"
                title = link.get_text(strip=True)
                # Get full text if available (for enhanced filtering)
                full_text = getattr(link, 'full_text', title)
                if url not in seen:
                    seen.add(url)
                    unique_urls.append((url, title, full_text))
            
            print(f"    Found {len(unique_urls)} unique order links")
            
            if len(unique_urls) == 0:
                print("    No results found on this page")
                break
            
            # Process each result (limit if configured)
            max_per_page = self.config.get_max_results_per_page()
            urls_to_process = unique_urls[:max_per_page] if max_per_page > 0 else unique_urls
            
            # Get early filtering setting
            early_filter = self.config.get('search.early_filter', True)
            filter_keywords = self.config.get('search.filter_keywords', [])
            exclude_keywords = self.config.get('search.exclude_keywords', [])
            use_word_boundaries = self.config.get('search.use_word_boundaries', True)
            skip_duplicates = self.config.get('search.skip_duplicates', True)
            
            skipped_count = 0
            duplicate_count = 0
            for idx, item in enumerate(urls_to_process, 1):
                # Handle both old format (url, title) and new format (url, title, full_text)
                if len(item) == 3:
                    url, title, full_text = item
                else:
                    url, title = item
                    full_text = title
                
                # Check for duplicate URLs first (fast check)
                if skip_duplicates and url in self.processed_urls:
                    print(f"    [{idx}/{len(urls_to_process)}] Skipping: {title[:60]}... (duplicate URL)")
                    duplicate_count += 1
                    continue
                
                # Early filtering - check full text (title + description) before opening detail page
                if early_filter and filter_keywords:
                    if self.should_skip_result(full_text, filter_keywords, exclude_keywords, use_word_boundaries):
                        print(f"    [{idx}/{len(urls_to_process)}] Skipping: {title[:60]}... (no keyword match)")
                        skipped_count += 1
                        continue
                
                print(f"    [{idx}/{len(urls_to_process)}] Processing: {title[:60]}...")
                processed = self.extract_order_details(url, search_term)
                if processed:
                    results_found += 1
                
                # Optional wait between results
                wait_time = self.config.get_timing('wait_between_results')
                if wait_time > 0:
                    time.sleep(wait_time)
            
            if skipped_count > 0:
                print(f"    Skipped {skipped_count} results (no keyword match)")
            if duplicate_count > 0:
                print(f"    Skipped {duplicate_count} duplicates")
            
            # Try next page
            if not self.go_to_next_page():
                break
                
            page += 1
            # No extra wait needed - page load handles it
        
        print(f"  Total results for '{search_term}': {results_found}")
    
    def extract_order_details(self, url, search_term):
        """Extract detailed information from an order page
        
        Returns:
            bool: True if successfully processed, False if skipped (duplicate or error)
        """
        skip_duplicates = self.config.get('search.skip_duplicates', True)
        
        try:
            # Open in new tab
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Navigate to detail page
            self.driver.get(url)
            
            # Smart wait for detail page
            self.wait_helper.wait_for_page_load()
            self.wait_helper.smart_wait(
                max_wait=self.config.get_timing('wait_for_detail_page')
            )
            
            # Check if logged in
            if 'anmelden' in self.driver.current_url.lower():
                print("      ✗ Not logged in - skipping details")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return False
            
            # Parse the page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract information
            info = {
                'search_term': search_term,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'title': '',
                'description': '',
                'contracting_authority': '',
                'location': '',
                'deadline': '',
                'cpv_codes': '',
                'reference': '',
                'vergabe_id': '',
                'procedure_type': '',
                'period_of_performance': '',
                'documents': []
            }
            
            # Get title from H1
            h1 = soup.find('h1', class_='header-flex__headline')
            if not h1:
                h1 = soup.find('h1')
            if h1:
                info['title'] = h1.get_text(strip=True)
            
            # Get description from the "Ausgeschriebene Leistung" section
            desc_section = soup.find('div', id='award_procedure_details')
            if desc_section:
                desc_text = desc_section.find('p', class_='shorttext')
                if desc_text:
                    info['description'] = desc_text.get_text(strip=True)
            
            # Get contracting authority (Auftraggeber)
            authority_section = soup.find('div', id='contracting_authority')
            if authority_section:
                # Look for the full authority text including all details
                authority_text = []
                # Get all p tags with authority information
                for p_tag in authority_section.find_all('p'):
                    text = p_tag.get_text(strip=True)
                    if text:
                        authority_text.append(text)
                if authority_text:
                    info['contracting_authority'] = ', '.join(authority_text)
            
            # Alternative: look for Auftraggeber header
            if not info['contracting_authority']:
                auftraggeber = soup.find(text=lambda x: x and 'Auftraggeber' in x)
                if auftraggeber:
                    parent = auftraggeber.find_parent()
                    if parent:
                        next_elem = parent.find_next_sibling()
                        if next_elem:
                            info['contracting_authority'] = next_elem.get_text(strip=True)
            
            # Get location from "Ausführungsort" section
            location_section = soup.find('div', id='award_procedure_places')
            if location_section:
                # Get all location-related text elements
                location_parts = []
                seen_texts = set()  # Track unique texts to avoid duplicates
                
                # Look for all p tags and spans with location info
                for elem in location_section.find_all(['p', 'span']):
                    text = elem.get_text(strip=True)
                    # Skip UI elements, headers, and duplicates
                    skip_terms = ['Ausführungsort', 'Karte anzeigen', 'mehr anzeigen', 
                                 'weniger anzeigen', 'anzeigen', '(1)', '(2)', '(3)']
                    
                    if text and not any(skip in text for skip in skip_terms) and len(text) > 2:
                        # Clean up the text
                        text = text.replace('Karte anzeigen', '').strip()
                        text = text.replace('mehr anzeigen', '').strip()
                        
                        # Only add if not already seen (avoid duplicates)
                        if text not in seen_texts:
                            seen_texts.add(text)
                            # Special handling for postal code + city + distance
                            if 'km)' in text:
                                # This is likely "04103 Leipzig (387 km)" format
                                location_parts.append(text)
                            elif text not in str(location_parts):  # Avoid substring duplicates
                                location_parts.append(text)
                
                # Clean and join location parts
                if location_parts:
                    # Remove any duplicate substrings
                    cleaned_parts = []
                    for part in location_parts:
                        is_duplicate = False
                        for other in location_parts:
                            if part != other and part in other:
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            cleaned_parts.append(part)
                    
                    info['location'] = ', '.join(cleaned_parts)
                else:
                    # Fallback: try to get any text from the section
                    location_text = location_section.get_text(separator=' ', strip=True)
                    # Clean up common UI elements
                    for term in ['Ausführungsort', 'Karte anzeigen', 'mehr anzeigen', '(1)']:
                        location_text = location_text.replace(term, ' ')
                    location_text = ' '.join(location_text.split())  # Clean whitespace
                    if location_text.strip():
                        info['location'] = location_text.strip()
            
            # Get deadline (Angebotsfrist)
            deadline_elem = soup.find('strong', class_='counter-headline', text='Angebotsfrist')
            if deadline_elem:
                deadline_parent = deadline_elem.find_parent()
                if deadline_parent:
                    deadline_span = deadline_parent.find_next('span', class_='d-block')
                    if deadline_span:
                        info['deadline'] = deadline_span.get_text(strip=True)
            
            # Get reference number (Vergabenummer) and Vergabe-ID
            ref_section = soup.find('div', id='file_number_contracting_authority')
            if ref_section:
                # Look for all h2 headers and their values
                h2_tags = ref_section.find_all('h2')
                for h2 in h2_tags:
                    header_text = h2.get_text(strip=True)
                    
                    # Check for Vergabenummer
                    if 'Vergabe' in header_text and 'nummer' in header_text:
                        # Look for the value - it might be in a p tag or as direct text
                        next_elem = h2.find_next_sibling()
                        if next_elem:
                            value = next_elem.get_text(strip=True)
                            # Filter out the header text if it's repeated
                            if value and not 'Auftraggebers' in value and value != header_text:
                                info['reference'] = value
                        else:
                            # Try to get text after the h2
                            parent = h2.parent
                            if parent:
                                full_text = parent.get_text(strip=True)
                                # Split by the header and get what comes after
                                parts = full_text.split(header_text)
                                if len(parts) > 1:
                                    value = parts[1].strip()
                                    # Take the first line if multiple lines
                                    if '\n' in value:
                                        value = value.split('\n')[0].strip()
                                    if value and not 'bei evergabe' in value:
                                        info['reference'] = value
                    
                    # Check for Vergabe-ID
                    elif 'Vergabe-ID' in header_text:
                        # Look for the value
                        next_elem = h2.find_next_sibling()
                        if next_elem:
                            value = next_elem.get_text(strip=True)
                            # Filter out the header text if it's repeated
                            if value and not 'evergabe.de' in value and value != header_text:
                                info['vergabe_id'] = value
                        else:
                            # Try to get text after the h2
                            parent = h2.parent
                            if parent:
                                full_text = parent.get_text(strip=True)
                                # Split by the header and get what comes after
                                parts = full_text.split(header_text)
                                if len(parts) > 1:
                                    value = parts[1].strip()
                                    # Extract just numbers
                                    import re
                                    match = re.search(r'\d+', value)
                                    if match:
                                        info['vergabe_id'] = match.group()
            
            # If still not found, try a more aggressive search
            if not info['reference'] or info['reference'] == '(des Auftraggebers)':
                # Look for pattern like "25A60179" - alphanumeric codes
                import re
                # Look for codes that look like reference numbers
                text = soup.get_text()
                # Pattern for reference numbers (mix of letters and numbers, 5-15 chars)
                matches = re.findall(r'\b[A-Z0-9]{5,15}\b', text)
                for match in matches:
                    # Check if this looks like a reference (has both letters and numbers)
                    if any(c.isalpha() for c in match) and any(c.isdigit() for c in match):
                        # Check if it's near "Vergabenummer" text
                        if 'Vergabenummer' in text:
                            idx = text.find('Vergabenummer')
                            match_idx = text.find(match)
                            if abs(match_idx - idx) < 200:  # Within 200 chars
                                info['reference'] = match
                                break
            
            if not info['vergabe_id'] or info['vergabe_id'] == '(bei evergabe.de)':
                # Look for 7-digit numbers that could be Vergabe-IDs
                import re
                text = soup.get_text()
                # Pattern for Vergabe-ID (typically 7 digits)
                matches = re.findall(r'\b\d{6,8}\b', text)
                for match in matches:
                    # Check if it's near "Vergabe-ID" text
                    if 'Vergabe-ID' in text:
                        idx = text.find('Vergabe-ID')
                        match_idx = text.find(match)
                        if abs(match_idx - idx) < 200:  # Within 200 chars
                            info['vergabe_id'] = match
                            break
            
            # Get procedure type
            type_section = soup.find('div', id='award_procedure_type')
            if type_section:
                type_span = type_section.find('span', text=lambda x: x and 'Ausschreibung' in x if x else False)
                if type_span:
                    info['procedure_type'] = type_span.get_text(strip=True)
            
            # Get period of performance
            period_section = soup.find('div', id='period_of_performance')
            if period_section:
                period_span = period_section.find('span')
                if period_span:
                    info['period_of_performance'] = period_span.get_text(strip=True)
            
            # Get CPV codes from badges
            cpv_badges = soup.find_all('a', class_='badge-primary-ultra-light', href=lambda x: x and 'craft_code_ids' in x)
            if cpv_badges:
                cpv_list = [badge.find('span', class_='link-text').get_text(strip=True) for badge in cpv_badges if badge.find('span', class_='link-text')]
                info['cpv_codes'] = ', '.join(cpv_list)
            
            # Find document links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.zip']) or 'herunterladen' in href:
                    if not href.startswith('http'):
                        href = f"https://www.evergabe.de{href}"
                    doc_name = link.get_text(strip=True) or 'Document'
                    if doc_name and 'PDF' not in doc_name and len(doc_name) > 3:
                        info['documents'].append({
                            'name': doc_name,
                            'url': href
                        })
            
            # Check for duplicate vergabe_id before adding to results
            if skip_duplicates and info['vergabe_id']:
                if info['vergabe_id'] in self.processed_vergabe_ids:
                    print(f"      ✗ Duplicate vergabe_id: {info['vergabe_id']} - skipping")
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    return False
                self.processed_vergabe_ids.add(info['vergabe_id'])
            
            # Mark URL as processed
            self.processed_urls.add(url)
            
            # Add to results
            self.results.append(info)
            print(f"      ✓ Extracted: {info['title'][:50]}")
            print(f"         Authority: {info['contracting_authority'][:50] if info['contracting_authority'] else 'N/A'}")
            print(f"         Location: {info['location'] if info['location'] else 'N/A'}")
            print(f"         Deadline: {info['deadline'] if info['deadline'] else 'N/A'}")
            if info['vergabe_id']:
                print(f"         Vergabe-ID: {info['vergabe_id']}")
            
            # Close tab and return
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            return True
            
        except Exception as e:
            print(f"      ✗ Error extracting details: {e}")
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return False
    
    def go_to_next_page(self):
        """Navigate to next page of results"""
        try:
            # Get current page number from URL to determine next page
            current_url = self.driver.current_url
            import re
            current_page = 1
            page_match = re.search(r'page=(\d+)', current_url)
            if page_match:
                current_page = int(page_match.group(1))
            next_page = current_page + 1
            
            # Updated selectors based on actual evergabe.de pagination
            next_selectors = [
                "//a[contains(text(), 'Nächste Seite')]",  # Primary selector for German "Next Page"
                f"//a[contains(@href, 'page={next_page}')]",  # Specific next page number
                "//a[contains(@class, 'page-link') and contains(@href, 'page=')]",  # Page link with next page
                "//ul[@class='pagination']//a[contains(@href, 'page=')]",  # Pagination links
                "//a[contains(text(), 'Weiter')]",  # Alternative German
                "//a[contains(text(), '»')]",  # Symbol
                "//a[@rel='next']",  # Semantic next
                "//a[contains(@class, 'next')]",  # Class-based
            ]
            
            for selector in next_selectors:
                try:
                    # Find all matching elements
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for next_btn in elements:
                        # Check if it's displayed and looks like a next button
                        if next_btn.is_displayed() and next_btn.is_enabled():
                            href = next_btn.get_attribute('href')
                            # Make sure it's a pagination link (contains page parameter)
                            if href and ('page=' in href or 'Nächste' in next_btn.text):
                                print(f"    → Clicking next page: {next_btn.text or 'Page link'}")
                                # Scroll to element to ensure it's in view
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                                self.wait_helper.smart_wait(max_wait=0.5)
                                
                                # Try to click
                                try:
                                    next_btn.click()
                                except:
                                    # If regular click fails, use JavaScript
                                    self.driver.execute_script("arguments[0].click();", next_btn)
                                
                                # Wait for new page to load
                                self.wait_helper.wait_for_page_load()
                                self.wait_helper.smart_wait(max_wait=1)
                                print(f"    ✓ Navigated to next page")
                                return True
                except Exception as e:
                    continue
            
            print("    ✗ No next page button found")
            return False
        except Exception as e:
            print(f"    ✗ Error navigating to next page: {e}")
            return False
    
    def should_skip_result(self, text, filter_keywords, exclude_keywords, use_word_boundaries=True):
        """Check if a result should be skipped based on title/preview text
        
        Returns True if result should be skipped, False if it should be processed
        """
        import re
        
        if not filter_keywords:
            return False  # No filtering, process everything
        
        text_lower = text.lower()
        
        # First check exclusions - if any exclusion keyword is found, skip
        if exclude_keywords:  # Check if exclude_keywords is not None/empty
            for ex_keyword in exclude_keywords:
                ex_keyword = ex_keyword.lower()
                if use_word_boundaries:
                    pattern = r'\b' + re.escape(ex_keyword) + r'\b'
                    if re.search(pattern, text_lower, re.IGNORECASE):
                        return True  # Skip this result
                else:
                    if ex_keyword in text_lower:
                        return True  # Skip this result
        
        # Check if any inclusion keyword matches
        for keyword in filter_keywords:
            keyword = keyword.lower()
            if use_word_boundaries:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return False  # Don't skip, keyword found
            else:
                if keyword in text_lower:
                    return False  # Don't skip, keyword found
        
        # No inclusion keywords matched, skip this result
        return True
    
    def filter_relevant(self, keywords=None, use_word_boundaries=None, exclude_keywords=None):
        """Filter results for relevant streetlamp orders
        
        Args:
            keywords: List of keywords to filter by (must contain at least one)
            use_word_boundaries: If True, match whole words only (avoid LED matching Leder)
            exclude_keywords: List of keywords to exclude (remove if contains any)
        """
        import re
        
        if keywords is None:
            keywords = self.config.get('search.filter_keywords', 
                                      ['straßen', 'lampe', 'leuchte', 'led', 'beleuchtung', 'licht'])
        
        if use_word_boundaries is None:
            use_word_boundaries = self.config.get('search.use_word_boundaries', True)
            
        if exclude_keywords is None:
            exclude_keywords = self.config.get('search.exclude_keywords', [])
        
        filtered = []
        for result in self.results:
            text = f"{result.get('title', '')} {result.get('description', '')}".lower()
            
            # First check exclusions - if any exclusion keyword is found, skip this result
            exclude = False
            if exclude_keywords:  # Check if exclude_keywords is not None/empty
                for ex_keyword in exclude_keywords:
                    ex_keyword = ex_keyword.lower()
                    if use_word_boundaries:
                        pattern = r'\b' + re.escape(ex_keyword) + r'\b'
                        if re.search(pattern, text, re.IGNORECASE):
                            exclude = True
                            break
                    else:
                        if ex_keyword in text:
                            exclude = True
                            break
            
            if exclude:
                continue  # Skip this result
            
            # Check if any inclusion keyword matches
            match_found = False
            for keyword in keywords:
                keyword = keyword.lower()
                
                if use_word_boundaries:
                    # Use word boundary regex to match whole words only
                    # \b ensures we match word boundaries
                    # This prevents LED from matching Leder or lediglich
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        match_found = True
                        break
                else:
                    # Simple substring match (old behavior)
                    if keyword in text:
                        match_found = True
                        break
            
            if match_found:
                filtered.append(result)
        
        return filtered
    
    def save_results(self):
        """Save results to files"""
        if not self.results:
            print("\nNo results to save")
            return
        
        # Ensure output directory exists
        output_dir = self.config.get_output_directory()
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        if self.config.get('output.include_timestamp', True):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = f'evergabe_results_{timestamp}'
        else:
            base_name = 'evergabe_results'
        
        formats = self.config.get_output_formats()
        
        # Save JSON
        if 'json' in formats:
            json_file = os.path.join(output_dir, f'{base_name}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Saved {len(self.results)} results to {json_file}")
        
        # Save Excel
        if 'excel' in formats:
            excel_file = os.path.join(output_dir, f'{base_name}.xlsx')
            df = pd.DataFrame(self.results)
            
            # Handle documents column
            if 'documents' in df.columns:
                df['documents'] = df['documents'].apply(
                    lambda x: '\n'.join([d['name'] for d in x]) if isinstance(x, list) else ''
                )
            
            df.to_excel(excel_file, index=False)
            print(f"✓ Saved results to {excel_file}")
        
        # Save CSV
        if 'csv' in formats:
            csv_file = os.path.join(output_dir, f'{base_name}.csv')
            df = pd.DataFrame(self.results)
            
            # Handle documents column
            if 'documents' in df.columns:
                df['documents'] = df['documents'].apply(
                    lambda x: '\n'.join([d['name'] for d in x]) if isinstance(x, list) else ''
                )
            
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"✓ Saved results to {csv_file}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("\n✓ Browser closed")