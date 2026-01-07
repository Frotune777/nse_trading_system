
import sys
import json
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from libs.storage import DataStorage

def migrate():
    storage = DataStorage()
    stats_dir = project_root / "data" / "processed" / "market_stats"
    
    mapping = [
        ("fii_dii", "market_fii_dii", ["category", "date"]),
        ("insider_trading", "market_insider_trading", ["symbol", "acqName", "date", "secAcq"]),
        ("upcoming_results", "market_upcoming_results", ["symbol", "date"])
    ]
    
    for json_name, table_name, unique_cols in mapping:
        path = stats_dir / f"{json_name}.json"
        if path.exists():
            print(f"Migrating {json_name}...")
            with open(path) as f:
                data = json.load(f)
                if data:
                    df = pd.DataFrame(data)
                    storage.update_market_stats(df, table_name, unique_cols)
                    print(f"Successfully migrated {len(df)} records to {table_name}")
        else:
            print(f"No JSON found for {json_name}")

if __name__ == "__main__":
    migrate()
