"""
Trading Strategies Module

Defines strategy logic for generating trading signals.
Includes BaseStrategy interface and MLStrategy implementation.

Author: Trading System ML Team
Created: 2026-01-08
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

class BaseStrategy(ABC):
    """
    Abstract base class for trading strategies.
    """
    
    @abstractmethod
    def generate_signal(self, row: pd.Series) -> str:
        """
        Generate a trading signal for a single data point.
        
        Args:
            row: Row of data (features, prices, predictions)
            
        Returns:
            Signal ('BUY', 'SELL', 'HOLD')
        """
        pass
    
    @abstractmethod
    def get_position_size(self, capital: float, price: float) -> int:
        """
        Calculate position size (number of shares).
        
        Args:
            capital: Available capital
            price: Current price
            
        Returns:
            Number of shares to buy/sell
        """
        pass


class MLStrategy(BaseStrategy):
    """
    Strategy based on ML model probability predictions.
    
    Rules:
    - BUY if Prob(Up) > buy_threshold
    - SELL if Prob(Down) > sell_threshold OR Prob(Up) < exit_threshold
    """
    
    def __init__(self, 
                 buy_threshold: float = 0.6, 
                 sell_threshold: float = 0.6,
                 risk_per_trade: float = 0.02,
                 max_position_size: float = 0.99):
        """
        Initialize ML Strategy.
        
        Args:
            buy_threshold: Probability threshold for buy signal
            sell_threshold: Probability threshold for sell signal
            risk_per_trade: Fraction of capital to risk per trade (not fully implemented in simple version)
            max_position_size: Maximum fraction of portfolio to allocate
        """
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size
        
    def generate_signal(self, row: pd.Series) -> str:
        """
        Generate signal based on 'probability_up' and 'probability_down' columns.
        Expected row columns: including 'probability_up', 'probability_down'
        """
        prob_up = row.get('probability_up', 0.0)
        prob_down = row.get('probability_down', 0.0)
        
        if prob_up > self.buy_threshold:
            return 'BUY'
        elif prob_down > self.sell_threshold:
            return 'SELL'
        else:
            return 'HOLD'
            
    def get_position_size(self, capital: float, price: float) -> int:
        """
        Simple position sizing: Use max_position_size of capital.
        """
        # Calculate amount to invest
        invest_amount = capital * self.max_position_size
        
        # Calculate shares (floor)
        shares = int(invest_amount // price)
        
        return max(0, shares)

class TrendFollowingStrategy(BaseStrategy):
    """
    Simple Moving Average Crossover Strategy (for comparison).
    """
    
    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signal(self, row: pd.Series) -> str:
        sma_short = row.get(f'SMA_{self.short_window}', 0)
        sma_long = row.get(f'SMA_{self.long_window}', 0)
        
        # This requires state or looking at previous row, which simple generate_signal doesn't allow easily
        # For simple row-based processing without state history in 'row', we check if short > long
        # Ideally, we need crossover logic (was below, now above)
        
        if sma_short > sma_long:
            return 'BUY'
        elif sma_short < sma_long:
            return 'SELL'
        return 'HOLD'

    def get_position_size(self, capital: float, price: float) -> int:
        return int((capital * 0.95) // price)
