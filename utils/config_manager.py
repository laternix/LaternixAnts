#!/usr/bin/env python3
"""
Configuration manager for the Evergabe scraper
"""

import os
import yaml
import json
from typing import Dict, Any, List, Optional

class ConfigManager:
    """Manages configuration for the scraper"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file (YAML or JSON)
        """
        self.config_path = config_path or self._find_config_file()
        self.config = self._load_config()
        self._validate_config()
    
    def _find_config_file(self) -> str:
        """Find configuration file in common locations"""
        possible_paths = [
            'config.yaml',
            'config.yml',
            'config.json',
            'config/config.yaml',
            'config/config.yml',
            'config/config.json',
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yml'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✓ Found config file: {path}")
                return path
        
        # If no config file found, create default
        default_path = 'config.yaml'
        print(f"⚠ No config file found, creating default at {default_path}")
        self._create_default_config(default_path)
        return default_path
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not os.path.exists(self.config_path):
            return self._get_default_config()
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.endswith('.json'):
                return json.load(f)
            else:
                return yaml.safe_load(f)
    
    def _validate_config(self):
        """Validate configuration values"""
        # Ensure required sections exist
        required_sections = ['search', 'browser', 'timing', 'output']
        for section in required_sections:
            if section not in self.config:
                self.config[section] = {}
        
        # Set defaults for missing values
        defaults = self._get_default_config()
        for section, values in defaults.items():
            if section not in self.config:
                self.config[section] = values
            elif isinstance(values, dict):
                for key, value in values.items():
                    if key not in self.config[section]:
                        self.config[section][key] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'search': {
                'terms': ['Straßenbeleuchtung', 'LED', 'Beleuchtung'],
                'max_pages': 3,
                'max_results_per_page': 0,
                'filter_keywords': []
            },
            'browser': {
                'headless': False,
                'window_width': 1920,
                'window_height': 1080,
                'use_profile': True,
                'profile_directory': ''
            },
            'timing': {
                'page_load_timeout': 10,
                'element_wait_timeout': 10,
                'smart_wait_min': 0.1,
                'smart_wait_max': 2.0,
                'wait_after_login': 1.0,
                'wait_after_search': 0.5,
                'wait_after_click': 0.5,
                'wait_between_results': 0.2,
                'wait_for_detail_page': 0.5,
                'max_retries': 3,
                'retry_delay': 1.0
            },
            'login': {
                'login_url': 'https://www.evergabe.de/anmelden',
                'search_url': 'https://www.evergabe.de/auftraege/auftrag-suchen',
                'max_attempts': 3
            },
            'output': {
                'directory': 'output',
                'formats': ['json', 'excel'],
                'include_timestamp': True,
                'save_debug_html': False,
                'extract_fields': [
                    'title', 'description', 'contracting_authority', 'location',
                    'deadline', 'cpv_codes', 'reference', 'vergabe_id',
                    'procedure_type', 'period_of_performance', 'documents'
                ]
            },
            'cookies': {
                'auto_handle': True,
                'remove_usercentrics': True,
                'handling_method': 'reject'
            },
            'logging': {
                'level': 'INFO',
                'log_to_file': True,
                'log_file': 'logs/scraper.log',
                'show_progress': True
            },
            'performance': {
                'parallel_details': False,
                'max_workers': 3,
                'use_cache': True,
                'cache_expiry': 24
            },
            'advanced': {
                'user_agent': '',
                'chrome_options': [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled'
                ],
                'wire_options': {},
                'headers': {}
            },
            'notifications': {
                'enabled': False,
                'email': {
                    'enabled': False
                },
                'webhook': {
                    'enabled': False
                }
            },
            'proxy': {
                'enabled': False
            }
        }
    
    def _create_default_config(self, path: str):
        """Create default configuration file"""
        config = self._get_default_config()
        
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'search.max_pages')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'search.max_pages')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: str = None):
        """Save configuration to file"""
        path = path or self.config_path
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.endswith('.json'):
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"✓ Configuration saved to {path}")
    
    def get_search_terms(self) -> List[str]:
        """Get list of search terms"""
        return self.get('search.terms', ['Beleuchtung'])
    
    def get_max_pages(self) -> int:
        """Get maximum pages to scrape"""
        return self.get('search.max_pages', 3)
    
    def get_max_results_per_page(self) -> int:
        """Get maximum results per page (0 = all)"""
        return self.get('search.max_results_per_page', 0)
    
    def is_headless(self) -> bool:
        """Check if browser should run headless"""
        return self.get('browser.headless', False)
    
    def get_timing(self, key: str) -> float:
        """Get timing configuration value"""
        return float(self.get(f'timing.{key}', 1.0))
    
    def get_output_formats(self) -> List[str]:
        """Get output formats"""
        return self.get('output.formats', ['json', 'excel'])
    
    def get_output_directory(self) -> str:
        """Get output directory"""
        return self.get('output.directory', 'output')
    
    def should_save_debug_html(self) -> bool:
        """Check if debug HTML should be saved"""
        return self.get('output.save_debug_html', False)
    
    def get_chrome_options(self) -> List[str]:
        """Get Chrome options"""
        return self.get('advanced.chrome_options', [])