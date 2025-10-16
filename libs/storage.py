# storage.py

import os
import re
import sqlite3
import pandas as pd
import pyarrow.parquet as pq
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from libs.data_fetcher import NSEDataFetcher
import time


class DataStorage:
    def __init__(self, db_path: Optional[str] = None):
        self.data_dir = Path("data").resolve()
        self.raw_path = self.data_dir / "raw"
        self.processed_path = self.data_dir / "processed"
        self.db_path = Path(db_path) if db_path else self.data_dir / "trading.db"

        os.makedirs(self.raw_path, exist_ok=True)
        os.makedirs(self.processed_path, exist_ok=True)

    @staticmethod
    def sanitize_table_name(symbol: str, interval: str) -> str:
        raw_name = f"{symbol}_{interval}_ohlc".lower()
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_name)
        return f'"{safe_name}"'

    @staticmethod
    def sanitize_file_name(symbol: str, interval: str) -> str:
        raw_name = f"{symbol}_{interval}".lower()
        return re.sub(r'[^a-zA-Z0-9_]', '_', raw_name)

    def _prepare_dataframe_for_storage(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ensures the DataFrame has a 'Timestamp' column and is ready for storage.
        """
        if df.empty:
            return df

        # If the index is a DatetimeIndex, reset it and name the new column 'Timestamp'
        if isinstance(df.index, pd.DatetimeIndex):
            # Use 'names' parameter for pandas 1.5.0+ or chain .rename()
            # If your pandas version is older, you might need df = df.rename(columns={'index': 'Timestamp'})
            df = df.reset_index(names=['Timestamp'])
        
        # Ensure 'Timestamp' column is present and is datetime type
        if 'Timestamp' not in df.columns:
            # This case might occur if the original data fetched did not have a DatetimeIndex
            # and already contained a 'Timestamp' or similar column.
            # We should try to identify the datetime column if not named 'Timestamp'
            # For simplicity here, assuming the fetcher always provides a suitable index
            # that gets reset to 'Timestamp'. If not, more robust column identification
            # might be needed based on the fetched data structure.
            pass # No action needed if already a column and named Timestamp
        
        # Convert to datetime if it's not already
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Set 'Timestamp' as the index for internal consistency before saving,
        # but ensure it's a column when saving to SQLite and Parquet.
        # This will make sure when we read it back from Parquet, it has DatetimeIndex
        df = df.set_index('Timestamp').sort_index()

        return df

    def save_to_parquet(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        if df.empty:
            return

        # Prepare the DataFrame before saving (reset index to 'Timestamp' column)
        df_prepared = self._prepare_dataframe_for_storage(df.copy()) # Use a copy to avoid modifying original df passed in

        file_name = self.sanitize_file_name(symbol, interval)
        path = self.processed_path / f"{file_name}.parquet"

        if path.exists():
            existing = pd.read_parquet(path)
            # Ensure existing also has DatetimeIndex for proper concatenation
            if not isinstance(existing.index, pd.DatetimeIndex):
                existing = existing.set_index('Timestamp') # Assumes 'Timestamp' column exists
            
            updated = pd.concat([existing, df_prepared])
            updated = updated[~updated.index.duplicated(keep='last')].sort_index()
            updated.to_parquet(path, engine='pyarrow')
        else:
            df_prepared.to_parquet(path, engine='pyarrow')

    def update_sqlite(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        if df.empty:
            return

        table_name = self.sanitize_table_name(symbol, interval)
        
        # Prepare the DataFrame for SQLite: 'Timestamp' column for storing
        # df_reset = df.reset_index().rename(columns={"index": "datetime", "Timestamp": "datetime"})
        # The above line was problematic if index was already named 'Timestamp'
        
        # Ensure the 'Timestamp' column is present and named 'datetime' for SQLite
        df_prepared_for_sqlite = self._prepare_dataframe_for_storage(df.copy()) # Use a copy
        
        # SQLite prefers a simpler column name like 'datetime' for the timestamp
        # So we explicitly rename 'Timestamp' to 'datetime' for SQLite storage
        df_prepared_for_sqlite = df_prepared_for_sqlite.reset_index().rename(columns={'Timestamp': 'datetime'})

        with sqlite3.connect(str(self.db_path)) as conn:
            df_prepared_for_sqlite.to_sql(
                name=table_name.strip('"'),
                con=conn,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )

            conn.execute(f"""
                DELETE FROM {table_name}
                WHERE rowid NOT IN (
                    SELECT MIN(rowid)
                    FROM {table_name}
                    GROUP BY datetime
                )
            """)

    def get_last_timestamp(self, symbol: str, interval: str) -> Optional[datetime]:
        table_name = self.sanitize_table_name(symbol, interval).strip('"')
        with sqlite3.connect(str(self.db_path)) as conn:
            try:
                result = conn.execute(
                    f"SELECT MAX(datetime) FROM {table_name}"
                ).fetchone()[0]
                if result:
                    return pd.to_datetime(result)
            except sqlite3.OperationalError:
                pass

        file_name = self.sanitize_file_name(symbol, interval)
        parquet_path = self.processed_path / f"{file_name}.parquet"
        if parquet_path.exists():
            df = pd.read_parquet(parquet_path)
            # When reading from Parquet, ensure the index is DatetimeIndex if 'Timestamp' column exists
            if 'Timestamp' in df.columns and not isinstance(df.index, pd.DatetimeIndex):
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                df = df.set_index('Timestamp')

            if not df.empty and isinstance(df.index, pd.DatetimeIndex):
                return df.index.max()
        return None

    # fetch_incremental remains the same as its input is df from fetcher
    def fetch_incremental(self, fetcher, symbol: str, interval: str, force_full: bool = False) -> pd.DataFrame:
        last_date = None if force_full else self.get_last_timestamp(symbol, interval)
        # For daily data, if last_date is 2025-07-29, we want to fetch from 2025-07-30.
        # If last_date has a time component (e.g., 2025-07-29 15:30:00), adding a day works.
        # If it's just a date (e.g., 2025-07-29 00:00:00), adding a day will correctly give 2025-07-30 00:00:00.
        start_date = last_date + timedelta(days=1) if last_date else datetime(2000, 1, 1)
        end_date = datetime.now() # Fetch up to current moment
        max_retries = 3

        for attempt in range(max_retries):
            try:
                print(f"Fetching {symbol} {interval} data (attempt {attempt + 1}/{max_retries}) from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
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

    def list_parquet_files(self) -> List[str]:
        """List all .parquet files"""
        if not self.processed_path.exists():
            return []
        return sorted([f.name for f in self.processed_path.glob("*.parquet")])

    def load_parquet_file(self, filename: str) -> pd.DataFrame:
        path = self.processed_path / filename
        if path.exists():
            df = pd.read_parquet(path)
            # Ensure the Timestamp column is the index when loading from Parquet
            if 'Timestamp' in df.columns and not isinstance(df.index, pd.DatetimeIndex):
                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                df = df.set_index('Timestamp').sort_index()
            return df
        return pd.DataFrame()

    def list_tables(self) -> List[str]:
        """List all table names in the database"""
        if not self.db_path.exists():
            return []
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                return sorted([row[0] for row in cursor.fetchall()])
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return []

    def load_table(self, table_name: str) -> pd.DataFrame:
        """Load all data from a specific table"""
        if not self.db_path.exists():
            return pd.DataFrame()
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                df = pd.read_sql_query(f"SELECT * FROM \"{table_name}\"", conn)
                # Ensure 'datetime' from SQLite is converted to 'Timestamp' index for consistency
                if 'datetime' in df.columns:
                    df['datetime'] = pd.to_datetime(df['datetime'])
                    df = df.set_index('datetime').rename_axis('Timestamp').sort_index()
                return df
        except Exception as e:
            print(f"Failed to read from table {table_name}: {e}")
            return pd.DataFrame()


# Test runner
if __name__ == "__main__":
    # Assuming NSEDataFetcher exists and returns a DataFrame with DatetimeIndex
    # For a minimal test without a real fetcher, you could mock it:
    class MockNSEDataFetcher:
        def fetch_data(self, symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
            print(f"Mocking fetch for {symbol} from {start} to {end}")
            # Create some dummy data
            dates = pd.date_range(start=start, end=end, freq='D')
            if dates.empty:
                return pd.DataFrame()
            data = {
                'Open': [100 + i for i in range(len(dates))],
                'High': [105 + i for i in range(len(dates))],
                'Low': [95 + i for i in range(len(dates))],
                'Close': [102 + i for i in range(len(dates))],
                'Volume': [1000 + i * 10 for i in range(len(dates))]
            }
            df = pd.DataFrame(data, index=dates)
            df.index.name = 'Timestamp' # The fetcher should ideally return it like this or with a named index
            return df

    try:
        fetcher = MockNSEDataFetcher() # Use the mock fetcher for testing
        storage = DataStorage()

        print("Testing incremental update (force_full=True for initial fetch)...")
        # Ensure 'Trading.db' and parquet files are cleared for a clean test
        if storage.db_path.exists():
            os.remove(storage.db_path)
        for f in storage.processed_path.glob("*.parquet"):
            os.remove(f)

        test_data_initial = storage.fetch_incremental(fetcher, "TCS", "1d", force_full=True)

        if not test_data_initial.empty:
            print("\nSample data (initial fetch):")
            print(test_data_initial.head())
            print(test_data_initial.tail())
            print(f"Initial data index type: {type(test_data_initial.index)}")
            print(f"Initial data columns: {test_data_initial.columns.tolist()}")

            # Verify Parquet file
            parquet_df = storage.load_parquet_file(storage.sanitize_file_name("TCS", "1d") + ".parquet")
            print(f"\nParquet data head:\n{parquet_df.head()}")
            print(f"Parquet data tail:\n{parquet_df.tail()}")
            print(f"Parquet data index type: {type(parquet_df.index)}")
            print(f"Parquet data columns: {parquet_df.columns.tolist()}") # Should now be Open, High, Low, Close, Volume

            # Verify SQLite table
            table_name = storage.sanitize_table_name("TCS", "1d").strip('"')
            sqlite_df = storage.load_table(table_name)
            print(f"\nSQLite data head:\n{sqlite_df.head()}")
            print(f"SQLite data tail:\n{sqlite_df.tail()}")
            print(f"SQLite data index type: {type(sqlite_df.index)}") # Should be DatetimeIndex
            print(f"SQLite data index name: {sqlite_df.index.name}") # Should be Timestamp
            print(f"SQLite data columns: {sqlite_df.columns.tolist()}") # Should be Open, High, Low, Close, Volume

            print("\nTesting incremental update (subsequent fetch)...")
            time.sleep(1) # Simulate time passing
            test_data_incremental = storage.fetch_incremental(fetcher, "TCS", "1d")

            if not test_data_incremental.empty:
                print("\nSample data (incremental fetch):")
                print(test_data_incremental.head())
                print(f"Incremental data index type: {type(test_data_incremental.index)}")
            else:
                print("\nNo new data fetched in incremental run.")

            # Load full data again to see if it combined correctly
            final_parquet_df = storage.load_parquet_file(storage.sanitize_file_name("TCS", "1d") + ".parquet")
            print(f"\nFinal Parquet data records: {len(final_parquet_df)}")
            print(f"Final Parquet data head:\n{final_parquet_df.head()}")
            print(f"Final Parquet data tail:\n{final_parquet_df.tail()}")

            final_sqlite_df = storage.load_table(table_name)
            print(f"\nFinal SQLite data records: {len(final_sqlite_df)}")
            print(f"Final SQLite data head:\n{final_sqlite_df.head()}")
            print(f"Final SQLite data tail:\n{final_sqlite_df.tail()}")

        else:
            print("\nNo data fetched in initial run.")
    except Exception as e:
        print(f"Critical error during test: {e}")