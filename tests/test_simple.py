"""
Simple Test Runner for AURACLE Forex System
===========================================

Can be run without pytest for basic validation.
"""

import os
import sys
import traceback
from datetime import datetime
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test that all core modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        from strategies.base_strategy import BaseStrategy
        from strategies.strategy_loader import StrategyLoader
        from strategies.rsi_macd_combo import RSI_MACD_Strategy
        print("  ✅ Strategy modules imported successfully")
    except Exception as e:
        print(f"  ❌ Strategy import failed: {e}")
        return False
    
    try:
        from risk_manager import RiskManager
        print("  ✅ Risk manager imported successfully")
    except Exception as e:
        print(f"  ❌ Risk manager import failed: {e}")
        return False
    
    try:
        from backtest_engine import BacktestEngine
        print("  ✅ Backtest engine imported successfully")
    except Exception as e:
        print(f"  ❌ Backtest engine import failed: {e}")
        return False
    
    try:
        from ml_optimizer import MLSignalOptimizer
        print("  ✅ ML optimizer imported successfully")
    except Exception as e:
        print(f"  ❌ ML optimizer import failed: {e}")
        return False
    
    try:
        from economic_calendar import EconomicCalendar
        print("  ✅ Economic calendar imported successfully")
    except Exception as e:
        print(f"  ❌ Economic calendar import failed: {e}")
        return False
    
    return True


def test_strategy_loader():
    """Test strategy loading functionality."""
    print("\n🧠 Testing strategy loader...")
    
    try:
        from strategies.strategy_loader import StrategyLoader
        
        loader = StrategyLoader('strategies')
        strategies = loader.load_all_strategies()
        
        if len(strategies) > 0:
            print(f"  ✅ Loaded {len(strategies)} strategies: {list(strategies.keys())}")
            
            # Test getting strategy instance
            strategy_name = list(strategies.keys())[0]
            strategy_instance = loader.get_strategy(strategy_name)
            print(f"  ✅ Created instance of {strategy_name}")
            
            return True
        else:
            print("  ⚠️  No strategies found in strategies/ directory")
            return True  # Not a failure, just no custom strategies
            
    except Exception as e:
        print(f"  ❌ Strategy loader test failed: {e}")
        traceback.print_exc()
        return False


def test_rsi_macd_strategy():
    """Test the RSI+MACD strategy."""
    print("\n📈 Testing RSI+MACD strategy...")
    
    try:
        from strategies.rsi_macd_combo import RSI_MACD_Strategy
        
        # Create strategy
        strategy = RSI_MACD_Strategy()
        print(f"  ✅ Strategy created: {strategy.get_strategy_name()}")
        
        # Generate sample data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
        np.random.seed(42)
        
        prices = []
        price = 1.1000
        for _ in range(100):
            price += np.random.normal(0, 0.001)
            prices.append(price)
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p + abs(np.random.normal(0, 0.0005)) for p in prices],
            'low': [p - abs(np.random.normal(0, 0.0005)) for p in prices],
            'close': prices,
            'volume': [np.random.randint(1000, 10000) for _ in range(100)]
        })
        
        # Generate signals
        signals = strategy.generate_signals(data, 'EURUSD')
        print(f"  ✅ Generated {len(signals)} signals")
        
        # Validate signals
        for signal in signals:
            if strategy.validate_signal(signal):
                print(f"  ✅ Signal validation passed")
                break
        
        return True
        
    except Exception as e:
        print(f"  ❌ RSI+MACD strategy test failed: {e}")
        traceback.print_exc()
        return False


def test_risk_manager():
    """Test risk management functionality."""
    print("\n⚖️ Testing risk manager...")
    
    try:
        from risk_manager import RiskManager
        
        config = {
            'account_balance': 10000,
            'max_daily_loss': 500,
            'max_positions': 3,
            'max_risk_per_trade': 0.02
        }
        
        risk_manager = RiskManager(config)
        print(f"  ✅ Risk manager created with balance: ${risk_manager.account_balance}")
        
        # Test position size calculation
        signal = {
            'pair': 'EURUSD',
            'signal': 'BUY',
            'entry_price': 1.1000,
            'stop_loss': 1.0950
        }
        
        position_size = risk_manager.calculate_position_size(signal, 1.1000)
        print(f"  ✅ Calculated position size: {position_size} lots")
        
        # Test position opening validation
        can_open, reason = risk_manager.can_open_position(signal)
        print(f"  ✅ Can open position: {can_open} ({reason})")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Risk manager test failed: {e}")
        traceback.print_exc()
        return False


def test_backtest_engine():
    """Test backtesting functionality."""
    print("\n📊 Testing backtest engine...")
    
    try:
        from backtest_engine import BacktestEngine
        from strategies.rsi_macd_combo import RSI_MACD_Strategy
        
        # Create sample data
        dates = pd.date_range(start='2024-01-01', periods=200, freq='1h')
        np.random.seed(42)
        
        prices = []
        price = 1.1000
        for _ in range(200):
            price += np.random.normal(0, 0.0005)
            prices.append(price)
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p + abs(np.random.normal(0, 0.0005)) for p in prices],
            'low': [p - abs(np.random.normal(0, 0.0005)) for p in prices],
            'close': prices,
            'volume': [np.random.randint(1000, 10000) for _ in range(200)]
        })
        
        # Run backtest
        engine = BacktestEngine(initial_balance=10000)
        strategy = RSI_MACD_Strategy()
        
        risk_config = {
            'max_positions': 3,
            'max_risk_per_trade': 0.02,
            'max_position_size': 1.0
        }
        
        results = engine.run_backtest(strategy, data, risk_config)
        
        print(f"  ✅ Backtest completed:")
        print(f"    - Total trades: {results.total_trades}")
        print(f"    - Win rate: {results.win_rate:.1f}%")
        print(f"    - Total P&L: ${results.total_pnl:.2f}")
        print(f"    - ROI: {results.roi:.2f}%")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Backtest engine test failed: {e}")
        traceback.print_exc()
        return False


def test_dashboard_components():
    """Test dashboard components."""
    print("\n🌐 Testing dashboard components...")
    
    try:
        from dashboard.app import AuracleDashboard
        
        config = {
            'port': 5000,
            'host': '127.0.0.1',
            'debug': False,
            'data_dir': 'data'
        }
        
        dashboard = AuracleDashboard(config)
        print("  ✅ Dashboard instance created")
        
        # Test route setup
        routes = list(dashboard.app.url_map.iter_rules())
        print(f"  ✅ Flask app configured with {len(routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Dashboard test failed: {e}")
        traceback.print_exc()
        return False


def test_data_directories():
    """Test that required data directories exist or can be created."""
    print("\n📁 Testing data directories...")
    
    required_dirs = [
        'data',
        'data/backtests',
        'data/logs',
        'strategies',
        'tests'
    ]
    
    for directory in required_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            if os.path.exists(directory):
                print(f"  ✅ Directory exists: {directory}")
            else:
                print(f"  ❌ Could not create directory: {directory}")
                return False
        except Exception as e:
            print(f"  ❌ Error with directory {directory}: {e}")
            return False
    
    return True


def main():
    """Run all tests."""
    print("🚀 AURACLE Forex System - Test Runner")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Data Directories", test_data_directories),
        ("Strategy Loader", test_strategy_loader),
        ("RSI+MACD Strategy", test_rsi_macd_strategy),
        ("Risk Manager", test_risk_manager),
        ("Backtest Engine", test_backtest_engine),
        ("Dashboard Components", test_dashboard_components)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! AURACLE Forex system is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)