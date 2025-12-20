"""
Automated Day Trading Bot
This module implements an automated day trading system that connects to Alpaca's API,
implements trading strategies, manages risk, and can be deployed to cloud services.
"""

import os
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import APIError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RiskManager:
    """Manages risk and position sizing for trading operations."""
    
    def __init__(
        self,
        max_risk_per_trade: float = 0.02,  # 2% max risk per trade
        max_drawdown: float = 0.10,  # 10% max portfolio drawdown
        max_position_size: float = 0.20  # 20% max position size
    ):
        """
        Initialize risk management parameters.
        
        Args:
            max_risk_per_trade: Maximum percentage of portfolio to risk per trade (default 2%)
            max_drawdown: Maximum portfolio drawdown before stopping trading (default 10%)
            max_position_size: Maximum percentage of portfolio per position (default 20%)
        """
        self.max_risk_per_trade = max_risk_per_trade
        self.max_drawdown = max_drawdown
        self.max_position_size = max_position_size
        logger.info(f"RiskManager initialized with max_risk_per_trade={max_risk_per_trade}, "
                   f"max_drawdown={max_drawdown}, max_position_size={max_position_size}")
    
    def calculate_position_size(
        self,
        account_value: float,
        current_price: float,
        stop_loss_price: float,
        volatility_adjustment: float = 1.0
    ) -> int:
        """
        Calculate position size based on risk parameters.
        
        Args:
            account_value: Current account balance
            current_price: Current price of the asset
            stop_loss_price: Stop loss price
            volatility_adjustment: Factor to adjust for market volatility (0.5-2.0)
        
        Returns:
            Number of shares to trade
        """
        # Calculate risk per share
        risk_per_share = abs(current_price - stop_loss_price)
        
        if risk_per_share == 0:
            logger.warning("Risk per share is 0, returning 0 shares")
            return 0
        
        # Calculate maximum dollar risk for this trade
        max_dollar_risk = account_value * self.max_risk_per_trade
        
        # Adjust for volatility
        adjusted_risk = max_dollar_risk * volatility_adjustment
        
        # Calculate position size
        position_size = int(adjusted_risk / risk_per_share)
        
        # Apply maximum position size constraint
        max_shares = int((account_value * self.max_position_size) / current_price)
        position_size = min(position_size, max_shares)
        
        logger.info(f"Calculated position size: {position_size} shares "
                   f"(price=${current_price:.2f}, stop=${stop_loss_price:.2f})")
        
        return max(0, position_size)
    
    def check_drawdown(self, account_value: float, peak_value: float) -> bool:
        """
        Check if current drawdown exceeds maximum allowed drawdown.
        
        Args:
            account_value: Current account value
            peak_value: Peak account value
        
        Returns:
            True if trading should continue, False if max drawdown exceeded
        """
        if peak_value == 0:
            return True
        
        drawdown = (peak_value - account_value) / peak_value
        
        if drawdown >= self.max_drawdown:
            logger.warning(f"Maximum drawdown exceeded: {drawdown:.2%} >= {self.max_drawdown:.2%}")
            return False
        
        return True


