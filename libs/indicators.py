# libs/indicators.py - COMPLETE VERSION
"""
Professional Technical Indicators using TA-Lib
70+ indicators with error handling
"""

import talib as ta
import pandas as pd
import numpy as np


class TechnicalIndicators:
    """Comprehensive TA-Lib indicator suite with error handling"""
    
    def __init__(self, df):
        self.df = df.copy()
        self._validate_and_prepare()
    
    def _validate_and_prepare(self):
        """Validate and prepare data for TA-Lib"""
        required = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        
        # Convert to float64 (TA-Lib requirement)
        self.open = self.df['Open'].astype(np.float64).values
        self.high = self.df['High'].astype(np.float64).values
        self.low = self.df['Low'].astype(np.float64).values
        self.close = self.df['Close'].astype(np.float64).values
        self.volume = self.df['Volume'].astype(np.float64).values
        
        # Replace zero/negative volumes with NaN
        self.volume = np.where(self.volume <= 0, np.nan, self.volume)
    
    def add_overlap_studies(self):
        """Moving averages and trend indicators"""
        
        # Simple Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            self.df[f'SMA_{period}'] = ta.SMA(self.close, timeperiod=period)
        
        # Exponential Moving Averages
        for period in [9, 12, 20, 26, 50, 200]:
            self.df[f'EMA_{period}'] = ta.EMA(self.close, timeperiod=period)
        
        # Weighted Moving Average
        self.df['WMA_20'] = ta.WMA(self.close, timeperiod=20)
        self.df['WMA_50'] = ta.WMA(self.close, timeperiod=50)
        
        # Double Exponential Moving Average
        self.df['DEMA_20'] = ta.DEMA(self.close, timeperiod=20)
        
        # Triple Exponential Moving Average
        self.df['TEMA_20'] = ta.TEMA(self.close, timeperiod=20)
        
        # Triangular Moving Average
        self.df['TRIMA_20'] = ta.TRIMA(self.close, timeperiod=20)
        
        # Kaufman Adaptive Moving Average
        self.df['KAMA_20'] = ta.KAMA(self.close, timeperiod=20)
        
        # MESA Adaptive Moving Average
        self.df['MAMA'], self.df['FAMA'] = ta.MAMA(self.close)
        
        # Triple Exponential Moving Average (T3)
        self.df['T3_20'] = ta.T3(self.close, timeperiod=20)
        
        # Bollinger Bands
        self.df['BB_UPPER'], self.df['BB_MIDDLE'], self.df['BB_LOWER'] = ta.BBANDS(
            self.close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )
        
        # Parabolic SAR
        self.df['SAR'] = ta.SAR(self.high, self.low)
        
        # Hilbert Transform - Instantaneous Trendline
        self.df['HT_TRENDLINE'] = ta.HT_TRENDLINE(self.close)
        
        return self
    
    def add_momentum_indicators(self):
        """Oscillators and momentum indicators"""
        
        # RSI
        for period in [7, 14, 21]:
            self.df[f'RSI_{period}'] = ta.RSI(self.close, timeperiod=period)
        
        # MACD
        self.df['MACD'], self.df['MACD_SIGNAL'], self.df['MACD_HIST'] = ta.MACD(
            self.close, fastperiod=12, slowperiod=26, signalperiod=9
        )
        
        # Stochastic
        self.df['STOCH_K'], self.df['STOCH_D'] = ta.STOCH(
            self.high, self.low, self.close,
            fastk_period=14, slowk_period=3, slowd_period=3
        )
        
        # Stochastic RSI
        self.df['STOCHRSI_K'], self.df['STOCHRSI_D'] = ta.STOCHRSI(
            self.close, timeperiod=14, fastk_period=5, fastd_period=3
        )
        
        # Williams %R
        self.df['WILLR_14'] = ta.WILLR(self.high, self.low, self.close, timeperiod=14)
        
        # Commodity Channel Index
        self.df['CCI_14'] = ta.CCI(self.high, self.low, self.close, timeperiod=14)
        self.df['CCI_20'] = ta.CCI(self.high, self.low, self.close, timeperiod=20)
        
        # Rate of Change
        for period in [10, 20]:
            self.df[f'ROC_{period}'] = ta.ROC(self.close, timeperiod=period)
        
        # Momentum
        self.df['MOM_10'] = ta.MOM(self.close, timeperiod=10)
        
        # ADX
        self.df['ADX_14'] = ta.ADX(self.high, self.low, self.close, timeperiod=14)
        self.df['PLUS_DI'] = ta.PLUS_DI(self.high, self.low, self.close, timeperiod=14)
        self.df['MINUS_DI'] = ta.MINUS_DI(self.high, self.low, self.close, timeperiod=14)
        
        # Aroon
        self.df['AROON_DOWN'], self.df['AROON_UP'] = ta.AROON(self.high, self.low, timeperiod=14)
        self.df['AROONOSC'] = ta.AROONOSC(self.high, self.low, timeperiod=14)
        
        # Balance of Power
        self.df['BOP'] = ta.BOP(self.open, self.high, self.low, self.close)
        
        # Ultimate Oscillator
        self.df['ULTOSC'] = ta.ULTOSC(self.high, self.low, self.close)
        
        # Money Flow Index - WITH ERROR HANDLING
        if not np.all(np.isnan(self.volume)):
            try:
                self.df['MFI'] = ta.MFI(self.high, self.low, self.close, self.volume, timeperiod=14)
            except:
                print("  ⚠️  MFI skipped (volume data issue)")
                self.df['MFI'] = np.nan
        else:
            self.df['MFI'] = np.nan
        
        # PPO
        self.df['PPO'] = ta.PPO(self.close, fastperiod=12, slowperiod=26)
        
        # TRIX
        self.df['TRIX'] = ta.TRIX(self.close, timeperiod=30)
        
        return self
    
    def add_volume_indicators(self):
        """Volume-based indicators"""
        
        # Only add volume indicators if we have valid volume data
        if not np.all(np.isnan(self.volume)):
            # On Balance Volume
            self.df['OBV'] = ta.OBV(self.close, self.volume)
            
            # Accumulation/Distribution
            self.df['AD'] = ta.AD(self.high, self.low, self.close, self.volume)
            
            # AD Oscillator
            self.df['ADOSC'] = ta.ADOSC(
                self.high, self.low, self.close, self.volume,
                fastperiod=3, slowperiod=10
            )
            
            # Volume Moving Averages
            for period in [10, 20, 50]:
                self.df[f'VOLUME_SMA_{period}'] = ta.SMA(self.volume, timeperiod=period)
        else:
            print("  ⚠️  Volume indicators skipped (no valid volume data)")
            self.df['OBV'] = np.nan
            self.df['AD'] = np.nan
            self.df['ADOSC'] = np.nan
        
        return self
    
    def add_volatility_indicators(self):
        """Volatility and range indicators"""
        
        # Average True Range
        for period in [7, 14, 21]:
            self.df[f'ATR_{period}'] = ta.ATR(self.high, self.low, self.close, timeperiod=period)
        
        # Normalized ATR
        self.df['NATR_14'] = ta.NATR(self.high, self.low, self.close, timeperiod=14)
        
        # Standard Deviation
        for period in [10, 20]:
            self.df[f'STDDEV_{period}'] = ta.STDDEV(self.close, timeperiod=period)
        
        return self
    
    def add_pattern_recognition(self):
        """Candlestick pattern recognition"""
        
        # Major patterns
        patterns = {
            'CDL_DOJI': ta.CDLDOJI,
            'CDL_HAMMER': ta.CDLHAMMER,
            'CDL_SHOOTINGSTAR': ta.CDLSHOOTINGSTAR,
            'CDL_ENGULFING': ta.CDLENGULFING,
            'CDL_MORNINGSTAR': ta.CDLMORNINGSTAR,
            'CDL_EVENINGSTAR': ta.CDLEVENINGSTAR,
        }
        
        for name, func in patterns.items():
            try:
                self.df[name] = func(self.open, self.high, self.low, self.close)
            except:
                self.df[name] = 0
        
        return self
    
    def add_all_indicators(self):
        """Add all indicators with error handling"""
        print("🚀 Adding TA-Lib indicators...")
        
        print("  ✓ Overlap Studies (trend indicators)")
        self.add_overlap_studies()
        
        print("  ✓ Momentum Indicators")
        self.add_momentum_indicators()
        
        print("  ✓ Volume Indicators")
        self.add_volume_indicators()
        
        print("  ✓ Volatility Indicators")
        self.add_volatility_indicators()
        
        print("  ✓ Pattern Recognition")
        self.add_pattern_recognition()
        
        total = len([col for col in self.df.columns 
                    if col not in ['Open', 'High', 'Low', 'Close', 'Volume']])
        print(f"\n✅ Total indicators: {total}")
        
        return self.df
    
    def get_indicator_list(self):
        """Get list of all indicators by category"""
        categories = {
            'Overlap (Trend)': [col for col in self.df.columns if any(x in col for x in 
                ['SMA', 'EMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'KAMA', 'MAMA', 'FAMA', 
                 'T3', 'BB_', 'SAR', 'HT_TRENDLINE'])],
            
            'Momentum': [col for col in self.df.columns if any(x in col for x in 
                ['RSI', 'MACD', 'STOCH', 'WILLR', 'CCI', 'ROC', 'MOM', 'ADX', 'PLUS_DI', 
                 'MINUS_DI', 'AROON', 'BOP', 'ULTOSC', 'MFI', 'PPO', 'TRIX'])],
            
            'Volume': [col for col in self.df.columns if any(x in col for x in 
                ['OBV', 'AD', 'ADOSC', 'VOLUME_'])],
            
            'Volatility': [col for col in self.df.columns if any(x in col for x in 
                ['ATR', 'NATR', 'STDDEV'])],
            
            'Patterns': [col for col in self.df.columns if col.startswith('CDL_')]
        }
        
        return categories


