PKDevTools
MADE-IN-INDIA GitHub release (latest by date) GitHub all releases GitHub CodeFactor BADGE

github license Downloads latest download PyPI is wheel Coverage Status codecov

Documentation PKDevTools Test - New Features 1. PKDevTools Build - New Release

Table of Contents
What is PKDevTools?
Installation
Quick Start
Architecture Overview
Core Modules
Data Provider System
Logging Framework
Database Management
Environment & Configuration
Multiprocessing
Telegram Integration
GitHub Integration
Pub/Sub Event System
Utilities
API Reference
Environment Variables
Contributing
License
What is PKDevTools?
PKDevTools is a comprehensive Python toolkit designed for building high-performance financial applications. It provides:

🚀 Unified Data Provider - Multi-source stock data with automatic failover
📝 Thread-Safe Logging - Process-safe logging with filtering and caller info
🗄️ Database Management - SQLite + Turso (libsql) with sync capabilities
⚡ Multiprocessing - Cross-platform multiprocessing with shared state
📱 Telegram Integration - Send messages, documents, and media
🔄 GitHub Automation - Workflow triggers, commits, and API integration
📡 Event System - Pub/Sub pattern for decoupled components
🛠️ Utilities - Caching, archiving, HTTP fetching, and more
This toolkit serves as the foundation for PKScreener, PKBrokers, and PKNSETools.

Installation
From PyPI (Recommended)
pip install PKDevTools
From Source
git clone https://github.com/pkjmesra/PKDevTools.git
cd PKDevTools
pip install -r requirements.txt
pip install -e .
Requirements
Python 3.9+
See requirements.txt for full dependency list
Quick Start
from PKDevTools.classes import get_data_provider, get_scalable_fetcher
from PKDevTools.classes.log import default_logger, setup_custom_logger

# Initialize logging (set environment variable first)
import os
os.environ["PKDevTools_Default_Log_Level"] = "10"  # DEBUG level

# Get stock data
provider = get_data_provider()
df = provider.get_stock_data("RELIANCE", interval="day", count=100)

# Use the logger
logger = default_logger()
logger.info("Data fetched successfully!")
Architecture Overview
┌─────────────────────────────────────────────────────────────────────────┐
│                           PKDevTools Architecture                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │  PKDataProvider  │  │ PKScalableData   │  │  DBManager       │       │
│  │  (Stock Data)    │  │ Fetcher (GitHub) │  │  (Turso/SQLite)  │       │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘       │
│           │                     │                     │                 │
│           └─────────────────────┼─────────────────────┘                 │
│                                 │                                       │
│                    ┌────────────▼────────────┐                          │
│                    │     Core Services       │                          │
│                    ├─────────────────────────┤                          │
│                    │ • Logging (filterlogger)│                          │
│                    │ • Environment Config    │                          │
│                    │ • HTTP Fetcher          │                          │
│                    │ • Archiver (Caching)    │                          │
│                    └────────────┬────────────┘                          │
│                                 │                                       │
│           ┌─────────────────────┼─────────────────────┐                 │
│           │                     │                     │                 │
│  ┌────────▼─────────┐  ┌────────▼───────┐  ┌──────────▼───────┐         │
│  │   Telegram       │  │  GitHub        │  │  Pub/Sub Events  │         │
│  │   Integration    │  │  Integration   │  │  (blinker)       │         │
│  └──────────────────┘  └────────────────┘  └──────────────────┘         │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐       │
│  │                    Multiprocessing Layer                     │       │
│  │  PKMultiProcessorClient | PKJoinableQueue | Process Logging  │       │
│  └──────────────────────────────────────────────────────────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
See Also: 1. Architecture 2. API Reference

Core Modules
1. Data Provider System
The unified data provider fetches stock OHLCV data from multiple sources with automatic failover.

PKDataProvider
from PKDevTools.classes.PKDataProvider import PKDataProvider, get_data_provider

# Get singleton instance
provider = get_data_provider()

# Fetch stock data with automatic source selection
# Priority: Real-time (PKBrokers) → Local Pickle → Remote GitHub Pickle
df = provider.get_stock_data("RELIANCE", interval="5m", count=50)

# Fetch multiple stocks
data = provider.get_multiple_stocks(["RELIANCE", "TCS", "INFY"], interval="day")

# Check real-time availability
if provider.is_realtime_available():
    price = provider.get_latest_price("INFY")
    ohlcv = provider.get_realtime_ohlcv("INFY")
Supported Intervals:

Interval	Description
1m, 2m, 3m, 4m, 5m	Minute candles
10m, 15m, 30m, 60m	Extended minute candles
day	Daily candles
PKScalableDataFetcher
GitHub-based data fetcher without Telegram dependency:

from PKDevTools.classes.PKScalableDataFetcher import PKScalableDataFetcher, get_scalable_fetcher

fetcher = get_scalable_fetcher()

# Fetch from GitHub raw content
data = fetcher.fetch_stock_data("RELIANCE")
2. Logging Framework
Thread and process-safe logging with automatic caller information injection.

Setup and Usage
import os
from PKDevTools.classes.log import (
    setup_custom_logger,
    default_logger,
    log_to,
    tracelog
)

# Enable logging via environment variable
os.environ["PKDevTools_Default_Log_Level"] = "10"  # DEBUG=10, INFO=20, WARNING=30, ERROR=40

# Setup custom logger
logger = setup_custom_logger(
    name="MyApp",
    levelname=10,  # DEBUG
    log_file_path="/path/to/logs.txt",
    filter="IMPORTANT"  # Only log messages containing "IMPORTANT"
)

# Use default logger
logger = default_logger()
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")  # Automatically includes traceback
logger.critical("Critical message")
Decorator for Function Tracing
from PKDevTools.classes.log import log_to, default_logger

@log_to(default_logger().info)
def my_function(param1, param2):
    """Function calls are automatically logged with arguments and timing"""
    return param1 + param2
