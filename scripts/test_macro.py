
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from libs.macro import MacroAnalyzer
import json

def test():
    print("Fetching Sector Data...")
    macro = MacroAnalyzer()
    data = macro.fetch_sector_performance()
    
    print(f"\nFetched {len(data)} sectors.")
    
    if "NIFTY 50" in data:
        nifty = data["NIFTY 50"]
        print(f"NIFTY 50: {nifty['last_price']} ({nifty['change_pct']:.2f}%)")
        print(f"Trend: {nifty['trend']}")
        print("✅ Macro Test Passed")
    else:
        print("❌ Macro Test Failed")

if __name__ == "__main__":
    test()
