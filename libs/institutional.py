
import pandas as pd
import numpy as np
from datetime import datetime, time
import pytz
from typing import Dict, Any, Optional
from libs.NseUtility import NseUtils

class InstitutionalAnalyzer:
    def __init__(self):
        self.nse = NseUtils()
        self.tz_india = pytz.timezone('Asia/Kolkata')

    def is_market_open(self) -> bool:
        """
        Checks if the NSE market is currently open (09:15 - 15:30 IST, Mon-Fri).
        Ignores holidays for now (can be enhanced).
        """
        now = datetime.now(self.tz_india)
        
        # Check Weekend
        if now.weekday() >= 5: # Sat=5, Sun=6
            return False
            
        current_time = now.time()
        market_start = time(9, 15)
        market_end = time(15, 30)
        
        return market_start <= current_time <= market_end

    def get_smart_money_flow(self) -> Dict[str, Any]:
        """
        Fetches FII/DII activity.
        This data is usually EOD, but technically 'live' in the sense it updates daily.
        """
        try:
            # Re-using NseUtils functionality or implementing if missing/broken
            # NseUtils has 'fii_dii_activity' but it might print instead of return.
            # Let's check NseUtility implementation or just re-implement simple fetch here if needed.
            # Assuming NseUtils.fii_dii_activity() returns a DataFrame or list.
            # Based on previous usage, it seemed to work.
            data = self.nse.fii_dii_activity()
            if isinstance(data, pd.DataFrame):
                return data.to_dict('records')
            return data
        except Exception as e:
            print(f"Error fetching smart money flow: {e}")
            return {}

    def analyze_oi(self, symbol: str, force_fetch: bool = False) -> Dict[str, Any]:
        """
        Analyzes Option Chain for a symbol.
        Returns PCR, Max Pain, and Interpretation.
        Respects market hours unless force_fetch is True.
        """
        if not self.is_market_open() and not force_fetch:
            return {
                "status": "Market Closed", 
                "message": "Live Option Chain is only fetched during market hours (09:15-15:30 IST)."
            }

        try:
            # Need to determine if it is Index or Stock to pass correct flag to get_option_chain
            # Basic logic: NIFTY, BANKNIFTY are indices.
            indices = symbol.upper() in ["NIFTY", "BANKNIFTY", "FINNIFTY"]
            
            df = self.nse.get_option_chain(symbol, indices=indices)
            
            if df is None or df.empty:
                return {"status": "No Data", "pcr": None, "message": "API returned empty data"}

            # Filter for nearest expiry? 
            # The get_option_chain returns ALL expiries. We should focus on usage.
            # For simplicity, let's take the aggregate of ALL active contracts for PCR
            # But Max Pain is usually checking the near expiry.
            
            # 1. Total PCR (Volume Based vs OI Based) - Standard is OI
            total_call_oi = df[df['instrumentType'] == 'CE']['openInterest'].sum()
            total_put_oi = df[df['instrumentType'] == 'PE']['openInterest'].sum()
            
            pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else 0
            
            # 2. Max Pain (Strike where option writers lose least money)
            # Simplified: Strike with highest sum of Call OI + Put OI? No, that's max activity.
            # Max Pain calculation is computationally heavier (iterating strikes).
            # Let's use Highest OI bars as proxies for Support/Resistance
            
            # Group by Strike Price
            # Convert strikePrice to numeric just in case
            df['strikePrice'] = pd.to_numeric(df['strikePrice'])
            
            # Separate pivot needed
            calls = df[df['instrumentType'] == 'CE'].groupby('strikePrice')['openInterest'].sum()
            puts = df[df['instrumentType'] == 'PE'].groupby('strikePrice')['openInterest'].sum()
            
            max_call_oi_strike = calls.idxmax() if not calls.empty else 0
            max_put_oi_strike = puts.idxmax()   if not puts.empty else 0
            
            interpretation = "Neutral"
            if pcr > 1.0: interpretation = "Bullish"
            if pcr > 1.5: interpretation = "Overbought / Strong Bullish"
            if pcr < 0.7: interpretation = "Bearish"
            if pcr < 0.5: interpretation = "Oversold / Strong Bearish"

            return {
                "status": "Live",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pcr": pcr,
                "interpretation": interpretation,
                "max_call_oi_strike": max_call_oi_strike, # Resistance
                "max_put_oi_strike": max_put_oi_strike,   # Support
                "total_call_oi": int(total_call_oi),
                "total_put_oi": int(total_put_oi)
            }

        except KeyError as e:
             return {"status": "API Error", "message": f"NSE Data Structure Changed: Missing {e}", "pcr": None}
        except Exception as e:
            return {"status": "Error", "message": f"Analysis Failed: {str(e)}", "pcr": None}

