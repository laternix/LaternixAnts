#!/usr/bin/env python3
"""
Setup script to configure evergabe.de login credentials
"""

import os
import getpass

def setup_credentials():
    """Setup login credentials for evergabe.de"""
    
    print("="*60)
    print("EVERGABE.DE SCRAPER SETUP")
    print("="*60)
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("\n.env file already exists.")
        response = input("Update credentials? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("\nEnter your evergabe.de login credentials:")
    username = input("Username/Email: ")
    password = getpass.getpass("Password: ")
    
    # Save to .env
    with open('.env', 'w') as f:
        f.write(f"EVERGABE_USERNAME={username}\n")
        f.write(f"EVERGABE_PASSWORD={password}\n")
    
    print("\n✓ Credentials saved to .env")
    print("✓ Ready to run the scraper!")
    print("\nUsage:")
    print("  python run.py")

if __name__ == "__main__":
    setup_credentials()