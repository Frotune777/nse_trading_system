from datetime import datetime, timedelta
from libs.nse_data_fetcher import NSEMasterData
from libs.data_cleaner import validate_data, add_technical_features
from libs.storage import DataStorage
import yaml


def update_all_symbols():
    try:
        from pathlib import Path
        yaml_path = Path(__file__).resolve().parent.parent / "config" / "symbols.yaml"
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
            symbols = config.get("tracked_symbols", [])

        if not symbols:
            print("⚠️ No symbols found in config/symbols.yaml")
            return

        fetcher = NSEMasterData()
        fetcher.download_symbol_master()
        storage = DataStorage()

        for symbol in symbols:
            print(f"\n🔄 Updating: {symbol}")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)

            df = fetcher.get_history(
                symbol=symbol,
                exchange="NSE",
                start=start_date,
                end=end_date,
                interval='1d'
            )

            if df.empty:
                print(f"❌ No new data for {symbol}")
                continue

            clean_df = validate_data(df)
            enhanced_df = add_technical_features(clean_df)
            storage.update_sqlite(enhanced_df, symbol, '1d')
            print(f"✅ Updated {symbol}: {len(enhanced_df)} records")

    except Exception as e:
        print(f"\n❌ Daily update failed: {e}")


if __name__ == "__main__":
    update_all_symbols()