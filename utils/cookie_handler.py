#!/usr/bin/env python3
"""
Cookie popup handler for evergabe.de
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class CookieHandler:
    def __init__(self, driver):
        self.driver = driver
        self.blocked_usercentrics = False
        
    def preemptive_block(self):
        """Preemptively block usercentrics and other cookie scripts from loading"""
        try:
            # Inject script to block usercentrics before it loads
            self.driver.execute_script("""
                // Block usercentrics from loading
                Object.defineProperty(window, 'UC_UI', {
                    value: undefined,
                    writable: false
                });
                
                // Override common consent management functions
                window.UC_SETTINGS = {};
                window.UC_PRIVACY = {};
                
                // Create a MutationObserver to remove usercentrics elements as they appear
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        mutation.addedNodes.forEach((node) => {
                            if (node.id && node.id.includes('usercentrics')) {
                                node.remove();
                                console.log('Removed usercentrics element:', node.id);
                            }
                        });
                    });
                });
                
                // Start observing
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
                
                // Store observer so it persists
                window.ucObserver = observer;
            """)
            self.blocked_usercentrics = True
            return True
        except:
            return False
        
    def handle_cookies(self):
        """Handle cookie consent popups including usercentrics"""
        # First try preemptive blocking if not done yet
        if not self.blocked_usercentrics:
            self.preemptive_block()
        
        # Quick check and removal
        handled = self.quick_remove_usercentrics()
        
        # If still present, try the full handling
        if not handled:
            handled = self.handle_usercentrics() or handled
        
        # Then check for other cookie popups
        handled = self.handle_generic_cookies() or handled
        
        return handled
    
    def quick_remove_usercentrics(self):
        """Quickly remove usercentrics overlay without waiting"""
        try:
            # Don't wait, just immediately try to remove it
            result = self.driver.execute_script("""
                var removed = false;
                // Remove usercentrics root
                var uc = document.getElementById('usercentrics-root');
                if (uc) {
                    uc.remove();
                    removed = true;
                }
                // Remove any shadow hosts
                document.querySelectorAll('[id*="usercentrics"]').forEach(el => {
                    el.remove();
                    removed = true;
                });
                // Remove high z-index overlays
                document.querySelectorAll('div').forEach(el => {
                    const style = window.getComputedStyle(el);
                    const zIndex = parseInt(style.zIndex);
                    if (zIndex > 9999) {
                        el.remove();
                        removed = true;
                    }
                });
                return removed;
            """)
            if result:
                print("  ✓ Instantly removed cookie overlay")
            return result
        except:
            return False
    
    def handle_usercentrics(self):
        """Handle usercentrics cookie consent overlay"""
        try:
            # Wait a moment for the popup to fully load
            time.sleep(2)
            
            # Check if usercentrics-root exists or if privacy text is visible
            usercentrics_root = self.driver.find_elements(By.ID, "usercentrics-root")
            privacy_text = "Privatsphäre-Einstellungen" in self.driver.page_source
            
            if not usercentrics_root and not privacy_text:
                return False
                
            print("  → Detected usercentrics/privacy consent popup")
            
            # First, try to find and click buttons in the main document
            # Try different selectors - prioritize "Ablehnen" (Reject) button
            usercentrics_selectors = [
                # Prioritize "Ablehnen" (Reject) button - simpler and faster
                "//button[text()='Ablehnen']",
                "//button[contains(text(), 'Ablehnen')]",
                "//button[contains(., 'Ablehnen')]",
                # Also try with different HTML elements
                "//a[contains(text(), 'Ablehnen')]",
                "//div[contains(text(), 'Ablehnen')]/parent::button",
                # Fallback to accept if reject doesn't work
                "//button[text()='Alles akzeptieren']",
                "//button[contains(text(), 'Alles akzeptieren')]",
                # Common usercentrics button selectors
                "//button[@data-testid='uc-deny-all-button']",
                "//button[@data-testid='uc-reject-button']",
                "//button[contains(@class, 'uc-btn-deny')]"
            ]
            
            # Try each selector
            for selector in usercentrics_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        try:
                            # Check if button is visible
                            if button.is_displayed():
                                print(f"  → Found button: '{button.text}' at location {button.location}")
                                
                                # Try multiple click methods
                                # Method 1: JavaScript click (most reliable)
                                try:
                                    self.driver.execute_script("arguments[0].click();", button)
                                    print("  ✓ Clicked with JavaScript")
                                    time.sleep(0.5)  # Brief wait
                                    # Check if popup is gone
                                    if not self.driver.find_elements(By.ID, "usercentrics-root"):
                                        return True
                                except:
                                    pass
                                
                                # Method 2: Regular click
                                try:
                                    button.click()
                                    print("  ✓ Clicked with regular click")
                                    time.sleep(0.5)  # Brief wait
                                    # Check if popup is gone
                                    if not self.driver.find_elements(By.ID, "usercentrics-root"):
                                        return True
                                except:
                                    pass
                                
                                # Method 3: Actions chain click
                                try:
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    ActionChains(self.driver).move_to_element(button).click().perform()
                                    print("  ✓ Clicked with ActionChains")
                                    time.sleep(0.5)  # Brief wait
                                    # Check if popup is gone
                                    if not self.driver.find_elements(By.ID, "usercentrics-root"):
                                        return True
                                except:
                                    pass
                                    
                        except Exception as e:
                            print(f"  → Error clicking button: {e}")
                            continue
                            
                except Exception as e:
                    continue
            
            # If buttons don't work, try to remove the overlay with JavaScript
            print("  → Buttons not working, trying to remove overlay with JavaScript...")
            try:
                # Remove usercentrics root element
                self.driver.execute_script("""
                    var element = document.getElementById('usercentrics-root');
                    if (element) {
                        element.remove();
                        console.log('Removed usercentrics-root');
                    }
                    // Also try to remove any shadow hosts
                    var shadows = document.querySelectorAll('*');
                    shadows.forEach(function(el) {
                        if (el.shadowRoot && el.id && el.id.includes('usercentrics')) {
                            el.remove();
                        }
                    });
                    // Remove any overlays
                    var overlays = document.querySelectorAll('div[style*="z-index: 2147"], div[style*="z-index: 9999"]');
                    overlays.forEach(function(el) {
                        el.remove();
                    });
                """)
                print("  ✓ Forcefully removed cookie overlay")
                # No wait needed after removal
                return True
            except Exception as e:
                print(f"  → Error removing overlay: {e}")
            
            # Last resort: brief wait
            print("  → Waiting for popup to disappear...")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  → Error handling usercentrics: {e}")
            pass
        
        return False
    
    def handle_generic_cookies(self):
        """Handle generic cookie consent popups"""
        try:
            # Cookie accept button selectors
            selectors = [
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'akzeptieren')]",
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'zustimmen')]",
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accept')]",
                "//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'akzeptieren')]",
                "//button[contains(@class, 'accept')]",
                "//button[contains(@id, 'accept')]",
                "//div[contains(@class, 'cookie')]//button[1]"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            elem.click()
                            print("  → Generic cookie popup handled")
                            time.sleep(1)
                            return True
                except:
                    continue
                    
        except Exception:
            pass
        
        return False