Log Levels
Level	Value	Description
DEBUG	10	Detailed diagnostic information
INFO	20	General operational messages
WARNING	30	Warning messages
ERROR	40	Error messages with traceback
CRITICAL	50	Critical failures
Key Classes
filterlogger: Thread/process-safe logger with filtering
emptylogger: No-op logger when logging is disabled
colors: ANSI color codes for terminal formatting
3. Database Management
Dual database support with SQLite (local) and Turso/libsql (cloud).

DBManager
from PKDevTools.classes.DBManager import DBManager, PKUser

# Initialize manager (uses environment variables for Turso connection)
db = DBManager()

# User operations
user = db.getUserByID(12345)
otp, subscription_model, validity, user = db.getOTP(
    userID=12345,
    userName="john_doe",
    fullName="John Doe"
)

# Scanner job subscriptions
db.subscribeScannerForUser(userID=12345, scannerIDs="X:12:9,X:12:31")
subscriptions = db.getSubscribedScannersByUser(userID=12345)
DatabaseSyncChecker
from PKDevTools.classes.DatabaseSyncChecker import DatabaseSyncChecker

checker = DatabaseSyncChecker(
    local_db_path="./local.db",
    turso_url="libsql://your-db.turso.io",
    turso_auth_token="your-token"
)

needs_sync, messages = checker.check_sync_status()
checker.print_counts()
Key Models
PKUser: User model with subscription management
PKScannerJob: Scanner job subscription model
PKUserModel: Enum for database column mapping
4. Environment & Configuration
Centralized environment variable and secrets management.

PKEnvironment
from PKDevTools.classes.Environment import PKEnvironment

# Singleton instance - loads from .env.dev file
env = PKEnvironment()

# Access secrets as attributes
github_token = env.GITHUB_TOKEN
chat_id = env.CHAT_ID
telegram_token = env.TOKEN

# Access all secrets
all_secrets = env.allSecrets  # Returns dict
Required Environment Variables
Variable	Description
GITHUB_TOKEN	GitHub API token for repository operations
CHAT_ID	Telegram channel/chat ID
TOKEN	Telegram bot token
chat_idADMIN	Admin chat ID for notifications
PKDevTools_Default_Log_Level	Logging level (10=DEBUG, 20=INFO, etc.)
5. Multiprocessing
Cross-platform multiprocessing with shared state and logging support.

PKMultiProcessorClient
from PKDevTools.classes.PKMultiProcessorClient import PKMultiProcessorClient
from PKDevTools.classes.PKJoinableQueue import PKJoinableQueue
from multiprocessing import Manager

# Create shared resources
manager = Manager()
task_queue = PKJoinableQueue()
result_queue = PKJoinableQueue()

# Define processor method
def process_task(stock_code, data_dict, result_dict):
    # Process stock data
    result = analyze_stock(stock_code)
    return result

# Create worker processes
workers = []
for i in range(4):  # 4 worker processes
    worker = PKMultiProcessorClient(
        processorMethod=process_task,
        task_queue=task_queue,
        result_queue=result_queue,
        objectDictionaryPrimary=manager.dict(),
        keyboardInterruptEvent=manager.Event()
    )
    worker.start()
    workers.append(worker)

# Add tasks
for stock in ["RELIANCE", "TCS", "INFY"]:
    task_queue.put(stock)

# Signal completion and wait
task_queue.join()
PKJoinableQueue
Enhanced multiprocessing queue with join support:

from PKDevTools.classes.PKJoinableQueue import PKJoinableQueue

queue = PKJoinableQueue()
queue.put("task1")
queue.put("task2")

# Worker processes call task_done() after processing
queue.join()  # Blocks until all tasks completed
6. Telegram Integration
Send messages, documents, and media to Telegram.

Basic Usage
from PKDevTools.classes.Telegram import (
    send_message,
    send_document,
    send_photo,
    send_media_group
)

# Send text message
send_message(
    message="Hello from PKDevTools!",
    userID="-1001234567890",
    parse_type="HTML"
)

# Send document
send_document(
    file_path="/path/to/file.pdf",
    message="Here's your report",
    userID="-1001234567890"
)

# Send photo
send_photo(
    photo_path="/path/to/image.png",
    caption="Analysis results",
    userID="-1001234567890"
)

# Send multiple documents as media group
send_media_group(
    file_paths=["/path/to/file1.pdf", "/path/to/file2.pdf"],
    message="Multiple reports",
    userID="-1001234567890"
)
Message Formatting
Messages support HTML formatting:

send_message(
    message="<b>Bold</b> <i>Italic</i> <code>Code</code>",
    userID=chat_id,
    parse_type="HTML"
)
7. GitHub Integration
Automate GitHub operations including commits, workflow triggers, and API calls.

Committer
from PKDevTools.classes.Committer import Committer

# Copy files
Committer.copySourceToDestination(
    srcPath="results/*.pkl",
    destPath="backup/"
)

# Commit and push changes
Committer.commitTempOutcomes(
    addPath="results/*",
    commitMessage="[Auto] Updated results",
    branchName="main"
)

# Execute OS command with logging
Committer.execOSCommand("git status", showStatus=True)
WorkflowManager
from PKDevTools.classes.WorkflowManager import WorkflowManager

# Trigger GitHub Actions workflow
WorkflowManager.trigger_workflow(
    repo="pkjmesra/PKScreener",
    workflow_id="scan.yml",
    ref="main",
    inputs={"scan_type": "full"}
)
githubutilities
from PKDevTools.classes.githubutilities import (
    getWorkflowRunByName,
    stopWorkflow,
    getLatestRelease
)

# Get latest release
release = getLatestRelease("pkjmesra/PKScreener")

# Get workflow run
run = getWorkflowRunByName("pkjmesra/PKScreener", "Build")
8. Pub/Sub Event System
Decoupled event publishing and subscription using blinker.

