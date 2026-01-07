
import pandas as pd
from datetime import datetime, timedelta
import logging
import yaml
from pathlib import Path
from libs.nse_data_fetcher import NSEMasterData

logger = logging.getLogger(__name__)

class MacroAnalyzer:
    """Analyzes Sector Performance using Native NSE Data (via Charting API)"""
    
    def __init__(self):
        self.fetcher = NSEMasterData()
        # Pre-download master data for symbols
        self.fetcher.download_symbol_master()
        
        self.config_path = Path(__file__).resolve().parent.parent / "config" / "indices.yaml"
        self.indices = self._load_indices()

    def _load_indices(self):
        try:
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
                return {item['name']: item['symbol'] for item in data.get('indices', [])}
        except Exception as e:
            logger.error(f"Failed to load indices config: {e}")
            return {}

    def fetch_sector_performance(self):
        """Fetches last 30 days of data for all sectors."""
        perf = {}
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=45) 

        for name, symbol in self.indices.items():
            try:
                # Use NSEMasterData to get history
                # It handles symbol lookup internally via self.search if needed, 
                # but get_history calls search.
                # symbol names in yaml are like "NIFTY 50" which works with search/match=False
                
                df = self.fetcher.get_history(symbol=symbol, start=start_date, end=end_date)
                
                if df is not None and not df.empty:
                    # df index is Timestamp (DatetimeIndex), columns: Open, High, Low, Close, Volume
                    series = df['Close'].astype(float)
                    
                    if len(series) >= 2:
                        last = series.iloc[-1]
                        prev = series.iloc[-2]
                        change = ((last - prev) / prev) * 100
                        
                        # Trend (Price > SMA 10)
                        sma_10 = series.tail(10).mean()
                        trend = "Up" if last > sma_10 else "Down"
                        
                        perf[name] = {
                            "symbol": symbol,
                            "last_price": float(last),
                            "change_pct": float(change),
                            "trend": trend,
                            "history": series.tail(30).to_dict() # Serialize for charts
                        }
            except Exception as e:
                print(f"Failed to fetch macro data for {name}: {e}")
                continue
                
        return perf

    def get_market_breadth(self):
        """Approximate breadth from sector movement."""
        perf = self.fetch_sector_performance()
        if not perf:
            return {"advance": 0, "decline": 0, "ratio": 0}
        
        adv = sum(1 for s in perf.values() if s['change_pct'] > 0)
        dec = sum(1 for s in perf.values() if s['change_pct'] <= 0)
        
        ratio = adv/dec if dec > 0 else adv
        return {"advance": adv, "decline": dec, "ratio": ratio}
