#!/usr/bin/env python3
"""
Interactive configuration editor for the Evergabe scraper
"""

import os
import sys
from utils.config_manager import ConfigManager

def main():
    """Main configuration editor"""
    
    print("="*60)
    print("EVERGABE SCRAPER CONFIGURATION EDITOR")
    print("="*60)
    
    # Load config
    config = ConfigManager()
    
    while True:
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)
        print("1. Search Settings")
        print("2. Browser Settings")
        print("3. Timing Settings")
        print("4. Output Settings")
        print("5. Advanced Settings")
        print("6. Show All Settings")
        print("7. Save and Exit")
        print("8. Exit without Saving")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == '1':
            edit_search_settings(config)
        elif choice == '2':
            edit_browser_settings(config)
        elif choice == '3':
            edit_timing_settings(config)
        elif choice == '4':
            edit_output_settings(config)
        elif choice == '5':
            edit_advanced_settings(config)
        elif choice == '6':
            show_all_settings(config)
        elif choice == '7':
            config.save()
            print("\n✓ Configuration saved!")
            break
        elif choice == '8':
            print("\n✗ Exiting without saving")
            break
        else:
            print("\n✗ Invalid option")

def edit_search_settings(config):
    """Edit search settings"""
    print("\n" + "="*60)
    print("SEARCH SETTINGS")
    print("="*60)
    
    # Edit search terms
    print("\nCurrent search terms:")
    terms = config.get_search_terms()
    for i, term in enumerate(terms, 1):
        print(f"  {i}. {term}")
    
    if input("\nEdit search terms? (y/n): ").lower() == 'y':
        print("Enter search terms (one per line, empty line to finish):")
        new_terms = []
        while True:
            term = input("> ").strip()
            if not term:
                break
            new_terms.append(term)
        if new_terms:
            config.set('search.terms', new_terms)
            print(f"✓ Updated {len(new_terms)} search terms")
    
    # Edit max pages
    current = config.get_max_pages()
    print(f"\nCurrent max pages per search: {current}")
    new_value = input("New value (or Enter to keep): ").strip()
    if new_value.isdigit():
        config.set('search.max_pages', int(new_value))
        print(f"✓ Updated max pages to {new_value}")
    
    # Edit max results per page
    current = config.get_max_results_per_page()
    print(f"\nCurrent max results per page: {current} (0 = all)")
    new_value = input("New value (or Enter to keep): ").strip()
    if new_value.isdigit():
        config.set('search.max_results_per_page', int(new_value))
        print(f"✓ Updated max results per page to {new_value}")
    
    # Edit filter keywords
    print("\nCurrent filter keywords:")
    keywords = config.get('search.filter_keywords', [])
    if keywords:
        for kw in keywords:
            print(f"  - {kw}")
    else:
        print("  (no filter)")
    
    if input("\nEdit filter keywords? (y/n): ").lower() == 'y':
        print("Enter keywords (one per line, empty line to finish):")
        new_keywords = []
        while True:
            kw = input("> ").strip().lower()
            if not kw:
                break
            new_keywords.append(kw)
        config.set('search.filter_keywords', new_keywords)
        print(f"✓ Updated {len(new_keywords)} filter keywords")

def edit_browser_settings(config):
    """Edit browser settings"""
    print("\n" + "="*60)
    print("BROWSER SETTINGS")
    print("="*60)
    
    # Headless mode
    current = config.is_headless()
    print(f"\nHeadless mode: {'Yes' if current else 'No'}")
    if input("Toggle headless mode? (y/n): ").lower() == 'y':
        config.set('browser.headless', not current)
        print(f"✓ Headless mode: {'enabled' if not current else 'disabled'}")
    
    # Window size
    width = config.get('browser.window_width', 1920)
    height = config.get('browser.window_height', 1080)
    print(f"\nWindow size: {width}x{height}")
    if input("Change window size? (y/n): ").lower() == 'y':
        new_width = input("Width (default 1920): ").strip()
        new_height = input("Height (default 1080): ").strip()
        if new_width.isdigit():
            config.set('browser.window_width', int(new_width))
        if new_height.isdigit():
            config.set('browser.window_height', int(new_height))
        print("✓ Window size updated")
    
    # Chrome profile
    use_profile = config.get('browser.use_profile', True)
    print(f"\nUse Chrome profile: {'Yes' if use_profile else 'No'}")
    if input("Toggle Chrome profile? (y/n): ").lower() == 'y':
        config.set('browser.use_profile', not use_profile)
        print(f"✓ Chrome profile: {'enabled' if not use_profile else 'disabled'}")

