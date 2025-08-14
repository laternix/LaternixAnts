#!/usr/bin/env python3
"""
Login manager for evergabe.de
"""

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException

class LoginManager:
    def __init__(self, driver, config=None):
        self.driver = driver
        self.credentials = self.load_credentials()
        # Import dependencies
        from .cookie_handler import CookieHandler
        from .wait_helper import WaitHelper
        from .config_manager import ConfigManager
        
        self.config = config or ConfigManager()
        self.cookie_handler = CookieHandler(driver)
        self.wait_helper = WaitHelper(
            driver, 
            default_timeout=self.config.get_timing('element_wait_timeout')
        )
        
    def load_credentials(self):
        """Load credentials from .env file"""
        username = None
        password = None
        
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('EVERGABE_USERNAME='):
                        username = line.split('=', 1)[1].strip()
                    elif line.startswith('EVERGABE_PASSWORD='):
                        password = line.split('=', 1)[1].strip()
        
        return username, password
    
    def login(self):
        """Perform login to evergabe.de"""
        username, password = self.credentials
        
        if not username or not password:
            print("✗ No credentials found in .env file")
            print("  Run: python setup.py")
            return False
        
        try:
            # Preemptively block cookie scripts
            print("  → Setting up cookie blocking...")
            self.cookie_handler.preemptive_block()
            
            # Navigate to login page directly
            print("  → Navigating to login page...")
            self.driver.get("https://www.evergabe.de/anmelden")
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Quick removal of any popups that might have appeared
            self.cookie_handler.quick_remove_usercentrics()
            
            # Check if we're redirected to OAuth login page
            current_url = self.driver.current_url
            if 'login.evergabe.de' in current_url:
                print("  → Redirected to OAuth login page")
            elif 'anmelden' not in current_url.lower():
                print("  ✓ Already logged in")
                return True
            
            print("  → Looking for login form...")
            
            # Debug: print what we see on the page
            page_source = self.driver.page_source
            if 'username' in page_source.lower():
                print("  ✓ Found username field in page")
            if 'password' in page_source.lower():
                print("  ✓ Found password field in page")
            
            # Wait for username field to be visible and interactable
            print("  → Waiting for username field...")
            try:
                # First, ensure any cookie overlays are gone
                time.sleep(2)
                self.cookie_handler.handle_cookies()
                
                # Try to find and click username field with retry logic
                max_retries = 5
                username_field = None
                
                for attempt in range(max_retries):
                    try:
                        # Quick removal before trying to interact
                        self.cookie_handler.quick_remove_usercentrics()
                        
                        # Find username field
                        username_field = self.driver.find_element(By.ID, "username")
                        
                        # Use JavaScript to directly focus and prepare the field
                        self.driver.execute_script("""
                            var field = document.getElementById('username');
                            if (field) {
                                field.focus();
                                field.click();
                            }
                        """)
                        print("  ✓ Username field found and focused")
                        break
                            
                    except NoSuchElementException:
                        print(f"  → Username field not found (attempt {attempt + 1}/{max_retries})")
                        self.wait_helper.smart_wait(max_wait=0.5)
                    except Exception as e:
                        print(f"  → Error on attempt {attempt + 1}: {e}")
                        if attempt == max_retries - 1:
                            raise
                        self.wait_helper.smart_wait(max_wait=0.5)
                
                if not username_field:
                    raise Exception("Could not find username field after retries")
                    
            except Exception as e:
                print(f"  → Error with username field: {e}")
                # Try alternative selectors
                print("  → Trying alternative username selectors...")
                username_field = None
                selectors = [
                    "//input[@name='username']",
                    "//input[@id='username']",
                    "//input[@type='text'][1]",
                    "//input[contains(@placeholder, 'Benutzer')]"
                ]
                for selector in selectors:
                    try:
                        username_field = self.driver.find_element(By.XPATH, selector)
                        if username_field.is_displayed():
                            print(f"  ✓ Found username field with: {selector}")
                            break
                    except:
                        continue
                
                if not username_field:
                    print("  ✗ Could not find username field")
                    # Save screenshot for debugging
                    self.driver.save_screenshot("login_error.png")
                    print("  → Screenshot saved to login_error.png")
                    return False
            
            # Clear and enter username (field already clicked/focused above)
            time.sleep(0.5)
            try:
                username_field.clear()
                username_field.send_keys(username)
                print(f"  ✓ Entered username: {username[:3]}...")
            except Exception as e:
                print(f"  → Regular input failed, using JavaScript...")
                self.driver.execute_script(f"""
                    var field = document.getElementById('username');
                    if (field) {{
                        field.value = '{username}';
                        field.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        field.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """)
                print(f"  ✓ Entered username with JavaScript: {username[:3]}...")
            
            # Find password field
            print("  → Looking for password field...")
            try:
                password_field = self.driver.find_element(By.ID, "password")
                print("  ✓ Password field found")
            except:
                try:
                    password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
                    print("  ✓ Password field found with XPath")
                except:
                    print("  ✗ Could not find password field")
                    return False
            
            # Enter password
            time.sleep(0.5)
            try:
                password_field.click()
                password_field.clear()
                password_field.send_keys(password)
                print("  ✓ Entered password")
            except Exception as e:
                print(f"  → Regular password input failed, using JavaScript...")
                self.driver.execute_script(f"""
                    var field = document.getElementById('password');
                    if (!field) {{
                        field = document.querySelector('input[type="password"]');
                    }}
                    if (field) {{
                        field.value = '{password}';
                        field.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        field.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                """)
                print("  ✓ Entered password with JavaScript")
            
            # Find and click submit button
            print("  → Looking for submit button...")
            
            # Try to find the submit button
            submit_button = None
            submit_selectors = [
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(text(), 'Anmelden')]",
                "//input[@value='Anmelden']",
                "//button[contains(@class, 'btn')]",
                "//input[contains(@class, 'btn')]"
            ]
            
            for selector in submit_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            submit_button = elem
                            print(f"  ✓ Found submit button with: {selector}")
                            break
                    if submit_button:
                        break
                except:
                    continue
            
            if submit_button:
                print("  → Clicking submit button...")
                submit_button.click()
            else:
                print("  → No submit button found, trying form submit...")
                password_field.submit()
            
            # Wait for login to process
            print("  → Waiting for login to complete...")
            # Wait for URL change or specific element
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: 'anmelden' not in driver.current_url.lower() or 'login' not in driver.current_url.lower()
                )
            except:
                pass
            
            # Check if we're on the handover/redirect page
            current_url = self.driver.current_url
            print(f"  Current URL: {current_url}")
            
            if 'uebernehmen' in current_url or 'sso' in current_url:
                print("  → OAuth handover detected, waiting...")
                # Wait for redirect to complete
                try:
                    WebDriverWait(self.driver, 5).until(
                        lambda driver: 'uebernehmen' not in driver.current_url and 'sso' not in driver.current_url
                    )
                except:
                    time.sleep(1)
            
            # Quick removal of any popups after login
            self.cookie_handler.quick_remove_usercentrics()
            
            # Check for "already logged in" warning and handle it
            self.handle_already_logged_in_warning()
            
            # Verify login by checking URL and trying to access protected page
            print("  → Verifying login...")
            
            # Try to access search page
            self.driver.get("https://www.evergabe.de/auftraege/auftrag-suchen")
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Check if we can access search (not redirected to login)
            final_url = self.driver.current_url
            if 'anmelden' not in final_url.lower() and 'login' not in final_url.lower():
                print("  ✓ Login successful!")
                return True
            else:
                print("  ✗ Login failed - redirected to login page")
                print(f"  Final URL: {final_url}")
                # Check for error messages
                page_source = self.driver.page_source.lower()
                if 'fehler' in page_source or 'ungültig' in page_source:
                    print("  ✗ Invalid credentials - please check username/password")
                return False
                
        except Exception as e:
            print(f"  ✗ Login error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def handle_already_logged_in_warning(self):
        """Handle the 'already logged in' warning"""
        try:
            # Check if there's a warning about being already logged in
            page_source = self.driver.page_source
            
            if 'Achtung!' in page_source and 'bereits' in page_source and 'angemeldet' in page_source:
                print("  → Found 'already logged in' warning")
                
                # Look for the "Ja, hier neu anmelden" button
                button_selectors = [
                    "//button[contains(text(), 'Ja, hier neu anmelden')]",
                    "//a[contains(text(), 'Ja, hier neu anmelden')]",
                    "//input[contains(@value, 'Ja, hier neu anmelden')]",
                    "//button[contains(text(), 'neu anmelden')]",
                    "//a[contains(text(), 'neu anmelden')]"
                ]
                
                for selector in button_selectors:
                    try:
                        btn = self.driver.find_element(By.XPATH, selector)
                        if btn.is_displayed():
                            print("  → Clicking 'Ja, hier neu anmelden' button...")
                            btn.click()
                            time.sleep(3)
                            print("  ✓ Handled already logged in warning")
                            return True
                    except:
                        continue
                
                print("  ⚠ Could not find 'neu anmelden' button")
        except Exception as e:
            # No warning present, that's fine
            pass
        return False