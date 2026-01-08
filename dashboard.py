
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from pathlib import Path
import yaml
import sys
from datetime import datetime, timedelta

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
import numpy as np

# Import Quad Analyzer
from libs.quad_analyzer import QuadAnalyzer
from libs.screener import StockScreener

def page_quad_report():
    st.header("🏆 Quad Analysis Report Card")
    st.caption("Holistic evaluation based on 4 Pillars: Fundamental, Technical, Institutional, Macro")
    
    # Custom CSS for smaller font
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            font-size: 14px;
        }
        .stMetric {
            font-size: 0.8rem !important;
        }
        h1, h2, h3 {
            font-size: 1.5rem !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        config = load_config()
        symbols = config.get("tracked_symbols", ["SBIN", "TCS", "RELIANCE"])
        symbol = st.selectbox("Select Symbol for Report", symbols)
        
        if st.button("Generate Report", type="primary"):
            with st.spinner(f"Analyzing {symbol} across 4 dimensions..."):
                analyzer = QuadAnalyzer()
                report = analyzer.get_report_card(symbol)
                st.session_state['report'] = report

    if 'report' in st.session_state and st.session_state['report']['symbol'] == symbol:
        report = st.session_state['report']
        pillars = report['pillars']
        score = report['quad_score']
        
        # Top Section: Score & Radar
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.metric("Quad Score (0-10)", f"{score}/10", 
                      delta="Strong Buy" if score > 7 else "Weak" if score < 4 else "Neutral",
                      delta_color="normal")
            
            # Gauge (Simple Progress Bar for now as gauge needs more code)
            st.progress(score / 10)
            st.write(f"**Verdict**: {'💎 Diamond Pick' if score > 8 else '⚠️ Caution' if score < 4 else '⚖️ Balanced'}")

        with c2:
            # Radar Chart
            df_radar = pd.DataFrame(dict(
                r=[pillars['Fundamental'], pillars['Technical'], pillars['Institutional'], pillars['Macro']],
                theta=['Fundamental', 'Technical', 'Institutional', 'Macro']
            ))
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=df_radar['r'],
                theta=df_radar['theta'],
                fill='toself',
                name=symbol
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False, height=300, margin=dict(l=40, r=40, t=20, b=20))
            st.plotly_chart(fig, width='stretch')

        # Tabs for details
        tab1, tab2, tab3, tab4 = st.tabs(["Fundamentals (Quality)", "Technicals (Trend)", "Institutional (Smart Money)", "Macro (Sector)"])
        
        with tab1:
            st.subheader("Fundamental Analysis")
            st.info(f"Score: {pillars['Fundamental']}/10")
            for reason in report['details']['fundamental']:
                st.write(f"- {reason}")
            
            # Valuation Chart (Price vs EPS)
            st.subheader("Valuation Trend (PE vs EPS)")
            
            # Need to fetch history here or pass it? QuadAnalyzer doesn't fetch history by default to save time.
            # We fetch it on demand for this tab.
            from libs.nse_data_fetcher import NSEMasterData
            from datetime import datetime, timedelta
            
            with st.spinner("Loading Valuation Data..."):
                fetcher = NSEMasterData()
                # Ensure master downloaded (usually quick if cached or run once)
                # fetcher.download_symbol_master() # Might fail if not initialized, assume app has done it?
                # Best to use a cached singleton or just run it. 
                # For safety:
                try:
                    fetcher.download_symbol_master()
                    end = datetime.now()
                    start = end - timedelta(days=365*5) # 5 years
                    price_df = fetcher.get_history(symbol, start=start, end=end)
                    
                    if not price_df.empty:
                        fund_fetcher = analyzer.fundamental
                        # We have raw fundamental data in report
                        raw_data = report['details']['raw_fundamental']
                        
                        pe_df = fund_fetcher.calculate_historical_pe(price_df, raw_data.get('quarterly_results', {}))
                        
                        if not pe_df.empty:
                            # Create Double Axis Chart
                            fig_val = make_subplots(specs=[[{"secondary_y": True}]])
                            
                            # EPS Bars (Use Quarter dates from raw data for bars, or daily line? Screener uses bars)
                            # Let's use the quarterly dates for EPS Bars to look like Screener
                            q_res = raw_data.get('quarterly_results', {})
                            if q_res:
                                q_df = pd.DataFrame(q_res)
                                # Clean dates
                                q_df['quarters'] = pd.to_datetime(q_df['quarters'], format='%b %Y', errors='coerce') + pd.offsets.MonthEnd(0)
                                q_df = q_df.dropna(subset=['quarters']).sort_values('quarters')
                                
                                # TTM EPS for bars? Screener shows Annualized EPS bars usually, or TTM EPS line.
                                # Let's show TTM EPS as Area/Bar
                                
                                fig_val.add_trace(
                                    go.Bar(x=pe_df.index, y=pe_df['ttm_eps'], name="TTM EPS", marker_color='lightblue', opacity=0.5),
                                    secondary_y=False
                                )
                                
                                # Median PE Line (Constant)
                                median_pe = pe_df['PE'].median()
                                
                                # PE Ratio Line
                                fig_val.add_trace(
                                    go.Scatter(x=pe_df.index, y=pe_df['PE'], name="PE Ratio", line=dict(color='purple', width=2)),
                                    secondary_y=True
                                )
                                
                                # Median PE Annotation
                                fig_val.add_hline(y=median_pe, line_dash="dash", line_color="gray", annotation_text=f"Median PE: {median_pe:.1f}", secondary_y=True)

                                fig_val.update_layout(title="Price to Earnings Trend (5Y)", height=400, showlegend=True)
                                fig_val.update_yaxes(title_text="EPS (₹)", secondary_y=False)
                                fig_val.update_yaxes(title_text="PE Ratio", secondary_y=True)
                                
                                st.plotly_chart(fig_val, width='stretch')
                        else:
                            st.warning("Insufficient data for PE Chart")
                except Exception as e:
                    st.error(f"Valuation Chart Error: {e}")

            # Show financial data if available
            raw = report['details']['raw_fundamental']
            if 'key_metrics' in raw:
                st.dataframe(raw['key_metrics'], use_container_width=True)
                st.caption("Source: Screener.in (EOD) + NSE Native History")

        with tab2:
            st.subheader("Technical Analysis")
            st.info(f"Score: {pillars['Technical']}/10")
            for reason in report['details']['technical']:
                st.write(f"- {reason}")
            st.caption("Source: NSE Historical Data (Daily)")

        with tab3:
            st.subheader("Institutional Analysis")
            st.info(f"Score: {pillars['Institutional']}/10")
            for reason in report['details']['institutional']:
                st.write(f"- {reason}")
            
            # Big Money Details
            big_money = report['details'].get('big_money', {})
            if big_money and big_money.get('deals_count', 0) > 0:
                st.write("---")
                st.write("### 🐋 Big Money Deals (Last 30 Days)")
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Net Qty", f"{big_money['net_qty']:,}")
                col_m2.metric("Players", big_money['unique_players'])
                col_m3.metric("Sentiment", big_money['net_sentiment'])
                
                st.caption("Source: NSE Bulk & Block deals archived in local DB")
            
            st.write("---")
            st.write("### 📊 Derivative Sentiment")
            inst_det = report['details']['institutional']
            if inst_det and "No Live" not in str(inst_det):
                 st.write("Options sentiment analysis active.")
            else:
                 st.warning("Live Derivatives Data Unavailable (Market Closed or Restricted)")
            st.caption("Source: NSE Option Chain (Live/Cached)")

        with tab4:
            st.subheader("Macro Analysis")
            st.info(f"Score: {pillars['Macro']}/10")
            for reason in report['details']['macro']:
                st.write(f"- {reason}")
            st.caption("Source: NSE Native Sector Indices")



# PATHS
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MARKET_STATS_DIR = DATA_DIR / "market_stats"

# UTILS
@st.cache_data
def load_config():
    with open(PROJECT_ROOT / "config" / "symbols.yaml") as f:
        return yaml.safe_load(f)

@st.cache_data
def load_market_data(filename):
    """Loads market statistics from SQLite."""
    table_map = {
        "fii_dii": "market_fii_dii",
        "insider_trading": "market_insider_trading",
        "upcoming_results": "market_upcoming_results"
    }
    table_name = table_map.get(filename)
    if not table_name:
        return []

    try:
        import sqlite3
        conn = sqlite3.connect(PROJECT_ROOT / "data" / "trading.db")
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return df.to_dict(orient='records')
    except Exception as e:
        st.error(f"Error loading {filename} from DB: {e}")
        return []

@st.cache_data
def load_stock_data(symbol):
    path = DATA_DIR / f"{symbol.lower()}_1d.parquet"
    if path.exists():
        return pd.read_parquet(path)
    return None

# UI COMPONENTS
def render_sidebar():
    st.sidebar.title("Navigation")
    
    # Broker status indicator
    try:
        from libs.broker_manager import BrokerManager
        broker_mgr = BrokerManager()
        has_creds, broker_name, error = broker_mgr.check_active_broker_credentials()
        
        if has_creds and not error:
            st.sidebar.success(f"🟢 {broker_name.upper()} Active")
        elif broker_name:
            st.sidebar.warning(f"🟡 {broker_name.upper()} (Check Config)")
        else:
            st.sidebar.error("🔴 No Broker Configured")
    except Exception as e:
        st.sidebar.info("⚪ Broker Status Unknown")
    
    page = st.sidebar.radio("Go to:", [
        "Stock Analysis", 
        "Market Overview", 
        "Big Money Tracker", 
        "Insider Activity", 
        "Strategy Screener", 
        "Quad Report Card", 
        "ML Predictions", 
        "Strategy Backtesting",
        "PKScreener",
        "MLOps Monitor",
        "Broker Configuration",
        "Data Management", 
        "Database Info"
    ])
    return page

