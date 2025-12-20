"""
Example usage of the trading bot with different configurations.
"""

import os
from trading_bot import TradingBot, RiskManager, TradingStrategy
from backtesting import Backtester
from notifications import NotificationService, TradingMonitor


def example_basic_usage():
    """Basic usage example."""
    print("\n" + "="*70)
    print("Example 1: Basic Trading Bot Usage")
    print("="*70)
    
    # Set up environment (in real usage, these would be in .env file)
    os.environ['APCA_API_KEY_ID'] = 'your_api_key'
    os.environ['APCA_API_SECRET_KEY'] = 'your_api_secret'
    
    # Initialize bot with paper trading
    try:
        bot = TradingBot(paper_trading=True)
        
        # Define symbols to trade
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        
        # Execute trading logic
        summary = bot.execute_trading_logic(symbols)
        
        print(f"\nExecution completed:")
        print(f"  - Symbols analyzed: {summary['symbols_analyzed']}")
        print(f"  - Orders placed: {summary['orders_placed']}")
        print(f"  - Errors: {len(summary['errors'])}")
        
    except ValueError as e:
        print(f"\nNote: {e}")
        print("In real usage, set environment variables in .env file")


def example_custom_risk_parameters():
    """Example with custom risk parameters."""
    print("\n" + "="*70)
    print("Example 2: Custom Risk Parameters")
    print("="*70)
    
    # Create custom risk manager
    custom_risk = RiskManager(
        max_risk_per_trade=0.01,  # 1% risk per trade (more conservative)
        max_drawdown=0.05,         # 5% max drawdown
        max_position_size=0.15     # 15% max position size
    )
    
    print("\nCustom risk parameters:")
    print(f"  - Max risk per trade: {custom_risk.max_risk_per_trade:.1%}")
    print(f"  - Max drawdown: {custom_risk.max_drawdown:.1%}")
    print(f"  - Max position size: {custom_risk.max_position_size:.1%}")
    
    # Calculate position size example
    position = custom_risk.calculate_position_size(
        account_value=100000.0,
        current_price=150.0,
        stop_loss_price=147.0
    )
    
    print(f"\nExample position calculation:")
    print(f"  - Account value: $100,000")
    print(f"  - Stock price: $150")
    print(f"  - Stop loss: $147")
    print(f"  - Calculated position: {position} shares")


def example_backtesting():
    """Example of backtesting a strategy."""
    print("\n" + "="*70)
    print("Example 3: Backtesting a Strategy")
    print("="*70)
    
    # Initialize backtester
    backtester = Backtester(initial_capital=100000.0)
    
    # Initialize strategy
    strategy = TradingStrategy(strategy_type="moving_average_crossover")
    
    # Initialize risk manager
    risk_manager = RiskManager()
    
    print("\nBacktest configuration:")
    print(f"  - Initial capital: $100,000")
    print(f"  - Strategy: Moving Average Crossover")
    print(f"  - Date range: 2023-01-01 to 2023-12-31")
    print(f"  - Symbols: AAPL, MSFT, GOOGL")
    
    print("\nNote: Running full backtest requires historical data from Alpaca API")
    print("      See backtesting.py for implementation details")


def example_notification_setup():
    """Example of setting up notifications."""
    print("\n" + "="*70)
    print("Example 4: Notification Setup")
    print("="*70)
    
    # Initialize notification service (will be disabled without credentials)
    notification_service = NotificationService()
    
    print(f"\nNotification service enabled: {notification_service.enabled}")
    
    if not notification_service.enabled:
        print("\nTo enable email notifications, set these environment variables:")
        print("  - SENDER_EMAIL")
        print("  - SENDER_PASSWORD")
        print("  - RECIPIENT_EMAIL")
        print("  - SMTP_SERVER (optional)")
        print("  - SMTP_PORT (optional)")
    
    # Initialize monitor
    monitor = TradingMonitor(notification_service)
    
    # Example execution summary
    example_summary = {
        'timestamp': '2024-01-01T10:00:00',
        'symbols_analyzed': 5,
        'orders_placed': 2,
        'errors': []
    }
    
    print("\nExample: Recording execution")
    monitor.record_execution(example_summary)
    
    metrics = monitor.get_metrics()
    print(f"\nMonitor metrics:")
    print(f"  - Total executions: {metrics['total_executions']}")
    print(f"  - Total orders: {metrics['total_orders']}")
    print(f"  - Total errors: {metrics['total_errors']}")


def example_live_trading_workflow():
    """Example of complete live trading workflow."""
    print("\n" + "="*70)
    print("Example 5: Complete Live Trading Workflow")
    print("="*70)
    
    print("\nStep 1: Set up environment")
    print("  - Create Alpaca account and get API credentials")
    print("  - Copy .env.example to .env and fill in credentials")
    print("  - Start with paper trading (PAPER_TRADING=true)")
    
    print("\nStep 2: Test locally")
    print("  $ python trading_bot.py")
    
    print("\nStep 3: Monitor and adjust")
    print("  - Review logs and execution summaries")
    print("  - Adjust risk parameters if needed")
    print("  - Test different symbols and strategies")
    
    print("\nStep 4: Deploy to cloud (optional)")
    print("  - Follow instructions in DEPLOYMENT.md")
    print("  - Set up Cloud Scheduler for automation")
    print("  - Monitor via Cloud Functions logs")
    
    print("\nStep 5: Go live (when ready)")
    print("  - Set PAPER_TRADING=false")
    print("  - Start with small position sizes")
    print("  - Monitor closely")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("TRADING BOT EXAMPLES")
    print("="*70)
    print("\nThese examples demonstrate how to use the automated trading bot.")
    print("They are for educational purposes only.")
    
    example_basic_usage()
    example_custom_risk_parameters()
    example_backtesting()
    example_notification_setup()
    example_live_trading_workflow()
    
    print("\n" + "="*70)
    print("For more information, see:")
    print("  - README.md: Complete documentation")
    print("  - DEPLOYMENT.md: Cloud deployment guide")
    print("  - test_trading_bot.py: Test examples")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
