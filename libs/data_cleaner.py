import pandas as pd


def validate_data(df):
    """Ensure data quality before storage"""
    if df.empty:
        return df

    # Basic OHLC validation
    mask = (
            (df['High'] >= df['Low']) &
            (df['Volume'] >= 0) &
            (df['Close'].between(df['Low'], df['High'])))

    return df[mask].copy()


def add_technical_features(df):
    """Add basic technical indicators"""
    if df.empty:
        return df

    # Simple Moving Average
    df['SMA_20'] = df['Close'].rolling(window=20).mean()

    # Relative Strength Index
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df['RSI_14'] = 100 - (100 / (1 + rs))

    return df