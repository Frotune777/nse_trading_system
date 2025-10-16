import pandas as pd
from libs.NseUtility import NseUtils # <--- Change 'nse_data_scraper' to your actual filename

# Instantiate the NseUtils class
nse = NseUtils()

# Get the full equity list
eq = nse.get_insider_trading()

# Define the CSV file name
csv_filename = "nse_equity_full_list.csv"

# Export the DataFrame to CSV
eq.to_csv(csv_filename, index=False)

print(f"Equity full list successfully exported to {csv_filename}")

# Optional: Display the first few rows to confirm
print("\nFirst 5 rows of the exported data:")
print(eq.head())