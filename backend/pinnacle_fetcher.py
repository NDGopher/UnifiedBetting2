import requests
import json
import time
from datetime import datetime

SWORDFISH_API_BASE_URL = "https://swordfish-production.up.railway.app/events/"

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Origin": "https://www.pinnacleoddsdropper.com",
    "Referer": "https://www.pinnacleoddsdropper.com/",
    "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not:A-Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
}

def remove_history(data):
    """Recursively remove any 'history' key from a dictionary."""
    if isinstance(data, dict):
        cleaned_data = {}
        for key, value in data.items():
            if key == "history":
                continue
            cleaned_data[key] = remove_history(value)
        return cleaned_data
    elif isinstance(data, list):
        return [remove_history(item) for item in data]
    else:
        return data

def fetch_live_pinnacle_event_odds(event_id):
    """
    Fetches all live lines for a given event_id from the Swordfish API that POD uses.
    Updated with faster timeout (8s) and retry delays to respect rate limits.
    """
    url = f"{SWORDFISH_API_BASE_URL}{event_id}"
    print(f"[Pinnacle Fetcher] Attempting to fetch: {url}")
    
    # Updated retry logic with faster timeout and delays
    max_retries = 1  # Reduced from 2 to 1 for faster cycling
    timeout_fast = 8  # seconds - for quick failure detection
    retry_delays = [1]  # seconds between retries
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                print(f"[Pinnacle Fetcher] Retry attempt {attempt} for {event_id} (waiting {retry_delays[attempt-1]}s)")
                time.sleep(retry_delays[attempt-1])
            
            response = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout_fast)
            response.raise_for_status()
            print(f"[Pinnacle Fetcher] SUCCESS: Status Code {response.status_code} for {event_id}")
            odds_data = response.json()
            cleaned_odds_data = remove_history(odds_data)  # Remove 'history'
            return {"success": True, "data": cleaned_odds_data, "event_id": event_id}
            
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                print(f"[Pinnacle Fetcher] TIMEOUT: Attempt {attempt + 1} timed out after {timeout_fast}s for {event_id}")
                continue
            else:
                error_message = f"Request timed out after {max_retries + 1} attempts ({timeout_fast}s each)"
                print(f"[Pinnacle Fetcher] FAILED: {error_message} for {event_id}")
                return {"success": False, "error": error_message, "event_id": event_id}
                
        except requests.exceptions.HTTPError as http_err:
            error_message = f"HTTP error occurred: {http_err} - Response: {response.text[:200]}"
            print(f"[Pinnacle Fetcher] HTTP ERROR: {error_message} for {event_id}")
            return {"success": False, "error": error_message, "event_id": event_id}
            
        except requests.exceptions.RequestException as req_err:
            error_message = f"Request error occurred: {req_err}"
            print(f"[Pinnacle Fetcher] REQUEST ERROR: {error_message} for {event_id}")
            return {"success": False, "error": error_message, "event_id": event_id}
            
        except json.JSONDecodeError as json_err:
            error_message = f"Failed to decode JSON: {json_err} - Response text: {response.text[:200]}"
            print(f"[Pinnacle Fetcher] JSON ERROR: {error_message} for {event_id}")
            return {"success": False, "error": error_message, "event_id": event_id}
            
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            print(f"[Pinnacle Fetcher] UNEXPECTED ERROR: {error_message} for {event_id}")
            return {"success": False, "error": error_message, "event_id": event_id}

if __name__ == '__main__':
    test_event_id = "1609669590"
    print(f"Testing fetch for event_id: {test_event_id}")
    result = fetch_live_pinnacle_event_odds(test_event_id)
    if result["success"]:
        print(f"Successfully fetched data for {test_event_id}")
        filename = f"test_pinnacle_fetcher_output_{test_event_id}.json"
        with open(filename, 'w') as f:
            json.dump(result["data"], f, indent=4)
        print(f"Test data saved to {filename}")
    else:
        print(f"Failed to fetch data for {test_event_id}: {result['error']}") 