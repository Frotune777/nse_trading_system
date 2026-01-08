# System Architecture & Flow Guide

This document provides a technical deep-dive into the `trader_start` architecture, designed to help LLMs and developers understand the implementation flow, data pipelines, and module interactions.

## 1. High-Level Architecture

The system follows a **Modular Monolith** pattern, primarily driven by a Streamlit Frontend (`dashboard.py`) that interacts with various "Engines" (libs) and a FastAPI Backend (`api/`).

```mermaid
graph TD
    User[User / Trader] --> UI[Streamlit Dashboard (dashboard.py)]
    
    subgraph Frontend Layer
        UI --> PagePK[Page: PKScreener]
        UI --> PageML[Page: ML Predictions]
        UI --> PageQuad[Page: Quad Analysis]
    end
    
    subgraph Logic Layer (libs/)
        PagePK --> Adapter[PKScreenerAdapter]
        PageML --> Pipeline[MLPipeline]
        PageQuad --> Quad[QuadAnalyzer]
        Pipeline --> FeatEng[FeatureEngineer]
    end
    
    subgraph Data Layer
        Adapter --> CLI[PKScreener CLI (Subprocess)]
        CLI --> Cache[Results/Cache (FileSystem)]
        Pipeline --> DB[(trading.db)]
        Quad --> DB
        Cache --> Adapter
    end
```

## 2. Core Modules & Units

### 2.1 PKScreener Integration
*   **File**: `libs/pkscreener_adapter.py`
*   **Purpose**: Interfaces with the external `pkscreener` CLI tool.
*   **Flow**:
    1.  Receives configuration (Timeframe, Strategy) from UI.
    2.  Updates `pkscreener.ini` dynamically.
    3.  Runs `python pkscreenercli.py` via `asyncio.subprocess`.
    4.  Locates result CSV in `results/Reports/` using recursive search.
    5.  Returns Pandas DataFrame.
*   **Key Data**: Custom Stock Lists stored in `trading.db` (`custom_stock_lists` table).

### 2.2 Machine Learning Engine
*   **File**: `libs/ml_pipeline.py`
*   **Purpose**: End-to-end training and prediction.
*   **Flow**:
    1.  `load_data()`: Fetches OHLCV data from `libs/historical_data_manager.py`.
    2.  `prepare_features()`: Uses `libs/feature_engineering.py` to add RSI, MACD, BBands.
    3.  `train()`: Trains XGBoost/RandomForest with time-series cross-validation.
    4.  `predict()`: Generates probabilities for Up/Down/Neutral.
    5.  `save()`: Persists model to `models/*.joblib`.

### 2.3 Quad Analyzer
*   **File**: `libs/quad_analyzer.py`
*   **Purpose**: multi-factor scoring.
*   **Pillars**:
    *   **Fundamental**: PE, PB, PEG (Mock/API data).
    *   **Technical**: Trend strength (ADX), Momentum (RSI).
    *   **Institutional**: FII/DII Dta (from `market.db`).
    *   **Macro**: Sector trends.

## 3. Database Schema Overview

The system uses two SQLite databases in `data/`:

### 3.1 `trading.db` (Application State)
*   **`custom_stock_lists`**: User-saved watchlists for scanning.
*   **`ml_predictions`**: History of all model predictions for accuracy tracking.
*   **`ml_model_performance`**: Meta-metrics of model training runs.

### 3.2 `market.db` (Market Data)
*   **`bulk_deals`**: Large trade records.
*   **`fii_stats`**: Institutional flow data.

*(See `docs/database_schema.md` for full SQL definitions)*

## 4. Directory Structure Review

```text
trader_start/
├── api/                  # Backend API (FastAPI)
├── data/                 # SQLite DBs and Parquet files
├── docs/                 # Documentation (Knowledge Base)
├── libs/                 # Business Logic
│   ├── feature_engineering.py
│   ├── historical_data_manager.py
│   ├── ml_pipeline.py
│   ├── pkscreener_adapter.py  <-- Key Integration
│   └── quad_analyzer.py
├── logs/                 # System logs
├── models/               # Saved ML models (.joblib, .pth)
├── pkscreener/           # Submodule: PKScreener Source
├── results/              # PKScreener Scan Outputs
├── dashboard.py          # Main Entry Point (Streamlit)
└── pkscreener.ini        # Configuration File
```

## 5. E2E Data Flow Example: Custom Scan

1.  **Input**: User performs "Upload New List" -> `FO_Stocks.csv`.
2.  **Storage**: Dashboard saves symbols to `trading.db` -> `custom_stock_lists`.
3.  **Action**: User runs "Momentum Scan" on this list.
4.  **Process**:
    *   `dashboard.py` retrieves symbols from DB.
    *   `pkscreener_adapter` calls CLI with `--stocklist`.
    *   CLI scans and saves CSV.
    *   Adapter reads CSV.
5.  **Output**: Dashboard displays results table.