Publishing Events
from PKDevTools.classes.pubsub.publisher import PKUserService
from PKDevTools.classes.pubsub.events import globalEventsSignal

# Using PKUserService
service = PKUserService()
service.notify_user(scannerID="X:12:9", notification="Scan complete!")

# Direct signal publishing
globalEventsSignal.send(
    sender=self,
    eventType="custom",
    data={"key": "value"}
)
Subscribing to Events
from PKDevTools.classes.pubsub.events import globalEventsSignal

def my_handler(sender, **kwargs):
    scanner_id = kwargs.get('scannerID')
    notification = kwargs.get('notification')
    print(f"Received: {scanner_id} - {notification}")

# Subscribe to events
globalEventsSignal.connect(my_handler)
9. Utilities
Archiver (Caching & File Management)
from PKDevTools.classes import Archiver

# Get user data directory
data_dir = Archiver.get_user_data_dir()

# Get user outputs directory
outputs_dir = Archiver.get_user_outputs_dir()

# Cache binary data
Archiver.cacheFile(binary_data, "cache_file.bin")

# Find cached file
data, path, modified_time = Archiver.findFile("cache_file.bin")

# Get last modified datetime
modified = Archiver.get_last_modified_datetime("/path/to/file")
Fetcher (HTTP Requests)
from PKDevTools.classes.Fetcher import fetcher

f = fetcher()

# Fetch URL with caching
response = f.fetchURL("https://api.example.com/data")

# Fetch with custom headers
response = f.fetchURL(
    url="https://api.example.com/data",
    headers={"Authorization": "Bearer token"}
)
PKDateUtilities
from PKDevTools.classes.PKDateUtilities import PKDateUtilities

# Check if market is open
is_open = PKDateUtilities.isTradingTime()

# Check if today is a holiday
is_holiday = PKDateUtilities.isTradingHoliday()

# Get current IST time
ist_now = PKDateUtilities.currentDateTime()

# Get trading day offset
trading_date = PKDateUtilities.tradingDate()
PKTimer
from PKDevTools.classes.PKTimer import PKTimer

# Measure execution time
with PKTimer("Operation name"):
    # Code to measure
    perform_operation()
ColorText
from PKDevTools.classes.ColorText import colorText

# Print colored text
print(colorText.GREEN + "Success!" + colorText.END)
print(colorText.FAIL + "Error!" + colorText.END)
print(colorText.WARN + "Warning!" + colorText.END)
FunctionTimeouts
from PKDevTools.classes.FunctionTimeouts import exit_after

@exit_after(5)  # Timeout after 5 seconds
def slow_function():
    # Long running operation
    pass
API Reference
Main Exports
from PKDevTools.classes import (
    # Data Providers
    PKDataProvider,
    get_data_provider,
    PKScalableDataFetcher,
    get_scalable_fetcher,
    
    # Version
    VERSION,
)
Module Structure
PKDevTools/
├── classes/
│   ├── __init__.py              # Main exports
│   ├── PKDataProvider.py        # Unified data provider
│   ├── PKScalableDataFetcher.py # GitHub-based fetcher
│   ├── log.py                   # Logging framework
│   ├── DBManager.py             # Database management
│   ├── Environment.py           # Environment/secrets
│   ├── Fetcher.py               # HTTP client
│   ├── Telegram.py              # Telegram integration
│   ├── Committer.py             # Git operations
│   ├── WorkflowManager.py       # GitHub Actions
│   ├── PKMultiProcessorClient.py # Multiprocessing
│   ├── PKJoinableQueue.py       # Enhanced queue
│   ├── Archiver.py              # Caching/files
│   ├── PKDateUtilities.py       # Date/time utilities
│   ├── pubsub/                  # Event system
│   │   ├── events.py            # Signal definitions
│   │   ├── publisher.py         # Event publishing
│   │   └── subscriber.py        # Event handling
│   └── ...                      # Other utilities
└── release.md                   # Release notes
Environment Variables
Variable	Required	Description
PKDevTools_Default_Log_Level	No	Logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR)
GITHUB_TOKEN	Yes*	GitHub API token
TOKEN	Yes*	Telegram bot token
CHAT_ID	Yes*	Default Telegram chat ID
chat_idADMIN	No	Admin notification chat ID
TURSO_DB_URL	No	Turso database URL
TURSO_DB_AUTH_TOKEN	No	Turso authentication token
*Required for respective functionality

Contributing
We welcome contributions! Please follow these guidelines:

Development Setup
Fork the repository
Clone your fork:
git clone https://github.com/YOUR_USERNAME/PKDevTools.git
cd PKDevTools
Create a virtual environment:
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
Install development dependencies:
pip install -r requirements.txt
pip install -e .
Running Tests
# Run all tests
pytest test/

# Run with coverage
pytest --cov=PKDevTools test/

# Run specific test file
pytest test/DBManager_test.py
Code Style
We use ruff for linting:

ruff check PKDevTools/
ruff format PKDevTools/
Pull Request Guidelines
Create a feature branch from main
Write tests for new functionality
Ensure all tests pass
Update documentation as needed
Submit a pull request with a clear description
See CONTRIBUTING.md for detailed guidelines.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Related Projects
PKScreener - Stock screening application
PKBrokers - Broker integration and real-time data
PKNSETools - NSE market data tools


PKNSETools
MADE-IN-INDIA PyPI is wheel github license

A comprehensive Python library for fetching stock market data from the National Stock Exchange (NSE) of India and NASDAQ.

Table of Contents
What is PKNSETools?
Installation
Quick Start
Architecture Overview
Core Modules
NSE Stock Data Fetcher
NSE API (Benny)
Intraday Data
Historical Data
All Stocks Data
NASDAQ Index
Morningstar Tools
API Reference
Index Maps
Contributing
Related Projects
What is PKNSETools?
PKNSETools provides tools for fetching and analyzing stock market data from NSE India. Key features include:

