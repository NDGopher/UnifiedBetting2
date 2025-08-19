#!/usr/bin/env python3
"""
Quick speed test for PTO data extraction
Tests different methods to get data faster
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_pto_api_calls():
    """Test if we can find PTO's API endpoints"""
    print("\n🔍 Testing PTO API Discovery...")
    
    base_url = "https://picktheodds.app"
    api_urls = [
        "https://api.picktheodds.app/graphql",
        "https://picktheodds.app/api/odds",
        "https://picktheodds.app/api/graphql",
        "https://api.picktheodds.app/odds",
        "https://api.picktheodds.app/v1/odds"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://picktheodds.app"
    }
    
    for url in api_urls:
        try:
            print(f"[API] Testing: {url}")
            response = requests.get(url, headers=headers, timeout=5)
            print(f"[API] Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"[API] ✅ SUCCESS! Found working endpoint")
                content = response.text[:200]
                print(f"[API] Content preview: {content}")
                return url
                
        except Exception as e:
            print(f"[API] Error: {e}")
    
    print(f"[API] No direct API endpoints found")
    return None

def test_fast_dom_scraping():
    """Test optimized DOM scraping"""
    print("\n⚡ Testing Fast DOM Scraping...")
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-images")
    options.add_argument("--disable-javascript")  # Skip JS for speed
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-extensions")
    
    # Connect to existing debug session
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")
    
    try:
        driver = webdriver.Chrome(options=options)
        print(f"[DOM] ✅ Connected to debug session")
        
        # Test loading speed
        start_time = time.time()
        
        url = "https://picktheodds.app/en/odds-screen?league=MLB&betGroup=MONEYLINE&group=MONEY_LINE&time=MONEY_LINE&betView=false"
        driver.get(url)
        
        load_time = time.time() - start_time
        print(f"[DOM] Page load time: {load_time:.2f}s")
        
        # Try to find odds elements quickly
        start_time = time.time()
        elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='odd'], .odd, .odds-value")
        find_time = time.time() - start_time
        
        print(f"[DOM] Found {len(elements)} elements in {find_time:.2f}s")
        
        if elements:
            print(f"[DOM] ✅ Fast DOM scraping successful!")
            for i, elem in enumerate(elements[:3]):
                text = elem.text.strip()
                if text:
                    print(f"[DOM]   Element {i+1}: {text}")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"[DOM] Error: {e}")
        return False

def test_network_monitoring():
    """Test monitoring network requests for data"""
    print("\n🌐 Testing Network Monitoring...")
    
    # This would require selenium with CDP (Chrome DevTools Protocol)
    options = Options()
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")
    
    try:
        driver = webdriver.Chrome(options=options)
        
        # Enable performance logging
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Runtime.enable', {})
        
        url = "https://picktheodds.app/en/odds-screen?league=MLB&betGroup=MONEYLINE&group=MONEY_LINE&time=MONEY_LINE&betView=false"
        driver.get(url)
        
        time.sleep(3)  # Wait for network activity
        
        # Get network logs
        logs = driver.get_log('performance')
        
        print(f"[NET] Captured {len(logs)} network events")
        
        # Look for GraphQL or API calls
        api_calls = []
        for log in logs:
            message = log.get('message', {})
            if isinstance(message, str):
                import json
                try:
                    message = json.loads(message)
                except:
                    continue
            
            method = message.get('message', {}).get('method', '')
            if method == 'Network.responseReceived':
                url = message.get('message', {}).get('params', {}).get('response', {}).get('url', '')
                if 'api' in url or 'graphql' in url:
                    api_calls.append(url)
        
        print(f"[NET] Found {len(api_calls)} API calls:")
        for call in api_calls[:5]:
            print(f"[NET]   {call}")
        
        driver.quit()
        return api_calls
        
    except Exception as e:
        print(f"[NET] Error: {e}")
        return []

def main():
    print("🚀 PTO Speed Test Suite")
    print("=" * 40)
    
    # Test 1: API Discovery
    api_endpoint = test_pto_api_calls()
    
    # Test 2: Fast DOM Scraping
    dom_success = test_fast_dom_scraping()
    
    # Test 3: Network Monitoring
    api_calls = test_network_monitoring()
    
    print("\n📊 SPEED TEST RESULTS:")
    print("=" * 30)
    print(f"✅ API Endpoint Found: {api_endpoint is not None}")
    print(f"✅ Fast DOM Working: {dom_success}")
    print(f"✅ Network Calls Found: {len(api_calls) if api_calls else 0}")
    
    if api_endpoint:
        print(f"\n🎯 RECOMMENDATION: Use API endpoint {api_endpoint}")
    elif api_calls:
        print(f"\n🎯 RECOMMENDATION: Monitor network calls to {api_calls[0]}")
    else:
        print(f"\n🎯 RECOMMENDATION: Optimize DOM scraping with faster selectors")

if __name__ == "__main__":
    main()
