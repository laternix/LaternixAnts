#!/usr/bin/env python3
"""
Smart waiting utilities for faster page interactions
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

class WaitHelper:
    def __init__(self, driver, default_timeout=10):
        self.driver = driver
        self.default_timeout = default_timeout
    
    def wait_for_page_load(self, timeout=None):
        """Wait for page to be fully loaded"""
        timeout = timeout or self.default_timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            # Also wait for jQuery if present
            self.driver.execute_script("""
                if (typeof jQuery !== 'undefined') {
                    return jQuery.active == 0;
                }
                return true;
            """)
            return True
        except:
            return False
    
    def wait_for_element(self, locator, timeout=None):
        """Wait for element to be present"""
        timeout = timeout or self.default_timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except:
            return None
    
    def wait_for_clickable(self, locator, timeout=None):
        """Wait for element to be clickable"""
        timeout = timeout or self.default_timeout
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except:
            return None
    
    def wait_for_url_change(self, current_url, timeout=None):
        """Wait for URL to change from current"""
        timeout = timeout or self.default_timeout
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.current_url != current_url
            )
            return True
        except:
            return False
    
    def wait_for_ajax(self, timeout=None):
        """Wait for AJAX requests to complete"""
        timeout = timeout or 5
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("""
                    if (typeof jQuery !== 'undefined') {
                        return jQuery.active == 0;
                    }
                    if (typeof fetch !== 'undefined' && window.fetch.active) {
                        return window.fetch.active == 0;
                    }
                    return true;
                """)
            )
            return True
        except:
            return False
    
    def smart_wait(self, max_wait=2):
        """Smart wait that checks for page readiness"""
        start_time = time.time()
        
        # First, check if page is still loading
        while time.time() - start_time < max_wait:
            ready_state = self.driver.execute_script("return document.readyState")
            if ready_state == "complete":
                # Check for active AJAX calls
                ajax_complete = self.driver.execute_script("""
                    if (typeof jQuery !== 'undefined') {
                        return jQuery.active == 0;
                    }
                    return true;
                """)
                if ajax_complete:
                    # Give UI a moment to update
                    time.sleep(0.1)
                    return True
            time.sleep(0.1)
        
        return False
    
    def wait_for_search_results(self, timeout=None):
        """Wait specifically for search results to load"""
        timeout = timeout or self.default_timeout
        try:
            # Try multiple possible selectors for results
            selectors = [
                (By.CLASS_NAME, "result-list-item"),
                (By.CLASS_NAME, "search-result"),
                (By.CSS_SELECTOR, "li.result-list-item"),
                (By.CSS_SELECTOR, "[data-href]")
            ]
            
            for selector in selectors:
                try:
                    element = WebDriverWait(self.driver, timeout/len(selectors)).until(
                        EC.presence_of_element_located(selector)
                    )
                    if element:
                        return True
                except:
                    continue
            
            return False
        except:
            return False