📊 Multi-Index Support - Nifty 50, Nifty Next 50, Nifty 500, and more
🔄 Real-Time Intraday Data - Live market data during trading hours
📈 Historical Data - Up to 3 years of historical OHLCV data
🌐 Multiple Sources - NSE official API, archives, and GitHub cache
🚀 High-Performance Integration - Works with PKBrokers for real-time data
📱 NASDAQ Support - Fetch NASDAQ index data
⭐ Morningstar Integration - Fair value and stock ratings
This library is part of the PKScreener ecosystem.

Installation
From PyPI
pip install PKNSETools
From Source
git clone https://github.com/pkjmesra/PKNSETools.git
cd PKNSETools
pip install -r requirements.txt
pip install -e .
Requirements
Python 3.9+
See requirements.txt for dependencies
Quick Start
Fetch Stock Data
from PKNSETools import nseStockDataFetcher

# Initialize fetcher
fetcher = nseStockDataFetcher()

# Fetch OHLCV data for a stock
df = fetcher.fetchStockData(
    stockCode="RELIANCE",
    period="1y",       # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max
    interval="1d"      # 1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo
)

print(df.head())
Get Index Constituents
from PKNSETools import nseStockDataFetcher

fetcher = nseStockDataFetcher()

# Get Nifty 50 stocks
nifty50_stocks = fetcher.fetchStockCodes(1)  # 1 = Nifty 50

# Get all NSE stocks
all_stocks = fetcher.fetchStockCodes(12)  # 12 = All equities
Use NSE API Directly
from PKNSETools.Benny.NSE import NSE

nse = NSE(download_folder="./data")

# Get stock quote
quote = nse.quote("RELIANCE")
print(f"LTP: {quote['priceInfo']['lastPrice']}")

# Get option chain
chain = nse.optionChain("NIFTY")

# Get market status
status = nse.marketStatus()
Architecture Overview
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PKNSETools Architecture                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │                    Application Layer                           │         │
│  │              PKScreener | Custom Applications                  │         │
│  └─────────────────────────────┬──────────────────────────────────┘         │
│                                │                                            │
│  ┌─────────────────────────────▼──────────────────────────────────┐         │
│  │                  nseStockDataFetcher                           │         │
│  │    (Unified data fetcher with source auto-selection)           │         │
│  └─────────────────────────────┬──────────────────────────────────┘         │
│                                │                                            │
│       ┌────────────────────────┼────────────────────────┐                   │
│       │                        │                        │                   │
│  ┌────▼────┐           ┌───────▼───────┐        ┌───────▼───────┐           │
│  │PKBrokers│           │  NSE API      │        │ yfinance      │           │
│  │(Real-   │           │  (Official)   │        │ (Fallback)    │           │
│  │ time)   │           │               │        │               │           │
│  └─────────┘           └───────────────┘        └───────────────┘           │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                      Core Modules                                │       │
│  ├──────────────────────────────────────────────────────────────────┤       │
│  │  NSE (Benny)     │  Intra_Day    │  PKCompanyStock  │ PKAllStocks│       │
│  │  PKNasdaqIndex   │  Morningstar  │  PKCompanyGeneral             │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                      Data Sources                                │       │
│  ├──────────────────────────────────────────────────────────────────┤       │
│  │  NSE India API   │  NSE Archives  │  GitHub Cache  │  yfinance   │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
Core Modules
1. NSE Stock Data Fetcher
The main interface for fetching stock data with automatic source selection.

from PKNSETools import nseStockDataFetcher

fetcher = nseStockDataFetcher()
fetchStockData(stockCode, period, interval, start, end)
Fetch OHLCV data for a stock.

Parameters:

stockCode (str): NSE symbol (e.g., "RELIANCE", "TCS")
period (str): Data period - "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"
interval (str): Candle interval - "1m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"
start (datetime, optional): Start date
end (datetime, optional): End date
Returns: pd.DataFrame with Date, Open, High, Low, Close, Volume columns

Example:

# Last 1 year daily data
df = fetcher.fetchStockData("INFY", period="1y", interval="1d")

# Last 5 days 15-minute data
df = fetcher.fetchStockData("TCS", period="5d", interval="15m")

# Custom date range
from datetime import datetime
df = fetcher.fetchStockData(
    "HDFC",
    start=datetime(2024, 1, 1),
    end=datetime(2024, 6, 30),
    interval="1d"
)
Data Source Priority
PKBrokers Real-time (if available and market is open)
NSE Official API (primary source)
yfinance (fallback)
fetchStockCodes(index, stockCode=None)
Fetch stock codes for an index.

Parameters:

index (int): Index identifier (see Index Maps)
stockCode (str, optional): Filter for specific stock
Returns: List of stock codes

Example:

# Get Nifty 50 constituents
nifty50 = fetcher.fetchStockCodes(1)
print(f"Nifty 50 stocks: {len(nifty50)}")

# Get all NSE equities
all_stocks = fetcher.fetchStockCodes(12)
print(f"Total NSE stocks: {len(all_stocks)}")

# Get F&O stocks
fno_stocks = fetcher.fetchStockCodes(14)
fetchLatestNiftyDaily(proxyServer=None)
Fetch latest Nifty 50 index data.

Returns: pd.DataFrame with index data

fetchNiftyCodes(niftyIndex, proxyServer=None)
Fetch Nifty index constituents from GitHub cache.

2. NSE API (Benny)
Direct interface to NSE India's official API.

from PKNSETools.Benny.NSE import NSE

nse = NSE(download_folder="./data")
Stock Quotes
# Get detailed quote
quote = nse.quote("RELIANCE")
print(f"LTP: {quote['priceInfo']['lastPrice']}")
print(f"Change: {quote['priceInfo']['change']}")
print(f"% Change: {quote['priceInfo']['pChange']}%")

# Get quote with trade info
trade_info = nse.quote("TCS", trade_info=True)
Option Chain
# Get option chain for index
chain = nse.optionChain("NIFTY")

