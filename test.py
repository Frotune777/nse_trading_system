import pandas as pd
import pyarrow.parquet as pq

# Set your Parquet file path here
parquet_path = "data/processed/wipro_1d.parquet"  # Change as needed

try:
    # Load the Parquet file
    df = pd.read_parquet(parquet_path)

    # If the index is a DatetimeIndex, reset it so it's accessible as a column
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index()

    print("First 5 rows:")
    print(df.head())

    print("\nColumns:")
    print(df.columns.tolist())
except Exception as e:
    print(f"Failed to load file: {e}")
