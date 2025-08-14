#!/usr/bin/env python3
"""
Evergabe.de scraper for streetlamp work orders
"""

import os
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

class EvergabeScraper:
    def __init__(self, headless=True, profile_path=None, auto_login=True):
        """
        Initialize the scraper with Chrome driver
        
        Args:
            headless: Run in headless mode (default True)
            profile_path: Path to Chrome profile directory (e.g., '/home/user/.config/google-chrome/Default')
            auto_login: Automatically login using .env credentials (default True)
        """
        self.setup_driver(headless, profile_path)
        self.results = []
        self.logged_in = False
        
        # Try auto-login if enabled and no profile is being used
        if auto_login and not profile_path:
            self.auto_login()
        
    def setup_driver(self, headless, profile_path=None):
        """
        Setup Chrome driver with options
        
        Args:
            headless: Run in headless mode
            profile_path: Path to Chrome profile directory
        """
        chrome_options = Options()
        
        # Add profile if specified
        if profile_path:
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            print(f"Using Chrome profile: {profile_path}")
            # Note: When using a profile, headless mode might not work properly
            if headless:
                print("Warning: Headless mode may not work properly with a user profile")
        
        if headless and not profile_path:
            chrome_options.add_argument("--headless")
            
        # Common options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent to appear more like a regular browser
        chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Chrome browser initialized successfully")
        except Exception as e:
            print(f"Error initializing Chrome: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure Chrome is installed: google-chrome --version")
            print("2. If using a profile, check the path is correct")
            print("3. Close any existing Chrome instances using the same profile")
            raise
    
    def load_env_credentials(self):
        """Load credentials from .env file"""
        username = None
        password = None
        
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('EVERGABE_USERNAME='):
                        username = line.split('=', 1)[1].strip()
                    elif line.startswith('EVERGABE_PASSWORD='):
                        password = line.split('=', 1)[1].strip()
        
        return username, password
    
    def handle_cookie_popup(self):
        """Handle cookie consent popup if it appears"""
        try:
            # Common cookie popup patterns
            cookie_selectors = [
                "//button[contains(text(), 'Akzeptieren')]",
                "//button[contains(text(), 'Alle akzeptieren')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(@class, 'accept')]",
                "//a[contains(text(), 'Akzeptieren')]",
                "//button[contains(text(), 'Zustimmen')]",
                "//button[contains(@id, 'accept')]",
                "//button[contains(@class, 'cookie') and contains(@class, 'accept')]"
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_button = self.driver.find_element(By.XPATH, selector)
                    if cookie_button.is_displayed():
                        cookie_button.click()
                        print("Handled cookie popup")
                        time.sleep(1)
                        return True
                except:
                    continue
                    
            # Also try to close cookie popup by clicking X or decline
            close_selectors = [
                "//button[@aria-label='Close']",
                "//button[contains(@class, 'close')]",
                "//span[contains(@class, 'close')]"
            ]
            
            for selector in close_selectors:
                try:
                    close_button = self.driver.find_element(By.XPATH, selector)
                    if close_button.is_displayed():
                        close_button.click()
                        print("Closed cookie popup")
                        time.sleep(1)
                        return True
                except:
                    continue
                    
        except Exception as e:
            # No cookie popup found or already handled
            pass
        
        return False
    
    def auto_login(self):
        """Automatically login using credentials from .env file"""
        print("\nAttempting automatic login...")
        
        # Load credentials
        username, password = self.load_env_credentials()
        
        if not username or not password:
            print("No credentials found in .env file")
            print("Run 'python setup_evergabe.py' to configure login")
            return False
        
        try:
            # First navigate to main page to handle cookies
            print("Navigating to evergabe.de...")
            self.driver.get("https://www.evergabe.de")
            time.sleep(2)
            
            # Handle cookie popup if present
            self.handle_cookie_popup()
            
            # Now navigate to login page
            login_url = "https://www.evergabe.de/anmelden"
            print(f"Navigating to login page...")
            self.driver.get(login_url)
            time.sleep(2)
            
            # Handle cookie popup again if it appears on login page
            self.handle_cookie_popup()
            
            # Check if already logged in (redirected away from login)
            if 'anmelden' not in self.driver.current_url.lower():
                print("Already logged in!")
                self.logged_in = True
                return True
            
            # Wait for and find username field
            try:
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
            except:
                # Try alternative selectors
                username_field = self.driver.find_element(By.XPATH, "//input[@name='username' or @type='email' or @type='text']")
            
            username_field.clear()
            username_field.send_keys(username)
            print("Entered username")
            
            # Find and fill password field
            try:
                password_field = self.driver.find_element(By.ID, "password")
            except:
                password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
                
            password_field.clear()
            password_field.send_keys(password)
            print("Entered password")
            
            # Find and click login button
            login_selectors = [
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(text(), 'Anmelden')]",
                "//button[contains(text(), 'Login')]",
                "//input[@value='Anmelden']"
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.XPATH, selector)
                    if login_button.is_displayed():
                        login_button.click()
                        login_clicked = True
                        print("Clicked login button")
                        break
                except:
                    continue
            
            if not login_clicked:
                # Try submitting the form
                password_field.submit()
                print("Submitted login form")
            
            # Wait for login to complete
            time.sleep(4)
            
            # Handle any cookie popup that appears after login
            self.handle_cookie_popup()
            
            # Check if login was successful by trying to access a protected page
            self.driver.get("https://www.evergabe.de/auftraege/auftrag-suchen")
            time.sleep(2)
            
            # Check if we're redirected to login or if we can access the search
            current_url = self.driver.current_url.lower()
            if 'anmelden' not in current_url and 'login' not in current_url:
                print("✓ Login successful - can access search page!")
                self.logged_in = True
                
                # Store cookies for session persistence
                self.cookies = self.driver.get_cookies()
                
                return True
            else:
                print("✗ Login failed - redirected to login page")
                print("Run 'python setup_evergabe.py' to verify credentials")
                self.logged_in = False
                return False
                
        except Exception as e:
            print(f"Error during auto-login: {e}")
            self.logged_in = False
            return False
        
    def search_orders(self, search_terms=None, max_pages=5):
        """
        Search for work orders on evergabe.de
        
        Args:
            search_terms: List of search terms (default: streetlamp related terms)
            max_pages: Maximum number of pages to scrape
        """
        if search_terms is None:
            # Default search terms for streetlamp-related orders
            search_terms = [
                "Straßenbeleuchtung",
                "Straßenlampen", 
                "Beleuchtung",
                "LED Beleuchtung",
                "Leuchten",
                "Lichtmasten",
                "Außenbeleuchtung",
                "öffentliche Beleuchtung"
            ]
        
        print(f"Starting search with terms: {search_terms}")
        
        for term in search_terms:
            print(f"\nSearching for: {term}")
            self.search_term(term, max_pages)
            
    def search_term(self, search_term, max_pages=5):
        """Search for a specific term"""
        try:
            # Build the correct search URL
            import urllib.parse
            
            # Encode the search term properly
            params = {
                'utf8': '✓',
                'search[source]': 'form_cms',
                'search[filters][publish_end]': '0',
                'search[query]': search_term,
                'commit': 'Aufträge suchen'
            }
            
            # Build the URL with parameters
            base_url = "https://www.evergabe.de/auftraege/auftrag-suchen"
            query_string = urllib.parse.urlencode(params, safe='[]')
            search_url = f"{base_url}?{query_string}"
            
            print(f"Searching for: {search_term}")
            print(f"URL: {search_url[:100]}...")
            
            # Navigate directly to search results
            self.driver.get(search_url)
            time.sleep(3)
            
            # Handle any cookie popup that might appear
            self.handle_cookie_popup()
            
            # Check if we need to login
            current_url = self.driver.current_url.lower()
            if 'anmelden' in current_url or 'login' in current_url:
                print("Redirected to login page - attempting login...")
                if not self.logged_in:
                    if self.auto_login():
                        # After successful login, navigate back to search
                        self.driver.get(search_url)
                        time.sleep(3)
                    else:
                        print("Login required to access search results")
                        return
            
            # Process results
            self.process_search_results(search_term, max_pages)
                
        except Exception as e:
            print(f"Error searching for {search_term}: {e}")
            
    def process_search_results(self, search_term, max_pages):
        """Process the search results"""
        page = 1
        
        while page <= max_pages:
            print(f"Processing page {page}")
            
            # Wait for results to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                print("Page loading timeout")
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for tender/order listings - evergabe.de specific patterns
            # Try multiple selectors based on typical evergabe.de structure
            listings = []
            
            # Common patterns for evergabe.de listings
            selectors = [
                ('div', {'class': 'result'}),
                ('div', {'class': 'auftrag'}),
                ('article', {}),
                ('div', {'class': lambda x: x and 'listing' in str(x).lower()}),
                ('tr', {'class': lambda x: x and 'row' in str(x).lower()}),
                ('div', {'class': lambda x: x and 'card' in str(x).lower()}),
            ]
            
            for tag, attrs in selectors:
                found = soup.find_all(tag, attrs)
                if found:
                    listings = found
                    break
            
            # If still no listings, try to find any div with links to /auftraege/
            if not listings:
                all_divs = soup.find_all('div')
                listings = [div for div in all_divs if div.find('a', href=lambda x: x and '/auftraege/' in x)]
            
            print(f"Found {len(listings)} listings on page {page}")
            
            if len(listings) == 0:
                # Print page title to debug
                title = soup.find('title')
                if title:
                    print(f"Page title: {title.text}")
                # Check if we're on a login page
                if 'anmeld' in str(soup).lower() or 'login' in str(soup).lower():
                    print("Note: Appears to be a login page. Use Chrome profile with saved login.")
            
            for listing in listings:
                self.extract_listing_info(listing, search_term)
            
            # Try to go to next page
            if not self.go_to_next_page():
                break
                
            page += 1
            time.sleep(2)
            
    def extract_listing_info(self, listing, search_term):
        """Extract basic information from a listing and URL for detailed scraping"""
        try:
            info = {
                'search_term': search_term,
                'scraped_at': datetime.now().isoformat(),
                'title': '',
                'description': '',
                'location': '',
                'deadline': '',
                'reference': '',
                'url': '',
                # Fields to be filled from detail page
                'detailed_description': '',
                'contracting_authority': '',
                'procedure_type': '',
                'cpv_codes': '',
                'submission_deadline': '',
                'opening_date': '',
                'contract_duration': '',
                'estimated_value': '',
                'contact_info': '',
                'documents': []
            }
            
            # Extract title
            title_elem = listing.find(['h2', 'h3', 'h4', 'a'])
            if title_elem:
                info['title'] = title_elem.get_text(strip=True)
            
            # Extract basic description
            desc_elem = listing.find(['p', 'div'], class_=lambda x: x and 'desc' in str(x).lower())
            if desc_elem:
                info['description'] = desc_elem.get_text(strip=True)
            
            # Extract URL - this is most important for detailed scraping
            link_elem = listing.find('a', href=True)
            if link_elem:
                info['url'] = link_elem['href']
                if not info['url'].startswith('http'):
                    info['url'] = f"https://www.evergabe.de{info['url']}"
            
            # Only process if we have a URL to get details from
            if info['url']:
                print(f"  Found: {info['title'][:80] if info['title'] else 'Untitled'}...")
                print(f"    URL: {info['url']}")
                
                # Get detailed information from the order page
                detailed_info = self.get_order_details(info['url'])
                info.update(detailed_info)
                
                self.results.append(info)
            
        except Exception as e:
            print(f"Error extracting listing info: {e}")
            
    def get_order_details(self, url):
        """Open the order detail page and extract comprehensive information"""
        detailed_info = {}
        
        try:
            # Store current URL to return to it later
            current_url = self.driver.current_url
            
            # Open the detail page in a new tab
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Navigate to the detail page
            self.driver.get(url)
            time.sleep(2)  # Wait for page to load
            
            # Wait for the page to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except:
                print("    Detail page loading timeout")
            
            # Parse the detail page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract detailed information based on common patterns
            # Title (often in h1 or main heading)
            h1 = soup.find('h1')
            if h1 and not detailed_info.get('title'):
                detailed_info['title'] = h1.get_text(strip=True)
            
            # Look for labeled fields (common pattern: label/dt followed by value/dd)
            field_mappings = {
                'vergabestelle': 'contracting_authority',
                'auftraggeber': 'contracting_authority',
                'contracting authority': 'contracting_authority',
                'verfahrensart': 'procedure_type',
                'procedure': 'procedure_type',
                'cpv': 'cpv_codes',
                'cpv-code': 'cpv_codes',
                'einreichungsfrist': 'submission_deadline',
                'submission deadline': 'submission_deadline',
                'abgabefrist': 'submission_deadline',
                'öffnungstermin': 'opening_date',
                'opening date': 'opening_date',
                'laufzeit': 'contract_duration',
                'duration': 'contract_duration',
                'geschätzter wert': 'estimated_value',
                'estimated value': 'estimated_value',
                'kontakt': 'contact_info',
                'contact': 'contact_info',
                'ansprechpartner': 'contact_info',
                'ort': 'location',
                'location': 'location',
                'standort': 'location',
                'referenznummer': 'reference',
                'reference': 'reference',
                'vergabenummer': 'reference'
            }
            
            # Try dt/dd pattern
            for dt in soup.find_all('dt'):
                label = dt.get_text(strip=True).lower()
                dd = dt.find_next_sibling('dd')
                if dd:
                    value = dd.get_text(strip=True)
                    for key, field in field_mappings.items():
                        if key in label:
                            detailed_info[field] = value
                            break
            
            # Try label/value pattern in divs or spans
            for elem in soup.find_all(['div', 'span', 'p']):
                text = elem.get_text(strip=True).lower()
                for key, field in field_mappings.items():
                    if key in text and ':' in text:
                        parts = elem.get_text(strip=True).split(':', 1)
                        if len(parts) == 2:
                            detailed_info[field] = parts[1].strip()
            
            # Try table rows
            for tr in soup.find_all('tr'):
                cells = tr.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    for key, field in field_mappings.items():
                        if key in label:
                            detailed_info[field] = value
                            break
            
            # Extract detailed description (usually in main content area)
            description_selectors = [
                ('div', {'class': lambda x: x and 'description' in str(x).lower()}),
                ('div', {'class': lambda x: x and 'content' in str(x).lower()}),
                ('section', {'class': lambda x: x and 'detail' in str(x).lower()}),
                ('article', {}),
            ]
            
            for tag, attrs in description_selectors:
                desc = soup.find(tag, attrs)
                if desc:
                    # Get text but limit length
                    full_text = desc.get_text(separator=' ', strip=True)
                    detailed_info['detailed_description'] = full_text[:2000]  # Limit to 2000 chars
                    break
            
            # Look for document links
            doc_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                link_text = link.get_text(strip=True)
                # Check if it's likely a document
                if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip']):
                    if not href.startswith('http'):
                        href = f"https://www.evergabe.de{href}"
                    doc_links.append({
                        'name': link_text or 'Document',
                        'url': href
                    })
            
            if doc_links:
                detailed_info['documents'] = doc_links[:10]  # Limit to 10 documents
            
            print(f"    Extracted details: {len(detailed_info)} fields")
            
            # Close the detail tab and switch back
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
        except Exception as e:
            print(f"    Error getting order details: {e}")
            # Make sure we return to the original tab
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
        
        return detailed_info
    
    def go_to_next_page(self):
        """Try to navigate to the next page"""
        try:
            # Look for next page button/link - common patterns on evergabe.de
            next_selectors = [
                "//a[contains(@class, 'next')]",
                "//a[contains(text(), 'Weiter')]",
                "//a[contains(text(), 'Next')]",
                "//a[contains(text(), '→')]",
                "//a[contains(text(), '»')]",
                "//a[@rel='next']",
                "//li[contains(@class, 'next')]/a",
                "//span[contains(@class, 'next')]/a",
                "//a[contains(@class, 'pagination') and contains(text(), '>')]"
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.XPATH, selector)
                    if next_button.is_displayed() and next_button.is_enabled():
                        # Scroll to element
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                        time.sleep(1)
                        next_button.click()
                        time.sleep(2)  # Wait for page to load
                        return True
                except:
                    continue
                    
            print("No more pages available")
            return False
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            return False
            
    def filter_relevant_orders(self, keywords=None):
        """Filter results for relevant streetlamp orders"""
        if keywords is None:
            keywords = [
                'straßen', 'lampe', 'leuchte', 'led', 'beleuchtung',
                'licht', 'mast', 'außen', 'öffentlich', 'wartung',
                'instandhaltung', 'austausch', 'erneueur', 'modernisier'
            ]
        
        filtered = []
        for result in self.results:
            text = f"{result['title']} {result['description']}".lower()
            if any(keyword in text for keyword in keywords):
                filtered.append(result)
                
        return filtered
        
    def save_results(self, filename='evergabe_results.json'):
        """Save results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\nSaved {len(self.results)} results to {filename}")
        
    def save_to_excel(self, filename='evergabe_results.xlsx'):
        """Save results to Excel file with better formatting"""
        if self.results:
            # Prepare data for Excel
            df = pd.DataFrame(self.results)
            
            # Convert documents list to string for Excel
            if 'documents' in df.columns:
                df['documents'] = df['documents'].apply(
                    lambda x: '\n'.join([f"{d['name']}: {d['url']}" for d in x]) if isinstance(x, list) else ''
                )
            
            # Reorder columns for better readability
            column_order = [
                'title', 'url', 'search_term', 'location', 'contracting_authority',
                'submission_deadline', 'reference', 'procedure_type', 'estimated_value',
                'description', 'detailed_description', 'cpv_codes', 'opening_date',
                'contract_duration', 'contact_info', 'documents', 'scraped_at'
            ]
            
            # Only include columns that exist
            columns = [col for col in column_order if col in df.columns]
            df = df[columns]
            
            # Save to Excel with auto-adjusted column widths
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Results')
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Results']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).str.len().max(),
                        len(col)
                    )
                    # Limit column width to 50 characters
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[chr(65 + idx)].width = adjusted_width
            
            print(f"Saved {len(self.results)} results to {filename}")
        else:
            print("No results to save")
            
    def close(self):
        """Close the browser"""
        self.driver.quit()


def main():
    """Main function to run the scraper"""
    import sys
    
    print("Starting Evergabe.de scraper for streetlamp work orders")
    print("=" * 60)
    
    # Check for command line arguments
    use_profile = False
    profile_path = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--profile' and len(sys.argv) > 2:
            profile_path = sys.argv[2]
            use_profile = True
        elif not sys.argv[1].startswith('--'):
            profile_path = sys.argv[1]
            use_profile = True
    
    # Determine login method
    if use_profile and profile_path:
        print(f"Using Chrome profile: {profile_path}")
        print("Note: Make sure Chrome is closed or use a different profile")
        auto_login = False
    else:
        # Check if .env exists for auto-login
        if os.path.exists('.env'):
            print("Found .env file - will attempt automatic login")
            auto_login = True
        else:
            print("No .env file found")
            print("\nTo setup automatic login, run:")
            print("  python setup_evergabe.py")
            print("\nOr use a Chrome profile with saved login:")
            print("  python evergabe_scraper.py /path/to/chrome/profile")
            
            response = input("\nContinue without login? (y/n): ")
            if response.lower() != 'y':
                print("Exiting...")
                sys.exit(0)
            auto_login = False
    
    # Initialize scraper
    scraper = EvergabeScraper(
        headless=False, 
        profile_path=profile_path,
        auto_login=auto_login
    )
    
    try:
        # Search for streetlamp-related orders
        scraper.search_orders(max_pages=2)
        
        # Filter for most relevant results
        relevant = scraper.filter_relevant_orders()
        print(f"\nFound {len(relevant)} relevant streetlamp orders out of {len(scraper.results)} total")
        
        # Save results
        scraper.save_results('all_results.json')
        scraper.save_to_excel('all_results.xlsx')
        
        # Save filtered results
        if relevant:
            scraper.results = relevant
            scraper.save_results('streetlamp_orders.json')
            scraper.save_to_excel('streetlamp_orders.xlsx')
            
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY OF RELEVANT ORDERS:")
        print("=" * 60)
        for i, order in enumerate(relevant[:10], 1):
            print(f"\n{i}. {order['title']}")
            if order['location']:
                print(f"   Location: {order['location']}")
            if order['deadline']:
                print(f"   Deadline: {order['deadline']}")
            if order['url']:
                print(f"   URL: {order['url']}")
                
    except Exception as e:
        print(f"Error during scraping: {e}")
        
    finally:
        # Always close the browser
        scraper.close()
        

if __name__ == "__main__":
    main()