
import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from libs.NseUtility import NseUtils

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime)):
        return obj.isoformat()
    return str(obj)

def safe_call(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        if isinstance(result, pd.DataFrame):
            return result.to_dict(orient='records')
        return result
    except Exception as e:
        return f"Error: {str(e)}"

def explore(symbol="SBIN"):
    nse = NseUtils()
    results = {}
    
    print(f"Exploring API for {symbol}...")
    
    print("1. Fetching Equity Info...")
    results['equity_info'] = safe_call(nse.equity_info, symbol)

    print("2. Fetching Price Info...")
    results['price_info'] = safe_call(nse.price_info, symbol)
        
    print("3. Fetching Market Depth...")
    results['market_depth'] = safe_call(nse.get_market_depth, symbol)
        
    print("4. Fetching FII/DII Activity...")
    results['fii_dii'] = safe_call(nse.fii_dii_activity)

    print("5. Fetching Insider Trading (Last 30 Days)...")
    results['insider_trading'] = safe_call(nse.get_insider_trading)

    print("6. Fetching Corporate Actions...")
    results['corporate_actions'] = safe_call(nse.get_corporate_action)

    print("7. Fetching Upcoming Results...")
    results['upcoming_results'] = safe_call(nse.get_upcoming_results_calendar)
    
    # print("8. Fetching Option Chain...")
    # results['option_chain'] = safe_call(nse.get_option_chain, symbol)

    # Save to file
    output_file = project_root / f"api_exploration_{symbol}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4, default=json_serial)
    
    print(f"Exploration complete. Results saved to {output_file}")

if __name__ == "__main__":
    explore()