# Get option chain for stock
chain = nse.optionChain("RELIANCE", optionType="stock")

# Available indices: banknifty, nifty, finnifty, niftyit
Market Data
# Market status
status = nse.marketStatus()

# Trading holidays
holidays = nse.holidays()

# Advances/Declines
advances = nse.advanceDecline()

# Pre-open market data
preopen = nse.preOpen()

# Market turnover
turnover = nse.marketTurnover()
Index Data
# Get all indices
indices = nse.allIndices()

# Get specific index data
nifty50 = nse.indexData("NIFTY 50")

# Get index constituents
constituents = nse.indexStocks("NIFTY 50")
Block/Bulk Deals
# Block deals
block = nse.blockDeal()

# Bulk deals
bulk = nse.bulkDeal()
Historical Data
# Get historical data
history = nse.equityHistory(
    symbol="RELIANCE",
    series="EQ",
    from_date="01-01-2024",
    to_date="30-06-2024"
)
Download Reports
# Download bhavcopy
nse.bhavCopyFull(date="2024-12-20")

# Download index report
nse.indexReport(date="2024-12-20")
3. Intraday Data
Real-time intraday data during market hours.

from PKNSETools import Intra_Day

# Initialize for a stock
intraday = Intra_Day("RELIANCE")

# Get intraday data (9:00 AM to now)
timestamps, prices = intraday.intraDay()

# For NIFTY indices
nifty_intra = Intra_Day("NIFTY 50")
timestamps, prices = nifty_intra.nifty_intraDay()
Features
Rate-limited (3 requests/second)
Session-based with cookie handling
Works during market hours (9:15 AM - 3:30 PM IST)
4. Historical Data
Fetch up to 3 years of historical data.

from PKNSETools import get_Company_History_Data, get_nifty_History_Data

# Company historical data
df = get_Company_History_Data(
    company="RELIANCE",
    from_date="01-01-2023",
    to_date="31-12-2023"
)

# Nifty index historical data
df = get_nifty_History_Data(
    indexName="NIFTY 50",
    from_date="01-01-2023",
    to_date="31-12-2023"
)
5. All Stocks Data
Fetch daily report for all stocks.

from PKNSETools import getTodayData

# Get today's data for all stocks
nifty_data, companies_data = getTodayData()

# Returns tuple:
# - nifty_data: NIFTY index performance
# - companies_data: All company data with OHLCV, volume, etc.
6. NASDAQ Index
Fetch NASDAQ index data.

from PKNSETools.Nasdaq.PKNasdaqIndex import PKNasdaqIndex

nasdaq = PKNasdaqIndex()

# Get NASDAQ-100 constituents
constituents = nasdaq.get_nasdaq100()

# Get NASDAQ Composite data
composite = nasdaq.get_nasdaq_composite()
7. Morningstar Tools
Integration with Morningstar for fundamental data.

from PKNSETools.morningstartools import PKMorningstarDataFetcher

# Initialize fetcher
ms = PKMorningstarDataFetcher()

# Get stock fair value
fair_value = ms.get_fair_value("RELIANCE")

# Get stock rating
rating = ms.get_stock_rating("TCS")

# Get mutual fund data
mf_data = ms.get_mutual_fund("HDFC Equity Fund")
Available Data
Fair value estimates
Star ratings
Analyst reports
Financial ratios
Mutual fund performance
API Reference
Main Exports
from PKNSETools import (
    # Stock Data
    nseStockDataFetcher,
    
    # Historical Data
    get_Company_History_Data,
    get_nifty_History_Data,
    
    # Intraday
    Intra_Day,
    
    # All Stocks
    getTodayData,
    
    # Constants
    NSE_INDEX_MAP,
    REPO_INDEX_MAP,
)

from PKNSETools.Benny.NSE import NSE

from PKNSETools.Nasdaq.PKNasdaqIndex import PKNasdaqIndex

from PKNSETools.morningstartools import PKMorningstarDataFetcher
Module Structure
PKNSETools/
├── __init__.py                 # Main exports
├── PKAllStocks.py              # All stocks daily data
├── PKCompanyGeneral.py         # Company general info
├── PKCompanyStock.py           # Company historical data
├── PKConstants.py              # URL constants and headers
├── PKIntraDay.py               # Intraday data
├── PKNSEStockDataFetcher.py    # Main stock data fetcher
├── Benny/
│   ├── __init__.py
│   └── NSE.py                  # NSE API wrapper
├── Nasdaq/
│   ├── __init__.py
│   └── PKNasdaqIndex.py        # NASDAQ index tools
└── morningstartools/
    ├── __init__.py
    ├── PKMorningstarDataFetcher.py
    ├── funds.py                # Mutual fund data
    ├── stock.py                # Stock fundamental data
    ├── security.py             # Security data
    ├── search.py               # Search functionality
    ├── NSEStockDB.py           # Stock database
    ├── NSEStockFairValueDB.py  # Fair value database
    └── NSEStockMFIDB.py        # MFI database
Index Maps
NSE_INDEX_MAP (Direct NSE URLs)
Index	Description	URL
1	Nifty 50	ind_nifty50list.csv
2	Nifty Next 50	ind_niftynext50list.csv
3	Nifty 100	ind_nifty100list.csv
4	Nifty 200	ind_nifty200list.csv
5	Nifty 500	ind_nifty500list.csv
6	Nifty Smallcap 50	ind_niftysmallcap50list.csv
7	Nifty Smallcap 100	ind_niftysmallcap100list.csv
8	Nifty Smallcap 250	ind_niftysmallcap250list.csv
9	Nifty Midcap 50	ind_niftymidcap50list.csv
10	Nifty Midcap 100	ind_niftymidcap100list.csv
11	Nifty Midcap 150	ind_niftymidcap150list.csv
12	All Equities	EQUITY_L.csv
14	F&O Stocks	NSE_FO_SosScheme.csv
REPO_INDEX_MAP (GitHub Cache)
Same indices but fetched from PKScreener's GitHub repository for reliability.

