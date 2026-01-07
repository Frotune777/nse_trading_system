"""
Backtesting Engine

Simulates trading strategies on historical data.

Author: Trading System ML Team
Created: 2026-01-08
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from .strategies import BaseStrategy

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Trade:
    date: datetime
    symbol: str
    type: str  # 'BUY' or 'SELL'
    price: float
    shares: int
    amount: float
    commission: float
    cash_balance: float

class Backtester:
    """
    Event-driven backtesting engine.
    """
    
    def __init__(self, 
                 initial_capital: float = 100000.0,
                 commission_pct: float = 0.001):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Starting cash
            commission_pct: Commission per trade (0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.cash = initial_capital
        self.shares = 0
        self.trades: List[Trade] = []
        self.history: List[Dict] = []
        
    def run(self, 
            data: pd.DataFrame, 
            strategy: BaseStrategy,
            price_col: str = 'Close',
            date_col: str = 'Date') -> Dict:
        """
        Run backtest simulation.
        
        Args:
            data: DataFrame with prices and features
            strategy: Strategy instance
            price_col: Column name for price execution
            date_col: Column name for dates (if not index)
        
        Returns:
            Dictionary with performance metrics
        """
        self._reset()
        logger.info(f"Starting backtest with ${self.initial_capital:,.2f}")
        
        # Ensure data is sorted
        data = data.sort_index()
        
        for i in range(len(data)):
            row = data.iloc[i]
            date = row.name # Assuming DatetimeIndex
            price = row[price_col]
            
            # 1. Update Portfolio Value (Mark-to-Market)
            portfolio_value = self.cash + (self.shares * price)
            self.history.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'cash': self.cash,
                'shares': self.shares,
                'price': price
            })
            
            # 2. Get Signal
            signal = strategy.generate_signal(row)
            
            # 3. Execute Trades
            if signal == 'BUY':
                # Entry rule: Buy if we have cash and aren't fully invested (simple logic: one position)
                # For advanced: check strategy.get_position_size
                
                # Check if we already have a position? 
                # Defined behavior: If 'BUY' signal and NO position -> BUY
                # If 'BUY' signal and ALREADY position -> HOLD (or Pyramid? Assume hold for now)
                
                if self.shares == 0:
                    size = strategy.get_position_size(self.cash, price)
                    if size > 0:
                        cost = size * price
                        commission = cost * self.commission_pct
                        total_cost = cost + commission
                        
                        if total_cost <= self.cash:
                            self.cash -= total_cost
                            self.shares += size
                            self._record_trade(date, 'BUY', price, size, total_cost, commission)
            
            elif signal == 'SELL':
                # Exit rule: Sell if we have shares
                if self.shares > 0:
                    revenue = self.shares * price
                    commission = revenue * self.commission_pct
                    net_revenue = revenue - commission
                    
                    self.cash += net_revenue
                    trade_shares = self.shares
                    self.shares = 0
                    self._record_trade(date, 'SELL', price, trade_shares, net_revenue, commission)
        
        logger.info(f"Backtest complete. Final Value: ${self.history[-1]['portfolio_value']:,.2f}")
        return self.calculate_metrics()
        
    def _reset(self):
        """Reset state."""
        self.cash = self.initial_capital
        self.shares = 0
        self.trades = []
        self.history = []
        
    def _record_trade(self, date, type_, price, shares, amount, commission):
        """Record trade details."""
        trade = Trade(
            date=date,
            symbol="TEST", # Generic for now
            type=type_,
            price=price,
            shares=shares,
            amount=amount,
            commission=commission,
            cash_balance=self.cash
        )
        self.trades.append(trade)
        
    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics."""
        if not self.history:
            return {}
            
        df = pd.DataFrame(self.history).set_index('date')
        df['returns'] = df['portfolio_value'].pct_change().fillna(0)
        
        # 1. Total Return
        final_value = df['portfolio_value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # 2. CAGR (Compound Annual Growth Rate)
        days = (df.index[-1] - df.index[0]).days
        years = days / 365.25
        cagr = (final_value / self.initial_capital) ** (1 / max(years, 0.01)) - 1 if years > 0 else 0
        
        # 3. Sharpe Ratio (assuming risk-free = 0)
        mean_return = df['returns'].mean()
        std_return = df['returns'].std()
        sharpe = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        
        # 4. Max Drawdown
        df['cum_max'] = df['portfolio_value'].cummax()
        df['drawdown'] = (df['portfolio_value'] - df['cum_max']) / df['cum_max']
        max_drawdown = df['drawdown'].min()
        
        # 5. Win Rate
        # Need to pair buy/sell trades to calculate per-trade proft
        # Calculating trade-level metrics
        trade_profits = []
        # Simple pairing logic assuming Buy then Sell
        buy_trades = [t for t in self.trades if t.type == 'BUY']
        sell_trades = [t for t in self.trades if t.type == 'SELL']
        
        for i in range(min(len(buy_trades), len(sell_trades))):
            buy = buy_trades[i]
            sell = sell_trades[i]
            # Profit = Net Revenue (Sell) - Total Cost (Buy)
            profit = sell.amount - buy.amount
            trade_profits.append(profit)
            
        winning_trades = [p for p in trade_profits if p > 0]
        win_rate = len(winning_trades) / len(trade_profits) if trade_profits else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'cagr': cagr,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'total_trades': len(trade_profits),
            'win_rate': win_rate
        }
        
    def get_equity_curve(self) -> pd.DataFrame:
        """Return daily equity curve."""
        return pd.DataFrame(self.history).set_index('date')
        
    def get_trade_log(self) -> pd.DataFrame:
        """Return trade log."""
        return pd.DataFrame([vars(t) for t in self.trades])
