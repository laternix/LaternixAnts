#!/usr/bin/env python3
"""
Helper script to find Chrome profiles on your system
"""

import os
import json
from pathlib import Path

def find_chrome_profiles():
    """Find all Chrome profiles on the system"""
    
    print("Searching for Chrome profiles...")
    print("=" * 60)
    
    # Common Chrome profile locations
    chrome_paths = [
        os.path.expanduser("~/.config/google-chrome"),  # Linux Chrome
        os.path.expanduser("~/.config/chromium"),       # Linux Chromium
        os.path.expanduser("~/snap/chromium/common/chromium"),  # Snap Chromium
    ]
    
    profiles_found = []
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            print(f"\nFound Chrome data directory: {chrome_path}")
            
            # Look for profile directories
            for item in os.listdir(chrome_path):
                item_path = os.path.join(chrome_path, item)
                
                # Check if it's a profile directory (contains Preferences file)
                pref_file = os.path.join(item_path, "Preferences")
                if os.path.isfile(pref_file):
                    profile_info = {
                        'path': item_path,
                        'name': item,
                        'full_path': chrome_path
                    }
                    
                    # Try to get profile name from Preferences
                    try:
                        with open(pref_file, 'r', encoding='utf-8') as f:
                            prefs = json.load(f)
                            if 'profile' in prefs:
                                if 'name' in prefs['profile']:
                                    profile_info['display_name'] = prefs['profile']['name']
                    except:
                        pass
                    
                    profiles_found.append(profile_info)
                    print(f"  Profile: {item}")
                    print(f"    Path: {item_path}")
                    if 'display_name' in profile_info:
                        print(f"    Name: {profile_info['display_name']}")
    
    if not profiles_found:
        print("\nNo Chrome profiles found.")
        print("Make sure Chrome is installed and you have created at least one profile.")
    else:
        print("\n" + "=" * 60)
        print("HOW TO USE WITH THE SCRAPER:")
        print("=" * 60)
        print("\n1. First, log into evergabe.de using Chrome normally")
        print("2. Close Chrome completely")
        print("3. Run the scraper with your profile:")
        print(f"\n   python evergabe_scraper.py '{profiles_found[0]['path']}'")
        print("\nOr set environment variable:")
        print(f"   export CHROME_PROFILE_PATH='{profiles_found[0]['path']}'")
        print("   python evergabe_scraper.py")
        
        if len(profiles_found) > 1:
            print("\nOther profiles found:")
            for profile in profiles_found[1:]:
                print(f"   {profile['path']}")

if __name__ == "__main__":
    find_chrome_profiles()