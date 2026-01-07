
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from libs.institutional import InstitutionalAnalyzer
from libs.NseUtility import NseUtils
import json

def test():
    analyzer = InstitutionalAnalyzer()
    
    print("\n1. Market Status Check:")
    is_open = analyzer.is_market_open()
    print(f"Is Market Open? {is_open}")
    
    print("\n2. Smart Money Flow (FII/DII):")
    try:
        fii_data = analyzer.get_smart_money_flow()
        print(f"Records found: {len(fii_data)}")
        if fii_data:
            print(f"Latest: {fii_data[0]}")
    except Exception as e:
        print(f"Failed: {e}")

    print("\n3. Option Chain Analysis (Force Fetch = True):")
    # Using 'SBIN' as example
    oi_data = analyzer.analyze_oi("SBIN", force_fetch=True)
    print(json.dumps(oi_data, indent=2))
    
    if oi_data.get('status') in ['Live', 'Market Closed']:
        print("\n✅ Institutional Test Passed")
    else:
        print("\n❌ Institutional Test Failed")

if __name__ == "__main__":
    test()
