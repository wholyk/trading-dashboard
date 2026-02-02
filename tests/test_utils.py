"""Tests for utility functions."""

import pytest
import yaml
from pathlib import Path
from src.utils import (
    format_currency,
    format_percentage,
    validate_ticker,
    safe_divide,
    get_color_for_change
)


def test_format_currency():
    """Test currency formatting."""
    assert format_currency(1000.50) == "$1,000.50"
    assert format_currency(0) == "$0.00"
    assert format_currency(1234567.89) == "$1,234,567.89"
    assert format_currency(100, "EUR") == "€100.00"


def test_format_percentage():
    """Test percentage formatting."""
    assert format_percentage(0.05) == "+5.00%"
    assert format_percentage(-0.03) == "-3.00%"
    assert format_percentage(0) == "0.00%"
    assert format_percentage(0.1234, include_sign=False) == "12.34%"


def test_validate_ticker():
    """Test ticker validation."""
    assert validate_ticker("AAPL") is True
    assert validate_ticker("GOOGL") is True
    assert validate_ticker("BRK.B") is True
    assert validate_ticker("^GSPC") is True
    assert validate_ticker("") is False
    assert validate_ticker("TOOLONGTICKER") is False
    assert validate_ticker("INVALID@") is False


def test_safe_divide():
    """Test safe division."""
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
    assert safe_divide(10, 0, default=1.0) == 1.0
    assert safe_divide(0, 5) == 0.0


def test_get_color_for_change():
    """Test color selection for value changes."""
    assert get_color_for_change(5.0) == "green"
    assert get_color_for_change(-3.0) == "red"
    # Zero change is treated as non-negative for display purposes and uses the positive (green) color.
    assert get_color_for_change(0) == "green"
