"""Technical indicators calculation module."""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
import logging


class TechnicalIndicators:
    """Calculate various technical indicators for stock data."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize TechnicalIndicators.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def calculate_sma(self, data: pd.DataFrame, period: int = 20, column: str = "Close") -> pd.Series:
        """
        Calculate Simple Moving Average.
        
        Args:
            data: DataFrame with price data
            period: Number of periods for SMA
            column: Column name to calculate SMA on
            
        Returns:
            Series with SMA values
        """
        try:
            return data[column].rolling(window=period).mean()
        except Exception as e:
            self.logger.error(f"Error calculating SMA: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def calculate_ema(self, data: pd.DataFrame, period: int = 20, column: str = "Close") -> pd.Series:
        """
        Calculate Exponential Moving Average.
        
        Args:
            data: DataFrame with price data
            period: Number of periods for EMA
            column: Column name to calculate EMA on
            
        Returns:
            Series with EMA values
        """
        try:
            return data[column].ewm(span=period, adjust=False).mean()
        except Exception as e:
            self.logger.error(f"Error calculating EMA: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14, column: str = "Close") -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            data: DataFrame with price data
            period: Number of periods for RSI (typically 14)
            column: Column name to calculate RSI on
            
        Returns:
            Series with RSI values (0-100)
        """
        try:
            delta = data[column].diff()
            gain = delta.where(delta > 0, 0.0)
            loss = -delta.where(delta < 0, 0.0)
            avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

            rs = avg_gain / avg_loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            return rsi.fillna(50)  # Fill NaN with neutral value
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, 
                      signal: int = 9, column: str = "Close") -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: DataFrame with price data
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            column: Column name to calculate MACD on
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        try:
            ema_fast = data[column].ewm(span=fast, adjust=False).mean()
            ema_slow = data[column].ewm(span=slow, adjust=False).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {e}")
            empty = pd.Series(index=data.index, dtype=float)
            return empty, empty, empty
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, 
                                  std_dev: float = 2.0, column: str = "Close") -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: DataFrame with price data
            period: Number of periods for moving average
            std_dev: Number of standard deviations
            column: Column name to calculate bands on
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        try:
            middle_band = data[column].rolling(window=period).mean()
            std = data[column].rolling(window=period).std()
            
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return upper_band, middle_band, lower_band
        except Exception as e:
            self.logger.error(f"Error calculating Bollinger Bands: {e}")
            empty = pd.Series(index=data.index, dtype=float)
            return empty, empty, empty
    
    def calculate_volume_sma(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average of volume.
        
        Args:
            data: DataFrame with volume data
            period: Number of periods for SMA
            
        Returns:
            Series with volume SMA values
        """
        try:
            return data['Volume'].rolling(window=period).mean()
        except Exception as e:
            self.logger.error(f"Error calculating volume SMA: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        Args:
            data: DataFrame with OHLC data
            period: Number of periods for ATR
            
        Returns:
            Series with ATR values
        """
        try:
            high = data['High']
            low = data['Low']
            close = data['Close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            
            return atr
        except Exception as e:
            self.logger.error(f"Error calculating ATR: {e}")
            return pd.Series(index=data.index, dtype=float)
    
    def calculate_stochastic(self, data: pd.DataFrame, period: int = 14, 
                            smooth_k: int = 3, smooth_d: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator.
        
        Args:
            data: DataFrame with OHLC data
            period: Lookback period
            smooth_k: %K smoothing period
            smooth_d: %D smoothing period
            
        Returns:
            Tuple of (%K, %D)
        """
        try:
            high = data['High']
            low = data['Low']
            close = data['Close']
            
            lowest_low = low.rolling(window=period).min()
            highest_high = high.rolling(window=period).max()
            
            k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            k = k.rolling(window=smooth_k).mean()
            d = k.rolling(window=smooth_d).mean()
            
            return k, d
        except Exception as e:
            self.logger.error(f"Error calculating Stochastic: {e}")
            empty = pd.Series(index=data.index, dtype=float)
            return empty, empty
    
    def add_all_indicators(self, data: pd.DataFrame, config: dict) -> pd.DataFrame:
        """
        Add all technical indicators to the DataFrame based on configuration.
        
        Args:
            data: DataFrame with OHLC data
            config: Configuration dictionary with indicator parameters
            
        Returns:
            DataFrame with added indicator columns
        """
        try:
            df = data.copy()
            
            # SMA
            if "sma" in config:
                for period in config["sma"].get("periods", [20, 50, 200]):
                    df[f"SMA_{period}"] = self.calculate_sma(df, period)
            
            # EMA
            if "ema" in config:
                for period in config["ema"].get("periods", [12, 26]):
                    df[f"EMA_{period}"] = self.calculate_ema(df, period)
            
            # RSI
            if "rsi" in config:
                period = config["rsi"].get("period", 14)
                df["RSI"] = self.calculate_rsi(df, period)
            
            # MACD
            if "macd" in config:
                macd_config = config["macd"]
                macd, signal, hist = self.calculate_macd(
                    df,
                    fast=macd_config.get("fast", 12),
                    slow=macd_config.get("slow", 26),
                    signal=macd_config.get("signal", 9)
                )
                df["MACD"] = macd
                df["MACD_Signal"] = signal
                df["MACD_Hist"] = hist
            
            # Bollinger Bands
            if "bollinger_bands" in config:
                bb_config = config["bollinger_bands"]
                upper, middle, lower = self.calculate_bollinger_bands(
                    df,
                    period=bb_config.get("period", 20),
                    std_dev=bb_config.get("std_dev", 2)
                )
                df["BB_Upper"] = upper
                df["BB_Middle"] = middle
                df["BB_Lower"] = lower
            
            return df
        
        except Exception as e:
            self.logger.error(f"Error adding indicators: {e}")
            return data
