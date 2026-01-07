
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from libs.quad_analyzer import QuadAnalyzer
import json

def test():
    print("Initializing Quad Analyzer...")
    quad = QuadAnalyzer()
    
    symbol = "SBIN"
    print(f"\nGenerating Report for {symbol}...")
    report = quad.get_report_card(symbol)
    
    # Prune heavy data for details
    if "raw_fundamental" in report["details"]:
        report["details"]["raw_fundamental"] = "Data Hidden for Summary"
        
    print("\n--- Quad Report ---")
    print(json.dumps(report, indent=2))
    
    if report["quad_score"] >= 0:
        print("\n✅ Quad Analysis Engine Functional")
    else:
        print("\n❌ Failed")

if __name__ == "__main__":
    test()
