# libs/data_cleaner.py
import pandas as pd
from libs.indicators import calculate_all_indicators, calculate_essential_indicators


def validate_data(df):
    """Ensure data quality before storage"""
    if df.empty:
        return df

    # Standardize column names (TA-Lib expects Title case)
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })

    # Basic OHLC validation
    mask = (
        (df['High'] >= df['Low']) &
        (df['Volume'] >= 0) &
        (df['Close'].between(df['Low'], df['High']))
    )

    return df[mask].copy()


def add_technical_features(df, mode='full'):
    """
    Add technical indicators using TA-Lib
    
    Args:
        df: OHLCV DataFrame
        mode: 'minimal' (fast, 2 indicators)
              'essential' (balanced, ~20 key indicators) 
              'full' (comprehensive, 70+ indicators)
    
    Returns:
        DataFrame with indicators
    """
    if df.empty:
        return df

    import talib as ta

    if mode == 'minimal':
        # Fast - only SMA and RSI
        df['SMA_20'] = ta.SMA(df['Close'].values, timeperiod=20)
        df['RSI_14'] = ta.RSI(df['Close'].values, timeperiod=14)
        return df
    
    elif mode == 'essential':
        # Balanced - key indicators only (~20)
        return calculate_essential_indicators(df)
    
    elif mode == 'full':
        # Comprehensive - all 70+ indicators
        return calculate_all_indicators(df)
    
    else:
        raise ValueError("mode must be 'minimal', 'essential', or 'full'")