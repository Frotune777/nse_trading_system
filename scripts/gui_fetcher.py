#!/usr/bin/env python3
import sys
import os
import traceback
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QTabWidget, QComboBox,
    QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
import pandas as pd
from pandasql import sqldf
from concurrent.futures import ThreadPoolExecutor, as_completed
# Assuming these are correctly located relative to this script
from libs.nse_data_fetcher import NSEMasterData
from libs.data_cleaner import validate_data, add_technical_features
from libs.storage import DataStorage


class GuiFetcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NSE Trading Data Fetcher")
        self.resize(950, 700)

        self.storage = DataStorage()
        # Initialize current_df as an empty DataFrame
        # This will hold the data from the selected parquet file,
        # prepared for pandasql queries.
        self.current_df_for_sql = pd.DataFrame()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.setup_fetch_update_tab()
        self.setup_view_data_tab()

    def setup_fetch_update_tab(self):
        self.fetch_tab = QWidget()
        layout = QVBoxLayout()

        # Symbol input
        symbol_layout = QHBoxLayout()
        symbol_layout.addWidget(QLabel("Symbol:"))
        self.symbol_input = QLineEdit()
        symbol_layout.addWidget(self.symbol_input)
        layout.addLayout(symbol_layout)

        # Interval input
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Interval:"))
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["1d", "1m", "5m", "10m", "30m", "1h"])
        interval_layout.addWidget(self.interval_combo)
        layout.addLayout(interval_layout)

        # Days input
        days_layout = QHBoxLayout()
        days_layout.addWidget(QLabel("Days:"))
        self.days_input = QLineEdit("30")
        days_layout.addWidget(self.days_input)
        layout.addLayout(days_layout)

        # Buttons layout
        btn_layout = QHBoxLayout()
        fetch_btn = QPushButton("Fetch & Update Data")
        fetch_btn.clicked.connect(self.fetch_and_update_single)
        btn_layout.addWidget(fetch_btn)

        bulk_btn = QPushButton("Bulk Fetch from CSV")
        bulk_btn.clicked.connect(self.fetch_bulk_from_csv)
        btn_layout.addWidget(bulk_btn)
        layout.addLayout(btn_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Log output
        self.fetch_log = QTextEdit()
        self.fetch_log.setReadOnly(True)
        layout.addWidget(self.fetch_log)

        self.fetch_tab.setLayout(layout)
        self.tabs.addTab(self.fetch_tab, "Fetch/Update Data")

    def fetch_and_update_single(self):
        symbol = self.symbol_input.text().strip().upper()
        interval = self.interval_combo.currentText()
        days_text = self.days_input.text().strip()
        days = int(days_text) if days_text.isdigit() else 30

        if not symbol:
            QMessageBox.warning(self, "Input Error", "Please enter a symbol.")
            return

        self.fetch_log.append(f"Starting fetch for {symbol} at interval {interval} for last {days} days...")
        try:
            # Note: The `fetch_incremental` method in DataStorage already handles start/end dates
            # and incremental logic. Passing 'days' here seems redundant if you intend to use
            # the full incremental logic from DataStorage.
            # If you specifically want to limit the fetch to the last N days regardless of existing data,
            # you might need to adjust how DataStorage's fetch_incremental is called or modify it.
            # For now, let's assume get_history needs a start_date.
            start_date_obj = datetime.now() - timedelta(days=days)
            self._fetch_process_save(symbol, interval, start_date_obj) # Pass datetime object
        except Exception as e:
            self.fetch_log.append(f"Error fetching {symbol}: {str(e)}")
            self.fetch_log.append(traceback.format_exc())

    def fetch_bulk_from_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV with symbols", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            df = pd.read_csv(file_path)
            df.columns = map(str.lower, df.columns)
        except Exception as e:
            self.fetch_log.append(f"Failed to read CSV: {str(e)}")
            return

        if 'symbol' not in df.columns:
            self.fetch_log.append("CSV must have 'symbol' column.")
            return

        self.progress_bar.setMaximum(len(df))
        self.progress_bar.setValue(0)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for _, row in df.iterrows():
                symbol = str(row.get('symbol', '')).strip().upper()
                interval = str(row.get('interval', '1d')).strip().lower()
                days = int(row.get('days', 30)) if str(row.get('days', '')).isdigit() else 30
                start_date_obj = datetime.now() - timedelta(days=days) # Pass datetime object
                futures.append(executor.submit(self._fetch_process_save, symbol, interval, start_date_obj))

            for idx, f in enumerate(as_completed(futures), 1):
                try:
                    f.result()
                except Exception as e:
                    self.fetch_log.append(f"Bulk fetch error: {str(e)}")
                self.progress_bar.setValue(idx)

        self.fetch_log.append("✅ Bulk fetch completed.")

    # Modified to accept datetime object for start
    def _fetch_process_save(self, symbol, interval, start_date: datetime):
        fetcher = NSEMasterData()
        fetcher.download_symbol_master() # This seems like it should be done once or cached

        df = fetcher.get_history(
            symbol=symbol, exchange="NSE",
            start=start_date, # Use datetime object directly
            end=datetime.now(), interval=interval
        )

        if df.empty:
            self.fetch_log.append(f"❌ No data for {symbol}")
            return

        # It's important that validate_data and add_technical_features
        # maintain the DatetimeIndex or convert a 'Timestamp' column to index.
        # Based on previous discussions, DataStorage expects a DatetimeIndex
        # and handles resetting it for storage.
        clean_df = validate_data(df)
        enhanced_df = add_technical_features(clean_df)

        # The DataStorage methods will internally handle the 'Timestamp' column vs. index
        self.storage.save_to_parquet(enhanced_df, symbol, interval)
        self.storage.update_sqlite(enhanced_df, symbol, interval)

        self.fetch_log.append(f"✅ Saved {len(enhanced_df)} records for {symbol}")

    def setup_view_data_tab(self):
        self.view_data_tab = QWidget()
        layout = QVBoxLayout()

        # Filters: Symbol + Interval
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Symbol Filter:"))
        self.symbol_filter = QLineEdit()
        filter_layout.addWidget(self.symbol_filter)

        filter_layout.addWidget(QLabel("Interval Filter:"))
        self.timeframe_filter = QComboBox()
        self.timeframe_filter.addItem("All")
        self.timeframe_filter.addItems(["1d", "1m", "5m", "10m", "30m", "1h"])
        filter_layout.addWidget(self.timeframe_filter)
        layout.addLayout(filter_layout)

        file_select_layout = QHBoxLayout()
        self.parquet_files_combo = QComboBox()
        self.refresh_files_btn = QPushButton("Refresh Files")
        file_select_layout.addWidget(QLabel("Select Parquet File:"))
        file_select_layout.addWidget(self.parquet_files_combo)
        file_select_layout.addWidget(self.refresh_files_btn)
        layout.addLayout(file_select_layout)

        self.sql_input = QTextEdit()
        self.sql_input.setPlaceholderText("Enter SQL query here (use table alias 'df'). 'Timestamp' column available.")
        layout.addWidget(self.sql_input)

        run_sql_btn = QPushButton("Run SQL")
        layout.addWidget(run_sql_btn)

        self.query_output = QTextEdit()
        self.query_output.setReadOnly(True)
        layout.addWidget(self.query_output)

        self.view_data_tab.setLayout(layout)
        self.tabs.addTab(self.view_data_tab, "View Data")

        self.refresh_files_btn.clicked.connect(self.load_parquet_files)
        self.parquet_files_combo.currentIndexChanged.connect(self.load_selected_parquet)
        run_sql_btn.clicked.connect(self.run_sql_query)
        self.symbol_filter.textChanged.connect(self.apply_file_filters)
        self.timeframe_filter.currentIndexChanged.connect(self.apply_file_filters)

        self.load_parquet_files()

    def load_parquet_files(self):
        self.all_files = self.storage.list_parquet_files()
        self.apply_file_filters()

    def apply_file_filters(self):
        symbol_text = self.symbol_filter.text().strip().upper()
        interval_text = self.timeframe_filter.currentText()

        filtered = [
            f for f in self.all_files
            if (symbol_text in f.upper())
            and (interval_text == "All" or interval_text in f)
        ]
        self.parquet_files_combo.clear()
        self.parquet_files_combo.addItems(filtered)
        if filtered:
            self.load_selected_parquet()

    def load_selected_parquet(self):
        filename = self.parquet_files_combo.currentText()
        if not filename:
            # Clear previous data if no file is selected (e.g., filters removed all options)
            self.current_df_for_sql = pd.DataFrame()
            self.query_output.setPlainText("No file selected or available.")
            self.sql_input.setPlainText("")
            return

        try:
            # Load the DataFrame. storage.load_parquet_file will return with DatetimeIndex.
            loaded_df = self.storage.load_parquet_file(filename)

            # --- CRITICAL CHANGE HERE ---
            # Reset the index to make 'Timestamp' a regular column for pandasql
            if isinstance(loaded_df.index, pd.DatetimeIndex):
                # Using .copy() to ensure we don't modify the underlying DataFrame
                # that might be returned by storage if it ever caches it.
                self.current_df_for_sql = loaded_df.reset_index().copy()
            else:
                # If for some reason it's not a DatetimeIndex, but 'Timestamp' is a column
                if 'Timestamp' in loaded_df.columns:
                    self.current_df_for_sql = loaded_df.copy()
                else:
                    self.current_df_for_sql = pd.DataFrame() # Clear if unexpected format
                    self.query_output.setPlainText(f"Error: Loaded DataFrame from {filename} does not have a 'Timestamp' column or DatetimeIndex.")
                    return


            preview = self.current_df_for_sql.head(10).to_string(index=False)
            self.query_output.setPlainText(f"Preview of {filename}:\n\n{preview}")
            self.sql_input.setPlainText("SELECT Timestamp, Open, High, Low, Close FROM df LIMIT 10;")
        except Exception as e:
            self.query_output.setPlainText(f"Failed to load {filename}: {str(e)}\n{traceback.format_exc()}")
            self.current_df_for_sql = pd.DataFrame() # Clear current data on error

    def run_sql_query(self):
        # Use the prepared DataFrame
        if self.current_df_for_sql.empty:
            self.query_output.setPlainText("No data loaded or prepared for SQL query.")
            return

        query = self.sql_input.toPlainText().strip()
        if not query:
            self.query_output.setPlainText("Please enter an SQL query.")
            return

        try:
            # Ensure the df alias points to the DataFrame with 'Timestamp' as a column
            pysqldf = lambda q: sqldf(q, {"df": self.current_df_for_sql})
            result = pysqldf(query)
            self.query_output.setPlainText(result.to_string(index=False))
        except Exception as e:
            self.query_output.setPlainText(f"SQL Error: {str(e)}\n{traceback.format_exc()}")


if __name__ == "__main__":
    # Ensure the 'data' directory exists for DataStorage
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)

    app = QApplication(sys.argv)
    window = GuiFetcher()
    window.show()
    sys.exit(app.exec())