def page_stock_analysis():
    st.header("📈 Stock Analysis")
    
    config = load_config()
    symbols = config.get("tracked_symbols", [])
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        symbol = st.selectbox("Select Symbol", symbols)
        df = load_stock_data(symbol)
        
        if df is None:
            st.error(f"No data found for {symbol}")
            return

        # Show basics
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        change = last_row['Close'] - prev_row['Close']
        pct_change = (change / prev_row['Close']) * 100
        
        st.metric("Latest Price", f"₹{last_row['Close']:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
        
        st.subheader("Indicators")
        show_sma = st.checkbox("Show SMA (50/200)", value=True)
        show_bb = st.checkbox("Show Bollinger Bands")
        show_rsi = st.checkbox("Show RSI")
        show_macd = st.checkbox("Show MACD")

    with col2:
        # Main Chart
        fig = make_subplots(rows=2 if (show_rsi or show_macd) else 1, cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.05,
                            row_heights=[0.7, 0.3] if (show_rsi or show_macd) else [1.0])

        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index,
                        open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'],
                        name=symbol), row=1, col=1)

        # SMA
        if show_sma:
            if 'SMA_50' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='orange', width=1), name='SMA 50'), row=1, col=1)
            if 'SMA_200' in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], line=dict(color='blue', width=1), name='SMA 200'), row=1, col=1)

        # Bollinger Bands
        if show_bb and 'BB_UPPER' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_UPPER'], line=dict(color='gray', width=1, dash='dash'), name='BB Upper'), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['BB_LOWER'], line=dict(color='gray', width=1, dash='dash'), fill='tonexty', name='BB Lower'), row=1, col=1)

        # RSI / MACD (Secondary)
        if show_rsi and 'RSI_14' in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI_14'], line=dict(color='purple', width=2), name='RSI 14'), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            fig.update_yaxes(title_text="RSI", row=2, col=1)
        
        elif show_macd and 'MACD' in df.columns:
             fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='blue', width=1), name='MACD'), row=2, col=1)
             fig.add_trace(go.Scatter(x=df.index, y=df['MACD_SIGNAL'], line=dict(color='orange', width=1), name='Signal'), row=2, col=1)
             fig.add_bar(x=df.index, y=df['MACD_HIST'], name='Hist', row=2, col=1)

        fig.update_layout(xaxis_rangeslider_visible=False, height=600, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, width='stretch')

    # Data Details Section
    tab_det1, tab_det2, tab_det3 = st.tabs(["Big Money Sentiment", "Corporate Milestones", "Raw Data"])
    
    with tab_det1:
        st.subheader("🐋 Big Money Activity")
        from libs.deal_analyzer import DealAnalyzer
        deal_analyzer = DealAnalyzer(PROJECT_ROOT / "data" / "trading.db")
        sentiment = deal_analyzer.get_symbol_sentiment(symbol)
        
        if sentiment['deals_count'] > 0:
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Net Qty", f"{sentiment['net_qty']:,}")
            col_s2.metric("Unique Players", sentiment['unique_players'])
            col_s3.metric("Sentiment", sentiment['net_sentiment'])
        else:
            st.info("No Bulk/Block deals detected in the last 30 days.")

    with tab_det2:
        st.subheader("📅 Corporate Milestones")
        try:
            import sqlite3
            conn = sqlite3.connect(PROJECT_ROOT / "data" / "trading.db")
            
            # Helper to check table
            def table_exists(name):
                return conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None

            if table_exists("market_corp_actions"):
                corp_df = pd.read_sql_query(f"SELECT exDate, purpose FROM market_corp_actions WHERE symbol = '{symbol}'", conn)
                if not corp_df.empty:
                    st.dataframe(corp_df.sort_values('exDate', ascending=False), use_container_width=True)
                else:
                    st.info("No recent corporate actions found for this symbol.")
            else:
                st.info("Corporate actions data not yet initialized in database.")
            
            conn.close()
        except Exception as e:
            st.error(f"Error loading corporate actions: {e}")

    with tab_det3:
        st.dataframe(df.tail(10), use_container_width=True)

def page_big_money():
    st.header("🐋 Big Money Tracker (Bulk & Block Deals)")
    st.write("Tracking institutional entries and 'clumping' signals (multiple big players buying together).")

    from libs.deal_analyzer import DealAnalyzer
    analyzer = DealAnalyzer(PROJECT_ROOT / "data" / "trading.db")

    tab1, tab2, tab3 = st.tabs(["Clumping Signals", "Recent Deals", "Short Selling"])

    with tab1:
        st.subheader("🔥 Institutional Clumping (Last 5 Days)")
        signals = analyzer.get_clumping_signals(days=5)
        if not signals.empty:
            st.dataframe(signals, use_container_width=True)
            st.caption("Symbols with multiple unique institutional buyers recently.")
        else:
            st.info("No clumping signals detected in the last 5 days.")

    with tab2:
        st.subheader("📋 Search All Deals")
        search = st.text_input("Filter by Symbol or Client Name")
        
        # Load all recent deals
        try:
            import sqlite3
            conn = sqlite3.connect(PROJECT_ROOT / "data" / "trading.db")
            
            # Helper to check table
            def table_exists(name):
                return conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None

            bulk = pd.read_sql_query("SELECT *, 'Bulk' as deal_type FROM market_bulk_deals", conn) if table_exists("market_bulk_deals") else pd.DataFrame()
            block = pd.read_sql_query("SELECT *, 'Block' as deal_type FROM market_block_deals", conn) if table_exists("market_block_deals") else pd.DataFrame()
            
            # Normalize column names (NSE uses BD_ and BLK_ prefixes)
            if not bulk.empty:
                bulk = bulk.rename(columns={
                    'BD_DT_DATE': 'date',
                    'BD_SYMBOL': 'symbol',
                    'BD_CLIENT_NAME': 'clientName',
                    'BD_BUY_SELL': 'type',
                    'BD_QTY_TRD': 'quantity',
                    'BD_TP_WATP': 'price'
                })
            if not block.empty:
                block = block.rename(columns={
                    'BLK_DT_DATE': 'date',
                    'BLK_SYMBOL': 'symbol',
                    'BLK_CLIENT_NAME': 'clientName',
                    'BLK_BUY_SELL': 'type',
                    'BLK_QTY_TRD': 'quantity',
                    'BLK_TP_WATP': 'price'
                })
            
            if not bulk.empty or not block.empty:
                df = pd.concat([bulk, block], ignore_index=True).sort_values('date', ascending=False)
                if search:
                    df = df[df['symbol'].str.contains(search, case=False, na=False) | df['clientName'].str.contains(search, case=False, na=False)]
                
                # Display relevant columns
                display_cols = ['date', 'symbol', 'clientName', 'type', 'quantity', 'price', 'deal_type']
                display_cols = [c for c in display_cols if c in df.columns]
                st.dataframe(df[display_cols], use_container_width=True)
            else:
                st.info("No Bulk or Block deals found in database.")
            
            conn.close()
        except Exception as e:
            st.error(f"Error loading deals: {e}")

    with tab3:
        st.subheader("📉 Short Selling Activity")
        search_short = st.text_input("Filter by Symbol or Client Name", key="short_search")
        
        try:
            import sqlite3
            conn = sqlite3.connect(PROJECT_ROOT / "data" / "trading.db")
            
            def table_exists(name):
                return conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone() is not None
            
            if table_exists("market_short_selling"):
                short_df = pd.read_sql_query("SELECT * FROM market_short_selling", conn)
                
                # Normalize column names
                if not short_df.empty:
                    short_df = short_df.rename(columns={
                        'SS_DATE': 'date',
                        'SS_SYMBOL': 'symbol',
                        'SS_NAME': 'clientName',
                        'SS_QTY': 'quantity'
                    })
                    
                    # Sort by date
                    short_df = short_df.sort_values('date', ascending=False)
                    
                    if search_short:
                        short_df = short_df[short_df['symbol'].str.contains(search_short, case=False, na=False) | 
                                           short_df['clientName'].str.contains(search_short, case=False, na=False)]
                    
                    # Display relevant columns
                    display_cols = ['date', 'symbol', 'clientName', 'quantity']
                    display_cols = [c for c in display_cols if c in short_df.columns]
                    st.dataframe(short_df[display_cols], use_container_width=True)
                    
                    # Show top shorted symbols
                    st.subheader("🔻 Most Shorted Symbols")
                    top_shorted = short_df.groupby('symbol')['quantity'].sum().sort_values(ascending=False).head(10)
                    st.bar_chart(top_shorted)
                else:
                    st.info("No Short Selling data found in database.")
            else:
                st.info("Short Selling data table not yet created. Run market_update.py to populate.")
            
            conn.close()
        except Exception as e:
            st.error(f"Error loading short selling data: {e}")

def page_market_overview():
    st.header("🌍 Market Overview")
    
    # FII/DII
    st.subheader("FII / DII Activity")
    fii_data = load_market_data("fii_dii")
    if fii_data:
        df_fii = pd.DataFrame(fii_data)
        # Convert numeric
        df_fii['netValue'] = pd.to_numeric(df_fii['netValue'], errors='coerce')
        df_fii['buyValue'] = pd.to_numeric(df_fii['buyValue'], errors='coerce')
        df_fii['sellValue'] = pd.to_numeric(df_fii['sellValue'], errors='coerce')
        
        # Chart
        fig = go.Figure()
        
        for category in df_fii['category'].unique():
            subset = df_fii[df_fii['category'] == category]
            fig.add_trace(go.Bar(x=subset['date'], y=subset['netValue'], name=category))
            
        fig.update_layout(title="Net Buy/Sell Value (Crores)", barmode='group')
        st.plotly_chart(fig, width='stretch')
        
        st.dataframe(df_fii, use_container_width=True)
    else:
        st.info("No FII/DII data available.")

def page_insider_activity():
    st.header("🕵️ Insider Trading Activity")
    
    insider_data = load_market_data("insider_trading")
    if insider_data:
        df = pd.DataFrame(insider_data)
        
        # Filters
        search = st.text_input("Search Symbol or Company", "")
        if search:
            df = df[df['symbol'].str.contains(search, case=False, na=False) | df['company'].str.contains(search, case=False, na=False)]
            
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No Insider Trading data available.")

