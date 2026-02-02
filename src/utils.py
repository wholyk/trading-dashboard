"""Utility functions for the trading dashboard."""

import logging
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import streamlit as st


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Configure logging based on application configuration.
    
    Args:
        config: Application configuration dictionary
        
    Returns:
        Configured logger instance
    """
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_file = log_config.get("file", "trading_dashboard.log")
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("trading_dashboard")


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Try the example file
        example_file = Path(f"{config_path}.example")
        if example_file.exists():
            config_file = example_file
        else:
            raise FileNotFoundError(
                f"Configuration file not found: {config_path} "
                f"(also tried example file: {example_file})"
            )
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config if config else {}
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing configuration file: {e}")


def format_currency(value: float, currency: str = "USD") -> str:
    """
    Format numeric value as currency.
    
    Args:
        value: Numeric value to format
        currency: Currency code (default: USD)
        
    Returns:
        Formatted currency string
    """
    symbol_map = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }
    
    symbol = symbol_map.get(currency, "$")
    return f"{symbol}{value:,.2f}"


def format_percentage(value: float, include_sign: bool = True) -> str:
    """
    Format numeric value as percentage.
    
    Args:
        value: Numeric value to format (0.05 = 5%)
        include_sign: Whether to include + sign for positive values
        
    Returns:
        Formatted percentage string
    """
    percent = value * 100
    sign = "+" if include_sign and percent > 0 else ""
    return f"{sign}{percent:.2f}%"


def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker symbol format.
    
    Args:
        ticker: Ticker symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not ticker:
        return False
    
    # Basic validation: alphanumeric, dots, hyphens, and carets allowed
    # Length between 1-10 characters
    ticker = ticker.strip().upper()
    
    if not (1 <= len(ticker) <= 10):
        return False
    
    allowed_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-^")
    return all(c in allowed_chars for c in ticker)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, handling zero division.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value to return on division by zero
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def get_color_for_change(value: float) -> str:
    """
    Get color based on positive/negative value.
    
    Args:
        value: Numeric value to evaluate
        
    Returns:
        Color string (red/green)
    """
    return "green" if value >= 0 else "red"


@st.cache_data(ttl=300)
def cached_config() -> Dict[str, Any]:
    """
    Load and cache configuration.
    Cache expires after 5 minutes.
    
    Returns:
        Configuration dictionary
    """
    try:
        return load_config()
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return {}


def handle_error(error: Exception, context: str = "", logger: Optional[logging.Logger] = None) -> str:
    """
    Handle and format errors consistently.
    
    Args:
        error: Exception that occurred
        context: Context description for the error
        logger: Optional logger instance
        
    Returns:
        User-friendly error message
    """
    error_msg = f"{context}: {str(error)}" if context else str(error)
    
    if logger:
        logger.error(error_msg, exc_info=True)
    
    # Map common errors to user-friendly messages
    if "Connection" in str(error) or "timeout" in str(error).lower():
        return "Network error. Please check your internet connection and try again."
    elif "404" in str(error):
        return "Data not found. Please verify the ticker symbol is correct."
    elif "rate limit" in str(error).lower():
        return "API rate limit reached. Please wait a moment and try again."
    else:
        return f"An error occurred: {error_msg}"
