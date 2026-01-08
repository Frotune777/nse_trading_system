# PKScreener: Deep Dive & Technical Analysis

## 1. System Overview
`PKScreener` is a highly optimized, multiprocessing-enabled Indian stock market scanner. Unlike simple loop-based screeners, it uses a sophisticated architecture to handle 2000+ stocks in seconds by leveraging pre-computed data caches and parallel processing.

### 🏗️ High-Level Architecture
```mermaid
graph TD
    CLI[User / CLI Args] --> Main[PKScreenerMain]
    Main --> Config[ConfigManager]
    Main --> Menu[MenuManager]
    Main --> Executor[ScanExecutor / Multiprocessing]
    
    Executor -->|Spawns| Worker[StockScreener (Worker)]
    
    Worker --> Fetcher[DataFetcher (Tiered)]
    Worker --> Algo[Technical Analysis (Pktalib)]
    Worker --> Stats[ScreeningStatistics]
    
    Fetcher --> Tier1[HP Provider (Realtime/Mem)]
    Fetcher --> Tier2[Scalable Fetcher (GitHub Cache)]
    Fetcher --> Tier3[YFinance/NSE (Fallback)]
    
    Worker -->|Result| ResultsQueue
    ResultsQueue --> Processor[ResultProcessor]
    Processor --> Output[Console / Telegram / Excel]
```

## 2. Key Components

### 🧠 The Brain: `StockScreener.py`
This is the worker class that processes individual stocks.
*   **Method**: `screenStocks()`
*   **Logic**:
    1.  Receives stock code and config.
    2.  Fetches data via `fetcher`.
    3.  Calculates indicators (RSI, EMA, etc.) for the required period.
    4.  Applies filters based on `executeOption` (e.g., if opt=6, check Reversal patterns).
    5.  **Control Flow**: Uses exceptions to exit early if a stock fails a check.
        *   `EligibilityConditionNotMet`: Generic failure.
        *   `StockDataEmptyException`: Data fetch failure.
        *   `NotNewlyListed`: Fails "New Listing" check.

### 📡 The Data Layer: `Fetcher.py`
The screener is fast because it doesn't query the NSE/Yahoo API for every request. It uses a **3-Tier Fetching Strategy**:
1.  **High Performance (HP) Provider**: In-memory candle store, optimized for real-time access during market hours.
2.  **Scalable Fetcher**: Downloads pre-computed pickle files from a dedicated GitHub repository (`actions-data-download`). This effectively uses GitHub Actions as a distributed compute/cache layer.
3.  **Fallback**: Standard `yfinance` or `nsepyshell` calls if cache is stale or missing.

### 📐 The Math: `Pktalib.py` & `ScreeningStatistics.py`
A wrapper around `TA-Lib` (Technical Analysis Library).
*   **Resilience**: Tries `import talib`, falls back to `pandas_ta`, then to manual pandas calculation.
*   **Capabilities**:
    *   **Patterns**: CDL_DOJI, CDL_MORNINGSTAR, CDL_ENGULFING, etc.
    *   **Trend**: EMA, SMA, MACD, ADX, SuperTrend, Ichimoku.
    *   **Custom**: Relative Volatility Measure (RVM), Consistency Scores.

## 3. Workflow & Data Flow

When we run `RUNNER=1 pkscreener ...`:

1.  **Initialization (`PKScreenerMain.py`)**:
    *   Parses arguments.
    *   Sets up the `multiprocessing.Manager` queues.
    *   Determines the stock list (Nifty 50, Nifty 500, etc.).

2.  **Execution (`ScanExecutor`)**:
    *    divides the stock list into chunks.
    *   Spawns consumer processes.
    *   Each consumer runs `StockScreener.screenStocks()`.

3.  **Filtering Logic (Example: RSI Buy)**:
    *   User selects Option 5 (RSI).
    *   Worker calculates `Pktalib.RSI(df['Close'], 14)`.
    *   Checks `minRSI < currentRSI < maxRSI`.
    *   If True -> Add to result dict.
    *   If False -> `raise EligibilityConditionNotMet`.

## 4. Extensibility
To add a new scan type:

1.  **Define Option**: Add entry in `MenuOptions.py`.
2.  **Implement Logic**:
    *   Add calculation method in `Pktalib.py` (if it's a standard indicator).
    *   Add logic check in `StockScreener.py` under the new `executeOption` ID.
3.  **Handle Output**: Ensure `screeningDictionary` is updated with the result value for the table.

## 5. Conclusion
PKScreener is a "Check-Engine" style architecture. It prioritizes speed (through caching and multiprocessing) and "fail-fast" filtering (through exceptions). Its reliance on external GitHub caches for historical data is a unique architectural choice that creates a distributed data delivery network without server costs.
