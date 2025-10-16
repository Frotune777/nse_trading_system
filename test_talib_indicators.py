# test_talib_indicators.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
from libs.indicators import TechnicalIndicators
import time

# Load data
df = pd.read_parquet('data/processed/tcs_1d.parquet')

print("="*80)
print("🚀 TESTING TA-LIB 70+ INDICATORS")
print("="*80)
print(f"Dataset: {len(df)} rows")

# Test performance
start_time = time.time()

# Add all indicators
indicators = TechnicalIndicators(df)
df_enhanced = indicators.add_all_indicators()

elapsed = time.time() - start_time

# Get categorized list
categories = indicators.get_indicator_list()

print("\n" + "="*80)
print("📊 INDICATOR BREAKDOWN BY CATEGORY")
print("="*80)

for category, indicator_list in categories.items():
    print(f"\n{category} ({len(indicator_list)} indicators):")
    for ind in sorted(indicator_list):
        print(f"  • {ind}")

print("\n" + "="*80)
print(f"⚡ Performance: {elapsed:.3f} seconds")
print(f"📦 Total columns: {len(df_enhanced.columns)}")
print(f"💾 Memory usage: {df_enhanced.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Show latest values
print("\n" + "="*80)
print("📈 LATEST INDICATOR VALUES")
print("="*80)

latest = df_enhanced.iloc[-1]
date = df_enhanced.index[-1]

print(f"\n📅 Date: {date.date()}")
print(f"💰 Close: ₹{latest['Close']:.2f}")

print(f"\n🔵 TREND (Moving Averages):")
print(f"  SMA_20:   ₹{latest['SMA_20']:.2f}  {'📈 Above' if latest['Close'] > latest['SMA_20'] else '📉 Below'}")
print(f"  SMA_50:   ₹{latest['SMA_50']:.2f}  {'📈 Above' if latest['Close'] > latest['SMA_50'] else '📉 Below'}")
print(f"  SMA_200:  ₹{latest['SMA_200']:.2f}  {'📈 Above' if latest['Close'] > latest['SMA_200'] else '📉 Below'}")
print(f"  EMA_12:   ₹{latest['EMA_12']:.2f}")
print(f"  EMA_26:   ₹{latest['EMA_26']:.2f}")

print(f"\n⚡ MOMENTUM:")
print(f"  RSI_14:       {latest['RSI_14']:.2f}  ", end='')
if latest['RSI_14'] > 70:
    print("🔴 Overbought")
elif latest['RSI_14'] < 30:
    print("🟢 Oversold")
else:
    print("🟡 Neutral")

print(f"  STOCH_K:      {latest['STOCH_K']:.2f}")
print(f"  STOCH_D:      {latest['STOCH_D']:.2f}")
print(f"  CCI_14:       {latest['CCI_14']:.2f}")
print(f"  WILLR_14:     {latest['WILLR_14']:.2f}")
print(f"  MFI:          {latest['MFI']:.2f}")

print(f"\n📊 MACD:")
print(f"  MACD:         {latest['MACD']:.2f}")
print(f"  Signal:       {latest['MACD_SIGNAL']:.2f}")
print(f"  Histogram:    {latest['MACD_HIST']:.2f}  {'🟢 Bullish' if latest['MACD_HIST'] > 0 else '🔴 Bearish'}")

print(f"\n📉 VOLATILITY:")
print(f"  ATR_14:       ₹{latest['ATR_14']:.2f}")
print(f"  BB_UPPER:     ₹{latest['BB_UPPER']:.2f}")
print(f"  BB_MIDDLE:    ₹{latest['BB_MIDDLE']:.2f}")
print(f"  BB_LOWER:     ₹{latest['BB_LOWER']:.2f}")
print(f"  STDDEV_20:    ₹{latest['STDDEV_20']:.2f}")

print(f"\n📦 VOLUME:")
print(f"  OBV:          {latest['OBV']:,.0f}")
print(f"  AD:           {latest['AD']:,.0f}")
print(f"  VOLUME_SMA_20: {latest['VOLUME_SMA_20']:,.0f}")

print(f"\n💪 TREND STRENGTH:")
print(f"  ADX_14:       {latest['ADX_14']:.2f}  ", end='')
if latest['ADX_14'] > 25:
    print("💪 Strong Trend")
else:
    print("😴 Weak Trend")
print(f"  +DI:          {latest['PLUS_DI']:.2f}")
print(f"  -DI:          {latest['MINUS_DI']:.2f}")

print(f"\n🔄 AROON:")
print(f"  AROON_UP:     {latest['AROON_UP']:.2f}")
print(f"  AROON_DOWN:   {latest['AROON_DOWN']:.2f}")

# Check for patterns
print(f"\n🕯️  CANDLESTICK PATTERNS (Recent 5 days):")
pattern_cols = [col for col in df_enhanced.columns if col.startswith('CDL_')]
recent_patterns = df_enhanced[pattern_cols].tail(5)
for date_idx, row in recent_patterns.iterrows():
    patterns_found = [col.replace('CDL_', '') for col, val in row.items() if val != 0]
    if patterns_found:
        print(f"  {date_idx.date()}: {', '.join(patterns_found)}")

# Save enhanced data
output_file = 'data/processed/tcs_1d_talib_full.parquet'
df_enhanced.to_parquet(output_file)
print(f"\n💾 Saved: {output_file}")

print("\n" + "="*80)
print("✅ TEST COMPLETE")
print("="*80)