class TradingStrategy:
    """Implements trading strategy logic."""
    
    def __init__(self, strategy_type: str = "moving_average_crossover"):
        """
        Initialize trading strategy.
        
        Args:
            strategy_type: Type of strategy to implement
        """
        self.strategy_type = strategy_type
        logger.info(f"TradingStrategy initialized with type={strategy_type}")
    
    def analyze(self, bars_data: List, symbol: str) -> Dict:
        """
        Analyze market data and generate trading signals.
        
        Args:
            bars_data: Historical price data
            symbol: Stock symbol
        
        Returns:
            Dictionary with signal ('buy', 'sell', 'hold'), confidence, and stop_loss
        """
        if not bars_data or len(bars_data) < 2:
            return {'signal': 'hold', 'confidence': 0.0, 'stop_loss': None}
        
        # Get current and previous prices
        current_bar = bars_data[-1]
        current_price = current_bar.c
        
        # Simple moving average crossover strategy
        if self.strategy_type == "moving_average_crossover":
            return self._moving_average_crossover(bars_data, current_price)
        
        # Default to hold
        return {'signal': 'hold', 'confidence': 0.0, 'stop_loss': None}
    
    def _moving_average_crossover(self, bars_data: List, current_price: float) -> Dict:
        """
        Implement moving average crossover strategy.
        
        Args:
            bars_data: Historical price data
            current_price: Current price
        
        Returns:
            Trading signal dictionary
        """
        # Calculate short and long moving averages
        short_period = 10
        long_period = 30
        
        if len(bars_data) < long_period:
            return {'signal': 'hold', 'confidence': 0.0, 'stop_loss': None}
        
        # Calculate moving averages
        short_ma = sum([bar.c for bar in bars_data[-short_period:]]) / short_period
        long_ma = sum([bar.c for bar in bars_data[-long_period:]]) / long_period
        prev_short_ma = sum([bar.c for bar in bars_data[-short_period-1:-1]]) / short_period
        prev_long_ma = sum([bar.c for bar in bars_data[-long_period-1:-1]]) / long_period
        
        # Check for crossover
        if prev_short_ma <= prev_long_ma and short_ma > long_ma:
            # Bullish crossover - buy signal
            stop_loss = current_price * 0.98  # 2% stop loss
            return {'signal': 'buy', 'confidence': 0.7, 'stop_loss': stop_loss}
        
        elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
            # Bearish crossover - sell signal
            return {'signal': 'sell', 'confidence': 0.7, 'stop_loss': None}
        
        return {'signal': 'hold', 'confidence': 0.0, 'stop_loss': None}


class TradingBot:
    """Main trading bot class that orchestrates trading operations."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        paper_trading: bool = True
    ):
        """
        Initialize trading bot.
        
        Args:
            api_key: Alpaca API key (or from environment)
            api_secret: Alpaca API secret (or from environment)
            base_url: API base URL (or from environment)
            paper_trading: Whether to use paper trading (default True)
        """
        # Get credentials from environment or parameters
        self.api_key = api_key or os.environ.get('APCA_API_KEY_ID')
        self.api_secret = api_secret or os.environ.get('APCA_API_SECRET_KEY')
        
        # Set base URL for paper or live trading
        if base_url:
            self.base_url = base_url
        elif paper_trading:
            self.base_url = 'https://paper-api.alpaca.markets'
        else:
            self.base_url = 'https://api.alpaca.markets'
        
        # Validate credentials
        if not self.api_key or not self.api_secret:
            raise ValueError("API credentials not provided. Set APCA_API_KEY_ID and APCA_API_SECRET_KEY environment variables.")
        
        # Initialize Alpaca API
        self.api = tradeapi.REST(
            self.api_key,
            self.api_secret,
            self.base_url,
            api_version='v2'
        )
        
        # Initialize components
        self.risk_manager = RiskManager()
        self.strategy = TradingStrategy()
        self.peak_value = 0.0
        
        logger.info(f"TradingBot initialized (paper_trading={paper_trading})")
    
    def get_account_info(self) -> Dict:
        """Get current account information."""
        try:
            account = self.api.get_account()
            account_info = {
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value)
            }
            logger.info(f"Account info: equity=${account_info['equity']:.2f}, "
                       f"cash=${account_info['cash']:.2f}")
            return account_info
        except APIError as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    def get_positions(self) -> List:
        """Get current open positions."""
        try:
            positions = self.api.list_positions()
            logger.info(f"Current positions: {len(positions)}")
            return positions
        except APIError as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_market_data(self, symbol: str, timeframe: str = '1Day', limit: int = 100) -> List:
        """
        Get historical market data for a symbol.
        
        Args:
            symbol: Stock symbol
            timeframe: Bar timeframe (e.g., '1Day', '1Hour')
            limit: Number of bars to retrieve
        
        Returns:
            List of bar data
        """
        try:
            bars = self.api.get_bars(symbol, timeframe, limit=limit).df
            logger.info(f"Retrieved {len(bars)} bars for {symbol}")
            return self.api.get_bars(symbol, timeframe, limit=limit)
        except APIError as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return []
    
    def place_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = 'market',
        time_in_force: str = 'day',
        stop_loss: Optional[float] = None
    ) -> Optional[str]:
        """
        Place an order.
        
        Args:
            symbol: Stock symbol
            qty: Quantity to trade
            side: 'buy' or 'sell'
            order_type: Order type (default 'market')
            time_in_force: Time in force (default 'day')
            stop_loss: Stop loss price (optional)
        
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            # Place main order
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force
            )
            
            logger.info(f"Order placed: {side} {qty} {symbol} - Order ID: {order.id}")
            
            # Place stop loss order if specified
            if stop_loss and side == 'buy':
                stop_order = self.api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side='sell',
                    type='stop',
                    time_in_force='gtc',  # Good till cancelled
                    stop_price=stop_loss
                )
                logger.info(f"Stop loss order placed at ${stop_loss:.2f} - Order ID: {stop_order.id}")
            
            return order.id
        except APIError as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def execute_trading_logic(self, symbols: List[str]) -> Dict:
        """
        Main trading logic execution.
        
        Args:
            symbols: List of symbols to trade
        
        Returns:
            Dictionary with execution summary
        """
        logger.info(f"Starting trading execution for symbols: {symbols}")
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'symbols_analyzed': len(symbols),
            'orders_placed': 0,
            'errors': []
        }
        
        try:
            # Get account information
            account_info = self.get_account_info()
            account_value = account_info['equity']
            
            # Update peak value
            self.peak_value = max(self.peak_value, account_value)
            
            # Check drawdown
            if not self.risk_manager.check_drawdown(account_value, self.peak_value):
                logger.warning("Maximum drawdown reached. Halting trading.")
                summary['errors'].append("Maximum drawdown reached")
                return summary
            
            # Analyze each symbol
            for symbol in symbols:
                try:
                    # Get market data
                    bars = self.get_market_data(symbol, timeframe='1Day', limit=100)
                    
                    if not bars:
                        logger.warning(f"No market data available for {symbol}")
                        continue
                    
                    # Analyze with strategy
                    signal = self.strategy.analyze(bars, symbol)
                    
                    if signal['signal'] == 'buy' and signal['confidence'] > 0.5:
                        # Calculate position size
                        current_price = bars[-1].c
                        stop_loss = signal.get('stop_loss', current_price * 0.98)
                        
                        qty = self.risk_manager.calculate_position_size(
                            account_value,
                            current_price,
                            stop_loss
                        )
                        
                        if qty > 0:
                            # Place buy order
                            order_id = self.place_order(
                                symbol,
                                qty,
                                'buy',
                                stop_loss=stop_loss
                            )
                            
                            if order_id:
                                summary['orders_placed'] += 1
                    
                    elif signal['signal'] == 'sell':
                        # Check if we have a position to sell
                        positions = self.get_positions()
                        for position in positions:
                            if position.symbol == symbol:
                                # Place sell order
                                qty = abs(int(position.qty))
                                order_id = self.place_order(symbol, qty, 'sell')
                                
                                if order_id:
                                    summary['orders_placed'] += 1
                                break
                
                except Exception as e:
                    error_msg = f"Error processing {symbol}: {str(e)}"
                    logger.error(error_msg)
                    summary['errors'].append(error_msg)
        
        except Exception as e:
            error_msg = f"Critical error in trading execution: {str(e)}"
            logger.error(error_msg)
            summary['errors'].append(error_msg)
        
        logger.info(f"Trading execution completed. Orders placed: {summary['orders_placed']}")
        return summary


