"""Tests for portfolio management."""

import pytest
from pathlib import Path
from src.portfolio import Portfolio, Watchlist
import logging


@pytest.fixture
def temp_portfolio_file(tmp_path):
    """Create temporary portfolio file."""
    return str(tmp_path / "test_portfolio.json")


@pytest.fixture
def temp_watchlist_file(tmp_path):
    """Create temporary watchlist file."""
    return str(tmp_path / "test_watchlist.json")


@pytest.fixture
def portfolio(temp_portfolio_file):
    """Create Portfolio instance for testing."""
    logger = logging.getLogger("test")
    return Portfolio(data_file=temp_portfolio_file, logger=logger)


@pytest.fixture
def watchlist(temp_watchlist_file):
    """Create Watchlist instance for testing."""
    logger = logging.getLogger("test")
    return Watchlist(data_file=temp_watchlist_file, logger=logger)


def test_portfolio_initialization(portfolio):
    """Test Portfolio initialization."""
    assert portfolio is not None
    assert portfolio.holdings == []


def test_add_holding(portfolio):
    """Test adding a holding to portfolio."""
    result = portfolio.add_holding("AAPL", 10, 150.0, "2024-01-01", "Test holding")
    
    assert result is True
    assert len(portfolio.holdings) == 1
    
    holding = portfolio.holdings[0]
    assert holding["ticker"] == "AAPL"
    assert holding["shares"] == 10
    assert holding["purchase_price"] == 150.0
    assert holding["purchase_date"] == "2024-01-01"
    assert holding["notes"] == "Test holding"


def test_add_multiple_holdings(portfolio):
    """Test adding multiple holdings."""
    portfolio.add_holding("AAPL", 10, 150.0)
    portfolio.add_holding("GOOGL", 5, 2800.0)
    portfolio.add_holding("MSFT", 15, 380.0)
    
    assert len(portfolio.holdings) == 3


def test_add_holding_validation(portfolio):
    """Test holding validation."""
    # Invalid shares
    result = portfolio.add_holding("AAPL", 0, 150.0)
    assert result is False
    
    result = portfolio.add_holding("AAPL", -5, 150.0)
    assert result is False
    
    # Invalid price
    result = portfolio.add_holding("AAPL", 10, 0)
    assert result is False
    
    result = portfolio.add_holding("AAPL", 10, -100)
    assert result is False


def test_remove_holding(portfolio):
    """Test removing a holding."""
    portfolio.add_holding("AAPL", 10, 150.0)
    portfolio.add_holding("GOOGL", 5, 2800.0)
    
    holding_id = portfolio.holdings[0]["id"]
    result = portfolio.remove_holding(holding_id)
    
    assert result is True
    assert len(portfolio.holdings) == 1
    assert portfolio.holdings[0]["ticker"] == "GOOGL"


def test_get_holdings(portfolio):
    """Test getting holdings."""
    portfolio.add_holding("AAPL", 10, 150.0)
    portfolio.add_holding("GOOGL", 5, 2800.0)
    
    holdings = portfolio.get_holdings()
    
    assert len(holdings) == 2
    assert holdings[0]["ticker"] == "AAPL"
    assert holdings[1]["ticker"] == "GOOGL"


def test_calculate_portfolio_value(portfolio):
    """Test portfolio value calculation."""
    portfolio.add_holding("AAPL", 10, 150.0)
    portfolio.add_holding("GOOGL", 5, 2800.0)
    
    current_prices = {
        "AAPL": 160.0,
        "GOOGL": 2900.0
    }
    
    metrics = portfolio.calculate_portfolio_value(current_prices)
    
    assert metrics["total_cost"] == (10 * 150.0) + (5 * 2800.0)  # 15500
    assert metrics["total_value"] == (10 * 160.0) + (5 * 2900.0)  # 16100
    assert metrics["total_gain_loss"] == 600.0
    assert metrics["holdings_count"] == 2


def test_calculate_portfolio_value_empty(portfolio):
    """Test portfolio value calculation with empty portfolio."""
    metrics = portfolio.calculate_portfolio_value({})
    
    assert metrics["total_value"] == 0
    assert metrics["total_cost"] == 0
    assert metrics["total_gain_loss"] == 0
    assert metrics["holdings_count"] == 0


