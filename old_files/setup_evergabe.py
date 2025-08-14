#!/usr/bin/env python3
"""
Setup script for evergabe.de scraper
Handles login and creates .env file with credentials
"""

import os
import sys
import getpass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def create_env_file():
    """Create or update .env file with login credentials"""
    
    print("=" * 60)
    print("EVERGABE.DE LOGIN SETUP")
    print("=" * 60)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("\n.env file already exists.")
        overwrite = input("Do you want to update the credentials? (y/n): ").lower()
        if overwrite != 'y':
            return load_env_credentials()
    
    print("\nPlease enter your evergabe.de login credentials:")
    username = input("Username/Email: ")
    password = getpass.getpass("Password: ")
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(f"EVERGABE_USERNAME={username}\n")
        f.write(f"EVERGABE_PASSWORD={password}\n")
    
    print("\n✓ Credentials saved to .env file")
    print("  Note: .env is already in .gitignore for security")
    
    return username, password

def load_env_credentials():
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

def handle_cookie_popup(driver):
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
            "//button[contains(@id, 'accept')]"
        ]
        
        for selector in cookie_selectors:
            try:
                cookie_button = driver.find_element(By.XPATH, selector)
                if cookie_button.is_displayed():
                    cookie_button.click()
                    print("  Handled cookie popup")
                    time.sleep(1)
                    return True
            except:
                continue
    except:
        pass
    return False

def test_login(username, password, headless=False):
    """Test login with provided credentials"""
    
    print("\n" + "=" * 60)
    print("TESTING LOGIN")
    print("=" * 60)
    
    # Setup Chrome
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # First navigate to main page to handle cookies
        print("Navigating to evergabe.de...")
        driver.get("https://www.evergabe.de")
        time.sleep(2)
        
        # Handle cookie popup if present
        handle_cookie_popup(driver)
        
        # Navigate to login page
        login_url = "https://www.evergabe.de/anmelden"
        print(f"Navigating to login page...")
        driver.get(login_url)
        time.sleep(2)
        
        # Handle cookie popup again if it appears
        handle_cookie_popup(driver)
        
        # Find and fill username field
        print("Entering username...")
        try:
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
        except:
            username_field = driver.find_element(By.XPATH, "//input[@name='username' or @type='email']")
            
        username_field.clear()
        username_field.send_keys(username)
        
        # Find and fill password field
        print("Entering password...")
        try:
            password_field = driver.find_element(By.ID, "password")
        except:
            password_field = driver.find_element(By.XPATH, "//input[@type='password']")
            
        password_field.clear()
        password_field.send_keys(password)
        
        # Find and click login button
        print("Clicking login button...")
        login_clicked = False
        login_selectors = [
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(text(), 'Anmelden')]",
            "//input[@value='Anmelden']"
        ]
        
        for selector in login_selectors:
            try:
                login_button = driver.find_element(By.XPATH, selector)
                if login_button.is_displayed():
                    login_button.click()
                    login_clicked = True
                    break
            except:
                continue
        
        if not login_clicked:
            password_field.submit()
        
        # Wait for redirect/login to complete
        time.sleep(4)
        
        # Handle any cookie popup after login
        handle_cookie_popup(driver)
        
        # Check if login was successful by accessing search page
        driver.get("https://www.evergabe.de/auftraege/auftrag-suchen")
        time.sleep(2)
        
        current_url = driver.current_url.lower()
        if 'anmelden' not in current_url and 'login' not in current_url:
            print("\n✓ Login successful!")
            print("✓ Can access search page")
            return True
        else:
            print("\n✗ Login failed - redirected to login page")
            page_source = driver.page_source.lower()
            if 'fehler' in page_source or 'error' in page_source or 'ungültig' in page_source:
                print("  Error message detected - check credentials")
            return False
            
    except Exception as e:
        print(f"\n✗ Error during login test: {e}")
        return False
        
    finally:
        driver.quit()

def create_gitignore():
    """Ensure .env is in .gitignore"""
    gitignore_exists = os.path.exists('.gitignore')
    env_in_gitignore = False
    
    if gitignore_exists:
        with open('.gitignore', 'r') as f:
            content = f.read()
            if '.env' in content:
                env_in_gitignore = True
    
    if not env_in_gitignore:
        with open('.gitignore', 'a') as f:
            if gitignore_exists:
                f.write('\n')
            f.write('# Environment variables\n')
            f.write('.env\n')
        print("✓ Added .env to .gitignore")

def main():
    """Main setup function"""
    
    print("EVERGABE.DE SCRAPER SETUP")
    print("=" * 60)
    
    # Ensure .env is in .gitignore
    create_gitignore()
    
    # Get or create credentials
    username, password = create_env_file()
    
    if username and password:
        # Test the login
        print("\nWould you like to test the login now? (recommended)")
        test = input("Test login? (y/n): ").lower()
        
        if test == 'y':
            success = test_login(username, password, headless=False)
            
            if success:
                print("\n" + "=" * 60)
                print("SETUP COMPLETE!")
                print("=" * 60)
                print("\nYou can now run the scraper with automatic login:")
                print("  python evergabe_scraper.py")
                print("\nYour credentials are saved in .env (git-ignored)")
            else:
                print("\n" + "=" * 60)
                print("LOGIN TEST FAILED")
                print("=" * 60)
                print("\nPlease check your credentials and run setup again:")
                print("  python setup_evergabe.py")
    else:
        print("\n✗ No credentials provided")
        sys.exit(1)

if __name__ == "__main__":
    main()