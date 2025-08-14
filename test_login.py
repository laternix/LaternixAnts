#!/usr/bin/env python3
"""
Test login functionality only
"""

import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

def test_login():
    """Test login directly"""
    
    print("="*60)
    print("TESTING LOGIN DIRECTLY")
    print("="*60)
    
    # Load credentials
    username = None
    password = None
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('EVERGABE_USERNAME='):
                    username = line.split('=', 1)[1].strip()
                elif line.startswith('EVERGABE_PASSWORD='):
                    password = line.split('=', 1)[1].strip()
    
    if not username or not password:
        print("✗ No credentials found in .env")
        print("Run: python setup.py")
        return
    
    print(f"Username: {username[:3]}...")
    print(f"Password: {'*' * len(password)}")
    
    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Go to login page
        print("\n→ Going to login page...")
        driver.get("https://www.evergabe.de/anmelden")
        time.sleep(3)
        
        print("→ Current URL:", driver.current_url)
        
        # Take screenshot
        driver.save_screenshot("login_page.png")
        print("→ Screenshot saved: login_page.png")
        
        # Look for form fields
        print("\n→ Looking for form fields...")
        
        # Find all input fields on page
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"→ Found {len(all_inputs)} input fields")
        
        for inp in all_inputs:
            input_type = inp.get_attribute("type")
            input_name = inp.get_attribute("name")
            input_id = inp.get_attribute("id")
            if input_type in ["text", "email", "password"]:
                print(f"  - Input: type={input_type}, name={input_name}, id={input_id}")
        
        # Try to find and fill username
        print("\n→ Filling username...")
        username_field = None
        
        # Try by ID first
        try:
            username_field = driver.find_element(By.ID, "username")
            print("  ✓ Found by ID: username")
        except:
            # Try by name
            try:
                username_field = driver.find_element(By.NAME, "username")
                print("  ✓ Found by NAME: username")
            except:
                # Try first text input
                try:
                    username_field = driver.find_element(By.XPATH, "//input[@type='text'][1]")
                    print("  ✓ Found by XPATH: first text input")
                except:
                    print("  ✗ Could not find username field!")
        
        if username_field:
            username_field.click()
            username_field.clear()
            username_field.send_keys(username)
            print(f"  ✓ Entered username: {username[:3]}...")
        
        # Try to find and fill password
        print("\n→ Filling password...")
        password_field = None
        
        try:
            password_field = driver.find_element(By.ID, "password")
            print("  ✓ Found by ID: password")
        except:
            try:
                password_field = driver.find_element(By.XPATH, "//input[@type='password']")
                print("  ✓ Found by XPATH: password input")
            except:
                print("  ✗ Could not find password field!")
        
        if password_field:
            password_field.click()
            password_field.clear()
            password_field.send_keys(password)
            print("  ✓ Entered password")
        
        # Take screenshot before submit
        driver.save_screenshot("login_filled.png")
        print("\n→ Screenshot saved: login_filled.png")
        
        # Find submit button
        print("\n→ Looking for submit button...")
        submit_button = None
        
        # Try different selectors
        selectors = [
            ("XPATH", "//button[@type='submit']", "button[type=submit]"),
            ("XPATH", "//input[@type='submit']", "input[type=submit]"),
            ("XPATH", "//button[contains(text(), 'Anmelden')]", "button with 'Anmelden'"),
            ("XPATH", "//input[@value='Anmelden']", "input with value 'Anmelden'"),
            ("XPATH", "//button", "any button"),
        ]
        
        for method, selector, description in selectors:
            try:
                if method == "XPATH":
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            text = elem.text or elem.get_attribute("value") or ""
                            print(f"  → Found {description}: '{text}'")
                            if "anmeld" in text.lower() or elem.get_attribute("type") == "submit":
                                submit_button = elem
                                print(f"  ✓ Using this button for submit")
                                break
                if submit_button:
                    break
            except:
                continue
        
        if submit_button:
            print("\n→ Clicking submit button...")
            submit_button.click()
        else:
            print("\n→ No submit button found, pressing Enter...")
            if password_field:
                password_field.send_keys(Keys.RETURN)
        
        # Wait for result
        print("\n→ Waiting for login to complete...")
        time.sleep(5)
        
        # Check result
        print("\n→ Checking login result...")
        print(f"  Current URL: {driver.current_url}")
        
        # Take screenshot of result
        driver.save_screenshot("login_result.png")
        print("  Screenshot saved: login_result.png")
        
        # Try to access search page
        print("\n→ Trying to access search page...")
        driver.get("https://www.evergabe.de/auftraege/auftrag-suchen")
        time.sleep(3)
        
        final_url = driver.current_url
        print(f"  Final URL: {final_url}")
        
        if 'anmelden' not in final_url.lower() and 'login' not in final_url.lower():
            print("\n✓ LOGIN SUCCESSFUL!")
        else:
            print("\n✗ LOGIN FAILED - Still on login page")
            print("  Check the screenshots to see what happened")
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_login()