def page_strategy_screener():
    st.header("🔍 Strategy Screener")
    st.write("Filter stocks based on technical indicators and patterns.")
    
    col1, col2 = st.columns([1, 2])
    
    criteria = {}
    
    with col1:
        st.subheader("Filters")
        
        # RSI
        enable_rsi = st.checkbox("RSI Filter")
        if enable_rsi:
            rsi_range = st.slider("RSI Range", 0, 100, (30, 70))
            if st.checkbox("Oversold (RSI < Min)"):
                criteria['rsi_min'] = None
                criteria['rsi_max'] = rsi_range[0]
            elif st.checkbox("Overbought (RSI > Max)"):
                 criteria['rsi_min'] = rsi_range[1]
                 criteria['rsi_max'] = None
            else:
                 # Standard range filter (Inside range) - Logic in screener needs update if we want 'inside'
                 # But usually people want outside: e.g. < 30 or > 70
                 # For now, let's just stick to the two checkboxes above for simplicity
                 st.info("Select Oversold or Overbought to filter.")

        # SMA Trend
        if st.checkbox("Price > SMA 50"):
            criteria['price_gt_sma'] = 'SMA_50'
            
        if st.checkbox("Price > SMA 200"):
            criteria['price_gt_sma'] = 'SMA_200'
            
        if st.checkbox("Golden Cross (SMA 50 > SMA 200)"):
            criteria['sma_gt_sma'] = ('SMA_50', 'SMA_200')
            
        # Patterns
        patterns = ["CDL_DOJI", "CDL_HAMMER", "CDL_ENGULFING", "CDL_SHOOTINGSTAR"]
        selected_pattern = st.selectbox("Candlestick Pattern", ["None"] + patterns)
        if selected_pattern != "None":
            criteria['pattern'] = selected_pattern
            
        # Volume
        if st.checkbox("Volume Spike (> 1.5x Avg)"):
            criteria['volume_spike'] = True
            
        run_screen = st.button("Run Screener", type="primary")

    with col2:
        if run_screen:
            screener = StockScreener(DATA_DIR)
            with st.spinner("Screening stocks..."):
                results = screener.apply_filter(criteria)
            
            if not results.empty:
                st.success(f"Found {len(results)} matches!")
                st.dataframe(results.set_index("Symbol"), use_container_width=True)
            else:
                st.warning("No stocks matched your criteria.")

def page_database_info():
    st.header("🗄️ Database Data Dictionary")
    st.write("Overview of the trading system's database structure and available data.")

    tab1, tab2, tab3 = st.tabs(["OHLC Dictionary", "Market Stats & Fundamentals", "Table Statistics"])

    with tab1:
        st.subheader("Data Dictionary: OHLC Tables (SQLite/Parquet)")
        st.markdown("""
        Historical price data is stored in SQLite and Parquet files.
        Tables follow the pattern: `{symbol}_{interval}_ohlc`
        
        | Column Name | Data Type | Description |
        | :--- | :--- | :--- |
        | `datetime` | TIMESTAMP | The beginning of the time period for the data point. |
        | `Open` | REAL | The price at which the symbol first traded during the period. |
        | `High` | REAL | The highest price reached during the period. |
        | `Low` | REAL | The lowest price reached during the period. |
        | `Close` | REAL | The last price at which the symbol traded during the period. |
        | `Volume` | INTEGER | The total number of shares/contracts traded during the period. |
        | `SMA_20` | REAL | 20-period Simple Moving Average of the `Close` price. |
        | `RSI_14` | REAL | 14-period Relative Strength Index. |
        """)

    with tab2:
        st.subheader("Non-Price Data Management")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("📊 Market Statistics (JSON)")
            st.markdown("""
            Stored in `/data/processed/market_stats/`
            - **fii_dii.json**: FII/DII Net values.
            - **insider_trading.json**: Insider trade records.
            - **upcoming_results.json**: Earnings calendar.
            """)
        
        with col2:
            st.info("🏢 Fundamentals (On-Demand)")
            st.markdown("""
            Fetched in real-time via `libs/fundamentals.py`
            - **Key Metrics**: Market Cap, PE, ROE, etc.
            - **Quarterly Results**: Past 10-12 quarters.
            - **Shareholding**: Promoter, FII, DII patterns.
            """)

    with tab3:
        st.subheader("Database Table Statistics")
        try:
            import sqlite3
            conn = sqlite3.connect(PROJECT_ROOT / "data" / "trading.db")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            st.write(f"Total Tables in Database: **{len(tables)}**")
            
            # Simple list of tables
            table_names = [t[0] for t in tables]
            st.selectbox("Explore Table List", table_names)
            
            if st.button("Refresh Statistics"):
                st.rerun()

            conn.close()
        except Exception as e:
            st.error(f"Error fetching database statistics: {e}")