def edit_timing_settings(config):
    """Edit timing settings"""
    print("\n" + "="*60)
    print("TIMING SETTINGS (in seconds)")
    print("="*60)
    
    timing_fields = [
        ('page_load_timeout', 'Page load timeout'),
        ('element_wait_timeout', 'Element wait timeout'),
        ('smart_wait_min', 'Smart wait minimum'),
        ('smart_wait_max', 'Smart wait maximum'),
        ('wait_after_login', 'Wait after login'),
        ('wait_after_search', 'Wait after search'),
        ('wait_after_click', 'Wait after click'),
        ('wait_between_results', 'Wait between results'),
        ('wait_for_detail_page', 'Wait for detail page'),
        ('max_retries', 'Max retries'),
        ('retry_delay', 'Retry delay')
    ]
    
    for field, label in timing_fields:
        current = config.get_timing(field)
        print(f"\n{label}: {current}")
        new_value = input("New value (or Enter to keep): ").strip()
        if new_value:
            try:
                config.set(f'timing.{field}', float(new_value))
                print(f"✓ Updated {label} to {new_value}")
            except ValueError:
                print("✗ Invalid number")

def edit_output_settings(config):
    """Edit output settings"""
    print("\n" + "="*60)
    print("OUTPUT SETTINGS")
    print("="*60)
    
    # Output directory
    current = config.get_output_directory()
    print(f"\nOutput directory: {current}")
    new_value = input("New directory (or Enter to keep): ").strip()
    if new_value:
        config.set('output.directory', new_value)
        print(f"✓ Updated output directory to {new_value}")
    
    # Output formats
    formats = config.get_output_formats()
    print(f"\nOutput formats: {', '.join(formats)}")
    print("Available: json, excel, csv")
    if input("Change formats? (y/n): ").lower() == 'y':
        new_formats = input("Enter formats (comma-separated): ").strip().split(',')
        new_formats = [f.strip() for f in new_formats if f.strip() in ['json', 'excel', 'csv']]
        if new_formats:
            config.set('output.formats', new_formats)
            print(f"✓ Updated formats: {', '.join(new_formats)}")
    
    # Include timestamp
    current = config.get('output.include_timestamp', True)
    print(f"\nInclude timestamp in filename: {'Yes' if current else 'No'}")
    if input("Toggle timestamp? (y/n): ").lower() == 'y':
        config.set('output.include_timestamp', not current)
        print(f"✓ Timestamp: {'enabled' if not current else 'disabled'}")
    
    # Save debug HTML
    current = config.should_save_debug_html()
    print(f"\nSave debug HTML files: {'Yes' if current else 'No'}")
    if input("Toggle debug HTML? (y/n): ").lower() == 'y':
        config.set('output.save_debug_html', not current)
        print(f"✓ Debug HTML: {'enabled' if not current else 'disabled'}")

def edit_advanced_settings(config):
    """Edit advanced settings"""
    print("\n" + "="*60)
    print("ADVANCED SETTINGS")
    print("="*60)
    
    # Cookie handling
    print("\nCookie handling:")
    auto_handle = config.get('cookies.auto_handle', True)
    method = config.get('cookies.handling_method', 'reject')
    print(f"  Auto-handle: {'Yes' if auto_handle else 'No'}")
    print(f"  Method: {method}")
    
    if input("Change cookie settings? (y/n): ").lower() == 'y':
        if input("Auto-handle cookies? (y/n): ").lower() == 'y':
            config.set('cookies.auto_handle', True)
            method = input("Method (reject/accept/remove): ").strip().lower()
            if method in ['reject', 'accept', 'remove']:
                config.set('cookies.handling_method', method)
                print(f"✓ Cookie method: {method}")
        else:
            config.set('cookies.auto_handle', False)
            print("✓ Cookie auto-handling disabled")
    
    # Logging level
    current = config.get('logging.level', 'INFO')
    print(f"\nLogging level: {current}")
    print("Options: DEBUG, INFO, WARNING, ERROR")
    new_level = input("New level (or Enter to keep): ").strip().upper()
    if new_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
        config.set('logging.level', new_level)
        print(f"✓ Logging level: {new_level}")

def show_all_settings(config):
    """Show all settings"""
    import yaml
    print("\n" + "="*60)
    print("CURRENT CONFIGURATION")
    print("="*60)
    print(yaml.dump(config.config, default_flow_style=False, allow_unicode=True))
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()