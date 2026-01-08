# PKScreener Dashboard Integration Guide

This document details the full integration of PKScreener into the Trading Dashboard, covering the unit architecture, integration layer, end-to-end execution cycle, and trading utility.

## 1. Unit Architecture: `PKScreenerAdapter`

The core of the integration is the **Adapter Pattern** implemented in `libs/pkscreener_adapter.py`.

### 1.1 Responsibilities
*   **Subprocess Management**: It runs `pkscreenercli.py` in a separate process to ensure isolation from the main Streamlit thread.
*   **Environment Injection**: It injects necessary environment variables (like `RUNNER=1`, `PYTHONPATH`) to bypass interactive menus (OTP/Telegram).
*   **Configuration Management**: It features a `update_config()` method that dynamically modifies `pkscreener.ini` based on UI inputs.
*   **Result Parsing**: It locates the generated CSV report in `results/Reports/` using a recursive search strategy and loads it into a Pandas DataFrame.

### 1.2 Key Methods
*   `run_scan(scan_option, index_option, sub_option, stock_list)`: The main entry point. Constructs the CLI command.
    *   *Stock List Logic*: If a custom list is provided, it appends `--stocklist "A,B,C"` to the command.
*   `update_config(settings)`: Safely updates the INI file.

## 2. Integration Layer: `dashboard.py`

The Dashboard acts as the **Controller** and **View**.

### 2.1 User Interface
*   **Selection Mode**: Added a switcher between "Predefined Index", "Saved Stock Lists" (Database), and "Upload New List".
*   **Database Integration**: Feature to **Save** uploaded lists into the local `trading.db` (`custom_stock_lists` table) for persistent, space-efficient storage.
*   **Advanced Configuration**: An expander to set Timeframe (`duration`), Lookback (`period`), and Filters (`Min Volume`).

### 2.2 Execution Flow
1.  **Config Update**: On clicking "Run Scan", the dashboard first gathers configuration inputs and calls `adapter.update_config()`.
2.  **Scan Execution**: It calls `asyncio.run(adapter.run_scan(...))`.
3.  **Visual Feedback**: A spinner indicates progress (1-2 minutes typically).
4.  **Result Display**: Results are shown in an interactive table and offered as a CSV download.

## 3. End-to-End (E2E) Cycle

The lifecycle of a single scan operation:

1.  **Trigger**: User selects "Volume Shockers" on "Nifty 50" with "15m" timeframe and clicks "Run".
2.  **Config Step**: `pkscreener.ini` is updated: `duration = 15m`.
3.  **Command Construction**: Adapter builds: 
    `python pkscreenercli.py -a Y -o X:12:9 -e`
4.  **Process Execution**:
    *   CLI launches.
    *   Downloads data (if not cached) for Nifty 50.
    *   Resamples data to 15m.
    *   Calculates RSI/Bollinger Bands/etc.
    *   Saves report to `results/Reports/PKS_...csv`.
5.  **Result Retrieval**: Adapter finds the new CSV.
6.  **Display**: Dashboard renders the DataFrame.

## 4. Trading Analysis & Utility

How to utilize this system for actual trading:

### 4.1 Workflow: Option Chain Analysis
**Scenario**: You have an Option Chain export (like the one you analyzed).
1.  **Upload**: Upload the export CSV to the "Custom Stock List" section.
2.  **Scan**: Run a **"Breakout" (Strategy 2)** or **"Volume Shocker" (Strategy 9)** scan on this list.
3.  **Insight**: This filters the 180+ F&O stocks down to the 5-10 that are actually moving *right now*.
4.  **Trade**: You can now look at the Option Chain for *only* those 5 stocks to pick strikes.

### 4.2 Workflow: Intraday Momentum
1.  **Configure**: Set Duration to `15m` or `5m`.
2.  **Strategy**: Select **Strategy 23 (Intraday Momentum)**.
3.  **Action**: Run this every 30 minutes.
4.  **Signal**: If a stock appears with `RSI > 60` and `Volume > 2.5x`, it is a high-probability intraday buy.

### 4.3 Future Analysis
*   **Automation**: You can set up a cron job to run the CLI command periodically.
*   **Backtesting**: Use the `Backtesting` page in the dashboard (separate from PKScreener) to validate these strategies on historical data.
