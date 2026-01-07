"""
Historical Data Manager - Centralized CRUD operations for OHLCV data

This module provides a unified interface for managing historical stock data
across multiple timeframes with proper CRUD operations, metadata tracking,
and efficient storage using both SQLite and Parquet formats.
"""

import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
import logging

from libs.nse_data_fetcher import NSEMasterData
from libs.data_cleaner import validate_data, add_technical_features
from libs.storage import DataStorage


class HistoricalDataManager:
    """
    Manages historical OHLCV data with CRUD operations across multiple timeframes.
    
    Supported timeframes: 1m, 5m, 10m, 15m, 30m, 1h, 1d, 1w, 1M
    """
    
    SUPPORTED_TIMEFRAMES = ['1m', '5m', '10m', '15m', '30m', '1h', '1d', '1w', '1M']
    
    def __init__(self, db_path: Optional[str] = None, parquet_path: Optional[str] = None):
        """
        Initialize the Historical Data Manager.
        
        Args:
            db_path: Path to SQLite database (default: data/trading.db)
            parquet_path: Path to parquet storage directory (default: data/processed)
        """
        self.storage = DataStorage(db_path)
        self.db_path = self.storage.db_path
        self.parquet_path = Path(parquet_path) if parquet_path else self.storage.processed_path
        self.fetcher = NSEMasterData()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize metadata table
        self._init_metadata_table()
    
    def _init_metadata_table(self):
        """Create the OHLCV metadata table if it doesn't exist."""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ohlcv_metadata (
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    first_date TEXT,
                    last_date TEXT,
                    record_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, timeframe)
                )
            """)
            conn.commit()
    
    # ==================== CREATE ====================
    
    def download_symbol_data(
        self,
        symbol: str,
        timeframes: List[str] = ['1d'],
        from_date: str = '1995-01-01',
        to_date: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Download historical data for a symbol across specified timeframes.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', 'TCS')
            timeframes: List of timeframes to download
            from_date: Start date (YYYY-MM-DD format)
            to_date: End date (default: today)
        
        Returns:
            Dictionary mapping timeframe to success status
        """
        symbol = symbol.upper()
        results = {}
        
        if to_date is None:
            to_date = datetime.now().strftime('%Y-%m-%d')
        
        start_dt = datetime.strptime(from_date, '%Y-%m-%d')
        end_dt = datetime.strptime(to_date, '%Y-%m-%d')
        
        self.logger.info(f"Downloading {symbol} data from {from_date} to {to_date}")
        
        # Download symbol master if not already done
        try:
            self.fetcher.download_symbol_master()
        except Exception as e:
            self.logger.warning(f"Symbol master download failed: {e}")
        
        for timeframe in timeframes:
            if timeframe not in self.SUPPORTED_TIMEFRAMES:
                self.logger.error(f"Unsupported timeframe: {timeframe}")
                results[timeframe] = False
                continue
            
            try:
                self.logger.info(f"Fetching {symbol} {timeframe} data...")
                
                # Fetch data from NSE
                df = self.fetcher.get_history(
                    symbol=symbol,
                    exchange="NSE",
                    start=start_dt,
                    end=end_dt,
                    interval=timeframe
                )
                
                if df.empty:
                    self.logger.warning(f"No data received for {symbol} {timeframe}")
                    results[timeframe] = False
                    continue
                
                # Clean and enhance data
                clean_df = validate_data(df)
                enhanced_df = add_technical_features(clean_df)
                
                # Save data
                self._save_ohlcv_data(enhanced_df, symbol, timeframe)
                
                self.logger.info(f"✅ Saved {len(enhanced_df)} records for {symbol} {timeframe}")
                results[timeframe] = True
                
            except Exception as e:
                self.logger.error(f"Failed to download {symbol} {timeframe}: {e}")
                results[timeframe] = False
        
        return results
    
    def bulk_download(
        self,
        symbols: List[str],
        timeframes: List[str] = ['1d'],
        from_date: str = '1995-01-01',
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Dict[str, bool]]:
        """
        Download data for multiple symbols.
        
        Args:
            symbols: List of stock symbols
            timeframes: List of timeframes to download
            from_date: Start date
            progress_callback: Optional callback function(symbol, timeframe, success)
        
        Returns:
            Nested dictionary: {symbol: {timeframe: success}}
        """
        results = {}
        total = len(symbols) * len(timeframes)
        current = 0
        
        for symbol in symbols:
            symbol_results = self.download_symbol_data(symbol, timeframes, from_date)
            results[symbol] = symbol_results
            
            for timeframe, success in symbol_results.items():
                current += 1
                if progress_callback:
                    progress_callback(symbol, timeframe, success, current, total)
        
        return results
    
    # ==================== READ ====================
    
    def get_symbol_data(
        self,
        symbol: str,
        timeframe: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve OHLCV data for a symbol and timeframe.
        
        Args:
            symbol: Stock symbol
            timeframe: Data timeframe
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
        
        Returns:
            DataFrame with OHLCV data
        """
        symbol = symbol.upper()
        
        # Try to load from parquet first (faster for large datasets)
        parquet_file = self.parquet_path / symbol / f"{timeframe}.parquet"
        
        if parquet_file.exists():
            df = pd.read_parquet(parquet_file)
            
            # Apply date filters if provided
            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]
            
            return df
        
        # Fallback to SQLite - use correct table naming: {symbol}_{timeframe}_ohlc
        table_name = f"{symbol.lower()}_{timeframe}_ohlc"
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Check if table exists
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    self.logger.warning(f"Table {table_name} does not exist")
                    return pd.DataFrame()
                
                query = f"SELECT * FROM {table_name}"
                conditions = []
                
                if start_date:
                    conditions.append(f"datetime >= '{start_date}'")
                if end_date:
                    conditions.append(f"datetime <= '{end_date}'")
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY datetime"
                
                df = pd.read_sql_query(query, conn, index_col='datetime', parse_dates=['datetime'])
                return df
        except Exception as e:
            self.logger.error(f"Failed to load {symbol} {timeframe}: {e}")
            return pd.DataFrame()
    
    def get_available_symbols(self) -> List[str]:
        """Get list of all symbols with downloaded data."""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute("SELECT DISTINCT symbol FROM ohlcv_metadata ORDER BY symbol")
            return [row[0] for row in cursor.fetchall()]
    
    def get_available_timeframes(self, symbol: str) -> List[str]:
        """Get list of available timeframes for a symbol."""
        symbol = symbol.upper()
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT timeframe FROM ohlcv_metadata WHERE symbol = ? ORDER BY timeframe",
                (symbol,)
            )
            return [row[0] for row in cursor.fetchall()]
    
    def get_data_info(self, symbol: str) -> Dict[str, Dict]:
        """
        Get metadata information for a symbol across all timeframes.
        
        Returns:
            Dictionary mapping timeframe to metadata (date_range, record_count, last_updated)
        """
        symbol = symbol.upper()
        info = {}
        
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.execute("""
                SELECT timeframe, first_date, last_date, record_count, last_updated
                FROM ohlcv_metadata
                WHERE symbol = ?
            """, (symbol,))
            
            for row in cursor.fetchall():
                timeframe, first_date, last_date, record_count, last_updated = row
                info[timeframe] = {
                    'first_date': first_date,
                    'last_date': last_date,
                    'record_count': record_count,
                    'last_updated': last_updated
                }
        
        return info
    
    # ==================== UPDATE ====================
    
    def update_symbol_data(
        self,
        symbol: str,
        timeframes: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Update symbol data by fetching the latest records.
        
        Args:
            symbol: Stock symbol
            timeframes: List of timeframes to update (default: all available)
        
        Returns:
            Dictionary mapping timeframe to success status
        """
        symbol = symbol.upper()
        
        if timeframes is None:
            timeframes = self.get_available_timeframes(symbol)
        
        if not timeframes:
            self.logger.warning(f"No timeframes found for {symbol}")
            return {}
        
        results = {}
        
        for timeframe in timeframes:
            try:
                # Get last date from metadata
                info = self.get_data_info(symbol)
                if timeframe not in info:
                    self.logger.warning(f"No existing data for {symbol} {timeframe}")
                    results[timeframe] = False
                    continue
                
                last_date = info[timeframe]['last_date']
                from_date = (datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                
                # Download new data
                result = self.download_symbol_data(symbol, [timeframe], from_date)
                results[timeframe] = result.get(timeframe, False)
                
            except Exception as e:
                self.logger.error(f"Failed to update {symbol} {timeframe}: {e}")
                results[timeframe] = False
        
        return results
    
    # ==================== DELETE ====================
    
    def delete_symbol_data(
        self,
        symbol: str,
        timeframe: Optional[str] = None
    ) -> bool:
        """
        Delete data for a symbol.
        
        Args:
            symbol: Stock symbol
            timeframe: Specific timeframe to delete (default: all timeframes)
        
        Returns:
            Success status
        """
        symbol = symbol.upper()
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                if timeframe:
                    # Delete specific timeframe
                    conn.execute(
                        "DELETE FROM ohlcv_metadata WHERE symbol = ? AND timeframe = ?",
                        (symbol, timeframe)
                    )
                    
                    # Delete parquet file
                    parquet_file = self.parquet_path / symbol / f"{timeframe}.parquet"
                    if parquet_file.exists():
                        parquet_file.unlink()
                    
                    self.logger.info(f"Deleted {symbol} {timeframe} data")
                else:
                    # Delete all timeframes
                    conn.execute("DELETE FROM ohlcv_metadata WHERE symbol = ?", (symbol,))
                    
                    # Delete parquet directory
                    symbol_dir = self.parquet_path / symbol
                    if symbol_dir.exists():
                        import shutil
                        shutil.rmtree(symbol_dir)
                    
                    self.logger.info(f"Deleted all data for {symbol}")
                
                conn.commit()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to delete {symbol} data: {e}")
            return False
    
    # ==================== PRIVATE METHODS ====================
    
    def _save_ohlcv_data(self, df: pd.DataFrame, symbol: str, timeframe: str):
        """Save OHLCV data and update metadata."""
        # Save to parquet
        self.storage.save_to_parquet(df, symbol, timeframe)
        
        # Save to SQLite (for quick queries)
        self.storage.update_sqlite(df, symbol, timeframe)
        
        # Update metadata
        first_date = df.index.min().strftime('%Y-%m-%d')
        last_date = df.index.max().strftime('%Y-%m-%d')
        record_count = len(df)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO ohlcv_metadata 
                (symbol, timeframe, first_date, last_date, record_count, last_updated)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (symbol, timeframe, first_date, last_date, record_count))
            conn.commit()
