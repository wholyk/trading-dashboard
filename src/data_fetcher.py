"""Data fetching module for retrieving market data from Yahoo Finance."""

import yfinance as yf
import pandas as pd
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import streamlit as st


class DataFetcher:
    """Handles all data fetching operations from Yahoo Finance."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize DataFetcher.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    @st.cache_data(ttl=60, show_spinner=False)
    def get_stock_data(_self, ticker: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data for a given ticker.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            _self.logger.info(f"Fetching data for {ticker}, period={period}, interval={interval}")
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                _self.logger.warning(f"No data returned for {ticker}")
                return None
            
            # Ensure timezone-naive datetime index for consistency
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            _self.logger.info(f"Successfully fetched {len(df)} rows for {ticker}")
            return df
        
        except Exception as e:
            _self.logger.error(f"Error fetching data for {ticker}: {e}")
            return None
    
    @st.cache_data(ttl=60, show_spinner=False)
    def get_stock_info(_self, ticker: str) -> Dict[str, Any]:
        """
        Get current stock information and metadata.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with stock information
        """
        try:
            _self.logger.info(f"Fetching info for {ticker}")
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract key information with defaults
            result = {
                "symbol": ticker,
                "name": info.get("longName", ticker),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "current_price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "previous_close": info.get("previousClose", 0),
                "open": info.get("open", 0),
                "day_high": info.get("dayHigh", 0),
                "day_low": info.get("dayLow", 0),
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
            }
            
            return result
        
        except Exception as e:
            _self.logger.error(f"Error fetching info for {ticker}: {e}")
            return {
                "symbol": ticker,
                "name": ticker,
                "sector": "N/A",
                "industry": "N/A",
                "current_price": 0,
                "previous_close": 0,
                "open": 0,
                "day_high": 0,
                "day_low": 0,
                "volume": 0,
                "market_cap": 0,
                "pe_ratio": 0,
                "dividend_yield": 0,
                "52_week_high": 0,
                "52_week_low": 0,
            }
    
    @st.cache_data(ttl=300, show_spinner=False)
    def get_multiple_stocks(_self, tickers: List[str], period: str = "1d") -> Dict[str, Dict[str, Any]]:
        """
        Get current data for multiple stocks efficiently.
        
        Args:
            tickers: List of stock ticker symbols
            period: Time period for data
            
        Returns:
            Dictionary mapping ticker to stock info
        """
        try:
            _self.logger.info(f"Fetching data for {len(tickers)} tickers")
            result = {}
            
            for ticker in tickers:
                info = _self.get_stock_info(ticker)
                result[ticker] = info
            
            return result
        
        except Exception as e:
            _self.logger.error(f"Error fetching multiple stocks: {e}")
            return {}
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_market_indices(_self, indices: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
        """
        Get data for major market indices.
        
        Args:
            indices: List of index dictionaries with 'symbol' and 'name'
            
        Returns:
            Dictionary mapping index name to data
        """
        try:
            _self.logger.info(f"Fetching {len(indices)} market indices")
            result = {}
            
            for index in indices:
                symbol = index.get("symbol")
                name = index.get("name")
                
                if not symbol:
                    continue
                
                try:
                    stock = yf.Ticker(symbol)
                    hist = stock.history(period="5d")
                    
                    if hist.empty:
                        continue
                    
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                    change = current - previous
                    change_pct = (change / previous) * 100 if previous != 0 else 0
                    
                    result[name] = {
                        "symbol": symbol,
                        "value": current,
                        "change": change,
                        "change_pct": change_pct / 100,  # Convert to decimal
                    }
                
                except Exception as idx_error:
                    _self.logger.warning(f"Error fetching index {symbol}: {idx_error}")
                    continue
            
            return result
        
        except Exception as e:
            _self.logger.error(f"Error fetching market indices: {e}")
            return {}
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol exists and has data.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if valid, False otherwise
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="5d")
            return not hist.empty
        except Exception:
            return False
