#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
from libs.nse_data_fetcher import NSEMasterData
from libs.data_cleaner import validate_data, add_technical_features
from libs.storage import DataStorage
import sys


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


def parse_args():
    """Parse command line arguments or fallback to interactive mode"""
    parser = argparse.ArgumentParser(description='Fetch and store NSE OHLC data', add_help=False)
    parser.add_argument('--symbol', type=str, help='Stock symbol (e.g., TCS, INFY)')
    parser.add_argument('--days', type=int, default=30, help='Number of historical days to fetch')
    parser.add_argument('--interval', type=str, default='1d',
                        choices=['1d', '1m', '5m', '10m', '30m', '1h'], help='Data interval')

    try:
        args = parser.parse_args()
        if not args.symbol:
            return get_user_input()
        return vars(args)
    except:
        return get_user_input()


def main():
    args = parse_args()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args['days'])

    print(f"\nFetching {args['days']} days of {args['interval']} data for {args['symbol']}...")

    try:
        # Setup fetcher and storage
        fetcher = NSEMasterData()
        fetcher.download_symbol_master()
        storage = DataStorage()

        print("⏳ Downloading data from NSE...")
        df = fetcher.get_history(
            symbol=args['symbol'],
            exchange="NSE",
            start=start_date,
            end=end_date,
            interval=args['interval']
        )

        if df.empty:
            print("❌ No data received from NSE")
            sys.exit(1)

        print(f"✅ Received {len(df)} records")

        print("🧹 Cleaning data...")
        clean_df = validate_data(df)
        print(f"🛁 After cleaning: {len(clean_df)} valid records")

        print("📊 Adding technical indicators...")
        enhanced_df = add_technical_features(clean_df)

        print("💾 Saving data...")
        storage.save_to_parquet(enhanced_df, args['symbol'], args['interval'])
        storage.update_sqlite(enhanced_df, args['symbol'], args['interval'])

        print(f"\n🎉 Successfully saved {len(enhanced_df)} records")
        print(f"📅 Date range: {enhanced_df.index.min().date()} to {enhanced_df.index.max().date()}")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()