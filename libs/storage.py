import os
import re
import sqlite3
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from libs.data_fetcher import NSEDataFetcher
import time


class DataStorage:
    def __init__(self):
        self.data_dir = Path("data")
        self.raw_path = self.data_dir / "raw"
        self.processed_path = self.data_dir / "processed"
        self.db_path = self.data_dir / "trading.db"

        os.makedirs(self.raw_path, exist_ok=True)
        os.makedirs(self.processed_path, exist_ok=True)

    @staticmethod
    def sanitize_table_name(symbol: str, interval: str) -> str:
        """Sanitize symbol and interval to create a safe SQLite table name"""
        raw_name = f"{symbol}_{interval}_ohlc".lower()
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_name)
        return f'"{safe_name}"'

    @staticmethod
    def sanitize_file_name(symbol: str, interval: str) -> str:
        """Sanitize symbol and interval to create a safe filename"""
        raw_name = f"{symbol}_{interval}".lower()
        return re.sub(r'[^a-zA-Z0-9_]', '_', raw_name)

    def save_to_parquet(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        """Save DataFrame to Parquet with incremental updates"""
        if df.empty:
            return

        file_name = self.sanitize_file_name(symbol, interval)
        path = self.processed_path / f"{file_name}.parquet"

        if path.exists():
            existing = pd.read_parquet(path)
            updated = pd.concat([existing, df])
            updated = updated[~updated.index.duplicated(keep='last')]
            updated.to_parquet(path, engine='pyarrow')
        else:
            df.to_parquet(path, engine='pyarrow')

    def update_sqlite(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        """Update SQLite with deduplication"""
        if df.empty:
            return

        table_name = self.sanitize_table_name(symbol, interval)

        # Ensure 'datetime' column is present
        df_reset = df.reset_index().rename(columns={"index": "datetime", "Timestamp": "datetime"})

        with sqlite3.connect(self.db_path) as conn:
            # Write data to SQLite
            df_reset.to_sql(
                name=table_name.strip('"'),  # to_sql does quoting internally
                con=conn,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )

            # Remove duplicates based on 'datetime'
            conn.execute(f"""
                DELETE FROM {table_name} 
                WHERE rowid NOT IN (
                    SELECT MIN(rowid) 
                    FROM {table_name} 
                    GROUP BY datetime
                )
            """)

    def get_last_timestamp(self, symbol: str, interval: str) -> Optional[datetime]:
        """Get most recent record datetime"""
        table_name = self.sanitize_table_name(symbol, interval).strip('"')
        with sqlite3.connect(self.db_path) as conn:
            try:
                result = conn.execute(
                    f"SELECT MAX(datetime) FROM {table_name}"
                ).fetchone()[0]
                if result:
                    return pd.to_datetime(result)
            except sqlite3.OperationalError:
                pass

        # Fallback to Parquet
        file_name = self.sanitize_file_name(symbol, interval)
        parquet_path = self.processed_path / f"{file_name}.parquet"
        if parquet_path.exists():
            df = pd.read_parquet(parquet_path)
            if not df.empty and isinstance(df.index, pd.DatetimeIndex):
                return df.index.max()

        return None

    def fetch_incremental(self, fetcher, symbol: str, interval: str, force_full: bool = False) -> pd.DataFrame:
        """Complete incremental update workflow with retry"""
        last_date = None if force_full else self.get_last_timestamp(symbol, interval)

        if last_date:
            start_date = last_date + timedelta(days=1)
        else:
            start_date = datetime(2000, 1, 1)

        end_date = datetime.now()
        max_retries = 3

        for attempt in range(max_retries):
            try:
                print(f"Fetching {symbol} {interval} data (attempt {attempt + 1}/{max_retries})...")
                new_data = fetcher.fetch_data(symbol=symbol, start=start_date, end=end_date)

                if not isinstance(new_data, pd.DataFrame):
                    raise TypeError(f"Expected DataFrame but got {type(new_data)}")

                if not new_data.empty:
                    print(f"Found {len(new_data)} new records")
                    self.save_to_parquet(new_data, symbol, interval)
                    self.update_sqlite(new_data, symbol, interval)
                    return new_data
                else:
                    print("No new data found")
                    return pd.DataFrame()

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {type(e).__name__} - {str(e)}")
                if attempt == max_retries - 1:
                    print("Max retries reached, giving up")
                    raise
                time.sleep(5 * (attempt + 1))

        return pd.DataFrame()


# Optional test runner
if __name__ == "__main__":
    try:
        fetcher = NSEDataFetcher()
        storage = DataStorage()

        print("Testing incremental update...")
        test_data = storage.fetch_incremental(fetcher, "TCS", "1d", force_full=True)

        if not test_data.empty:
            print("\nSample data:")
            print(test_data.head())
            print("\nStorage test completed successfully!")
        else:
            print("\nFailed to fetch test data")

    except Exception as e:
        print(f"Critical error during test: {str(e)}")