def page_data_management():
    st.header("📊 Historical Data Management")
    st.caption("Download, view, and manage multi-timeframe OHLCV data")
    
    from libs.historical_data_manager import HistoricalDataManager
    
    manager = HistoricalDataManager()
    
    tab1, tab2, tab3 = st.tabs(["Symbol Data Viewer", "Download Manager", "Data Management"])
    
    with tab1:
        st.subheader("📈 Symbol Data Viewer")
        
        # Symbol and Timeframe Selection
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            # Get available symbols
            available_symbols = manager.get_available_symbols()
            if available_symbols:
                symbol = st.selectbox("Select Symbol", available_symbols, key="viewer_symbol")
            else:
                st.info("No data downloaded yet. Use the Download Manager tab to get started.")
                symbol = None
        
        with col2:
            if symbol:
                available_timeframes = manager.get_available_timeframes(symbol)
                if available_timeframes:
                    timeframe = st.selectbox("Timeframe", available_timeframes, key="viewer_timeframe")
                else:
                    st.warning(f"No timeframes available for {symbol}")
                    timeframe = None
            else:
                timeframe = None
        
        with col3:
            if symbol and timeframe:
                # Quick date range selector
                date_range = st.selectbox(
                    "Quick Range",
                    ["All Data", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 1 Year", "Custom"],
                    key="quick_range"
                )
            else:
                date_range = None
        
        if symbol and timeframe:
            # Calculate date range based on selection
            from datetime import datetime, timedelta
            
            end_date_val = datetime.now()
            start_date_val = None
            
            if date_range == "Last 7 Days":
                start_date_val = end_date_val - timedelta(days=7)
            elif date_range == "Last 30 Days":
                start_date_val = end_date_val - timedelta(days=30)
            elif date_range == "Last 90 Days":
                start_date_val = end_date_val - timedelta(days=90)
            elif date_range == "Last 1 Year":
                start_date_val = end_date_val - timedelta(days=365)
            elif date_range == "Custom":
                col1, col2 = st.columns(2)
                with col1:
                    start_date_val = st.date_input("Start Date", value=None, key="viewer_start")
                with col2:
                    end_date_val = st.date_input("End Date", value=datetime.now(), key="viewer_end")
            
            # Load and display data
            try:
                df = manager.get_symbol_data(
                    symbol,
                    timeframe,
                    start_date_val.strftime('%Y-%m-%d') if start_date_val else None,
                    end_date_val.strftime('%Y-%m-%d') if end_date_val else None
                )
                
                if not df.empty:
                    # Data statistics in a nice card layout
                    st.markdown("---")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.metric("📊 Records", f"{len(df):,}")
                    with col2:
                        st.metric("📅 First Date", df.index.min().strftime('%Y-%m-%d'))
                    with col3:
                        st.metric("📅 Last Date", df.index.max().strftime('%Y-%m-%d'))
                    with col4:
                        st.metric("💰 Latest Close", f"₹{df['Close'].iloc[-1]:.2f}")
                    with col5:
                        change_pct = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                        st.metric("📈 Period Change", f"{change_pct:+.2f}%")
                    
                    st.markdown("---")
                    
                    # Enhanced Chart with controls
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    
                    # Chart type selector
                    col1, col2, col3 = st.columns([2, 2, 6])
                    with col1:
                        chart_type = st.radio("Chart Type", ["Candlestick", "Line"], horizontal=True, key="chart_type")
                    with col2:
                        show_volume = st.checkbox("Show Volume", value=True, key="show_volume")
                    
                    # Create subplots if volume is enabled
                    if show_volume:
                        fig = make_subplots(
                            rows=2, cols=1,
                            shared_xaxes=True,
                            vertical_spacing=0.03,
                            row_heights=[0.7, 0.3],
                            subplot_titles=(f'{symbol} - {timeframe}', 'Volume')
                        )
                    else:
                        fig = go.Figure()
                    
                    # Add price chart
                    if chart_type == "Candlestick":
                        candlestick = go.Candlestick(
                            x=df.index,
                            open=df['Open'],
                            high=df['High'],
                            low=df['Low'],
                            close=df['Close'],
                            name=symbol,
                            increasing_line_color='#26a69a',
                            decreasing_line_color='#ef5350'
                        )
                        if show_volume:
                            fig.add_trace(candlestick, row=1, col=1)
                        else:
                            fig.add_trace(candlestick)
                    else:
                        line = go.Scatter(
                            x=df.index,
                            y=df['Close'],
                            mode='lines',
                            name=symbol,
                            line=dict(color='#2196F3', width=2)
                        )
                        if show_volume:
                            fig.add_trace(line, row=1, col=1)
                        else:
                            fig.add_trace(line)
                    
                    # Add volume bars if enabled
                    if show_volume:
                        colors = ['#26a69a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ef5350' 
                                 for i in range(len(df))]
                        
                        volume_bars = go.Bar(
                            x=df.index,
                            y=df['Volume'],
                            name='Volume',
                            marker_color=colors,
                            showlegend=False
                        )
                        fig.add_trace(volume_bars, row=2, col=1)
                    
                    # Update layout with range selector and slider
                    fig.update_layout(
                        height=700,
                        showlegend=True,
                        hovermode='x unified',
                        xaxis=dict(
                            rangeslider=dict(visible=False),
                            rangeselector=dict(
                                buttons=list([
                                    dict(count=1, label="1D", step="day", stepmode="backward"),
                                    dict(count=7, label="1W", step="day", stepmode="backward"),
                                    dict(count=1, label="1M", step="month", stepmode="backward"),
                                    dict(count=3, label="3M", step="month", stepmode="backward"),
                                    dict(count=6, label="6M", step="month", stepmode="backward"),
                                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                                    dict(step="all", label="All")
                                ]),
                                bgcolor='#f0f0f0',
                                activecolor='#2196F3'
                            ),
                            type='date'
                        ),
                        yaxis=dict(title="Price (₹)"),
                        template='plotly_white',
                        margin=dict(l=50, r=50, t=50, b=50)
                    )
                    
                    if show_volume:
                        fig.update_yaxes(title_text="Price (₹)", row=1, col=1)
                        fig.update_yaxes(title_text="Volume", row=2, col=1)
                        fig.update_xaxes(title_text="Date", row=2, col=1)
                    else:
                        fig.update_yaxes(title_text="Price (₹)")
                        fig.update_xaxes(title_text="Date")
                    
                    # Display chart
                    st.plotly_chart(fig, use_container_width=True, config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                    })
                    
                    # Data table in expandable section
                    with st.expander("📋 View Data Table", expanded=False):
                        st.dataframe(
                            df.tail(100).style.format({
                                'Open': '₹{:.2f}',
                                'High': '₹{:.2f}',
                                'Low': '₹{:.2f}',
                                'Close': '₹{:.2f}',
                                'Volume': '{:,.0f}'
                            }),
                            use_container_width=True,
                            height=400
                        )
                    
                    # Download options
                    col1, col2 = st.columns(2)
                    with col1:
                        csv = df.to_csv()
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name=f"{symbol}_{timeframe}_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    with col2:
                        # Export chart as image button (info only)
                        st.info("💡 Use the camera icon in the chart toolbar to save as image")
                else:
                    st.warning("⚠️ No data found for the selected criteria")
            
            except Exception as e:
                st.error(f"❌ Error loading data: {e}")
                import traceback
                with st.expander("Error Details"):
                    st.code(traceback.format_exc())
    
    with tab2:
        st.subheader("📥 Download Manager")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            symbols_input = st.text_input(
                "Symbols (comma-separated)",
                placeholder="e.g., RELIANCE, TCS, INFY",
                key="download_symbols"
            )
        
        with col2:
            timeframes = st.multiselect(
                "Timeframes",
                options=['1d', '1w', '1M', '1h', '30m', '15m', '10m', '5m', '1m'],
                default=['1d'],
                key="download_timeframes"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input(
                "From Date",
                value=datetime(1995, 1, 1),
                key="download_from"
            )
        with col2:
            to_date = st.date_input(
                "To Date",
                value=datetime.now(),
                key="download_to"
            )
        
        if st.button("📥 Download Data", type="primary"):
            if not symbols_input:
                st.error("Please enter at least one symbol")
            elif not timeframes:
                st.error("Please select at least one timeframe")
            else:
                symbols = [s.strip().upper() for s in symbols_input.split(',')]
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total = len(symbols) * len(timeframes)
                current = 0
                
                results = {}
                
                for symbol in symbols:
                    status_text.text(f"Downloading {symbol}...")
                    
                    symbol_results = manager.download_symbol_data(
                        symbol,
                        timeframes,
                        from_date.strftime('%Y-%m-%d'),
                        to_date.strftime('%Y-%m-%d')
                    )
                    
                    results[symbol] = symbol_results
                    
                    for tf, success in symbol_results.items():
                        current += 1
                        progress_bar.progress(current / total)
                
                status_text.empty()
                progress_bar.empty()
                
                # Show results
                st.success("Download complete!")
                
                successful = sum(1 for r in results.values() for s in r.values() if s)
                failed = total - successful
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("✅ Successful", successful)
                with col2:
                    st.metric("❌ Failed", failed)
                
                # Show details
                if failed > 0:
                    st.warning("Failed downloads:")
                    for symbol, symbol_results in results.items():
                        for tf, success in symbol_results.items():
                            if not success:
                                st.write(f"- {symbol} {tf}")
    
    with tab3:
        st.subheader("🗂️ Data Management")
        
        available_symbols = manager.get_available_symbols()
        
        if not available_symbols:
            st.info("No data downloaded yet. Use the Download Manager tab to get started.")
        else:
            st.write(f"**Total Symbols:** {len(available_symbols)}")
            
            # Build data table
            data_rows = []
            for symbol in available_symbols:
                info = manager.get_data_info(symbol)
                for timeframe, metadata in info.items():
                    data_rows.append({
                        'Symbol': symbol,
                        'Timeframe': timeframe,
                        'First Date': metadata['first_date'],
                        'Last Date': metadata['last_date'],
                        'Records': metadata['record_count'],
                        'Last Updated': metadata['last_updated']
                    })
            
            df_management = pd.DataFrame(data_rows)
            
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                filter_symbol = st.text_input("Filter by Symbol", key="mgmt_filter_symbol")
            with col2:
                filter_timeframe = st.selectbox(
                    "Filter by Timeframe",
                    options=['All'] + manager.SUPPORTED_TIMEFRAMES,
                    key="mgmt_filter_tf"
                )
            
            # Apply filters
            filtered_df = df_management.copy()
            if filter_symbol:
                filtered_df = filtered_df[filtered_df['Symbol'].str.contains(filter_symbol, case=False)]
            if filter_timeframe != 'All':
                filtered_df = filtered_df[filtered_df['Timeframe'] == filter_timeframe]
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # Bulk actions
            st.subheader("Bulk Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Update All Daily Data"):
                    with st.spinner("Updating all symbols..."):
                        for symbol in available_symbols:
                            manager.update_symbol_data(symbol, ['1d'])
                    st.success("All daily data updated!")
            
            with col2:
                if st.button("🗑️ Delete Symbol Data"):
                    delete_symbol = st.text_input("Symbol to delete", key="delete_symbol_input")
                    if delete_symbol and st.button("Confirm Delete", type="primary"):
                        if manager.delete_symbol_data(delete_symbol.upper()):
                            st.success(f"Deleted all data for {delete_symbol.upper()}")
                            st.rerun()
                        else:
                            st.error("Failed to delete data")


# MAIN
def page_ml_predictions():
    """
    ML Predictions page with comprehensive features.
    """
    st.header("🤖 ML Stock Predictions")
    st.caption("Machine Learning powered stock direction predictions")
    
    from libs.ml_pipeline import MLPipeline
    from libs.historical_data_manager import HistoricalDataManager
    from libs.feature_engineering import FeatureEngineer
    
    # Check if models directory exists
    models_dir = Path('models')
    if not models_dir.exists():
        st.warning("⚠️ No trained models found. Please train a model first.")
        st.info("💡 Use the ML Pipeline to train models: `python -c \"from libs.ml_pipeline import train_model_for_symbol; train_model_for_symbol('TCS', '1d', '3class', 'xgboost')\"`")
        return
    
    # Get available models
    model_files = list(models_dir.glob("*_v1.joblib"))
    if not model_files:
        st.warning("⚠️ No trained models found.")
        return
    
    # Extract symbol-timeframe combinations
    available_models = []
    for model_file in model_files:
        parts = model_file.stem.split('_')
        if len(parts) >= 3:
            symbol = parts[0]
            timeframe = parts[1]
            available_models.append(f"{symbol}_{timeframe}")
    
    available_models = list(set(available_models))
    
    # Sidebar controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Model Selection")
    
    if available_models:
        selected_model = st.sidebar.selectbox(
            "Choose Model",
            available_models,
            format_func=lambda x: f"{x.split('_')[0]} - {x.split('_')[1]}"
        )
        
        symbol, timeframe = selected_model.split('_')
        
        # Model version
        version = st.sidebar.selectbox("Model Version", ["v1"], index=0)
        
        # Prediction horizon
        horizon = st.sidebar.slider("Prediction Horizon (days)", 1, 5, 1)
        
    else:
        st.error("No models available")
        return
    
    # Main content
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Predictions", 
        "📈 Feature Importance", 
        "🎯 Model Performance",
        "📜 Prediction History",
        "🤖 Advanced Models",
        "🧠 Explainability"
    ])
    
    # Load model
    try:
        pipeline = MLPipeline(symbol, timeframe)
        pipeline.load_model(version=version)
        
        # Load latest data
        manager = HistoricalDataManager()
        df = manager.get_symbol_data(symbol, timeframe)
        
        if df.empty:
            st.error(f"No data found for {symbol} {timeframe}")
            return
        
        # Engineer features
        engineer = FeatureEngineer(df)
        features = engineer.build_all()
        
        # Combine with OHLCV
        ml_data = pd.concat([df, features], axis=1).dropna()
        
        if len(ml_data) == 0:
            st.error("No valid data after feature engineering")
            return
        
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return
    
    # Tab 1: Predictions
    with tab1:
        st.subheader(f"📊 Predictions for {symbol}")
        
        # Get latest data point
        latest_date = ml_data.index[-1]
        latest_features = ml_data[features.columns].iloc[[-1]]
        
        # Make prediction
        try:
            predictions, probabilities = pipeline.predict(latest_features)
            pred_class = predictions[0]
            pred_proba = probabilities[0]
            
            # Class labels
            class_labels = {0: "📉 Down", 1: "➡️ Neutral", 2: "📈 Up"}
            class_colors = {0: "#ef5350", 1: "#ffa726", 2: "#26a69a"}
            
            # Display prediction
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 2, 3])
            
            with col1:
                st.metric(
                    "Latest Close",
                    f"₹{ml_data['Close'].iloc[-1]:.2f}",
                    f"{ml_data['Close'].pct_change().iloc[-1]:.2%}"
                )
            
            with col2:
                st.metric(
                    "Prediction",
                    class_labels[pred_class],
                    f"{pred_proba[pred_class]:.1%} confidence"
                )
            
            with col3:
                st.metric(
                    "Date",
                    latest_date.strftime('%Y-%m-%d'),
                    f"Next {horizon} day(s)"
                )
            
            # Confidence gauge
            st.markdown("---")
            st.subheader("Confidence Breakdown")
            
            col1, col2, col3 = st.columns(3)
            
            for idx, (col, (class_id, label)) in enumerate(zip([col1, col2, col3], class_labels.items())):
                with col:
                    confidence = pred_proba[class_id] * 100
                    
                    # Create gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=confidence,
                        title={'text': label},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': class_colors[class_id]},
                            'steps': [
                                {'range': [0, 33], 'color': "lightgray"},
                                {'range': [33, 66], 'color': "gray"},
                                {'range': [66, 100], 'color': "darkgray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 50
                            }
                        }
                    ))
                    
                    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig, use_container_width=True)
            
            # Recent price action
            st.markdown("---")
            st.subheader("Recent Price Action (Last 30 Days)")
            
            recent_data = ml_data.tail(30)
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=recent_data.index,
                open=recent_data['Open'],
                high=recent_data['High'],
                low=recent_data['Low'],
                close=recent_data['Close'],
                name=symbol
            ))
            
            # Add prediction marker
            fig.add_trace(go.Scatter(
                x=[latest_date],
                y=[ml_data['Close'].iloc[-1]],
                mode='markers+text',
                marker=dict(size=15, color=class_colors[pred_class], symbol='star'),
                text=[class_labels[pred_class]],
                textposition="top center",
                name="Prediction"
            ))
            
            fig.update_layout(
                title=f"{symbol} - Last 30 Days with Prediction",
                yaxis_title="Price (₹)",
                xaxis_title="Date",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Key statistics
            st.markdown("---")
            st.subheader("Key Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                volatility = ml_data['volatility_20d'].iloc[-1]
                st.metric("Volatility (20d)", f"{volatility:.4f}")
            
            with col2:
                volume_momentum = ml_data['volume_momentum_10d'].iloc[-1]
                st.metric("Volume Momentum", f"{volume_momentum:.2f}x")
            
            with col3:
                rsi = ml_data['RSI_14'].iloc[-1] if 'RSI_14' in ml_data.columns else None
                if rsi:
                    st.metric("RSI (14)", f"{rsi:.1f}")
            
            with col4:
                macd = ml_data['MACD'].iloc[-1] if 'MACD' in ml_data.columns else None
                if macd:
                    st.metric("MACD", f"{macd:.2f}")
            
        except Exception as e:
            st.error(f"Error making prediction: {e}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
    
    # Tab 2: Feature Importance
    with tab2:
        st.subheader("📈 Feature Importance Analysis")
        
        try:
            # Get feature importance
            importance_df = pipeline.get_feature_importance(top_n=20)
            
            # Bar chart
            fig = px.bar(
                importance_df,
                x='importance',
                y='feature',
                orientation='h',
                title="Top 20 Most Important Features",
                labels={'importance': 'Importance Score', 'feature': 'Feature'},
                color='importance',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Feature importance table
            st.subheader("Feature Importance Table")
            st.dataframe(
                importance_df.style.format({'importance': '{:.4f}'}),
                width="stretch",
                height=400
            )
            
            # Feature categories breakdown
            st.markdown("---")
            st.subheader("Feature Categories")
            
            categories = {
                'Returns': [f for f in importance_df['feature'] if 'return' in f.lower()],
                'Volatility': [f for f in importance_df['feature'] if 'vol' in f.lower()],
                'Momentum': [f for f in importance_df['feature'] if any(x in f.lower() for x in ['momentum', 'roc'])],
                'Volume': [f for f in importance_df['feature'] if 'volume' in f.lower() or 'vwap' in f.lower()],
                'Patterns': [f for f in importance_df['feature'] if any(x in f.lower() for x in ['range', 'gap', 'shadow', 'body'])]
            }
            
            category_importance = {}
            for cat, features in categories.items():
                total_imp = importance_df[importance_df['feature'].isin(features)]['importance'].sum()
                category_importance[cat] = total_imp
            
            # Pie chart
            fig = px.pie(
                values=list(category_importance.values()),
                names=list(category_importance.keys()),
                title="Importance by Feature Category"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error displaying feature importance: {e}")
    
    # Tab 3: Model Performance
    with tab3:
        st.subheader("🎯 Model Performance Metrics")
        
        st.info("📝 **Note:** Performance metrics are from the test set during training.")
        
        # Load model metadata
        try:
            import joblib
            metadata_path = models_dir / f"{symbol}_{timeframe}_{version}_metadata.joblib"
            metadata = joblib.load(metadata_path)
            
            st.markdown("### Model Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Symbol", metadata['symbol'])
            with col2:
                st.metric("Timeframe", metadata['timeframe'])
            with col3:
                st.metric("Model Type", metadata['model_type'])
            
            st.markdown("---")
            st.markdown("### Training Configuration")
            st.write(f"**Classification Type:** {metadata['classification_type']}")
            st.write(f"**Features Used:** {len(metadata['feature_names'])}")
            st.write(f"**Target Variable:** {metadata['target_name']}")
            
            # Performance metrics (would need to be saved during training)
            st.markdown("---")
            st.markdown("### Performance Metrics")
            st.warning("⚠️ To display performance metrics, re-train the model with metric saving enabled.")
            
        except Exception as e:
            st.error(f"Error loading model metadata: {e}")
    
    # Tab 4: Prediction History
    with tab4:
        st.subheader("📜 Prediction History & Performance Tracking")
        
        from libs.prediction_tracker import PredictionTracker
        
        tracker = PredictionTracker()
        
        # Auto-save current prediction
        st.markdown("### Current Prediction")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info("💡 Save predictions to track accuracy over time")
        
        with col2:
            if st.button("💾 Save Prediction", type="primary"):
                try:
                    # Get latest prediction
                    latest_features = ml_data[features.columns].iloc[[-1]]
                    predictions, probabilities = pipeline.predict(latest_features)
                    pred_class = predictions[0]
                    # Store standard prediction
                    pred_class = predictions[0]
                    confidence = probabilities[0][pred_class]
                    
                    tracker.save_prediction(
                        symbol=symbol,
                        timeframe=timeframe,
                        prediction_class=int(pred_class),
                        confidence=float(confidence),
                        probabilities=probabilities[0].tolist(),
                        model_version=version,
                        close_price=float(latest_features['Close'].iloc[0])
                    )
                    st.success("Prediction saved!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error saving prediction: {e}")
        
        st.markdown("---")
        
        # Historical predictions
        st.markdown("### Historical Predictions")
        
        # Time range selector
        col1, col2 = st.columns([2, 1])
        
        with col1:
            days_back = st.slider("Days to show", 7, 90, 30, key="history_days")
        
        with col2:
            total_predictions = len(tracker.get_prediction_history(symbol, timeframe))
            st.metric("Total Predictions", total_predictions)
        
        # Get prediction history
        history = tracker.get_prediction_history(symbol, timeframe, days=days_back)
        
        if len(history) == 0:
            st.warning("⚠️ No prediction history found. Save predictions to start tracking!")
            st.info("💡 Click 'Save Prediction' above to record your first prediction")
        else:
            # Display history table
            st.markdown("#### Prediction Log")
            
            # Format for display
            display_df = history.copy()
            display_df['prediction_date'] = pd.to_datetime(display_df['prediction_date'])
            
            # Add class labels
            class_labels = {0: "📉 Down", 1: "➡️ Neutral", 2: "📈 Up"}
            display_df['Predicted'] = display_df['predicted_class'].map(class_labels)
            
            if 'actual_class' in display_df.columns:
                display_df['Actual'] = display_df['actual_class'].map(
                    lambda x: class_labels.get(int(x), "⏳ Pending") if pd.notna(x) else "⏳ Pending"
                )
                display_df['Correct'] = display_df['is_correct'].map(
                    lambda x: "✅" if x == 1 else ("❌" if x == 0 else "⏳")
                )
            
            # Select columns to display
            display_cols = ['prediction_date', 'Predicted', 'confidence_down', 'confidence_neutral', 'confidence_up']
            if 'Actual' in display_df.columns:
                display_cols.extend(['Actual', 'actual_return', 'Correct'])
            
            # Handle None values in actual_return for formatting
            if 'actual_return' in display_df.columns:
                display_df['actual_return'] = display_df['actual_return'].fillna(0)
            
            st.dataframe(
                display_df[display_cols].style.format({
                    'confidence_down': '{:.1%}',
                    'confidence_neutral': '{:.1%}',
                    'confidence_up': '{:.1%}',
                    'actual_return': '{:.2%}'
                }),
                width="stretch",
                height=400
            )
            
            # Performance metrics
            st.markdown("---")
            st.markdown("### Performance Metrics")
            
            metrics = tracker.calculate_accuracy(symbol, timeframe, days=days_back)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Predictions", metrics.get('total_predictions', 0))
            
            with col2:
                st.metric("With Outcomes", metrics.get('predictions_with_outcomes', 0))
            
            with col3:
                accuracy_pct = metrics.get('accuracy', 0) * 100
                st.metric("Accuracy", f"{accuracy_pct:.1f}%")
            
            with col4:
                correct = metrics.get('correct_predictions', 0)
                st.metric("Correct", correct)
            
            # Precision and Recall by class
            if metrics['predictions_with_outcomes'] > 0:
                st.markdown("---")
                st.markdown("#### Precision & Recall by Class")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Precision** (of predictions, how many were correct)")
                    precision = metrics['precision_by_class']
                    
                    pcol1, pcol2, pcol3 = st.columns(3)
                    with pcol1:
                        st.metric("📉 Down", f"{precision.get(0, 0):.1%}")
                    with pcol2:
                        st.metric("➡️ Neutral", f"{precision.get(1, 0):.1%}")
                    with pcol3:
                        st.metric("📈 Up", f"{precision.get(2, 0):.1%}")
                
                with col2:
                    st.markdown("**Recall** (of actual outcomes, how many did we predict)")
                    recall = metrics['recall_by_class']
                    
                    rcol1, rcol2, rcol3 = st.columns(3)
                    with rcol1:
                        st.metric("📉 Down", f"{recall.get(0, 0):.1%}")
                    with rcol2:
                        st.metric("➡️ Neutral", f"{recall.get(1, 0):.1%}")
                    with rcol3:
                        st.metric("📈 Up", f"{recall.get(2, 0):.1%}")
                
                # Performance trend chart
                if len(history) > 5:
                    st.markdown("---")
                    st.markdown("### Performance Trend")
                    
                    # Calculate rolling accuracy
                    history_sorted = history.sort_values('prediction_date')
                    history_sorted['prediction_date'] = pd.to_datetime(history_sorted['prediction_date'])
                    
                    # Only include predictions with outcomes
                    with_outcomes = history_sorted[history_sorted['is_correct'].notna()].copy()
                    
                    if len(with_outcomes) > 0:
                        # Calculate cumulative accuracy
                        with_outcomes['cumulative_correct'] = with_outcomes['is_correct'].cumsum()
                        with_outcomes['cumulative_total'] = range(1, len(with_outcomes) + 1)
                        with_outcomes['cumulative_accuracy'] = (
                            with_outcomes['cumulative_correct'] / with_outcomes['cumulative_total']
                        )
                        
                        # Plot
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=with_outcomes['prediction_date'],
                            y=with_outcomes['cumulative_accuracy'] * 100,
                            mode='lines+markers',
                            name='Cumulative Accuracy',
                            line=dict(color='#2196F3', width=2),
                            marker=dict(size=8)
                        ))
                        
                        # Add 50% baseline
                        fig.add_hline(
                            y=50, 
                            line_dash="dash", 
                            line_color="red",
                            annotation_text="Random Baseline (50%)",
                            annotation_position="right"
                        )
                        
                        # Add 33% baseline (3-class random)
                        fig.add_hline(
                            y=33.33, 
                            line_dash="dot", 
                            line_color="orange",
                            annotation_text="3-Class Random (33%)",
                            annotation_position="right"
                        )
                        
                        fig.update_layout(
                            title="Prediction Accuracy Over Time",
                            xaxis_title="Date",
                            yaxis_title="Accuracy (%)",
                            height=400,
                            yaxis=dict(range=[0, 100]),
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Download predictions
                        st.markdown("---")
                        st.markdown("### Export Data")
                        
                        csv = display_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Prediction History (CSV)",
                            data=csv,
                            file_name=f"{symbol}_{timeframe}_predictions.csv",
                            mime="text/csv"
                        )



    # Tab 5: Advanced Models (New)
    with tab5:
        st.subheader("🤖 Advanced Models & Ensembles")
        
        try:
            import torch
            from libs.sequence_generator import SequenceGenerator
            from libs.lstm_model import LSTMClassifier
            from libs.ensemble_models import VotingEnsemble
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### LSTM Deep Learning")
                # Generate sequence
                generator = SequenceGenerator(lookback=20)
                # Initialize path variable
                lstm_path = models_dir / f"{symbol}_{timeframe}_lstm_v1.pth"
                try:
                    # Get sequence for latest data
                    # Need scaling from saved scaler? The pipeline handles it?
                    # Ideally we should use the pipeline's feature engineering
                    # But sequence generator expects raw features?
                    # Let's use the features we already engineered in ml_data
                    
                    seq = generator.create_single_sequence(ml_data[features.columns])
                    
                    # Load LSTM model
                    lstm_model = LSTMClassifier(input_size=47, hidden_size=64, num_layers=1)
                    # Check for model file
                    # lstm_path defined above
                    
                    if lstm_path.exists():
                        checkpoint = torch.load(str(lstm_path), map_location='cpu')
                        lstm_model.load_state_dict(checkpoint['model_state_dict'])
                        lstm_model.eval()
                        
                        # Predict
                        with torch.no_grad():
                            output = lstm_model(torch.FloatTensor(seq))
                            lstm_probs = torch.softmax(output, dim=1).numpy()[0]
                            lstm_pred = torch.argmax(output, dim=1).item()
                        
                        # Display results
                        lstm_conf = lstm_probs[lstm_pred]
                        st.metric("LSTM Prediction", 
                                 ["Down", "Neutral", "Up"][lstm_pred],
                                 f"{lstm_conf:.1%}")
                        
                        # Probabilities chart
                        lstm_df = pd.DataFrame({
                            'Class': ['Down', 'Neutral', 'Up'],
                            'Probability': lstm_probs
                        })
                        st.bar_chart(lstm_df.set_index('Class'))
                    else:
                        st.warning(f"LSTM model not found at {lstm_path}")
                        st.info("Train LSTM model to verify this tab.")
                        
                except Exception as e:
                    st.error(f"Error running LSTM: {e}")
            
            with col2:
                st.markdown("### Ensemble Model")
                if lstm_path.exists():
                    # Create Voting Ensemble
                    xgb_probs = probabilities[0] # from XGBoost
                    # lstm_probs from above
                    
                    # Weighted average (40% XGB, 60% LSTM)
                    ensemble_probs = (0.4 * xgb_probs) + (0.6 * lstm_probs)
                    ensemble_pred = np.argmax(ensemble_probs)
                    ensemble_conf = ensemble_probs[ensemble_pred]
                    
                    st.metric("Ensemble Prediction",
                             ["Down", "Neutral", "Up"][ensemble_pred],
                             f"{ensemble_conf:.1%}")
                    
                    st.info(f"Combines XGBoost (40%) and LSTM (60%) for robust prediction.")
                    
                    # Comparison Table
                    comp_df = pd.DataFrame({
                        'Model': ['XGBoost', 'LSTM', 'Ensemble'],
                        'Prediction': [
                            ["Down", "Neutral", "Up"][predictions[0]],
                            ["Down", "Neutral", "Up"][lstm_pred],
                            ["Down", "Neutral", "Up"][ensemble_pred]
                        ],
                        'Confidence': [
                            f"{probabilities[0][predictions[0]]:.1%}",
                            f"{lstm_conf:.1%}",
                            f"{ensemble_conf:.1%}"
                        ]
                    })
                    st.table(comp_df)
                else:
                    st.info("Train LSTM model to enable Ensemble predictions")

        except ImportError as e:
            st.error(f"Import Error (Advanced Models): {e}")
            st.warning("Make sure torch is installed.")
            
    # Tab 6: Explainability (New)
    with tab6:
        st.subheader("🧠 SHAP Model Explainability")
        
        try:
            from libs.model_explainer import ModelExplainer, explain_xgboost_prediction
            import matplotlib.pyplot as plt
            
            st.write("Understanding why the model made this prediction for the latest data point.")
            
            # Create explainer
            # Need pipeline.model
            if hasattr(pipeline, 'model'):
                with st.spinner("Calculating SHAP values..."):
                    latest_sample = ml_data[features.columns].iloc[-1].values
                    feature_names = features.columns.tolist()
                    
                    # Waterfall plot
                    st.markdown("### Decision Waterfall")
                    st.caption("How each feature pushed the prediction from the base value.")
                    
                    explainer = ModelExplainer(pipeline.model, model_type='tree')
                    # Need to reshape for latest_sample
                    try:
                        fig = explainer.plot_waterfall(
                            latest_sample, 
                            feature_names,
                            class_idx=int(predictions[0]),
                            max_display=15
                        )
                        st.pyplot(fig)
                        plt.close()
                    except Exception as e:
                        st.error(f"Error plotting waterfall: {e}")
                    
                    # Top Features
                    st.markdown("### Top Contributing Features")
                    try:
                        explanation = explain_xgboost_prediction(
                            pipeline.model, latest_sample, feature_names,
                            class_names=['Down', 'Neutral', 'Up']
                        )
                        
                        top_shap = pd.DataFrame(explanation['top_features'])
                        st.dataframe(
                            top_shap[['feature', 'shap_value', 'feature_value', 'abs_shap_value']].style.background_gradient(subset=['shap_value'], cmap='RdBu'),
                            width="stretch"
                        )
                    except Exception as e:
                         st.error(f"Error calculating explanation: {e}")
            else:
                st.error("Model not loaded in pipeline.")
                
        except Exception as e:
            st.error(f"Error generating explanations: {e}")




def page_pkscreener():
    """
    PKScreener Integration Page.
    """
    st.title("🚀 PKScreener Integration")
    st.markdown("Run advanced technical scans using [PKScreener](https://github.com/pkjmesra/PKScreener).")

    # Import adapter
    sys.path.append(str(PROJECT_ROOT)) # Ensure root is in path
    try:
        from libs.pkscreener_adapter import game_scanner
    except ImportError as e:
        st.error(f"Failed to import PKScreener Adapter: {e}")
        return

    # Mode Selection (Outside form for interactivity)
    scan_mode = st.radio("Selection Mode", ["Predefined Index", "Saved Stock Lists" , "Upload New List"], horizontal=True)

    # Database Initialization (Ensure table exists)
    import sqlite3
    db_path = PROJECT_ROOT / "data" / "trading.db"
    
    def init_custom_lists_db():
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS custom_stock_lists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    symbols TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    init_custom_lists_db()

    # Helpers
    def get_saved_lists():
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql("SELECT name, symbols FROM custom_stock_lists ORDER BY created_at DESC", conn)

    def save_list(name, symbols):
        if not name: return False, "Name required"
        if not symbols: return False, "No symbols"
        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO custom_stock_lists (name, symbols) VALUES (?, ?)", 
                    (name, ",".join(symbols))
                )
            return True, "Saved"
        except Exception as e:
            return False, str(e)

    # Configuration Form
    with st.form("pkscreener_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            scan_option = st.selectbox(
                "Scan Type",
                options=["X"],
                format_func=lambda x: "Scanners (X)" if x == "X" else x
            )
            
        with col2:
            custom_stock_list = []
            index_option = "12" # Default fallback
            selected_list_name = None
            
            if scan_mode == "Predefined Index":
                index_option = st.selectbox(
                    "Index / Stock List",
                    options=["12", "5", "8", "11", "13", "14"],
                    format_func=lambda x: {
                        "12": "Nifty 50",
                        "5": "Nifty Next 50", 
                        "8": "Nifty 100",
                        "11": "Nifty 500",
                        "13": "Newly Listed",
                        "14": "F&O Stocks"
                    }.get(x, x)
                )
            elif scan_mode == "Saved Stock Lists":
                df_lists = get_saved_lists()
                if not df_lists.empty:
                    selected_list_name = st.selectbox("Select Saved List", df_lists['name'].tolist())
                else:
                    st.warning("No saved lists found.")
                    
            else: # Upload New
                st.markdown("**Upload New List**")
                uploaded_file = st.file_uploader("Upload CSV/Excel", type=['csv', 'xlsx'])
                text_symbols = st.text_area("Or copy-paste symbols")
                save_name = st.text_input("Save as (Optional Name to store in DB)")
                
        with col3:
            sub_option = st.selectbox(
                "Strategy",
                options=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35"],
                format_func=lambda x: {
                    "0": "Full Screening",
                    "1": "Momentum",
                    "2": "Breakouts",
                    "3": "Consolidation",
                    "4": "Volume Monitor",
                    "5": "RSI / ADX / Ichimoku",
                    "6": "Reversals / MAs",
                    "7": "Chart Patterns",
                    "8": "CCI / MA / Volume",
                    "9": "Volume Shockers",
                    "10": "Kellner Channels",
                    "11": "Stock Performance",
                    "12": "Nifty/Market Strength",
                    "13": "Momentum (Short)",
                    "14": "Breakout (Short)",
                    "15": "Consolidation (Short)",
                    "16": "Volume Monitor (Short)",
                    "17": "Stock Performance (Short)",
                    "18": "Live Trends",
                    "19": "Live Trends (Short)",
                    "20": "Closing / Next Day",
                    "21": "Closing / Next Day (Short)",
                    "22": "Intraday (High Vol)",
                    "23": "Intraday (Momentum)",
                    "24": "Intraday (Reversals)",
                    "25": "Intraday (Breakouts)",
                    "26": "Intraday (Volume)",
                    "27": "Intraday (High Vol Short)",
                    "28": "Intraday (Momentum Short)",
                    "29": "Intraday (Reversals Short)",
                    "30": "Intraday (Breakouts Short)",
                    "31": "Intraday (Volume Short)",
                    "32": "Quick Daily Scans",
                    "33": "Quick Daily Scans (Short)",
                    "34": "Live Index Scan",
                    "35": "Live Index Scan (Short)"
                 }.get(x, f"Option {x}")
            )
            
        with st.expander("⚙️ Advanced Configuration (Timeframe, Period, Filters)"):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                cfg_duration = st.selectbox("Duration (Timeframe)", options=["1d", "15m", "5m", "1h"], index=0)
            with c2:
                cfg_period = st.selectbox("Lookback Period", options=["1y", "2y", "220d", "500d"], index=0)
            with c3:
                cfg_minvol = st.number_input("Min Volume", value=10000, step=5000)
            with c4:
                cfg_rsi = st.checkbox("Calc RSI Intraday", value=True)

        submit = st.form_submit_button("Run Scan 🔍")
        
    if submit:
        # Update Config
        settings = {
            'config.duration': cfg_duration,
            'config.period': cfg_period,
            'filters.minimumvolume': cfg_minvol,
            'config.calculatersiintraday': 'y' if cfg_rsi else 'n'
        }
        if not game_scanner.update_config(settings):
            st.warning("Could not update PKScreener configuration. Proceeding with defaults.")
            
        # Process Custom List
        final_stock_list = None
        
        # Mode 1: Saved List
        if scan_mode == "Saved Stock Lists":
            if selected_list_name:
                df_lists = get_saved_lists()
                symbols_str = df_lists[df_lists['name'] == selected_list_name]['symbols'].iloc[0]
                final_stock_list = symbols_str.split(',')
            else:
                st.error("Please select a list.")
                return

        # Mode 2: Upload logic
        elif scan_mode == "Upload New List":
            final_stock_list = []
            
            # 1. From Text
            if text_symbols:
                raw_list = text_symbols.replace('\n', ',').split(',')
                final_stock_list.extend([s.strip().upper() for s in raw_list if s.strip()])
                
            # 2. From File
            if uploaded_file:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df_upload = pd.read_csv(uploaded_file)
                    else:
                        df_upload = pd.read_excel(uploaded_file)
                    
                    found_col = None
                    possible_cols = ['Symbol', 'SYMBOL', 'Stock Code', 'Ticker']
                    for col in df_upload.columns:
                        if col in possible_cols:
                            found_col = col
                            break
                    
                    if found_col:
                        final_stock_list.extend(df_upload[found_col].astype(str).str.upper().tolist())
                    else:
                         final_stock_list.extend(df_upload.iloc[:, 0].astype(str).str.upper().tolist())
                         
                    st.info(f"Loaded {len(final_stock_list)} symbols from file.")
                    
                except Exception as e:
                    st.error(f"Error reading file: {e}")
            
            final_stock_list = list(set(final_stock_list))
            
            # Save to DB if requested
            if save_name and final_stock_list:
                success, msg = save_list(save_name, final_stock_list)
                if success:
                    st.success(f"Running scan and SAVED list as '{save_name}' to Database!")
                else:
                    st.error(f"Failed to save list: {msg}")

            if not final_stock_list:
                st.error("No valid symbols found in input.")
                return

        with st.spinner(f"Running PKScreener (Option {scan_option}:{index_option}:{sub_option})... This may take a minute."):
            # Run the scan asynchronously
            import asyncio
            try:
                # Streamlit runs in a loop, so we can use run_until_complete or similar if compatible,
                # but asyncio.run() is safer for isolated calls.
                results_df = asyncio.run(game_scanner.run_scan(scan_option, index_option, sub_option, stock_list=final_stock_list))
                
                if not results_df.empty:
                    st.success(f"Scan Completed! Found {len(results_df)} stocks.")
                    st.dataframe(results_df, width="stretch")
                    
                    # Convert to CSV for download
                    csv = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name='pkscreener_results.csv',
                        mime='text/csv',
                    )
                else:
                    st.warning("No stocks found matching criteria or error executing scan.")
                    st.info("Check terminal logs for detailed error usage.")
                    
            except Exception as e:
                st.error(f"Error executing scan: {e}")


    """
    Backtesting interface for validating strategies.
    """
    st.header("🧪 Strategy Backtesting")
    st.caption("Simulate trading strategies on historical data")
    
    from libs.backtester import Backtester
    from libs.strategies import MLStrategy
    from libs.ml_pipeline import MLPipeline
    from libs.historical_data_manager import HistoricalDataManager
    from libs.feature_engineering import FeatureEngineer
    import plotly.express as px
    import plotly.graph_objects as go
    
    # 1. Configuration
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Configuration")
        
        # Symbol/Model Selection (reuse similar logic to ML page)
        models_dir = Path('models')
        model_files = list(models_dir.glob("*_v1.joblib")) if models_dir.exists() else []
        
        if not model_files:
            st.error("No models found. Train a model first.")
            return

        available_models = list(set([f"{f.stem.split('_')[0]}_{f.stem.split('_')[1]}" for f in model_files]))
        
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            format_func=lambda x: f"{x.split('_')[0]} - {x.split('_')[1]}"
        )
        symbol, timeframe = selected_model.split('_')
        
        initial_capital = st.number_input("Initial Capital (₹)", value=100000.0, step=10000.0)
        commission = st.number_input("Commission (%)", value=0.1, step=0.01) / 100
        
        st.markdown("---")
        st.markdown("### Strategy Parameters")
        buy_threshold = st.slider("Buy Threshold (Prob Up)", 0.3, 0.9, 0.4, 0.05)
        sell_threshold = st.slider("Sell Threshold (Prob Down)", 0.3, 0.9, 0.4, 0.05)
        
    with col2:
        st.subheader("📊 Backtest Results")
        
        if st.button("🚀 Run Backtest", type="primary"):
            with st.spinner("Running simulation..."):
                try:
                    # 1. Load Data & Model
                    pipeline = MLPipeline(symbol, timeframe)
                    pipeline.load_model(version='v1')
                    
                    manager = HistoricalDataManager()
                    df = manager.get_symbol_data(symbol, timeframe)
                    
                    # 2. Engineer Features
                    engineer = FeatureEngineer(df)
                    features = engineer.build_all()
                    ml_data = pd.concat([df, features], axis=1).dropna()
                    
                    # 3. Get Predictions
                    st.info(f"Generating predictions for {len(ml_data)} records...")
                    
                    X = ml_data[features.columns]
                    _, probs = pipeline.predict(X)
                    
                    ml_data['probability_down'] = probs[:, 0]
                    ml_data['probability_neutral'] = probs[:, 1]
                    ml_data['probability_up'] = probs[:, 2]
                    
                    # Debug: Show probability distribution
                    with st.expander("Probability Distribution (Debug)"):
                        st.write(ml_data[['probability_up', 'probability_down']].describe())
                    
                    # 4. Run Backtester
                    strategy = MLStrategy(
                        buy_threshold=buy_threshold,
                        sell_threshold=sell_threshold
                    )
                    
                    tester = Backtester(
                        initial_capital=initial_capital,
                        commission_pct=commission
                    )
                    
                    metrics = tester.run(ml_data, strategy)
                    
                    if not metrics:
                        st.warning("No trades executed.")
                    else:
                        # 5. Display Results
                        
                        # Metrics Cards
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Total Return", f"{metrics['total_return']:.2%}")
                        m2.metric("CAGR", f"{metrics['cagr']:.2%}")
                        m3.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
                        m4.metric("Max Drawdown", f"{metrics['max_drawdown']:.2%}")
                        
                        m5, m6, m7, m8 = st.columns(4)
                        m5.metric("Final Equity", f"₹{metrics['final_value']:,.2f}")
                        m6.metric("Total Trades", metrics['total_trades'])
                        m7.metric("Win Rate", f"{metrics['win_rate']:.1%}")
                        m8.metric("Profit Factor", "N/A") # Not calc yet
                        
                        # Equity Curve
                        st.subheader("📈 Equity Curve")
                        equity_df = tester.get_equity_curve()
                        
                        fig = px.line(equity_df, x=equity_df.index, y='portfolio_value', title='Portfolio Value Over Time')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Trade Log
                        st.subheader("📜 Trade Log")
                        trades_df = tester.get_trade_log()
                        if not trades_df.empty:
                            st.dataframe(trades_df, width="stretch")
                        else:
                            st.info("No trades recorded.")
                            
                except Exception as e:
                    st.error(f"Backtest failed: {e}")
                    import traceback
                    st.code(traceback.format_exc())


