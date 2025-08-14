#!/usr/bin/env python3
"""
Check the evergabe.de login page structure
"""

import requests
from bs4 import BeautifulSoup

def check_login_page():
    """Analyze the login page structure"""
    
    # Common login URLs for evergabe.de
    login_urls = [
        "https://www.evergabe.de/login",
        "https://www.evergabe.de/anmelden",
        "https://www.evergabe.de/users/sign_in",
        "https://www.evergabe.de/konto/anmelden"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    }
    
    for url in login_urls:
        print(f"\nTrying: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for login forms
                forms = soup.find_all('form')
                print(f"Found {len(forms)} forms")
                
                # Look for input fields
                inputs = soup.find_all('input')
                for inp in inputs:
                    inp_type = inp.get('type', '')
                    inp_name = inp.get('name', '')
                    inp_id = inp.get('id', '')
                    placeholder = inp.get('placeholder', '')
                    
                    if inp_type in ['email', 'text', 'password'] or 'user' in inp_name.lower() or 'pass' in inp_name.lower():
                        print(f"  Input: type={inp_type}, name={inp_name}, id={inp_id}, placeholder={placeholder}")
                
                return url
        except Exception as e:
            print(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    check_login_page()