# Helper functions
def calculate_all_indicators(df):
    """Add all indicators to dataframe"""
    indicators = TechnicalIndicators(df)
    return indicators.add_all_indicators()


def calculate_essential_indicators(df):
    """Add only essential indicators (faster)"""
    import talib as ta
    
    df = df.copy()
    close = df['Close'].astype(np.float64).values
    high = df['High'].astype(np.float64).values
    low = df['Low'].astype(np.float64).values
    volume = df['Volume'].astype(np.float64).values
    
    # Trend
    for period in [20, 50, 200]:
        df[f'SMA_{period}'] = ta.SMA(close, timeperiod=period)
    for period in [12, 26]:
        df[f'EMA_{period}'] = ta.EMA(close, timeperiod=period)
    
    # Momentum
    df['RSI_14'] = ta.RSI(close, timeperiod=14)
    df['MACD'], df['MACD_SIGNAL'], df['MACD_HIST'] = ta.MACD(close)
    df['STOCH_K'], df['STOCH_D'] = ta.STOCH(high, low, close)
    
    # Volatility
    df['ATR_14'] = ta.ATR(high, low, close)
    df['BB_UPPER'], df['BB_MIDDLE'], df['BB_LOWER'] = ta.BBANDS(close)
    
    # Volume (if valid)
    volume_clean = np.where(volume <= 0, np.nan, volume)
    if not np.all(np.isnan(volume_clean)):
        df['OBV'] = ta.OBV(close, volume_clean)
    
    # Trend strength
    df['ADX_14'] = ta.ADX(high, low, close)
    
    return df