def page_pkscreener():
    """
    PKScreener Integration Page.
    """
    st.title("🚀 PKScreener Integration")
    st.markdown("Run advanced technical scans using [PKScreener](https://github.com/pkjmesra/PKScreener).")

    # Import adapter
    sys.path.append(str(PROJECT_ROOT)) # Ensure root is in path
    try:
        from libs.pkscreener_adapter import game_scanner
    except ImportError as e:
        st.error(f"Failed to import PKScreener Adapter: {e}")
        return

    # Tabs for Scanner and Docs
    tab_scan, tab_docs = st.tabs(["🔍 Run Scanner", "📚 Technical Documentation"])

    with tab_scan:
        # Configuration Form
        with st.form("pkscreener_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                scan_option = st.selectbox(
                    "Scan Type",
                    options=["X"],
                    format_func=lambda x: "Scanners (X)" if x == "X" else x
                )
                
            with col2:
                index_option = st.selectbox(
                    "Index / Stock List",
                    options=["12", "5", "8", "11", "13", "14"],
                    format_func=lambda x: {
                        "12": "Nifty 50",
                        "5": "Nifty Next 50", 
                        "8": "Nifty 100",
                        "11": "Nifty 500",
                        "13": "Newly Listed",
                        "14": "F&O Stocks"
                    }.get(x, x)
                )
                
            with col3:
                sub_option = st.selectbox(
                    "Strategy",
                    options=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35"],
                    format_func=lambda x: {
                        "0": "Full Screening",
                        "1": "Momentum",
                        "2": "Breakouts",
                        "3": "Consolidation",
                        "4": "Volume Monitor",
                        "5": "RSI / ADX / Ichimoku",
                        "6": "Reversals / MAs",
                        "7": "Chart Patterns",
                        "8": "CCI / MA / Volume",
                        "9": "Volume Shockers",
                        "10": "Kellner Channels",
                        "11": "Stock Performance",
                        "12": "Nifty/Market Strength",
                        "13": "Momentum (Short)",
                        "14": "Breakout (Short)",
                        "15": "Consolidation (Short)",
                        "16": "Volume Monitor (Short)",
                        "17": "Stock Performance (Short)",
                        "18": "Live Trends",
                        "19": "Live Trends (Short)",
                        "20": "Closing / Next Day",
                        "21": "Closing / Next Day (Short)",
                        "22": "Intraday (High Vol)",
                        "23": "Intraday (Momentum)",
                        "24": "Intraday (Reversals)",
                        "25": "Intraday (Breakouts)",
                        "26": "Intraday (Volume)",
                        "27": "Intraday (High Vol Short)",
                        "28": "Intraday (Momentum Short)",
                        "29": "Intraday (Reversals Short)",
                        "30": "Intraday (Breakouts Short)",
                        "31": "Intraday (Volume Short)",
                        "32": "Quick Daily Scans",
                        "33": "Quick Daily Scans (Short)",
                        "34": "Live Index Scan",
                        "35": "Live Index Scan (Short)"
                     }.get(x, f"Option {x}")
                )
                
            submit = st.form_submit_button("Run Scan 🔍")
        
    if submit:
        with st.spinner(f"Running PKScreener (Option {scan_option}:{index_option}:{sub_option})... This may take a minute."):
            # Run the scan asynchronously
            import asyncio
            try:
                # Streamlit runs in a loop, running asyncio.run inside it can be tricky.
                # However, for a simple script it often works if no other loop is running.
                # If it fails, we can fall back to normal execution.
                try:
                    results_df = asyncio.run(game_scanner.run_scan(scan_option, index_option, sub_option))
                except RuntimeError:
                    # If event loop is already running
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    results_df = loop.run_until_complete(game_scanner.run_scan(scan_option, index_option, sub_option))


                if not results_df.empty:
                    st.success(f"Scan Completed! Found {len(results_df)} stocks.")
                    st.dataframe(results_df, width="stretch")
                    
                    # Convert to CSV for download
                    csv = results_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Results as CSV",
                        data=csv,
                        file_name='pkscreener_results.csv',
                        mime='text/csv',
                    )
                else:
                    st.warning("No stocks found matching criteria or error executing scan.")
                    st.info("Check terminal logs for detailed error usage.")
                    
            except Exception as e:
                st.error(f"Error executing scan: {e}")

    with tab_docs:
        try:
            doc_path = PROJECT_ROOT / "docs" / "pkscreener_analysis.md"
            if doc_path.exists():
                with open(doc_path, "r") as f:
                    st.markdown(f.read())
            else:
                 st.info("Documentation not found at docs/pkscreener_analysis.md")
        except Exception as e:
            st.error(f"Error loading documentation: {e}")


