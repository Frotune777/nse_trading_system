
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, Any, Optional, List
import re
from io import StringIO
import logging

logger = logging.getLogger(__name__)

class FundamentalFetcher:
    """Fetcher for fundamental financial data using Screener.in"""
    
    def __init__(self):
        self.base_url = "https://www.screener.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _parse_number(self, value: Any) -> Optional[float]:
        """Safely parse a string into a float."""
        if value is None or pd.isna(value):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        
        # Remove currency symbols, commas, spaces, and percentage signs
        cleaned = re.sub(r'[₹,%\s]', '', str(value))
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None

    def _get_company_page(self, symbol: str) -> Optional[BeautifulSoup]:
        """Fetch and parse company page."""
        try:
            url = f"{self.base_url}/company/{symbol}/"
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page for {symbol}: {e}")
            return None

    def _extract_table(self, soup: BeautifulSoup, table_id: str) -> Optional[pd.DataFrame]:
        try:
            section = soup.find('section', id=table_id)
            if not section: 
                return None
            table = section.find('table')
            if not table: 
                return None
            
            # Read table
            df = pd.read_html(StringIO(str(table)))[0]
            
            # Clean columns
            if 'Unnamed: 0' in df.columns:
                df = df.rename(columns={'Unnamed: 0': 'Metric'})
            elif len(df.columns) > 0:
                df = df.rename(columns={df.columns[0]: 'Metric'})
                
            # Set index
            df = df.set_index('Metric')
            
            # Clean values
            df = df.map(lambda x: str(x).replace('+', '').strip() if isinstance(x, str) else x)
            return df
        except Exception as e:
            print(f"Error extracting table '{table_id}': {e}")
            return None

    def fetch_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch complete fundamental data for a symbol.
        Returns a dictionary matching the Fundamental Data Model.
        """
        soup = self._get_company_page(symbol)
        if not soup:
            return {}

        data = {
            "metadata": self._extract_metadata(soup, symbol),
            "key_metrics": self._extract_key_metrics(soup),
            "quarterly_results": self._extract_quarterly_results(soup),
            "shareholding": self._extract_shareholding(soup),
            "annual_financials": self._extract_annual_financials(soup)
        }
        return data

    def _extract_metadata(self, soup: BeautifulSoup, symbol: str) -> Dict[str, str]:
        info = {
            'symbol': symbol,
            'company_name': symbol,
            'sector': 'Unknown',
            'industry': 'Unknown'
        }
        try:
            h1 = soup.find('h1')
            if h1:
                info['company_name'] = h1.text.strip()
            
            # Try to find sector/industry links
            links = soup.find_all('a', href=re.compile(r'/sector/'))
            if links:
                info['sector'] = links[0].text.strip()
        except Exception:
            pass
        return info

    def _extract_key_metrics(self, soup: BeautifulSoup) -> Dict[str, float]:
        metrics = {}
        try:
            # Screener has a top ratios list ul#top-ratios
            ratios_list = soup.select('#top-ratios li')
            for li in ratios_list:
                name_span = li.find('span', class_='name')
                val_span = li.find('span', class_='number')
                if name_span and val_span:
                    name = name_span.text.strip()
                    val = self._parse_number(val_span.text.strip())
                    
                    # Map to standard keys
                    key_map = {
                        'Market Cap': 'market_cap',
                        'Current Price': 'current_price',
                        'Stock P/E': 'pe_ratio',
                        'Book Value': 'book_value',
                        'Dividend Yield': 'dividend_yield',
                        'ROCE': 'roce',
                        'ROE': 'roe',
                        'Face Value': 'face_value'
                    }
                    if name in key_map:
                        metrics[key_map[name]] = val
        except Exception:
            pass
        return metrics

    def _extract_quarterly_results(self, soup: BeautifulSoup) -> Dict[str, List]:
        df = self._extract_table(soup, 'quarters')
        if df is None or df.empty:
            return {}
        
        # Transpose so columns are metrics and rows are periods, or just extract lists
        # The table usually has periods as columns and metrics as rows.
        # We want arrays of values for specific metrics.
        
        result = {"quarters": list(df.columns)}
        
        # Specific metrics to extract
        metrics_map = {
            'Sales': 'revenue', # Sometimes called Revenue or Sales
            'Revenue': 'revenue', 
            'Operating Profit': 'operating_profit',
            'Net Profit': 'net_profit',
            'EPS in Rs': 'eps',
            'EPS': 'eps',
            'OPM %': 'margin_opm'
        }
        
        for row_name, key in metrics_map.items():
            # Find row that contains the name (flexible match)
            matched_rows = [idx for idx in df.index if row_name.lower() in str(idx).lower()]
            if matched_rows:
                row_data = df.loc[matched_rows[0]]
                # Parse all values in the row
                result[key] = [self._parse_number(v) for v in row_data.values]
                
        return result

    def _extract_shareholding(self, soup: BeautifulSoup) -> Dict[str, List]:
        df = self._extract_table(soup, 'shareholding')
        if df is None or df.empty:
            return {}
            
        result = {"periods": list(df.columns)}
        
        metrics_map = {
            'Promoters': 'promoters',
            'FIIs': 'fiis',
            'DIIs': 'diis',
            'Public': 'public'
        }
        
        for row_name, key in metrics_map.items():
             matched_rows = [idx for idx in df.index if row_name.lower() in str(idx).lower()]
             if matched_rows:
                row_data = df.loc[matched_rows[0]]
                result[key] = [self._parse_number(v) for v in row_data.values]
                
        return result

    def _extract_annual_financials(self, soup: BeautifulSoup) -> Dict[str, List]:
        df = self._extract_table(soup, 'profit-loss')
        if df is None or df.empty:
            return {}
            
        result = {"years": list(df.columns)}
        
        metrics_map = {
            'Sales': 'revenue',
            'Revenue': 'revenue',
            'Net Profit': 'net_profit'
        }
        
        for row_name, key in metrics_map.items():
            matched_rows = [idx for idx in df.index if row_name.lower() in str(idx).lower()]
            if matched_rows:
                row_data = df.loc[matched_rows[0]]
                result[key] = [self._parse_number(v) for v in row_data.values]
                
        return result
        return result

    def calculate_historical_pe(self, price_df: pd.DataFrame, quarterly_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Calculates Historical PE Ratio series.
        :param price_df: DataFrame with 'Close' and Datetime Index (from NSEMasterData)
        :param quarterly_data: Dictionary from _extract_quarterly_results
        :return: DataFrame with ['Close', 'TTM_EPS', 'PE']
        """
        if price_df is None or price_df.empty or not quarterly_data or 'eps' not in quarterly_data:
            return pd.DataFrame()
            
        try:
            # 1. Prepare EPS DataFrame
            quarters = quarterly_data.get('quarters', [])
            eps_vals = quarterly_data.get('eps', [])
            
            if len(quarters) != len(eps_vals):
                return pd.DataFrame()
                
            eps_df = pd.DataFrame({'quarter': quarters, 'eps': eps_vals})
            
            # Parse dates (e.g., "Sep 2024" -> 2024-09-30)
            def parse_q_date(q_str):
                try:
                    # Simplify: Assume end of month. 
                    # Sep 2024 -> Sep 1 2024 -> Month End
                    dt = pd.to_datetime(q_str, format='%b %Y')
                    return dt + pd.offsets.MonthEnd(0)
                except:
                    return None
                    
            eps_df['date'] = eps_df['quarter'].apply(parse_q_date)
            eps_df = eps_df.dropna(subset=['date']).sort_values('date').set_index('date')
            
            # 2. Calculate TTM EPS (Rolling Sum of 4)
            # We need strictly 4 quarters. 
            eps_df['ttm_eps'] = eps_df['eps'].rolling(window=4, min_periods=4).sum()
            
            # 3. Merge with Price Data
            # Result dates (approximate) - we assume TTM EPS is valid from the quarter end date
            # Reindex EPS to daily price index using forward fill
            
            combined = price_df[['Close']].copy()
            combined = combined.sort_index()
            
            # Merge asof or just reindex
            # We want to fill TTM EPS forward from valid dates
            # combined['ttm_eps'] = pd.NA # REMOVED to avoid suffix collision
            
            # Iterate and fill (vectorized approach via merge_asof is better but requires sorted)
            # combined must be sorted. eps_df must be sorted.
            combined = pd.merge_asof(combined, eps_df[['ttm_eps']], left_index=True, right_index=True, direction='backward')
            
            # Fill missing initial values if needed or drop
            # combined['ttm_eps'] = combined['ttm_eps'].ffill() # merged backward does lookback
            
            # Calculate PE
            combined['PE'] = combined['Close'] / combined['ttm_eps']
            
            return combined.dropna()
            
        except Exception as e:
            logger.error(f"Error calculating PE: {e}")
            return pd.DataFrame()