Constants
from PKNSETools.PKConstants import (
    _base_domain,           # "https://www.nseindia.com"
    _headers,               # Default request headers
    _head,                  # Headers with cookies
    _quote_url_path,        # Quote API path
    _chart_data_open_url,   # Chart data URL
)
Contributing
Development Setup
git clone https://github.com/pkjmesra/PKNSETools.git
cd PKNSETools
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
Running Tests
pytest test/
Code Style
ruff check PKNSETools/
ruff format PKNSETools/




PKBrokers
MADE-IN-INDIA GitHub release (latest by date) Downloads latest download Docker Pulls

Platforms	Windows	Linux(x64) Linux(arm64)	Mac OS(x64) Mac OS(arm64)	Docker Status
Package / Docs	Documentation OpenSSF Best Practices	PyPI	is wheel	github license
Tests/Code-Quality	CodeFactor	Coverage Status	codecov	After Market
Table of Contents
What is PKBrokers?
Installation
Quick Start
Architecture Overview
Core Modules
In-Memory Candle Store
Data Manager
Kite Instruments
Tick Watcher
Local Candle Database
Telegram Bots
Authentication
GitHub Actions Workflows
PKL Generator Script
API Reference
Environment Variables
Contributing
Related Projects
What is PKBrokers?
PKBrokers is a high-performance Python library for connecting to stock brokers (primarily Zerodha's Kite Connect) to fetch real-time market data, instruments, and ticks. Key features include:

🚀 High-Performance Candle Store - O(1) access to OHLCV candles across 10 timeframes
📊 Real-Time Tick Processing - WebSocket-based tick aggregation
💾 Multi-Source Data Management - SQLite, Turso, pickle files, and Kite API
🤖 Telegram Bot Integration - Distribute tick data via Telegram
🔐 Automated Authentication - TOTP-based Kite login
📦 24/7 Data Availability - GitHub-based data persistence
This library is part of the PKScreener ecosystem.

Installation
From PyPI
pip install pkbrokers
From Source
git clone https://github.com/pkjmesra/pkbrokers.git
cd pkbrokers
pip install -r requirements.txt
pip install -e .
Requirements
Python 3.9+
Zerodha Kite Connect account (for real-time data)
See requirements.txt for dependencies
Quick Start
High-Performance Data Provider
from pkbrokers.kite import get_candle_store, HighPerformanceDataProvider

# Get singleton candle store
store = get_candle_store()

# Or use high-level data provider
provider = HighPerformanceDataProvider()

# Get 5-minute candles for any stock
df = provider.get_stock_data("RELIANCE", interval="5m", count=50)

# Get current day's OHLCV
ohlcv = provider.get_current_ohlcv("TCS")
print(f"Open: {ohlcv['open']}, High: {ohlcv['high']}, Low: {ohlcv['low']}, Close: {ohlcv['close']}")
Data Manager (Multi-Source)
from pkbrokers.kite.datamanager import InstrumentDataManager

# Initialize manager
manager = InstrumentDataManager()

# Execute data synchronization
success = manager.execute()

if success:
    # Access stock data
    reliance = manager.pickle_data["RELIANCE"]
    df = pd.DataFrame(
        data=reliance['data'],
        columns=reliance['columns'],
        index=reliance['index']
    )
    print(f"Shape: {df.shape}")
Kite Authentication
from pkbrokers.kite.examples.externals import kite_auth

# Authenticate and get access token
# Requires KUSER, KPWD, KTOTP environment variables
kite_auth()

# Token is now available as KTOKEN
from PKDevTools.classes.Environment import PKEnvironment
token = PKEnvironment().KTOKEN
Architecture Overview
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PKBrokers Architecture                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │                     Application Layer                          │         │
│  │            PKScreener | Custom Applications                    │         │
│  └─────────────────────────────┬──────────────────────────────────┘         │
│                                │                                            │
│  ┌─────────────────────────────▼──────────────────────────────────┐         │
│  │                      Data Provider API                         │         │
│  │   HighPerformanceDataProvider | InstrumentDataManager          │         │
│  └─────────────────────────────┬──────────────────────────────────┘         │
│                                │                                            │
│       ┌────────────────────────┼────────────────────────┐                   │
│       │                        │                        │                   │
│  ┌────▼────┐           ┌───────▼───────┐        ┌───────▼───────┐           │
│  │InMemory │           │  Local SQLite │        │ Remote Data   │           │
│  │Candle   │           │  Database     │        │ (GitHub/Turso)│           │
│  │Store    │           │               │        │               │           │
│  └────┬────┘           └───────────────┘        └───────────────┘           │
│       │                                                                     │
│  ┌────▼──────────────────────────────────────────────────────────-┐         │
│  │                    Tick Processing Layer                       │         │
│  │   KiteTokenWatcher | CandleAggregator | TickProcessor          │         │
│  └────────────────────────────┬───────────────────────────────────┘         │
│                               │                                             │
│  ┌────────────────────────────▼───────────────────────────────────┐         │
│  │                     WebSocket Layer                            │         │
│  │          ZerodhaWebSocketClient | KiteTicker                   │         │
│  └────────────────────────────┬───────────────────────────────────┘         │
│                               │                                             │
│  ┌────────────────────────────▼───────────────────────────────────┐         │
│  │                  Kite Connect API / Authentication             │         │
│  │            Authenticator | KiteInstruments                     │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │                      Bot Layer (Telegram)                      │         │
│  │         PKTickBot | Orchestrator | Consumer                    │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
See more details on Architecture
Core Modules
1. In-Memory Candle Store
High-performance, in-memory OHLCV storage with O(1) access to all timeframes.

from pkbrokers.kite.inMemoryCandleStore import InMemoryCandleStore, get_candle_store

# Get singleton instance
store = get_candle_store()

# Process incoming tick
store.process_tick({
    'instrument_token': 256265,
    'last_price': 21500.50,
    'volume': 1000000,
    'timestamp': datetime.now()
})

# Get completed candles
candles = store.get_candles(
    instrument_token=256265,
    interval='5m',
    count=50
)

# Get current forming candle
current = store.get_current_candle(
    instrument_token=256265,
    interval='5m'
)

# Export to ticks.json
store.save_ticks_json("/path/to/ticks.json")

# Get statistics
stats = store.get_stats()
print(f"Instruments: {stats['instrument_count']}")
print(f"Ticks processed: {stats['ticks_processed']}")
Supported Timeframes
Interval	Description	Max Candles Stored
1m	1 minute	375 (full day)
2m	2 minutes	188
3m	3 minutes	125
4m	4 minutes	94
5m	5 minutes	75
10m	10 minutes	38
15m	15 minutes	25
30m	30 minutes	13
60m	60 minutes	7
day	Daily	1
Features
O(1) Access: Instant lookup via hash-based indexing
No Rate Limits: Unlike Yahoo Finance
Auto-Persistence: Saves to disk every 5 minutes
Memory Efficient: ~100MB for 2000 instruments
Thread-Safe: Lock-protected operations
2. Data Manager
Comprehensive data synchronization from multiple sources.

from pkbrokers.kite.datamanager import InstrumentDataManager

manager = InstrumentDataManager()

# Set specific stocks (optional)
manager.list_stock_codes = ["RELIANCE", "TCS", "INFY"]

# Execute synchronization
# Priority: SQLite → InMemoryCandleStore → Kite API → Pickle files
success = manager.execute()

# Access data
if success:
    for symbol, data in manager.pickle_data.items():
        df = pd.DataFrame(
            data=data['data'],
            columns=data['columns'],
            index=data['index']
        )
        print(f"{symbol}: {len(df)} rows")
Data Source Priority
During Market Hours:

Local SQLite database
InMemoryCandleStore (real-time ticks)
Kite API (authenticated)
GitHub ticks.json
After Market Hours:

Local pickle files
Remote GitHub pickle files
3. Kite Instruments
Manage instrument data from Kite Connect API.

from pkbrokers.kite.instruments import KiteInstruments, Instrument

# Initialize with credentials
kite = KiteInstruments(
    api_key="your_api_key",
    access_token="your_access_token"
)

# Sync instruments from Kite API
kite.sync_instruments(force_fetch=True)

# Get instrument count
count = kite.get_instrument_count()
print(f"Total instruments: {count}")

# Get NSE stocks only
equities = kite.get_equities(only_nse_stocks=True)

# Get instrument tokens for subscription
tokens = kite.get_instrument_tokens(equities)

# Fetch instrument by token
instrument = kite.get_instrument(256265)  # NIFTY 50
print(f"Symbol: {instrument.tradingsymbol}")
Instrument Model
@dataclass
class Instrument:
    instrument_token: int      # Unique identifier
    exchange_token: str        # Exchange-specific token
    tradingsymbol: str         # Trading symbol (e.g., 'RELIANCE')
    name: Optional[str]        # Full name
    last_price: Optional[float]
    expiry: Optional[str]      # For derivatives
    strike: Optional[float]    # For options
    tick_size: float
    lot_size: int
    instrument_type: str       # EQ, FUT, OPT, INDEX
    segment: str               # NSE, BSE
    exchange: str
    last_updated: str
    nse_stock: bool
4. Tick Watcher
WebSocket-based real-time tick processing.

from pkbrokers.kite.kiteTokenWatcher import KiteTokenWatcher

# Initialize watcher
watcher = KiteTokenWatcher()

# Start watching (blocking)
try:
    watcher.watch(test_mode=False)
except KeyboardInterrupt:
    watcher.stop()
Command-Line Usage
# Start tick watcher
pkkite --ticks

# Test mode (3 minutes)
pkkite --ticks --test

# Authenticate first
pkkite --auth

# Fetch historical data
pkkite --history=5minute
5. Local Candle Database
SQLite-based candle storage for persistence.

from pkbrokers.kite.localCandleDatabase import LocalCandleDatabase

# Initialize database
db = LocalCandleDatabase()

# Save daily candle
db.save_daily_candle(
    symbol="RELIANCE",
    date=date.today(),
    open_price=2500.0,
    high_price=2550.0,
    low_price=2480.0,
    close_price=2530.0,
    volume=1000000
)

# Load candles
candles = db.load_daily_candles("RELIANCE", days=30)

# Save intraday candles
db.save_intraday_candle(
    symbol="RELIANCE",
    timestamp=datetime.now(),
    interval="5m",
    open_price=2500.0,
    high_price=2510.0,
    low_price=2495.0,
    close_price=2505.0,
    volume=50000
)
6. Telegram Bots
PKTickBot
Telegram bot for distributing tick data.

from pkbrokers.bot.tickbot import PKTickBot

bot = PKTickBot(
    bot_token="your_bot_token",
    ticks_file_path="/path/to/ticks.json",
    chat_id="-1001234567890"
)

# Start bot (blocking)
bot.run()
Available Commands:

Command	Description
/ticks	Get zipped ticks.json file
/db	Get local SQLite database
/status	Check bot and data status
/top	Get top 20 ticking symbols
/token	Get current KTOKEN
/refresh_token	Generate new KTOKEN
/restart	Refresh token and restart watcher
/test_ticks	Start 3-minute tick test
/help	Show help message
Orchestrator
Multi-process orchestrator for bot and data management.

from pkbrokers.bot.orchestrator import Orchestrator

orchestrator = Orchestrator()

# Check if market is open
if orchestrator.should_run_kite_process():
    orchestrator.start_kite_process()
7. Authentication
Automated Kite Connect authentication using TOTP.

from pkbrokers.kite.authenticator import KiteAuthenticator

auth = KiteAuthenticator(
    user_id="your_user_id",
    password="your_password",
    totp_secret="your_totp_secret",
    api_key="your_api_key"
)

# Get access token
access_token = auth.authenticate()

# Token is automatically saved to environment
Environment Variables Required:

KUSER: Kite user ID
KPWD: Kite password
KTOTP: TOTP secret key
KAPI: Kite API key
8. GitHub Actions Workflows
PKBrokers includes automated GitHub Actions workflows for OHLCV data collection.

History Data Workflow
The w1-workflow-history-data-child.yml workflow fetches historical data from Kite API and saves to PKScreener.

Triggering with --history=day:

# Via pkkite CLI
pkkite --history=day --pastoffset=0 --verbose
What happens:

Fetches all NSE instrument tokens (~2000 stocks)
Calls Kite Historical API for each instrument (rate-limited: 3 req/sec)
Saves to local SQLite database (instrument_history.db)
Exports to pkl files (stock_data_DDMMYYYY.pkl)
Commits to PKScreener actions-data-download branch
Data Flow:

Kite API → SQLite DB → PKL Export → Git Commit → PKScreener Branch
PKL Files Saved to PKScreener:

actions-data-download/stock_data_DDMMYYYY.pkl - Daily candles
actions-data-download/daily_candles.pkl - Latest daily data
results/Data/ - Secondary storage location
Programmatic Trigger:

from pkbrokers.bot.dataSharingManager import DataSharingManager

manager = DataSharingManager()
manager.trigger_history_download_workflow(past_offset=5)  # Fetch last 5 days
See ARCHITECTURE.md for detailed workflow documentation.

9. PKL Generator Script
Unified script for generating pkl files from ticks.json OR SQLite database with historical data merge.

# From ticks.json (default - used by Ticks Runner)
python pkbrokers/scripts/generate_pkl_from_ticks.py --data-dir results/Data --verbose

# From SQLite database (used by History Data Child workflow)
python pkbrokers/scripts/generate_pkl_from_ticks.py --from-db --data-dir results/Data --verbose
# Programmatic usage
from pkbrokers.scripts.generate_pkl_from_ticks import (
    download_historical_pkl,
    download_ticks_json,
    load_from_sqlite,
    find_sqlite_database,
    convert_ticks_to_candles,
    merge_candles,
    save_pkl_files
)

# From ticks.json
historical = download_historical_pkl()  # ~37MB from GitHub
ticks = download_ticks_json()           # Today's ticks
candles = convert_ticks_to_candles(ticks)
merged = merge_candles(historical, candles)
save_pkl_files(merged, "results/Data")

# From SQLite database
db_path = find_sqlite_database()
db_candles = load_from_sqlite(db_path)
merged = merge_candles(historical, db_candles)
save_pkl_files(merged, "results/Data")
What it does:

Loads new data from ticks.json OR SQLite database
Downloads historical pkl (~37MB) from PKScreener actions-data-download
Converts data to candle format
Merges today's data with historical (~2000 stocks × 2+ years)
Saves both intraday and daily pkl files (~37MB+)
Output Files:

File	Description
stock_data_DDMMYYYY.pkl	Daily candles merged with historical
daily_candles.pkl	Same as above (generic name)
intraday_stock_data_DDMMYYYY.pkl	Today's intraday data only
intraday_1m_candles.pkl	Same as above (generic name)
API Reference
Main Exports
from pkbrokers.kite import (
    # Candle Store
    InMemoryCandleStore,
    get_candle_store,
    
    # Data Providers
    HighPerformanceDataProvider,
    InstrumentDataManager,
    
    # Instruments
    KiteInstruments,
    Instrument,
    
    # Tick Processing
    KiteTokenWatcher,
    CandleAggregator,
    
    # Database
    LocalCandleDatabase,
    
    # Authentication
    KiteAuthenticator,
)

from pkbrokers.bot import (
    PKTickBot,
    Orchestrator,
)
Module Structure
pkbrokers/
├── __init__.py
├── bot/
│   ├── __init__.py
│   ├── consumer.py          # Data consumer
│   ├── orchestrator.py      # Multi-process orchestrator
│   └── tickbot.py           # Telegram tick bot
├── kite/
│   ├── __init__.py
│   ├── authenticator.py     # Kite authentication
│   ├── candleAggregator.py  # Tick → Candle aggregation
│   ├── datamanager.py       # Multi-source data manager
│   ├── databasewriter.py    # Database writer
│   ├── inMemoryCandleStore.py  # In-memory candle store
│   ├── instrumentHistory.py # Historical data
│   ├── instruments.py       # Instrument management
│   ├── kiteTokenWatcher.py  # WebSocket tick watcher
│   ├── localCandleDatabase.py  # SQLite candle storage
│   ├── tickProcessor.py     # Tick processing
│   ├── ticks.py             # Tick utilities
│   ├── trader.py            # Trading operations
│   ├── zerodhaWebSocketClient.py  # WebSocket client
│   └── examples/
│       ├── externals.py     # External helpers
│       └── pkkite.py        # CLI entry point
└── scripts/
    └── publish_candle_data.py  # Data publishing
Environment Variables
Variable	Required	Description
KUSER	Yes*	Kite user ID
KPWD	Yes*	Kite password
KTOTP	Yes*	TOTP secret for 2FA
KAPI	Yes*	Kite API key
KTOKEN	Auto	Access token (auto-generated)
TOKEN	Yes**	Telegram bot token
CHAT_ID	Yes**	Default Telegram chat ID
TURSO_DB_URL	No	Turso database URL
TURSO_DB_AUTH_TOKEN	No	Turso auth token
*Required for Kite Connect features
**Required for Telegram bot features

Contributing
Development Setup
git clone https://github.com/pkjmesra/pkbrokers.git
cd pkbrokers
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
Running Tests
pytest test/
pytest --cov=pkbrokers test/
Code Style
ruff check pkbrokers/
ruff format pkbrokers/