
import pandas as pd
import logging
from libs.fundamentals import FundamentalFetcher
from libs.institutional import InstitutionalAnalyzer
from libs.macro import MacroAnalyzer
from libs.storage import DataStorage
from libs.deal_analyzer import DealAnalyzer

class QuadAnalyzer:
    """
    The Core Engine of Quad Analysis System.
    Aggregates:
    1. Fundamentals (Quality & Growth)
    2. Technicals (Trend & Momentum)
    3. Institutional (Smart Money)
    4. Macro (Sector & Environment)
    """
    
    SECTOR_MAP = {
        "Banks": "NIFTY BANK",
        "Bank": "NIFTY BANK",
        "IT": "NIFTY IT",
        "Software": "NIFTY IT",
        "Auto": "NIFTY AUTO",
        "Automobiles": "NIFTY AUTO",
        "Pharma": "NIFTY PHARMA",
        "FMCG": "NIFTY FMCG",
        "Metal": "NIFTY METAL",
        "Realty": "NIFTY REALTY",
        "Energy": "NIFTY ENERGY",
    }

    def __init__(self):
        self.fundamental = FundamentalFetcher()
        self.institutional = InstitutionalAnalyzer()
        self.macro = MacroAnalyzer()
        self.storage = DataStorage()
        self.deals = DealAnalyzer(self.storage.db_path)
        
        # Cache macro data on init to avoid repeated calls
        self.sector_data = self.macro.fetch_sector_performance()
        
    def get_report_card(self, symbol: str):
        """Generates a full report card for a symbol."""
        report = {
            "symbol": symbol,
            "quad_score": 0,
            "pillars": {},
            "details": {}
        }
        
        # 1. Fundamental Analysis
        fund_data = self.fundamental.fetch_data(symbol)
        fund_score, fund_details = self._score_fundamental(fund_data)
        
        # 2. Technical Analysis
        # Load latest daily data
        price_df = self.storage.load_data(symbol, '1d')
        tech_score, tech_details = self._score_technical(price_df)
        
        # 3. Institutional Analysis
        inst_data = self.institutional.analyze_oi(symbol)
        deal_data = self.deals.get_symbol_sentiment(symbol)
        inst_score, inst_details = self._score_institutional(inst_data, deal_data)
        
        # 4. Macro Analysis (Sector Relative Strength)
        sector_name = self._map_sector(fund_data.get('metadata', {}).get('sector', ''))
        macro_score, macro_details = self._score_macro(symbol, price_df, sector_name)
        
        # Consolidate
        report["pillars"] = {
            "Fundamental": fund_score,
            "Technical": tech_score,
            "Institutional": inst_score,
            "Macro": macro_score
        }
        report["quad_score"] = round((fund_score + tech_score + inst_score + macro_score) / 4, 1)
        report["details"] = {
            "fundamental": fund_details,
            "technical": tech_details,
            "institutional": inst_details,
            "macro": macro_details,
            "raw_fundamental": fund_data, # For display
            "big_money": deal_data # New signals
        }
        
        return report

    def _score_fundamental(self, data):
        score = 5 # Start neutral
        reasons = []
        metrics = data.get("key_metrics", {})
        
        # ROE
        roe = metrics.get('roe', 0)
        if roe > 20: score += 2; reasons.append("Excellent ROE (>20%)")
        elif roe > 15: score += 1; reasons.append("Good ROE (>15%)")
        elif roe < 10: score -= 1; reasons.append("Low ROE (<10%)")
        
        # PE (Crude check, ideally compare with industry)
        pe = metrics.get('pe_ratio', 0)
        if 0 < pe < 20: score += 1; reasons.append("Attractive Valuation (PE<20)")
        elif pe > 50: score -= 1; reasons.append("Expensive (PE>50)")
        
        # Growth (Net Profit recent quarter vs previous)
        qr = data.get("quarterly_results", {})
        if qr and "net_profit" in qr and len(qr["net_profit"]) > 4:
            latest = qr["net_profit"][-1] or 0
            yoy = qr["net_profit"][-5] or 0 # Compare with same quarter last year
            
            if latest > yoy * 1.2: score += 2; reasons.append("Strong Profit Growth (>20% YoY)")
            elif latest > yoy: score += 1; reasons.append("Positive Growth")
            elif latest < yoy: score -= 1; reasons.append("Negative Growth")
            
        return min(max(score, 0), 10), reasons

    def _score_technical(self, df):
        if df is None or df.empty:
            return 0, ["No Price Data"]
            
        score = 5
        reasons = []
        latest = df.iloc[-1]
        
        # Trend
        if 'SMA_50' in latest and 'SMA_200' in latest:
            if latest['Close'] > latest['SMA_50']: score += 1; reasons.append("Above SMA 50")
            if latest['SMA_50'] > latest['SMA_200']: score += 2; reasons.append("Golden Cross Trend")
            if latest['Close'] < latest['SMA_200']: score -= 2; reasons.append("Below Long Term Trend")
            
        # Momentum
        if 'RSI_14' in latest:
            rsi = latest['RSI_14']
            if 50 < rsi < 70: score += 1; reasons.append("Bullish Momentum")
            if rsi > 75: score -= 1; reasons.append("Overbought RSI")
            if rsi < 30: score += 1; reasons.append("Oversold Bounce Potential")
            
        return min(max(score, 0), 10), reasons

    def _score_institutional(self, data, deals=None):
        score = 5
        reasons = []
        
        # 1. Options PCR (Short-term sentiment)
        if data.get('status') == 'Live':
            pcr = data.get('pcr', 0)
            if pcr > 1: score += 1; reasons.append("Bullish PCR (>1)")
            if pcr < 0.6: score -= 1; reasons.append("Bearish PCR (<0.6)")
        else:
            reasons.append("No Live Derivatives Data")
            
        # 2. Big Money Deals (Medium-term commitment)
        if deals:
            deal_score = deals.get("score", 0)
            sentiment = deals.get("net_sentiment", "Neutral")
            
            if "Strongly Bullish" in sentiment:
                score += 2
                reasons.append(f"Institutional Clumping Detected ({deals.get('unique_players')} players)")
            elif "Bullish" in sentiment:
                score += 1
                reasons.append("Net Bulk/Block Buying Detected")
            elif "Bearish" in sentiment:
                score -= 1
                reasons.append("Net Bulk/Block Selling Detected")
        
        return min(max(score, 0), 10), reasons

    def _score_macro(self, symbol, df, sector_name):
        score = 5
        reasons = []
        
        if sector_name and sector_name in self.sector_data:
            sec_perf = self.sector_data[sector_name]
            change = sec_perf.get('change_pct', 0)
            
            if change > 0: score += 1; reasons.append(f"{sector_name} Trending Up")
            else: score -= 1; reasons.append(f"{sector_name} Weak")
            
            # Relative Strength: Stock vs Sector
            if df is not None and not df.empty:
                last_row = df.iloc[-1]
                prev_row = df.iloc[-2]
                stock_chg = ((last_row['Close'] - prev_row['Close']) / prev_row['Close']) * 100
                
                if stock_chg > change: score += 2; reasons.append("Outperforming Sector")
                else: score -= 1; reasons.append("Underperforming Sector")
                
        else:
            reasons.append(f"Sector '{sector_name}' Not Tracked")
            
        return min(max(score, 0), 10), reasons

    def _map_sector(self, raw_sector):
        # Very simple fuzzy map
        for key, val in self.SECTOR_MAP.items():
            if key.lower() in raw_sector.lower():
                return val
        return None
