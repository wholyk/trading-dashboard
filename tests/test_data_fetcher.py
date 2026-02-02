"""Tests for data fetching functionality."""

import pytest
import pandas as pd
from src.data_fetcher import DataFetcher
import logging


@pytest.fixture
def data_fetcher():
    """Create DataFetcher instance for testing."""
    logger = logging.getLogger("test")
    return DataFetcher(logger)


def test_data_fetcher_initialization(data_fetcher):
    """Test DataFetcher initialization."""
    assert data_fetcher is not None
    assert data_fetcher.logger is not None


def test_get_stock_data_valid_ticker(data_fetcher):
    """Test fetching data for a valid ticker."""
    # Use a well-known ticker
    df = data_fetcher.get_stock_data("AAPL", period="5d", interval="1d")
    
    assert df is not None
    assert not df.empty
    assert "Close" in df.columns
    assert "Open" in df.columns
    assert "High" in df.columns
    assert "Low" in df.columns
    assert "Volume" in df.columns


def test_get_stock_data_invalid_ticker(data_fetcher):
    """Test fetching data for an invalid ticker."""
    df = data_fetcher.get_stock_data("INVALIDTICKER123456", period="1d")
    
    # Should return None or empty DataFrame for invalid ticker
    assert df is None or df.empty


def test_get_stock_info_valid_ticker(data_fetcher):
    """Test fetching info for a valid ticker."""
    info = data_fetcher.get_stock_info("AAPL")
    
    assert info is not None
    assert "symbol" in info
    assert info["symbol"] == "AAPL"
    assert "name" in info
    assert "current_price" in info


def test_get_stock_info_invalid_ticker(data_fetcher):
    """Test fetching info for an invalid ticker."""
    info = data_fetcher.get_stock_info("INVALIDTICKER123456")
    
    # Should return default dict with symbol
    assert info is not None
    assert info["symbol"] == "INVALIDTICKER123456"


def test_validate_ticker_valid(data_fetcher):
    """Test ticker validation with valid ticker."""
    # Note: This makes a real API call
    result = data_fetcher.validate_ticker("AAPL")
    assert result is True


def test_validate_ticker_invalid(data_fetcher):
    """Test ticker validation with invalid ticker."""
    result = data_fetcher.validate_ticker("INVALIDTICKER123456")
    assert result is False


def test_get_multiple_stocks(data_fetcher):
    """Test fetching multiple stocks."""
    tickers = ["AAPL", "GOOGL", "MSFT"]
    result = data_fetcher.get_multiple_stocks(tickers, period="1d")
    
    assert result is not None
    assert isinstance(result, dict)
    # At least one ticker should have data
    assert len(result) > 0
