
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from libs.nse_data_fetcher import NSEMasterData
from libs.fundamentals import FundamentalFetcher

def test():
    symbol = "SBIN"
    print(f"Testing Valuation Logic for {symbol}...")
    
    # 1. Fetch Price
    print("1. Fetching Price History (NSEMasterData)...")
    fetcher = NSEMasterData()
    fetcher.download_symbol_master()
    end = datetime.now()
    start = end - timedelta(days=365*2) # 2 years
    price_df = fetcher.get_history(symbol, start=start, end=end)
    print(f"   Fetched {len(price_df)} rows")
    
    # 2. Fetch Fundamentals
    print("\n2. Fetching Quarterly EPS (FundamentalFetcher)...")
    fund = FundamentalFetcher()
    data = fund.fetch_data(symbol)
    q_data = data.get('quarterly_results', {})
    print(f"   Quarters found: {len(q_data.get('quarters', []))}")
    
    # 3. Calculate PE
    print("\n3. Calculating Historical PE...")
    pe_df = fund.calculate_historical_pe(price_df, q_data)
    
    if not pe_df.empty:
        print("✅ Success! PE Series Generated.")
        print(pe_df[['Close', 'ttm_eps', 'PE']].tail())
        
        last_pe = pe_df['PE'].iloc[-1]
        print(f"\nLast PE: {last_pe:.2f}")
    else:
        print("❌ Failed to generate PE Series")

if __name__ == "__main__":
    test()