def main_trading_function(request=None):
    """
    Main function to be called by cloud scheduler or manually.
    This function can be deployed as a Google Cloud Function.
    
    Args:
        request: HTTP request object (for Google Cloud Functions)
    
    Returns:
        Execution summary
    """
    logger.info("=" * 50)
    logger.info("Starting automated trading bot execution")
    logger.info("=" * 50)
    
    try:
        # Initialize trading bot
        bot = TradingBot(paper_trading=True)
        
        # Define symbols to trade (can be configured via environment or request)
        symbols = os.environ.get('TRADING_SYMBOLS', 'AAPL,MSFT,GOOGL,AMZN').split(',')
        
        # Execute trading logic
        summary = bot.execute_trading_logic(symbols)
        
        # Log summary
        logger.info("Execution Summary:")
        logger.info(f"  Symbols analyzed: {summary['symbols_analyzed']}")
        logger.info(f"  Orders placed: {summary['orders_placed']}")
        logger.info(f"  Errors: {len(summary['errors'])}")
        
        if summary['errors']:
            for error in summary['errors']:
                logger.error(f"  - {error}")
        
        return summary
    
    except Exception as e:
        logger.error(f"Fatal error in main_trading_function: {e}")
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'status': 'failed'
        }


if __name__ == "__main__":
    # For local testing
    main_trading_function()
