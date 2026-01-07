
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from libs.nse_data_fetcher import NSEMasterData
from datetime import datetime, timedelta

def test():
    fetcher = NSEMasterData()
    print("1. Downloading Master Data...")
    fetcher.download_symbol_master()
    
    print("\n2. Searching for Nifty 50...")
    # Try different search terms if needed
    res = fetcher.search("Nifty 50", "NSE")
    print(f"Search Results:\n{res}")
    
    if not res.empty:
        symbol = res.iloc[0]['Symbol']
        print(f"\n3. Fetching History for {symbol}...")
        end = datetime.now()
        start = end - timedelta(days=30)
        
        df = fetcher.get_history(symbol=symbol, start=start, end=end, interval='1d')
        if not df.empty:
            print("\n✅ Success!")
            print(df.head())
        else:
            print("\n❌ History Empty")
    else:
        print("\n❌ Nifty 50 not found in Master Data")

if __name__ == "__main__":
    test()
