import pandas as pd
import time
import json
import requests
from datetime import datetime, timedelta
import re
from tenacity import retry, stop_after_attempt, wait_exponential


class NSEMasterData:
    def __init__(self):
        self.session = requests.Session()
        self._configure_session()
        self.nse_url = "https://charting.nseindia.com/Charts/GetEQMasters"
        self.nfo_url = "https://charting.nseindia.com/Charts/GetFOMasters"
        self.historical_url = "https://charting.nseindia.com/Charts/symbolhistoricaldata/"
        self.nse_data = None
        self.nfo_data = None

    def _configure_session(self):
        """Configure session with proper headers and cookies"""
        self.session.headers.update({
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            'Content-Type': 'application/json',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate'
        })

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _ensure_cookies(self):
        """Ensure we have valid cookies"""
        self.session.get("https://www.nseindia.com", timeout=5)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_nse_symbol_master(self, url):
        """Fetch symbol master data with retry logic"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.text.splitlines()
            columns = ['ScripCode', 'Symbol', 'Name', 'Type']
            return pd.DataFrame([line.split('|') for line in data], columns=columns)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download data from {url}: {e}")
            raise

    def download_symbol_master(self):
        """Download both NSE and NFO master data"""
        try:
            self._ensure_cookies()
            self.nse_data = self.get_nse_symbol_master(self.nse_url)
            self.nfo_data = self.get_nse_symbol_master(self.nfo_url)
        except Exception as e:
            print(f"Failed to download symbol masters: {e}")

    def search(self, symbol, exchange, match=False):
        """Search for symbols with enhanced error handling"""
        exchange = exchange.upper()
        if exchange not in ('NSE', 'NFO'):
            raise ValueError("Exchange must be either 'NSE' or 'NFO'")

        df = self.nse_data if exchange == 'NSE' else self.nfo_data
        if df is None:
            raise ValueError(f"Data for {exchange} not downloaded. Run download_symbol_master() first.")

        if match:
            result = df[df['Symbol'].str.upper() == symbol.upper()]
        else:
            result = df[df['Symbol'].str.contains(symbol, case=False, na=False)]

        if result.empty:
            print(f"No matches found for '{symbol}' in {exchange}")
            return pd.DataFrame()

        return result.reset_index(drop=True)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_history(self, symbol="Nifty 50", exchange="NSE", start=None, end=None, interval='1d'):
        """Get historical data with improved reliability"""
        try:
            self._ensure_cookies()
            symbol_info = self.search(symbol, exchange).iloc[0]

            interval_xref = {
                '1m': ('1', 'I'), '3m': ('3', 'I'), '5m': ('5', 'I'), '10m': ('5', 'I'),
                '15m': ('15', 'I'), '30m': ('15', 'I'), '1h': ('15', 'I'),
                '1d': ('1', 'D'), '1w': ('1', 'W'), '1M': ('1', 'M')
            }
            time_interval, chart_period = interval_xref.get(interval, ('1', 'D'))

            payload = {
                "exch": "N" if exchange.upper() == "NSE" else "D",
                "instrType": "C" if exchange.upper() == "NSE" else "D",
                "ScripCode": int(symbol_info['ScripCode']),
                "ulScripCode": int(symbol_info['ScripCode']),
                "fromDate": int(start.timestamp()) if start else 0,
                "toDate": int(end.timestamp()) if end else int(time.time()),
                "timeInterval": time_interval,
                "chartPeriod": chart_period,
                "chartStart": 0
            }

            response = self.session.post(self.historical_url, data=json.dumps(payload), timeout=15)
            response.raise_for_status()
            data = response.json()

            if not data:
                print("No data received from NSE")
                return pd.DataFrame()

            df = pd.DataFrame(data)
            df.columns = ['Status', 'TS', 'Open', 'High', 'Low', 'Close', 'Volume']
            df['TS'] = pd.to_datetime(df['TS'], unit='s', utc=True).dt.tz_localize(None)
            df = df[['TS', 'Open', 'High', 'Low', 'Close', 'Volume']]

            # Process based on interval type
            if interval in ['1m', '3m', '5m', '15m', '10m', '30m', '1h']:
                cutoff_time = pd.Timestamp('15:30:00').time()
                df = df[df['TS'].dt.time <= cutoff_time]
                df['Timestamp'] = self._adjust_timestamp(df['TS'], interval)
                df = df.drop(columns=['TS']).set_index('Timestamp')

                if interval in ['10m', '30m', '1h']:
                    df = self._resample_intraday(df, interval)

            else:
                df = df.rename(columns={'TS': 'Timestamp'}).set_index('Timestamp')

            return df

        except Exception as e:
            print(f"Error fetching {symbol} data: {e}")
            return pd.DataFrame()

    def _adjust_timestamp(self, ts_series, interval):
        """Adjust timestamps for intraday data"""
        if interval in ['30m', '1h']:
            num = 15
        elif interval in ['10m']:
            num = 5
        else:
            num = int(re.match(r'\d+', interval).group())

        if num == 0:
            return (ts_series - timedelta(minutes=num)).dt.round('min')
        return (ts_series - timedelta(minutes=num)).dt.round(f'{num}min')

    def _resample_intraday(self, df, interval):
        """Resample intraday data to desired interval"""
        agg_map = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }

        if interval == '10m':
            freq = '10min'
        elif interval == '30m':
            freq = '30min'
        else:  # 1h
            freq = '60min'

        first_ts = df.index.min()
        offset = pd.to_timedelta(first_ts.time().strftime('%H:%M:%S'))
        return df.resample(freq, origin='start_day', offset=offset).agg(agg_map).dropna()