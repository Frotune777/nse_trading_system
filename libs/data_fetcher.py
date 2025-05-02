import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import pandas as pd
from datetime import datetime
import time


class NSEDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self._configure_session()
        self.cookie_refresh_interval = 30  # Minutes
        self.last_cookie_refresh = None
        self.max_retries = 5
        self.timeout = 15

    def _configure_session(self):
        """Configure session with proper headers"""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        })
        self._refresh_cookies(force=True)

    def _should_refresh_cookies(self):
        """Check if cookies need refresh"""
        if not self.last_cookie_refresh:
            return True
        return (datetime.now() - self.last_cookie_refresh).total_seconds() > (self.cookie_refresh_interval * 60)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _refresh_cookies(self, force=False):
        """Refresh session cookies with retry"""
        if force or self._should_refresh_cookies():
            try:
                # First get the homepage to set cookies
                self.session.get("https://www.nseindia.com", timeout=self.timeout)
                # Then get market data page to set additional cookies
                self.session.get("https://www.nseindia.com/market-data", timeout=self.timeout)
                self.last_cookie_refresh = datetime.now()
                print("Cookies refreshed successfully")
            except requests.exceptions.RequestException as e:
                print(f"Cookie refresh failed: {str(e)}")
                raise

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=30))
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
            # Refresh cookies if needed
            self._refresh_cookies()

            url = "https://www.nseindia.com/api/historical/cm/equity"
            params = {
                'symbol': symbol,
                'series': 'EQ',
                'from': start.strftime('%d-%m-%Y'),
                'to': end.strftime('%d-%m-%Y')
            }

            # Add delay to avoid rate limiting
            time.sleep(1)

            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            if not data or 'data' not in data:
                print(f"No data returned for {symbol}")
                return pd.DataFrame()

            df = pd.DataFrame(data['data'])

            # Standardize column names
            column_map = {
                'CH_TIMESTAMP': 'datetime',
                'CH_OPENING_PRICE': 'open',
                'CH_TRADE_HIGH_PRICE': 'high',
                'CH_TRADE_LOW_PRICE': 'low',
                'CH_CLOSING_PRICE': 'close',
                'CH_TOT_TRADED_QTY': 'volume'
            }
            df = df.rename(columns=column_map)[list(column_map.values())]

            # Convert date format
            df['datetime'] = pd.to_datetime(df['datetime'], format='%d-%b-%Y')
            df = df.sort_values('datetime').set_index('datetime')

            return df

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error for {symbol}: {http_err}")
            if http_err.response.status_code == 401:
                self._refresh_cookies(force=True)
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Request failed for {symbol}: {req_err}")
            raise
        except Exception as e:
            print(f"Unexpected error for {symbol}: {str(e)}")
            raise