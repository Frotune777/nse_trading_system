
import requests
import json

def debug_chain():
    symbol = "SBIN"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    
    session = requests.Session()
    
    # 1. Hit Homepage
    print("1. Hitting Homepage...")
    try:
        r = session.get("https://www.nseindia.com", headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
    except Exception as e:
        print(f"Homepage failed: {e}")
        return

    # 2. Hit Data API
    url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"
    print(f"\n2. Hitting API: {url}")
    try:
        r = session.get(url, headers=headers, timeout=10)
        print(f"Status: {r.status_code}")
        print("Response Content Preview:")
        print(r.text[:500])
        
        data = r.json()
        if "records" in data:
            print("\n✅ Success: Found 'records' key.")
        else:
            print(f"\n❌ JSON Key Error. Keys: {list(data.keys())}")
            
    except Exception as e:
        print(f"\n❌ Request Failed: {e}")

if __name__ == "__main__":
    debug_chain()
