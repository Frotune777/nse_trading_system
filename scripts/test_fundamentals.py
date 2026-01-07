
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from libs.fundamentals import FundamentalFetcher
import json

def test_fetch():
    fetcher = FundamentalFetcher()
    symbol = "SBIN"
    print(f"Fetching data for {symbol}...")
    
    data = fetcher.fetch_data(symbol)
    
    print("\n--- Data Fetched ---")
    print(json.dumps(data, indent=2))
    
    if data and "key_metrics" in data:
        print("\n✅ Fundamentals Fetch Successful")
    else:
        print("\n❌ Fetch Failed or Empty")

if __name__ == "__main__":
    test_fetch()
