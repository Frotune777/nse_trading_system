import os
import sqlite3
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


class DataStorage:
    def __init__(self):
        self.data_dir = Path("data")
        self.raw_path = self.data_dir / "raw"
        self.processed_path = self.data_dir / "processed"
        self.db_path = self.data_dir / "trading.db"

        os.makedirs(self.raw_path, exist_ok=True)
        os.makedirs(self.processed_path, exist_ok=True)

    def save_to_parquet(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        """Save DataFrame to Parquet with incremental updates"""
        if df.empty:
            return

        path = self.processed_path / f"{symbol}_{interval}.parquet"

        # Read and merge with existing data if file exists
        if path.exists():
            existing = pd.read_parquet(path)
            updated = pd.concat([existing, df])

            # Remove duplicates keeping last occurrence
            if 'datetime' in df.columns:
                updated = updated.drop_duplicates(subset=['datetime'], keep='last')
            elif df.index.name == 'datetime':
                updated = updated[~updated.index.duplicated(keep='last')]

            updated.to_parquet(path, engine='pyarrow')
        else:
            # First time save
            df.to_parquet(path, engine='pyarrow')

    def update_sqlite(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        """Update SQLite with deduplication and batch inserts"""
        if df.empty:
            return

        table_name = f"{symbol}_{interval}_ohlc".lower()
        df_reset = df.reset_index() if df.index.name == 'datetime' else df.copy()

        with sqlite3.connect(self.db_path) as conn:
            # Create table if not exists
            if 'datetime' in df_reset.columns:
                df_reset.to_sql(
                    name=table_name,
                    con=conn,
                    if_exists='append',
                    index=False,
                    method='multi',
                    chunksize=1000
                )

                # Remove duplicates (SQLite doesn't have UPSERT in older versions)
                conn.execute(f"""
                    DELETE FROM {table_name} 
                    WHERE rowid NOT IN (
                        SELECT MIN(rowid) 
                        FROM {table_name} 
                        GROUP BY datetime
                    )
                """)

    def get_last_timestamp(self, symbol: str, interval: str) -> Optional[datetime]:
        """Get most recent record datetime for a symbol-interval pair"""
        table_name = f"{symbol}_{interval}_ohlc".lower()

        # Check SQLite first
        with sqlite3.connect(self.db_path) as conn:
            try:
                result = conn.execute(
                    f"SELECT MAX(datetime) FROM {table_name}"
                ).fetchone()[0]
                if result:
                    return pd.to_datetime(result)
            except sqlite3.OperationalError:
                pass  # Table doesn't exist

        # Fallback to Parquet
        parquet_path = self.processed_path / f"{symbol}_{interval}.parquet"
        if parquet_path.exists():
            df = pd.read_parquet(parquet_path)
            if not df.empty:
                if df.index.name == 'datetime':
                    return df.index.max()
                elif 'datetime' in df.columns:
                    return pd.to_datetime(df['datetime']).max()

        return None

    def fetch_incremental(self, fetcher, symbol: str, interval: str, force_full: bool = False) -> None:
        """Complete incremental update workflow"""
        last_date = None if force_full else self.get_last_timestamp(symbol, interval)

        # Calculate start date based on interval
        if last_date:
            if interval.endswith('m'):  # Minute data
                start_date = last_date + timedelta(minutes=1)
            else:  # Daily/weekly
                start_date = last_date + timedelta(days=1)
        else:
            start_date = datetime(2000, 1, 1)  # Default to old date if no history

        end_date = datetime.now()

        print(f"Fetching {symbol} {interval} data from {start_date} to {end_date}")
        new_data = fetcher.fetch_data(
            symbol=symbol,
            start=start_date,
            end=end_date,
            interval=interval
        )

        if not new_data.empty:
            print(f"Found {len(new_data)} new records")
            self.save_to_parquet(new_data, symbol, interval)
            self.update_sqlite(new_data, symbol, interval)
        else:
            print("No new data found")


# Example Usage
if __name__ == "__main__":
    from libs.data_fetcher import NSEDataFetcher  # Your existing fetcher

    storage = DataStorage()
    fetcher = NSEDataFetcher()

    # First run (full history)
    print("Initial data load...")
    storage.fetch_incremental(fetcher, "TCS", "1d", force_full=True)

    # Subsequent runs (incremental)
    print("\nIncremental update...")
    storage.fetch_incremental(fetcher, "TCS", "1d")

    # For intraday data
    print("\nFetching minute data...")
    storage.fetch_incremental(fetcher, "NIFTY", "15m", force_full=True)