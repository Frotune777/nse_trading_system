#!/usr/bin/env python3
"""
Bulk Historical Data Downloader

Downloads historical OHLCV data for multiple symbols across multiple timeframes
with progress tracking, resume capability, and parallel processing.

Usage:
    python scripts/bulk_download_historical.py --symbols RELIANCE,TCS,INFY --timeframes 1d,1w --from-date 1995-01-01
    python scripts/bulk_download_historical.py --symbols-file symbols.txt --timeframes 1d --parallel 3
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import argparse
import time
from datetime import datetime
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from libs.historical_data_manager import HistoricalDataManager


def read_symbols_from_file(filepath: str) -> List[str]:
    """Read symbols from a text file (one per line)."""
    with open(filepath, 'r') as f:
        return [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]


def download_single_symbol(
    manager: HistoricalDataManager,
    symbol: str,
    timeframes: List[str],
    from_date: str,
    progress_dict: dict
) -> dict:
    """Download data for a single symbol."""
    try:
        results = manager.download_symbol_data(symbol, timeframes, from_date)
        progress_dict[symbol] = results
        return {symbol: results}
    except Exception as e:
        print(f"❌ Error downloading {symbol}: {e}")
        progress_dict[symbol] = {tf: False for tf in timeframes}
        return {symbol: {tf: False for tf in timeframes}}


def print_progress(current: int, total: int, symbol: str, timeframe: str, success: bool):
    """Print download progress."""
    status = "✅" if success else "❌"
    percentage = (current / total) * 100
    print(f"[{current}/{total}] ({percentage:.1f}%) {status} {symbol} {timeframe}")


def main():
    parser = argparse.ArgumentParser(
        description='Bulk download historical OHLCV data from NSE',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download daily data for specific symbols from 1995
  python bulk_download_historical.py --symbols RELIANCE,TCS,INFY --timeframes 1d --from-date 1995-01-01
  
  # Download multiple timeframes from a file
  python bulk_download_historical.py --symbols-file symbols.txt --timeframes 1d,1w,1m
  
  # Parallel downloads (3 concurrent)
  python bulk_download_historical.py --symbols RELIANCE,TCS --timeframes 1d --parallel 3
        """
    )
    
    # Symbol input
    symbol_group = parser.add_mutually_exclusive_group(required=True)
    symbol_group.add_argument(
        '--symbols',
        type=str,
        help='Comma-separated list of symbols (e.g., RELIANCE,TCS,INFY)'
    )
    symbol_group.add_argument(
        '--symbols-file',
        type=str,
        help='Path to file containing symbols (one per line)'
    )
    
    # Timeframes
    parser.add_argument(
        '--timeframes',
        type=str,
        default='1d',
        help='Comma-separated list of timeframes (default: 1d). Options: 1m,5m,10m,15m,30m,1h,1d,1w,1M'
    )
    
    # Date range
    parser.add_argument(
        '--from-date',
        type=str,
        default='1995-01-01',
        help='Start date in YYYY-MM-DD format (default: 1995-01-01)'
    )
    parser.add_argument(
        '--to-date',
        type=str,
        default=None,
        help='End date in YYYY-MM-DD format (default: today)'
    )
    
    # Performance
    parser.add_argument(
        '--parallel',
        type=int,
        default=1,
        help='Number of parallel downloads (default: 1, max: 5)'
    )
    
    # Resume
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip symbols that already have data for the specified timeframes'
    )
    
    args = parser.parse_args()
    
    # Parse symbols
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(',')]
    else:
        symbols = read_symbols_from_file(args.symbols_file)
    
    # Parse timeframes
    timeframes = [tf.strip() for tf in args.timeframes.split(',')]
    
    # Validate timeframes
    valid_timeframes = ['1m', '5m', '10m', '15m', '30m', '1h', '1d', '1w', '1M']
    for tf in timeframes:
        if tf not in valid_timeframes:
            print(f"❌ Invalid timeframe: {tf}")
            print(f"Valid options: {', '.join(valid_timeframes)}")
            sys.exit(1)
    
    # Limit parallel downloads
    parallel = min(max(1, args.parallel), 5)
    
    # Initialize manager
    print("🚀 Initializing Historical Data Manager...")
    manager = HistoricalDataManager()
    
    # Filter existing symbols if skip-existing is enabled
    if args.skip_existing:
        print("🔍 Checking for existing data...")
        filtered_symbols = []
        for symbol in symbols:
            existing_timeframes = set(manager.get_available_timeframes(symbol))
            requested_timeframes = set(timeframes)
            if not requested_timeframes.issubset(existing_timeframes):
                filtered_symbols.append(symbol)
            else:
                print(f"⏭️  Skipping {symbol} (already has {', '.join(timeframes)})")
        symbols = filtered_symbols
    
    if not symbols:
        print("✅ All symbols already have the requested data!")
        return
    
    # Summary
    print("\n" + "="*60)
    print(f"📊 Bulk Download Configuration")
    print("="*60)
    print(f"Symbols: {len(symbols)} ({', '.join(symbols[:5])}{'...' if len(symbols) > 5 else ''})")
    print(f"Timeframes: {', '.join(timeframes)}")
    print(f"Date Range: {args.from_date} to {args.to_date or 'today'}")
    print(f"Parallel Downloads: {parallel}")
    print(f"Total Downloads: {len(symbols) * len(timeframes)}")
    print("="*60 + "\n")
    
    # Confirm
    if len(symbols) * len(timeframes) > 10:
        response = input("⚠️  This will download a lot of data. Continue? (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled")
            return
    
    # Start download
    start_time = time.time()
    progress_dict = {}
    total_downloads = len(symbols) * len(timeframes)
    current_download = 0
    
    print(f"\n📥 Starting bulk download...\n")
    
    if parallel == 1:
        # Sequential download
        for symbol in symbols:
            results = manager.download_symbol_data(
                symbol,
                timeframes,
                args.from_date,
                args.to_date
            )
            progress_dict[symbol] = results
            
            for timeframe, success in results.items():
                current_download += 1
                print_progress(current_download, total_downloads, symbol, timeframe, success)
    else:
        # Parallel download
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(
                    download_single_symbol,
                    manager,
                    symbol,
                    timeframes,
                    args.from_date,
                    progress_dict
                ): symbol
                for symbol in symbols
            }
            
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    result = future.result()
                    for tf, success in result[symbol].items():
                        current_download += 1
                        print_progress(current_download, total_downloads, symbol, tf, success)
                except Exception as e:
                    print(f"❌ Error processing {symbol}: {e}")
    
    # Summary
    elapsed_time = time.time() - start_time
    successful = sum(1 for results in progress_dict.values() for success in results.values() if success)
    failed = total_downloads - successful
    
    print("\n" + "="*60)
    print("📊 Download Summary")
    print("="*60)
    print(f"Total Downloads: {total_downloads}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Time Elapsed: {elapsed_time:.1f}s")
    print(f"📈 Average: {elapsed_time/total_downloads:.1f}s per download")
    print("="*60)
    
    # Show failed downloads
    if failed > 0:
        print("\n❌ Failed Downloads:")
        for symbol, results in progress_dict.items():
            for timeframe, success in results.items():
                if not success:
                    print(f"  - {symbol} {timeframe}")


if __name__ == "__main__":
    main()
