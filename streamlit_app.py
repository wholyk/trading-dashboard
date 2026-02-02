"""
Trading Dashboard - Main Streamlit Application

A production-ready trading dashboard for real-time market data visualization,
technical analysis, and portfolio tracking.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import logging

# Import custom modules
from src.utils import load_config, setup_logging, format_currency, format_percentage, validate_ticker, handle_error
from src.data_fetcher import DataFetcher
from src.indicators import TechnicalIndicators
from src.charts import ChartGenerator
from src.portfolio import Portfolio, Watchlist


# Page configuration
st.set_page_config(
    page_title="Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def initialize_app():
    """Initialize application components."""
    try:
        config = load_config()
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        config = {}
    
    logger = setup_logging(config)
    data_fetcher = DataFetcher(logger)
    indicators = TechnicalIndicators(logger)
    chart_gen = ChartGenerator(config.get("charts", {}).get("theme", "plotly_dark"), logger)
    portfolio = Portfolio(logger=logger)
    watchlist = Watchlist(logger=logger)
    
    return config, logger, data_fetcher, indicators, chart_gen, portfolio, watchlist


def render_market_overview(config, data_fetcher):
    """Render market overview section."""
    st.header("📊 Market Overview")
    
    indices = config.get("market_indices", [])
    if not indices:
        st.info("No market indices configured.")
        return
    
    with st.spinner("Loading market indices..."):
        indices_data = data_fetcher.get_market_indices(indices)
    
    if not indices_data:
        st.warning("Unable to load market indices data.")
        return
    
    cols = st.columns(len(indices_data))
    
    for col, (name, data) in zip(cols, indices_data.items()):
        with col:
            change_color = "green" if data["change"] >= 0 else "red"
            st.metric(
                label=name,
                value=f"{data['value']:.2f}",
                delta=f"{format_percentage(data['change_pct'])}",
                delta_color="normal"
            )


def render_stock_analysis(config, logger, data_fetcher, indicators, chart_gen):
    """Render stock analysis section."""
    st.header("📈 Stock Analysis")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        ticker = st.text_input(
            "Enter Ticker Symbol",
            value="AAPL",
            max_chars=10,
            help="Enter a valid stock ticker symbol (e.g., AAPL, GOOGL, MSFT)"
        ).upper()
    
    with col2:
        timeframe_map = {
            "1 Day": "1d",
            "5 Days": "5d",
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y"
        }
        timeframe_display = st.selectbox(
            "Timeframe",
            options=list(timeframe_map.keys()),
            index=5
        )
        timeframe = timeframe_map[timeframe_display]
    
    with col3:
        interval_map = {
            "1 Day": {"1m": "1 Minute", "5m": "5 Minutes", "15m": "15 Minutes", "1h": "1 Hour"},
            "5 Days": {"5m": "5 Minutes", "15m": "15 Minutes", "30m": "30 Minutes", "1h": "1 Hour"},
            "1 Month": {"1h": "1 Hour", "1d": "1 Day"},
            "3 Months": {"1d": "1 Day", "1wk": "1 Week"},
            "6 Months": {"1d": "1 Day", "1wk": "1 Week"},
            "1 Year": {"1d": "1 Day", "1wk": "1 Week"},
            "2 Years": {"1d": "1 Day", "1wk": "1 Week"},
            "5 Years": {"1wk": "1 Week", "1mo": "1 Month"}
        }
        available_intervals = interval_map.get(timeframe_display, {"1d": "1 Day"})
        interval_display = st.selectbox("Interval", options=list(available_intervals.values()))
        interval = [k for k, v in available_intervals.items() if v == interval_display][0]
    
    if not validate_ticker(ticker):
        st.error("Please enter a valid ticker symbol.")
        return
    
    # Fetch data
    with st.spinner(f"Fetching data for {ticker}..."):
        stock_data = data_fetcher.get_stock_data(ticker, period=timeframe, interval=interval)
        stock_info = data_fetcher.get_stock_info(ticker)
    
    if stock_data is None or stock_data.empty:
        st.error(f"Unable to fetch data for {ticker}. Please verify the ticker symbol is correct.")
        return
    
    # Display stock info
    st.subheader(f"{stock_info['name']} ({ticker})")
    
    metric_cols = st.columns(6)
    with metric_cols[0]:
        current_price = stock_info.get("current_price", 0)
        previous_close = stock_info.get("previous_close", 0)
        change = current_price - previous_close
        change_pct = (change / previous_close) if previous_close > 0 else 0
        st.metric("Current Price", format_currency(current_price), 
                 delta=f"{format_percentage(change_pct)}")
    
    with metric_cols[1]:
        st.metric("Open", format_currency(stock_info.get("open", 0)))
    
    with metric_cols[2]:
        st.metric("Day High", format_currency(stock_info.get("day_high", 0)))
    
    with metric_cols[3]:
        st.metric("Day Low", format_currency(stock_info.get("day_low", 0)))
    
    with metric_cols[4]:
        volume = stock_info.get("volume", 0)
        st.metric("Volume", f"{volume:,}" if volume else "N/A")
    
    with metric_cols[5]:
        market_cap = stock_info.get("market_cap", 0)
        if market_cap:
            if market_cap >= 1e12:
                st.metric("Market Cap", f"${market_cap/1e12:.2f}T")
            elif market_cap >= 1e9:
                st.metric("Market Cap", f"${market_cap/1e9:.2f}B")
            else:
                st.metric("Market Cap", f"${market_cap/1e6:.2f}M")
        else:
            st.metric("Market Cap", "N/A")
    
    # Technical indicators configuration
    st.subheader("Technical Indicators")
    
    indicator_cols = st.columns(4)
    
    with indicator_cols[0]:
        show_sma = st.multiselect(
            "SMA",
            options=[20, 50, 200],
            default=[]
        )
    
    with indicator_cols[1]:
        show_ema = st.multiselect(
            "EMA",
            options=[12, 26],
            default=[]
        )
    
    with indicator_cols[2]:
        show_bb = st.checkbox("Bollinger Bands")
    
    with indicator_cols[3]:
        show_volume = st.checkbox("Volume", value=True)
    
    # Calculate indicators
    indicator_config = config.get("indicators", {})
    stock_data_with_indicators = indicators.add_all_indicators(stock_data, indicator_config)
    
    # Prepare indicators for chart
    chart_indicators = {}
    if show_sma:
        chart_indicators["sma"] = show_sma
    if show_ema:
        chart_indicators["ema"] = show_ema
    if show_bb:
        chart_indicators["bollinger_bands"] = True
    
    # Create and display candlestick chart
    chart_height = config.get("charts", {}).get("height", 600)
    fig = chart_gen.create_candlestick_chart(
        stock_data_with_indicators,
        ticker,
        indicators=chart_indicators,
        show_volume=show_volume,
        height=chart_height
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Additional indicator charts
    show_additional = st.expander("Additional Indicators", expanded=False)
    
    with show_additional:
        ind_col1, ind_col2 = st.columns(2)
        
        with ind_col1:
            if st.checkbox("Show RSI"):
                rsi_fig = chart_gen.create_indicator_chart(stock_data_with_indicators, "rsi", ticker)
                st.plotly_chart(rsi_fig, use_container_width=True)
        
        with ind_col2:
            if st.checkbox("Show MACD"):
                macd_fig = chart_gen.create_indicator_chart(stock_data_with_indicators, "macd", ticker)
                st.plotly_chart(macd_fig, use_container_width=True)


def render_portfolio(config, logger, data_fetcher, portfolio):
    """Render portfolio management section."""
    st.header("💼 Portfolio")
    
    # Portfolio summary
    holdings = portfolio.get_holdings()
    
    if not holdings:
        st.info("Your portfolio is empty. Add your first holding below.")
    else:
        # Get current prices for all holdings
        tickers = list(set([h["ticker"] for h in holdings]))
        with st.spinner("Updating portfolio values..."):
            current_prices = {}
            tickers_valued_at_cost = []
            tickers_without_price = []
            for ticker in tickers:
                info = data_fetcher.get_stock_info(ticker)
                current_price = None
                if isinstance(info, dict):
                    current_price = info.get("current_price")
                
                if current_price is not None:
                    # Use the live market price when available
                    current_prices[ticker] = current_price
                else:
                    # Fall back to a quantity-weighted average purchase price, if possible
                    ticker_holdings = [h for h in holdings if h.get("ticker") == ticker]
                    total_qty = sum(h.get("quantity", 0) for h in ticker_holdings)
                    if total_qty > 0:
                        total_cost = sum(
                            h.get("quantity", 0) * h.get("purchase_price", 0)
                            for h in ticker_holdings
                        )
                        fallback_price = total_cost / total_qty if total_qty else None
                        if fallback_price is not None:
                            current_prices[ticker] = fallback_price
                            tickers_valued_at_cost.append(ticker)
                            logger.warning(
                                "Falling back to purchase-price-based valuation for ticker %s "
                                "because current price data is unavailable.",
                                ticker,
                            )
                        else:
                            tickers_without_price.append(ticker)
                            logger.warning(
                                "Unable to determine either current or fallback price for ticker %s. "
                                "It will be excluded from current-value-based calculations.",
                                ticker,
                            )
                    else:
                        tickers_without_price.append(ticker)
                        logger.warning(
                            "No quantity available to value ticker %s. "
                            "It will be excluded from current-value-based calculations.",
                            ticker,
                        )
        
        if tickers_valued_at_cost or tickers_without_price:
            msg_parts = []
            if tickers_valued_at_cost:
                msg_parts.append(
                    "valued at their purchase price: "
                    + ", ".join(sorted(set(tickers_valued_at_cost)))
                )
            if tickers_without_price:
                msg_parts.append(
                    "excluded from current-value-based calculations due to missing data: "
                    + ", ".join(sorted(set(tickers_without_price)))
                )
            st.warning(
                "Some tickers did not have up-to-date price data and were handled specially: "
                + "; ".join(msg_parts)
            )
        
        # Calculate portfolio metrics
        portfolio_metrics = portfolio.calculate_portfolio_value(current_prices)
        
        # Display summary metrics
        summary_cols = st.columns(4)
        with summary_cols[0]:
            st.metric("Total Value", format_currency(portfolio_metrics["total_value"]))
        with summary_cols[1]:
            st.metric("Total Cost", format_currency(portfolio_metrics["total_cost"]))
        with summary_cols[2]:
            gain_loss = portfolio_metrics["total_gain_loss"]
            st.metric(
                "Gain/Loss",
                format_currency(gain_loss),
                delta=format_percentage(portfolio_metrics["total_gain_loss_pct"]),
                delta_color="normal"
            )
        with summary_cols[3]:
            st.metric("Holdings", portfolio_metrics["holdings_count"])
        
        # Display holdings table
        st.subheader("Holdings")
        holdings_df = portfolio.get_holdings_with_current_data(current_prices)
        
        if not holdings_df.empty:
            # Format the dataframe for display
            display_df = holdings_df.copy()
            display_df["Purchase Price"] = display_df["Purchase Price"].apply(lambda x: format_currency(x))
            display_df["Current Price"] = display_df["Current Price"].apply(lambda x: format_currency(x))
            display_df["Cost Basis"] = display_df["Cost Basis"].apply(lambda x: format_currency(x))
            display_df["Current Value"] = display_df["Current Value"].apply(lambda x: format_currency(x))
            display_df["Gain/Loss"] = display_df["Gain/Loss"].apply(lambda x: format_currency(x))
            display_df["Gain/Loss %"] = display_df["Gain/Loss %"].apply(lambda x: f"{x:.2f}%")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Allocation pie chart
        st.subheader("Allocation")
        allocation = portfolio.get_allocation(current_prices)
        
        if allocation:
            fig = go.Figure(data=[go.Pie(
                labels=list(allocation.keys()),
                values=list(allocation.values()),
                hole=0.3
            )])
            fig.update_layout(
                template="plotly_dark",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Add new holding
    st.subheader("Add Holding")
    
    with st.form("add_holding_form"):
        add_cols = st.columns(4)
        
        with add_cols[0]:
            new_ticker = st.text_input("Ticker", max_chars=10).upper()
        with add_cols[1]:
            new_shares = st.number_input("Shares", min_value=0.0, step=0.01)
        with add_cols[2]:
            new_price = st.number_input("Purchase Price", min_value=0.0, step=0.01)
        with add_cols[3]:
            new_date = st.date_input("Purchase Date", value=datetime.now())
        
        new_notes = st.text_input("Notes (optional)")
        
        submit = st.form_submit_button("Add Holding")
        
        if submit:
            if not new_ticker or not validate_ticker(new_ticker):
                st.error("Please enter a valid ticker symbol.")
            elif new_shares <= 0:
                st.error("Number of shares must be greater than 0.")
            elif new_price <= 0:
                st.error("Purchase price must be greater than 0.")
            else:
                if portfolio.add_holding(
                    new_ticker,
                    new_shares,
                    new_price,
                    new_date.isoformat(),
                    new_notes
                ):
                    st.success(f"Added {new_shares} shares of {new_ticker} to portfolio.")
                    st.rerun()
                else:
                    st.error("Failed to add holding. Please try again.")
    
    # Remove holdings
    if holdings:
        st.subheader("Remove Holding")
        holding_options = {f"{h['ticker']} - {h['shares']} shares": h['id'] for h in holdings}
        
        if holding_options:
            selected_holding = st.selectbox("Select holding to remove", options=list(holding_options.keys()))
            
            if st.button("Remove Selected Holding"):
                holding_id = holding_options[selected_holding]
                if portfolio.remove_holding(holding_id):
                    st.success("Holding removed successfully.")
                    st.rerun()
                else:
                    st.error("Failed to remove holding. Please try again.")


def render_watchlist(config, logger, data_fetcher, watchlist):
    """Render watchlist section."""
    st.header("⭐ Watchlist")
    
    tickers = watchlist.get_tickers()
    
    if not tickers:
        st.info("Your watchlist is empty. Add tickers below.")
    else:
        # Fetch current data for all tickers
        with st.spinner("Loading watchlist data..."):
            watchlist_data = {}
            for ticker in tickers:
                info = data_fetcher.get_stock_info(ticker)
                if info:
                    watchlist_data[ticker] = info
        
        if watchlist_data:
            # Create watchlist table
            watchlist_rows = []
            for ticker, info in watchlist_data.items():
                current_price = info.get("current_price", 0)
                previous_close = info.get("previous_close", 0)
                change = current_price - previous_close
                change_pct = (change / previous_close) if previous_close > 0 else 0
                
                watchlist_rows.append({
                    "Ticker": ticker,
                    "Name": info.get("name", ticker),
                    "Price": current_price,
                    "Change": change,
                    "Change %": change_pct * 100,
                    "Volume": info.get("volume", 0),
                    "Market Cap": info.get("market_cap", 0)
                })
            
            watchlist_df = pd.DataFrame(watchlist_rows)
            
            # Format for display
            display_df = watchlist_df.copy()
            display_df["Price"] = display_df["Price"].apply(lambda x: format_currency(x))
            display_df["Change"] = display_df["Change"].apply(lambda x: format_currency(x))
            display_df["Change %"] = display_df["Change %"].apply(lambda x: f"{x:+.2f}%")
            display_df["Volume"] = display_df["Volume"].apply(lambda x: f"{x:,}")
            display_df["Market Cap"] = display_df["Market Cap"].apply(
                lambda x: (
                    "N/A" if x is None or x <= 0
                    else f"${x/1e12:.2f}T" if x >= 1e12
                    else f"${x/1e9:.2f}B" if x >= 1e9
                    else f"${x/1e6:.2f}M" if x >= 1e6
                    else "<$1M"
                )
            )
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Add/Remove tickers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add to Watchlist")
        new_ticker = st.text_input("Enter Ticker", max_chars=10, key="watchlist_add").upper()
        
        if st.button("Add Ticker"):
            if not new_ticker or not validate_ticker(new_ticker):
                st.error("Please enter a valid ticker symbol.")
            elif new_ticker in tickers:
                st.warning(f"{new_ticker} is already in your watchlist.")
            else:
                # Validate ticker exists
                with st.spinner(f"Validating {new_ticker}..."):
                    if data_fetcher.validate_ticker(new_ticker):
                        if watchlist.add_ticker(new_ticker):
                            st.success(f"Added {new_ticker} to watchlist.")
                            st.rerun()
                        else:
                            st.error("Failed to add ticker. Please try again.")
                    else:
                        st.error(f"Ticker {new_ticker} not found or has no data.")
    
    with col2:
        st.subheader("Remove from Watchlist")
        if tickers:
            remove_ticker = st.selectbox("Select Ticker", options=tickers, key="watchlist_remove")
            
            if st.button("Remove Ticker"):
                if watchlist.remove_ticker(remove_ticker):
                    st.success(f"Removed {remove_ticker} from watchlist.")
                    st.rerun()
                else:
                    st.error("Failed to remove ticker. Please try again.")


def main():
    """Main application entry point."""
    try:
        # Initialize components
        config, logger, data_fetcher, indicators, chart_gen, portfolio, watchlist = initialize_app()
        
        logger.info("Trading Dashboard started")
        
        # Sidebar navigation
        st.sidebar.title("📈 Trading Dashboard")
        st.sidebar.markdown("---")
        
        page = st.sidebar.radio(
            "Navigation",
            ["Market Overview", "Stock Analysis", "Portfolio", "Watchlist"]
        )
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### About")
        st.sidebar.info(
            "This dashboard provides real-time market data, "
            "technical analysis tools, and portfolio tracking.\n\n"
            "Data provided by Yahoo Finance."
        )
        
        # Render selected page
        if page == "Market Overview":
            render_market_overview(config, data_fetcher)
        elif page == "Stock Analysis":
            render_stock_analysis(config, logger, data_fetcher, indicators, chart_gen)
        elif page == "Portfolio":
            render_portfolio(config, logger, data_fetcher, portfolio)
        elif page == "Watchlist":
            render_watchlist(config, logger, data_fetcher, watchlist)
    
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        if 'logger' in locals():
            logger.error(f"Application error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
