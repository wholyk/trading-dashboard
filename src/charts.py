"""Chart generation and visualization module."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List, Dict, Any
import logging


class ChartGenerator:
    """Generate interactive charts for stock data visualization."""
    
    def __init__(self, theme: str = "plotly_dark", logger: Optional[logging.Logger] = None):
        """
        Initialize ChartGenerator.
        
        Args:
            theme: Plotly theme name
            logger: Optional logger instance
        """
        self.theme = theme
        self.logger = logger or logging.getLogger(__name__)
    
    def create_candlestick_chart(self, data: pd.DataFrame, ticker: str, 
                                indicators: Optional[Dict[str, Any]] = None,
                                show_volume: bool = True, height: int = 600) -> go.Figure:
        """
        Create an interactive candlestick chart with optional indicators.
        
        Args:
            data: DataFrame with OHLCV data
            ticker: Stock ticker symbol
            indicators: Dictionary of indicators to display
            show_volume: Whether to show volume subplot
            height: Chart height in pixels
            
        Returns:
            Plotly Figure object
        """
        try:
            # Determine number of subplots
            rows = 2 if show_volume else 1
            row_heights = [0.7, 0.3] if show_volume else [1.0]
            
            fig = make_subplots(
                rows=rows,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=row_heights,
                subplot_titles=(f"{ticker} Price", "Volume") if show_volume else (f"{ticker} Price",)
            )
            
            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name="Price",
                    increasing_line_color='#26a69a',
                    decreasing_line_color='#ef5350'
                ),
                row=1, col=1
            )
            
            # Add technical indicators if provided
            if indicators:
                self._add_indicators_to_chart(fig, data, indicators)
            
            # Volume subplot
            if show_volume:
                colors = ['#26a69a' if close >= open_ else '#ef5350' 
                         for close, open_ in zip(data['Close'], data['Open'])]
                
                fig.add_trace(
                    go.Bar(
                        x=data.index,
                        y=data['Volume'],
                        name="Volume",
                        marker_color=colors,
                        showlegend=False
                    ),
                    row=2, col=1
                )
            
            # Update layout
            fig.update_layout(
                template=self.theme,
                height=height,
                xaxis_rangeslider_visible=False,
                hovermode='x unified',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            # Update axes
            fig.update_xaxes(title_text="Date", row=rows, col=1)
            fig.update_yaxes(title_text="Price", row=1, col=1)
            if show_volume:
                fig.update_yaxes(title_text="Volume", row=2, col=1)
            
            return fig
        
        except Exception as e:
            self.logger.error(f"Error creating candlestick chart: {e}")
            # Return empty figure on error
            return go.Figure()
    
    def _add_indicators_to_chart(self, fig: go.Figure, data: pd.DataFrame, 
                                 indicators: Dict[str, Any]) -> None:
        """
        Add technical indicators to the chart.
        
        Args:
            fig: Plotly figure to add indicators to
            data: DataFrame with indicator data
            indicators: Dictionary specifying which indicators to show
        """
        try:
            # SMA lines
            if indicators.get("sma"):
                for period in indicators["sma"]:
                    col_name = f"SMA_{period}"
                    if col_name in data.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=data.index,
                                y=data[col_name],
                                name=f"SMA {period}",
                                line=dict(width=1.5),
                                opacity=0.7
                            ),
                            row=1, col=1
                        )
            
            # EMA lines
            if indicators.get("ema"):
                for period in indicators["ema"]:
                    col_name = f"EMA_{period}"
                    if col_name in data.columns:
                        fig.add_trace(
                            go.Scatter(
                                x=data.index,
                                y=data[col_name],
                                name=f"EMA {period}",
                                line=dict(width=1.5, dash='dash'),
                                opacity=0.7
                            ),
                            row=1, col=1
                        )
            
            # Bollinger Bands
            if indicators.get("bollinger_bands") and all(col in data.columns for col in ["BB_Upper", "BB_Lower"]):
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data["BB_Upper"],
                        name="BB Upper",
                        line=dict(width=1, color='rgba(250, 250, 250, 0.3)'),
                        showlegend=False
                    ),
                    row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data["BB_Lower"],
                        name="BB Lower",
                        fill='tonexty',
                        line=dict(width=1, color='rgba(250, 250, 250, 0.3)'),
                        fillcolor='rgba(250, 250, 250, 0.1)',
                        showlegend=False
                    ),
                    row=1, col=1
                )
        
        except Exception as e:
            self.logger.error(f"Error adding indicators to chart: {e}")
    
    def create_indicator_chart(self, data: pd.DataFrame, indicator_type: str, 
                              ticker: str, height: int = 300) -> go.Figure:
        """
        Create a separate chart for indicators like RSI, MACD.
        
        Args:
            data: DataFrame with indicator data
            indicator_type: Type of indicator ('rsi', 'macd', 'stochastic')
            ticker: Stock ticker symbol
            height: Chart height in pixels
            
        Returns:
            Plotly Figure object
        """
        try:
            fig = go.Figure()
            
            if indicator_type == "rsi" and "RSI" in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data["RSI"],
                        name="RSI",
                        line=dict(color='#FFA726', width=2)
                    )
                )
                
                # Add overbought/oversold lines
                fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5)
                fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5)
                fig.update_yaxes(range=[0, 100])
                fig.update_layout(title=f"{ticker} - RSI (14)")
            
            elif indicator_type == "macd" and all(col in data.columns for col in ["MACD", "MACD_Signal"]):
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data["MACD"],
                        name="MACD",
                        line=dict(color='#42A5F5', width=2)
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data["MACD_Signal"],
                        name="Signal",
                        line=dict(color='#EF5350', width=2)
                    )
                )
                
                if "MACD_Hist" in data.columns:
                    colors = ['#26a69a' if val >= 0 else '#ef5350' for val in data["MACD_Hist"]]
                    fig.add_trace(
                        go.Bar(
                            x=data.index,
                            y=data["MACD_Hist"],
                            name="Histogram",
                            marker_color=colors,
                            opacity=0.3
                        )
                    )
                
                fig.update_layout(title=f"{ticker} - MACD (12, 26, 9)")
            
            # Common layout settings
            fig.update_layout(
                template=self.theme,
                height=height,
                xaxis_rangeslider_visible=False,
                hovermode='x unified',
                showlegend=True
            )
            
            return fig
        
        except Exception as e:
            self.logger.error(f"Error creating indicator chart: {e}")
            return go.Figure()
    
    def create_comparison_chart(self, data_dict: Dict[str, pd.DataFrame], 
                               tickers: List[str], height: int = 500) -> go.Figure:
        """
        Create a comparison chart for multiple stocks (normalized).
        
        Args:
            data_dict: Dictionary mapping ticker to DataFrame
            tickers: List of ticker symbols
            height: Chart height in pixels
            
        Returns:
            Plotly Figure object
        """
        try:
            fig = go.Figure()
            
            for ticker in tickers:
                if ticker in data_dict and not data_dict[ticker].empty:
                    data = data_dict[ticker]
                    # Normalize to percentage change from first value
                    normalized = (data['Close'] / data['Close'].iloc[0] - 1) * 100
                    
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=normalized,
                            name=ticker,
                            line=dict(width=2)
                        )
                    )
            
            fig.update_layout(
                template=self.theme,
                height=height,
                title="Stock Price Comparison (% Change)",
                xaxis_title="Date",
                yaxis_title="Change (%)",
                hovermode='x unified',
                showlegend=True
            )
            
            fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
            
            return fig
        
        except Exception as e:
            self.logger.error(f"Error creating comparison chart: {e}")
            return go.Figure()
