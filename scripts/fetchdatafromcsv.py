#!/usr/bin/env python3
import argparse
import os
from datetime import datetime, timedelta
from libs.nse_data_fetcher import NSEMasterData
from libs.data_cleaner import validate_data, add_technical_features
from libs.storage import DataStorage
import sys
import pandas as pd

DEFAULT_CSV = 'stocklist.csv'

def get_user_input():
    """Get input from user interactively"""
    print("\nNSE Data Fetcher - Interactive Mode")
    print("---------------------------------")

    symbol = input("Enter stock symbol (e.g., TCS, INFY): ").strip().upper()
    days = input("Number of days to fetch [30]: ").strip()
    days = int(days) if days.isdigit() else 30
    interval = input("Interval (1d, 1m, 5m, 10m, 30m, 1h) [1d]: ").strip().lower()
    interval = interval if interval in ['1d', '1m', '5m', '10m', '30m', '1h'] else '1d'

    return {
        'symbol': symbol,
        'days': days,
        'interval': interval
    }

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

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Fetch and store NSE OHLC data')
    parser.add_argument('--symbol', type=str, help='Stock symbol (e.g., TCS, INFY)')
    parser.add_argument('--days', type=int, default=30, help='Number of historical days to fetch')
    parser.add_argument('--interval', type=str, default='1d', choices=['1d', '1m', '5m', '10m', '30m', '1h'], help='Data interval')
    parser.add_argument('--file', type=str, help='Path to CSV file with stock symbols')

    return parser.parse_args()

def main():
    args = parse_args()

    if args.file:
        # Fetch data for multiple symbols from CSV
        fetch_data_from_csv(args.file)
    elif args.symbol:
        # Fetch data for a single symbol
        start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
        fetch_data_for_symbol(args.symbol, args.interval, start_date)
    else:
        # Default to interactive mode
        if os.path.exists(DEFAULT_CSV):
            print(f"Using default CSV file: {DEFAULT_CSV}")
            fetch_data_from_csv(DEFAULT_CSV)
        else:
            print("No CSV file found. Entering interactive mode...")
            user_input = get_user_input()
            fetch_data_for_symbol(user_input['symbol'], user_input['interval'], (datetime.now() - timedelta(days=user_input['days'])).strftime('%Y-%m-%d'))

if __name__ == "__main__":
    main()