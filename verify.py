#!/usr/bin/env python3
"""
Verification script to ensure all components are working correctly.
Run this before deploying to production.
"""

import sys
import os
from pathlib import Path


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists."""
    exists = Path(filepath).exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {filepath}")
    return exists


def check_module_imports() -> bool:
    """Check if all modules can be imported."""
    print("\n2. Checking Module Imports:")
    modules = [
        'trading_bot',
        'backtesting',
        'notifications',
        'main'
    ]
    
    all_success = True
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module}: {e}")
            all_success = False
    
    return all_success


def check_dependencies() -> bool:
    """Check if all dependencies are installed."""
    print("\n3. Checking Dependencies:")
    dependencies = [
        'alpaca_trade_api',
        'flask',
        'pandas',
        'numpy'
    ]
    
    all_success = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} - Not installed")
            all_success = False
    
    return all_success


def check_environment_setup() -> bool:
    """Check if environment is configured."""
    print("\n4. Checking Environment Configuration:")
    
    # Check for .env.example
    example_exists = check_file_exists('.env.example')
    
    # Check for .env (optional but recommended)
    env_exists = Path('.env').exists()
    if env_exists:
        print("  ✓ .env file found (credentials configured)")
    else:
        print("  ⚠ .env file not found (you'll need to create it)")
    
    return example_exists


def run_basic_tests() -> bool:
    """Run basic functionality tests."""
    print("\n5. Running Basic Tests:")
    
    try:
        from trading_bot import RiskManager, TradingStrategy
        
        # Test RiskManager
        risk_manager = RiskManager()
        position = risk_manager.calculate_position_size(
            account_value=100000.0,
            current_price=100.0,
            stop_loss_price=98.0
        )
        
        if position > 0:
            print(f"  ✓ RiskManager working (calculated {position} shares)")
        else:
            print("  ✗ RiskManager returned 0 shares")
            return False
        
        # Test TradingStrategy
        strategy = TradingStrategy()
        signal = strategy.analyze([], 'TEST')
        
        if signal['signal'] == 'hold':
            print("  ✓ TradingStrategy working (returned 'hold' for empty data)")
        else:
            print(f"  ✗ TradingStrategy returned unexpected signal: {signal}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error running tests: {e}")
        return False


def check_documentation() -> bool:
    """Check if documentation exists."""
    print("\n6. Checking Documentation:")
    docs = [
        'README.md',
        'DEPLOYMENT.md',
        'QUICKSTART.md'
    ]
    
    all_exist = True
    for doc in docs:
        if not check_file_exists(doc):
            all_exist = False
    
    return all_exist


def main():
    """Run all verification checks."""
    print("="*70)
    print("AUTOMATED TRADING BOT - VERIFICATION")
    print("="*70)
    
    print("\n1. Checking Required Files:")
    required_files = [
        'trading_bot.py',
        'main.py',
        'backtesting.py',
        'notifications.py',
        'requirements.txt',
        '.env.example',
        '.gitignore'
    ]
    
    files_ok = all(check_file_exists(f) for f in required_files)
    
    # Run all checks
    modules_ok = check_module_imports()
    deps_ok = check_dependencies()
    env_ok = check_environment_setup()
    tests_ok = run_basic_tests()
    docs_ok = check_documentation()
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    checks = {
        "Required Files": files_ok,
        "Module Imports": modules_ok,
        "Dependencies": deps_ok,
        "Environment Setup": env_ok,
        "Basic Tests": tests_ok,
        "Documentation": docs_ok
    }
    
    for check_name, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {check_name}")
    
    all_passed = all(checks.values())
    
    print("="*70)
    
    if all_passed:
        print("\n✓ All checks passed! The bot is ready to use.")
        print("\nNext steps:")
        print("  1. Copy .env.example to .env and add your credentials")
        print("  2. Run: python examples.py")
        print("  3. Run: python trading_bot.py (with paper trading)")
        print("  4. See QUICKSTART.md for more details")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Check file paths and names")
        print("  - Review error messages above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
