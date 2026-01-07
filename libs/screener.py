
import pandas as pd
from pathlib import Path

class StockScreener:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.data_cache = {}

    def load_data(self):
        """Loads all available parquet files into memory."""
        self.data_cache = {}
        files = list(self.data_dir.glob("*_1d.parquet"))
        
        for file in files:
            symbol = file.stem.replace("_1d", "").upper()
            try:
                df = pd.read_parquet(file)
                if not df.empty:
                    self.data_cache[symbol] = df
            except Exception as e:
                print(f"Error loading {file}: {e}")
        
        return list(self.data_cache.keys())

    def apply_filter(self, criteria):
        """
        Filters stocks based on criteria.
        
        criteria: dict with keys:
            - rsi_min, rsi_max (float)
            - price_gt_sma (str, e.g., 'SMA_50')
            - sma_crossover (tuple, e.g., ('SMA_50', 'SMA_200'))
            - pattern (str, e.g., 'CDL_DOJI')
            - volume_spike (bool, > 1.5 * Volume SMA 20)
        """
        results = []
        
        # Ensure data is loaded
        if not self.data_cache:
            self.load_data()
            
        for symbol, df in self.data_cache.items():
            try:
                # Use latest data point
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else latest
                match = True
                reasons = []

                # 1. RSI Filter
                if 'rsi_min' in criteria and criteria['rsi_min'] is not None:
                    rsi_col = 'RSI_14' # Default to RSI 14
                    if rsi_col in latest and latest[rsi_col] < criteria['rsi_min']:
                         match = False
                    elif rsi_col in latest:
                         reasons.append(f"RSI: {latest[rsi_col]:.2f}")

                if 'rsi_max' in criteria and criteria['rsi_max'] is not None:
                    rsi_col = 'RSI_14'
                    if rsi_col in latest and latest[rsi_col] > criteria['rsi_max']:
                        match = False
                    elif rsi_col in latest:
                         reasons.append(f"RSI: {latest[rsi_col]:.2f}")

                # 2. Moving Average Filter (Price > SMA)
                if 'price_gt_sma' in criteria and criteria['price_gt_sma']:
                    sma_col = criteria['price_gt_sma']
                    if sma_col in latest:
                        if latest['Close'] <= latest[sma_col]:
                            match = False
                        else:
                            reasons.append(f"Price > {sma_col}")

                # 3. SMA Crossover (Golden/Death Cross check on CURRENT values for simplicity)
                # Ideally, check if crossover happened recently, but for now checking order
                if 'sma_gt_sma' in criteria and criteria['sma_gt_sma']:
                    fast, slow = criteria['sma_gt_sma']
                    if fast in latest and slow in latest:
                        if latest[fast] <= latest[slow]:
                            match = False
                        else:
                            reasons.append(f"{fast} > {slow}")

                # 4. Patterns
                if 'pattern' in criteria and criteria['pattern']:
                    pat_col = criteria['pattern']
                    if pat_col in latest:
                        if latest[pat_col] == 0:
                            match = False
                        else:
                            reasons.append(f"Pattern: {pat_col}")

                # 5. Volume Spike
                if 'volume_spike' in criteria and criteria['volume_spike']:
                    if 'Volume' in latest and 'VOLUME_SMA_20' in latest:
                        if latest['Volume'] <= 1.5 * latest['VOLUME_SMA_20']:
                            match = False
                        else:
                            reasons.append("Vol Spike")

                if match:
                    if not reasons:
                        reasons.append("Default View (No Filters)")
                    
                    # Add specific indicator values to reasons if they were part of the match
                    if filter_options.get('Pattern') != 'All':
                        reasons.append(f"Pattern: {filter_options['Pattern']}")
                    if filter_options.get('RSI') != 'All':
                        reasons.append(f"RSI: {latest.get('RSI_14', 0):.1f}")
                    if filter_options.get('SMA') != 'All':
                        reasons.append(f"SMA Alignment (Price > SMA200: {latest['Close'] > latest.get('SMA_200', 0)})")
                    
                    results.append({
                        "Symbol": symbol,
                        "Price": f"₹{latest['Close']:.2f}",
                        "Change%": f"{((latest['Close'] - prev['Close']) / prev['Close']) * 100:.2f}%",
                        "Volume": f"{latest['Volume']:,}",
                        "RSI": f"{latest.get('RSI_14', 0):.2f}",
                        "Match Reasons": " | ".join(list(dict.fromkeys(reasons))) # Deduplicate
                    })
            
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
                
        return pd.DataFrame(results)
