"""
Backtesting module for testing trading strategies on historical data.
"""

import logging
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import pandas as pd
import alpaca_trade_api as tradeapi


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Backtester:
    """Backtesting engine for trading strategies."""
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.0  # Alpaca is commission-free
    ):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Starting capital for backtest
            commission: Commission per trade (default 0 for Alpaca)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.reset()
        logger.info(f"Backtester initialized with capital=${initial_capital:.2f}")
    
    def reset(self):
        """Reset backtest state."""
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.peak_value = self.initial_capital
    
    def run_backtest(
        self,
        strategy,
        symbols: List[str],
        start_date: str,
        end_date: str,
        risk_manager=None
    ) -> Dict:
        """
        Run backtest on historical data.
        
        Args:
            strategy: Trading strategy instance
            symbols: List of symbols to trade
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            risk_manager: Risk manager instance (optional)
        
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest from {start_date} to {end_date}")
        self.reset()
        
        # Import here to avoid circular dependency
        from trading_bot import RiskManager
        
        if risk_manager is None:
            risk_manager = RiskManager()
        
        # Simulate trading for each day
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        days_simulated = 0
        
        while current_date <= end_date_dt:
            # Check if it's a weekday
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                self._simulate_trading_day(
                    current_date,
                    strategy,
                    symbols,
                    risk_manager
                )
                days_simulated += 1
            
            current_date += timedelta(days=1)
        
        # Calculate metrics
        results = self._calculate_metrics()
        results['days_simulated'] = days_simulated
        
        logger.info(f"Backtest completed: {days_simulated} days simulated")
        logger.info(f"Final capital: ${self.capital:.2f}")
        logger.info(f"Total return: {results['total_return']:.2%}")
        
        return results
    
    def _simulate_trading_day(
        self,
        date: datetime,
        strategy,
        symbols: List[str],
        risk_manager
    ):
        """Simulate trading for a single day."""
        # Get current portfolio value
        portfolio_value = self.capital
        for symbol, position in self.positions.items():
            # Simplified: assume we can get the price
            # In real backtest, you'd fetch historical prices
            portfolio_value += position['qty'] * position['avg_price']
        
        # Update peak value
        self.peak_value = max(self.peak_value, portfolio_value)
        
        # Record equity
        self.equity_curve.append({
            'date': date,
            'equity': portfolio_value
        })
        
        # Check drawdown
        if not risk_manager.check_drawdown(portfolio_value, self.peak_value):
            logger.warning(f"Max drawdown reached on {date.date()}")
            return
        
        # Simulate trading for each symbol
        for symbol in symbols:
            # In a real backtest, you would:
            # 1. Fetch historical bars up to this date
            # 2. Run strategy analysis
            # 3. Execute simulated trades
            # 4. Update positions and capital
            pass
    
    def _calculate_metrics(self) -> Dict:
        """Calculate backtest performance metrics."""
        if not self.equity_curve:
            return {
                'total_return': 0.0,
                'max_drawdown': 0.0,
                'sharpe_ratio': 0.0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0
            }
        
        # Calculate returns
        final_equity = self.equity_curve[-1]['equity']
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        
        # Calculate maximum drawdown
        max_drawdown = 0.0
        peak = self.initial_capital
        
        for point in self.equity_curve:
            equity = point['equity']
            peak = max(peak, equity)
            drawdown = (peak - equity) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate trade statistics
        winning_trades = sum(1 for trade in self.trades if trade.get('profit', 0) > 0)
        losing_trades = sum(1 for trade in self.trades if trade.get('profit', 0) < 0)
        
        # Calculate Sharpe ratio (simplified)
        if len(self.equity_curve) > 1:
            returns = []
            for i in range(1, len(self.equity_curve)):
                prev_equity = self.equity_curve[i-1]['equity']
                curr_equity = self.equity_curve[i]['equity']
                daily_return = (curr_equity - prev_equity) / prev_equity
                returns.append(daily_return)
            
            if returns and len(returns) > 0:
                avg_return = sum(returns) / len(returns)
                std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
                sharpe_ratio = (avg_return / std_return * (252 ** 0.5)) if std_return > 0 else 0.0
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
        
        return {
            'total_return': total_return,
            'final_equity': final_equity,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': len(self.trades),
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / len(self.trades) if self.trades else 0.0
        }
    
    def get_equity_curve(self) -> pd.DataFrame:
        """Get equity curve as pandas DataFrame."""
        return pd.DataFrame(self.equity_curve)


def run_sample_backtest():
    """Run a sample backtest for demonstration."""
    from trading_bot import TradingStrategy, RiskManager
    
    # Initialize components
    backtester = Backtester(initial_capital=100000.0)
    strategy = TradingStrategy(strategy_type="moving_average_crossover")
    risk_manager = RiskManager()
    
    # Run backtest
    results = backtester.run_backtest(
        strategy=strategy,
        symbols=['AAPL', 'MSFT', 'GOOGL'],
        start_date='2023-01-01',
        end_date='2023-12-31',
        risk_manager=risk_manager
    )
    
    # Print results
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    print(f"Total Return: {results['total_return']:.2%}")
    print(f"Final Equity: ${results['final_equity']:.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2%}")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Total Trades: {results['total_trades']}")
    print(f"Winning Trades: {results['winning_trades']}")
    print(f"Losing Trades: {results['losing_trades']}")
    print(f"Win Rate: {results['win_rate']:.2%}")
    print("="*50)
    
    return results


if __name__ == "__main__":
    run_sample_backtest()
