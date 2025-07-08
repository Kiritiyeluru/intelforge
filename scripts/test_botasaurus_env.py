#!/usr/bin/env python3
"""
Test script to diagnose and fix Botasaurus environment issues.
Based on implementation issues analysis, this script will:
1. Test Chrome connection in proper environment
2. Check available driver methods
3. Fix API method issues
"""
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_chrome_direct():
    """Test Chrome connection directly."""
    print("=== Testing Chrome Direct Connection ===")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        
        # Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9223')  # Different port
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        
        # Create driver
        print("Creating Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Test basic functionality
        print("Testing basic navigation...")
        driver.get("https://httpbin.org/json")
        time.sleep(2)
        
        # Get page source
        content = driver.page_source
        print(f"✅ Chrome connection successful! Content length: {len(content)}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Chrome direct test failed: {e}")
        return False

def test_botasaurus_import():
    """Test Botasaurus import and check available methods."""
    print("\n=== Testing Botasaurus Import and API ===")
    try:
        # Test import
        print("Testing botasaurus import...")
        from botasaurus.browser import browser
        from botasaurus import bt
        print("✅ Botasaurus import successful!")
        
        # Check browser decorator
        print("Testing browser decorator...")
        
        @browser(
            headless=True,
            # Remove problematic options first
            # profile="stealth-profile",
            # block_images_and_css=True,
            lang="en-US",
            # wait_for_complete_page_load=True
        )
        def test_browser_function(driver, url: str):
            """Test function to check driver methods."""
            print(f"Driver type: {type(driver)}")
            print(f"Available methods: {[m for m in dir(driver) if not m.startswith('_')]}")
            
            # Test basic navigation
            driver.get(url)
            
            # Test different method names that might work
            methods_to_test = [
                'page_source', 'current_url', 'title',
                'find_element', 'find_elements',
                'execute_script', 'get_screenshot_as_png',
                'implicitly_wait', 'set_page_load_timeout'
            ]
            
            working_methods = []
            for method in methods_to_test:
                if hasattr(driver, method):
                    working_methods.append(method)
            
            print(f"Working methods: {working_methods}")
            return driver.page_source if hasattr(driver, 'page_source') else "No page_source method"
        
        # Test the function
        print("Testing browser function...")
        result = test_browser_function("https://httpbin.org/json")
        print(f"✅ Botasaurus test successful! Result length: {len(result)}")
        return True
        
    except Exception as e:
        print(f"❌ Botasaurus test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test and set proper environment variables."""
    print("\n=== Testing Environment Variables ===")
    
    # Display settings
    display = os.environ.get('DISPLAY', ':0')
    print(f"DISPLAY: {display}")
    
    # Set Chrome-specific environment variables
    env_vars = {
        'DISPLAY': ':0',
        'CHROME_BIN': '/usr/bin/google-chrome-stable',
        'CHROME_PATH': '/usr/bin/google-chrome-stable',
        'GOOGLE_CHROME_BIN': '/usr/bin/google-chrome-stable',
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"Set {key}={value}")
    
    # Test Chrome binary exists
    chrome_path = '/usr/bin/google-chrome-stable'
    if os.path.exists(chrome_path):
        print(f"✅ Chrome binary found at {chrome_path}")
    else:
        print(f"❌ Chrome binary not found at {chrome_path}")
    
    return True

def main():
    """Main test function."""
    print("🔧 Botasaurus Environment Diagnosis and Fix")
    print("=" * 50)
    
    # Test environment variables
    test_environment_variables()
    
    # Test Chrome direct connection
    chrome_works = test_chrome_direct()
    
    # Test Botasaurus
    botasaurus_works = test_botasaurus_import()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS RESULTS:")
    print(f"Chrome Direct: {'✅ WORKING' if chrome_works else '❌ FAILED'}")
    print(f"Botasaurus: {'✅ WORKING' if botasaurus_works else '❌ FAILED'}")
    
    if chrome_works and botasaurus_works:
        print("\n🎉 SUCCESS: Both Chrome and Botasaurus are working!")
        print("Environment fix complete. Ready for stealth browser automation.")
    elif chrome_works and not botasaurus_works:
        print("\n⚠️  Chrome works but Botasaurus has issues.")
        print("Check Botasaurus installation and API usage.")
    elif not chrome_works:
        print("\n❌ Chrome connection failed.")
        print("Check display environment and Chrome installation.")
    
    return chrome_works and botasaurus_works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)