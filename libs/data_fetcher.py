import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import pandas as pd
from datetime import datetime
import time


class NSEDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self._configure_session()

    def _configure_session(self):
        """Configure session headers and cookies"""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        })
        # Initial cookie setup
        self._refresh_cookies()

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=10))
    def _refresh_cookies(self):
        """Refresh session cookies with retry"""
        try:
            self.session.get("https://www.nseindia.com", timeout=5)
        except requests.exceptions.RequestException as e:
            print(f"Cookie refresh failed: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_data(self, symbol, start, end):
        """
        Fetch OHLC data for given symbol and date range
        Args:
            symbol (str): Stock symbol (e.g., 'TCS', 'INFY')
            start (datetime): Start date
            end (datetime): End date
        Returns:
            pd.DataFrame: DataFrame with OHLC data
        """
        try:
            # Refresh cookies before each request
            self._refresh_cookies()

            url = "https://www.nseindia.com/api/historical/cm/equity"
            params = {
                'symbol': symbol,
                'series': 'EQ',
                'from': start.strftime('%d-%m-%Y'),
                'to': end.strftime('%d-%m-%Y')
            }

            response = self.session.get(
                url,
                params=params,
                timeout=10
            )
            response.raise_for_status()

            data = response.json()

            if not data or 'data' not in data:
                print(f"No data returned for {symbol}")
                return pd.DataFrame()

            df = pd.DataFrame(data['data'])

            # Standardize column names
            column_map = {
                'CH_TIMESTAMP': 'date',
                'CH_OPENING_PRICE': 'open',
                'CH_TRADE_HIGH_PRICE': 'high',
                'CH_TRADE_LOW_PRICE': 'low',
                'CH_CLOSING_PRICE': 'close',
                'CH_TOT_TRADED_QTY': 'volume'
            }
            df = df.rename(columns=column_map)[list(column_map.values())]

            # Convert date format
            df['date'] = pd.to_datetime(df['date'], format='%d-%b-%Y')
            df = df.sort_values('date')

            return df

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error for {symbol}: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error for {symbol}: {conn_err}")
        except Exception as e:
            print(f"Error fetching {symbol}: {str(e)}")

        return pd.DataFrame()

    # Alias for backward compatibility
    def fetch_ohlc(self, symbol, start, end):
        return self.fetch_data(symbol, start, end)