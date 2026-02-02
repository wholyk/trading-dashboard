"""Tests for technical indicators."""

import pytest
import pandas as pd
import numpy as np
from src.indicators import TechnicalIndicators
import logging


@pytest.fixture
def sample_data():
    """Create sample OHLCV data for testing."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    
    # Generate realistic price data
    np.random.seed(42)
    base_price = 100
    returns = np.random.normal(0, 0.02, 100)
    prices = base_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        "Open": prices * (1 + np.random.uniform(-0.01, 0.01, 100)),
        "High": prices * (1 + np.random.uniform(0, 0.02, 100)),
        "Low": prices * (1 + np.random.uniform(-0.02, 0, 100)),
        "Close": prices,
        "Volume": np.random.randint(1000000, 10000000, 100)
    }, index=dates)
    
    return df


@pytest.fixture
def indicators():
    """Create TechnicalIndicators instance for testing."""
    logger = logging.getLogger("test")
    return TechnicalIndicators(logger)


def test_indicators_initialization(indicators):
    """Test TechnicalIndicators initialization."""
    assert indicators is not None
    assert indicators.logger is not None


def test_calculate_sma(indicators, sample_data):
    """Test SMA calculation."""
    sma = indicators.calculate_sma(sample_data, period=20)
    
    assert sma is not None
    assert len(sma) == len(sample_data)
    # First 19 values should be NaN
    assert pd.isna(sma.iloc[:19]).all()
    # Later values should be valid numbers
    assert not pd.isna(sma.iloc[19:]).any()


def test_calculate_ema(indicators, sample_data):
    """Test EMA calculation."""
    ema = indicators.calculate_ema(sample_data, period=20)
    
    assert ema is not None
    assert len(ema) == len(sample_data)
    # EMA should have fewer NaN values than SMA
    assert not pd.isna(ema.iloc[20:]).any()


def test_calculate_rsi(indicators, sample_data):
    """Test RSI calculation."""
    rsi = indicators.calculate_rsi(sample_data, period=14)
    
    assert rsi is not None
    assert len(rsi) == len(sample_data)
    # RSI should be between 0 and 100
    valid_rsi = rsi[~pd.isna(rsi)]
    assert (valid_rsi >= 0).all()
    assert (valid_rsi <= 100).all()


def test_calculate_macd(indicators, sample_data):
    """Test MACD calculation."""
    macd_line, signal_line, histogram = indicators.calculate_macd(sample_data)
    
    assert macd_line is not None
    assert signal_line is not None
    assert histogram is not None
    
    assert len(macd_line) == len(sample_data)
    assert len(signal_line) == len(sample_data)
    assert len(histogram) == len(sample_data)


def test_calculate_bollinger_bands(indicators, sample_data):
    """Test Bollinger Bands calculation."""
    upper, middle, lower = indicators.calculate_bollinger_bands(sample_data, period=20)
    
    assert upper is not None
    assert middle is not None
    assert lower is not None
    
    assert len(upper) == len(sample_data)
    assert len(middle) == len(sample_data)
    assert len(lower) == len(sample_data)
    
    # Upper should be > Middle > Lower (where valid)
    valid_idx = ~pd.isna(upper)
    assert (upper[valid_idx] >= middle[valid_idx]).all()
    assert (middle[valid_idx] >= lower[valid_idx]).all()


def test_calculate_volume_sma(indicators, sample_data):
    """Test volume SMA calculation."""
    vol_sma = indicators.calculate_volume_sma(sample_data, period=20)
    
    assert vol_sma is not None
    assert len(vol_sma) == len(sample_data)


def test_calculate_atr(indicators, sample_data):
    """Test ATR calculation."""
    atr = indicators.calculate_atr(sample_data, period=14)
    
    assert atr is not None
    assert len(atr) == len(sample_data)
    # ATR should be positive
    valid_atr = atr[~pd.isna(atr)]
    assert (valid_atr >= 0).all()


def test_calculate_stochastic(indicators, sample_data):
    """Test Stochastic Oscillator calculation."""
    k, d = indicators.calculate_stochastic(sample_data, period=14)
    
    assert k is not None
    assert d is not None
    assert len(k) == len(sample_data)
    assert len(d) == len(sample_data)
    
    # Stochastic should be between 0 and 100
    valid_k = k[~pd.isna(k)]
    valid_d = d[~pd.isna(d)]
    assert (valid_k >= 0).all() and (valid_k <= 100).all()
    assert (valid_d >= 0).all() and (valid_d <= 100).all()


def test_add_all_indicators(indicators, sample_data):
    """Test adding all indicators to DataFrame."""
    config = {
        "sma": {"periods": [20, 50]},
        "ema": {"periods": [12, 26]},
        "rsi": {"period": 14},
        "macd": {"fast": 12, "slow": 26, "signal": 9},
        "bollinger_bands": {"period": 20, "std_dev": 2}
    }
    
    df_with_indicators = indicators.add_all_indicators(sample_data, config)
    
    assert df_with_indicators is not None
    assert "SMA_20" in df_with_indicators.columns
    assert "SMA_50" in df_with_indicators.columns
    assert "EMA_12" in df_with_indicators.columns
    assert "EMA_26" in df_with_indicators.columns
    assert "RSI" in df_with_indicators.columns
    assert "MACD" in df_with_indicators.columns
    assert "MACD_Signal" in df_with_indicators.columns
    assert "MACD_Hist" in df_with_indicators.columns
    assert "BB_Upper" in df_with_indicators.columns
    assert "BB_Middle" in df_with_indicators.columns
    assert "BB_Lower" in df_with_indicators.columns
