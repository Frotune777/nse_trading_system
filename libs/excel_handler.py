import pandas as pd
from datetime import datetime
from libs.nse_data_fetcher import NSEMasterData
from libs.data_cleaner import validate_data, add_technical_features
from libs.storage import DataStorage

def fetch_data_for_symbol(symbol, timeframe, startdate):
    """Fetch and process data for a single symbol."""
    end_date = datetime.now()
    start_date = datetime.strptime(startdate, '%Y-%m-%d')

    fetcher = NSEMasterData()
    fetcher.download_symbol_master()
    storage = DataStorage()

    print(f"Fetching data for {symbol} from {start_date.date()} to {end_date.date()} with {timeframe} interval...")
    df = fetcher.get_history(symbol=symbol, exchange="NSE", start=start_date, end=end_date, interval=timeframe)

    if df.empty:
        print(f"❌ No data received for {symbol}")
        return

    clean_df = validate_data(df)
    enhanced_df = add_technical_features(clean_df)
    storage.save_to_parquet(enhanced_df, symbol, timeframe)
    storage.update_sqlite(enhanced_df, symbol, timeframe)
    print(f"✅ Successfully saved data for {symbol}")

def fetch_data_from_csv(file_path):
    """Fetch and process data for multiple symbols listed in a CSV file."""
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        fetch_data_for_symbol(row['symbol'], row['timeframe'], row['startdate'])