"""
Feature Engineering Module

Generates predictive features from raw OHLCV data for machine learning models.
This is the most critical step for ML success - quality features = quality predictions.

Author: Trading System ML Team
Created: 2026-01-07
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Generate features for ML models from OHLCV data.
    
    Features created:
    - Returns (simple & log) for multiple periods
    - Volatility (rolling std, Parkinson, Garman-Klass)
    - Momentum indicators
    - Volume features (momentum, correlation, VWAP)
    - Price patterns (gaps, ranges)
    - Lagged features
    - Rolling statistics
    
    Example:
        >>> from libs.feature_engineering import FeatureEngineer
        >>> engineer = FeatureEngineer(df)
        >>> features = engineer.build_all()
        >>> print(f"Created {len(features.columns)} features")
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize feature engineer.
        
        Args:
            df: DataFrame with OHLCV data (datetime index)
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must have DatetimeIndex")
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        self.df = df.copy()
        self.features = pd.DataFrame(index=df.index)
        logger.info(f"Initialized FeatureEngineer with {len(df)} rows")
    
    def add_returns(self, periods: List[int] = [1, 5, 10, 20, 60]) -> 'FeatureEngineer':
        """
        Calculate returns for multiple periods.
        
        Returns = (Price_t - Price_t-n) / Price_t-n
        Log Returns = ln(Price_t / Price_t-n)
        
        Args:
            periods: List of lookback periods (days)
        
        Returns:
            self for method chaining
        """
        logger.info(f"Adding returns for periods: {periods}")
        
        for period in periods:
            # Simple returns
            self.features[f'return_{period}d'] = self.df['Close'].pct_change(period)
            
            # Log returns (more suitable for ML, assumes normal distribution)
            self.features[f'log_return_{period}d'] = np.log(
                self.df['Close'] / self.df['Close'].shift(period)
            )
        
        return self
    
    def add_volatility(self, windows: List[int] = [10, 20, 60]) -> 'FeatureEngineer':
        """
        Calculate volatility metrics.
        
        Includes:
        - Simple volatility (rolling std of returns)
        - Parkinson volatility (high-low based, more efficient)
        - Garman-Klass volatility (OHLC based, most efficient)
        
        Args:
            windows: List of rolling window sizes
        
        Returns:
            self for method chaining
        """
        logger.info(f"Adding volatility for windows: {windows}")
        
        for window in windows:
            # Simple volatility (rolling std of returns)
            returns = self.df['Close'].pct_change()
            self.features[f'volatility_{window}d'] = returns.rolling(window).std()
            
            # Parkinson volatility (high-low based)
            # More efficient than close-to-close, uses intraday range
            hl_ratio = np.log(self.df['High'] / self.df['Low'])
            self.features[f'parkinson_vol_{window}d'] = np.sqrt(
                (1 / (4 * np.log(2))) * (hl_ratio ** 2).rolling(window).mean()
            )
            
            # Garman-Klass volatility (OHLC based)
            # Most efficient estimator using all OHLC data
            hl = (np.log(self.df['High'] / self.df['Low'])) ** 2
            co = (np.log(self.df['Close'] / self.df['Open'])) ** 2
            self.features[f'gk_vol_{window}d'] = np.sqrt(
                0.5 * hl.rolling(window).mean() - 
                (2 * np.log(2) - 1) * co.rolling(window).mean()
            )
        
        return self
    
    def add_momentum(self, periods: List[int] = [5, 10, 20]) -> 'FeatureEngineer':
        """
        Price momentum indicators.
        
        Args:
            periods: List of lookback periods
        
        Returns:
            self for method chaining
        """
        logger.info(f"Adding momentum for periods: {periods}")
        
        for period in periods:
            # Simple momentum (absolute price change)
            self.features[f'momentum_{period}d'] = (
                self.df['Close'] - self.df['Close'].shift(period)
            )
            
            # Rate of change (percentage)
            self.features[f'roc_{period}d'] = (
                (self.df['Close'] - self.df['Close'].shift(period)) / 
                self.df['Close'].shift(period) * 100
            )
        
        return self
    
    def add_volume_features(self, windows: List[int] = [5, 10, 20]) -> 'FeatureEngineer':
        """
        Volume-based features.
        
        Includes:
        - Volume momentum (current vs average)
        - Volume-price correlation
        - VWAP (Volume Weighted Average Price)
        - Abnormal volume detection
        
        Args:
            windows: List of rolling window sizes
        
        Returns:
            self for method chaining
        """
        logger.info(f"Adding volume features for windows: {windows}")
        
        for window in windows:
            # Volume momentum (current volume / average volume)
            self.features[f'volume_momentum_{window}d'] = (
                self.df['Volume'] / self.df['Volume'].rolling(window).mean()
            )
            
            # Volume-price correlation
            returns = self.df['Close'].pct_change()
            volume_change = self.df['Volume'].pct_change()
            self.features[f'volume_price_corr_{window}d'] = (
                returns.rolling(window).corr(volume_change)
            )
        
        # VWAP (Volume Weighted Average Price)
        # Cumulative (price * volume) / cumulative volume
        typical_price = (self.df['High'] + self.df['Low'] + self.df['Close']) / 3
        self.features['vwap'] = (
            (typical_price * self.df['Volume']).cumsum() / 
            self.df['Volume'].cumsum()
        )
        
        # Distance from VWAP (percentage)
        self.features['vwap_distance'] = (
            (self.df['Close'] - self.features['vwap']) / self.features['vwap'] * 100
        )
        
        return self
    
    def add_price_patterns(self) -> 'FeatureEngineer':
        """
        Price pattern features.
        
        Includes:
        - High-Low range
        - Gap (open vs previous close)
        - Intraday range
        - Close position in range
        - Body size (open-close)
        - Upper/lower shadows
        
        Returns:
            self for method chaining
        """
        logger.info("Adding price pattern features")
        
        # High-Low range (normalized by close)
        self.features['hl_range'] = (
            (self.df['High'] - self.df['Low']) / self.df['Close']
        )
        
        # Gap (open vs previous close)
        self.features['gap'] = (
            (self.df['Open'] - self.df['Close'].shift(1)) / 
            self.df['Close'].shift(1)
        )
        
        # Intraday range (normalized by open)
        self.features['intraday_range'] = (
            (self.df['High'] - self.df['Low']) / self.df['Open']
        )
        
        # Close position in range (0 = at low, 1 = at high)
        range_size = self.df['High'] - self.df['Low']
        self.features['close_position'] = np.where(
            range_size > 0,
            (self.df['Close'] - self.df['Low']) / range_size,
            0.5  # Default to middle if no range
        )
        
        # Candlestick body size
        self.features['body_size'] = (
            abs(self.df['Close'] - self.df['Open']) / self.df['Open']
        )
        
        # Upper shadow (high - max(open, close))
        self.features['upper_shadow'] = (
            (self.df['High'] - self.df[['Open', 'Close']].max(axis=1)) / 
            self.df['Close']
        )
        
        # Lower shadow (min(open, close) - low)
        self.features['lower_shadow'] = (
            (self.df[['Open', 'Close']].min(axis=1) - self.df['Low']) / 
            self.df['Close']
        )
        
        return self
    
    def add_lagged_features(self, columns: List[str], lags: List[int] = [1, 5, 20]) -> 'FeatureEngineer':
        """
        Create lagged versions of features.
        
        Useful for capturing temporal dependencies.
        
        Args:
            columns: List of column names to lag
            lags: List of lag periods
        
        Returns:
            self for method chaining
        """
        logger.info(f"Adding lagged features for {len(columns)} columns with lags {lags}")
        
        for col in columns:
            if col in self.features.columns:
                for lag in lags:
                    self.features[f'{col}_lag{lag}'] = self.features[col].shift(lag)
        
        return self
    
    def add_rolling_stats(self, columns: List[str], windows: List[int] = [5, 10, 20]) -> 'FeatureEngineer':
        """
        Rolling statistics for features.
        
        Calculates mean, std, min, max for each window.
        
        Args:
            columns: List of column names
            windows: List of rolling window sizes
        
        Returns:
            self for method chaining
        """
        logger.info(f"Adding rolling stats for {len(columns)} columns with windows {windows}")
        
        for col in columns:
            if col in self.features.columns:
                for window in windows:
                    self.features[f'{col}_mean_{window}d'] = (
                        self.features[col].rolling(window).mean()
                    )
                    self.features[f'{col}_std_{window}d'] = (
                        self.features[col].rolling(window).std()
                    )
                    self.features[f'{col}_min_{window}d'] = (
                        self.features[col].rolling(window).min()
                    )
                    self.features[f'{col}_max_{window}d'] = (
                        self.features[col].rolling(window).max()
                    )
        
        return self
    
    def get_features(self) -> pd.DataFrame:
        """
        Return all engineered features.
        
        Returns:
            DataFrame with all features
        """
        return self.features
    
    def build_all(self, 
                  return_periods: List[int] = [1, 5, 10, 20],
                  volatility_windows: List[int] = [10, 20],
                  momentum_periods: List[int] = [5, 10, 20],
                  volume_windows: List[int] = [10, 20]) -> pd.DataFrame:
        """
        Build all features in one call with default parameters.
        
        This is the recommended way to use FeatureEngineer.
        
        Args:
            return_periods: Periods for return calculation
            volatility_windows: Windows for volatility metrics
            momentum_periods: Periods for momentum indicators
            volume_windows: Windows for volume features
        
        Returns:
            DataFrame with all engineered features
        """
        logger.info("Building all features...")
        
        # Core features
        self.add_returns(return_periods)
        self.add_volatility(volatility_windows)
        self.add_momentum(momentum_periods)
        self.add_volume_features(volume_windows)
        self.add_price_patterns()
        
        # Lagged features for key indicators
        key_features = ['return_1d', 'volatility_20d', 'volume_momentum_10d']
        self.add_lagged_features(key_features, lags=[1, 5])
        
        # Rolling stats for returns
        self.add_rolling_stats(['return_1d'], windows=[5, 10])
        
        feature_count = len(self.features.columns)
        logger.info(f"✅ Feature engineering complete: {feature_count} features created")
        
        return self.get_features()
    
    def get_feature_summary(self) -> Dict:
        """
        Get summary statistics of engineered features.
        
        Returns:
            Dictionary with feature statistics
        """
        summary = {
            'total_features': len(self.features.columns),
            'total_rows': len(self.features),
            'missing_values': self.features.isnull().sum().sum(),
            'missing_percentage': (self.features.isnull().sum().sum() / 
                                 (len(self.features) * len(self.features.columns)) * 100),
            'feature_types': {
                'returns': len([c for c in self.features.columns if 'return' in c]),
                'volatility': len([c for c in self.features.columns if 'vol' in c]),
                'momentum': len([c for c in self.features.columns if 'momentum' in c or 'roc' in c]),
                'volume': len([c for c in self.features.columns if 'volume' in c or 'vwap' in c]),
                'patterns': len([c for c in self.features.columns if any(p in c for p in ['gap', 'range', 'shadow', 'body'])]),
                'lagged': len([c for c in self.features.columns if 'lag' in c]),
                'rolling': len([c for c in self.features.columns if any(s in c for s in ['mean', 'std', 'min', 'max'])])
            }
        }
        
        return summary


def engineer_features_for_symbol(symbol: str, timeframe: str = '1d') -> pd.DataFrame:
    """
    Convenience function to engineer features for a symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'TCS')
        timeframe: Data timeframe (e.g., '1d')
    
    Returns:
        DataFrame with OHLCV + engineered features
    
    Example:
        >>> features_df = engineer_features_for_symbol('TCS', '1d')
        >>> print(features_df.columns)
    """
    from libs.historical_data_manager import HistoricalDataManager
    
    # Load data
    manager = HistoricalDataManager()
    df = manager.get_symbol_data(symbol, timeframe)
    
    if df.empty:
        logger.error(f"No data found for {symbol} {timeframe}")
        return pd.DataFrame()
    
    # Engineer features
    engineer = FeatureEngineer(df)
    features = engineer.build_all()
    
    # Combine with original OHLCV
    result = pd.concat([df, features], axis=1)
    
    logger.info(f"Engineered {len(features.columns)} features for {symbol} {timeframe}")
    
    return result
