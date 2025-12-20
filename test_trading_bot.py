"""
Test suite for trading bot components.
Run with: python test_trading_bot.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot import RiskManager, TradingStrategy, TradingBot
from backtesting import Backtester
from notifications import NotificationService, TradingMonitor


class TestRiskManager(unittest.TestCase):
    """Test risk management functionality."""
    
    def setUp(self):
        self.risk_manager = RiskManager(
            max_risk_per_trade=0.02,
            max_drawdown=0.10,
            max_position_size=0.20
        )
    
    def test_calculate_position_size(self):
        """Test position size calculation."""
        # Test basic calculation
        account_value = 100000.0
        current_price = 100.0
        stop_loss_price = 98.0
        
        position_size = self.risk_manager.calculate_position_size(
            account_value,
            current_price,
            stop_loss_price
        )
        
        # Should risk 2% of account ($2000) with $2 risk per share = 1000 shares
        # But limited by max_position_size (20%) = $20,000 / $100 = 200 shares
        self.assertEqual(position_size, 200)
    
    def test_position_size_with_max_constraint(self):
        """Test position size respects maximum position size."""
        account_value = 100000.0
        current_price = 10.0
        stop_loss_price = 9.99  # Very tight stop
        
        position_size = self.risk_manager.calculate_position_size(
            account_value,
            current_price,
            stop_loss_price
        )
        
        # Maximum position size is 20% = $20,000 / $10 = 2000 shares
        self.assertLessEqual(position_size, 2000)
    
    def test_check_drawdown_within_limit(self):
        """Test drawdown check when within limits."""
        result = self.risk_manager.check_drawdown(
            account_value=95000.0,
            peak_value=100000.0
        )
        
        # 5% drawdown is within 10% limit
        self.assertTrue(result)
    
    def test_check_drawdown_exceeds_limit(self):
        """Test drawdown check when exceeding limits."""
        result = self.risk_manager.check_drawdown(
            account_value=85000.0,
            peak_value=100000.0
        )
        
        # 15% drawdown exceeds 10% limit
        self.assertFalse(result)


class TestTradingStrategy(unittest.TestCase):
    """Test trading strategy logic."""
    
    def setUp(self):
        self.strategy = TradingStrategy(strategy_type="moving_average_crossover")
    
    def test_analyze_with_insufficient_data(self):
        """Test analysis with insufficient data."""
        signal = self.strategy.analyze([], 'AAPL')
        
        self.assertEqual(signal['signal'], 'hold')
        self.assertEqual(signal['confidence'], 0.0)
    
    def test_moving_average_crossover_hold(self):
        """Test moving average crossover returns hold when no crossover."""
        # Create mock bars
        mock_bars = []
        for i in range(50):
            bar = Mock()
            bar.c = 100.0  # Constant price, no crossover
            mock_bars.append(bar)
        
        signal = self.strategy.analyze(mock_bars, 'AAPL')
        
        self.assertEqual(signal['signal'], 'hold')


class TestNotificationService(unittest.TestCase):
    """Test notification service."""
    
    def test_notification_service_disabled_without_config(self):
        """Test that service is disabled without configuration."""
        with patch.dict(os.environ, {}, clear=True):
            service = NotificationService()
            self.assertFalse(service.enabled)
    
    def test_notification_service_enabled_with_config(self):
        """Test that service is enabled with configuration."""
        with patch.dict(os.environ, {
            'SENDER_EMAIL': 'test@example.com',
            'SENDER_PASSWORD': 'password',
            'RECIPIENT_EMAIL': 'recipient@example.com'
        }):
            service = NotificationService()
            self.assertTrue(service.enabled)


class TestTradingMonitor(unittest.TestCase):
    """Test trading monitor."""
    
    def setUp(self):
        self.monitor = TradingMonitor()
    
    def test_record_execution(self):
        """Test recording execution summary."""
        summary = {
            'timestamp': '2024-01-01T10:00:00',
            'orders_placed': 5,
            'symbols_analyzed': 10,
            'errors': []
        }
        
        self.monitor.record_execution(summary)
        
        metrics = self.monitor.get_metrics()
        self.assertEqual(metrics['total_executions'], 1)
        self.assertEqual(metrics['total_orders'], 5)
        self.assertEqual(metrics['total_errors'], 0)
    
    def test_record_execution_with_errors(self):
        """Test recording execution with errors."""
        summary = {
            'timestamp': '2024-01-01T10:00:00',
            'orders_placed': 2,
            'symbols_analyzed': 10,
            'errors': ['Error 1', 'Error 2']
        }
        
        self.monitor.record_execution(summary)
        
        metrics = self.monitor.get_metrics()
        self.assertEqual(metrics['total_errors'], 2)


class TestBacktester(unittest.TestCase):
    """Test backtesting functionality."""
    
    def setUp(self):
        self.backtester = Backtester(initial_capital=100000.0)
    
    def test_backtester_initialization(self):
        """Test backtester initializes correctly."""
        self.assertEqual(self.backtester.initial_capital, 100000.0)
        self.assertEqual(self.backtester.capital, 100000.0)
        self.assertEqual(len(self.backtester.trades), 0)
    
    def test_backtester_reset(self):
        """Test backtester reset."""
        self.backtester.capital = 50000.0
        self.backtester.trades.append({'test': 'trade'})
        
        self.backtester.reset()
        
        self.assertEqual(self.backtester.capital, 100000.0)
        self.assertEqual(len(self.backtester.trades), 0)


class TestTradingBotInitialization(unittest.TestCase):
    """Test trading bot initialization."""
    
    def test_initialization_without_credentials_raises_error(self):
        """Test that initialization fails without credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                TradingBot()
    
    @patch('trading_bot.tradeapi.REST')
    def test_initialization_with_credentials(self, mock_rest):
        """Test successful initialization with credentials."""
        with patch.dict(os.environ, {
            'APCA_API_KEY_ID': 'test_key',
            'APCA_API_SECRET_KEY': 'test_secret'
        }):
            bot = TradingBot(paper_trading=True)
            
            self.assertEqual(bot.api_key, 'test_key')
            self.assertEqual(bot.api_secret, 'test_secret')
            self.assertEqual(bot.base_url, 'https://paper-api.alpaca.markets')
            mock_rest.assert_called_once()


def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("Running Trading Bot Test Suite")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRiskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTradingStrategy))
    suite.addTests(loader.loadTestsFromTestCase(TestNotificationService))
    suite.addTests(loader.loadTestsFromTestCase(TestTradingMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestBacktester))
    suite.addTests(loader.loadTestsFromTestCase(TestTradingBotInitialization))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
