# Trader Start - Comprehensive Project Documentation

## 1. Executive Summary
`trader_start` is a sophisticated algorithmic trading dashboard that merges three powerful domains: **Technical Analysis** (via PKScreener), **Fundamental/Quad Analysis**, and **Machine Learning** (XGBoost/RF models). Built on a modular architecture using FastAPI and Streamlit, it provides a unified interface for traders to screen stocks, analyze deal flow, and generate AI-driven price predictions.

---

## 2. System Architecture

### 🏗️ Core Stack
*   **Frontend**: Streamlit (Dashboard UI, interactive charts via Plotly).
*   **Backend**: FastAPI (Prediction API, model serving).
*   **Data & ML Layer**: Custom Python libraries (`libs/`) using Pandas, NumPy, Scikit-learn, XGBoost.
*   **Infrastructure**: Dockerized services using `uv` for dependency management.

### 📦 Key Modules
| Module | Description | Location |
| :--- | :--- | :--- |
| **PKScreener Adapter** | Bridges the CLI-based PKScreener tool to the GUI, enabling complex technical scans. | `libs/pkscreener_adapter.py` |
| **ML Engine** | End-to-end pipeline for training XGBoost/RandomForest models with time-series splitting. | `libs/ml_pipeline.py` |
| **Quad Analyzer** | Proprietary 4-Pillar scoring system (Fundamental, Technical, Institutional, Macro). | `libs/quad_analyzer.py` |
| **Data Manager** | Handles historical data fetching (NSE), caching, and feature engineering. | `libs/historical_data_manager.py` |

---

## 3. Detailed Feature Breakdown

### A. 🚀 PKScreener Integration (Technical Screening)
*   **Functionality**: Runs over 35+ advanced technical scans including Breakouts, Consolidations, Volume Shockers, and Chart Patterns.
*   **Scope**: Covers Nifty 50, 100, 500, Bank Nifty, Smallcap indices, and **Custom Stock Lists**.
*   **Implementation**: A custom subprocess adapter (`libs/pkscreener_adapter.py`) executes the PKScreener CLI in a headless mode (`RUNNER=1`), bypassing authentication gates and parsing results into Pandas DataFrames for display.
*   **Key Capabilities**:
    *   **Custom Lists**: Upload CSV/Excel files (e.g., Option Chains) to scan specific portfolios.
    *   **Intraday Scanning**: Configure 5m/15m timeframes for live momentum detection.
    *   **Live Filters**: Dynamic adjustment of Volume and RSI thresholds directly from the UI.
*   **Usage**: Navigate to **"🚀 PKScreener"** page, select an Index or Custom List, configure filters, and click Run.

### B. 🤖 ML & AI Engine
*   **Models**: Supports **XGBoost** and **Random Forest** classifiers.
*   **Prediction Targets**:
    *   **2-Class**: Up/Down
    *   **3-Class**: Up/Neutral/Down (Threshold: ±1%)
    *   **5-Class**: Strong Up/Up/Neutral/Down/Strong Down
*   **Features**: Automatically engineers technical indicators (RSI, MACD, Bollinger Bands) via `libs/feature_engineering.py`.
*   **API**: `POST /predict` endpoint returns prediction confidence and probability distribution.

### C. 🏆 Quad Analysis (Holistic Scoring)
Evaluates stocks based on 4 distinct pillars to generate a 0-10 "Quad Score":
1.  **Fundamental**: Valuation (PE, PB), Earnings Growth, Debt/Equity.
2.  **Technical**: Trend (Moving Averages), Momentum (RSI), Volatility.
3.  **Institutional**: FII/DII activity, bulk deals.
4.  **Macro**: Sector performance and broader market indices.
*   **Visuals**: Renders a Radar Chart to visualize the balance between these pillars.

### D. 📊 Deal Analysis
*   **Bulk Deals**: Analyzes NSE bulk/block deal data to identify significant institutional interest using `libs/deal_analyzer.py`.

---

## 4. Developer Guide

### Project Structure
```text
trader_start/
├── api/                # FastAPI backend
│   └── main.py         # API endpoints (/predict, /models)
├── dashboard.py        # Streamlit Frontend application
├── libs/               # Shared logic libraries
│   ├── pkscreener_adapter.py  # PKScreener wrapper or bridge
│   ├── ml_pipeline.py         # ML Training & Prediction logic
│   └── quad_analyzer.py       # 4-Pillar Analysis logic
├── pkscreener/         # PKScreener submodule (source code)
├── docker-compose.yml  # Docker orchestration
└── pyproject.toml      # Dependency configuration (uv)
```

### Setup & Running
**Option 1: Docker (Recommended)**
```bash
docker-compose up --build
```
*   Dashboard: `http://localhost:8501`
*   API Docs: `http://localhost:8000/docs`

**Option 2: Local Development**
1.  **Install Dependencies**:
    ```bash
    uv sync
    ```
2.  **Run API**:
    ```bash
    uvrun uvicorn api.main:app --reload
    ```
3.  **Run Dashboard**:
    ```bash
    streamlit run dashboard.py
    ```

### Troubleshooting Notes
*   **"0 Results" in Scans**: Often caused by `yfinance` connectivity issues or network proxies preventing data download.
*   **"Illegal Instruction"**: Solved by removing `tensorflow`/`keras` dependency. Use the simplified ML libraries provided.
*   **PKScreener Config**: Managed via `pkscreener.ini`. `onlyStageTwoStocks=n` is set to ensure broad scanning.

## 6. System Knowledge Base (Deep Dive)
For comprehensive technical details, refer to:
*   **[System Architecture & Flow](system_architecture.md)**: Detailed data pipelines, control flow diagrams, and module interactions.
*   **[Database Schema](database_schema.md)**: Full SQL definitions for `trading.db` and `market.db`.
*   **[PKScreener Integration](pkscreener_integration_guide.md)**: Specifics on the Scanning Engine.
*   **[ML Implementation](ml_implementation_guide.md)**: Details on the Machine Learning pipeline.

## 7. License & Credits
*   **Trader Start**: Custom proprietary dashboard.
## 8. Strategic Roadmap
*   **[Master Implementation Checklist](master_implementation_checklist.md)** - Complete TODO list with 84 items across 7 phases (START HERE for implementation)
*   **[Gap Analysis](gap_analysis.md)** - Current vs target state analysis (27% complete)
*   **[SaaS Transformation](saas_roadmap.md)** - A professional assessment and architectural roadmap to evolve this MVP into a global-scale SaaS platform.
*   **[Quantitative System Architecture](quantitative_system_architecture_plan.md)** - Deep-dive blueprint for building a high-fidelity, explainable AI trading engine (Data Strategy -> Backtesting -> Decision).

