
import sys
import yaml
import time
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from libs.nse_data_fetcher import NSEMasterData
from libs.NseUtility import NseUtils
from libs.data_cleaner import validate_data, add_technical_features
from libs.storage import DataStorage

def load_config():
    config_path = project_root / "config" / "symbols.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

def json_serial(obj):
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    return str(obj)

def save_market_data(data, filename):
    output_dir = project_root / "data" / "processed" / "market_stats"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"{filename}.json"
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, default=json_serial)
    print(f"Saved {filename} to {file_path}")

def update_market():
    print("🚀 Starting Market Update...")
    
    # 1. Load Config
    config = load_config()
    symbols = config.get("tracked_symbols", [])
    print(f"📝 Found {len(symbols)} symbols to track")

    # 2. Setup Components
    ohlc_fetcher = NSEMasterData()
    ohlc_fetcher.download_symbol_master()
    
    api_fetcher = NseUtils()
    storage = DataStorage()

    # 3. Fetch Market Broad Data
    print("\n🌍 Fetching Market Broad Data...")
    
    # Common date range for deals and actions (last 7 days by default)
    deals_from = (datetime.now() - timedelta(days=7)).strftime("%d-%m-%Y")
    deals_to = datetime.now().strftime("%d-%m-%Y")

    try:
        fii_dii = api_fetcher.fii_dii_activity()
        if isinstance(fii_dii, pd.DataFrame) and not fii_dii.empty:
            storage.update_market_stats(fii_dii, "market_fii_dii", ["category", "date"])
    except Exception as e:
        print(f"❌ Failed to fetch FII/DII: {e}")

    try:
        insider = api_fetcher.get_insider_trading()
        if isinstance(insider, pd.DataFrame) and not insider.empty:
            storage.update_market_stats(insider, "market_insider_trading", ["symbol", "acqName", "date", "secAcq"])
    except Exception as e:
        print(f"❌ Failed to fetch Insider Trading: {e}")

    try:
        bulk_deals = api_fetcher.get_bulk_deals(from_date=deals_from, to_date=deals_to)
        if isinstance(bulk_deals, pd.DataFrame) and not bulk_deals.empty:
            # Table Schema: symbol, date, clientName, type, quantity, price
            storage.update_market_stats(bulk_deals, "market_bulk_deals", ["symbol", "date", "clientName", "type", "quantity"])
    except Exception as e:
        print(f"❌ Failed to fetch Bulk Deals: {e}")

    try:
        block_deals = api_fetcher.get_block_deals(from_date=deals_from, to_date=deals_to)
        if isinstance(block_deals, pd.DataFrame) and not block_deals.empty:
            storage.update_market_stats(block_deals, "market_block_deals", ["symbol", "date", "clientName", "type", "quantity"])
    except Exception as e:
        print(f"❌ Failed to fetch Block Deals: {e}")

    try:
        corp_actions = api_fetcher.get_corporate_action(from_date_str=deals_from, to_date_str=deals_to)
        if isinstance(corp_actions, pd.DataFrame) and not corp_actions.empty:
            # Table Schema: symbol, exDate, purpose
            storage.update_market_stats(corp_actions, "market_corp_actions", ["symbol", "exDate", "purpose"])
    except Exception as e:
        print(f"❌ Failed to fetch Corporate Actions: {e}")

    try:
        short_selling = api_fetcher.get_short_selling(from_date=deals_from, to_date=deals_to)
        if isinstance(short_selling, pd.DataFrame) and not short_selling.empty:
            # Table Schema: symbol, date, clientName, quantity
            storage.update_market_stats(short_selling, "market_short_selling", ["symbol", "date", "clientName", "quantity"])
    except Exception as e:
        print(f"❌ Failed to fetch Short Selling: {e}")
        
    try:
        results = api_fetcher.get_upcoming_results_calendar()
        if isinstance(results, pd.DataFrame) and not results.empty:
            storage.update_market_stats(results, "market_upcoming_results", ["symbol", "date"])
    except Exception as e:
        print(f"❌ Failed to fetch Upcoming Results: {e}")

    # 4. Fetch OHLC + Technicals for each symbol
    print("\n📈 Updating Stock Data...")
    stats = {"updated": 0, "failed": 0, "no_new_data": 0}
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60) # Fetch last 60 days to ensure enough data for indicators

    for symbol in tqdm(symbols):
        try:
            # Add small delay to be polite
            time.sleep(1)
            
            df = ohlc_fetcher.get_history(
                symbol=symbol,
                exchange="NSE",
                start=start_date,
                end=end_date,
                interval='1d'
            )

            if df.empty:
                stats["no_new_data"] += 1
                continue

            # Clean & Enrich
            clean_df = validate_data(df)
            enhanced_df = add_technical_features(clean_df)

            # Save
            storage.save_to_parquet(enhanced_df, symbol, '1d')
            storage.update_sqlite(enhanced_df, symbol, '1d')
            stats["updated"] += 1
            
        except Exception as e:
            print(f"\n❌ Error updating {symbol}: {e}")
            stats["failed"] += 1

    print("\n✅ Update Complete!")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")
    print(f"No Data: {stats['no_new_data']}")

if __name__ == "__main__":
    update_market()
