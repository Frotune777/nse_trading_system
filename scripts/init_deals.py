
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from libs.NseUtility import NseUtils
from libs.storage import DataStorage

def initialize_deals():
    print("🚀 Initializing Bulk/Block Deals & Corp Actions (30 Day Lookback)...")
    
    api_fetcher = NseUtils()
    storage = DataStorage()
    
    to_date = datetime.now().strftime("%d-%m-%Y")
    from_date = (datetime.now() - timedelta(days=30)).strftime("%d-%m-%Y")
    
    print(f"Fetching from {from_date} to {to_date}...")
    
    # 1. Bulk Deals
    try:
        df = api_fetcher.get_bulk_deals(from_date=from_date, to_date=to_date)
        if not df.empty:
            storage.update_market_stats(df, "market_bulk_deals", ["symbol", "date", "clientName", "type", "quantity"])
            print(f"✅ Saved {len(df)} Bulk Deals")
        else:
            print("⚠️ No Bulk Deals found in last 30 days.")
    except Exception as e:
        print(f"❌ Error Bulk Deals: {e}")

    # 2. Block Deals
    try:
        df = api_fetcher.get_block_deals(from_date=from_date, to_date=to_date)
        if not df.empty:
            storage.update_market_stats(df, "market_block_deals", ["symbol", "date", "clientName", "type", "quantity"])
            print(f"✅ Saved {len(df)} Block Deals")
        else:
            print("⚠️ No Block Deals found in last 30 days.")
    except Exception as e:
        print(f"❌ Error Block Deals: {e}")

    # 3. Corporate Actions
    try:
        df = api_fetcher.get_corporate_action(from_date_str=from_date, to_date_str=to_date)
        if not df.empty:
            storage.update_market_stats(df, "market_corp_actions", ["symbol", "exDate", "purpose"])
            print(f"✅ Saved {len(df)} Corporate Actions")
        else:
            print("⚠️ No Corporate Actions found in last 30 days.")
    except Exception as e:
        print(f"❌ Error Corp Actions: {e}")

    # 4. Short Selling
    try:
        df = api_fetcher.get_short_selling(from_date=from_date, to_date=to_date)
        if not df.empty:
            storage.update_market_stats(df, "market_short_selling", ["symbol", "date", "clientName", "quantity"])
            print(f"✅ Saved {len(df)} Short Selling Records")
        else:
            print("⚠️ No Short Selling found in last 30 days.")
    except Exception as e:
        print(f"❌ Error Short Selling: {e}")

if __name__ == "__main__":
    initialize_deals()
