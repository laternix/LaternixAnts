#!/usr/bin/env python3
"""
Main script to run the evergabe.de scraper
"""

import os
import sys
import argparse
from src.evergabe_scraper import EvergabeScraper

def main():
    """Main function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Evergabe.de Scraper')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--test', action='store_true', help='Run in test mode (limited search)')
    parser.add_argument('--terms', nargs='+', help='Search terms to use (overrides config)')
    parser.add_argument('--max-pages', type=int, help='Max pages per search term (overrides config)')
    parser.add_argument('--show-config', action='store_true', help='Show current configuration and exit')
    parser.add_argument('--create-config', action='store_true', help='Create default config file and exit')
    
    args = parser.parse_args()
    
    print("="*60)
    print("EVERGABE.DE STREETLAMP ORDER SCRAPER")
    print("="*60)
    
    # Handle config operations
    if args.show_config or args.create_config:
        from utils.config_manager import ConfigManager
        config = ConfigManager(args.config)
        
        if args.show_config:
            import yaml
            print("\nCurrent Configuration:")
            print("="*60)
            print(yaml.dump(config.config, default_flow_style=False, allow_unicode=True))
        
        if args.create_config:
            config.save('config.yaml')
            print("\n✓ Configuration file created: config.yaml")
        return
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n✗ No credentials found!")
        print("Please run setup first:")
        print("  python setup.py")
        sys.exit(1)
    
    # Initialize scraper with config
    print(f"\n→ Running with {'headless' if args.headless else 'visible'} browser")
    scraper = EvergabeScraper(headless=args.headless, config_path=args.config)
    
    try:
        # Override config with command line arguments if provided
        search_terms = args.terms if args.terms else None
        max_pages = args.max_pages
        
        # In test mode, limit to 1 page
        if args.test:
            print(f"\n→ Test mode: limited search")
            max_pages = 1
            if not search_terms:
                # Use first term from config for test
                search_terms = [scraper.config.get_search_terms()[0]]
        else:
            print(f"\n→ Full search mode")
        
        # Run search
        scraper.search_orders(search_terms=search_terms, max_pages=max_pages)
        
        # Show results summary
        print(f"\n{'='*60}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Total orders found: {len(scraper.results)}")
        
        # Filter relevant
        relevant = scraper.filter_relevant()
        print(f"Relevant to streetlamps: {len(relevant)}")
        
        # Save results
        if scraper.results:
            scraper.save_results()
        
        # Show sample results
        if scraper.results:
            print(f"\n{'='*60}")
            print("SAMPLE RESULTS (First 3):")
            print(f"{'='*60}")
            
            for i, result in enumerate(scraper.results[:3], 1):
                print(f"\n{i}. {result.get('title', 'No title')}")
                print(f"   URL: {result.get('url', 'No URL')}")
                print(f"   Authority: {result.get('contracting_authority', 'Unknown')[:60]}")
                print(f"   Reference: {result.get('reference', 'Unknown')}")
                print(f"   Vergabe-ID: {result.get('vergabe_id', 'Unknown')}")
                print(f"   Location: {result.get('location', 'Unknown')}")
                print(f"   Deadline: {result.get('deadline', 'Unknown')}")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        if '--debug' in sys.argv:
            traceback.print_exc()
    finally:
        scraper.close()
        
    print(f"\n{'='*60}")
    print("SCRAPER FINISHED")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()