def test_get_allocation(portfolio):
    """Test portfolio allocation calculation."""
    portfolio.add_holding("AAPL", 10, 150.0)
    portfolio.add_holding("GOOGL", 5, 2800.0)
    
    current_prices = {
        "AAPL": 160.0,  # 1600 total
        "GOOGL": 2900.0  # 14500 total
    }
    # Total: 16100
    
    allocation = portfolio.get_allocation(current_prices)
    
    assert "AAPL" in allocation
    assert "GOOGL" in allocation
    assert abs(allocation["AAPL"] - (1600/16100*100)) < 0.01
    assert abs(allocation["GOOGL"] - (14500/16100*100)) < 0.01


def test_watchlist_initialization(watchlist):
    """Test Watchlist initialization."""
    assert watchlist is not None
    assert watchlist.tickers == []


def test_add_ticker_to_watchlist(watchlist):
    """Test adding ticker to watchlist."""
    result = watchlist.add_ticker("AAPL")
    
    assert result is True
    assert "AAPL" in watchlist.tickers


def test_add_duplicate_ticker(watchlist):
    """Test adding duplicate ticker."""
    watchlist.add_ticker("AAPL")
    result = watchlist.add_ticker("AAPL")
    
    assert result is True
    assert len(watchlist.tickers) == 1


def test_add_ticker_case_insensitive(watchlist):
    """Test ticker case handling."""
    watchlist.add_ticker("aapl")
    
    assert "AAPL" in watchlist.tickers
    assert "aapl" not in watchlist.tickers


def test_remove_ticker_from_watchlist(watchlist):
    """Test removing ticker from watchlist."""
    watchlist.add_ticker("AAPL")
    watchlist.add_ticker("GOOGL")
    
    result = watchlist.remove_ticker("AAPL")
    
    assert result is True
    assert "AAPL" not in watchlist.tickers
    assert "GOOGL" in watchlist.tickers


def test_get_tickers(watchlist):
    """Test getting all tickers."""
    watchlist.add_ticker("AAPL")
    watchlist.add_ticker("GOOGL")
    watchlist.add_ticker("MSFT")
    
    tickers = watchlist.get_tickers()
    
    assert len(tickers) == 3
    assert "AAPL" in tickers
    assert "GOOGL" in tickers
    assert "MSFT" in tickers


def test_clear_watchlist(watchlist):
    """Test clearing watchlist."""
    watchlist.add_ticker("AAPL")
    watchlist.add_ticker("GOOGL")
    watchlist.add_ticker("MSFT")
    
    result = watchlist.clear()
    
    assert result is True
    assert len(watchlist.tickers) == 0


def test_portfolio_persistence(temp_portfolio_file):
    """Test portfolio data persistence."""
    logger = logging.getLogger("test")
    
    # Create portfolio and add holdings
    portfolio1 = Portfolio(data_file=temp_portfolio_file, logger=logger)
    portfolio1.add_holding("AAPL", 10, 150.0)
    portfolio1.add_holding("GOOGL", 5, 2800.0)
    
    # Create new instance and verify data persisted
    portfolio2 = Portfolio(data_file=temp_portfolio_file, logger=logger)
    
    assert len(portfolio2.holdings) == 2
    assert portfolio2.holdings[0]["ticker"] == "AAPL"
    assert portfolio2.holdings[1]["ticker"] == "GOOGL"


def test_watchlist_persistence(temp_watchlist_file):
    """Test watchlist data persistence."""
    logger = logging.getLogger("test")
    
    # Create watchlist and add tickers
    watchlist1 = Watchlist(data_file=temp_watchlist_file, logger=logger)
    watchlist1.add_ticker("AAPL")
    watchlist1.add_ticker("GOOGL")
    
    # Create new instance and verify data persisted
    watchlist2 = Watchlist(data_file=temp_watchlist_file, logger=logger)
    
    assert len(watchlist2.tickers) == 2
    assert "AAPL" in watchlist2.tickers
    assert "GOOGL" in watchlist2.tickers
