
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

class DealAnalyzer:
    """
    Analyzes Bulk and Block deals to identify 'Big Money' sentiment.
    Key Concept: 'Institutional Clumping' - Multiple distinct institutions 
    buying the same stock in a short window.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def _table_exists(self, table_name: str) -> bool:
        """Checks if a table exists in the database."""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                return cursor.fetchone() is not None
        except Exception:
            return False

    def get_clumping_signals(self, days: int = 5) -> pd.DataFrame:
        """
        Identifies symbols with high institutional buying concentration.
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Load Bulk Deals
                bulk_df = pd.DataFrame()
                if self._table_exists("market_bulk_deals"):
                    bulk_query = f"SELECT * FROM market_bulk_deals WHERE BD_DT_DATE >= '{since_date}'"
                    bulk_df = pd.read_sql_query(bulk_query, conn)
                
                # Load Block Deals
                block_df = pd.DataFrame()
                if self._table_exists("market_block_deals"):
                    block_query = f"SELECT * FROM market_block_deals WHERE date >= '{since_date}'"
                    block_df = pd.read_sql_query(block_query, conn)
                
            if bulk_df.empty and block_df.empty:
                return pd.DataFrame()

            # Normalize column names (NSE uses BD_ and BLK_ prefixes)
            if not bulk_df.empty:
                bulk_df = bulk_df.rename(columns={
                    'BD_DT_DATE': 'date',
                    'BD_SYMBOL': 'symbol',
                    'BD_CLIENT_NAME': 'clientName',
                    'BD_BUY_SELL': 'type',
                    'BD_QTY_TRD': 'quantity',
                    'BD_TP_WATP': 'price'
                })
            if not block_df.empty:
                block_df = block_df.rename(columns={
                    'BLK_DT_DATE': 'date',
                    'BLK_SYMBOL': 'symbol',
                    'BLK_CLIENT_NAME': 'clientName',
                    'BLK_BUY_SELL': 'type',
                    'BLK_QTY_TRD': 'quantity',
                    'BLK_TP_WATP': 'price'
                })

            # Consolidate deals
            all_deals = pd.concat([bulk_df, block_df], ignore_index=True)
            
            # Filter for BUY deals (usually 'BUY' or 'B' in type)
            buy_deals = all_deals[all_deals['type'].str.contains('BUY|B', case=False, na=False)]
            
            if buy_deals.empty:
                return pd.DataFrame()

            # Aggregate by symbol
            clumping = buy_deals.groupby('symbol').agg({
                'clientName': 'nunique',  # Count distinct buyers
                'quantity': 'sum',
                'date': 'max'
            }).rename(columns={
                'clientName': 'unique_buyers',
                'quantity': 'total_buy_qty',
                'date': 'latest_deal'
            })
            
            # Calculate a signal strength (e.g., unique_buyers * log(quantity))
            # For now, just return companies with more than 1 unique buyer or very high quantity
            signals = clumping[clumping['unique_buyers'] >= 1].sort_values('unique_buyers', ascending=False)
            
            return signals

        except Exception as e:
            print(f"Error in DealAnalyzer: {e}")
            return pd.DataFrame()

    def get_symbol_sentiment(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Provides detailed deal sentiment for a specific symbol.
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        symbol = symbol.upper()

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                df = pd.DataFrame()
                if self._table_exists("market_bulk_deals"):
                    query = f"SELECT * FROM market_bulk_deals WHERE BD_SYMBOL = '{symbol}' AND BD_DT_DATE >= '{since_date}'"
                    df = pd.read_sql_query(query, conn)
                
                block_df = pd.DataFrame()
                if self._table_exists("market_block_deals"):
                    block_query = f"SELECT * FROM market_block_deals WHERE symbol = '{symbol}' AND date >= '{since_date}'"
                    block_df = pd.read_sql_query(block_query, conn)
                
                df = pd.concat([df, block_df], ignore_index=True)

            if df.empty:
                return {"score": 0, "deals_count": 0, "net_sentiment": "Neutral"}

            # Calculate net sentiment
            buys = df[df['type'].str.contains('BUY|B', case=False, na=False)]['quantity'].sum()
            sells = df[df['type'].str.contains('SELL|S', case=False, na=False)]['quantity'].sum()
            
            net_qty = buys - sells
            unique_players = df['clientName'].nunique()
            
            score = 0
            if net_qty > 0: score += 1
            if unique_players > 2: score += 1
            if (buys / (sells + 1)) > 2: score += 1 # Buy ratio > 2
            
            sentiment = "Bullish" if net_qty > 0 else "Bearish"
            if unique_players >= 3 and net_qty > 0:
                sentiment = "Strongly Bullish (Clumping)"

            return {
                "score": score,
                "deals_count": len(df),
                "net_sentiment": sentiment,
                "unique_players": unique_players,
                "net_qty": net_qty
            }

        except Exception as e:
            print(f"Error fetching sentiment for {symbol}: {e}")
            return {"score": 0, "deals_count": 0, "net_sentiment": "Error"}

    def get_short_selling_pressure(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Analyze short selling pressure for a specific symbol.
        Returns pressure level and metrics.
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        symbol = symbol.upper()

        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                if not self._table_exists("market_short_selling"):
                    return {"pressure": "Unknown", "total_qty": 0, "unique_sellers": 0}
                
                query = f"SELECT * FROM market_short_selling WHERE symbol = '{symbol}' AND date >= '{since_date}'"
                df = pd.read_sql_query(query, conn)
                
                if df.empty:
                    return {"pressure": "None", "total_qty": 0, "unique_sellers": 0}
                
                # Normalize column names
                df = df.rename(columns={
                    'SS_DATE': 'date',
                    'SS_SYMBOL': 'symbol',
                    'SS_NAME': 'clientName',
                    'SS_QTY': 'quantity'
                })
                
                total_qty = df['quantity'].sum()
                unique_sellers = df['clientName'].nunique()
                
                # Determine pressure level
                if total_qty > 100000:
                    pressure = "High"
                elif total_qty > 50000:
                    pressure = "Medium"
                elif total_qty > 0:
                    pressure = "Low"
                else:
                    pressure = "None"
                
                return {
                    "pressure": pressure,
                    "total_qty": int(total_qty),
                    "unique_sellers": unique_sellers,
                    "recent_count": len(df)
                }
        
        except Exception as e:
            print(f"Error fetching short selling for {symbol}: {e}")
            return {"pressure": "Error", "total_qty": 0, "unique_sellers": 0}
