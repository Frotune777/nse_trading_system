
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from libs.NseUtility import NseUtils

def test_deals():
    print("Testing Bulk & Block Deals Fetching...")
    nse = NseUtils()
    
    # Define date range (last 7 days to be safe and quick)
    end_date = datetime.now().strftime("%d-%m-%Y")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%d-%m-%Y")
    
    print(f"\n1. Fetching Bulk Deals ({start_date} to {end_date})...")
    bulk_df = nse.get_bulk_deals(from_date=start_date, to_date=end_date)
    if not bulk_df.empty:
        print(f"   ✅ Success! Fetched {len(bulk_df)} records.")
        print(bulk_df[['symbol', 'securityName', 'clientName', 'buySell', 'quantity', 'tradePrice']].head().to_string())
    else:
        print("   ⚠️ No data returned. (Expected if API is blocked or no deals in range).")

    print(f"\n2. Fetching Block Deals ({start_date} to {end_date})...")
    block_df = nse.get_block_deals(from_date=start_date, to_date=end_date)
    if not block_df.empty:
        print(f"   ✅ Success! Fetched {len(block_df)} records.")
        print(block_df[['symbol', 'securityName', 'clientName', 'buySell', 'quantity', 'tradePrice']].head().to_string())
    else:
        print("   ⚠️ No data returned. (Expected if API is blocked or no deals in range).")

if __name__ == "__main__":
    test_deals()
