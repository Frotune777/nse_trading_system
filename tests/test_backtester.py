
import unittest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from libs.backtester import Backtester
from libs.strategies import MLStrategy

class TestBacktester(unittest.TestCase):
    
    def setUp(self):
        # Create dummy data
        dates = pd.date_range(start='2024-01-01', periods=10, freq='D')
        
        # Scenario: 
        # Day 0: Neutral
        # Day 1: Strong Buy signal (Prob Up 0.8) -> Buy at Close (100)
        # Day 2-4: Hold (Price goes up 100 -> 110)
        # Day 5: Strong Sell signal (Prob Down 0.8) -> Sell at Close (110) -> Profit
        
        data = {
            'Close': [100, 100, 102, 105, 108, 110, 109, 105, 100, 95],
            'probability_up':   [0.3, 0.8, 0.4, 0.4, 0.4, 0.1, 0.1, 0.1, 0.1, 0.1],
            'probability_down': [0.3, 0.1, 0.1, 0.1, 0.1, 0.8, 0.4, 0.4, 0.4, 0.4]
        }
        self.df = pd.DataFrame(data, index=dates)
        
    def test_ml_strategy_execution(self):
        # Strategy: Buy > 0.6, Sell > 0.6
        strategy = MLStrategy(buy_threshold=0.6, sell_threshold=0.6)
        
        backtester = Backtester(initial_capital=10000)
        metrics = backtester.run(self.df, strategy)
        
        trades = backtester.get_trade_log()
        
        # Verification
        self.assertEqual(len(trades), 2, "Should have 2 trades (Buy and Sell)")
        
        # Trade 1: Buy on Day 1 (Index 1)
        buy_trade = trades.iloc[0]
        self.assertEqual(buy_trade['type'], 'BUY')
        self.assertEqual(buy_trade['price'], 100)
        
        # Trade 2: Sell on Day 5 (Index 5)
        sell_trade = trades.iloc[1]
        self.assertEqual(sell_trade['type'], 'SELL')
        self.assertEqual(sell_trade['price'], 110)
        
        # Metrics
        # Bought at 100, Sold at 110. Profit approx 10%.
        # Commission is 0.1% * 100 + 0.1% * 110 = 0.1 + 0.11 = 0.21 per share?
        # Actually it calculates total commission.
        
        self.assertGreater(metrics['total_return'], 0, "Should be profitable")
        self.assertAlmostEqual(metrics['win_rate'], 1.0, "Win rate should be 100%")

if __name__ == '__main__':
    unittest.main()