# Add this function to dashboard.py
def main():
    st.set_page_config(
        page_title="Trading Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Broker credential check on startup
    try:
        from libs.broker_manager import BrokerManager
        broker_mgr = BrokerManager()
        has_creds, broker_name, error = broker_mgr.check_active_broker_credentials()
        
        if not has_creds:
            if not broker_name:
                st.warning(
                    "⚠️ **No broker configured.** Please configure your broker credentials to enable live trading features.",
                    icon="⚠️"
                )
                if st.button("Configure Broker Now →"):
                    st.session_state['force_broker_config'] = True
                    st.rerun()
            elif error and "not yet validated" not in error:
                st.error(
                    f"❌ **Broker authentication issue:** {error}",
                    icon="❌"
                )
                if st.button("Update Credentials →"):
                    st.session_state['force_broker_config'] = True
                    st.rerun()
    except Exception as e:
        # Silently fail if broker manager not available
        pass
    
    # Force broker config page if requested
    if st.session_state.get('force_broker_config'):
        from pages.broker_config import page_broker_config
        page_broker_config()
        st.session_state['force_broker_config'] = False
        return
    
    page = render_sidebar()
    if page == "Stock Analysis":
        page_stock_analysis()
    elif page == "Market Overview":
        page_market_overview()
    elif page == "Big Money Tracker":
        page_big_money()
    elif page == "Insider Activity":
        page_insider_activity()
    elif page == "Strategy Screener":
        page_strategy_screener()
    elif page == "Quad Report Card":
        page_quad_report()
    elif page == "ML Predictions":
        page_ml_predictions()
    elif page == "PKScreener":
        page_pkscreener()
    elif page == "Strategy Backtesting":
        page_backtesting()
    elif page == "Broker Configuration":
        from pages.broker_config import page_broker_config
        page_broker_config()
    elif page == "Data Management":
        page_data_management()
    elif page == "Database Info":
        page_database_info()
    elif page == "MLOps Monitor":
        page_mlops()

def page_mlops():
    """
    MLOps Monitor Page: API Health, Data Drift, Experiment Tracking.
    """
    st.title("🤖 MLOps Monitor")
    
    # 1. System Health
    st.header("1. System Health")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API Status")
        try:
            import requests
            from config import PROJECT_ROOT
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ Online (Latency: {response.elapsed.total_seconds()*1000:.0f}ms)")
                st.json(data)
            else:
                st.error(f"❌ Error: {response.status_code}")
        except Exception as e:
            st.error("❌ Offline (Connection Refused)")
            st.caption("Ensure `uvicorn api.main:app` is running on port 8000")
            
    with col2:
        st.subheader("Database Status")
        try:
            import sqlite3
            from config import PROJECT_ROOT
            conn = sqlite3.connect(PROJECT_ROOT / "data" / "trading.db")
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM ml_predictions")
            count = cursor.fetchone()[0]
            conn.close()
            st.success("✅ Connected")
            st.metric("Total Predictions Tracked", count)
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.markdown("---")

    # 2. Data Drift Monitor
    st.header("2. Data Drift Monitor")
    
    symbol = st.selectbox("Select Symbol for Drift Check", ["TCS", "RELIANCE", "INFY", "SBIN"])
    timeframe = "1d"
    
    if st.button("Analyze Data Drift"):
        with st.spinner("Calculating Drift Metrics..."):
            try:
                # Load data
                from libs.historical_data_manager import HistoricalDataManager
                manager = HistoricalDataManager()
                df = manager.get_symbol_data(symbol, timeframe)
                if df is None:
                    st.error("Data not found")
                else:
                    # Engineer features
                    from libs.feature_engineering import FeatureEngineer
                    from libs.data_drift_detector import DataDriftDetector
                    
                    engineer = FeatureEngineer(df)
                    features = engineer.build_all()
                    
                    # Split Reference (Old) vs Current (New)
                    # Simulating reference as first 50% and current as last 20%
                    n = len(features)
                    ref_data = features.iloc[:int(n*0.5)]
                    curr_data = features.iloc[int(n*0.8):]
                    
                    detector = DataDriftDetector(ref_data)
                    report = detector.detect_drift(curr_data)
                    
                    if report['drift_detected']:
                        st.error(f"⚠️ Drift Detected in {len(report['drifted_features'])} features!")
                    else:
                        st.success("✅ No Significant Drift Detected")
                    
                    # Details Table
                    details = []
                    for feat, metric in report['details'].items():
                        details.append({
                            "Feature": feat,
                            "PSI": f"{metric['psi']:.4f}",
                            "KS p-value": f"{metric['ks_p_value']:.4f}",
                            "Status": "🔴 Drift" if metric['drift_detected'] else "🟢 Stable"
                        })
                    
                    st.dataframe(pd.DataFrame(details))
                    
            except Exception as e:
                st.error(f"Drift analysis failed: {e}")

    st.markdown("---")

    # 3. Experiment Tracking
    st.header("3. Experiment Experiments (MLflow)")
    
    try:
        from config import PROJECT_ROOT
        mlruns_path = PROJECT_ROOT / "mlruns"
        if mlruns_path.exists():
            import mlflow
            mlflow.set_tracking_uri(f"file://{mlruns_path}")
            
            runs = mlflow.search_runs()
            if not runs.empty:
                st.subheader("Recent Training Runs")
                # Clean up columns for display
                cols = [c for c in runs.columns if c.startswith("metrics.") or c.startswith("params.") or c == "tags.mlflow.runName"]
                display_df = runs[cols].head(10)
                st.dataframe(display_df, width="stretch")
            else:
                st.info("No experiments found in MLflow.")
        else:
            st.warning("MLflow mlruns directory not found.")
            
    except Exception as e:
        st.error(f"Failed to load MLflow data: {e}")

if __name__ == "__main__":
    main()
"""
ML Predictions Page for Dashboard

Provides comprehensive interface for ML model predictions including:
- Symbol and model selection
- Real-time predictions with confidence
- Feature importance visualization
- Historical accuracy tracking
- Prediction explanations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
import warnings
import yaml
import sys
import requests
import sqlite3
warnings.filterwarnings('ignore')

